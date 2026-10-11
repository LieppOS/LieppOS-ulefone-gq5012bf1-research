#!/usr/bin/env python3
"""Read-only historical USB inputs; preprocess to private new outputs only.

New source-backed hypothesis: successful OEM BTF lineage also contains two
actually used headers (printk/dev_printk) differing from the public GKI headers.
Check whether this authentic complete common lineage explains the one extra
TCPC counter. No counter assignment, macro filler, or declaration deletion.
"""
from pathlib import Path
import difflib
import hashlib
import json
import os
import re
import shlex
import subprocess

P=Path(__file__).resolve().parents[1]
OLD=Path('/home/armol/kernel-work/usb-typec-closure-proof-debugmapped/F0-B1/ws')
NEW=Path('/home/armol/kernel-work/allc/drm/ws-B1/mtkack-tree')
OUT=Path('/home/armol/kernel-work/allc/usb-mtkack-counter');OUT.mkdir(exist_ok=True)
cmdfile=OLD/'src/kdm/drivers/misc/mediatek/typec/tcpc/.tcpc_mt6375.o.cmd'
args=shlex.split(cmdfile.read_text().splitlines()[0].split(' := ',1)[1])
assert '-c' in args and '-o' in args and ';' not in args
args[0]=str(OLD/'prebuilts/clang/host/linux-x86/clang-r487747c/bin/clang')
args[args.index('-c')]='-E';args+=['-P']
results=[]
for label,common in [('baseline',OLD/'common'),('mtkack',NEW)]:
    argv=[s.replace(str(OLD/'common'),str(common)) for s in args]
    argv[argv.index('-o')+1]=str(OUT/(label+'.i'))
    argv=['-Wp,-MMD,'+str(OUT/(label+'.d')) if s.startswith('-Wp,-MMD,') else s for s in argv]
    proc=subprocess.run(['taskset','-c','0-3','nice','-n','19',*argv],cwd=OLD/'kout',capture_output=True,text=True)
    (OUT/(label+'.log')).write_text(proc.stdout+proc.stderr)
    record=dict(label=label,cwd=str(OLD/'kout'),command=argv,exit=proc.returncode,
                common_pin='6b18f0b574ab3267615ae6ce642d5a7c3c21ac09' if label=='baseline' else 'c364c39ae8d83dfb5d72802a7718b756c238b07e')
    if proc.returncode==0:
        text=(OUT/(label+'.i')).read_text();record['preprocess_sha256']=hashlib.sha256(text.encode()).hexdigest()
        record['modinfo_counter_names']=sorted(set(re.findall(r'__UNIQUE_ID_(?:license|version|description|author|alias)\d+',text)))
        record['addressable_names']=sorted(set(re.findall(r'__UNIQUE_ID___addressable_[A-Za-z_0-9]+',text)))
    else:record['diagnostic']=proc.stderr[-2000:]
    results.append(record)
for name in ['include/linux/printk.h','include/linux/dev_printk.h']:
    a=(OLD/'common'/name).read_text().splitlines();b=(NEW/name).read_text().splitlines()
    (OUT/(Path(name).name+'.diff')).write_text('\n'.join(difflib.unified_diff(a,b,fromfile='GKI6b18/'+name,tofile='MTKACKc364/'+name,lineterm=''))+'\n')
assert all(r['exit']==0 for r in results),results
record=dict(hypothesis=__doc__,runs=results,
            counter_changed=results[0]['modinfo_counter_names']!=results[1]['modinfo_counter_names'],
            stock_license_prefix=454,scope='Preprocessing diagnostic only; no compiled module parity or fingerprint acceptance')
(OUT/'result.json').write_text(json.dumps(record,indent=2)+'\n')
print([(r['label'],r['modinfo_counter_names']) for r in results])
print('Counter changed:',record['counter_changed'])
