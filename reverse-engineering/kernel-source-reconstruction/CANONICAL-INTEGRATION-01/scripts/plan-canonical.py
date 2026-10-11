#!/usr/bin/env python3
"""Deterministically derive the Stage-4 (ALL-C 10 promotions) and Stage-6 (USB closure
22 fields) compare-and-swap plans.

expected_before values come ONLY from committed audit blobs (git show), never from the
working tree being changed:
  * ALL-C: staged audit at NEXT-DG 437ebd57 (the actual pre-Stage-4 integration audit).
  * USB:   the original USB-TYPEC-CLOSURE AUDIT-DELTA rows (prepared against f61ebf03),
           re-checked here against 437ebd57 so a drifted row fails instead of overwriting.
Ownership fields source_owner/source_group/source_repo/build_script are deliberately
NOT in the ALL-C plan: original batch ownership is preserved; only the proven status,
commit, proof and residual fields change.  No CRC/BTF/srcversion value is touched.
"""
import csv, io, json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
STAGED = '437ebd5762afa2512fe1ba10102e6b4f4d6beba9'
AUD = 'reverse-engineering/kernel-source-parity-audit/'
ALLC = R / 'reverse-engineering/kernel-source-reconstruction/ALL-C-TO-A-CLOSURE'
USB = R / 'reverse-engineering/kernel-source-reconstruction/USB-TYPEC-CLOSURE'
show = lambda p: subprocess.check_output(['git', 'show', f'{STAGED}:{p}'], cwd=R, text=True)
rows = {r['module_id']: r for r in csv.DictReader(io.StringIO(show(AUD + 'ALL-457-MODULES.tsv')), delimiter='\t')}
frozen = json.loads(show(AUD + 'evidence/stock-identities.json'))
state = json.loads((ALLC / 'C-CLOSURE-STATE.json').read_text())
family = {  # ALL-C evidence directory, canonical reverify prefix, verified maintained tip
    'cmdq': ('cmdq', '0b4b07f38397ca6c0630b9edc5ccf2df9251da1d'),
    'connectivity': ('connectivity', '40bf42967a213af6faa45a6a579571973b8e5d15'),
    'thermal_cooling': ('thermal', 'ff6e97b3bf1f29c1e1fba4ba0c0e28493cbd0698'),
    'audio_shared_infrastructure': ('drm', '4697eac32544fbfaeab76f6d7a5367a8d8d32460')}
REV = 'reverse-engineering/kernel-source-reconstruction/CANONICAL-INTEGRATION-01/evidence/reverify/'
plan = []
accepted = [m for m in state['modules'] if m['accepted']]
assert len(accepted) == 10
for m in accepted:
    i = m['module_id']; r = rows[i]
    assert r['source_status'] == 'C', (i, r['source_status'])
    assert r['stock_sha256'] == m['stock_sha256']
    fam = r['source_repo'].removeprefix('../android_kernel_modules_').removesuffix('_ulefone_gq5012bf1')
    rdir, tip = family[fam]
    assert m['source_commit'] == tip, (i, m['source_commit'])
    revdir = 'connectivity' if rdir == 'connectivity' else rdir
    proof = [f'reverse-engineering/kernel-source-reconstruction/ALL-C-TO-A-CLOSURE/{e}' for e in m['evidence']]
    proof += [f'{REV}{revdir}-B1/acceptance.json', f'{REV}{revdir}-B2/acceptance.json']
    count = str(frozen[i]['function_count'])
    after = dict(source_status='A', source_commit=tip,
                 source_pin=f"{r['source_repo']}/SOURCE-PINS.tsv",
                 parity_evidence=';'.join(proof), abi_status='VERIFIED', crc_status='VERIFIED',
                 kcfi_status='VERIFIED', exact_functions=count, equivalent_functions='0',
                 unresolved_functions='0', verified_difference_classification='GNU20_ONLY',
                 blocker='NONE',
                 preservation_risk='LOW: maintained repository fast-forwarded to verified tip; ALL-C fresh-bundle B1/B2; canonical combined-environment strict reverification; recovery bundle verified')
    for k, v in after.items():
        if r[k] != v:
            plan.append(dict(stage='4-ALL-C', module_id=i, filename=r['filename'], stock_sha256=r['stock_sha256'],
                             stock_size=r['stock_size'], field=k, expected_before=r[k], proposed_after=v))
# Stage 5: the verified newer recipe supersedes the older tip for every ALREADY-A row owned by a
# fast-forwarded maintained repository whose recorded proof inputs changed.  Each such row must
# pass the canonical combined-environment strict reverification in BOTH builds; otherwise abort.
REVROOT = R / REV
stage4 = {p['module_id'] for p in plan}
for fam, (rdir, tip) in family.items():
    repo = f'../android_kernel_modules_{fam}_ulefone_gq5012bf1'
    revdir = rdir
    acc = [json.loads((REVROOT / f'{revdir}-{t}/acceptance.json').read_text()) for t in ['B1', 'B2']]
    for i, r in rows.items():
        if r['source_repo'] != repo or i in stage4 or r['source_status'] != 'A' or r['source_commit'] == tip:
            continue
        changed = [p for p in json.loads(show(AUD + 'evidence/review-input-hashes.json'))[i]
                   if p.startswith(repo + '/') and subprocess.run(['git', '-C', str(R.parent / repo[3:]), 'diff', '--quiet',
                   r['source_commit'], tip, '--', p[len(repo) + 1:]]).returncode]
        if not changed:
            continue
        name = r['filename'][:-3]
        assert all(a[name]['stock_sha256'] == r['stock_sha256'] and a[name]['unresolved'] == 0 for a in acc), (i, 'not reverified')
        extra = [f'{REV}{revdir}-B1/acceptance.json', f'{REV}{revdir}-B2/acceptance.json']
        for k, v in [('source_commit', tip), ('parity_evidence', ';'.join(r['parity_evidence'].split(';') + extra))]:
            plan.append(dict(stage='5-SOURCE-SUPERSEDE', module_id=i, filename=r['filename'], stock_sha256=r['stock_sha256'],
                             stock_size=r['stock_size'], field=k, expected_before=r[k], proposed_after=v))
usb = list(csv.DictReader((USB / 'AUDIT-DELTA.tsv').open(), delimiter='\t'))
assert len(usb) == 22
for d in usb:
    r = rows[d['module_id']]
    assert r['source_status'] == 'C' and d['field'] != 'source_status'
    assert r[d['field']] == d['expected_before'], ('USB drift', d['module_id'], d['field'])
    plan.append(dict(stage='6-USB-TYPEC-CLOSURE', module_id=d['module_id'], filename=d['filename'],
                     stock_sha256=r['stock_sha256'], stock_size=r['stock_size'], field=d['field'],
                     expected_before=d['expected_before'], proposed_after=d['proposed_after']))
assert not ({p['module_id'] for p in plan if p['stage'].startswith('4')} & {p['module_id'] for p in plan if p['stage'].startswith('6')})
out = P / 'CAS-PLAN.tsv'
with out.open('w', newline='') as f:
    w = csv.DictWriter(f, list(plan[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(plan)
print(f'stage5 supersede: {sum(p["stage"].startswith("5") for p in plan)} field CAS over '
      f'{len({p["module_id"] for p in plan if p["stage"].startswith("5")})} already-A identities')
print(f'plan: {sum(p["stage"].startswith("4") for p in plan)} ALL-C field CAS over '
      f'{len({p["module_id"] for p in plan if p["stage"].startswith("4")})} identities; '
      f'{sum(p["stage"].startswith("6") for p in plan)} USB field CAS over '
      f'{len({p["module_id"] for p in plan if p["stage"].startswith("6")})} identities')
