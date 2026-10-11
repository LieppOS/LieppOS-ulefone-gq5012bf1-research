#!/usr/bin/env python3
"""Prepare compare-and-swap FIELD deltas; never edit the live canonical audit."""
from pathlib import Path
import csv,json,hashlib,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent
base=list(csv.DictReader((P/'evidence/baseline/ALL-458-MODULES.tsv').open(),delimiter='\t'))
live=ROOT/'ulefone-gq5012bf1-research';file=live/'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv';now=list(csv.DictReader(file.open(),delimiter='\t'));by={r['module_id']:r for r in now}
proof=json.loads((P/'evidence/fresh-clones/result.json').read_text());assert proof['newly_certified']==0
commits={r['name']:r['commit'] for r in proof['source_commits']};results={r['module']:r for r in json.loads((P/'evidence/final/full-acceptance/summary.json').read_text())}
delta=[];drift=[];ids=[];prefix='reverse-engineering/kernel-source-reconstruction/USB-TYPEC-CLOSURE/'
for row in base:
 m=row['filename'].removesuffix('.ko')
 if m not in results:continue
 id=row['module_id'];ids.append(id);current=by[id];assert current['source_status']=='C'
 changed={k:[row[k],current[k]] for k in row if row[k]!=current[k]}
 if changed:drift.append({'module_id':id,'changed_fields':changed})
 source='android_kernel_modules_charging_battery_ulefone_gq5012bf1' if m in ['charger_class','mtk_chg_type_det'] else 'android_kernel_modules_usb_typec_ulefone_gq5012bf1'
 msg='Srcversion-only raw OEM source-token/dependency lineage remains unavailable; instructions/data except fingerprint, ABI and relocations exact; no metadata waiver'
 if m=='tcpc_mt6375':msg='66/66 code exact; genuine license/version order restored; unknown +1 counter prefix and natural srcversion remain; no fabricated declarations or metadata'
 if m=='tcpc_class':msg='709/709 instruction bodies/positions and 113/114 data objects exact, including all54 timers; natural srcversion, six source-line diagnostic strings/37 BUG lines and string-pool relocations remain; no A/B waiver'
 changes={'source_commit':commits[source],'exact_functions':str(results[m]['axes']['functions']['body_exact']),'unresolved_functions':str(results[m]['axes']['functions']['stock_count']-results[m]['axes']['functions']['body_exact']),'verified_difference_classification':'UNACCEPTED:'+msg,'blocker':msg,'parity_evidence':current['parity_evidence']+';'+prefix+'evidence/final/full-acceptance/'+m+'/result.json;'+prefix+'evidence/fresh-clones/result.json;'+prefix+'evidence/mutation-tests/result.json'}
 for key,value in changes.items():
  if current[key]!=value:delta.append({'module_id':id,'filename':row['filename'],'field':key,'expected_before':current[key],'proposed_after':value,'integration_condition':'Only after reconciling concurrent work and integrating matching maintained source commits/evidence; re-run validators. No class promotion.'})
with (P/'AUDIT-DELTA.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['module_id','filename','field','expected_before','proposed_after','integration_condition'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(delta)
counts={c:sum(r['source_status']==c for r in now) for c in 'ABCDEFG'};assert len(now)==458
j={'canonical_base_at_task_start':json.loads((P/'STATE.json').read_text())['canonical_base'],'canonical_head_at_delta_preparation':subprocess.check_output(['git','-C',str(live),'rev-parse','HEAD'],text=True).strip(),'canonical_audit_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'live_audit_edited':False,'selected_module_ids':ids,'selected_field_drift_since_base':drift,'fields_proposed':len(delta),'source_class_changes':0,'newly_certified':0,'current_counts':counts,'certified_before':counts['A']+counts['B'],'certified_after_if_delta_applied':counts['A']+counts['B'],'remaining_before':458-counts['A']-counts['B'],'remaining_after_if_delta_applied':458-counts['A']-counts['B'],'unselected_rows_preserved':453,'runtime_and_owner_fields_changed':False,'instruction_count_is_not_complete_acceptance':True}
(P/'evidence/audit-delta.json').write_text(json.dumps(j,indent=2)+'\n');print('FIELD deltas',len(delta),'new certifications0; live audit unchanged',j['certified_before'],'/',j['remaining_before'])
