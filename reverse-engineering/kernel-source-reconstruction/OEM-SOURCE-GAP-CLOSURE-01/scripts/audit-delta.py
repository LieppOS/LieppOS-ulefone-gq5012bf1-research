#!/usr/bin/env python3
"""OEM-SOURCE-GAP-CLOSURE-01 (tmem_ffa C->A) identity-keyed, field-level audit delta (compare-and-swap).

  audit-delta.py plan                       -> writes AUDIT-DELTA.tsv from the canonical 0390534d rows (read-only)
  audit-delta.py apply <scratch-root> --expected-head SHA [--canonical-base SHA]
        applies AUDIT-DELTA.tsv to <scratch-root>'s audit only, updates source-reviews.json and
        review-input-hashes.json for the 5 certified rows, runs the reviewed regenerate() (AST-extracted from
        COMPLETED-BATCHES-INTEGRATION-01/scripts/apply-staging.py, unmodified), restores the current
        canonical queue narrative header, then the unchanged validator and 14 audit mutation tests.

Refuses the canonical checkout and this research branch worktree. Stops before writing on any CAS,
identity, hash or size mismatch. Never touches stock files, CRC, BTF or srcversion.
"""
import argparse, ast, collections, csv, hashlib, json, os, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]
HERE = P.parents[2]
CANON_BASE = '4e47a5b9369577751c2457da0c42ec194f56d332'
REPO = '../android_kernel_modules_trustkernel_abi_ulefone_gq5012bf1'
COMMIT = '15e7e8d8d4f9cbf56982791b2fac0e54087d0f49'
PKG = 'reverse-engineering/kernel-source-reconstruction/OEM-SOURCE-GAP-CLOSURE-01'
AUD = 'reverse-engineering/kernel-source-parity-audit'
ap = argparse.ArgumentParser()
ap.add_argument('mode', choices=['plan', 'apply'])
ap.add_argument('scratch', nargs='?')
ap.add_argument('--expected-head')
ap.add_argument('--canonical-base', default=CANON_BASE)
args = ap.parse_args()


def show(path, commit):
    return subprocess.check_output(['git', '-C', str(HERE), 'show', f'{commit}:{path}'], text=True)


def rd(text):
    return list(csv.DictReader(text.splitlines(), delimiter='\t'))


def write(p, rows, fields=None):
    with Path(p).open('w') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)


if args.mode == 'plan':
    base = {r['module_id']: r for r in rd(show(f'{AUD}/ALL-457-MODULES.tsv', args.canonical_base))}
    man = list(csv.DictReader((P / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
    par = {r['module_id']: r for r in csv.DictReader((P / 'BATCH-PARITY.tsv').open(), delimiter='\t')}
    ev = f'{PKG}/evidence/independent-proof'
    out = []
    for m in man:
        i = m['module_id']; r = base[i]; p = par[i]
        assert r['source_status'] == 'C' and r['stock_sha256'] == m['stock_sha256']
        n = int(r['stock_functions'])
        acc = [json.loads((P / f'evidence/independent-proof/{x}/acceptance/acceptance.json').read_text()) for x in ('B1', 'B2')]
        mod = m['filename'].removesuffix('.ko')
        assert all((P / f'evidence/independent-proof/{x}/verify-exit').read_text().strip() == '0' for x in ('B1', 'B2'))
        assert acc[0][mod]['normalized_sha256'] == acc[1][mod]['normalized_sha256'] and acc[0][mod]['functions'] == n
        owner = f"OEM-SOURCE-GAP-CLOSURE-01:{m['family']}"
        after = dict(source_status='A', abi_status='VERIFIED', crc_status='VERIFIED', kcfi_status='VERIFIED', blocker='NONE',
                     build_script=f'{REPO}/scripts/build-reproducible.sh', equivalent_functions='0', exact_functions=str(n), unresolved_functions='0',
                     gap_kind='NONE_SOURCE_CERTIFIED', parity_evidence=f'{ev}/B1/acceptance/acceptance.json;{ev}/B2/acceptance/acceptance.json',
                     reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2', source_commit=COMMIT, source_group=owner, source_owner=owner,
                     source_pin=f'{REPO}/SOURCE-PINS.tsv', source_repo=REPO, source_snapshot_path=f'{REPO}/SOURCE-PINS.tsv',
                     verified_difference_classification='GNU20_ONLY')
        for k, v in after.items():
            if r[k] != v:
                out.append(dict(module_id=i, filename=r['filename'], stock_sha256=r['stock_sha256'], stock_size=r['stock_size'],
                                stock_paths=r['stock_paths'], field=k, expected_before=r[k], proposed_after=v, canonical_base=args.canonical_base))
    write(P / 'AUDIT-DELTA.tsv', out)
    print('AUDIT-DELTA', len(out), 'field changes over', len({o['module_id'] for o in out}), 'identities')
    raise SystemExit(0)

# ---------------------------------------------------------------- apply (scratch only)
R = Path(args.scratch).resolve()
assert R.name not in ('ulefone-gq5012bf1-research', HERE.name), 'refuse canonical / research branch worktree; scratch only'
head = subprocess.check_output(['git', '-C', str(R), 'rev-parse', 'HEAD'], text=True).strip()
assert head == args.expected_head, f'scratch HEAD {head} != expected'
A = R / AUD; E = R / PKG / 'evidence/audit-scratch'; E.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
pre = subprocess.run([sys.executable, str(A / 'scripts/validate.py')], capture_output=True, text=True, env=env)
(E / 'pre-validate.json').write_text(pre.stdout); assert pre.returncode == 0, 'scratch pre-state must validate: ' + pre.stdout[-2000:]
table = lambda p: list(csv.DictReader(Path(p).open(), delimiter='\t'))
SHA = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
base = table(A / 'ALL-457-MODULES.tsv'); rows = [dict(r) for r in base]; by = {r['module_id']: r for r in rows}
assert len(by) == 458
review = json.loads((A / 'evidence/source-reviews.json').read_text())
hashes = json.loads((A / 'evidence/review-input-hashes.json').read_text())
plan = table(R / PKG / 'AUDIT-DELTA.tsv'); sid = {d['module_id'] for d in plan}
snapshot = {i: dict(r) for i, r in by.items()}
log, conflicts = [], []
for d in plan:
    r = by.get(d['module_id'])
    if r is None or r['stock_sha256'] != d['stock_sha256'] or r['stock_size'] != d['stock_size'] or r['filename'] != d['filename'] or r['stock_paths'] != d['stock_paths']:
        conflicts.append(dict(module_id=d['module_id'], reason='IDENTITY_HASH_SIZE_PATH')); continue
    k = d['field']
    if r[k] == d['proposed_after']:
        log.append(dict(d, result='ALREADY_APPLIED')); continue
    if r[k] != d['expected_before']:
        conflicts.append(dict(module_id=d['module_id'], field=k, expected=d['expected_before'], current=r[k])); continue
    r[k] = d['proposed_after']; log.append(dict(d, result='APPLIED'))
    if d['module_id'] in review and k in review[d['module_id']]:
        review[d['module_id']][k] = r[k].split(';') if k == 'parity_evidence' else r[k]
if conflicts:
    (E / 'conflicts.json').write_text(json.dumps(conflicts, indent=1)); raise SystemExit('STOP before write: CAS conflicts')
assert all(snapshot[i] == by[i] for i in by if i not in sid), 'unselected row changed'
recipe = [l for l in subprocess.check_output(['git', '-C', str((R / REPO).resolve()), 'ls-files'], text=True).splitlines()
          if l.startswith(('scripts/', 'reference/', 'patches/', 'families/')) or l == 'SOURCE-PINS.tsv' or l.startswith('source/')]
for i in sid:
    inputs = dict(hashes[i])
    for p in by[i]['parity_evidence'].split(';'):
        inputs[p] = SHA(R / p)
    for rel in recipe:
        inputs[f'{REPO}/{rel}'] = SHA(R / REPO / rel)
    hashes[i] = inputs
code = ast.parse((R / 'reverse-engineering/kernel-source-reconstruction/COMPLETED-BATCHES-INTEGRATION-01/scripts/apply-staging.py').read_text())
fn = next(n for n in code.body if isinstance(n, ast.FunctionDef) and n.name == 'regenerate')
ns = dict(globals()); ns.update(sid=sid, E=E, A=A, base=base, rows=rows, by=by, review=review, hashes=hashes, table=table, write=write)
queue_before = (A / 'RECONSTRUCTION-QUEUE.md').read_text().splitlines()
exec(compile(ast.Module(body=[fn], type_ignores=[]), '<reviewed-regenerator>', 'exec'), ns)
ns['regenerate']('oem-source-gap-closure-01')
# Narrative: keep the current canonical integration header, append this batch (no other text changed).
q = (A / 'RECONSTRUCTION-QUEUE.md').read_text().splitlines()
old_hdr = next(l for l in queue_before if l.startswith('Completed integration'))
idx = next(n for n, l in enumerate(q) if l.startswith('Completed integration'))
# Compose on canonical after DISPLAY-INTEGRATION-01.
for anchor, new in [(' DISPLAY-BACKLIGHT-G-BATCH-01 (8 display/backlight/PWM/MET-backlight G->A). Retained', ' DISPLAY-BACKLIGHT-G-BATCH-01 (8 display/backlight/PWM/MET-backlight G->A); OEM-SOURCE-GAP-CLOSURE-01 (tmem_ffa C->A via stock-evidenced TrustKernel 6:1.1 provider witness). Retained')]:
    if old_hdr.count(anchor) == 1:
        q[idx] = old_hdr.replace(anchor, new); break
else:
    raise SystemExit('queue header anchor not found: ' + old_hdr)
(A / 'RECONSTRUCTION-QUEUE.md').write_text('\n'.join(q) + '\n')
post = subprocess.run([sys.executable, str(A / 'scripts/validate.py')], capture_output=True, text=True, env=env)
(E / 'post-validate.json').write_text(post.stdout); assert post.returncode == 0, post.stdout[-3000:]
mut = subprocess.run([sys.executable, str(A / 'scripts/test_validate.py'), '-v'], capture_output=True, text=True, env=env)
(E / 'audit-mutations.log').write_text(mut.stdout + mut.stderr); assert mut.returncode == 0, mut.stderr[-3000:]
res = json.loads(post.stdout)
write(R / PKG / 'evidence/audit-scratch/DELTA-APPLICATION-LOG.tsv', log)
result = dict(scratch_head=head, canonical_base=args.canonical_base, field_changes=sum(x['result'] == 'APPLIED' for x in log),
              identities=len({x['module_id'] for x in log}), validator=res['result'], errors=len(res['errors']),
              counts=res['source_status_counts'], distinct=res['distinct_stock_identities'], occurrences=res['stock_occurrences'],
              audit_mutations='PASS 14/14' if 'Ran 14 tests' in mut.stderr and '\nOK' in mut.stderr else mut.stderr[-300:])
(E / 'apply-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=1))
