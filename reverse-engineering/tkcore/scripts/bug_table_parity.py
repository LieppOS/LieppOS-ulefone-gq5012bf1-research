#!/usr/bin/env python3
"""Compare __bug_table entries (WARN_ON sites: file reloc, __LINE__, flags).
usage: bug_table_parity.py stock.ko rebuilt.ko"""
import sys, subprocess, struct, re
def sec(path, name):
    for l in subprocess.run(['llvm-readelf', '-SW', path], capture_output=True, text=True).stdout.splitlines():
        m = re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+\S+\s+(\S+)\s+(\S+)', l)
        if m and m.group(2) == name:
            o, s = int(m.group(3), 16), int(m.group(4), 16); return open(path, 'rb').read()[o:o + s]
def relas(path):
    cur = None; r = {}
    for l in subprocess.run(['llvm-readelf', '-rW', path], capture_output=True, text=True).stdout.splitlines():
        m = re.match(r"Relocation section '(\S+)'", l)
        if m: cur = m.group(1); continue
        p = l.split()
        if cur == '.rela__bug_table' and len(p) >= 5 and re.match(r'^[0-9a-f]+$', p[0]): r[int(p[0], 16)] = ' '.join(p[4:])
    return r
A, B = sec(sys.argv[1], '__bug_table'), sec(sys.argv[2], '__bug_table'); ra, rb = relas(sys.argv[1]), relas(sys.argv[2])
print('idx\tsite\tfile_str\tstock_line\trebuilt_line\tflags\tresult'); ok = 0
for i in range(0, len(A), 12):
    la, fa = struct.unpack('<HH', A[i + 8:i + 12]); lb, fb = struct.unpack('<HH', B[i + 8:i + 12])
    same = (la, fa) == (lb, fb) and ra.get(i) == rb.get(i) and ra.get(i + 4) == rb.get(i + 4); ok += same
    print(f'{i // 12}\t{ra.get(i, "")}\t{ra.get(i + 4, "")}\t{la}\t{lb}\t0x{fa:x}\t{"EXACT" if same else "DIFF"}')
print(f'# {ok}/{len(A) // 12} entries identical', file=sys.stderr)
