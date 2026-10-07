#!/usr/bin/env python3
"""Prove the sh_fg_probe residual is a pure register-allocation permutation.
Within the differing window, rename x22<->x25 in the rebuild and swap the two
adjacent hoisted address-materialisation pairs; the result must equal stock.
usage: probe_residual_check.py stock.ko rebuilt_stripped.ko"""
import subprocess, re, sys
def fn(ko, name='sh_fg_probe'):
    out, on = [], False
    for l in subprocess.check_output(['llvm-objdump', '-dr', '--no-show-raw-insn', ko]).decode().split('\n'):
        if re.match(r'^[0-9a-f]+ <%s>:' % name, l): on = True; continue
        if on and re.match(r'^[0-9a-f]+ <', l): break
        if not on or not l.strip(): continue
        m = re.match(r'\s+[0-9a-f]+:\s+(R_\S+\s+\S+)', l)
        if m: out[-1] += ' ; ' + m.group(1); continue
        m = re.match(r'\s+[0-9a-f]+:\s+(.*)', l)
        if m: out.append(re.sub(r'\s+', ' ', m.group(1)))
    return out
A, B = fn(sys.argv[1]), fn(sys.argv[2])
assert len(A) == len(B)
raw = [i for i in range(len(A)) if A[i] != B[i]]
print(f'instructions {len(A)}; differing {len(raw)} in window [{raw[0]},{raw[-1]}]')
def ren(s):
    s = re.sub(r'\b([wx])22\b', r'\1__T', s); s = re.sub(r'\b([wx])25\b', r'\g<1>22', s); return s.replace('__T', '25')
lo, hi = raw[0], raw[-1]
Br = B[:lo] + [ren(x) for x in B[lo:hi + 1]] + B[hi + 1:]
d = [i for i in range(len(A)) if A[i] != Br[i]]
print('after x22<->x25 renaming inside the window:', len(d), 'differ at', d)
if d:
    assert len(d) == 4 and d == list(range(d[0], d[0] + 4))
    Br[d[0]:d[0] + 4] = Br[d[0] + 2:d[0] + 4] + Br[d[0]:d[0] + 2]
left = sum(1 for i in range(len(A)) if A[i] != Br[i])
print('after swapping the two independent adrp/add pairs:', left, 'differ')
print('VERDICT:', 'REGISTER-ALLOCATION PERMUTATION ONLY' if left == 0 else 'NOT A PURE PERMUTATION')
for i in raw: print(f'  {i}: A {A[i][:70]} | B {B[i][:70]}')
