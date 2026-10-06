#!/usr/bin/env python3
"""Workspace-wide COPY-MANIFEST audit (regenerable; reports drift, changes nothing).

Implements the verification procedure recorded in the workspace index
(`REVERSE-ENGINEERING-STATUS.md`) over every pack at once:

  A  every manifest row resolves: `local_path` exists and its `current_sha256`
     and `bytes` still match the file on disk;
  B  every file inside a status tree (`Reverse Engineer - <STATUS>/…`, component
     packs and the aggregate files at the workspace root alike) has a manifest
     row, and no path is registered twice.

Rows are matched by exact workspace-relative path. Basename matching is NOT used:
it hides renames and status-tree reprefixing, which is exactly the drift sought.

    python3 reverse-engineering/scripts/manifest-audit.py "../.." \
        --json workspace/<phase>/manifest-audit.json

The JSON report lists the offending paths per component. Exit status is non-zero
unless A and B are both clean.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter

STATUS_DIR = "Reverse Engineer - {status}"


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace", help="workspace root holding the status trees")
    ap.add_argument("--manifest", default="COPY-MANIFEST.tsv")
    ap.add_argument("--json", help="optional JSON report path")
    args = ap.parse_args()

    root = os.path.abspath(args.workspace)
    header: list[str] | None = None
    rows: list[list[str]] = []
    with open(os.path.join(root, args.manifest), encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if header is None:
                header = fields
                continue
            rows.append(fields)
    if header is None:
        raise SystemExit(f"empty manifest: {args.manifest}")
    col = {name: i for i, name in enumerate(header)}
    for required in ("status", "component", "local_path", "bytes"):
        if required not in col:
            sys.exit(f"manifest {args.manifest} has no {required!r} column")
    sha_field = next((f for f in ("current_sha256", "sha256") if f in col), None)
    if sha_field is None:
        raise SystemExit(f"manifest {args.manifest} has no sha256 column")

    # --- A: every row resolves and still matches ----------------------------
    drift: dict[str, dict[str, list[str]]] = {}
    wrong_field_count: list[int] = []
    resolved = 0
    for row in rows:
        comp = row[col["component"]]
        rel = row[col["local_path"]]
        bucket = drift.setdefault(comp, {"fields": [], "missing": [], "hash": [], "size": []})
        if len(row) != len(header):
            bucket["fields"].append(rel or f"<row {len(bucket['fields'])}>")
            wrong_field_count.append(len(row))
            continue
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            bucket["missing"].append(rel)
            continue
        resolved += 1
        if sha256(path) != row[col[sha_field]].strip():
            bucket["hash"].append(rel)
        if str(os.path.getsize(path)) != row[col["bytes"]].strip():
            bucket["size"].append(rel)

    # --- B: every status-tree file is registered exactly once ---------------
    registered: Counter[str] = Counter(row[col["local_path"]] for row in rows)
    statuses = sorted(
        s
        for s in {row[col["status"]] for row in rows}
        if os.path.isdir(os.path.join(root, STATUS_DIR.format(status=s)))
    )
    if not statuses:
        raise SystemExit(f"no status tree directories under {root}")
    unregistered: dict[str, list[str]] = {}
    components_per_status: dict[str, int] = {}
    files_total = 0
    for status in statuses:
        sdir = os.path.join(root, STATUS_DIR.format(status=status))
        comps = sorted(c for c in os.listdir(sdir) if os.path.isdir(os.path.join(sdir, c)))
        components_per_status[status] = len(comps)
        for comp in comps:
            cdir = os.path.join(sdir, comp)
            if not os.path.isdir(cdir):
                continue
            missing = []
            for dirpath, _dirs, names in os.walk(cdir):
                for name in sorted(names):
                    if name == ".DS_Store":
                        continue
                    rel = os.path.relpath(os.path.join(dirpath, name), root)
                    files_total += 1
                    if registered[rel] == 0:
                        missing.append(rel)
            if missing:
                unregistered[comp] = sorted(missing)
    duplicate_paths = sorted(p for p, n in registered.items() if n > 1)

    report = {
        "workspace": root,
        "manifest": os.path.abspath(os.path.join(root, args.manifest)),
        "header": header,
        "status_trees": statuses,
        "rows_total": len(rows),
        "rows_resolved": resolved,
        "rows_wrong_field_count": len(wrong_field_count),
        "rows_missing_file": sum(len(v["missing"]) for v in drift.values()),
        "rows_hash_mismatch": sum(len(v["hash"]) for v in drift.values()),
        "rows_size_mismatch": sum(len(v["size"]) for v in drift.values()),
        "components_with_drift": {
            c: {k: len(v) for k, v in d.items() if v}
            for c, d in sorted(drift.items())
            if any(d.values())
        },
        "status_tree_components": components_per_status,
        "status_tree_files_total": files_total,
        "unregistered_files_total": sum(len(v) for v in unregistered.values()),
        "components_with_unregistered_files": {
            c: len(v) for c, v in sorted(unregistered.items())
        },
        "duplicate_paths": duplicate_paths,
        "drift_paths": {
            c: {k: v for k, v in d.items() if v} for c, d in sorted(drift.items())
        },
        "unregistered_paths": unregistered,
    }
    report["clean"] = not (
        report["rows_wrong_field_count"]
        or report["rows_missing_file"]
        or report["rows_hash_mismatch"]
        or report["rows_size_mismatch"]
        or unregistered
        or duplicate_paths
    )
    print(
        f"rows={report['rows_total']} resolved={report['rows_resolved']} "
        f"missing={report['rows_missing_file']} hash={report['rows_hash_mismatch']} "
        f"size={report['rows_size_mismatch']} fields={len(wrong_field_count)} "
        f"components_with_drift={len(report['components_with_drift'])} | "
        f"status_tree_files={files_total} "
        f"unregistered={report['unregistered_files_total']} in {len(unregistered)} "
        f"components duplicates={len(duplicate_paths)} "
        f"components_per_status={components_per_status} | clean={report['clean']}"
    )
    if args.json:
        out = os.path.abspath(args.json)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"wrote {out}")
    return 0 if report["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
