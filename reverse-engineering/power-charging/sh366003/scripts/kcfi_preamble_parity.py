#!/usr/bin/env python3
"""Compare the KCFI type-id word preceding every function of two .ko files and
name the prototype through reverse-engineering/scripts/ko-kcfi-typeid.py.
usage: kcfi_preamble_parity.py stock.ko rebuilt.ko [out.tsv]"""
import subprocess, sys, re, struct, os, importlib.util
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('k', os.path.join(here, '..', '..', '..', 'scripts', 'ko-kcfi-typeid.py'))
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
PROTOS = {
 '_ZTSFiP12power_supply21power_supply_propertyP20power_supply_propvalE': 'int (struct power_supply *, enum power_supply_property, union power_supply_propval *)',
 '_ZTSFvP12power_supplyE': 'void (struct power_supply *)',
 '_ZTSFvP11work_structE': 'void (struct work_struct *)',
 '_ZTSFlP5classP15class_attributePcE': 'ssize_t (struct class *, struct class_attribute *, char *)',
 '_ZTSFlP5classP15class_attributePKcmE': 'ssize_t (struct class *, struct class_attribute *, const char *, size_t)',
 '_ZTSFiP10i2c_clientPK13i2c_device_idE': 'int (struct i2c_client *, const struct i2c_device_id *)',
 '_ZTSFvP10i2c_clientE': 'void (struct i2c_client *)',
 '_ZTSFivE': 'int (void)', '_ZTSFvvE': 'void (void)',
 '_ZTSFiP10sh_fg_chipPcE': 'int (struct sh_fg_chip *, char *)',
 '_ZTSFbP10i2c_clientE': 'bool (struct i2c_client *)'}
REV = {k.kcfi(m) & 0xffffffff: (m, d) for m, d in PROTOS.items()}
def info(ko):
    b = open(ko, 'rb').read(); sec = {}
    for l in subprocess.check_output(['llvm-readelf', '-S', '-W', ko]).decode().split('\n'):
        m = re.search(r'\[\s*(\d+)\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)', l)
        if m: sec[int(m.group(1))] = int(m.group(3), 16)
    fs = []
    for l in subprocess.check_output(['llvm-readelf', '-s', '-W', ko]).decode().split('\n'):
        p = l.split()
        if len(p) >= 8 and p[3] == 'FUNC' and p[6].isdigit(): fs.append((int(p[6]), int(p[1], 16), int(p[2]), p[7]))
    out = {}
    for s, v, sz, n in fs:
        end = max([v2 + z2 for s2, v2, z2, _ in fs if s2 == s and v2 < v] or [0])
        out[n] = struct.unpack('<I', b[sec[s] + v - 4:sec[s] + v])[0] if v - 4 >= end else None
    return out
A, B = info(sys.argv[1]), info(sys.argv[2])
rows = ['function\tstock_kcfi\trebuilt_kcfi\tmangled\tprototype\tresult']
for n in sorted(A):
    a, b = A[n], B.get(n)
    if a is None and b is None: rows.append(f'{n}\t-\t-\t-\t(no KCFI preamble: not address-taken)\tEXACT'); continue
    m, d = REV.get(a, ('?', '?'))
    rows.append(f'{n}\t0x{a:08x}\t0x{(b or 0):08x}\t{m}\t{d}\t{"EXACT" if a == b else "DIFF"}')
txt = '\n'.join(rows) + '\n'
(open(sys.argv[3], 'w').write(txt) if len(sys.argv) > 3 else print(txt))
pre = [n for n in A if A[n] is not None]
print(f'functions {len(A)}/{len(B)}; KCFI preambles {len(pre)}; equal {sum(1 for n in pre if A[n] == B.get(n))}; named {sum(1 for n in pre if A[n] in REV)}', file=sys.stderr)
