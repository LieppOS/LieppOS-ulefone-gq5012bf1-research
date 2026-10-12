#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,hashlib,shutil,os
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2].parent;W=Path('/home/armol/kernel-work/g-source-recovery-batch-02')
for fam,tag in [('camera_aux','D4'),('biometric_transport','D4')]:
 S=ROOT/('android_kernel_modules_'+fam+'_ulefone_gq5012bf1');rows=json.loads((P/'evidence/development'/(fam+'-'+tag)/'ACTUAL-RESULTS.json').read_text());assert all(r['compiled'] for r in rows);plan=dict(A=[r['module'] for r in rows if r['strict_stock']=='PASS'],C={r['module']:dict(functions=f"{r['functions_exact']}/{r['functions_total']}",data=f"{r['data_exact']}/{r['data_total']}",nonGNU_sections=r['nonGNU_section_residuals'],imports=r['import_residuals'],provenance_gap='LiteralOEMglue/headerlist notfound; pure-Ccandidateprovenance explicit' if r['module']=='fingerprint' else 'Original exactsourcegeneration/sourcecode scheduling/dataorder/metadata provenance notfound; do not waive') for r in rows if r['strict_stock']!='PASS'},provider_errors=json.loads((W/'dev'/(fam+'-D1')/'out'/tag/'provider/provider-errors.json').read_text()),normalization='UNCHANGED_GNU20_ONLY; C strictREJECT required not waived')
 (S/'reference/acceptance-plan.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copyfile(P/'scripts/verify-planned.py',S/'scripts/verify-planned.py');shutil.copyfile(P/'scripts/mutation-accepted.py',S/'scripts/mutation-accepted.py')
 (S/'scripts/build-reproducible.sh').write_text('''#!/bin/bash
# Complete-source reproduction only; strictA andC classification gate separately.
set -euo pipefail
R=$(cd "$(dirname "$0")/.." && pwd); WS=${1:?}; TAG=${2:?}
set +e
bash "$R/scripts/bulk-build.sh" "$WS" "$TAG"
RC=$?
set -e
python3 - "$R" "$WS/out/$TAG" "$RC" <<'PY'
from pathlib import Path
import csv,json,sys
R,O=map(Path,sys.argv[1:3]);p=json.loads((R/'reference/acceptance-plan.json').read_text());assert (O/'object-exit').read_text().strip()=='0';assert (O/'module-exit').read_text().strip()=='0';actual=json.loads((O/'provider/provider-errors.json').read_text());assert actual==p['provider_errors'],(actual,p['provider_errors']);assert int(sys.argv[3])==(1 if actual else 0)
for r in csv.DictReader((R/'reference/BATCH-MANIFEST.tsv').open(),delimiter='\\t'):
 m=r['filename'].removesuffix('.ko');assert (O/(m+'.ko')).exists() and (O/(m+'.stripped')).exists()
print('Complete source compile/link; naturalCRC residuals visible:',actual,'NOTSTOCKACCEPTANCE')
PY
''');print(fam,'Adevelopment',plan['A'],'Cstrictrejections',list(plan['C']),'actualsourceprovidererrors',plan['provider_errors'])
