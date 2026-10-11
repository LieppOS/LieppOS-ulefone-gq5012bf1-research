#!/usr/bin/env python3
"""Validate SCP-CONNECTIVITY-BATCH-01 deliverables against the frozen baseline and preserved evidence."""
import csv, json, hashlib, subprocess, collections
from pathlib import Path

P = Path(__file__).resolve().parents[1]; R = P.parents[2]
def ok(c, m):
    if not c: raise AssertionError(m)
rows = lambda n: list(csv.DictReader((P / n).open(), delimiter='\t'))
req = ['BATCH-MANIFEST.tsv', 'BATCH-PARITY.tsv', 'BATCH-SUMMARY.md', 'BATCH-STATE.json', 'SOURCE-REPOSITORIES.tsv', 'DEPENDENCIES.tsv',
       'SCP-HOST-INTERFACES.md', 'SENSOR-HUB-TOPOLOGY.md', 'CONNECTIVITY-HARDWARE.md', 'FIRMWARE-BOUNDARIES.md', 'BLOCKERS.tsv',
       'BUILD-REPRODUCTION.md', 'AUDIT-DELTA.tsv', 'MERGE-INSTRUCTIONS.md', 'NEXT-BATCH.md', 'PROVIDER-BOUNDARIES.tsv']
for n in req: ok((P / n).stat().st_size > 400, f'missing/placeholder {n}')
ok(hashlib.sha256((P / 'BATCH-MANIFEST.tsv').read_bytes()).hexdigest() == (P / 'BATCH-MANIFEST.sha256').read_text().split()[0], 'manifest changed after freeze')
want = subprocess.check_output(['git', 'show', '548526fc711cf9943a20d2daad42158ee1543842:reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'], cwd=R)
ok((P / 'evidence/baseline/ALL-457-MODULES.tsv').read_bytes() == want, 'baseline snapshot drift')
ok((R / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').read_bytes() == want, 'this branch must not modify the canonical audit')
base = {r['module_id']: r for r in csv.DictReader((P / 'evidence/baseline/ALL-457-MODULES.tsv').open(), delimiter='\t')}
ok(len(base) == 458, 'identity count')
man, par, dl = rows('BATCH-MANIFEST.tsv'), rows('BATCH-PARITY.tsv'), rows('AUDIT-DELTA.tsv')
ids = [r['module_id'] for r in man]
ok(len(ids) == 20 == len(set(ids)) and all(i in base for i in ids), 'manifest identities')
ok([r['module'] for r in par] == [r['filename'] for r in man] and [r['module_id'] for r in dl] == ids, 'row alignment')
for d in dl: ok(base[d['module_id']]['source_status'] == d['old_source_status'] == 'G', 'old class ' + d['filename'])
b4 = {r['module_id'] for r in csv.DictReader((R / 'reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-04/BATCH-MANIFEST.tsv').open(), delimiter='\t')}
au = {r['module_id'] for r in csv.DictReader((R.parent / 'ulefone-gq5012bf1-research-codex-audio/reverse-engineering/kernel-source-reconstruction/AUDIO-BATCH-01/BATCH-MANIFEST.tsv').open(), delimiter='\t')}
ok(len(b4) == 30 and len(au) == 21 and not (b4 | au) & set(ids) and not b4 & au, 'overlap between concurrent batches')
acc = {}
for k, n, mut in (('scp-sensorhub', 3, 23), ('connectivity', 17, 29)):
    E = P / 'evidence' / k / 'cleancheck'
    a1 = json.loads((E / 'acceptance-B1/acceptance.json').read_text()); a2 = json.loads((E / 'acceptance-B2/acceptance.json').read_text())
    ok(a1 == a2, f'{k}: B1/B2 acceptance differ'); acc.update(a1)
    ok((E / 'B1-B2-compare.log').read_text().count('IDENTICAL') == 5, f'{k}: B1/B2 compare')
    ok('CLEANCHECK PASS' in (E / 'run.log').read_text() and 'dev checkout and dev workspace hidden' in (E / 'run.log').read_text(), f'{k}: cleancheck')
    ok(json.loads((E / 'acceptance-B1/mutation-test.log').read_text().strip().splitlines()[-1]) == {'mutations': mut, 'all_detected': True}, f'{k}: mutations')
    ok('failed 0 ' in (E / 'acceptance-B1/provider.log').read_text(), f'{k}: provider witnesses')
c1 = json.loads((P / 'evidence/connectivity/cleancheck/acceptance-B1/class-c-residuals.json').read_text())
ok(c1 == json.loads((P / 'evidence/connectivity/cleancheck/acceptance-B2/class-c-residuals.json').read_text()), 'C residual B1/B2')
for p in par:
    m = p['module'][:-3]
    if p['final_class'] == 'A':
        a = acc[m]; lo = a['allowed_range'][0]
        ok(a['unresolved'] == 0 and all(lo <= o < lo + 20 for o in a['raw_difference_offsets']), 'A without whole-file proof ' + m)
    else:
        ok(p['final_class'] == 'C' and m in c1 and c1[m]['non_btf_bytes_identical'] and c1[m]['id_mapping_bijective'], 'unexpected class ' + m)
ok({b['module'] for b in rows('BLOCKERS.tsv')} == {p['module'] for p in par if p['final_class'] != 'A'}, 'blockers incomplete')
pb = rows('PROVIDER-BOUNDARIES.tsv')
ok(len(pb) == 57 and all(r['provider_classification_changed'] == 'no' for r in pb)
   and collections.Counter(r['result'] for r in pb) == {'MATCH': 47, 'DECLARED': 10}
   and {r['provider_module'] for r in pb if r['result'] == 'DECLARED'} == {'yft_devinfo'}, 'provider boundary ledger')
cnt = collections.Counter(d['new_source_status'] for d in dl)
proj = collections.Counter(r['source_status'] for r in base.values()); proj['G'] -= 20; proj.update(cnt)
st = json.loads((P / 'BATCH-STATE.json').read_text())
ok(st['projected_canonical_counts_provisional'] == dict(proj) and st['projected_certified_provisional'] == proj['A'] + proj['B'] == 237, 'projection')
dt = json.loads((P / 'evidence/audit-delta-test.json').read_text())
ok(dt['certified_after_this_delta'] == 237 and dt['changed_rows'] == 20 and all(v == 'REJECTED' for v in dt['mutation_tests'].values()) and not dt['live_canonical_touched'], 'delta test')
ok(all('BUNDLE-RECOVERY OK' in l for l in (P / 'evidence/bundle-recovery.log').read_text().strip().splitlines()), 'bundle recovery')
print('SCP-CONNECTIVITY-BATCH-01 VALID:', dict(cnt), 'projected certified', proj['A'] + proj['B'], '/ 458 (this delta only); canonical audit untouched; disjoint from AUDIO-BATCH-01 and PLATFORM-BATCH-04')
