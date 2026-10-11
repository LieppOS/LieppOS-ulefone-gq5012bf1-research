#!/usr/bin/env python3
"""22-identity CAS dry-run by default; preserve newer A/B and stop before conflicts."""
from pathlib import Path
import argparse,csv,json,subprocess,os,hashlib,collections,sys,ast
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('target',type=Path);ap.add_argument('--expected-head',required=True);ap.add_argument('--apply',action='store_true');ap.add_argument('--report',type=Path,required=True);args=ap.parse_args();R=args.target.resolve();A=R/'reverse-engineering/kernel-source-parity-audit'
assert R.name not in ['ulefone-gq5012bf1-research','ulefone-gq5012bf1-research-codex-integration','ulefone-gq5012bf1-research-codex-all-c-closure'],'Refuse canonical/completed staging/Claude checkout; owner private worktree only'
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip();assert head==args.expected_head,'HEAD advanced'
p=subprocess.run([sys.executable,str(A/'scripts/validate.py')],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));assert p.returncode==0,p.stdout[-1800:]+p.stderr

def table(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows,fields=None):
 with p.open('w') as f:w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
base=table(A/'ALL-457-MODULES.tsv');rows=[dict(r) for r in base];by={r['module_id']:r for r in rows};plan=table(P/'AUDIT-DELTA.tsv');ids={d['module_id'] for d in plan};assert len(ids)==22
protected={r['module_id'] for r in table(P.parent/'COMPLETED-BATCHES-INTEGRATION-01/COMBINED-MANIFEST.tsv')};assert ids.isdisjoint(protected)
conflicts=[];applied=[];skipped=set()
for i in ids:
 ds=[d for d in plan if d['module_id']==i];r=by.get(i)
 if r is None or any(r[k]!=ds[0][k] for k in ['filename','stock_sha256','stock_size']):conflicts.append(dict(module_id=i,reason='IDENTITY_HASH_SIZE_CONFLICT'));continue
 if r['source_status'] in ['A','B'] and any(r[d['field']]!=d['proposed_after'] for d in ds):skipped.add(i);continue
 for d in ds:
  k=d['field']
  if r[k]==d['proposed_after']:continue
  if r[k]!=d['expected_before']:conflicts.append(dict(module_id=i,field=k,expected=d['expected_before'],current=r[k],proposed=d['proposed_after']));continue
  r[k]=d['proposed_after'];applied.append(d)
review=json.loads((A/'evidence/source-reviews.json').read_text());hashes=json.loads((A/'evidence/review-input-hashes.json').read_text())
for name,current in [('source-reviews.json',review),('review-input-hashes.json',hashes)]:
 for i,record in json.loads((P/('PROPOSED-'+name)).read_text()).items():
  if i in skipped:continue
  old,new=record['expected_before'],record['proposed_after'];cur=current[i]
  for k in set(old)|set(new):
   if old.get(k)==new.get(k) or cur.get(k)==new.get(k):continue
   if cur.get(k)!=old.get(k):conflicts.append(dict(module_id=i,json=name,key=k,reason='NEWER_JSON_REVIEW_CONFLICT'));continue
   if k in new:cur[k]=new[k]
   else:cur.pop(k,None)
report=dict(target=str(R),head=head,apply=args.apply,selected=22,field_changes=len(applied),protected_newer_certified=sorted(skipped),conflicts=conflicts,counts={s:sum(r['source_status']==s for r in rows) for s in 'ABCDEFG'},no_stock_writes=True,prior_completed63_not_selected=True)
args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n')
if conflicts:raise SystemExit('STOP: owner review; no target audit writes')
assert len(by)==458 and all(by[r['module_id']]==r for r in base if r['module_id'] not in ids)
if args.apply:
 code=ast.parse((P.parent/'COMPLETED-BATCHES-INTEGRATION-01/scripts/apply-staging.py').read_text());fn=next(n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='regenerate');E=args.report.parent;sid=ids;SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ns=dict(globals());exec(compile(ast.Module(body=[fn],type_ignores=[]),'<reviewed-regenerator>','exec'),ns);ns['regenerate']('owner-next-dg-reconciled')
 p=subprocess.run([sys.executable,str(A/'scripts/test_validate.py'),'-v'],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));(E/'owner-next-dg-mutations.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()==head,'Concurrent owner commit'
print(json.dumps(dict(result='APPLIED_AND_VALIDATED' if args.apply else 'DRY_RUN_READY',field_changes=len(applied),newer_AB_preserved=len(skipped),counts=report['counts']),indent=2))
