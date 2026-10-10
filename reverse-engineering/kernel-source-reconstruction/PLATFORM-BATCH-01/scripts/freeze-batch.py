#!/usr/bin/env python3
"""Freeze 35 authoritative D-class platform identities before any compilation."""
import csv,hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit'
families={
'CMDQ-MAILBOX':'cmdq-platform-mt6878 cmdq-sec-drv cmdq-test mtk-cmdq-drv-ext cmdq_helper_inf'.split(),
'IOMMU-AUX':'iommu_debug iommu_secure iommu_test'.split(),
'SMI-PLATFORM':'mtk-smi mtk-smi-dbg'.split(),
'MTK-POWER-PLATFORM':'clk-bringup clk-chk-mt6878 clk-dbg-mt6878 clk-disable-unused clk-mt6878-cam clk-mt6878-ccu clk-mt6878-img clk-mt6878-mmsys mtk-dvfsrc mtk-dvfsrc-start mtk-dvfsrc-devfreq mtk-dvfsrc-helper mtk-scpsys mtk-scpsys-bringup mtk-scpsys-mt6878 mtk-pm-domain-disable-unused mtk-mmdvfs mtk-mmdvfs-v3 irq-dbg mtk-uart-apdma device-apc-common device-apc-mt6878 mt6338-core mtk-pmic-wrap mtk-socinfo'.split()}
pins={'alps':'5e415e059253ce0d2e61c97108e5f5785d71f06f','kdm_config':'957dac185efe46cbf6336b0fff9516d84c8cd78f','common':'6b18f0b574ab3267615ae6ce642d5a7c3c21ac09','clang':'7775eb113f960bc69a780b621d03a715914d4bca'}
assert not (P/'BATCH-MANIFEST.tsv').exists(),'Frozen manifest already exists: never overwrite'
rows=list(csv.DictReader((A/'ALL-457-MODULES.tsv').open(),delimiter='\t'));s=json.loads((A/'evidence/audit-summary.json').read_text())
assert len(rows)==len({r['module_id'] for r in rows})==458 and s['verified_A_B']==129 and s['unverified_and_unexcluded']==329
names={n:f for f,ns in families.items() for n in ns};selected=[r for r in rows if r['filename'].removesuffix('.ko') in names];assert len(selected)==len(names)==35 and all(r['source_status']=='D' for r in selected)
fields=['module_id','filename','initial_class','canonical_owner','component_status','source_owner','initial_source_group','donor','donor_commit','dependency_group','candidate_directory','candidate_configs','stock_sha256','stock_size','stock_paths','load_phase','stock_functions','stock_data_objects','stock_imports','stock_exports','stock_kcfi_abs_ids','stock_relocations']
with (P/'BATCH-MANIFEST.tsv').open('w') as o:
 w=csv.DictWriter(o,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader()
 for r in sorted(selected,key=lambda r:(names[r['filename'].removesuffix('.ko')],r['filename'])):
  x={k:r[k] for k in fields if k in r};x.update(initial_class=r['source_status'],canonical_owner=r['component_owner'],initial_source_group=r['source_group'],donor='MediaTek ALPS public KDM',donor_commit=pins['alps'],dependency_group=names[r['filename'].removesuffix('.ko')],candidate_directory=r['candidate_path'].split('device_modules/')[-1]);w.writerow(x)
(P/'evidence/baseline').mkdir(parents=True)
for name in ['ALL-457-MODULES.tsv','SOURCE-OWNERSHIP.tsv','evidence/audit-summary.json','evidence/workspace-baseline.json']:
 (P/'evidence/baseline'/Path(name).name).write_bytes((A/name).read_bytes())
h=hashlib.sha256((P/'BATCH-MANIFEST.tsv').read_bytes()).hexdigest();(P/'BATCH-MANIFEST.sha256').write_text(h+'  BATCH-MANIFEST.tsv\n')
ids={r['module_id'] for r in selected};edges=list(csv.DictReader((A/'DEPENDENCY-EDGES.tsv').open(),delimiter='\t'));edges=[e for e in edges if e['consumer_module_id'] in ids]
with (P/'DEPENDENCIES.tsv').open('w') as o:
 w=csv.DictWriter(o,fieldnames=list(edges[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(edges)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
state={'schema':1,'phase':'MANIFEST_FROZEN_NOT_COMPILED','baseline_research_commit':head,'baseline_certified':129,'baseline_uncertified':329,'manifest_sha256':h,'selected_count':35,'families':families,'source_pins':pins,'completed_modules':[],'current_module':None,'failed_modules':{},'remaining_modules':[r['filename'] for r in selected],'build_directories':{'development':'/home/armol/kernel-work/platform-batch-01-dev','cleancheck':'/home/armol/kernel-work/platform-batch-01-cleancheck','immutable_mirror':'/home/armol/kernel-work/interconnect-pin-mirror'},'latest_successful_verification':'Canonical audit validator PASS, zero errors before any batch compilation','relevant_commits':{'baseline_research':head},'safety':'Offline mirrors only; no hardware operations; local commits only'}
(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n')
print('FROZEN',len(selected),'identities',h,'dependency edges',len(edges))
