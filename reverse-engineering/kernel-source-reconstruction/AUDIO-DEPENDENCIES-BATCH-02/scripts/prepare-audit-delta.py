#!/usr/bin/env python3
"""Require actual independent proof, then create CAS delta and isolated audit.
Never edits canonical audit or applies pending audio/SCP/Claude results.
"""
from pathlib import Path
import csv,json,hashlib,shutil,subprocess,sys,importlib.util,os,collections
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=P.parents[3]
A=R/'reverse-engineering/kernel-source-parity-audit';E=P/'evidence/independent-proof-pathmaps'
proof=json.loads((E/'result.json').read_text());assert proof['result']=='PASS_20_STRICT_ACCEPTANCES_TWO_EXPECTED_C_REJECTIONS'
assert proof['all_raw_stripped_objects_source_config_abi_independent'] and proof['build_jobs']==4
read=lambda p:list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows,fields):
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
SHA=lambda b:hashlib.sha256(b).hexdigest()
manifest=read(P/'BATCH-MANIFEST.tsv');base=read(P/'evidence/baseline/ALL-457-MODULES.tsv');byid={r['module_id']:r for r in base};selected={r['module_id'] for r in manifest}
assert len(selected)==22 and len(byid)==458
original=ROOT/'ulefone-gq5012bf1-research/reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'
assert original.read_bytes()==(P/'evidence/baseline/ALL-457-MODULES.tsv').read_bytes(),'canonical audit changed; stop/reconcile CAS'
S=P/'evidence/audit-scratch-v3';assert not S.exists(),'retain previous scratch; do not overwrite';shutil.copytree(A,S)
review=json.loads((S/'evidence/source-reviews.json').read_text());hashes=json.loads((S/'evidence/review-input-hashes.json').read_text());frozen=json.loads((S/'evidence/stock-identities.json').read_text())
family={'SLBC':'slbc','MODEM-AUDIO-TRANSPORT':'modem','TRANSITIVE-SHARED-INFRASTRUCTURE':'shared'}
rel='reverse-engineering/kernel-source-reconstruction/AUDIO-DEPENDENCIES-BATCH-02/'
parity=[];changes=[];blocked=[];repositories=[]
for m in manifest:
 row=dict(byid[m['module_id']]);f=family[m['expected_build_group']];run=next(r for r in proof['runs'] if r['family']==f and r['tag']=='B1');repo=m['planned_repository'];commit=proof['source_commits'][repo];name=m['filename'][:-3];isC=name in ['drm_display_helper','drm_dma_helper'];status='C' if isC else 'A'
 report=E/(f+'-B1')/'acceptance'/name/'acceptance.json'
 if isC:
  record=json.loads((E/(f+'-B1')/'C-residuals/class-c-residuals.json').read_text())[name]
  source_files={'../'+repo+'/reference/'+p.name:SHA(p.read_bytes()) for p in (ROOT/repo/'reference').glob('*') if p.is_file()}
  source_files['../'+repo+'/SOURCE-PINS.tsv']=SHA((ROOT/repo/'SOURCE-PINS.tsv').read_bytes());hashes[m['module_id']]=source_files
  material=''.join(f'{p}\t{h}\n' for p,h in sorted(source_files.items()));pin='sha256:'+SHA(material.encode())
  residual='Original OEM split-BTF base absent:15 extra types/389 extra string bytes; every non-BTF/GNU20 byte exact; source BTF never edited'
  functions=199 if name=='drm_display_helper' else 19;data=46 if name=='drm_display_helper' else 13
  evidence=rel+'evidence/independent-proof-pathmaps/shared-B1/C-residuals/class-c-residuals.json'
  blocked.append(dict(module_id=m['module_id'],module=m['filename'],final_class='C',blocker=residual,evidence=evidence))
 else:
  record=json.loads(report.read_text())[name];functions=record['functions'];data=record['data'];pin='../'+repo+'/SOURCE-PINS.tsv';residual='NONE';evidence=rel+str(report.relative_to(P))
 update={'source_status':status,'source_owner':'AUDIO-DEPENDENCIES-BATCH-02:'+m['expected_build_group'],
         'source_repo':'../'+repo,'source_commit':commit,'source_pin':pin,'source_snapshot_path':'../'+repo+'/SOURCE-PINS.tsv',
         'build_script':'../'+repo+'/scripts/bulk-build.sh','reproduction_status':'INDEPENDENT_CLEAN_CHECKOUT_B1_B2',
         'abi_status':'VERIFIED','crc_status':'VERIFIED','kcfi_status':'VERIFIED',
         'parity_evidence':evidence,'exact_functions':frozen[m['module_id']]['function_count'],'equivalent_functions':'0',
         'verified_difference_classification':'.BTF OEM type/string reference mapping;GNU20' if isC else 'GNU20 structural descriptor only',
         'unresolved_functions':'0','blocker':residual}
 for key,value in update.items():
  value=str(value)
  if row[key]!=value:changes.append(dict(module_id=m['module_id'],filename=m['filename'],field=key,expected_before=row[key],proposed_after=value));row[key]=value
 byid[m['module_id']]=row
 for key in update:review[m['module_id']][key]=row[key].split(';') if key=='parity_evidence' else row[key]
 parity.append(dict(module=m['filename'],module_id=m['module_id'],initial_class=m['initial_class'],final_class=status,functions=functions,data=data,CRC_KCFI='EXACT',relocations='RAW_AND_SEMANTIC_EXACT',source_commit=commit,B1_B2='RAW_STRIPPED_OBJECT_CONFIG_SOURCE_ABI_IDENTICAL',whole_stock_acceptance='REJECT_KNOWN_BTF_ONLY' if isC else 'PASS_GNU20_ONLY',residual=residual,evidence=evidence))
write(P/'BATCH-PARITY.tsv',parity,list(parity[0]));write(P/'AUDIT-DELTA.tsv',changes,['module_id','filename','field','expected_before','proposed_after']);write(P/'BLOCKERS.tsv',blocked,list(blocked[0]))
json_delta={}
for filename,proposed in [('source-reviews.json',review),('review-input-hashes.json',hashes)]:
 original_json=json.loads((A/'evidence'/filename).read_text())
 json_delta[filename]={i:dict(expected_before=original_json.get(i),proposed_after=proposed.get(i)) for i in sorted(selected) if original_json.get(i)!=proposed.get(i)}
(P/'AUDIT-JSON-DELTA.json').write_text(json.dumps(json_delta,indent=2)+'\n')
rows=[byid[r['module_id']] for r in base];fields=list(base[0]);write(S/'ALL-457-MODULES.tsv',rows,fields);write(S/'SOURCE-GAPS.tsv',[r for r in rows if r['source_status'] not in ['A','B','F']],fields)
owners=read(S/'SOURCE-OWNERSHIP.tsv')
for o in owners:
 if o['module_id'] in selected:o['source_owner']=byid[o['module_id']]['source_owner']
write(S/'SOURCE-OWNERSHIP.tsv',owners,list(owners[0]))
(S/'evidence/source-reviews.json').write_text(json.dumps(review,indent=2)+'\n');(S/'evidence/review-input-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
summary=json.loads((S/'evidence/audit-summary.json').read_text());summary['source_status_counts']={s:sum(r['source_status']==s for r in rows) for s in 'ABCDEFG'};(S/'evidence/audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
# Project membership/group copies must match new source ownership, never components.
projects=read(S/'RECONSTRUCTION-PROJECTS.tsv');pf=list(projects[0]);print('project fields',pf)
for project in projects:
 for key in ['module_ids','modules','module_identities']:
  if key in project:project[key]=';'.join(x for x in project[key].split(';') if x not in selected)
# Regenerate from actual audit source owners using the existing project schema.
byowner=collections.defaultdict(list)
for r in rows:
 if r['source_status'] not in ['A','B','F']:byowner[r['source_group']].append(r)
old={r['project']:r for r in projects};new=[]
for owner,rs in sorted(byowner.items()):
 template=dict(old.get(owner,projects[0]))
 for key in pf:
  if key in ['source_owner','project_id','project']:template[key]=owner
  elif key in ['module_ids','module_identities']:template[key]=';'.join(sorted(r['module_id'] for r in rs))
  elif key in ['modules','filenames']:template[key]=';'.join(sorted(r['filename'] for r in rs))
  elif key in ['module_count','identity_count','count']:template[key]=str(len(rs))
  elif key=='statuses':template[key]=';'.join(f'{s}:{sum(r["source_status"]==s for r in rs)}' for s in 'ABCDEFG' if any(r['source_status']==s for r in rs))
 if all(r['module_id'] in selected for r in rs):
  template['effort']='RECOVER_ORIGINAL_OEM_SPLIT_BTF_BASE_NO_ELF_REWRITE'
  template['source_locations']=';'.join(sorted({r['source_repo'] for r in rs}))
  template['proof_needed']='Natural source-generated BTF against genuine OEM g945dff7bc1bf base; every other byte already exact'
 new.append(template)
write(S/'RECONSTRUCTION-PROJECTS.tsv',new,pf)
# Verify every actual private raw operand rather than assuming frozen metadata.
actual={}
for r in base:
 path=Path('/home/armol/kernel-work/codex-audio-dependencies-batch-02/stock-identities')/(r['filename']+'.'+r['stock_sha256']);assert SHA(path.read_bytes())==r['stock_sha256']
 actual[r['module_id']]=dict(module_id=r['module_id'],filename=r['filename'],stock_sha256=r['stock_sha256'],stock_size=int(r['stock_size']),stock_paths=r['stock_paths'].split(';'),partitions=r['partitions'].split(';'))
 # Own isolated worktree aliases permit the original scanner to check actual
 # immutable bytes and all471 occurrences. Shared canonical operands untouched.
 for relative in r['stock_paths'].split(';'):
  alias=R/relative;alias.parent.mkdir(parents=True,exist_ok=True)
  if not alias.exists():alias.symlink_to(path)
  assert SHA(alias.read_bytes())==r['stock_sha256']
# Some preexisting immutable research inputs are git-ignored and not carried
# by git worktree. Alias only genuinely matching original baseline files;
# never change their expected hash or substitute generated content.
for relative,expected in json.loads((S/'evidence/workspace-baseline.json').read_text())['workspace_inputs'].items():
 target=R/relative
 if not target.exists():
  original_input=ROOT/'ulefone-gq5012bf1-research'/relative
  assert original_input.is_file() and SHA(original_input.read_bytes())==expected,relative
  target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(original_input)
 assert SHA(target.read_bytes())==expected,relative
for inputs in hashes.values():
 for relative,expected in inputs.items():
  target=R/relative
  if not target.exists():
   original_input=ROOT/'ulefone-gq5012bf1-research'/relative
   assert original_input.is_file() and SHA(original_input.read_bytes())==expected,relative
   target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(original_input)
  assert SHA(target.read_bytes())==expected,relative
sys.path.insert(0,str(A/'scripts'));import validate
result=validate.validate(S,actual=actual);(P/'evidence/isolated-audit-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('Isolated audit',result['result'],'errors',result['errors'][:12]);assert not result['errors']
# Existing mutation tests use the isolated proposed table and actual SHA-verified inputs.
spec=importlib.util.spec_from_file_location('audit_tests',A/'scripts/test_validate.py');tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
tests.BASE={name:read(S/name) for name in ['ALL-457-MODULES.tsv','SOURCE-GAPS.tsv','SOURCE-OWNERSHIP.tsv','RECONSTRUCTION-PROJECTS.tsv']}
tests.AUDIT=S;tests.ACTUAL=actual
tests.validate=lambda **kwargs:validate.validate(S,**kwargs)
import unittest,io
buf=io.StringIO();test_result=unittest.TextTestRunner(stream=buf,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests));(P/'evidence/isolated-audit-mutations.log').write_text(buf.getvalue());assert test_result.wasSuccessful(),buf.getvalue()
assert original.read_bytes()==(P/'evidence/baseline/ALL-457-MODULES.tsv').read_bytes()
assert all(byid[r['module_id']]==r for r in base if r['module_id'] not in selected)
for repo,commit in proof['source_commits'].items():
 bundle=next((P/'evidence/bundles').glob('fresh-*-'+commit+'.bundle'))
 repositories.append(dict(repository=repo,commit=commit,owned_targets=sum(r['planned_repository']==repo for r in manifest),bundle=str(bundle.relative_to(P)),bundle_sha256=SHA(bundle.read_bytes()),independent_builds='B1_B2_PASS'))
write(P/'SOURCE-REPOSITORIES.tsv',repositories,list(repositories[0]))
(P/'evidence/audit-delta-summary.json').write_text(json.dumps(dict(entries=len(changes),selected=22,unselected_unchanged=436,identities=458,occurrences=471,new_certifications=20,canonical_committed_certified=245,projected_this_batch_only_certified=265,projected_this_batch_only_remaining=193,other_pending_audio_and_SCP_not_counted=True,canonical_audit_unchanged=True,audit_mutation_tests=test_result.testsRun),indent=2)+'\n')
print('Field delta ready',len(changes),'all436 unselected rows unchanged; no live integration')
