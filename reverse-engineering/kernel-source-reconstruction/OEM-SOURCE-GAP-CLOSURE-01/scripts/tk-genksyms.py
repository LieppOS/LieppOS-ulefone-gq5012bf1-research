#!/usr/bin/env python3
"""Natural genksyms CRCs for every EXPORT_SYMBOL translation unit of a TrustKernel tkcore source tree.

Reuses the recorded ALL-C-TO-A-CLOSURE preprocessing argv (pinned GKI 12901745 kout, clang r487747c) and the
pinned scripts/genksyms/genksyms. Only the source root is substituted. No CRC is written into any source or
symvers; output is a JSON report compared with stock tkcore.ko export CRCs.
usage: tk-genksyms.py <variant-src-root> <out-dir> <name>
"""
import json, os, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ARGV = Path('/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/kernel-source-reconstruction/ALL-C-TO-A-CLOSURE/evidence/tkcore-7.2.2/genksyms-argv.json')
GK = '/home/armol/kernel-work/gki-12901745-workspace/lieppos/nfc/kout/scripts/genksyms/genksyms'
OLD_ROOT = '/home/armol/kernel-work/gki-12901745-workspace/lieppos/tkcore-core-natural/srcroot/drivers/tee/tkcore'
OLD_SRC = '/home/armol/kernel-work/gki-12901745-workspace/common/../lieppos/tkcore-core-natural/src/core/tee_core.c'
STOCK = json.loads((HERE / 'stock-tkcore-export-crcs.json').read_text())
src, out, name = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), sys.argv[3]
out.mkdir(parents=True, exist_ok=True)
rec = json.loads(ARGV.read_text())
crcs, errors = {}, {}
for c in sorted(src.rglob('*.c')):
    if 'EXPORT_SYMBOL' not in c.read_text(errors='replace'):
        continue
    argv = [a.replace(OLD_ROOT, str(src)) for a in rec['argv']]
    argv[-1] = str(c)
    argv = [f'-DKBUILD_BASENAME="{c.stem}"' if a.startswith('-DKBUILD_BASENAME=') else a for a in argv]
    pp = subprocess.run(argv, cwd=rec['cwd'], capture_output=True)
    if pp.returncode:
        errors[str(c.relative_to(src))] = pp.stderr.decode()[-1500:]; continue
    st = out / f'{name}-{c.stem}.symtypes'
    g = subprocess.run([GK, '-T', str(st), '-r', '/dev/null'], input=pp.stdout, capture_output=True)
    if g.returncode:
        errors[str(c.relative_to(src))] = g.stderr.decode()[-1500:]; continue
    for m in re.finditer(r'#SYMVER (\S+) 0x([0-9a-f]+)', g.stdout.decode()):
        crcs[m.group(1)] = '0x%08x' % int(m.group(2), 16)
match = sorted(s for s in STOCK if crcs.get(s) == STOCK[s])
miss = sorted(s for s in STOCK if crcs.get(s) != STOCK[s])
res = dict(name=name, src=str(src), matches=len(match), total=len(STOCK), match=match, miss={s: [crcs.get(s), STOCK[s]] for s in miss}, errors=errors)
(out / f'{name}.json').write_text(json.dumps(res, indent=1) + '\n')
print(name, f'{len(match)}/{len(STOCK)}', 'errors', len(errors))
