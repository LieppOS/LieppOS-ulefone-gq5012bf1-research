#!/usr/bin/env python3
"""linemap.py BUILD_KO PARITY_DIR OBJMAP_DIR OBJECT [maxline]
For every non-identical function of OBJECT, pair A/B instructions that differ only by an
immediate (mov wN,#imm) and print (B_imm -> A_imm, delta) sorted by B_imm: a __LINE__ shift map.
"""
import sys, subprocess, re, difflib, collections
S = '/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/display-input/rear-display-input/scripts/symdis.py'
A = '/home/armol/kernel-work/gki-12901745-workspace/lieppos/drm/stock-mediatek-drm.ko'
B, PD, OM, OBJ = sys.argv[1:5]
maxl = int(sys.argv[5]) if len(sys.argv) > 5 else 20000
funcs = []
for l in open(OM + '/object-groups.tsv').read().splitlines()[1:]:
    c = l.split('\t')
    if c[0] == OBJ:
        pass
st = {}
for l in open(PD + '/function-parity.tsv').read().splitlines()[1:]:
    c = l.split('\t'); st[c[0]] = c[3]
# functions of object from objmap's assignment: recompute quickly via B .o symbol table
import os
o = os.path.join(os.path.dirname(B), OBJ)
out = subprocess.run(['llvm-nm', '--defined-only', o], capture_output=True, text=True).stdout
names = [l.split()[2] for l in out.splitlines() if l.split()[1] in 'tT']
norm = lambda s: re.sub(r'0x[0-9a-f]+ <[^>]*>', '<T>', re.sub(r'^ *[0-9a-f]+:\s*', '', s)).replace('\t', ' ')
pairs = collections.defaultdict(set)
for n in names:
    if st.get(n) == 'BYTE-IDENTICAL':
        continue
    da = [norm(x) for x in subprocess.run(['python3', S, A, n], capture_output=True, text=True).stdout.splitlines() if not x.strip().startswith(';')]
    db = [norm(x) for x in subprocess.run(['python3', S, B, n], capture_output=True, text=True).stdout.splitlines() if not x.strip().startswith(';')]
    sm = difflib.SequenceMatcher(None, da, db, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'replace' and i2 - i1 == j2 - j1:
            for x, y in zip(da[i1:i2], db[j1:j2]):
                mx = re.match(r'(mov w\d+), #(0x[0-9a-f]+|\d+)$', x)
                my = re.match(r'(mov w\d+), #(0x[0-9a-f]+|\d+)$', y)
                if mx and my and mx.group(1) == my.group(1):
                    a, b = int(mx.group(2), 0), int(my.group(2), 0)
                    if 20 < b < maxl and abs(a - b) < 400:
                        pairs[b].add((a - b, n))
for b in sorted(pairs):
    ds = sorted(set(d for d, _ in pairs[b]))
    print(b, ds, sorted(set(f for _, f in pairs[b]))[:3])
