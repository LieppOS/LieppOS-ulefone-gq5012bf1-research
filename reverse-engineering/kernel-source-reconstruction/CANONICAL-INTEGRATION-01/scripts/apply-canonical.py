#!/usr/bin/env python3
"""Apply CAS-PLAN.tsv stage by stage to THIS worktree's audit; regenerate derivatives with the
reviewed COMPLETED-BATCHES-INTEGRATION-01 regenerate() (AST-extracted, unmodified); run the
unchanged validator after each stage and the 14 audit mutation tests at the end.

usage: apply-canonical.py --expected-head SHA [--apply]
Dry run by default. Refuses the canonical checkout path. Stops before any write on a CAS
mismatch or identity/hash/size mismatch.  Never edits stock files, CRC, BTF or srcversion.
"""
import argparse, ast, collections, csv, hashlib, json, os, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
A = R / 'reverse-engineering/kernel-source-parity-audit'
E = P / 'evidence'
ap = argparse.ArgumentParser(); ap.add_argument('--expected-head', required=True); ap.add_argument('--apply', action='store_true')
args = ap.parse_args()
assert R.name != 'ulefone-gq5012bf1-research', 'refuse canonical checkout; private integration worktree only'
head = subprocess.check_output(['git', '-C', str(R), 'rev-parse', 'HEAD'], text=True).strip()
assert head == args.expected_head, f'HEAD {head} != expected'
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
FF_REPOS = tuple(f'../android_kernel_modules_{f}_ulefone_gq5012bf1/' for f in
                 ['cmdq', 'connectivity', 'thermal_cooling', 'audio_shared_infrastructure'])
pre = subprocess.run([sys.executable, str(A / 'scripts/validate.py')], capture_output=True, text=True, env=env)
if pre.returncode:
    # The only tolerated pre-state drift: proof-input files inside the four maintained source
    # repositories that were fast-forwarded to their verified tips (source-fast-forward.tsv).
    # Stage 4+5 resolves exactly these; anything else stops.
    errs = json.loads(pre.stdout)['errors']
    bad = [e for e in errs if not (e['code'] == 'PROOF_INPUT_HASH_CHANGED' and e['message'].startswith(FF_REPOS))]
    assert not bad, 'unexpected pre-state validator errors: ' + json.dumps(bad[:10])
    PRE_DRIFT = sorted({e['message'] for e in errs})
else:
    PRE_DRIFT = []


def table(p): return list(csv.DictReader(Path(p).open(), delimiter='\t'))


def write(p, rows, fields=None):
    with Path(p).open('w') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)


SHA = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
base = table(A / 'ALL-457-MODULES.tsv'); rows = [dict(r) for r in base]; by = {r['module_id']: r for r in rows}
assert len(by) == 458
review = json.loads((A / 'evidence/source-reviews.json').read_text())
hashes = json.loads((A / 'evidence/review-input-hashes.json').read_text())
plan = table(P / 'CAS-PLAN.tsv')
log, counts, conflicts, planned = [], [], [], []


def count(label):
    c = {s: sum(r['source_status'] == s for r in rows) for s in 'ABCDEFG'}
    counts.append(dict(step=label, **c, certified=c['A'] + c['B'], uncertified=458 - c['A'] - c['B']))


# AST-extract the reviewed regenerator exactly as NEXT-DG reconcile-owner.py did.
code = ast.parse((R / 'reverse-engineering/kernel-source-reconstruction/COMPLETED-BATCHES-INTEGRATION-01/scripts/apply-staging.py').read_text())
fn = next(n for n in code.body if isinstance(n, ast.FunctionDef) and n.name == 'regenerate')
count('pre-stage4 (437ebd57 + original package merges)')
for label, stages in [('4+5-ALL-C-AND-SOURCE-SUPERSEDE', ['4-ALL-C', '5-SOURCE-SUPERSEDE']), ('6-USB-TYPEC-CLOSURE', ['6-USB-TYPEC-CLOSURE'])]:
    steps = [d for d in plan if d['stage'] in stages]; sid = {d['module_id'] for d in steps}; stage = label
    snapshot = {i: dict(by[i]) for i in by}
    for d in steps:
        r = by.get(d['module_id'])
        if r is None or r['stock_sha256'] != d['stock_sha256'] or r['stock_size'] != d['stock_size'] or r['filename'] != d['filename']:
            conflicts.append(dict(stage=stage, module_id=d['module_id'], reason='IDENTITY_HASH_SIZE')); continue
        k = d['field']
        if r[k] == d['proposed_after']:
            log.append(dict(d, result='ALREADY_APPLIED')); continue
        if r[k] != d['expected_before']:
            conflicts.append(dict(stage=stage, module_id=d['module_id'], field=k, expected=d['expected_before'], current=r[k])); continue
        r[k] = d['proposed_after']; log.append(dict(d, result='APPLIED'))
        if d['module_id'] in review:
            review[d['module_id']][k] = r[k].split(';') if k == 'parity_evidence' else r[k]
    if conflicts:
        raise SystemExit('STOP before write: ' + json.dumps(conflicts, indent=1))
    # Review-input hashes record the new proof inputs for promoted identities (A rows are
    # not sha-pinned; C rows keep their existing pin material unchanged).
    for i in sid:
        if by[i]['source_status'] == 'A':
            inputs = dict(hashes[i])
            for p in by[i]['parity_evidence'].split(';'): inputs[p] = SHA(R / p)
            for rel in [by[i]['source_pin'], by[i]['build_script']]: inputs[rel] = SHA(R / rel)
            for rel in list(inputs):  # refresh proof inputs of the superseding verified tip
                if rel.startswith(FF_REPOS): inputs[rel] = SHA(R / rel)
            hashes[i] = inputs
    assert all(snapshot[i] == by[i] for i in by if i not in sid), 'unselected row changed'
    for s in stages: planned.append(dict(stage=s, fields=sum(d['stage'] == s for d in steps),
                                        identities=len({d['module_id'] for d in steps if d['stage'] == s})))
    count(stage)
    if args.apply:
        ns = dict(globals()); ns.update(sid=sid, E=E)
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<reviewed-regenerator>', 'exec'), ns)
        ns['regenerate']('stage' + stage)
E.mkdir(parents=True, exist_ok=True)
write(P / 'DELTA-APPLICATION-LOG.tsv', log)
write(P / 'CLASSIFICATIONS-BEFORE-AFTER.tsv', counts)
result = dict(head=head, apply=args.apply, tolerated_pre_drift=PRE_DRIFT, field_changes=sum(x['result'] == 'APPLIED' for x in log),
              identities=len({x['module_id'] for x in log}), planned=planned, counts=counts, conflicts=conflicts)
if args.apply:
    m = subprocess.run([sys.executable, str(A / 'scripts/test_validate.py'), '-v'], capture_output=True, text=True, env=env)
    (E / 'audit-mutations-final.log').write_text(m.stdout + m.stderr); assert m.returncode == 0, m.stderr[-3000:]
    result['audit_mutations'] = 'PASS 14/14' if 'Ran 14 tests' in m.stderr and 'OK' in m.stderr else m.stderr[-300:]
    assert subprocess.check_output(['git', '-C', str(R), 'rev-parse', 'HEAD'], text=True).strip() == head, 'concurrent commit'
(E / ('apply-result.json' if args.apply else 'dry-run-result.json')).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'conflicts'}, indent=1))
