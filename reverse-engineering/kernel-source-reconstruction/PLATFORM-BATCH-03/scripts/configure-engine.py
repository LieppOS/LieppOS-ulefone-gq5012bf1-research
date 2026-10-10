#!/usr/bin/env python3
"""Finish source-engine setup; declarations copied only from preserved genuine C."""
from pathlib import Path
import csv,json,shutil,subprocess,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[2];S=json.loads((P/'BATCH-STATE.json').read_text());N=R.parent/S['repositories']['SECURE-DIAGNOSTICS'];H=P.parent/'PLATFORM-BATCH-02';O=Path('/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1')
for f in ['bulk-build.sh','lib.sh']:
 p=N/'scripts'/f;t=p.read_text().replace('batch02','batch03').replace('bulk27','bulk34').replace('batch01','batch03');p.write_text(t)
a=N/'scripts/assemble.sh';t=a.read_text();needle='git -C "$SRC/kdm" init -q;'
insert='''# Genuine common thermal implementation and historically declared board interfaces.
git -C "$COMMON" show "$(pin common commit):drivers/thermal/thermal-generic-adc.c" > "$SRC/kdm/drivers/thermal/thermal-generic-adc.c"
cp "$REPO/reference/lieppos-charger-declarations.c" "$SRC/kdm/drivers/power/supply/lieppos-charger-declarations.c"
git -C "$SRC/kdm" add drivers/thermal/thermal-generic-adc.c drivers/power/supply/lieppos-charger-declarations.c
'''
# Verify original ALPS before overlay, then insert overlay before applying scope patches.
t=t.replace('if [ -f "$REPO/patches/0001-joint-kbuild-scope.patch" ]; then',insert+'if [ -f "$REPO/patches/0001-joint-kbuild-scope.patch" ]; then');a.write_text(t)
D=N/'reference/historical-charger';D.mkdir(exist_ok=True);declarations=['// SPDX-License-Identifier: GPL-2.0-only\n// Declaration-only ABI witness, NOT a charger implementation/certification.\n#include <linux/module.h>\n#include <linux/cache.h>\n'];proof=[]
for p,s in [('drivers/power/supply/mtk_basic_charger.c','yft_cam_open_flag'),('drivers/power/supply/mtk_charger.c','yft_long_charger_flag')]:
 f=O/p;shutil.copyfile(f,D/f.name);ls=f.read_text().splitlines();selected=[(i+1,l) for i,l in enumerate(ls) if s in l and (l.startswith('bool ') or l.startswith('int ') or l.startswith('EXPORT_SYMBOL'))];assert len(selected)==2
 declarations.extend(l+'\n' for _,l in selected);proof.append({'symbol':s,'historical_source':str(f),'preserved_source':'historical-charger/'+f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'exact_declaration_lines':selected,'boundary':'Declaration-only board object export/CRC/licence, no behavior or whole provider claim'})
(N/'reference/lieppos-charger-declarations.c').write_text(''.join(declarations));(N/'reference/charger-declaration-provenance.json').write_text(json.dumps(proof,indent=2)+'\n')
# Reuse audited acceptance tools with current batch paths/counts, not prior build operands.
for f in ['prepare-reference.py','compare-batch.py','test-acceptance.py']:
 t=(H/'scripts'/f).read_text().replace('android_kernel_modules_memory_platform_ulefone_gq5012bf1',S['repositories']['SECURE-DIAGNOSTICS']).replace('all27','all34').replace('27','34')
 (P/'scripts'/f).write_text(t)
subprocess.run(['python3',str(P/'scripts/prepare-reference.py')],check=True)
# Owned golden reference per family; joint acceptance explicitly covers all34.
for family,name in S['repositories'].items():
 n=R.parent/name
 if n!=N:
  for f in (N/'scripts').iterdir():
   if f.is_file():shutil.copyfile(f,n/'scripts'/f.name)
  for f in ['lieppos-charger-declarations.c','charger-declaration-provenance.json','provider-boundaries.json','external-provider.symvers']:shutil.copyfile(N/'reference'/f,n/'reference'/f)
  shutil.copytree(D,n/'reference/historical-charger',dirs_exist_ok=True)
 rows=list(csv.DictReader((N/'reference/stock-normalized.tsv').open(),delimiter='\t'));shutil.copyfile(N/'reference/stock-normalized.tsv',n/'reference/joint-stock-normalized.tsv')
 with (n/'reference/stock-normalized.tsv').open('w') as o:
  w=csv.DictWriter(o,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(r for r in rows if r['module'] in S['families'][family])
 for f in (n/'scripts').glob('*.sh'):f.chmod(0o755)
print('Configured five joint34 engines, source-only board declaration witness, independent acceptance refs')
