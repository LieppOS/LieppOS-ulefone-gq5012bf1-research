#!/usr/bin/env python3
"""Narrow field CAS against exact validated55dab overlay; requires REAL proof PASS."""
from pathlib import Path
import ast,csv,json,collections,hashlib,copy,subprocess,os,sys
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10);os.environ['PYTHONDONTWRITEBYTECODE']='1'
P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit';E=P/'evidence';proof=P/'evidence/independent-proof/RESULT.json'
assert json.loads(proof.read_text())['result']=='PASS','Real independent B1/B2/mutations/bundle result required before any A proposal'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def table(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rs,fields=None):
 with p.open('w') as f:w=csv.DictWriter(f,fieldnames=fields or list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
selected=table(P/'BATCH-MANIFEST.tsv');sid={m['module_id'] for m in selected};assert len(sid)==22
protected={r['module_id'] for r in table(P.parent/'COMPLETED-BATCHES-INTEGRATION-01/COMBINED-MANIFEST.tsv')};assert sid.isdisjoint(protected)
# Save the exact actual current audit before writes; no forced status-only reset.
base=table(A/'ALL-457-MODULES.tsv');assert dict(collections.Counter(r['source_status'] for r in base))==dict(A=301,B=1,C=20,D=82,G=54)
write(E/'baseline-ALL-457-MODULES.tsv',base)
rows=copy.deepcopy(base);by={r['module_id']:r for r in rows};assert len(by)==458
review=json.loads((A/'evidence/source-reviews.json').read_text());hashes=json.loads((A/'evidence/review-input-hashes.json').read_text());old_review=copy.deepcopy(review);old_hashes=copy.deepcopy(hashes)
for n,j in [('source-reviews.json',review),('review-input-hashes.json',hashes)]:
 (E/('baseline-'+n)).write_text(json.dumps(j,indent=2)+'\n')
result=json.loads(proof.read_text());log=[];parity=[]
for m in selected:
 row=by[m['module_id']];assert row['source_status']==m['initial_class']=='D';assert row['source_owner']==m['source_owner'];assert row['stock_sha256']==m['stock_sha256'] and row['stock_size']==m['stock_size']
 family='diagnostics' if m['source_family']=='MTK-SYSTEM-DIAGNOSTICS' else 'met';rep=m['maintained_repository'];commit=result['families'][family]['commit'];assert subprocess.check_output(['git','-C',str(R.parent/rep),'rev-parse','HEAD'],text=True).strip()==commit
 ev=E/'independent-proof'/family/'B1/acceptance/acceptance.json';e=json.loads(ev.read_text())[m['filename'].removesuffix('.ko')];assert e['unresolved']==0 and e['stock_sha256']==m['stock_sha256'];v2=json.loads((E/'independent-proof'/family/'B2/acceptance/acceptance.json').read_text())[m['filename'].removesuffix('.ko')];assert e==v2
 group='NEXT-DG-BATCH-01:'+m['source_family'];vals=dict(source_status='A',source_group=group,source_owner=group,source_repo='../'+rep,source_commit=commit,source_pin='../'+rep+'/SOURCE-PINS.tsv',source_snapshot_path='../'+rep+'/SOURCE-PINS.tsv',build_script='../'+rep+'/scripts/bulk-build.sh',parity_evidence=str(ev.relative_to(R)),reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',exact_functions=str(e['functions']),equivalent_functions='0',unresolved_functions='0',verified_difference_classification='GNU20_ONLY',blocker='NONE',gap_kind='NONE_SOURCE_CERTIFIED')
 for k,v in vals.items():
  if row[k]!=v:log.append(dict(module_id=m['module_id'],filename=m['filename'],stock_sha256=m['stock_sha256'],stock_size=m['stock_size'],field=k,expected_before=row[k],proposed_after=v,origin='REAL_WHOLE_STOCK_B1_B2_SOURCE_CONFIG_ALL_OBJECTS_NATURAL_ABI_MUTATIONS_BUNDLE_PROOF'));row[k]=v
 for k,v in vals.items():review[m['module_id']][k]=v.split(';') if k=='parity_evidence' else v
 inputs=dict(hashes[m['module_id']]);refs=[R.parent/rep/'SOURCE-PINS.tsv',R.parent/rep/'scripts/bulk-build.sh',R.parent/rep/'scripts/make-kout.sh',R.parent/rep/'scripts/kb.sh',R.parent/rep/'reference/BATCH-MANIFEST.tsv',ev,proof,E/'independent-proof'/(rep+'.bundle')]
 for f in refs:
  ref='../'+str(f.relative_to(R.parent)) if f.is_relative_to(R.parent/rep) else str(f.relative_to(R));inputs[ref]=SHA(f)
 hashes[m['module_id']]=inputs
 parity.append(dict(module=m['filename'],initial_class='D',final_class='A',functions=str(e['functions'])+'/'+str(e['functions']),data=str(e['data'])+'/'+str(e['data']),crc_kcfi=f"{e['imports']}imports/{e['exports']}exports/{e['kcfi_abs_ids']}KCFI_EXACT",relocations=str(e['relocations'])+'_RAW_AND_SEMANTIC_EXACT',source_repo=rep,source_commit=commit,residual='NONE_GNU20_ONLY',module_id=m['module_id'],evidence=str(ev.relative_to(R))))
for old in base:
 current=by[old['module_id']]
 if old['module_id'] not in sid:assert current==old
 for k in old:
  if not k.startswith('source_') and k in ['component_owner','component_status','canonical_component_status','runtime_status','runtime_evidence','stock_sha256','stock_size','stock_paths','partitions','load_phase','load_order']:assert current[k]==old[k]
assert all(old_review[i]==review[i] and old_hashes[i]==hashes[i] for i in old_review if i not in sid)
# Reuse the already independently validated derivative function, NOT its63-row application.
module=ast.parse((P.parent/'COMPLETED-BATCHES-INTEGRATION-01/scripts/apply-staging.py').read_text());fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='regenerate');ns=globals();exec(compile(ast.Module(body=[fn],type_ignores=[]),'<validated-derivative-regenerator>','exec'),ns);regenerate('next-dg-proposed')
write(P/'AUDIT-DELTA.tsv',log);write(P/'BATCH-PARITY.tsv',parity)
for name,old,new in [('source-reviews.json',old_review,review),('review-input-hashes.json',old_hashes,hashes)]:
 (P/('PROPOSED-'+name)).write_text(json.dumps({i:dict(expected_before=old[i],proposed_after=new[i]) for i in sorted(sid)},indent=2)+'\n')
p=subprocess.run([sys.executable,str(A/'scripts/test_validate.py'),'-v'],capture_output=True,text=True);(E/'audit-mutations.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr[-3000:]
counts={s:sum(r['source_status']==s for r in rows) for s in 'ABCDEFG'};assert counts==dict(A=323,B=1,C=20,D=60,E=0,F=0,G=54)
(E/'audit-delta-result.json').write_text(json.dumps(dict(result='PASS',baseline_counts=dict(A=301,B=1,C=20,D=82,E=0,F=0,G=54),projected_counts=counts,certified=324,remaining=134,selected=22,unchanged_unselected=436,protected_completed63='UNCHANGED',field_changes=len(log),audit_mutation_tests=14),indent=2)+'\n')
print('PASS isolated proposal:324certified/134remaining;22 D→A;436 unselected unchanged;'+str(len(log))+'source field CAS changes')
