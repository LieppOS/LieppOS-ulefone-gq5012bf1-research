#!/usr/bin/env python3
from pathlib import Path
import json,csv,subprocess,shutil,hashlib,collections
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=Path('/home/armol/kernel-work/g-source-recovery-batch-01');E=P/'evidence';state=json.loads((P/'BATCH-STATE.json').read_text());manifest=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));proofs={};rows=[]
# Historical14-target checkpoint helper; final mixed22A/1C state uses finalize.py.
assert not (E/'independent-proof/secure_transport/RESULT.json').exists(),'Use finalize.py for completed mixed A/C proof; never misclassify C'
for fam in ['camera_lens','modem_interfaces','secure_transport']:
 f=E/'independent-proof'/fam/'RESULT.json'
 if f.exists():j=json.loads(f.read_text());assert j['result']=='PASS';proofs[fam]=dict(commit=j['commit'],scope=j['scope'],object_pairs=len(j['builds'][0]['objects']),status='PASS');d=W/(fam.replace('_','-')+'-independent-driver.log')
 if f.exists() and d.exists():shutil.copyfile(d,E/'independent-proof'/fam/'driver.log')
for r in manifest:
 fam={'CAMERA-LENS':'camera_lens','MODEM-INTERFACES':'modem_interfaces','NORMAL-WORLD-SECURE-TRANSPORT':'secure_transport'}[r['source_family']];proof=proofs.get(fam);module=r['filename'].removesuffix('.ko');src=R.parent/('android_kernel_modules_'+fam+'_ulefone_gq5012bf1');commit=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip();j={}
 if proof:j=json.loads((E/'independent-proof'/fam/'B1/acceptance/acceptance.json').read_text())[module]
 status='A_PROPOSED' if proof else 'G_PENDING_NO_PROMOTION';residual='GNU20_ONLY' if proof else 'SECURE_RELEASE_AND_NATURAL_PROVIDER_ABI_UNDER_INVESTIGATION'
 rows.append(dict(module_id=r['module_id'],module=r['filename'],initial_class='G',current_proposed_class='A' if proof else 'G',functions=str(j.get('functions','NOT_YET_ACCEPTED')),data=str(j.get('data','NOT_YET_ACCEPTED')),crc_kcfi='WHOLE_STOCK_EXACT' if proof else 'PENDING',relocations=str(j.get('relocations','PENDING')),source_repository=src.name,source_commit=proof['commit'] if proof else commit,independent_proof=proof['status'] if proof else 'NOT_COMPLETE',residual=residual));state['targets'][r['module_id']]=dict(initial='G',state=status,source_commit=proof['commit'] if proof else commit,next='Owner-reviewed source CAS only' if proof else 'Inspect secureD2 naturalAPItypes and fullpermodule residual; continue all9')
state.update(phase='14_FRESH_G_TO_A_PROPOSALS_SECURE9_SOURCE_RECOVERY_RUNNING',completed_families=proofs,new_A_proposals=sum(j['scope'] for j in proofs.values()),canonical_not_modified=True,next_action='SecureD2 per-target actual acceptance/prototype/data/symbol residuals; do not relaxprovider/stockgate; independentC/A reproduction as factual');(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n')
with (P/'BATCH-PARITY.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
print('Durable checkpoint',state['new_A_proposals'],'freshAproposals; secure9notpromoted')
