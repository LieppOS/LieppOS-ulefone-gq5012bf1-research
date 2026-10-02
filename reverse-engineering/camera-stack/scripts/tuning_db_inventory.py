#!/usr/bin/env python3
"""Inventory of the stock MTK ISP tuning SQLite databases (read-only).

Usage: tuning_db_inventory.py <vendor_root> <out_tsv>
For every tuning_DB/<sensor>/mt6878/*.db: size, sha256[:12], tables and row
counts, plus whether the file is byte-identical to another sensor's DB.
Opened with immutable=1 / mode=ro so the stock files are never touched.
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
import sys

FOCUS = ("imx989", "imx989cts", "ov64b", "s5kjn1", "s5kjn1cts", "s5kjn1main2", "s5kgn1sp", "s5kgm2sp", "ov32b40",
         "default_sensor")


def main():
    v, out = sys.argv[1], sys.argv[2]
    base = os.path.join(v, "bin/crossbuild/DataSet/SQLiteModule/db/tuning_DB")
    rows = []
    hashes = {}
    for sd in sorted(os.listdir(base)):
        d = os.path.join(base, sd, "mt6878")
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
            hashes.setdefault(h, []).append(f"{sd}/{f}")
            tabs = []
            try:
                con = sqlite3.connect(f"file:{p}?mode=ro&immutable=1", uri=True)
                for (t,) in con.execute("select name from sqlite_master where type='table'"):
                    n = con.execute(f'select count(*) from "{t}"').fetchone()[0]
                    cols = [c[1] for c in con.execute(f'pragma table_info("{t}")')]
                    tabs.append(f"{t}[{n} rows; cols={'|'.join(cols[:8])}{'…' if len(cols) > 8 else ''}]")
                con.close()
            except sqlite3.Error as e:
                tabs.append(f"ERR:{e}")
            rows.append((sd, f, os.path.getsize(p), h, "; ".join(tabs)))
    with open(out, "w") as fo:
        fo.write("sensor_dir\tfile\tsize\tsha256_12\tidentical_to\tfocus\ttables\n")
        for sd, f, sz, h, t in rows:
            same = [x for x in hashes[h] if x != f"{sd}/{f}"]
            fo.write(f"{sd}\t{f}\t{sz}\t{h}\t{','.join(same)}\t{'Y' if sd.replace('_mipi_raw','') in FOCUS else ''}\t{t}\n")
    print(f"{len(rows)} mt6878 tuning DB files inventoried -> {out}")


if __name__ == "__main__":
    main()
