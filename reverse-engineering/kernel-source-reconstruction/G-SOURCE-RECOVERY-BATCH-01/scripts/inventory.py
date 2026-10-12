#!/usr/bin/env python3
"""Read-only G archaeology/ownership snapshot; writes only this task's research."""
from pathlib import Path
import subprocess,csv,json,hashlib,collections,os,re,io
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
os.environ.update(GIT_NO_LAZY_FETCH='1',GIT_ALLOW_PROTOCOL='file',GIT_TERMINAL_PROMPT='0')
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent;C=ROOT/'ulefone-gq5012bf1-research';E=P/'evidence';M=Path('/home/armol/kernel-work/interconnect-pin-mirror');ALPS='5e415e059253ce0d2e61c97108e5f5785d71f06f';D=M/'alps5e41.git';sha=lambda b:hashlib.sha256(b).hexdigest()
def git(d,*args):return subprocess.check_output(['git','-C',str(d),*args],text=True)
def donor(*args):return subprocess.check_output(['git','--git-dir',str(D),*args])
head=git(C,'rev-parse','HEAD').strip();audit='reverse-engineering/kernel-source-parity-audit';raw=git(C,'show',head+':'+audit+'/ALL-457-MODULES.tsv');allrows=list(csv.DictReader(io.StringIO(raw),delimiter='\t'));G=[r for r in allrows if r['source_status']=='G'];assert len(G)==54
(E/'baseline-ALL-457-MODULES.tsv').write_text(raw)
for f in ['SOURCE-GAPS.tsv','SOURCE-OWNERSHIP.tsv','RECONSTRUCTION-QUEUE.md','SUMMARY.md']:(E/('baseline-'+f)).write_text(git(C,'show',head+':'+audit+'/'+f))
worktrees=git(C,'worktree','list','--porcelain');(E/'worktrees-start.txt').write_text(worktrees);claims=collections.defaultdict(list);pending=set();snap=[]
for line in worktrees.splitlines():
 if not line.startswith('worktree '):continue
 w=Path(line[9:]);h=git(w,'rev-parse','HEAD').strip();dirty=git(w,'status','--porcelain');snap.append(dict(path=str(w),head=h,dirty=dirty))
 for f in w.glob('reverse-engineering/kernel-source-reconstruction/*/BATCH-MANIFEST.tsv'):
  if f.parent.name in ['BOOT-DEPENDENCY-BATCH-01','LOW-POWER-BATCH-01']:
   for r in csv.DictReader(f.open(),delimiter='\t'):pending.add(r['module_id'])
  if f.parent.name not in [p.name for p in (C/'reverse-engineering/kernel-source-reconstruction').iterdir() if p.is_dir()] and f.parent.name not in ['BOOT-DEPENDENCY-BATCH-01','LOW-POWER-BATCH-01']:
   for r in csv.DictReader(f.open(),delimiter='\t'):
    if 'module_id' in r:claims[r['module_id']].append(str(f))
(E/'ownership-overlay.json').write_text(json.dumps(dict(canonical=head,canonical_counts=dict(collections.Counter(r['source_status'] for r in allrows)),pending28_ids=sorted(pending),active_manifest_claims=dict(claims),worktrees=snap,claude_reserved='Boot/LowPower integration; MediaTekPerformance/PowerHAL/FPSGO/CPUQoS/scheduler/task_turbo/touch boost',resource=dict(fs='btrfs; zero reported inode counters mean dynamic inode allocation, not inode exhaustion',available_gib=round(os.statvfs(R).f_bavail*os.statvfs(R).f_frsize/2**30,2),estimate='three families sequential; ~30-50GiB including development and fresh B1/B2/common/Clang clones; stop checkpoint below20GiB')),indent=2)+'\n')
assert len(pending)==28 and not ({r['module_id'] for r in G}&pending)
files=donor('ls-tree','-r','--name-only',ALPS).decode().splitlines();makefiles={f:donor('show',ALPS+':'+f).decode(errors='replace') for f in files if Path(f).name in ['Makefile','Kbuild']};publicmap={};hashes=[];out=[]
for r in G:
 stem=r['filename'].removesuffix('.ko');matches=[p for p,t in makefiles.items() if re.search(r'(?<![\w-])'+re.escape(stem)+r'\.o(?![\w-])',t)];cand=r['candidate_path'];candidate_dir=cand.split('/device_modules/',1)[1] if '/device_modules/' in cand else 'UNKNOWN';specific=[p for p in matches if candidate_dir!='UNKNOWN' and p.startswith(candidate_dir+'/')];matches=specific or matches
 paths=sorted({str(Path(p).parent) for p in matches});publicmap[r['module_id']]=dict(kbuild_matches=matches,candidate_directories=paths,source_tree=ALPS,tree_id=donor('rev-parse',ALPS+'^{tree}').decode().strip())
 for f in matches:hashes.append(dict(module_id=r['module_id'],path=f,source='ALPS',revision=ALPS,sha256=sha(donor('show',ALPS+':'+f))))
 historical=R/r['source_snapshot_path'];historical=historical.resolve();historicfiles=[]
 if historical.exists():
  historicfiles=[historical] if historical.is_file() else [f for f in historical.rglob('*') if f.is_file() and f.suffix in ['.c','.h','.sh','.py','.tsv'] or (f.is_file() and f.name in ['Makefile','Kbuild','Kconfig'])]
 for f in historicfiles:
  hashes.append(dict(module_id=r['module_id'],path=str(f),source='HISTORICAL_MUTABLE_NOT_BUILD_INPUT',revision=r['source_commit'],sha256=sha(f.read_bytes())))
 evidence=R/r['parity_evidence'];actualevidence=evidence.exists();active=';'.join(claims[r['module_id']]) or 'NONE_AT_SNAPSHOT';confidence='PUBLIC_KBUILD_TARGET_AND_HISTORICAL_STOCK_MATCH; FRESH_NOT_PROVED' if matches else 'HISTORICAL_RECONSTRUCTION_ONLY; ORIGINAL_SOURCE_NOT_ESTABLISHED'
 subsystem=r['source_group'].removeprefix('PRESERVE:');firmware=r['firmware_boundary'];dt=r['observed_bindings'] or 'UNKNOWN'
 row=dict(module_id=r['module_id'],filename=r['filename'],initial_class='G',partitions=r['partitions'],stock_paths=r['stock_paths'],stock_sha256=r['stock_sha256'],stock_size=r['stock_size'],existing_research_owner=r['source_owner'],historical_source_path=r['source_snapshot_path'],historical_files_found=len(historicfiles),historical_source_commit_claim=r['source_commit'],public_source_candidate=';'.join(matches) or 'UNKNOWN',public_revision=ALPS if matches else 'UNKNOWN',binary_analysis_evidence=r['parity_evidence']+'; '+r['historical_parity'],subsystem=subsystem,direct_abi_providers=r['provider_dependencies'],kernel_dependencies=r['dependency_evidence'],device_tree_relationship=dt,firmware_HAL_boundary=firmware,unmaintained_source_exists=str(historical.exists()),active_agent_claim=active,source_recovery_complexity='MODERATE_BOOTSTRAP_PROVIDER_CONFIG_CLOSURE' if matches else 'HIGH_ORIGINAL_PROVENANCE_AND_OEM_RECOVERY',lineage_confidence=confidence,complete_authentic_source_recoverability='LIKELY_EXACT_PUBLIC_NEEDS_SOURCE_LIST_AND_FULL_ELF_BUILD_PROOF' if matches else 'UNKNOWN_SEARCH_OTHER_OEM_AND_GIT_HISTORY',build_together=subsystem,missing_certification_evidence=r['blocker'],runtime_status=r['runtime_status'],stock_functions=r['stock_functions'],stock_data_objects=r['stock_data_objects'],stock_imports=r['stock_imports'],stock_exports=r['stock_exports'],stock_kcfi_abs_ids=r['stock_kcfi_abs_ids'],stock_relocations=r['stock_relocations'],eligible=str(active=='NONE_AT_SNAPSHOT'))
 out.append(row)
with (P/'G-REMAINING-INVENTORY.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(out)
with (E/'historical-public-source-hashes.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(hashes[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(hashes)
(E/'ALPS-KBUILD-MATCHES.json').write_text(json.dumps(publicmap,indent=2,sort_keys=True)+'\n')
# Historical commits are source discovery evidence only, not proof of input closure.
logs=git(C,'log','--all','--format=%H %s','--','reverse-engineering/geniezone','reverse-engineering/modem','reverse-engineering/camera/vcm','reverse-engineering/camera/ois','reverse-engineering/camera/eeprom');(E/'historical-research-commits.txt').write_text(logs)
print('canonical',head,'allG',len(G),'public Kbuild matches',sum(bool(r['public_source_candidate']!='UNKNOWN') for r in out),'historical source exists',sum(r['unmaintained_source_exists']=='True' for r in out),'pendingD28excluded',len(pending),'historical+publicfilehashrecords',len(hashes),'Gclaimed',sum(r['active_agent_claim']!='NONE_AT_SNAPSHOT' for r in out))
for r in out:print(r['filename'],r['public_source_candidate'],r['historical_files_found'])
