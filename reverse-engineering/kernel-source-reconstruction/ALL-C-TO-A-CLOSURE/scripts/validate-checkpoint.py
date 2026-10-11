#!/usr/bin/env python3
"""Fail closed on checkpoint identity/proof/delta inconsistencies; read-only."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
required = ['C-CLOSURE-MANIFEST.tsv','C-CLOSURE-STATE.json','C-CLOSURE-SUMMARY.md',
    'MODULE-PARITY.tsv','SOURCE-PINS.tsv','SOURCE-CHANGES.tsv','EXPERIMENTS.tsv',
    'CMDQ-CRC-TYPE-GRAPHS.md','USB-SRCVERSION-PROVENANCE.md','TCPC-CLASS-FINAL-DIFFS.md',
    'OEM-BTF-BASE-INVESTIGATION.md','AW883XX-FINAL-DIFF.md','LEGACY-C-RECONSTRUCTION.md',
    'BLOCKERS.tsv','BUILD-REPRODUCTION.md','AUDIT-DELTA.tsv','MERGE-INSTRUCTIONS.md']
for name in required:
    assert (P/name).is_file() and (P/name).stat().st_size > 0, name
read = lambda name: list(csv.DictReader((P/name).open(),delimiter='\t'))
manifest = read('C-CLOSURE-MANIFEST.tsv')
state = json.loads((P/'C-CLOSURE-STATE.json').read_text())
sha = hashlib.sha256((P/'C-CLOSURE-MANIFEST.tsv').read_bytes()).hexdigest()
assert sha == (P/'C-CLOSURE-MANIFEST.sha256').read_text().split()[0] == state['frozen_manifest_sha256']
ids = {r['module_id'] for r in manifest}
assert len(manifest) == len(ids) == 18
assert {r['module_id'] for r in state['modules']} == ids
assert state['objective_complete'] is False
assert collections.Counter(r['final_class'] for r in state['modules']) == {'A':8,'C':10}
assert len(read('BLOCKERS.tsv')) == 10 and len(read('MODULE-PARITY.tsv')) == 18
accepted = {r['module_id']: r for r in state['modules'] if r['accepted']}
assert len(accepted) == 8
for mid,row in accepted.items():
    assert row['metadata_exceptions'] == ['20-byte GNU build ID only']
    results = [json.loads((P/p).read_text())[row['filename'].removesuffix('.ko')] for p in row['evidence']]
    assert len(results) == 2
    for d in results:
        assert d['stock_sha256'] == row['stock_sha256'] and d['unresolved'] == 0
        start,length = d['allowed_range']; assert length == 20
        assert all(start <= off < start + length for off in d['raw_difference_offsets'])
        assert d['raw_differing_bytes'] == len(d['raw_difference_offsets']) <= 20
    for k in ['stock_sha256','normalized_sha256','bytes','functions','data','imports','exports','kcfi_abs_ids','relocations']:
        assert results[0][k] == results[1][k], (mid,k)
    assert row['next_immediate_action']
for name in ['cmdq/mutations-B2.json','thermal/thermal-mutations-B2.json']:
    d=json.loads((P/'evidence'/name).read_text());assert d['all_detected']
    assert all(c['result']=='OK' for c in d['cases'])
for tag in ['B1','B2']:
    log=(P/'evidence/connectivity'/tag/'mutation-test.log').read_text().splitlines()
    d=json.loads(log[-1]);assert d == {'mutations':44,'all_detected':True}
for family in ['cmdq','connectivity','thermal']:
    d=json.loads((P/'evidence'/family/'build-input-comparison.json').read_text())
    assert d['objects_with_non_debug_difference'] == []
    assert all(c['identical'] for c in d['configurations'])
    assert all(v['strip_debug_identical'] for v in d.get('native_intermediates',{}).values())
validation=json.loads((P/'evidence/inventory-validation.json').read_text())
assert validation['distinct_stock_identities']==458 and validation['stock_occurrences']==471 and not validation['errors']
base = state['canonical_baseline_commit']
aud = 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'
assert (R/aud).read_bytes() == subprocess.check_output(['git','show',f'{base}:{aud}'],cwd=R)
canonical={r['module_id']:r for r in csv.DictReader((R/aud).open(),delimiter='\t')}
delta=read('AUDIT-DELTA.tsv');keys=set()
for r in delta:
    key=(r['module_id'],r['field']);assert key not in keys;keys.add(key)
    assert r['module_id'] in accepted and r['baseline_commit']==base
    assert r['expected_old_value']==canonical[r['module_id']][r['field']],key
    assert not r['field'].startswith('stock_') and r['field'] not in ['partitions','component_owner','runtime_status']
assert {r['module_id'] for r in delta} == set(accepted)
assert all(r['new_value']=='A' for r in delta if r['field']=='source_status')
for b in json.loads((P/'evidence/bundle-verification.json').read_text()):
    path=P/b['path']; assert hashlib.sha256(path.read_bytes()).hexdigest()==b['sha256']
    assert b['verify_exit']==0
    heads=subprocess.check_output(['git','bundle','list-heads',str(path)],text=True,cwd=R)
    assert b['final_commit'] in heads
legacy=json.loads((P/'evidence/legacy-source-search/zte-tkcore-manifest.json').read_text())
assert legacy['commit']=='b0c0f1ec4cb6d616090e7879a7df0785a1323c5d' and len(legacy['files'])==52
for f in legacy['files']:
    relative=f['path'].removeprefix('drivers/misc/mediatek/tkcore/')
    data=(P/'evidence/legacy-source-search/zte-tkcore'/relative).read_bytes()
    assert hashlib.sha256(data).hexdigest()==f['sha256']
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==f['git_blob']
layout=json.loads((P/'evidence/legacy-source-search/public-layout-result.json').read_text())
assert layout['compile_exit']==0 and layout['values']['tee.size']==0x158 and layout['values']['tee_context.size']==0xc8
print('VALID checkpoint: 18 immutable targets, 8 independently accepted A, 10 explicit C; no canonical audit edits; strict GNU20 only; 52 legacy candidate source blobs verified')
