#!/usr/bin/env python3
"""Actual planner AST on in-memory synthetic guard controls; no ELF/proof forgery."""
from pathlib import Path
import ast,csv,copy,json
P=Path(__file__).resolve().parents[1]
def table(p):return list(csv.DictReader(p.open(),delimiter='\t'))
plan=table(P/'AUDIT-DELTA.tsv');base=table(P/'evidence/baseline-ALL-457-MODULES.tsv');identity=plan[0]['module_id'];ds=[d for d in plan if d['module_id']==identity];original=next(r for r in base if r['module_id']==identity)
t=ast.parse((P/'scripts/reconcile-owner.py').read_text());loop=next(n for n in t.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='i');code=compile(ast.Module(body=[loop],type_ignores=[]),'<actual-next-DG-planner>','exec')
def evaluate(row):
 ns=dict(ids={identity},plan=copy.deepcopy(ds),by={identity:copy.deepcopy(row)} if row else {},conflicts=[],applied=[],skipped=set());exec(code,ns);return ns
cases={};r=evaluate(original);assert not r['conflicts'] and len(r['applied'])==len(ds);cases['authentic_baseline']='APPLY'
already=dict(original)
for d in ds:already[d['field']]=d['proposed_after']
r=evaluate(already);assert not r['conflicts'] and not r['applied'];cases['identical_reapply']='IDEMPOTENT'
r=evaluate(None);assert r['conflicts'];cases['unknown_identity']='REJECT'
for k in ['stock_sha256','stock_size','source_owner']:
 row=dict(original);row[k]='mutated';r=evaluate(row);assert r['conflicts'];cases[k]='REJECT'
row=dict(original,source_status='C');r=evaluate(row);assert r['conflicts'];cases['unexpected_C']='REJECT'
for s in ['A','B']:
 row=dict(original,source_status=s,source_commit='newer-genuine-certified-source');r=evaluate(row);assert identity in r['skipped'] and not r['applied'];cases['newer_'+s]='WHOLE_IDENTITY_PROTECTED'
print(json.dumps(dict(result='PASS',controls=len(cases),cases=cases),indent=2))
