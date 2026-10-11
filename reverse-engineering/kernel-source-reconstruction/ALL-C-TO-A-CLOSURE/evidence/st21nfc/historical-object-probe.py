#!/usr/bin/env python3
"""Replay preserved compile flags with isolated source, dependency and object outputs.
No historical or stock files are modified. Object-level experiment, not a full recipe.
"""
from pathlib import Path
import json
import shlex
import subprocess
import sys

root = Path('/home/armol/kernel-work/allc/st21')
hist = Path('/home/armol/kernel-work/gki-12901745-workspace/lieppos/nfc')
cmdfile = hist / 'kernel_device_modules-6.1/drivers/misc/mediatek/nfc/st21nfc/.st21nfc.o.cmd'
source, output = map(lambda x: Path(x).resolve(), sys.argv[1:])
args = shlex.split(cmdfile.read_text().splitlines()[0].split(' := ', 1)[1])
args[0] = '/home/armol/kernel-work/allc/cmdq-ws/prebuilts/clang/host/linux-x86/clang-r487747c/bin/clang'
args[args.index('-o') + 1] = str(output)
args[-1] = str(source)
args = ['-Wp,-MMD,' + str(output.with_suffix('.d')) if x.startswith('-Wp,-MMD,') else x for x in args]
result = subprocess.run(args, cwd=hist / 'kout', capture_output=True, text=True)
output.with_suffix('.log').write_text(result.stdout + result.stderr)
output.with_suffix('.command.json').write_text(json.dumps(dict(cwd=str(hist/'kout'), argv=args), indent=2) + '\n')
print('compiler exit', result.returncode)
if result.returncode:
    print(result.stderr[-3000:])
sys.exit(result.returncode)
