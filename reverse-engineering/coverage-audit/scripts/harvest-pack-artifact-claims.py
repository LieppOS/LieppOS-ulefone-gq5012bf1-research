#!/usr/bin/env python3
"""Axis 4-8 evidence harvest: every per-component claim about a userspace artifact.

A "claim" is a literal mention of a shipped userspace/firmware/boot artifact
(service name, executable path, HAL interface, firmware filename or partition
name) inside an RE component's own text (workspace pack README/notes/evidence or
research-repo scope document).  Nothing is inferred: the builder scripts resolve
ownership only from what a component already asserts, and every classification
stays traceable to the file that asserts it.

Short generic tokens (single English words, bare version numbers) are excluded so
ordinary prose cannot masquerade as an ownership claim.

Output: audit-evidence/harvested-pack-artifact-claims.tsv
"""
from __future__ import annotations

import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CA = os.path.abspath(os.path.join(HERE, ".."))
EV = os.path.join(CA, "audit-evidence")
WS = os.environ.get("RE_WORKSPACE", os.path.abspath(os.path.join(CA, "..", "..", "..")))
RE_ROOT = os.path.join(WS, "ulefone-gq5012bf1-research/reverse-engineering")
OUT = os.path.join(EV, "harvested-pack-artifact-claims.tsv")
STATUSES = ("DONE", "PARTIAL", "BLOCKED", "TODO")

# artifacts too generic to prove ownership from a bare mention
STOP = {
    "service", "interface", "default", "version", "instance", "manifest", "system",
    "vendor", "product", "partition", "firmware", "daemon", "daemon.sh", "shell",
    "main", "test", "tests", "init", "ueventd", "healthd", "prng_seeder",
    "statsd", "traced", "uprobestats", "gpuservice", "mediadrmfwdrm", "ranchin",
}


def universe() -> dict[str, str]:
    """artifact key -> axis family"""
    keys: dict[str, str] = {}

    def add(k: str, family: str) -> None:
        k = k.strip().strip('"\'`,').strip()
        if not k or k.lower() in STOP or len(k) < 4:
            return
        keys.setdefault(k, family)

    for fam, fn, cols in (
            ("vintf", "raw-vintf.tsv", ("interface",)),
            ("service", "raw-init-services.tsv", ("service",)),
            ("binary", "raw-init-services.tsv", ("exec",)),
            ("legacy-hw", "raw-legacy-hw.tsv", ("module",)),
            ("firmware", "raw-firmware.tsv", ("path",)),
            ("partition", "raw-partitions.tsv", ("partition",))):
        path = os.path.join(EV, fn)
        if not os.path.exists(path):
            continue
        for r in csv.DictReader(open(path, encoding="utf8"), delimiter="\t"):
            for c in cols:
                v = (r.get(c) or "").strip()
                if not v:
                    continue
                if fam == "binary":
                    for tok in re.split(r"[\s|&]+", v):
                        tok = tok.split("/")[-1]
                        if tok and not tok.startswith(("-", "@", "$")):
                            add(tok, fam)
                elif fam in ("vintf", "firmware"):
                    add(v.split("/")[-1] if fam == "firmware" else v, fam)
                    if fam == "vintf":
                        add(v, fam)
                else:
                    add(v, fam)
    return keys


def scan(roots: list[tuple[str, str]], keys: dict[str, str]) -> list[dict]:
    pats = {k: re.compile(r"(?<![A-Za-z0-9_.:/@-])" + re.escape(k) + r"(?![A-Za-z0-9_])")
            for k in keys}
    # one alternation for candidate filtering, exact per-key check afterwards
    alt = re.compile("|".join(sorted((re.escape(k) for k in keys), key=len, reverse=True)))
    out = []
    per: dict[tuple, int] = collections.Counter()
    for scope, tier in roots:
        for dirpath, _dirs, files in os.walk(scope):
            top = os.path.relpath(dirpath, scope).split(os.sep)[0]
            for fn in sorted(files):
                if not fn.endswith((".md", ".tsv", ".csv")):
                    continue
                if tier in ("pack", "scope") and not (fn == "README.md" or top == "notes"
                                                     or top == "evidence"):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    text = open(path, encoding="utf8", errors="ignore").read()
                except OSError:
                    continue
                if not alt.search(text):
                    continue
                rel = os.path.relpath(path, WS)
                for line in text.splitlines():
                    hit = alt.findall(line)
                    if not hit:
                        continue
                    for h in set(hit):
                        p = pats[h]
                        if not p.search(line):
                            continue
                        key = (scope_label(scope, dirpath, fn), tier, h, rel)
                        if per[key] >= 2:
                            continue
                        per[key] += 1
                        out.append({"scope": scope_label(scope, dirpath, fn), "tier": tier,
                                    "artifact": h, "family": keys[h], "source_file": rel,
                                    "line": re.sub(r"\s+", " ", line).strip()[:150].rstrip()})
    return out


def scope_label(root: str, dirpath: str, fn: str) -> str:
    rel = os.path.relpath(dirpath, root)
    return rel.split(os.sep)[0] if rel != "." else fn


def main() -> int:
    keys = universe()
    by_fam = collections.Counter(keys.values())
    print(f"universe keys={len(keys)} {dict(by_fam)}")
    roots: list[tuple[str, str]] = []
    for st in STATUSES:
        d = os.path.join(WS, f"Reverse Engineer - {st}")
        if os.path.isdir(d):
            roots.append((d, "pack"))
    scopes = [os.path.join(RE_ROOT, s) for s in ("audio", "boot", "camera", "camera-stack",
                                               "connectivity", "display-input", "geniezone",
                                               "modem", "nfc", "power", "power-charging",
                                               "sensors", "storage", "thermal-camera",
                                               "tinysys", "usb")]
    roots += [(s, "scope") for s in scopes if os.path.isdir(s)]
    rows = scan(roots, keys)
    rows.sort(key=lambda r: (r["family"], r["artifact"], r["scope"]))
    with open(OUT, "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"claims={len(rows)} artifacts-claimed={len({(r['family'], r['artifact']) for r in rows})}")
    fam = collections.Counter(r["family"] for r in rows
                              if not r["scope"].startswith("research"))
    print("  workspace claims by family:", dict(fam))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
