#!/usr/bin/env python3
"""Freeze exact eligible provider identities; refuse to change an existing manifest."""
from pathlib import Path
import csv, json, hashlib
P = Path(__file__).resolve().parents[1]
R = P.parents[3] / 'ulefone-gq5012bf1-research'
read = lambda f: list(csv.DictReader(f.open(), delimiter='\t'))
base = read(R / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv')
byname = {r['filename']: r for r in base}
selection = json.loads((P / 'evidence/graph-selection.json').read_text())
reachable = {r['filename'] for r in selection['eligible_reachable_uncertified']}
registered = {'ccci_ccif.ko', 'ccci_dpmaif.ko', 'ccci_fsm_scp.ko'}
selected = reachable | registered
assert len(reachable) == 19 and len(selected) == 22
pending = set()
for worktree, batch in [('ulefone-gq5012bf1-research-codex-audio', 'AUDIO-BATCH-01'),
                        ('ulefone-gq5012bf1-research-codex-connectivity', 'SCP-CONNECTIVITY-BATCH-01')]:
    pending.update(r['module_id'] for r in read(P.parents[3] / worktree / 'reverse-engineering/kernel-source-reconstruction' / batch / 'BATCH-MANIFEST.tsv'))
modem = {'ccci_auxadc.ko', 'ccci_ccif.ko', 'ccci_dpmaif.ko', 'ccci_fsm_scp.ko',
         'ccci_md_all.ko', 'ccci_util_lib.ko', 'ccmni.ko', 'rps_perf.ko', 'mtk_mdpm.ko'}
fields = ['module_id', 'filename', 'initial_class', 'source_owner', 'component_owner', 'stock_sha256',
          'stock_size', 'stock_partitions', 'stock_paths', 'selection_evidence', 'dependency',
          'candidate_source', 'donor_candidate', 'historical_source', 'expected_build_group', 'planned_repository']
rows = []
for name in sorted(selected):
    r = byname[name]
    assert r['source_status'] not in ['A', 'B', 'C'] and r['module_id'] not in pending
    if name == 'mtk_slbc.ko':
        group = 'SLBC'; repo = 'android_kernel_modules_slbc_ulefone_gq5012bf1'
    elif name in modem:
        group = 'MODEM-AUDIO-TRANSPORT'; repo = 'android_kernel_modules_modem_audio_transport_ulefone_gq5012bf1'
    else:
        group = 'TRANSITIVE-SHARED-INFRASTRUCTURE'; repo = 'android_kernel_modules_audio_shared_infrastructure_ulefone_gq5012bf1'
    donor = ('fae67a9257dc79e6a233e8781c60edf2aaf920aa' if name.startswith('ccci') else
             '6b18f0b574ab3267615ae6ce642d5a7c3c21ac09' if name == 'drm_display_helper.ko' else
             '957dac185efe46cbf6336b0fff9516d84c8cd78f' if name in modem else
             '5e415e059253ce0d2e61c97108e5f5785d71f06f')
    values = [r['module_id'], name, r['source_status'], r['source_owner'], r['component_owner'],
              r['stock_sha256'], r['stock_size'], r['partitions'], r['stock_paths'],
              'SOURCE_HIF_STATE_REGISTRATION_AND_STOCK_PORT_MAP' if name in registered else 'AUDIO_TRANSITIVE_STOCK_ABI_PROVIDER',
              r['provider_dependencies'], r['candidate_path'], donor, r['source_snapshot_path'], group, repo]
    rows.append(dict(zip(fields, values)))
import io
f = io.StringIO(); w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n');w.writeheader();w.writerows(rows)
payload = f.getvalue().encode(); out = P / 'BATCH-MANIFEST.tsv'
assert not out.exists() or out.read_bytes() == payload, 'frozen manifest differs; review rather than overwrite'
out.write_bytes(payload)
(P / 'BATCH-MANIFEST.sha256').write_text(hashlib.sha256(payload).hexdigest() + '  BATCH-MANIFEST.tsv\n')
statefile = P / 'BATCH-STATE.json'; state = json.loads(statefile.read_text())
state.update(phase='MANIFEST_FROZEN_SOURCE_RECOVERY_NEXT', selected_modules=[r['filename'] for r in rows],
             selected_count=22, manifest_sha256=hashlib.sha256(payload).hexdigest(),
             families={g:[r['filename'] for r in rows if r['expected_build_group']==g] for g in {r['expected_build_group'] for r in rows}},
             next_experiment='Recover exact modem fae67a/957dac trees and SLBC/ancillary sources; bootstrap separate source engines; compile all selected targets')
statefile.write_text(json.dumps(state, indent=2)+'\n')
print('Frozen22 eligible targets,41 pending identities and all canonical A/B/C excluded; no quota padding')
