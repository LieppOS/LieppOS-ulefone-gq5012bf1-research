#!/usr/bin/env python3
"""Cross-match every stock register table of one sensor against every table
of one or more donor oracles (any index, any name).

Usage: crossmatch_tables.py <stock_oracle_dir> <stock_prefix|sensor:NAME> <donor_oracle_dir>...
  sensor:NAME selects exactly the tables referenced by that sub-driver in
  oracle.json (needed for legacy addr_data_pair_* names shared by many TUs).

For each stock table prints the best donor table by (exact pairs in common)
and classifies: IDENTICAL / SAME_ADDR_SEQ(n diffs) / NEAREST(common/len).
"""
from __future__ import annotations

import csv
import glob
import os
import json
import sys


def load(p):
    with open(p) as f:
        return [tuple(r) for r in list(csv.reader(f, delimiter="\t"))[1:]]


def main():
    sd, pref, donors = sys.argv[1], sys.argv[2], sys.argv[3:]
    dt = {}
    for d in donors:
        for p in glob.glob(os.path.join(d, "settings", "*.tsv")):
            dt[f"{os.path.basename(d)}:{os.path.basename(p)[:-4]}"] = load(p)
    print("stock_table\tpairs\tbest_donor_table\tclass\tdetail")
    if pref.startswith("sensor:"):
        j = json.load(open(os.path.join(sd, "oracle.json")))
        s = [x for x in j["sensors"] if x["name"] == pref[7:]][0]
        names = {s["static_ctx"]["init_setting_table"]} | {m["setting"] for m in s["modes"]} | \
            {m["seamless_setting"] for m in s["modes"]}
        paths = sorted(os.path.join(sd, "settings", n.split("+")[0] + ".tsv") for n in names if n)
        paths = [p for p in paths if os.path.exists(p)]
    else:
        paths = sorted(glob.glob(os.path.join(sd, "settings", pref + "_*.tsv")))
    for p in paths:
        st = load(p)
        name = os.path.basename(p)[:-4]
        best = None
        for k, v in dt.items():
            if v == st:
                best = (k, "IDENTICAL", "")
                break
        if best is None:
            sa = [a for a, _ in st]
            cands = []
            for k, v in dt.items():
                if [a for a, _ in v] == sa:
                    nd = sum(1 for x, y in zip(st, v) if x != y)
                    cands.append((nd, k))
            if cands:
                nd, k = min(cands)
                best = (k, "SAME_ADDR_SEQ", f"{nd} values differ")
            else:
                ss = set(st)
                sc = max(((len(ss & set(v)), k) for k, v in dt.items()), default=(0, ""))
                best = (sc[1], "NEAREST", f"{sc[0]}/{len(st)} pairs shared")
        print(f"{name}\t{len(st)}\t{best[0]}\t{best[1]}\t{best[2]}")


if __name__ == "__main__":
    main()
