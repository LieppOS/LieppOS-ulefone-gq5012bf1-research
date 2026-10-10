#!/usr/bin/env python3
"""Freeze actual30 Batch03 handoff against458 canonical IDs before implementation."""
from pathlib import Path
import csv,json,hashlib,subprocess,collections
P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit';H=P.parent/'PLATFORM-BATCH-03'
assert not (P/'BATCH-MANIFEST.tsv').exists(),'Immutable manifest already frozen'
rows=lambda p:list(csv.DictReader(p.open(),delimiter='\t'));allr=rows(A/'ALL-457-MODULES.tsv');proposal=rows(H/'evidence/NEXT-BATCH-PROPOSAL.tsv');s=json.loads((A/'evidence/audit-summary.json').read_text())
assert len(allr)==458 and s['stock_occurrences']==471 and s['verified_A_B']==220 and s['source_status_counts']==dict(A=219,B=1,C=9,D=98,E=0,F=0,G=131)
md=[]
for line in (H/'NEXT-BATCH.md').read_text().splitlines():
 if line.startswith('| `'):
  cells=[x.strip() for x in line.split('|')[1:-1]];assert len(cells)==4;md.append((cells[0].strip('`'),cells[1],cells[2],cells[3].strip('`')))
assert len(md)==len(proposal)==30 and len({x[3] for x in md})==30
assert md==[(r['filename'],r['current_class'],r['canonical_owner'],r['module_id']) for r in proposal]
selected=[];families={};repos={'CHARGER-GAUGE-ADC':'android_kernel_modules_charging_battery_ulefone_gq5012bf1','TYPEC-PD-MUX':'android_kernel_modules_usb_typec_ulefone_gq5012bf1','USB-HOST-GADGET-PHY':'android_kernel_modules_usb_platform_ulefone_gq5012bf1'}
for p in proposal:
 matches=[r for r in allr if r['module_id']==p['module_id']];assert len(matches)==1;r=matches[0]
 for x,y in [('filename','filename'),('source_status','current_class'),('component_owner','canonical_owner'),('stock_sha256','stock_sha256'),('stock_paths','stock_paths'),('source_owner','source_owner')]:assert r[x]==p[y],(r['filename'],'stale handoff',x)
 for f in r['stock_paths'].split(';'):
  b=(R/f).read_bytes();assert len(b)==int(r['stock_size']) and hashlib.sha256(b).hexdigest()==r['stock_sha256']
 selected.append(r);families.setdefault(p['family'],[]).append(r['filename'].removesuffix('.ko'))
assert collections.Counter(r['source_status'] for r in selected)=={'D':7,'G':23}
ids={r['module_id'] for r in selected};edges=[e for e in rows(A/'DEPENDENCY-EDGES.tsv') if e['consumer_module_id'] in ids]
fields=['module_id','filename','initial_class','canonical_owner','component_status','source_owner','initial_source_group','dependency_group','candidate_directory','candidate_configs','stock_sha256','stock_size','stock_paths','load_phase','stock_functions','stock_data_objects','stock_imports','stock_exports','stock_kcfi_abs_ids','stock_relocations','historical_source_snapshot','historical_build_script','historical_parity_evidence','historical_parity','public_source_commit','public_source_url','public_source_files','source_lineage_note','build_configuration','external_providers','module_dependencies','maintained_repository','reproduction_status']
P.mkdir(parents=True,exist_ok=True)
with (P/'BATCH-MANIFEST.tsv').open('w') as o:
 w=csv.DictWriter(o,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader()
 for r,p in zip(selected,proposal):
  providers=sorted({e['provider_module_ids'] for e in edges if e['consumer_module_id']==r['module_id']});x={k:r[k] for k in fields if k in r};x.update(initial_class=r['source_status'],canonical_owner=r['component_owner'],initial_source_group=r['source_group'],dependency_group=p['family'],candidate_directory=p['candidate_directory'],historical_source_snapshot=r['source_snapshot_path'],historical_build_script=r['build_script'],historical_parity_evidence=r['parity_evidence'],public_source_commit=p['public_source_commit'],public_source_url='https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878',public_source_files=r['candidate_files'],source_lineage_note='Candidate only; recover historical whole source, all OEM patches and actual Kbuild composition before public-source build; no parity assumed',build_configuration='Verified common +957dac mgk_64_k61_defconfig; LLVM17/r487747c IAS/faddrsig; stock release6.1.115-android14-11-g945dff7bc1bf; generated headers/config hashes must be preserved',external_providers=';'.join(x for x in providers if x not in ids),module_dependencies=';'.join(providers),maintained_repository='../'+repos[p['family']]);w.writerow(x)
E=P/'evidence/baseline';E.mkdir(parents=True)
for n in ['ALL-457-MODULES.tsv','SOURCE-OWNERSHIP.tsv','evidence/audit-summary.json','evidence/workspace-baseline.json']:(E/Path(n).name).write_bytes((A/n).read_bytes())
(E/'selected-original-rows.json').write_text(json.dumps(selected,indent=2)+'\n');(E/'NEXT-BATCH-handoff.md').write_bytes((H/'NEXT-BATCH.md').read_bytes())
with (P/'DEPENDENCIES.tsv').open('w') as o:
 w=csv.DictWriter(o,fieldnames=list(edges[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(edges)
h=hashlib.sha256((P/'BATCH-MANIFEST.tsv').read_bytes()).hexdigest();(P/'BATCH-MANIFEST.sha256').write_text(h+'  BATCH-MANIFEST.tsv\n');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();pins=json.loads((H/'BATCH-STATE.json').read_text())['source_pins']
state={'schema':4,'phase':'MANIFEST_FROZEN_NOT_IMPLEMENTED','baseline_research_commit':head,'baseline_certified':220,'baseline_uncertified':238,'manifest_sha256':h,'selected_count':30,'families':families,'repositories':repos,'source_pins':pins,'completed_modules':[],'pending_modules':[r['filename'] for r in selected],'blocked_modules':{},'current_module':'Recover23 historical G sources before implementation','build_directories':{'development':'/home/armol/kernel-work/platform-batch-04-dev','cleancheck':'/home/armol/kernel-work/platform-batch-04-cleancheck','immutable_mirror':'/home/armol/kernel-work/interconnect-pin-mirror'},'latest_parity_result':'Baseline canonical validator PASS; exact handoff/source owners/hashes/stock occurrences unchanged','independent_validation_status':'NOT_STARTED','relevant_commits':{'baseline_research':head},'next_immediate_action':'Read historical USB/charger/MT6375/TCPC full recipes and compare every source unit to actual public ALPS revisions; preserve complete deltas/config/header risks; create three real subsystem maintained recipes','safety':'Strict offline; local commits only; no phone/register/role/PD/firmware commands or push'};(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n');print('FROZEN30',h,'classes7D23G imports',len(edges),'all458/471 baseline preserved')
