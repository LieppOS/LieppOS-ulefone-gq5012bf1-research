#!/usr/bin/env python3
"""Harvest each component pack's own declared identity/scope lines.

The packs carry a structured header (`- **Subsystem:**`, `- **Hardware identity:**`,
`- **Stock artifact:**`, `- **Still required:**`, ...). Axis 3 (hardware) needs the
physical identity exactly as its owning pack states it, so the audit never invents a
part number the evidence does not support.

Output: coverage-audit/audit-evidence/pack-identity.tsv
"""
from __future__ import annotations

import csv
import os
import re

ROOT = "/home/armol/androido_dalykai/LieppOS custom ROM"
REPO = os.path.join(ROOT, "ulefone-gq5012bf1-research")
OUT = os.path.join(REPO, "reverse-engineering/coverage-audit/audit-evidence/"
                         "pack-identity.tsv")
FIELDS = ("component", "status", "subsystem", "hardware_identity", "stock_artifact",
          "interfaces", "remaining", "path")
KEYS = {
    "subsystem": r"sub-?system",
    "hardware_identity": r"hardware (identity|device|part)|physical (component|device)",
    "stock_artifact": r"stock artifact|parity",
    "interfaces": r"interface|bus|i2c|spi|spmi|gpio",
    "remaining": r"still required|remaining|open (work|question)",
}


def main() -> int:
    rows = []
    for status_dir in ("DONE", "PARTIAL", "BLOCKED", "TODO"):
        base = os.path.join(ROOT, f"Reverse Engineer - {status_dir}")
        if not os.path.isdir(base):
            continue
        for comp in sorted(os.listdir(base)):
            d = os.path.join(base, comp)
            if not os.path.isdir(d):
                continue
            readme = os.path.join(d, "README.md")
            if not os.path.exists(readme):
                continue
            text = open(readme, encoding="utf-8", errors="replace").read()[:20000]
            rec = {"component": comp, "status": status_dir,
                   "path": os.path.relpath(d, ROOT)}
            for field, pat in KEYS.items():
                val = ""
                for line in text.splitlines():
                    if re.search(pat, line, re.I) is None:
                        continue
                    if line.lstrip().startswith("- **") and line.count("**") >= 2:
                        val = line.split("**", 2)[2].lstrip(":. ")
                        break
                    m = re.search(rf"^\|[^|\n]*(?:{pat})[^|\n]*\|\s*(.+?)\s*\|", line,
                                  re.I)
                    if m:
                        val = m.group(1).strip("*` ")
                        break
                rec[field] = re.sub(r"\s+", " ", val).strip(" .")[:400]
            rows.append(rec)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(FIELDS), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"components={len(rows)} with-hardware-identity={sum(1 for r in rows if r['hardware_identity'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
