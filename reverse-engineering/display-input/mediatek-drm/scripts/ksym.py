#!/usr/bin/env python3
"""ksym.py OBJ.o SYMBOL [--sub OLD=NEW ...] [--cands OLD file]
Recompute the genksyms CRC of SYMBOL exported from OBJ's source, using the exact kbuild
compile line (from .OBJ.cmd) with -E -D__GENKSYMS__ and kout/scripts/genksyms.
--cands OLD FILE: try each line of FILE as replacement token for OLD in the preprocessed
text and print matches against --want CRC.
"""
import sys, subprocess, shlex, os, re
G = '/home/armol/kernel-work/gki-12901745-workspace'
K = G + '/lieppos/nfc/kout'
obj = os.path.abspath(sys.argv[1]); sym = sys.argv[2]
d, b = os.path.split(obj)
cmd = open(f'{d}/.{b}.cmd').read().split(':=', 1)[1].split('\n')[0]
a = shlex.split(cmd)
out = []; skip = False
for x in a:
    if skip: skip = False; continue
    if x == '-o': skip = True; continue
    if x.startswith('-Wp,-MMD'): continue
    out.append(x)
src = out[-1]
cpp = out[:-1] + ['-E', '-D__GENKSYMS__', src]
env = dict(os.environ, PATH=G + '/prebuilts/clang/host/linux-x86/clang-r487747c/bin:' + os.environ['PATH'])
pre = subprocess.run(cpp, cwd=K, capture_output=True, text=True, env=env).stdout


def crc(text):
    r = subprocess.run([K + '/scripts/genksyms/genksyms', '-r', '/dev/null'], input=text, capture_output=True, text=True)
    m = re.search(r'#SYMVER ' + re.escape(sym) + r' (0x[0-9a-f]+)', r.stdout) or \
        re.search(r'SYMBOL_CRC\(' + re.escape(sym) + r',\s*(0x[0-9a-f]+)', r.stdout)
    return m.group(1) if m else None


args = sys.argv[3:]
want = None
if '--want' in args:
    want = args[args.index('--want') + 1]
subs = [x.split('=', 1) for i, x in enumerate(args) if i > 0 and args[i - 1] == '--sub']
for o, n in subs:
    pre = re.sub(r'\b' + re.escape(o) + r'\b', n, pre)
if '--cands' in args:
    i = args.index('--cands'); old, f = args[i + 1], args[i + 2]
    for c in open(f).read().split():
        v = crc(re.sub(r'\b' + re.escape(old) + r'\b', c, pre))
        if want is None or v == want:
            print(c, v)
else:
    print(sym, crc(pre))
