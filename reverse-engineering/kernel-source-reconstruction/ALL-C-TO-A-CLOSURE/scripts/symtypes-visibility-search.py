#!/usr/bin/env python3
"""Search which per-type visibility (defined vs `{ UNKNOWN }`) reproduces stock export CRCs.

usage: symtypes-visibility-search.py TU.symtypes OTHER.symtypes STOCK.crc SYMBOL...

For every type whose expansion differs between TU and OTHER and is reachable from the given
exports, try both variants (2^n combinations, n small). A hit means: "the stock translation unit
saw exactly this set of complete type definitions". It is a hypothesis about the stock #include
set, to be realized by a source include change and a real rebuild. It never edits CRCs.
"""
import importlib.util, itertools, sys
from pathlib import Path

sp = importlib.util.spec_from_file_location('sc', Path(__file__).with_name('symtypes-crc.py'))
sc = importlib.util.module_from_spec(sp); sp.loader.exec_module(sc)
tu, other = sc.load(sys.argv[1]), sc.load(sys.argv[2])
stock = {l.split()[1]: int(l.split()[0], 16) for l in open(sys.argv[3])}
syms = sys.argv[4:]

def reach(defs, roots):
    seen, todo = set(), list(roots)
    while todo:
        k = todo.pop()
        for t in defs.get(k, []):
            if '#' in t and t[0] in 'sueEt' and t not in seen and t in defs:
                seen.add(t); todo.append(t)
    return seen

union = dict(tu); union.update({k: v for k, v in other.items() if k not in tu})
cand = sorted(k for k in reach(union, syms) | reach(tu, syms)
              if '#' in k and k in tu and k in other and tu[k] != other[k])
print('reachable differing types:', cand, file=sys.stderr)
hits = []
for mask in itertools.product((0, 1), repeat=len(cand)):
    d = dict(tu)
    for k, m in zip(cand, mask):
        if m:
            d[k] = other[k]
    # types only defined in OTHER become visible when a type pulling them in is switched
    for k, v in other.items():
        d.setdefault(k, v)
    got = {s: sc.crc_of(s, d) for s in syms}
    ok = [s for s in syms if got[s] == stock.get(s)]
    if len(ok) == len(syms):
        hits.append(mask)
        print('HIT', {k: ('OTHER' if m else 'TU') for k, m in zip(cand, mask)})
print(f'{len(hits)} full hits over {2 ** len(cand)} combinations')
