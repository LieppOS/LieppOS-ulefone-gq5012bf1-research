#!/usr/bin/env python3
"""Axis 2a: harvest device-tree claims made by workspace packs and research docs.

Universe is the merged GQ5012BF1 live device tree
(`workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`, built
offline from the vendor_boot FDT + the single dtbo entry; see
`extraction-manifest.txt` next to it).  Every distinct `compatible` value in
that tree is looked up as a literal string in every Markdown/TSV/CSV/JSON body
of the RE workspace; each hit becomes one row so ownership can be resolved with
the same narrowest-scope rule as the kernel-module axis.

Output: audit-evidence/harvested-pack-dt-claims.tsv
"""
from __future__ import annotations

import csv
import os
import re
import sys

ROOT = "/home/armol/androido_dalykai/LieppOS custom ROM"
MERGED_DTS = os.path.join(
    ROOT, "ulefone-gq5012bf1-research/workspace/phase4-connfem-hardware/"
          "offline-dt/gq5012bf1-merged.dts")
OUT = os.path.join(ROOT, "ulefone-gq5012bf1-research/reverse-engineering/"
                         "coverage-audit/audit-evidence/harvested-pack-dt-claims.tsv")

TEXT_EXT = (".md", ".tsv", ".csv", ".json", ".txt", ".fragment")
SKIP_DIRS = {".git", "__pycache__", "node_modules"}
# a document quoting more compatibles than this is a device-tree dump, not a
# component claim: recording it as an owner would make every compatible trivially
# "covered by itself".  Dump files are reported in the `dump` tier instead.
DUMP_THRESHOLD = 60


def workspace_sources():
    """yield (component, kind, abspath) for every pack/research body file"""
    for base, label in (("Reverse Engineer - DONE", "pack"),
                        ("Reverse Engineer - PARTIAL", "pack"),
                        ("Reverse Engineer - BLOCKED", "pack"),
                        ("ulefone-gq5012bf1-research", "research")):
        top = os.path.join(ROOT, base)
        for dirpath, dirnames, files in os.walk(top):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            rel = os.path.relpath(dirpath, top)
            if label == "pack":
                component = rel.split(os.sep)[0] if rel != "." else ""
            else:
                component = "research:" + (rel.split(os.sep)[0] if rel != "." else "root")
            if not component:
                continue
            for fn in files:
                if fn.lower().endswith(TEXT_EXT):
                    yield component, label, os.path.join(dirpath, fn)


COMPAT = re.compile(r'compatible\s*=\s*((?:"[^"]+"\s*,?\s*)+)')
STRING = re.compile(r'"([^"]+)"')


def main() -> int:
    dts = open(MERGED_DTS, encoding="utf-8", errors="replace").read()
    universe: set[str] = set()
    for grp in COMPAT.findall(dts):
        universe.update(STRING.findall(grp))

    rows: dict[tuple[str, str, str], str] = {}
    for component, kind, path in workspace_sources():
        try:
            if os.path.getsize(path) > 4_000_000:
                continue
            body = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        relp = os.path.relpath(path, ROOT)
        hits = {c for c in universe if f'"{c}"' in body or f"`{c}`" in body}
        if len(hits) > DUMP_THRESHOLD:
            print(f"  dump (not a claim source): {relp} ({len(hits)} compatibles)")
            continue
        for c in hits:
            if f'"{c}"' in body or f"`{c}`" in body:
                rows.setdefault((component, "quoted-compatible", c), relp)
                continue
            tail = c.split(",")[-1]
            if len(tail) >= 6 and f"`{tail}`" in body:
                rows.setdefault((component, "bare-name", c), relp)
        listed = set(re.findall(r'compatible\s*=\s*"([^"]+)"', body))
        lower_map = {c.lower(): c for c in universe}
        for hit in (x.lower() for x in listed):
            if hit in lower_map:
                rows.setdefault((component, "compatible-list", lower_map[hit]), relp)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(("component", "kind", "compatible", "path"))
        for (component, kind, c), path in sorted(rows.items()):
            w.writerow((component, kind, c, path))
    print(f"universe distinct compatibles={len(universe)} claims={len(rows)}")
    import collections
    by = collections.Counter(k for _, k, _ in rows)
    print("kinds:", dict(by))
    print("claiming components:", len({c for c, _, _ in rows}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
