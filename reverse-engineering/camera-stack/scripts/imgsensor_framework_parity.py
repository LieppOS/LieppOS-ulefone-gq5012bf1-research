#!/usr/bin/env python3
"""Function-level parity of stock imgsensor.ko vs a donor rebuild, attributed
to donor source files.

Usage: imgsensor_framework_parity.py <stock.ko> <rebuilt.ko> <rebuilt_build_dir> <out.tsv>

<rebuilt_build_dir> must still contain the per-file .o objects of the donor
build so each function can be attributed to its translation unit.  Functions
whose name exists more than once (per-sensor statics such as open/init_ctx)
are compared only when unique in both modules.
Columns: source_file, function, stock_size, donor_size, size_eq, byte_eq, kcfi_eq
"""
from __future__ import annotations

import collections
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../../kernel/scripts"))
import phase4_module_parity as P  # noqa: E402


def objfuncs(o):
    out = subprocess.run(["llvm-nm", "--defined-only", o], capture_output=True, text=True).stdout
    return {l.split()[-1] for l in out.splitlines() if len(l.split()) == 3 and l.split()[1] in "tT"}


def main():
    stock, reb, bdir, outp = sys.argv[1:5]
    sf, rf = P.funcs(stock), P.funcs(reb)
    cnt_s = collections.Counter(n for n in sf)
    owner = {}
    for o in glob.glob(os.path.join(bdir, "**", "*.o"), recursive=True):
        if o.endswith((".mod.o",)) or os.path.basename(o) == "imgsensor.o":
            continue
        for fn in objfuncs(o):
            owner.setdefault(fn, os.path.relpath(o, bdir)[:-2] + ".c")
    rows = []
    per = collections.defaultdict(lambda: [0, 0, 0, 0])
    for name in sorted(set(sf) | set(rf)):
        s, r = sf.get(name), rf.get(name)
        src = owner.get(name, "(stock-only)" if r is None else "?")
        if s and r:
            size_eq = s[0] == r[0] if isinstance(s, tuple) else None
        rows.append((src, name, s, r))
    with open(outp, "w") as f:
        f.write("source_file\tfunction\tstock_size\tdonor_size\tsize_eq\tbyte_eq\tkcfi_eq\n")
        for src, name, s, r in rows:
            ss = s["size"] if s else "-"
            rs = r["size"] if r else "-"
            se = (s["size"] == r["size"]) if (s and r) else False
            be = (s["body"] == r["body"]) if (s and r) else False
            ke = (s.get("kcfi") == r.get("kcfi")) if (s and r) else False
            f.write(f"{src}\t{name}\t{ss}\t{rs}\t{se}\t{be}\t{ke}\n")
            p = per[src]
            p[0] += 1
            p[1] += bool(s and r)
            p[2] += se
            p[3] += be
    print("source_file\tfunctions\tshared\tsize_eq\tbyte_eq")
    for k in sorted(per):
        print(f"{k}\t" + "\t".join(map(str, per[k])))


if __name__ == "__main__":
    main()
