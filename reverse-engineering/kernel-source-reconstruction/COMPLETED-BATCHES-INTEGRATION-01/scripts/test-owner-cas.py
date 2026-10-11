#!/usr/bin/env python3
"""Exercise the actual owner's pure planning AST on synthetic conflict variants.
No proof/classification is fabricated on disk. No audit/stock files are written.
"""
from pathlib import Path
import ast,csv,copy,json
P=Path(__file__).resolve().parents[1]
def table(p):return list(csv.DictReader(p.open(),delimiter='\t'))
plan=table(P/'FINAL-FIELD-DELTA.tsv');base=table(P/'evidence/baseline-ALL-457-MODULES.tsv');identity=plan[0]['module_id'];ds=[d for d in plan if d['module_id']==identity];original=next(r for r in base if r['module_id']==identity)
t=ast.parse((P/'scripts/reconcile-owner.py').read_text());loop=next(n for n in t.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='i');code=compile(ast.Module(body=[loop],type_ignores=[]),'<actual-owner-CAS-loop>','exec')
def evaluate(row,delta=ds):
 ns=dict(ids={d['module_id'] for d in delta},plan=copy.deepcopy(delta),by={identity:copy.deepcopy(row)} if row else {},conflicts=[],applied=[],skipped=set());exec(code,ns);return ns
cases={}
r=evaluate(original);assert not r['conflicts'] and len(r['applied'])==len(ds);cases['authentic_baseline']='APPLY'
already=dict(original)
for d in ds:already[d['field']]=d['proposed_after']
r=evaluate(already);assert not r['conflicts'] and not r['applied'];cases['identical_second_apply']='IDEMPOTENT_NO_CHANGE'
r=evaluate(None);assert r['conflicts'];cases['unknown_identity']='REJECT'
for key in ['stock_sha256','stock_size','source_owner']:
 row=dict(original);row[key]='corrupted-or-new-owner';r=evaluate(row);assert r['conflicts'];cases[key+'_mutation']='REJECT'
row=dict(original);row['source_status']='C';r=evaluate(row);assert r['conflicts'];cases['unexpected_current_class']='REJECT'
for status in ['A','B']:
 row=dict(original,source_status=status,source_commit='newer-valid-source-is-protected');r=evaluate(row);assert identity in r['skipped'] and not r['applied'];cases['newer_'+status]='PROTECT_WHOLE_IDENTITY_NO_DEMOTION'
print(json.dumps(dict(result='PASS',tests=len(cases),cases=cases),indent=2))
