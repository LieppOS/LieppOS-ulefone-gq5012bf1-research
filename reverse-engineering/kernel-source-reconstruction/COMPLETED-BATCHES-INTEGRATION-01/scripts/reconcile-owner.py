#!/usr/bin/env python3
"""Dry-run/apply narrow CAS to an OWNER-CREATED PRIVATE worktree, never canonical.
Defaults to no writes. Supports newer certified identities without demotion.
Raises on any unresolved field/JSON/identity conflict. No stock writes/builds/push.
"""
from pathlib import Path
import argparse,csv,json,subprocess,os,hashlib,collections,sys,ast
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('target',type=Path);ap.add_argument('--expected-head',required=True);ap.add_argument('--apply',action='store_true');ap.add_argument('--report',type=Path,required=True);args=ap.parse_args();R=args.target.resolve();A=R/'reverse-engineering/kernel-source-parity-audit'
if R.name in ['ulefone-gq5012bf1-research','ulefone-gq5012bf1-research-codex-all-c-closure']:raise SystemExit('Refuse canonical/Category-C owner checkout; create a new private worktree')
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip();assert head==args.expected_head,'HEAD advanced; re-review'
# Validator baseline must pass against restored private operands before any write.
p=subprocess.run([sys.executable,str(A/'scripts/validate.py')],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));assert p.returncode==0,p.stdout[-1800:]+p.stderr

def table(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def write(p,rows,fields=None):
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
base=table(A/'ALL-457-MODULES.tsv');rows=[dict(r) for r in base];by={r['module_id']:r for r in rows};plan=table(P/'FINAL-FIELD-DELTA.tsv');ids={d['module_id'] for d in plan};conflicts=[];applied=[];skipped=set()
for i in ids:
 ds=[d for d in plan if d['module_id']==i];r=by.get(i)
 if r is None or any(r[k]!=ds[0][k] for k in ['filename','stock_sha256','stock_size']):conflicts.append(dict(module_id=i,reason='IDENTITY_HASH_SIZE_CONFLICT'));continue
 status=next(d for d in ds if d['field']=='source_status')
 # An already integrated identical proposal is idempotent. A newer proved A/B
 # protects the WHOLE identity, including source/parity/owner metadata.
 if r['source_status'] in ['A','B'] and any(r[d['field']]!=d['proposed_after'] for d in ds):skipped.add(i);continue
 for d in ds:
  key=d['field']
  if r[key]==d['proposed_after']:continue
  if r[key]!=d['expected_before']:conflicts.append(dict(module_id=i,field=key,expected=d['expected_before'],current=r[key],proposed=d['proposed_after']));continue
  r[key]=d['proposed_after'];applied.append(d)
review=json.loads((A/'evidence/source-reviews.json').read_text());hashes=json.loads((A/'evidence/review-input-hashes.json').read_text())
for name,current in [('source-reviews.json',review),('review-input-hashes.json',hashes)]:
 records=json.loads((P/('FINAL-'+name)).read_text())
 for i,record in records.items():
  if i in skipped:continue
  old,new=record['expected_before'],record['proposed_after'];cur=current[i]
  for key in set(old)|set(new):
   if old.get(key)==new.get(key):continue
   if cur.get(key)==new.get(key):continue
   if cur.get(key)!=old.get(key):conflicts.append(dict(module_id=i,json=name,key=key,reason='NEWER_JSON_FIELD_REQUIRES_OWNER_REVIEW'));continue
   if key in new:cur[key]=new[key]
   else:cur.pop(key,None)
report=dict(target=str(R),head=head,apply=args.apply,field_changes=len(applied),protected_newer_certified=sorted(skipped),conflicts=conflicts,counts={s:sum(r['source_status']==s for r in rows) for s in 'ABCDEFG'},no_stock_writes=True)
args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n')
if conflicts:raise SystemExit('STOP: owner review required; target untouched, see report')
assert len(by)==458 and all(by[r['module_id']]==r for r in base if r['module_id'] not in ids)
if args.apply:
 # The same pure authoritative derivative/validator function used by staging.
 # AST-selecting the function prevents executing the staging-specific main body
 # or hard-coded f61 counts in the new owner's context.
 code=ast.parse((P/'scripts/apply-staging.py').read_text());fn=next(n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='regenerate')
 E=args.report.parent;sid=ids;SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ns=dict(globals());ns.update(locals());exec(compile(ast.Module(body=[fn],type_ignores=[]),str(P/'scripts/apply-staging.py'),'exec'),ns);ns['regenerate']('owner-reconciled')
 p=subprocess.run([sys.executable,str(A/'scripts/test_validate.py'),'-v'],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));(E/'owner-mutations.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()==head,'Concurrent commit detected; do not integrate'
print(json.dumps(dict(result='APPLIED_AND_VALIDATED' if args.apply else 'DRY_RUN_READY',field_changes=len(applied),newer_certified_preserved=len(skipped),counts=report['counts']),indent=2))
