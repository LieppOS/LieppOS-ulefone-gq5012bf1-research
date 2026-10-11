#!/usr/bin/env python3
"""Private baseline/signed-stock/source-bundle recovery. No canonical writes."""
from pathlib import Path
import os,json,csv,hashlib,subprocess,shutil,collections
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent;C=ROOT/'ulefone-gq5012bf1-research';A=R/'reverse-engineering/kernel-source-parity-audit';E=P/'evidence';W=Path('/home/armol/kernel-work/completed-batches-integration-01');W.mkdir(exist_ok=True)
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
def table(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
head=git(C,'rev-parse','HEAD').strip();assert head=='f61ebf03275ba2d3f6aa4f9d5aebe18e12922263';assert not git(C,'status','--porcelain')
baseline=dict(canonical_branch=git(C,'branch','--show-current').strip(),canonical_head=head,canonical_dirty=git(C,'status','--porcelain'),worktrees=git(C,'worktree','list','--porcelain'),branches=git(C,'for-each-ref','--format=%(refname) %(objectname)','refs/heads'),category_C_branch=git(C,'rev-parse','codex/all-c-to-a-closure').strip(),category_C_dirty=git(ROOT/'ulefone-gq5012bf1-research-codex-all-c-closure','status','--porcelain'),cpu_affinity=sorted(os.sched_getaffinity(0)),nice=10)
rows=table(A/'ALL-457-MODULES.tsv');baseline['classifications']={s:sum(r['source_status']==s for r in rows) for s in 'ABCDEFG'};baseline['canonical_audit_sha256']=SHA(C/'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv');dump(E/'baseline.json',baseline)
shutil.copy2(A/'ALL-457-MODULES.tsv',E/'baseline-ALL-457-MODULES.tsv');shutil.copy2(A/'evidence/source-reviews.json',E/'baseline-source-reviews.json');shutil.copy2(A/'evidence/review-input-hashes.json',E/'baseline-review-input-hashes.json')
# Authenticate every copied occurrence; read the intact prior restoration first.
integrity=ROOT/'ulefone-gq5012bf1-research-codex-inventory';fallback=Path('/home/armol/kernel-work/codex-audio-dependencies-batch-02/stock-identities');records=[];canonical_damage=[]
for r in rows:
 for relative in r['stock_paths'].split(';'):
  src=next((p for p in [integrity/relative,fallback/(r['filename']+'.'+r['stock_sha256']),C/relative] if p.is_file() and p.stat().st_size==int(r['stock_size']) and SHA(p)==r['stock_sha256']),None);assert src,relative
  dest=R/relative;dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():subprocess.run(['cp','--reflink=auto','--preserve=mode,timestamps',str(src),str(dest)],check=True)
  assert SHA(dest)==r['stock_sha256'];dest.chmod(dest.stat().st_mode & ~0o222)
  actual=C/relative
  if SHA(actual)!=r['stock_sha256']:canonical_damage.append(dict(path=relative,expected=r['stock_sha256'],actual=SHA(actual),actual_size=actual.stat().st_size,expected_size=int(r['stock_size'])))
  records.append(dict(module_id=r['module_id'],path=relative,sha256=SHA(dest),size=dest.stat().st_size,source=str(src),partition='system_dlkm' if '/system_dlkm/' in relative else 'vendor_dlkm' if '/vendor_dlkm/' in relative else 'vendor_boot_platform'))
assert len(records)==471;assert collections.Counter(r['partition'] for r in records)==dict(system_dlkm=60,vendor_dlkm=215,vendor_boot_platform=196)
dump(E/'private-stock.json',records);dump(E/'canonical-stock-damage.json',canonical_damage)
# Copy exact load lists only; never symlink stock roots to a damaged shared tree.
for root in ['workspace/gq5012bf1/stock/partitions/system_dlkm','workspace/gq5012bf1/stock/partitions/vendor_dlkm','workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted']:
 for src in (integrity/root/'lib/modules').glob('modules.load*'):
  dst=R/src.relative_to(integrity);shutil.copy2(src,dst);assert SHA(src)==SHA(dst)
# Git-ignored historical baseline proof files are read-only aliases to SHA-frozen originals.
inputs=dict(json.loads((A/'evidence/workspace-baseline.json').read_text())['workspace_inputs'])
for values in json.loads((A/'evidence/review-input-hashes.json').read_text()).values():
 for p,h in values.items():
  if p in inputs:assert inputs[p]==h
  inputs[p]=h
for relative,h in inputs.items():
 dst=R/relative
 if not dst.exists():
  src=C/relative;assert src.is_file() and SHA(src)==h,relative;dst.parent.mkdir(parents=True,exist_ok=True);dst.symlink_to(src)
 assert SHA(dst)==h,relative
specs=[('AUDIO-BATCH-01','f00bd8af7e6bd4fde4355ae67e8392feab596a80'),('SCP-CONNECTIVITY-BATCH-01','40bfedda097cc33d05eba145fa0c51d6ceb0a07e'),('AUDIO-DEPENDENCIES-BATCH-02','fb558640b3227eb57b4172e129c6048b46d07ed6')]
combined=[];repos=[];ids=set();by={r['module_id']:r for r in rows};stock=W/'stock-selected';stock.mkdir(exist_ok=True)
for batch,commit in specs:
 B=R/'reverse-engineering/kernel-source-reconstruction'/batch;man=table(B/'BATCH-MANIFEST.tsv');par=table(B/'BATCH-PARITY.tsv');assert len(man) in [20,21,22]
 for m in man:
  i=m['module_id'];assert i not in ids;irow=by[i];assert m['stock_sha256']==irow['stock_sha256'] and str(m['stock_size'])==irow['stock_size'] and m['stock_paths']==irow['stock_paths'];ids.add(i)
  p=next(p for p in par if p['module']==m['filename'] and p.get('stock_sha256',m['stock_sha256'])==m['stock_sha256']);repo=Path(m['planned_repository']).name
  entry=dict(batch=batch,research_commit=commit,module_id=i,filename=m['filename'],stock_sha256=m['stock_sha256'],stock_size=m['stock_size'],stock_paths=m['stock_paths'],partitions=irow['partitions'],initial_class=m['initial_class'],current_class=irow['source_status'],proposed_class=p['final_class'],source_repository=repo,source_commit=p['source_commit'],original_delta=str((B/'AUDIT-DELTA.tsv').relative_to(R)),acceptance_evidence=p['evidence'],current_source_owner=irow['source_owner'],component_owner=irow['component_owner'],residual=p['residual'])
  combined.append(entry);dest=stock/m['filename'];src=R/irow['stock_paths'].split(';')[0]
  if dest.exists():assert SHA(dest)==m['stock_sha256'],'Never deduplicate bluetooth by filename'
  else:dest.symlink_to(src)
 for rec in table(B/'SOURCE-REPOSITORIES.tsv'):
  src=Path(rec['bundle']);src=src if src.is_absolute() else B/src;assert SHA(src)==rec['bundle_sha256'];bundle=P/'bundles'/src.name;shutil.copy2(src,bundle)
  clone=W/'sources'/rec['repository'];clone.parent.mkdir(exist_ok=True)
  if not clone.exists():subprocess.run(['git','clone','-q','--no-hardlinks',str(bundle),str(clone)],check=True)
  assert git(clone,'rev-parse','HEAD').strip()==rec['commit'];assert not (clone/'.git/objects/info/alternates').exists()
  for args in [('bundle','verify',str(bundle)),('fsck','--full')]:
   p=subprocess.run(['git','-C',str(clone),*args],capture_output=True,text=True);(E/(rec['repository']+'-'+args[0]+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0
  original=ROOT/rec['repository'];assert git(original,'rev-parse','HEAD').strip()==rec['commit'];assert not git(original,'status','--porcelain')
  repos.append(dict(repository=rec['repository'],commit=rec['commit'],original_head=git(original,'rev-parse','HEAD').strip(),original_dirty=git(original,'status','--porcelain'),bundle=str(bundle.relative_to(P)),bundle_sha256=SHA(bundle),private_clone=str(clone),donor_pins_sha256=SHA(clone/'SOURCE-PINS.tsv'),private_clone_fsck='PASS',licence_files=';'.join(str(p.relative_to(clone)) for p in clone.rglob('*') if p.is_file() and p.name in ['LICENSE','COPYING','NOTICE'])))
assert len(ids)==63 and collections.Counter(r['proposed_class'] for r in combined)==dict(A=57,C=6);assert len(repos)==6
for name,data in [('COMBINED-MANIFEST.tsv',combined),('SOURCE-REPOSITORIES.tsv',repos)]:
 with (P/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(data[0]),delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(data)
dump(E/'preparation-result.json',dict(result='PASS',identities=458,occurrences=471,selected_distinct=63,proposed_A=57,retained_C=6,private_stock_read_only=True,canonical_damaged_occurrences=len(canonical_damage),source_bundles=6,cpu_affinity=sorted(os.sched_getaffinity(0))))
print('PASS preparation:63 distinct targets,57A/6C,6 pinned bundle recovery clones,471 private stock copies;',len(canonical_damage),'damaged canonical copies left untouched')
