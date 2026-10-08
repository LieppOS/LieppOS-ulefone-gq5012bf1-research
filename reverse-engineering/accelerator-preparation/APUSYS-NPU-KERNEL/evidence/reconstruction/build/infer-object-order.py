#!/usr/bin/env python3
"""Infer the stock object link order of a multi-object module.
usage: objorder.py <common-dir> <file.mod> <stock.ko>
Prints the object order that reproduces the stock .text function sequence."""
import subprocess, sys, os
common, modf, stock = sys.argv[1:4]
objs = [o for o in open(modf).read().split() if o.endswith('.o')]
def text_funcs(path):
    out = subprocess.run(['llvm-readelf', '-SsW', path], capture_output=True, text=True).stdout
    idx = None
    for l in out.splitlines():
        p = l.split()
        if len(p) > 2 and p[0] == '[' and p[2] == '.text': idx = p[1].rstrip(']')
        elif len(p) > 2 and p[0].startswith('[') and p[1] == '.text': idx = p[0].strip('[]')
    fs = []
    for l in out.splitlines():
        p = l.split()
        if len(p) >= 8 and p[3] == 'FUNC' and p[6] == idx:
            fs.append((int(p[1], 16), p[7]))
    return [n for _, n in sorted(fs)]
of = {o: text_funcs(os.path.normpath(os.path.join(common, o))) for o in objs}
stockseq = text_funcs(stock)
order, i = [], 0
remaining = dict(of)
while i < len(stockseq):
    cand = [o for o, fs in remaining.items() if fs and stockseq[i:i+len(fs)] == fs]
    if not cand:
        print(f"NOMATCH at {i} {stockseq[i]}", file=sys.stderr); break
    o = min(cand, key=objs.index)   # identical name lists: keep Makefile order
    order.append(o)
    i += len(remaining.pop(o))
empties = [o for o, fs in remaining.items() if not fs]
print("\n".join(o.split('/apusys/',1)[-1] for o in order))
print(f"# matched {i}/{len(stockseq)} functions; objects without .text: {len(empties)}; unmatched with text: {[o.split('/apusys/',1)[-1] for o,f in remaining.items() if f]}", file=sys.stderr)
