#!/usr/bin/env python3
"""Verify a registered component source tree without touching the network.

Three independent checks, all re-derivable from the bytes on disk:

1. manifests    - every `SHA256SUMS` under `<component>/source/` must verify
                  (relative entries resolve against the manifest directory,
                  absolute entries are used as written; a missing target is a
                  WARN, because build-tree manifests point into the ignored
                  research `workspace/`).
2. upstream     - every registered source file must hash (`git hash-object`,
                  i.e. the git blob id) to a blob of a donor revision, and the
                  `blob` column of `<component>/notes/source-map.tsv` must be
                  reachable.  Donor revisions come from local clones: pass
                  `--repo <git-rev-parse-ish repo> --ref <rev>` pairs.
3. copy-manifest - every COPY-MANIFEST.tsv row of this component must exist on
                  disk with the recorded sha256 and byte count; files under the
                  component directory with no row, and blobs registered under
                  more than one component, are reported.

`source-exact`/`reconstructed`/`copied-evidence`/... are not interpreted: the
script only reports hash facts and leaves classification to the reader.

usage:
  source-verify.py <component-dir> [--manifest COPY-MANIFEST.tsv]
                   [--repo R --ref REV]... [--json OUT] [--strict]

exit 0 = all checks pass; 1 = a check failed; 2 = usage/IO problem.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def blob_id(path: str) -> str:
    out = subprocess.run(["git", "hash-object", path], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git hash-object failed for {path}: {out.stderr.strip()}")
    return out.stdout.strip()


def walk_files(root: str) -> list[str]:
    if not os.path.isdir(root):
        return []
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        files.extend(os.path.join(dirpath, f) for f in filenames)
    return sorted(files)


def check_manifests(source_dir: str) -> dict:
    report = {"manifests": [], "checked": 0, "ok": True}
    for manifest in walk_files(source_dir):
        if not os.path.basename(manifest).endswith("SHA256SUMS"):
            continue
        entry = {"manifest": manifest, "entries": 0, "fail": [], "missing": []}
        for line in open(manifest, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2 or len(parts[0]) not in (64,):
                entry["fail"].append({"line": line, "reason": "malformed"})
                continue
            want, target = parts[0], parts[1].lstrip(" *")
            path = target if os.path.isabs(target) else os.path.join(
                os.path.dirname(manifest), target
            )
            entry["entries"] += 1
            report["checked"] += 1
            if not os.path.exists(path):
                entry["missing"].append(path)
                continue
            got = sha256(path)
            if got != want:
                entry["fail"].append({"path": path, "want": want, "got": got})
        if entry["fail"]:
            report["ok"] = False
        report["manifests"].append(entry)
    return report


def donor_tree(repo: str, rev: str) -> dict:
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    out = subprocess.run(
        ["git", "-C", repo, "ls-tree", "-r", "--format=%(objectname) %(path)", rev],
        capture_output=True,
        text=True,
        env=env,
    )
    if out.returncode != 0:
        raise RuntimeError(f"ls-tree {rev} in {repo} failed: {out.stderr.strip()}")
    tree: dict[str, list[str]] = {}
    for line in out.stdout.splitlines():
        sha, _, path = line.partition(" ")
        if sha and path:
            tree.setdefault(sha, []).append(path)
    return tree


def check_upstream(
    source_dir: str, map_path: str, donors: list[tuple[str, str]]
) -> dict:
    report = {"donors": [f"{r}@{rev}" for r, rev in donors], "files": [], "ok": True}
    trees = {}
    for repo, rev in donors:
        try:
            trees[f"{repo}@{rev}"] = donor_tree(repo, rev)
        except Exception as exc:  # a broken donor must not hide the other checks
            report["files"].append({"donor_error": str(exc), "rev": f"{repo}@{rev}"})
            report["ok"] = False
    recorded = {}
    if os.path.exists(map_path):
        with open(map_path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                b = (row.get("blob") or "").strip()
                if b:
                    recorded[b] = row
    map_blobs = set(recorded)
    for path in walk_files(source_dir):
        if os.path.basename(path).endswith("SHA256SUMS"):
            continue
        b = blob_id(path)
        hits = {rev: tree[b] for rev, tree in trees.items() if b in tree}
        entry = {
            "path": os.path.relpath(path, source_dir),
            "blob": b,
            "donor_paths": hits or {},
            "in_source_map": b[:10] in map_blobs if map_blobs else None,
        }
        if not hits:
            entry["verdict"] = "not-in-donor-trees"
        else:
            entry["verdict"] = "verbatim"
        report["files"].append(entry)
    for b, row in recorded.items():
        if not any(f.get("blob", "").startswith(b) for f in report["files"]):
            report.setdefault("map_blobs_unmatched", []).append(
                {"blob": b, "module": row.get("module"), "source_file": row.get("source_file")}
            )
            report["ok"] = False
    return report


def check_copy_manifest(component: str, manifest: str, comp_dir: str) -> dict:
    report = {"manifest": manifest, "rows": 0, "checked": 0, "ok": True}
    if not os.path.exists(manifest):
        report["ok"] = False
        report["error"] = "COPY-MANIFEST.tsv not found"
        return report
    with open(manifest, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    mine = [r for r in rows if r["component"] == component]
    by_hash: dict[str, set] = {}
    for r in rows:
        by_hash.setdefault(r["current_sha256"], set()).add(r["component"])
    report["rows"] = len(mine)
    listed = set()
    for r in mine:
        path = r["local_path"]
        if not os.path.exists(path):
            report.setdefault("absent", []).append(path)
            report["ok"] = False
            continue
        digest, size = sha256(path), os.path.getsize(path)
        listed.add(os.path.abspath(path))
        report["checked"] += 1
        bad = []
        if digest != r["current_sha256"]:
            bad.append(f"sha256 {digest}")
        if str(size) != r["bytes"]:
            bad.append(f"bytes {size}")
        if bad:
            report.setdefault("mismatch", []).append({"path": path, "detail": bad})
            report["ok"] = False
    own_dir = os.path.abspath(comp_dir)
    on_disk = {os.path.abspath(p) for p in walk_files(own_dir)}
    report["uncovered"] = sorted(os.path.relpath(p, own_dir) for p in on_disk - listed)
    report["shared_identities"] = [
        {
            "sha256": h[:16],
            "components": sorted(components),
            "paths": sorted(r["local_path"] for r in rows if r["current_sha256"] == h),
        }
        for h, components in sorted(by_hash.items())
        if len(components) > 1 and any(r["current_sha256"] == h for r in mine)
    ]
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("component_dir", help="…/<STATUS>/<COMPONENT> directory")
    ap.add_argument("--manifest", default="COPY-MANIFEST.tsv")
    ap.add_argument("--repo", action="append", default=[])
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--json")
    ap.add_argument(
        "--strict",
        help="treat coverage gaps (files with no COPY-MANIFEST row) as failure",
        action="store_true",
    )
    args = ap.parse_args()
    comp_dir = os.path.abspath(args.component_dir.rstrip("/"))
    if len(args.repo) != len(args.ref):
        print("every --repo needs a --ref", file=sys.stderr)
        return 2
    component = os.path.basename(comp_dir)
    source_dir = os.path.join(comp_dir, "source")
    report = {
        "component": component,
        "manifests": check_manifests(source_dir),
        "upstream": check_upstream(
            source_dir,
            os.path.join(comp_dir, "notes", "source-map.tsv"),
            list(zip(args.repo, args.ref)),
        )
        if args.repo
        else {"skipped": "no --repo/--ref given"},
        "copy_manifest": check_copy_manifest(component, args.manifest, comp_dir),
    }
    ok = report["manifests"]["ok"] and report["copy_manifest"]["ok"]
    if args.repo:
        ok = ok and report["upstream"].get("ok", True)
    if args.strict and report["copy_manifest"].get("uncovered"):
        ok = False

    m, u, c = report["manifests"], report["upstream"], report["copy_manifest"]
    print(f"component {component}")
    for e in m["manifests"]:
        print(
            f"  manifest {e['manifest']}: {e['entries']} entries, "
            f"{len(e['fail'])} bad, {len(e['missing'])} missing-target"
        )
    print(f"  manifests: {m['checked']} hash comparisons, ok={m['ok']}")
    if "files" in u:
        verb = [f for f in u["files"] if f.get("verdict") == "verbatim"]
        print(
            f"  upstream: {len(verb)}/{len(u['files'])} source blobs verbatim vs "
            f"{u['donors']}"
        )
        for f in u["files"]:
            if f.get("verdict") != "verbatim":
                print(f"    not-in-donor  {f['path']}  {f['blob'][:10]}")
    if "error" in c:
        print(f"  copy-manifest: ERROR {c['error']}")
    else:
        print(
            f"  copy-manifest: {c['rows']} rows / {c['checked']} verified, "
            f"{len(c.get('absent', []))} absent, {len(c.get('mismatch', []))} mismatched, "
            f"{len(c.get('uncovered', []))} files uncovered"
        )
        for p in c.get("uncovered", []):
            print(f"    uncovered     {p}")
        for s in c.get("shared_identities", []):
            print(f"    shared blob   {s['sha256']}… -> {', '.join(s['components'])}")
    print(f"RESULT {'PASS' if ok else 'FAIL'}")
    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"json {args.json}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
