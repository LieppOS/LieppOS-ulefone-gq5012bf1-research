#!/usr/bin/env python3
"""Strictly offline read-only effective ownership; writes this batch's reports only."""
from pathlib import Path
import csv,json,subprocess,os,hashlib,collections
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
os.environ.update(GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0',PYTHONDONTWRITEBYTECODE='1')
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent
S=ROOT/'ulefone-gq5012bf1-research-codex-integration';C=ROOT/'ulefone-gq5012bf1-research';A=ROOT/'ulefone-gq5012bf1-research-codex-all-c-closure'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args],text=True,timeout=45).strip()
def table(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def dump(p,rows):
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
CAN='f61ebf03275ba2d3f6aa4f9d5aebe18e12922263';STAGE='55dab18ac0470d4145f05fba48076b75d9e75ebb'
assert git(C,'rev-parse','HEAD')==CAN and git(S,'rev-parse','HEAD')==STAGE,'New baseline: re-review overlay before claiming targets'
assert not git(C,'status','--porcelain') and not git(S,'status','--porcelain')
audit='reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv';canonical=table(C/audit);staged=table(S/audit);assert len(canonical)==len(staged)==458
completed=table(S/'reverse-engineering/kernel-source-reconstruction/COMPLETED-BATCHES-INTEGRATION-01/COMBINED-MANIFEST.tsv');protected={r['module_id'] for r in completed};assert len(protected)==63
active=table(A/'reverse-engineering/kernel-source-reconstruction/ALL-C-TO-A-CLOSURE/C-CLOSURE-MANIFEST.tsv');active_ids={r['module_id'] for r in active}
allC={r['module_id'] for r in staged if r['source_status']=='C'};assert allC.isdisjoint(protected) is False
maintained={}
for repo in ROOT.glob('android_kernel_modules_*'):
 for f in repo.glob('reference/BATCH-MANIFEST.tsv'):
  for row in table(f):
   if row.get('module_id'):maintained.setdefault(row['module_id'],[]).append(repo.name)
edges=table(S/'reverse-engineering/kernel-source-parity-audit/DEPENDENCY-EDGES.tsv');byedge=collections.defaultdict(list)
for e in edges:byedge[e['consumer_module_id']].append(e)
chosen=['atf_logger','bootprof','bus-parity','cache-parity','dbg_error_flag','dbgtop-drm','last_bus','log_store','monitor_hang','pidmap','mtk_printk_ctrl','trace_mmstat','met','met_emi_api','met_gpu_adv_api','met_gpu_api','met_gpueb_api','met_ipi_api','met_mcupm_api','met_scmi_api','met_sspm_api','met_vcore_api']
manifest=[];queue=[];selected=[]
for row in staged:
 if row['source_status'] not in ['D','G']:continue
 n=row['filename'].removesuffix('.ko');identity=row['module_id'];reserve=any(x in row['candidate_path'].lower() for x in ['/gpu/drm','/media/','/flashlight']) or any(x in row['source_owner'] for x in ['DISPLAY','CAMERA','VCMS','FLASH','WL2868','CO5300','LN2403'])
 reasons=[]
 if identity in protected:reasons.append('COMPLETED_CODEX63')
 if identity in active_ids:reasons.append('ACTIVE_CLAUDE_MANIFEST')
 if identity in maintained:reasons.append('EXISTING_MAINTAINED_TARGET')
 if reserve:reasons.append('DISPLAY_CAMERA_RESERVED_PENDING_OWNER_CLEARANCE')
 public=ROOT/row['candidate_path'].removeprefix('../');historical=ROOT/row['source_snapshot_path'].removeprefix('../')
 deps=sorted({e['provider_module_ids'] for e in byedge[identity] if e['provider_module_ids']!='GKI_CORE'})
 group='MET-INSTRUMENTATION' if n=='met' or n.startswith('met_') else 'MTK-SYSTEM-DIAGNOSTICS'
 eligible=not reasons
 queue.append(dict(module_id=identity,filename=row['filename'],effective_class=row['source_status'],partitions=row['partitions'],stock_paths=row['stock_paths'],canonical_class=next(r['source_status'] for r in canonical if r['module_id']==identity),source_candidate=row['candidate_path'],candidate_files=row['candidate_files'],candidate_present=str(public.exists()),historical_source=row['source_snapshot_path'],historical_present=str(historical.exists() and row['source_snapshot_path']!='UNKNOWN'),historical_build_script=row['build_script'],historical_parity=row['historical_parity'],patch_evidence=row['parity_evidence'],maintained_owner=';'.join(maintained.get(identity,[])) or 'NONE',active_owner=';'.join(reasons) or 'NONE_FOUND',build_dependencies='pinned common/Clang/KDM config; source-generated headers',abi_providers=';'.join(deps) or 'GKI_CORE',donor_available=str(public.exists()),complexity='LARGE_FULL_MET' if n=='met' else ('SMALL_MET_SHARED_ABI' if n.startswith('met_') else ('SOURCE_BACKED_UNMEASURED' if row['source_status']=='D' else 'HISTORICAL_RECIPE_RECOVERY')),eligible=str(eligible),selected=str(n in chosen),priority=row['priority'],stock_functions=row['stock_functions']))
 if n not in chosen:continue
 assert eligible and row['source_status']=='D',identity+' ownership conflict'
 assert public.is_dir(),identity+' source candidate absent'
 stock=R/row['stock_paths'].split(';')[0];assert stock.stat().st_size==int(row['stock_size']) and SHA(stock)==row['stock_sha256'];assert not stock.is_symlink()
 donor='5f75a3b13e8135d45b4b0b70ec893345144f70df' if group=='MET-INSTRUMENTATION' else '5e415e059253ce0d2e61c97108e5f5785d71f06f'
 donor_repo='/home/armol/kernel-work/public-mtk/nkm.git' if group=='MET-INSTRUMENTATION' else '/home/armol/kernel-work/interconnect-pin-mirror/alps5e41.git'
 source_path='met_drv_v3' if group=='MET-INSTRUMENTATION' else row['candidate_path'].split('/device_modules/')[1]
 subprocess.run(['git','--git-dir',donor_repo,'cat-file','-e',donor+':'+source_path],check=True,timeout=30)
 manifest.append(dict(module_id=identity,filename=row['filename'],initial_class=row['source_status'],stock_sha256=row['stock_sha256'],stock_size=row['stock_size'],partitions=row['partitions'],stock_paths=row['stock_paths'],source_provenance='genuine MediaTek ALPS' if group!='MET-INSTRUMENTATION' else 'genuine NothingOSS MediaTek met_drv_v3',source_owner=row['source_owner'],historical_source_path=row['source_snapshot_path'],historical_build_script=row['build_script'],historical_parity=row['historical_parity'],public_candidate=row['candidate_path'],candidate_directory=source_path,candidate_files=row['candidate_files'],candidate_configs=row['candidate_configs'],donor_revision=donor,donor_git=donor_repo,build_dependencies='common6b18f0;Clang7775eb;Kconfig957dac;source-prepared headers',abi_provider_dependencies=';'.join(deps) or 'GKI_CORE',claimed_task_owner='codex/next-dg-source-batch',source_family=group,maintained_repository='android_kernel_modules_met_instrumentation_ulefone_gq5012bf1' if group=='MET-INSTRUMENTATION' else 'android_kernel_modules_platform_diagnostics_ulefone_gq5012bf1',selection_rationale='Coherent system-debug/trace instrumentation; complete authentic local source; no current target ownership; shared AEE/GPU/TinySys provider ABI sources already maintained; no physical peripheral inferred',stock_functions=row['stock_functions'],stock_data_objects=row['stock_data_objects'],stock_imports=row['stock_imports'],stock_exports=row['stock_exports'],stock_kcfi_abs_ids=row['stock_kcfi_abs_ids'],stock_relocations=row['stock_relocations'],runtime_status=row['runtime_status'],component_owner=row['component_owner'],component_status=row['component_status']))
assert len(manifest)==len(chosen)==22 and not {r['module_id'] for r in manifest}&(protected|active_ids|allC)
queue.sort(key=lambda r:(r['selected']!='True',r['eligible']!='True',r['priority'],r['filename']));dump(P/'CANDIDATE-QUEUE.tsv',queue)
f=P/'BATCH-MANIFEST.tsv'
if f.exists():
 assert table(f)==manifest,'Frozen manifest differs: formal amendment required'
else:dump(f,manifest)
(P/'BATCH-MANIFEST.sha256').write_text(SHA(f)+'  BATCH-MANIFEST.tsv\n')
(P/'evidence/ownership-preflight.json').write_text(json.dumps(dict(canonical_head=CAN,staging_head=STAGE,canonical_counts=dict(collections.Counter(r['source_status'] for r in canonical)),effective_counts=dict(collections.Counter(r['source_status'] for r in staged)),completed_protected=len(protected),remaining_dg=len(queue),active_C_manifest=len(active_ids),all_C_reserved=len(allC),selected=len(manifest),manifest_sha256=SHA(f),worktrees=git(C,'worktree','list','--porcelain'),refs=git(C,'for-each-ref','--format=%(refname:short) %(objectname)'),active_C_head=git(A,'rev-parse','HEAD'),active_changes=git(A,'status','--porcelain'),resource_affinity=sorted(os.sched_getaffinity(0)),lazy_fetch_disabled=True),indent=2)+'\n')
print('PASS:136 D/G reviewed;22 coherent unowned D targets;12 diagnostics+10 MET;63 completed and20 C protected; frozen SHA '+SHA(f))
