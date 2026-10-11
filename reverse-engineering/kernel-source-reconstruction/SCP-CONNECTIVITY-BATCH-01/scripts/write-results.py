#!/usr/bin/env python3
"""Derive SCP-CONNECTIVITY-BATCH-01 machine-readable results from preserved clean-check evidence.

Inputs (all committed): BATCH-MANIFEST.tsv, evidence/{scp-sensorhub,connectivity}/cleancheck/**.
Outputs: BATCH-PARITY.tsv, AUDIT-DELTA.tsv, SOURCE-REPOSITORIES.tsv, BLOCKERS.tsv,
PROVIDER-BOUNDARIES.tsv, BATCH-STATE.json. Never writes the live canonical audit.
"""
import csv, json, collections
from pathlib import Path

P = Path(__file__).resolve().parents[1]
BASELINE = '548526fc711cf9943a20d2daad42158ee1543842'
FAM = {
    'SCP-SENSORHUB': dict(key='scp-sensorhub', repo='android_kernel_modules_scp_sensorhub_ulefone_gq5012bf1',
                          commit='26507aa653a09f907329795b6c31c6ec1bd694dd', mutations=23,
                          pins='common 6b18f0b5; clang 7775eb11 r487747c; kdm 957dac18 (Kconfig); alps5e41 5e415e05'),
    'CONN': dict(key='connectivity', repo='android_kernel_modules_connectivity_ulefone_gq5012bf1',
                 commit='d0b9e10fbb3bb4810de79fda190a4216cec65b00', mutations=29,
                 pins='common 6b18f0b5; clang 7775eb11 r487747c; kdm 957dac18 (Kconfig); alps5e41 5e415e05; nkm 2115d278 (connectivity d7cfca48); kernel-build-tools e905be25 (pahole 1.23); public GKI 12901745 vmlinux 27abab46'),
}
fam_of = lambda g: 'SCP-SENSORHUB' if g == 'SCP-SENSORHUB' else 'CONN'
PATCH = {'hf_manager': 'scp-sensorhub patches/0002 (YFT devinfo hooks, sensor-type enum)',
         'sensorhub': 'scp-sensorhub patches/0002 (display-blank notifier)',
         'wlan_drv_gen4m_6878': 'connectivity patches/nkm/0003 (13 recovered ALPS V11.24 hunks)',
         'uarthub_drv': 'pristine ALPS; Kbuild path spelling patches/kdm/0009'}
man = list(csv.DictReader((P / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
ev, acc, res = {}, {}, {}
for f, v in FAM.items():
    E = P / 'evidence' / v['key'] / 'cleancheck'; ev[f] = E
    a = {t: json.loads((E / f'acceptance-{t}/acceptance.json').read_text()) for t in ('B1', 'B2')}
    assert a['B1'] == a['B2']; acc[f] = a['B1']
    rp = {t: E / f'acceptance-{t}/class-c-residuals.json' for t in ('B1', 'B2')}
    res[f] = json.loads(rp['B1'].read_text()) if rp['B1'].exists() else {}
    if rp['B1'].exists(): assert rp['B1'].read_text() == rp['B2'].read_text()
    log = (E / 'run.log').read_text(); assert 'CLEANCHECK PASS ' + v['commit'] in log and (E / 'B1-B2-compare.log').read_text().count('IDENTICAL') == 5
    mut = json.loads((E / 'acceptance-B1/mutation-test.log').read_text().strip().splitlines()[-1])
    assert mut == {'mutations': v['mutations'], 'all_detected': True}, mut

par, delta, block = [], [], []
for r in man:
    m = r['filename'][:-3]; f = fam_of(r['dependency_group']); v = FAM[f]
    rel = f"evidence/{v['key']}/cleancheck/acceptance-B1/"
    if m in acc[f]:
        a = acc[f][m]
        lo = a['allowed_range'][0]
        assert a['unresolved'] == 0 and set(a['raw_difference_offsets']) <= set(range(lo, lo + 20))
        assert a['functions'] == int(r['stock_functions']) and a['imports'] == int(r['stock_imports']) and a['exports'] == int(r['stock_exports'])
        final = 'A'
        row = dict(functions=f"{a['functions']}/{r['stock_functions']} byte-identical", data=f"{a['data']} objects byte-identical",
                   crc_kcfi=f"imports {a['imports']} CRC identical; exports {a['exports']} CRC+licence identical; KCFI type ids {a['kcfi_abs_ids']} identical",
                   relocations=f"{a['relocations']} raw+semantic identical",
                   btf='no .BTF in stock' if r['stock_btf'] == 'no' else 'identical',
                   elf=f"whole file identical except GNU build-ID descriptor ({a['raw_differing_bytes']} of 20 bytes differ); sections/symtab/modinfo/vermagic/srcversion identical",
                   residual='none (build-ID normalization only)', evidence=rel + 'acceptance.json')
    else:
        c = res[f][m]; final = 'C'
        assert c['non_btf_bytes_identical'] and c['id_mapping_bijective']
        row = dict(functions=f"{r['stock_functions']}/{r['stock_functions']} byte-identical", data=f"{r['stock_data_objects']} objects byte-identical",
                   crc_kcfi=f"imports {r['stock_imports']} CRC identical; exports {r['stock_exports']} CRC+licence identical; KCFI ids {r['stock_kcfi_abs_ids']} identical",
                   relocations=f"{r['stock_relocations']} raw identical (every non-.BTF section byte-identical)",
                   btf=(f".BTF {c['btf_bytes']} B: header/strings/{c['btf_records']} records/reference positions identical; {c['btf_differing_bytes']} bytes differ = "
                        f"{c['differing_reference_fields']} type-ID refs (bijective, module-local +{c['module_local_id_delta']}) + {c['differing_string_offset_fields']} name-offset refs (bijective, module-local +{c['module_local_str_delta']})"),
                   elf='every byte outside .BTF and the GNU build ID identical (incl. intree=Y, scmversion, vermagic, sections, symtab)',
                   residual='split-BTF base: stock generated against private OEM g945dff7bc1bf vmlinux (15 more types, 389 more string bytes than public GKI 12901745)',
                   evidence=rel + 'class-c-residuals.json')
        block.append(dict(module=r['filename'], final_class='C', blocker='split-BTF base lineage (OEM g945dff7bc1bf vmlinux BTF unavailable; device boots public GKI 12901745)',
                          evidence=rel + 'class-c-residuals.json; evidence/btf-residual/' + m + '.json',
                          unmatched=f".BTF only: {c['btf_differing_bytes']}/{c['btf_bytes']} bytes, all type-ID/name-offset references",
                          crc_kcfi_btf='CRC/KCFI/relocations/modinfo identical; BTF residual as stated',
                          candidates='public ACK android14-6.1 commits after 6b18f0b5 at 6.1.115 whose gki_defconfig vmlinux BTF has 130366 types and a 2300745-byte string table',
                          next_experiment='Fetch public CI vmlinux artifacts (or build vmlinux with pinned clang/pahole) for later android14-6.1 6.1.115 commits; accept a base only if it is public, verified by sha/tree, and makes .BTF byte-identical without any edit. Same experiment closes Batch03 thermal-generic-adc and 7 other vendor in-tree D modules',
                          continue_policy='independent; does not block any other module'))
    par.append(dict(module=r['filename'], family=r['dependency_group'], initial_class=r['initial_class'], final_class=final,
                    stock_sha256=r['stock_sha256'], functions=row['functions'], data=row['data'], crc_kcfi=row['crc_kcfi'],
                    relocations=row['relocations'], btf=row['btf'], elf=row['elf'], residual=row['residual'],
                    source_repository=v['repo'], source_commit=v['commit'], source_patches=PATCH.get(m, 'none (pristine pinned source)'),
                    b1_b2='identical raw .ko + stripped + all .o (bwrap-isolated clean clone)', evidence=row['evidence']))
    delta.append(dict(module_id=r['module_id'], filename=r['filename'], baseline_commit=BASELINE,
                      old_source_status=r['initial_class'], new_source_status=final, old_source_group=r['initial_source_group'],
                      new_source_group='SCP-CONNECTIVITY-BATCH-01:' + r['dependency_group'], new_source_owner=v['repo'] + '@' + v['commit'],
                      new_parity_evidence='reverse-engineering/kernel-source-reconstruction/SCP-CONNECTIVITY-BATCH-01/' + row['evidence'],
                      new_build_script=v['repo'] + '/scripts/bulk-build.sh',
                      new_reproduction='INDEPENDENT_CLEAN_CLONE_B1_B2_IDENTICAL_STOCK_ACCEPTED' if final == 'A' else 'INDEPENDENT_CLEAN_CLONE_B1_B2_IDENTICAL_RESIDUAL_DOCUMENTED',
                      verified_A_B='yes' if final == 'A' else 'no'))

def write(name, rows):
    with (P / name).open('w') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)
write('BATCH-PARITY.tsv', par); write('AUDIT-DELTA.tsv', delta); write('BLOCKERS.tsv', block)
repos = []
for f, v in FAM.items():
    E = ev[f]; b = next(E.glob('*.bundle.sha256')).read_text().split()
    repos.append(dict(repository=v['repo'], path='../' + v['repo'], commit=v['commit'], bundle=b[1], bundle_sha256=b[0],
                      families=';'.join(sorted({r['dependency_group'] for r in man if fam_of(r['dependency_group']) == f})),
                      modules=sum(1 for r in man if fam_of(r['dependency_group']) == f),
                      source_trees=' '.join((E.parent.parent.parent / 'evidence' / v['key'] / 'cleancheck' / 'B1-B2-compare.log').read_text().split('== source tree\n')[1].split()[:2]),
                      pins=v['pins'], pushed='no'))
write('SOURCE-REPOSITORIES.tsv', repos)
# Provider ABI ledger: every external slot of both recipes with its genuine witness or declared class.
pb = []
for f, v in FAM.items():
    w = json.loads((ev[f] / 'acceptance-B1/provider-witnesses.json').read_text())
    sp = ev[f] / 'acceptance-B1/stock-provider-exports.json'
    stock = json.loads(sp.read_text()) if sp.exists() else {}
    for s, lst in sorted(w.items()):
        x = lst[0]
        pb.append(dict(recipe=v['repo'], symbol=s, provider_module=x['module'], crc=x['crc'], licence=x['licence'], namespace=x['namespace'] or '',
                       stock_kcfi_prefix_word=x['stock_kcfi_prefix_word'] or '', source_kcfi_prefix_word=x['source_kcfi_prefix_word'] or '',
                       witness_class='SOURCE_WITNESS', source_revision=x['source_revision'], source_unit=x['object'],
                       result='MATCH' if not any(y['errors'] for y in lst) else 'FAIL', provider_classification_changed='no'))
    for s, x in sorted(stock.items()):
        pb.append(dict(recipe=v['repo'], symbol=s, provider_module=x['provider_module'], crc=x['crc'], licence=x['licence'], namespace=x['namespace'],
                       stock_kcfi_prefix_word=x['stock_kcfi_prefix_word'] or '', source_kcfi_prefix_word='',
                       witness_class='STOCK_PROVIDER_EXPORT', source_revision='none public (ODM-private provider)', source_unit='stock provider __kcrctab',
                       result='DECLARED', provider_classification_changed='no'))
write('PROVIDER-BOUNDARIES.tsv', pb)
cnt = collections.Counter(p['final_class'] for p in par)
baseline = {'A': 219, 'B': 1, 'C': 9, 'D': 98, 'G': 131}
proj = dict(baseline); proj['G'] -= len(man); proj['A'] += cnt['A']; proj['C'] += cnt['C']
state = json.loads((P / 'BATCH-STATE.json').read_text())
state.update(phase='COMPLETE_17A_3C_INDEPENDENTLY_VERIFIED_DELTA_NOT_MERGED',
             completed_modules=sorted(p['module'][:-3] for p in par), in_progress_modules=[],
             blocked_modules={b['module'][:-3]: b['blocker'] for b in block},
             source_commits={v['repo']: v['commit'] for v in FAM.values()},
             build_results={'SCP-SENSORHUB': '3/3 whole-file accepted; CLEANCHECK PASS; 28 boundaries (18 source witness, 10 STOCK_PROVIDER_EXPORT yft_devinfo)',
                            'CONNECTIVITY': '17/17 built; 14 whole-file accepted; 3 C .BTF-only residual; CLEANCHECK PASS; 29/29 boundaries source-witnessed'},
             latest_tests={'verify.py': '17 A PASS (B1 and B2)', 'residual-btf.py': 'cfg80211/mac80211/bluetooth RESIDUAL-ONLY-BTF',
                           'mutation-test.py': 'scp-sensorhub 23/23, connectivity 29/29 (incl. 6 class-C gate cases)',
                           'clean_clone': {v['repo']: 'PASS ' + v['commit'] for v in FAM.values()}},
             final_classes=dict(cnt), projected_canonical_counts_provisional=proj,
             projected_certified_provisional=proj['A'] + proj['B'], projected_uncertified_provisional=458 - proj['A'] - proj['B'],
             projection_basis='frozen baseline 548526fc only; excludes unmerged AUDIO-BATCH-01 (+20 A +1 C) and in-progress PLATFORM-BATCH-04',
             next_exact_action='Wait for Claude PLATFORM-BATCH-04 and the AUDIO-BATCH-01 merge; then follow MERGE-INSTRUCTIONS.md',
             latest_parity_result=f"{cnt['A']} A + {cnt['C']} C",
             resume='Complete. Optional: BTF-base experiment in BLOCKERS.tsv.')
(P / 'BATCH-STATE.json').write_text(json.dumps(state, indent=2) + '\n')
print('classes', dict(cnt), 'projected', proj, 'certified', proj['A'] + proj['B'], 'provider rows', len(pb), collections.Counter(x['result'] for x in pb))
