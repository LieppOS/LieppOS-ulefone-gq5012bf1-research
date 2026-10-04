#!/usr/bin/env python3
"""classify.py BUILD_KO PARITY_DIR [OBJ...]
Classify every non-byte-identical shared function:
  LINE   only `mov wN,#imm` immediates differ (pr_fmt/__LINE__ style), same length
  RELOC  only relocation-target comments differ (layout-only)
  CODE   anything else (prints first differing hunk)
"""
import sys, subprocess, re, difflib, os
S = '/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/display-input/rear-display-input/scripts/symdis.py'
A = '/home/armol/kernel-work/gki-12901745-workspace/lieppos/drm/stock-mediatek-drm.ko'
B, PD = sys.argv[1:3]
objs = sys.argv[3:]
st = {}
for l in open(PD + '/function-parity.tsv').read().splitlines()[1:]:
    c = l.split('\t'); st[c[0]] = c
names = None
if objs:
    names = []
    for o in objs:
        out = subprocess.run(['llvm-nm', '--defined-only', os.path.join(os.path.dirname(B), o)], capture_output=True, text=True).stdout
        names += [l.split()[2] for l in out.splitlines() if len(l.split()) == 3 and l.split()[1] in 'tT']
else:
    names = list(st)
norm = lambda s: re.sub(r'0x[0-9a-f]+ <[^>]*>', '<T>', re.sub(r'^ *[0-9a-f]+:\s*', '', s)).replace('\t', ' ')
VERB = os.environ.get('V')
for n in names:
    c = st.get(n)
    if not c or c[3] in ('BYTE-IDENTICAL', 'ONE-SIDED'):
        continue
    da = [norm(x) for x in subprocess.run(['python3', S, A, n], capture_output=True, text=True).stdout.splitlines()]
    db = [norm(x) for x in subprocess.run(['python3', S, B, n], capture_output=True, text=True).stdout.splitlines()]
    sm = difflib.SequenceMatcher(None, da, db, autojunk=False)
    kinds = set(); first = None; lines = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        if tag == 'replace' and i2 - i1 == j2 - j1:
            ok = True
            for x, y in zip(da[i1:i2], db[j1:j2]):
                if x.strip().startswith(';') and y.strip().startswith(';'):
                    kinds.add('RELOC'); continue
                mx = re.match(r'(mov w\d+), #(0x[0-9a-f]+|\d+)$', x); my = re.match(r'(mov w\d+), #(0x[0-9a-f]+|\d+)$', y)
                if mx and my and mx.group(1) == my.group(1):
                    kinds.add('LINE'); lines.append(int(mx.group(2), 0) - int(my.group(2), 0)); continue
                ok = False
            if ok:
                continue
        kinds.add('CODE')
        if first is None:
            first = (da[i1:i2][:6], db[j1:j2][:6])
    k = 'CODE' if 'CODE' in kinds else ('LINE' if 'LINE' in kinds else 'RELOC')
    print(f'{k}\t{n}\t{c[1]}/{c[2]}\t' + (f'dl={sorted(set(lines))}' if lines else '') + (f'\t{first}' if (k == 'CODE' and VERB) else ''))
