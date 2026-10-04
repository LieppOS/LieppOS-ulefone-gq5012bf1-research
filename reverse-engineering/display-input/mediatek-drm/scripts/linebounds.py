#!/usr/bin/env python3
"""linebounds.py BUILD_KO PARITY_DIR SRC.c OBJ.o
Bound where stock has extra/missing source lines in SRC.c.
Every __LINE__ site in SRC.c (B line numbers) gets a delta:
  * functions byte-identical in A/B -> all their __LINE__ sites have delta 0
  * otherwise deltas paired from `mov wN,#imm` immediates (linemap style)
Prints intervals between consecutive known sites where the delta changes.
"""
import sys, re, subprocess, difflib, bisect, os
S = '/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/display-input/rear-display-input/scripts/symdis.py'
A = '/home/armol/kernel-work/gki-12901745-workspace/lieppos/drm/stock-mediatek-drm.ko'
B, PD, SRC, OBJ = sys.argv[1:5]
src = open(SRC).read().split('\n')
st = {}
for l in open(PD + '/function-parity.tsv').read().splitlines()[1:]:
    c = l.split('\t'); st[c[0]] = c[3]
# function spans in source: crude: a line starting at col 0 with identifier and '(' followed later by '{' at col 0
spans = []
for i, l in enumerate(src):
    m = re.match(r'^(?:static\s+)?(?:inline\s+)?[A-Za-z_][\w\s\*]*?\b(\w+)\s*\(', l)
    if m and not l.rstrip().endswith(';'):
        # find opening brace
        for k in range(i, min(i + 12, len(src))):
            if src[k].startswith('{'):
                spans.append((i + 1, m.group(1)))
                break
            if src[k].rstrip().endswith(';'):
                break
starts = [s for s, _ in spans]
sites = [i + 1 for i, l in enumerate(src) if re.search(os.environ.get('SITE_RE', r'__LINE__'), l)]
def func_of(line):
    k = bisect.bisect_right(starts, line) - 1
    return spans[k][1] if k >= 0 else None
norm = lambda s: re.sub(r'0x[0-9a-f]+ <[^>]*>', '<T>', re.sub(r'^ *[0-9a-f]+:\s*', '', s)).replace('\t', ' ')
cache = {}
def deltas(fn):
    if fn in cache:
        return cache[fn]
    da = [norm(x) for x in subprocess.run(['python3', S, A, fn], capture_output=True, text=True).stdout.splitlines() if not x.strip().startswith(';')]
    db = [norm(x) for x in subprocess.run(['python3', S, B, fn], capture_output=True, text=True).stdout.splitlines() if not x.strip().startswith(';')]
    sm = difflib.SequenceMatcher(None, da, db, autojunk=False)
    d = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'replace' and i2 - i1 == j2 - j1:
            for x, y in zip(da[i1:i2], db[j1:j2]):
                mx = re.match(r'(mov w\d+), #(0x[0-9a-f]+|\d+)$', x); my = re.match(r'(mov w\d+), #(0x[0-9a-f]+|\d+)$', y)
                if mx and my and mx.group(1) == my.group(1):
                    a, b = int(mx.group(2), 0), int(my.group(2), 0)
                    d.setdefault(b, set()).add(a - b)
    cache[fn] = d
    return d
known = []
for s in sites:
    fn = func_of(s)
    if fn is None or fn not in st:
        continue
    if st[fn] == 'BYTE-IDENTICAL':
        known.append((s, 0, fn)); continue
    d = deltas(fn)
    # the __LINE__ value is s (or a line of a multi-line macro call; accept s..s+3)
    for c in (s, s - 1, s - 2, s - 3):
        if c in d and len(d[c]) == 1:
            known.append((s, d[c].pop(), fn)); break
import os
if os.environ.get('ALL'):
    lo,hi=map(int,os.environ['ALL'].split(','))
    for s_,dl_,fn_ in known:
        if lo<=s_<=hi: print('  site',s_,dl_,fn_)
prev = None
for s, dl, fn in known:
    if prev is None or dl != prev[1]:
        print(f'{"" if prev is None else prev[0]:>6} -> {s:<6} delta {"" if prev is None else prev[1]:>4} -> {dl:<4}  ({fn})')
    prev = (s, dl, fn)
print('last known', prev)
