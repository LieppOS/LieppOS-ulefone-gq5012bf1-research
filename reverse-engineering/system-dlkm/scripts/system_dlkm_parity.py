#!/usr/bin/env python3
"""system_dlkm parity: every stock system_dlkm .ko vs the stamped GKI build (bazel-bin/common/kernel_aarch64).
Module signatures are stripped on both sides (PKCS#7 appended blocks; stock signed with Google GKI key,
rebuild with the ephemeral build key) and the remaining ELF bodies compared byte-for-byte.
usage: system_dlkm_parity.py <stock system_dlkm/lib/modules> <bazel-bin/common/kernel_aarch64>"""
import os, sys, hashlib, struct
S, B = sys.argv[1], sys.argv[2]
idx = {}
for dp, dn, fns in os.walk(B, followlinks=True):
    if '/unstripped' in dp: continue
    for f in fns:
        if f.endswith('.ko'): idx.setdefault(f, os.path.join(dp, f))
M = b'~Module signature appended~\n'
def unsign(b):
    if b.endswith(M):
        sl = struct.unpack('>I', b[-len(M)-4:-len(M)])[0]; return b[:-len(M)-12-sl], True
    return b, False
same = body = 0; rows = []
for f in sorted(os.listdir(S)):
    if not f.endswith('.ko'): continue
    s = open(os.path.join(S, f), 'rb').read(); r = idx.get(f)
    if not r: rows.append((f, 'MISSING')); continue
    r = open(r, 'rb').read()
    if s == r: same += 1; rows.append((f, 'IDENTICAL (incl. signature)')); continue
    su, ss = unsign(s); ru, rs = unsign(r)
    if su == ru: body += 1; rows.append((f, f'IDENTICAL BODY, signature differs (stock signed={ss}, rebuild signed={rs})')); continue
    nd = sum(1 for a, b in zip(su, ru) if a != b) if len(su) == len(ru) else None
    rows.append((f, f'DIFF body {len(su)} vs {len(ru)} differing_bytes={nd}'))
for r in rows: print('\t'.join(r))
print(f'# {len(rows)} modules: {same} identical incl. signature, {body} identical body (signature differs), {len(rows)-same-body} other')
