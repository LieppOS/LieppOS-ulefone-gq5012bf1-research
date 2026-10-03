#!/usr/bin/env python3
"""Per-function donor graft search.

For every function of <module> that is not EXACT/EXACT-CODE after the
current build, try each donor tree's definition of the same function (same
relative source file), rebuild the one object, and keep the graft only if
that function becomes EXACT/EXACT-CODE *and* no other function of the same
object regresses.  Writes a TSV log of every attempt (provenance).

Object-level test: the candidate .o is compared against the stock module's
functions by name (same Norm as ko_parity, relocations symbolic), so no link
is needed per attempt.

usage: graft_search.py <stock.ko> <parity.tsv> <srcroot> <objroot> <compile.sh> <log.tsv> <donor_root>...
  compile.sh <rel/file.c>  -> must produce <objroot>/<rel/file.o>
"""
import csv
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cfunc  # noqa: E402
import ko_parity as KP  # noqa: E402
from elfmini import Elf  # noqa: E402


def obj_funcs(o):
    out = subprocess.run(["llvm-nm", "--defined-only", o], capture_output=True, text=True).stdout
    return {l.split()[2] for l in out.splitlines() if len(l.split()) == 3 and l.split()[1] in "tT"}


def score(stock, so, ob, names):
    """class per function name: compare stock module function vs object function."""
    a, b = stock, Elf(ob)
    na, nb = KP.Norm(a), KP.Norm(b)
    res = {}
    for n in names:
        sa = [s for s in a.symbols if s.name == n and s.type == 2 and 0 < s.shndx < 0xFF00]
        sb = [s for s in b.symbols if s.name == n and s.type == 2 and 0 < s.shndx < 0xFF00]
        if len(sa) != 1 or len(sb) != 1:
            res[n] = "AMBIG"
            continue
        c, _ = KP.compare(a, b, sa[0], sb[0], na, nb, True)
        # in an unlinked .o, calls to other TU functions are relocs; layout check is meaningful
        res[n] = c
    return res


def main():
    stock_p, tsv, srcroot, objroot, comp, logp = sys.argv[1:7]
    donors = sys.argv[7:]
    stock = Elf(stock_p)
    rows = list(csv.DictReader(open(tsv), delimiter="\t"))
    bad = [r["name"] for r in rows if r["class"] not in ("EXACT", "EXACT-CODE", "EXTRA") and r["occ"] == "0"]
    # map function -> source file via objects
    fmap = {}
    for dp, _, fs in os.walk(objroot):
        for f in fs:
            if f.endswith(".o") and not f.endswith(".mod.o") and os.path.exists(
                    os.path.join(srcroot, os.path.relpath(os.path.join(dp, f[:-2] + ".c"), objroot))):
                o = os.path.join(dp, f)
                for n in obj_funcs(o):
                    fmap.setdefault(n, os.path.relpath(o, objroot)[:-2] + ".c")
    log = open(logp, "a")
    good = ("EXACT", "EXACT-CODE")
    for fn in bad:
        rel = fmap.get(fn)
        if not rel:
            log.write(f"{fn}\t-\t-\tNO-SOURCE\n")
            continue
        src = os.path.join(srcroot, rel)
        obj = os.path.join(objroot, rel[:-2] + ".o")
        names = sorted(obj_funcs(obj))
        base = score(stock, None, obj, names)
        if base.get(fn) in good:
            continue
        orig = open(src).read()
        done = False
        for d in donors:
            dsrc = os.path.join(d, rel)
            if not os.path.exists(dsrc):
                continue
            ds = open(dsrc).read()
            rd, rs = cfunc.find(orig, fn), cfunc.find(ds, fn)
            if not rd or not rs or orig[rd[0]:rd[1]] == ds[rs[0]:rs[1]]:
                continue
            new = orig[:rd[0]] + ds[rs[0]:rs[1]] + orig[rd[1]:]
            open(src, "w").write(new)
            r = subprocess.run([comp, rel], capture_output=True, text=True)
            if r.returncode != 0:
                log.write(f"{fn}\t{rel}\t{d}\tCOMPILE-FAIL\n")
                open(src, "w").write(orig)
                continue
            sc = score(stock, None, obj, names)
            regress = [n for n in names if base.get(n) in good and sc.get(n) not in good]
            if sc.get(fn) in good and not regress:
                log.write(f"{fn}\t{rel}\t{d}\tGRAFTED({sc[fn]})\n")
                orig = new
                base = sc
                done = True
                break
            log.write(f"{fn}\t{rel}\t{d}\tno({sc.get(fn)};regress={len(regress)})\n")
            open(src, "w").write(orig)
        if not done:
            subprocess.run([comp, rel], capture_output=True)
        log.flush()
        print(fn, "grafted" if done else "-", flush=True)


if __name__ == "__main__":
    main()
