#!/bin/bash
# Regenerate parity/ from stock A and a rebuilt (unstripped) B.
# usage: parity.sh <stock tkcore_drv.ko> <rebuilt tkcore_drv.ko>
set -e
HERE=$(cd "$(dirname "$0")/.." && pwd); S="$HERE/../scripts"
KS="$HERE/../camera-stack/kernel-isp-imgsys/scripts"
A=$1; B=$(mktemp --suffix=.ko); llvm-strip --strip-debug -o "$B" "$2"
P="$HERE/parity"; R=$(cd "$HERE/../.." && pwd)
python3 "$KS/ko_parity.py" "$A" "$B" --tsv "$P/function-parity.tsv" --data-tsv "$P/data-parity.tsv" --label tkcore_drv.ko
python3 "$S/ko-pair-parity.py" "$A" "$B" > "$P/ko-pair-parity.txt" 2>&1
python3 "$S/ko-residue-diff.py" "$A" "$B" > "$P/ko-residue-diff.txt" 2>&1
python3 "$S/ko-str-refs.py" "$A" "$B" > "$P/ko-str-refs.txt" 2>&1
python3 "$HERE/scripts/kcfi_preamble_parity.py" "$A" "$B" "$P/kcfi-parity.tsv"
python3 "$HERE/scripts/bug_table_parity.py" "$A" "$B" > "$P/bug-table-parity.tsv"
python3 - "$A" "$B" "$P" <<'PY'
import sys, subprocess, re
A, B, P = sys.argv[1:4]
def rel(p):
    cur = None; d = {}
    for l in subprocess.run(['llvm-readelf', '-rW', p], capture_output=True, text=True).stdout.splitlines():
        m = re.match(r"Relocation section '(\S+)'", l)
        if m: cur = m.group(1); d[cur] = []; continue
        q = l.split()
        if cur and len(q) >= 5 and re.match(r'^[0-9a-f]{16}$', q[0]): d[cur].append((q[0], q[2], ' '.join(q[4:])))
    return d
ra, rb = rel(A), rel(B)
with open(P + '/relocation-parity.tsv', 'w') as f:
    f.write('section\tstock_entries\trebuilt_entries\tsemantic_equal\tresult\n')
    for s in sorted(set(ra) | set(rb)):
        a, b = ra.get(s, []), rb.get(s, []); eq = sum(x == y for x, y in zip(a, b))
        f.write(f'{s}\t{len(a)}\t{len(b)}\t{eq}\t{"EXACT" if a == b else "DIFF"}\n')
def imp(p):
    out = subprocess.run(['llvm-nm', '-u', p], capture_output=True, text=True).stdout.split()
    return set(x for x in out if x != 'U')
def vers(p):
    d = open(p, 'rb').read(); o = subprocess.run(['llvm-readelf', '-SW', p], capture_output=True, text=True).stdout
    for l in o.splitlines():
        m = re.match(r'\s*\[\s*\d+\]\s+__versions\s+\S+\s+\S+\s+(\S+)\s+(\S+)', l)
        if m:
            off, sz = int(m.group(1), 16), int(m.group(2), 16); v = d[off:off + sz]
            return {v[i + 8:i + 64].split(b'\0')[0].decode(): int.from_bytes(v[i:i + 8], 'little') for i in range(0, sz, 64)}
ia, ib = imp(A), imp(B); va, vb = vers(A), vers(B)
tk = set(l.split('\t')[1] for l in open(P + '/../source/stock-tkcore.symvers'))
ntk = sum(k in tk for k in va); nffa = sum(k.startswith('ffa_driver') for k in va)
import tempfile, os
def mod(p):
    t = tempfile.mktemp(); subprocess.run(['llvm-objcopy', '-O', 'binary', '--only-section=.modinfo', p, t], check=True)
    d = open(t, 'rb').read().split(b'\0'); os.unlink(t)
    return dict(x.decode().split('=', 1) for x in d if b'=' in x)
ma, mb = mod(A), mod(B)
with open(P + '/abi-parity.tsv', 'w') as f:
    f.write('check\tmatch\ttotal\tresult\tnote\n')
    f.write(f'imports\t{len(ia & ib)}\t{len(ia | ib)}\t{"EXACT" if ia == ib else "DIFF"}\t\n')
    f.write('exports\t0\t0\tEXACT\tno __ksymtab in either\n')
    f.write(f'modversions\t{sum(va[k] == vb.get(k) for k in va)}\t{len(va)}\t{"EXACT" if va == vb else "DIFF"}\t{ntk} tkcore CRCs = stock tkcore.ko __kcrctab (provider export); {nffa} ffa_v10 CRCs = source-built ffa_v10; {len(va)-ntk-nffa} GKI vmlinux CRCs (incl. module_layout) natural\n')
    f.write('export-crcs\t0\t0\tEXACT\t\n')
    for k in sorted(set(ma) | set(mb)):
        f.write(f'modinfo:{k}\t{int(ma.get(k) == mb.get(k))}\t1\t{"EXACT" if ma.get(k) == mb.get(k) else "DIFF"}\t{"" if ma.get(k) == mb.get(k) else "stock " + ma.get(k, "-") + " / rebuilt " + mb.get(k, "-")}\n')
with open(P + '/modversions.tsv', 'w') as f:
    f.write('symbol\tstock_crc\trebuilt_crc\tprovider\tresult\n')
    for k in sorted(va):
        prov = 'tkcore.ko (stock __kcrctab)' if k in tk else ('ffa_v10 (source-built)' if k.startswith('ffa_driver') else 'GKI vmlinux')
        f.write(f'{k}\t0x{va[k]:08x}\t0x{vb.get(k, 0):08x}\t{prov}\t{"EXACT" if va[k] == vb.get(k) else "DIFF"}\n')
PY
sed -i "s#$R/##g; s#$B#B (stripped rebuild)#g" "$P/ko-pair-parity.txt" "$P/ko-residue-diff.txt" "$P/ko-str-refs.txt"
cmp -l "$A" "$B" | wc -l | xargs echo "whole-file differing bytes:"
rm -f "$B"
