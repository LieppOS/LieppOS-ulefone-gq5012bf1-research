#!/usr/bin/env python3
"""Validate AUDIO-BATCH-01 deliverables against the frozen baseline and preserved evidence."""
import csv, json, hashlib, subprocess, collections
from pathlib import Path
P = Path(__file__).resolve().parents[1]; R = P.parents[2]
ok = lambda c, m: (_ for _ in ()).throw(AssertionError(m)) if not c else None
rows = lambda n: list(csv.DictReader((P / n).open(), delimiter='\t'))
req = ['BATCH-MANIFEST.tsv', 'BATCH-PARITY.tsv', 'BATCH-SUMMARY.md', 'BATCH-STATE.json', 'SOURCE-REPOSITORIES.tsv', 'DEPENDENCIES.tsv',
       'AUDIO-HARDWARE-TOPOLOGY.md', 'AUDIO-DSP-BOUNDARIES.md', 'BLOCKERS.tsv', 'BUILD-REPRODUCTION.md', 'AUDIT-DELTA.tsv',
       'MERGE-INSTRUCTIONS.md', 'NEXT-BATCH.md', 'PROVIDER-BOUNDARIES.tsv']
for n in req: ok((P / n).stat().st_size > 400, f'missing/placeholder {n}')
ok(hashlib.sha256((P / 'BATCH-MANIFEST.tsv').read_bytes()).hexdigest() == (P / 'BATCH-MANIFEST.sha256').read_text().split()[0], 'manifest changed after freeze')
base = {r['module_id']: r for r in csv.DictReader((P / 'evidence/baseline/ALL-457-MODULES.tsv').open(), delimiter='\t')}
want = subprocess.check_output(['git', 'show', '548526fc711cf9943a20d2daad42158ee1543842:reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'], cwd=R)
ok((P / 'evidence/baseline/ALL-457-MODULES.tsv').read_bytes() == want, 'baseline snapshot drift')
ok(len(base) == 458, 'identity count')
live = R / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'
ok(live.read_bytes() == want, 'this branch must not modify the canonical audit')
man, par, dl = rows('BATCH-MANIFEST.tsv'), rows('BATCH-PARITY.tsv'), rows('AUDIT-DELTA.tsv')
ids = [r['module_id'] for r in man]
ok(len(ids) == 21 == len(set(ids)) and all(i in base for i in ids), 'manifest identities')
ok([r['module'] for r in par] == [r['filename'] for r in man] and [r['module_id'] for r in dl] == ids, 'row alignment')
for d in dl:
    ok(base[d['module_id']]['source_status'] == d['old_source_status'] == 'G', f"old class {d['filename']}")
b4 = {r['module_id'] for r in csv.DictReader((R / 'reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-04/BATCH-MANIFEST.tsv').open(), delimiter='\t')}
ok(not b4 & set(ids), 'overlap with PLATFORM-BATCH-04')
acc = json.loads((P / 'evidence/cleancheck/acceptance-B1/acceptance.json').read_text())
acc2 = json.loads((P / 'evidence/cleancheck/acceptance-B2/acceptance.json').read_text())
ok(acc == acc2, 'B1/B2 acceptance differ')
for p in par:
    m = p['module'][:-3]
    if p['final_class'] == 'A':
        a = acc[m]; ok(a['unresolved'] == 0 and a['raw_differing_bytes'] <= 20, f'A without whole-file proof {m}')
        lo, n = a['allowed_range']; ok(all(lo <= o < lo + n for o in a['raw_difference_offsets']), f'diff outside build-id {m}')
    else:
        ok(p['final_class'] == 'C' and m == 'aw883xx_driver', 'unexpected non-A')
blk = rows('BLOCKERS.tsv'); ok({b['module'] for b in blk} == {p['module'] for p in par if p['final_class'] != 'A'}, 'blockers incomplete')
cnt = collections.Counter(d['new_source_status'] for d in dl)
base_cnt = collections.Counter(r['source_status'] for r in base.values())
proj = base_cnt.copy(); proj['G'] -= 21; proj.update(cnt)
st = json.loads((P / 'BATCH-STATE.json').read_text())
ok(st['projected_canonical_counts_provisional'] == dict(proj) and st['projected_certified_provisional'] == proj['A'] + proj['B'] == 240, 'projection')
pb = rows('PROVIDER-BOUNDARIES.tsv'); ok(len(pb) == 39 and all(r['result'] == 'MATCH' and r['provider_classification_changed'] == 'no' for r in pb), 'provider boundary')
cmp = (P / 'evidence/cleancheck/B1-B2-compare.log').read_text(); ok(cmp.count('IDENTICAL') == 5, 'B1/B2 compare')
ok('CLEANCHECK PASS ' + st['source_commits']['android_kernel_modules_audio_ulefone_gq5012bf1'] in (P / 'evidence/cleancheck/run.log').read_text(), 'cleancheck pass')
print('AUDIO-BATCH-01 VALID:', dict(cnt), 'projected certified', proj['A'] + proj['B'], '/ 458; canonical audit untouched')
