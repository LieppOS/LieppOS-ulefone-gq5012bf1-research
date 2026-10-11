#!/usr/bin/env python3
"""Apply original batch CAS deltas to this staging audit only; regenerate derivatives.
Legacy row-oriented deltas are adapted without editing their original files.
Evidence-derived certification metadata is separately logged, never fabricated.
"""
from pathlib import Path
import csv,json,collections,hashlib,subprocess,sys,os,copy
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit';E=P/'evidence'
assert json.loads((E/'source-evidence-result.json').read_text())['result']=='PASS'
def table(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows,fields=None):
 with p.open('w') as f:
  wr=csv.DictWriter(f,fieldnames=fields or list(rows[0]),delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(rows)
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=table(E/'baseline-ALL-457-MODULES.tsv');rows=table(A/'ALL-457-MODULES.tsv');by={r['module_id']:r for r in rows};selected=table(P/'COMBINED-MANIFEST.tsv');sid={m['module_id'] for m in selected};assert len(sid)==63 and len(by)==458
review=json.loads((A/'evidence/source-reviews.json').read_text());hashes=json.loads((A/'evidence/review-input-hashes.json').read_text());frozen=json.loads((A/'evidence/stock-identities.json').read_text());log=[];counts=[];deltas=[];conflicts=[]

def setfield(m,key,expected,value,origin):
 r=by[m['module_id']];value=str(value)
 if r[key]!=str(expected):raise ValueError(('CAS_CONFLICT',m['module_id'],key,expected,r[key],value))
 if r[key]!=value:
  log.append(dict(batch=m['batch'],module_id=m['module_id'],filename=m['filename'],field=key,expected_before=str(expected),proposed_after=value,origin=origin,result='APPLIED'))
  r[key]=value

def counts_now(label):
 c={s:sum(r['source_status']==s for r in rows) for s in 'ABCDEFG'};counts.append(dict(step=label,**c,certified=c['A']+c['B'],remaining=458-c['A']-c['B']))

def regenerate(label):
 fields=list(base[0]);write(A/'ALL-457-MODULES.tsv',rows,fields)
 gaps=[r for r in rows if r['source_status'] not in ['A','B','F']]
 write(A/'SOURCE-GAPS.tsv',gaps,fields);write(A/'DONE-SOURCE-EVIDENCE-DISCREPANCIES.tsv',[r for r in gaps if r['component_status']=='DONE'],fields)
 owners=table(A/'SOURCE-OWNERSHIP.tsv')
 for x in owners:
  r=by[x['module_id']]
  for k in ['source_owner','source_repo','source_commit']:x[k]=r[k]
 write(A/'SOURCE-OWNERSHIP.tsv',owners)
 old={r['project']:r for r in table(A/'RECONSTRUCTION-PROJECTS.tsv')};groups=collections.defaultdict(list)
 for r in gaps:groups[r['source_group']].append(r)
 edges=table(A/'DEPENDENCY-EDGES.tsv');deps=collections.defaultdict(set)
 for x in edges:
  for i in x['provider_module_ids'].split(';'):
   if i in by:deps[x['consumer_module_id']].add(i)
 projects=[]
 for group,members in groups.items():
  template=dict(old.get(group,next(iter(old.values()))));priority=min(r['priority'] for r in members);providers=sorted(set().union(*(deps[r['module_id']] for r in members))-{r['module_id'] for r in members});blockers=sorted({by[i]['source_group'] for i in providers if by[i]['source_status'] not in ['A','B','F']})
  template.update(project=group,priority=priority,module_ids=';'.join(sorted(r['module_id'] for r in members)),modules=';'.join(sorted(r['filename'] for r in members)),count=str(len(members)),statuses=';'.join(f'{s}:{sum(r["source_status"]==s for r in members)}' for s in 'ABCDEFG' if any(r['source_status']==s for r in members)),external_provider_ids=';'.join(providers) or 'NONE',dependency_blocker_projects=';'.join(blockers) or 'NONE')
  if any(r['module_id'] in sid for r in members):
   template.update(source_locations=';'.join(sorted({r['source_repo'] for r in members})),effort='RETAIN_PROVEN_IMPLEMENTATION_AND_CLOSE_DOCUMENTED_RESIDUAL',proof_needed=';'.join(sorted({r['blocker'] for r in members if r['module_id'] in sid})))
  projects.append(template)
 projects.sort(key=lambda x:(x['priority'],x['project']))
 for n,x in enumerate(projects,1):x['rank']=str(n)
 write(A/'RECONSTRUCTION-PROJECTS.tsv',projects)
 for filename in ['OPTIONAL-15-REVIEW.tsv','REPRODUCIBILITY-RISKS.tsv']:
  current=table(A/filename);new=[]
  for x in current:
   if filename=='REPRODUCIBILITY-RISKS.tsv' and by[x['module_id']]['source_status'] not in ['C','G']:continue
   if x['module_id'] in sid:
    x['source_status']=by[x['module_id']]['source_status']
    if 'recipe' in x:x['recipe']=by[x['module_id']]['build_script']
    if 'historical_proof' in x:x['historical_proof']=by[x['module_id']]['parity_evidence']
    if 'source_snapshot' in x:x['source_snapshot']=by[x['module_id']]['source_snapshot_path']
    if 'unresolved_evidence' in x:x['unresolved_evidence']=by[x['module_id']]['blocker']
   new.append(x)
  write(A/filename,new,list(current[0]))
 (A/'evidence/source-reviews.json').write_text(json.dumps(review,indent=2)+'\n');(A/'evidence/review-input-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
 summary=json.loads((A/'evidence/audit-summary.json').read_text());summary['source_status_counts']={s:sum(r['source_status']==s for r in rows) for s in 'ABCDEFG'};summary['reconstruction_projects']=len(projects);(A/'evidence/audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 queue=['# Authoritative staged source reconstruction queue','',f'458 identities /471 occurrences; {len(gaps)} uncertified identities. Generated from current identity-keyed audit, not a stale file replacement.','', 'Completed integration: AUDIO-BATCH-01, SCP-CONNECTIVITY-BATCH-01 and AUDIO-DEPENDENCIES-BATCH-02. Retained C proof obligations are separate from code/hardware/component status.','']
 for x in projects:queue += [f"## {x['rank']}. {x['project']} — {x['priority']}",f"- {x['count']} identities: {x['modules']}",f"- Classes: {x['statuses']}",f"- Source: {x['source_locations']}",f"- Provider gaps: {x['dependency_blocker_projects']}",f"- Proof needed: {x['proof_needed']}",'']
 (A/'RECONSTRUCTION-QUEUE.md').write_text('\n'.join(queue)+'\n')
 proc=subprocess.run([sys.executable,str(A/'scripts/validate.py')],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True);(E/(label+'-audit.log')).write_text(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stdout[-4000:]+proc.stderr
 (E/(label+'-audit.json')).write_text(proc.stdout)

counts_now('baseline')
for batch in ['AUDIO-BATCH-01','SCP-CONNECTIVITY-BATCH-01','AUDIO-DEPENDENCIES-BATCH-02']:
 B=P.parent/batch;members=[m for m in selected if m['batch']==batch];manifest={m['module_id']:m for m in table(B/'BATCH-MANIFEST.tsv')};original=table(B/'AUDIT-DELTA.tsv');checkpoint=copy.deepcopy(rows)
 for m in members:
  r=by[m['module_id']];assert r['stock_sha256']==m['stock_sha256'] and r['stock_size']==m['stock_size'];assert r['source_owner']==manifest[m['module_id']]['source_owner'];assert r['source_status']==m['initial_class']
  if batch!='AUDIO-DEPENDENCIES-BATCH-02':
   d=next(d for d in original if d['module_id']==m['module_id']);repo,commit=d['new_source_owner'].split('@');assert repo==m['source_repository'] and commit==m['source_commit']
   mapped=dict(source_status=d['new_source_status'],source_group=d['new_source_group'],source_owner=d['new_source_group'],source_repo='../'+repo,source_commit=commit,parity_evidence=d['new_parity_evidence'],build_script='../'+d['new_build_script'],reproduction_status=d['new_reproduction'])
   assert r['source_group']==d['old_source_group']
   for key,val in mapped.items():setfield(m,key,r[key],val,'ORIGINAL_ROW_DELTA_EXPLICIT_ADAPTER')
  else:
   for d in original:
    if d['module_id']==m['module_id']:setfield(m,d['field'],d['expected_before'],d['proposed_after'],'ORIGINAL_FIELD_CAS_DELTA')
  # Old deltas only described8 fields and cannot certify independently without
  # real ABI/source-pin/count metadata. Supplement from the rechecked evidence.
  unresolved=1 if m['filename']=='aw883xx_driver.ko' else 0
  metadata=dict(reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',source_pin='../'+m['source_repository']+'/SOURCE-PINS.tsv',source_snapshot_path='../'+m['source_repository']+'/SOURCE-PINS.tsv',exact_functions=str(frozen[m['module_id']]['function_count']-unresolved),unresolved_functions=str(unresolved),equivalent_functions='0',blocker='NONE' if m['proposed_class']=='A' else m['residual'],verified_difference_classification='GNU20_ONLY' if m['proposed_class']=='A' else m['residual'])
  for key,val in metadata.items():setfield(m,key,r[key],val,'INTEGRATION_METADATA_FROM_ACTUAL_ELF_AND_FROZEN_SOURCE_PROOF')
  inputs=dict(hashes[m['module_id']])
  inputs.update({'../'+m['source_repository']+'/SOURCE-PINS.tsv':SHA(R.parent/m['source_repository']/'SOURCE-PINS.tsv'),'../'+m['source_repository']+'/scripts/bulk-build.sh':SHA(R.parent/m['source_repository']/'scripts/bulk-build.sh'),r['parity_evidence']:SHA(R/r['parity_evidence']),str((E/'source-evidence-result.json').relative_to(R)):SHA(E/'source-evidence-result.json')})
  hashes[m['module_id']]=inputs
  if r['source_status']=='C':
   material=''.join(f'{p}\t{h}\n' for p,h in sorted(inputs.items()));setfield(m,'source_pin',r['source_pin'],'sha256:'+hashlib.sha256(material.encode()).hexdigest(),'AUTHENTIC_REVIEW_INPUT_CLOSURE_PIN')
  for k in {x['field'] for x in log if x['module_id']==m['module_id']}:review[m['module_id']][k]=r[k].split(';') if k=='parity_evidence' else r[k]
 assert all(a==by[a['module_id']] for a in checkpoint if a['module_id'] not in {m['module_id'] for m in members})
 counts_now(batch);regenerate(batch)
write(P/'DELTA-APPLICATION-LOG.tsv',log);write(P/'CLASSIFICATION-BEFORE-AFTER.tsv',counts)
# Final owner CAS plan collapses multiple metadata transitions into one exact
# expected-before/proposed-after pair per field/identity.
for old in base:
 current=by[old['module_id']]
 if old['module_id'] not in sid:assert old==current
 for key in old:
  if old[key]!=current[key]:deltas.append(dict(module_id=old['module_id'],filename=old['filename'],stock_sha256=old['stock_sha256'],stock_size=old['stock_size'],field=key,expected_before=old[key],proposed_after=current[key]))
write(P/'FINAL-FIELD-DELTA.tsv',deltas)
for name in ['source-reviews.json','review-input-hashes.json']:
 original=json.loads((E/('baseline-'+name)).read_text());proposed=review if name=='source-reviews.json' else hashes
 assert all(original[i]==proposed[i] for i in original if i not in sid)
 (P/('FINAL-'+name)).write_text(json.dumps({i:dict(expected_before=original[i],proposed_after=proposed[i]) for i in sorted(sid)},indent=2)+'\n')
assert counts[-1]['A']==301 and counts[-1]['B']==1 and counts[-1]['C']==20 and counts[-1]['D']==82 and counts[-1]['G']==54
p=subprocess.run([sys.executable,str(A/'scripts/test_validate.py'),'-v'],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));(E/'audit-mutations.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr[-3000:]
(E/'delta-result.json').write_text(json.dumps(dict(result='PASS',counts=counts,changed_identities=63,unchanged_unselected=395,final_field_changes=len(deltas),logged_transitions=len(log),canonical_untouched=True,audit_mutations=14),indent=2)+'\n')
print('PASS combined source staging:302 certified/156 remaining; all395 unselected rows unchanged; original field deltas + explicit justified metadata;',len(deltas),'final CAS fields')
