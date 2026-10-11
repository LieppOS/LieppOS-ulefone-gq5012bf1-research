#!/usr/bin/env python3
"""Generate the closure checkpoint/delta from frozen identities and preserved evidence.
Does not change the frozen manifest, canonical audit, source repos, or stock operands.
"""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
BASE = 'f61ebf03275ba2d3f6aa4f9d5aebe18e12922263'
rows = list(csv.DictReader((P/'C-CLOSURE-MANIFEST.tsv').open(), delimiter='\t'))
assert len(rows) == 18
canonical = {r['module_id']: r for r in csv.DictReader(
    (R/'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').open(), delimiter='\t')}
families = {
 'CMDQ': ('cmdq', 'cmdq', '059e2fe439309c3adc2e95b87aa547967e7e5f80',
          '0b4b07f38397ca6c0630b9edc5ccf2df9251da1d'),
 'BTF-CONNECTIVITY': ('connectivity', 'connectivity', '40bf42967a213af6faa45a6a579571973b8e5d15',
          '40bf42967a213af6faa45a6a579571973b8e5d15'),
 'BTF-THERMAL': ('thermal_cooling', 'thermal', '9e0e1a0df474f1e5a748d0302fba8445f13c996d',
          'ff6e97b3bf1f29c1e1fba4ba0c0e28493cbd0698')}
next_actions = {
 'USB': 'Recover authentic OEM token inputs; retain latest 709/709 TCPC source; no srcversion or counter override.',
 'AUDIO': 'Test a helper-extracted insertion sort with independent j/k widths and stock dual bounds-check shape; current variants are unaccepted.',
 'focaltech_touch_spi_ft3680.ko': 'Recover an authentic FT3680 SPI OEM driver revision; compare all 40 size-different functions and YFT dependencies.',
 'yft_devinfo.ko': 'Recover ODM enum tag/type declarations from authentic consumer/source release; retain CRC/KCFI and sysfs/probe blockers.',
 'st21nfc.ko': 'Find original OEM/ST revision beyond the scanned public blobs; close ioctl/ping and natural srcversion, then preserve a full clean recipe.',
 'tkcore.ko': 'Recover original TrustKernel private declarations/member names for the 14 private-type consumer CRC edges; do not patch CRCs.'}
state, parity, delta = [], [], []
for r in rows:
    name = r['filename']; m = name.removesuffix('.ko')
    fam = 'CMDQ' if r['group']=='CMDQ' else ('BTF-THERMAL' if name=='thermal-generic-adc.ko' else
          'BTF-CONNECTIVITY' if name in ['cfg80211.ko','mac80211.ko','bluetooth.ko'] else None)
    item = dict(r, final_class='C', accepted=False, source_commit=r['maintained_source_commit'],
                current_experiment='Bounded experiments complete; genuine residual retained',
                exact_parity=r['current_exact_residual'], evidence=[],
                next_immediate_action=next_actions.get(name,next_actions.get(r['group'],r['proposed_next_experiment'])))
    evidence = ''; pair = 'Inherited only; no new accepted B1/B2'
    if fam:
        source, directory, tested, final = families[fam]
        rel = f'../android_kernel_modules_{source}_ulefone_gq5012bf1-allc'
        def load(tag):
            path = P/'evidence'/directory/tag
            if fam == 'CMDQ': path = path/m
            return json.loads((path/'acceptance.json').read_text())[m]
        a,b = load('B1'),load('B2')
        for k in ['stock_sha256','normalized_sha256','functions','data','imports','exports','kcfi_abs_ids','relocations','unresolved']:
            assert a[k] == b[k], (m,k)
        assert a['stock_sha256'] == r['stock_sha256'] and a['unresolved'] == 0
        evidence = f'evidence/{directory}/B1/{m+"/" if fam=="CMDQ" else ""}acceptance.json;evidence/{directory}/B2/{m+"/" if fam=="CMDQ" else ""}acceptance.json'
        item.update(final_class='A', accepted=True, source_commit=final, tested_source_commit=tested,
                    maintained_source_repo=rel, current_experiment='Independent B1/B2 whole-stock acceptance PASS',
                    exact_parity=a, evidence=evidence.split(';'), metadata_exceptions=['20-byte GNU build ID only'],
                    next_immediate_action='Owner-reviewed field-level integration; no runtime or flash claim.')
        pair = 'PASS independent B1/B2; GNU20-normalized identity'
        updates = dict(source_status='A', source_commit=final, source_repo=rel,
            source_pin=rel+'/SOURCE-PINS.tsv', source_snapshot_path=rel+'/patches',
            source_group='ALL-C-TO-A-CLOSURE:'+fam, source_owner='ALL-C-TO-A-CLOSURE:'+fam,
            build_script=rel+'/scripts/bulk-build.sh', reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',
            parity_evidence=';'.join('reverse-engineering/kernel-source-reconstruction/ALL-C-TO-A-CLOSURE/'+p for p in evidence.split(';')),
            verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',
            abi_status='VERIFIED', crc_status='VERIFIED', kcfi_status='VERIFIED',
            exact_functions=str(a['functions']), unresolved_functions='0',
            blocker='NONE (static source parity only; runtime and secure/firmware behavior not validated)',
            preservation_risk='LOW: maintained public pins, independent B1/B2, strict full-ELF evidence, verified recovery bundle')
        for field,value in updates.items():
            old = canonical[r['module_id']][field]
            if old != value:
                delta.append(dict(module_id=r['module_id'], filename=name, baseline_commit=BASE,
                    field=field, expected_old_value=old, new_value=value,
                    projected_previous_class='C', supporting_evidence=evidence))
    else:
        if r['group']=='USB':
            item['evidence']=['evidence/srcversion/history-scan.json','evidence/srcversion/history-scan-micode.json']
            item['current_experiment']='No stock srcversion hits for four scanned modules; tcpc_class retains inherited traced source-provenance blocker.'
        elif r['group']=='AUDIO':
            item.update(current_experiment='90 type-grid candidates plus targeted structural variants: no acceptance',
                        evidence=['evidence/aw883xx/grid.log','evidence/aw883xx/grid2.log','evidence/aw883xx/grid3.log'],
                        diagnostic_best='255 diff lines; whole stripped file size 331808 equals stock; neither metric proves equivalence',
                        exact_parity='235/236 raw functions exact; aw883xx_dev_cfg_load 3560 B stock vs 3564 B best experimental build; complete ELF remains unaccepted')
        elif name=='st21nfc.ko':
            item.update(current_experiment='Historical object baseline reproduced 24/24; 28 authentic blob pairs tested (4 compile, 24 incompatible I2C probe API); no ioctl/ping hits.',
                        evidence=['evidence/st21nfc/public-history-object-scan.json','evidence/st21nfc/historic-baseline-vs-preserved-object.txt'])
        elif name=='tkcore.ko':
            item.update(current_experiment='ZTE3.2p3 layout rejects drop-in;two pinned Vivo3.2p8 trees retain all10 old struct blocks;UMIDIGI/kernel/vendor scopes yield no matching newer header;eight stock provider/consumer occurrences have no BTF/debug sections.',
                        evidence=['evidence/legacy-source-search/zte-tkcore-manifest.json','evidence/legacy-source-search/public-layout-result.json',
                                  'evidence/legacy-source-search/newer-provider-search/candidate-comparisons.json',
                                  'evidence/legacy-source-search/newer-provider-search/struct-block-comparison.json',
                                  'evidence/legacy-source-search/newer-provider-search/stock-type-info-scope.json'],
                        next_immediate_action='Find the authentic newer 6:1.1-k6.6 source lineage carrying version/log/list-of-misc-device and extra context fields; use the recovered public headers as constraints, not a stock-compatible replacement.')
        evidence = ';'.join(item['evidence'])
    state.append(item)
    parity.append(dict(module_id=r['module_id'],filename=name,initial_class=r['initial_class'],
        remaining_issue='GNU build-ID only (allowed)' if item['accepted'] else item['exact_parity'],
        source_fix='Microtrust visibility/config correction' if fam=='CMDQ' else 'Public-source OEM split-BTF base' if fam else item['current_experiment'],
        B1_B2=pair,whole_stock_acceptance='PASS' if item['accepted'] else 'NOT ACCEPTED',
        final_class=item['final_class'],source_commit=item['source_commit'],evidence=evidence))

def tsv(name,data):
    with (P/name).open('w',newline='') as f:
        w=csv.DictWriter(f, list(data[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(data)

tsv('MODULE-PARITY.tsv',parity)
tsv('AUDIT-DELTA.tsv',delta)
tsv('BLOCKERS.tsv',[dict(module_id=i['module_id'],filename=i['filename'],final_class='C',
    exact_remaining_issue=i['exact_parity'],last_experiment=i['current_experiment'],
    next_experiment=i['next_immediate_action']) for i in state if not i['accepted']])
(P/'C-CLOSURE-STATE.json').write_text(json.dumps(dict(
    objective_complete=False, frozen_manifest_sha256=hashlib.sha256((P/'C-CLOSURE-MANIFEST.tsv').read_bytes()).hexdigest(),
    canonical_baseline_commit=BASE, canonical_audit_unchanged=True, count=dict(targets=18,accepted_A=8,accepted_B=0,remaining_C=10),
    projected_counts_after_pending_audio_connectivity_and_this_delta=dict(A=289,B=1,C=10,D=91,E=0,F=0,G=67),
    exclusions=['No canonical integration','No phone/device operations','No firmware or trusted-world reconstruction','No pushes'],
    next_checkpoint='Finish legacy OEM/source retrieval and a new constrained AW883XX/helper or TCPC-token experiment; do not repeat completed grids.',
    modules=state),indent=2)+'\n')
summary = '''# Category-C closure checkpoint — 8 accepted, 10 unresolved

**The 18/18 mission is not complete.** All 18 frozen identities are tracked; eight have
independent strict Category-A evidence, none are relabeled B, and ten retain C blockers.
No canonical audit, phone, stock image, firmware/calibration, runtime module, secure world,
or remote Git repository was modified. This is an isolated local research checkpoint.

## All selected identities

“Initial C (pending)” refers to a canonical G row that becomes C under its pending family
delta; it is not claimed to have already been canonically integrated.

| Module | Initial | Exact remaining issue | Source reconstruction/fix | B1/B2 | Whole stock | Final |
|---|---|---|---|---|---|---|
'''
for row in parity:
    initial = 'C' if row['initial_class']=='C' else 'C (pending)'
    summary += '| ' + ' | '.join([row['filename'],initial,row['remaining_issue'],row['source_fix'],
                                  row['B1_B2'],row['whole_stock_acceptance'],row['final_class']]) + ' |\n'
summary += '''
## Resolved root causes

1. Four CMDQ modules: Microtrust header visibility from a generic vendor configuration
   contaminated recursive genksyms type graphs. The recovered board config removes it;
   Trustonic stays enabled for genuine provider source. Natural CRC/counter metadata match.
2. Four BTF modules: public GKI base was the wrong split-BTF lineage. Pinned NothingOSS MTK
   ACK, vendor configuration, Kleaf flags, OEM release-string length and pahole reproduce
   exact base BTF. No BTF copying, rewriting or extra normalization.

Source changes and exact tested/final commits: SOURCE-CHANGES.tsv and SOURCE-PINS.tsv.
Fresh-clone/source/bundle and intermediate comparisons: BUILD-REPRODUCTION.md.
Raw/semantic function/data/ABI/section/relocation evidence: evidence/ family ledgers.

## Checks

- CMDQ 35/35 joint B1/B2 accepts, 40/40 mutation checks; 120 debug-stripped objects exact.
- Connectivity 17/17 B1/B2 accepts, 44/44 mutation checks; 577 raw objects exact.
- Thermal 34/34 B1/B2 accepts, 11/11 mutation checks; 130 debug-stripped vendor objects
  and separately checked native intermediates; BTF identical, not complete base vmlinux.
- All compared configs and natural symvers match (text workspace-path normalization only).
- Recovery bundles verified; documentation-only post-build commits distinguished explicitly.
- Unchanged isolated inventory validator: 458 identities / 471 occurrences, zero errors;
  its 14 mutation/regression checks pass. evidence/inventory-validation.json records the
  canonical baseline counts, not a silently promoted audit.

## Unresolved findings and next actions

Public NothingOSS/MiCode searches found no stock fingerprints in 1100 + 4443 four-module
USB candidate combinations. This is a bounded history/one-file-variation search, not all
possible OEM source or a full multi-input Cartesian product. TCPC's 709/709 code and 54
recovered timers remain intact; srcversion/counter/source composition remain blockers.
AW883XX's diagnostic best still has one mismatching function (3564 vs stock3560), despite
235/236 raw matches and equal total file size. All 90 grid attempts and 97 source variants
are preserved, not certified. Historical ST21 flags reproduce its preserved object, but
neither the public blob scan nor natural fingerprint scan closes ioctl/ping/OEM tokens.
FT3680, YFT private enum/type graph and TrustKernel private CRC declarations remain open;
no new accepted source release was recovered for them. A public ZTE TKCore 3.2p3 release
was recovered at b0c0f1ec4cb6d616090e7879a7df0785a1323c5d (52 verified source blobs).
A compile-only layout probe proves it is not the newer stock 6:1.1-k6.6 declaration
lineage: tee 0x158 versus stock0x138, context0xc8 versus stock0xd0. It supplies authentic
historical constraints, not an accepted replacement. A further two pinned Vivo3.2p8
publications preserve the same10 core struct blocks (57 recovered blobs); the inspected
UMIDIGI kernel/vendor scopes supply no matching newer normal-world header. Four stock
provider/consumer identities (eight occurrences) have no BTF/debug sections to expose
member names. No redundant layout build or C promotion followed; see
LEGACY-C-RECONSTRUCTION.md and scripts/validate-legacy-search.py.

BLOCKERS.tsv has a next experiment for every remaining C. C-CLOSURE-STATE.json is the
resumption checkpoint. Continue a genuinely new authentic source/header/helper-composition
investigation; do not repeat completed grids or normalize missing OEM metadata.

## Audit status and projected counts

Canonical at f61ebf03 remains A244 B1 C14 D91 E0 F0 G108: 245 certified / 213 remaining.
With the pending audio/connectivity deltas and these eight closures, projected only:
A289 B1 C10 D91 E0 F0 G67: 290 certified / 168 remaining / 458 total.
Concurrent other-family work is excluded until reconciled. AUDIT-DELTA.tsv supplies exact
field preconditions for eight identities; it is not applied. MERGE-INSTRUCTIONS.md requires
inventory repair/validation, current-HEAD reconciliation, owner-reviewed regeneration and
unchanged validator/mutation acceptance. No stale audit replacement or push.
'''
(P/'C-CLOSURE-SUMMARY.md').write_text(summary)
print('checkpoint: 18 targets, 8 A, 10 C; no canonical audit changes; field-level delta',len(delta),'records')
