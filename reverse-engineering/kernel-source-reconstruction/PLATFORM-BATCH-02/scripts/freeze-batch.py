#!/usr/bin/env python3
"""Extract exact27 handoff identities and freeze authoritative pre-build evidence."""
from pathlib import Path
import csv,json,re,hashlib,subprocess,collections
P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit';H=P.parent/'PLATFORM-BATCH-01'
assert not (P/'BATCH-MANIFEST.tsv').exists(),'Never overwrite frozen manifest'
names=re.findall(r'^- `([^`]+\.ko)`',(H/'NEXT-BATCH.md').read_text(),re.M);assert len(names)==len(set(names))==27
families={'INTERCONNECT-MEMORY':'mtk-icc-core emi emi-mpu emi-fake-eng smpu smpu-hook-v1 mtk_dramc'.split(),'PMIF-SPMI':'spmi-mtk-mpu spmi-mtk-pmif mtk-pmic-keys mtk-pmic-oc-debug'.split(),'MAILBOX-TINYSYS':'mtk-mbox mtk-mbox-mailbox mtk_rpmsg_mbox mtk_tinysys_ipi mcupm sspm_v3'.split(),'POWER-POLICY':'fhctl pd-chk-mt6878 mtk_battery_oc_throttling mtk_bp_thl mtk_cpu_power_throttling mtk_dynamic_loading_throttling mtk_gpu_power_throttling mtk_low_battery_throttling pmic_lbat_service pmic_lvsys_notify'.split()};group={m+'.ko':f for f,ns in families.items() for m in ns};assert set(group)==set(names)
allr=list(csv.DictReader((A/'ALL-457-MODULES.tsv').open(),delimiter='\t'));s=json.loads((A/'evidence/audit-summary.json').read_text());assert len(allr)==458 and s['verified_A_B']==160 and s['source_status_counts']==dict(A=159,B=1,C=8,D=147,E=0,F=0,G=143)
selected=[next(r for r in allr if r['filename']==n) for n in names];assert len({r['module_id'] for r in selected})==27 and collections.Counter(r['source_status'] for r in selected)=={'D':21,'G':6}
fields=['module_id','filename','initial_class','canonical_owner','component_status','source_owner','initial_source_group','dependency_group','candidate_directory','candidate_configs','stock_sha256','stock_size','stock_paths','load_phase','stock_functions','stock_data_objects','stock_imports','stock_exports','stock_kcfi_abs_ids','stock_relocations','historical_source_snapshot','historical_build_script','historical_parity_evidence','historical_parity','public_source_commit']
with (P/'BATCH-MANIFEST.tsv').open('w') as o:
 w=csv.DictWriter(o,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader()
 for r in selected:
  x={k:r[k] for k in fields if k in r};x.update(initial_class=r['source_status'],canonical_owner=r['component_owner'],initial_source_group=r['source_group'],dependency_group=group[r['filename']],candidate_directory=r['candidate_path'].split('device_modules/')[-1],historical_source_snapshot=r['source_snapshot_path'],historical_build_script=r['build_script'],historical_parity_evidence=r['parity_evidence'],public_source_commit='5e415e059253ce0d2e61c97108e5f5785d71f06f');w.writerow(x)
E=P/'evidence/baseline';E.mkdir(parents=True)
for n in ['ALL-457-MODULES.tsv','SOURCE-OWNERSHIP.tsv','evidence/audit-summary.json','evidence/workspace-baseline.json']:(E/Path(n).name).write_bytes((A/n).read_bytes())
(E/'selected-original-rows.json').write_text(json.dumps(selected,indent=2)+'\n')
ids={r['module_id'] for r in selected};edges=[e for e in csv.DictReader((A/'DEPENDENCY-EDGES.tsv').open(),delimiter='\t') if e['consumer_module_id'] in ids]
with (P/'DEPENDENCIES.tsv').open('w') as o:
 w=csv.DictWriter(o,fieldnames=list(edges[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(edges)
h=hashlib.sha256((P/'BATCH-MANIFEST.tsv').read_bytes()).hexdigest();(P/'BATCH-MANIFEST.sha256').write_text(h+'  BATCH-MANIFEST.tsv\n');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();pins=json.loads((H/'BATCH-STATE.json').read_text())['source_pins']
state={'schema':2,'phase':'MANIFEST_FROZEN_NOT_COMPILED','baseline_research_commit':head,'baseline_certified':160,'baseline_uncertified':298,'manifest_sha256':h,'selected_count':27,'families':families,'source_pins':pins,'completed_modules':[],'current_module':None,'failed_modules':{},'remaining_modules':names,'build_directories':{'development':'/home/armol/kernel-work/platform-batch-02-dev','cleancheck':'/home/armol/kernel-work/platform-batch-02-cleancheck','immutable_mirror':'/home/armol/kernel-work/interconnect-pin-mirror'},'latest_successful_verification':'Canonical458 audit validator PASS zero errors','relevant_commits':{'baseline_research':head},'next_immediate_action':'Recover six G historical inputs and prepare shared scoped source recipes','safety':'Strict offline, local commits; no phone, firmware commands or push'};(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n');print('FROZEN27',h,'imports',len(edges),'classes21D6G')
