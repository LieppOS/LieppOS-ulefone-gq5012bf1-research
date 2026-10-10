#!/usr/bin/env python3
"""Derive AUDIO-BATCH-01 machine-readable results from preserved clean-check evidence.

Inputs (all committed): BATCH-MANIFEST.tsv, evidence/cleancheck/acceptance-B{1,2}/*.json,
evidence/cleancheck/B1-B2-compare.log, evidence/baseline/selected-original-rows.json.
Outputs: BATCH-PARITY.tsv, AUDIT-DELTA.tsv, SOURCE-REPOSITORIES.tsv, BLOCKERS.tsv, BATCH-STATE.json.
Never writes the live canonical audit.
"""
import csv, json, hashlib, collections
from pathlib import Path

P = Path(__file__).resolve().parents[1]
E = P / 'evidence/cleancheck'
REPO = 'android_kernel_modules_audio_ulefone_gq5012bf1'
SRC_COMMIT = 'ec57573ca9f48c92b8485137064840025525f23f'
man = list(csv.DictReader((P / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
acc = {t: json.loads((E / f'acceptance-{t}/acceptance.json').read_text()) for t in ('B1', 'B2')}
res = {t: json.loads((E / f'acceptance-{t}/class-c-residuals.json').read_text()) for t in ('B1', 'B2')}
cmp = (E / 'B1-B2-compare.log').read_text()
assert cmp.count('IDENTICAL') == 5 and acc['B1'] == acc['B2'] and res['B1'] == res['B2']
mut = (E / 'acceptance-B1/mutation-test.log').read_text().strip().splitlines()[-1]
assert json.loads(mut) == {'mutations': 24, 'all_detected': True}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PATCH = {'mt6878-mt6369': '0002', 'mtk-sp-spk-amp': '0003', 'mt6369-accdet': '0004', 'aw883xx_driver': '0005+0006'}

par, delta, block = [], [], []
for r in man:
    m = r['filename'][:-3]
    if m in acc['B1']:
        a = acc['B1'][m]
        assert a['unresolved'] == 0 and a['normalized_sha256'] and set(a['raw_difference_offsets']) <= set(range(a['allowed_range'][0], a['allowed_range'][0] + 20))
        final = 'A'
        row = dict(functions=f"{a['functions']}/{r['stock_functions']} byte-identical", data=f"{a['data']} objects byte-identical",
                   crc_kcfi=f"imports {a['imports']} CRC identical; exports {a['exports']} CRC+licence identical; KCFI type ids {a['kcfi_abs_ids']} identical",
                   relocations=f"{a['relocations']} raw+semantic identical",
                   elf=f"whole file identical except GNU build-ID descriptor ({a['raw_differing_bytes']} of 20 bytes differ); sections/symtab/modinfo/vermagic/srcversion identical",
                   residual='none (build-ID normalization only)')
    else:
        c = res['B1'][m]
        final = 'C'
        row = dict(functions=f"{c['byte_identical_functions']}/{c['functions']} byte-identical; differs: {','.join(c['differing_functions'])} (stock {c['stock_function_sizes']} vs build {c['build_function_sizes']} bytes)",
                   data=f"{c['data_objects']} objects identical (values/bytes)",
                   crc_kcfi=f"imports {c['imports']} CRC identical; exports {c['exports']} identical; KCFI ids identical",
                   relocations='identical outside aw883xx_dev_cfg_load; address-dependent addends shift by text size delta',
                   elf=f"modinfo/vermagic identical; address-dependent sections differ: {';'.join(c['differing_sections'])}",
                   residual='inlined v1.7.1 scene-parser codegen (insertion-sort loop shape) not reproduced; stock semantics restored')
        block.append(dict(module=r['filename'], final_class='C', blocker='aw883xx_dev_cfg_load byte identity (inlined aw_dev_parse_scene_v_1_0_0_0)',
                          evidence='evidence/aw883xx-scene-parser/ (18 falsified variants, stock disassembly, harness)',
                          unmatched='1 function: 3560 B stock vs 3496 B build; 248/892 normalized instructions differ',
                          crc_kcfi_btf='none: imports/exports/CRCs/KCFI identical; no BTF section in stock module',
                          candidates='private Awinic v1.7.1 source (not public); loop/temporary structure of scene parser',
                          next_experiment='Recover stock block order of pass-1 (empty-list fast path + j==32 and (u32)j==32 dual bounds traps) by testing helper-function extraction of the insertion sort and int8/uint16 profile temporaries; accept only byte-identical result',
                          continue_policy='independent; does not block any other module'))
    par.append(dict(module=r['filename'], family=r['dependency_group'], initial_class=r['initial_class'], final_class=final,
                    stock_sha256=r['stock_sha256'], **row, source_repository=REPO, source_commit=SRC_COMMIT,
                    source_patches=PATCH.get(m, 'none (pristine ALPS 5e415e05)'), b1_b2='identical raw .ko + stripped + all .o',
                    evidence=f"evidence/cleancheck/acceptance-B1/{'acceptance' if final == 'A' else 'class-c-residuals'}.json"))
    delta.append(dict(module_id=r['module_id'], filename=r['filename'], baseline_commit='548526fc711cf9943a20d2daad42158ee1543842',
                      old_source_status=r['initial_class'], new_source_status=final, old_source_group=r['initial_source_group'],
                      new_source_group='AUDIO-BATCH-01:' + r['dependency_group'], new_source_owner=REPO + '@' + SRC_COMMIT,
                      new_parity_evidence='reverse-engineering/kernel-source-reconstruction/AUDIO-BATCH-01/' + par[-1]['evidence'],
                      new_build_script=REPO + '/scripts/bulk-build.sh', new_reproduction='INDEPENDENT_CLEAN_CLONE_B1_B2_IDENTICAL_STOCK_ACCEPTED' if final == 'A' else 'INDEPENDENT_CLEAN_CLONE_B1_B2_IDENTICAL_RESIDUAL_DOCUMENTED',
                      verified_A_B='yes' if final == 'A' else 'no'))

def write(name, rows):
    with (P / name).open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)
write('BATCH-PARITY.tsv', par); write('AUDIT-DELTA.tsv', delta); write('BLOCKERS.tsv', block)
write('SOURCE-REPOSITORIES.tsv', [dict(repository=REPO, path='../' + REPO, commit=SRC_COMMIT,
      bundle='/home/armol/kernel-work/codex-audio-batch-01/bundle/audio-' + SRC_COMMIT + '.bundle',
      bundle_sha256=(E / 'bundle.sha256').read_text().split()[0], families='AFE-ASOC;CODEC-AMP;DSP-HOST', modules=len(man),
      source_tree=(E / 'B1-TARGET-SOURCE-TREE').read_text().strip(), pins='common 6b18f0b5; clang 7775eb11 r487747c; kdm 957dac18; alps5e41 5e415e05; aw883xx 4f52a107',
      pushed='no')])
cnt = collections.Counter(p['final_class'] for p in par)
baseline = {'A': 219, 'B': 1, 'C': 9, 'D': 98, 'G': 131}
proj = dict(baseline); proj['G'] -= len(man); proj['A'] += cnt['A']; proj['C'] += cnt['C']
state = json.loads((P / 'BATCH-STATE.json').read_text())
state.update(phase='COMPLETE_20A_1C_INDEPENDENTLY_VERIFIED_DELTA_NOT_MERGED',
             completed_modules=sorted(p['module'][:-3] for p in par), in_progress_modules=[],
             blocked_modules={b['module'][:-3]: b['blocker'] for b in block},
             source_commits={REPO: SRC_COMMIT},
             build_results={'development_D2': '21/21 built; 20 whole-file accepted; aw883xx residual-only',
                            'cleancheck': 'bwrap-isolated fresh clone, independent B1/B2 workspaces: raw .ko, stripped, 220 .o, witnesses, config, symvers identical',
                            'provider_boundaries': '39/39 stock external export slots reproduced by genuine ALPS provider source (14 providers, uncertified here)'},
             latest_tests={'verify.py': '20 PASS (B1 and B2)', 'residual-check.py': 'aw883xx_driver RESIDUAL-ONLY', 'mutation-test.py': mut, 'clean_clone': 'PASS ' + SRC_COMMIT},
             final_classes=dict(cnt), projected_canonical_counts_provisional=proj,
             projected_certified_provisional=proj['A'] + proj['B'], projected_uncertified_provisional=458 - proj['A'] - proj['B'],
             next_exact_action='Wait for Claude PLATFORM-BATCH-04; then follow MERGE-INSTRUCTIONS.md to revalidate AUDIT-DELTA.tsv against the then-current canonical audit',
             latest_parity_result='20 A + 1 C')
(P / 'BATCH-STATE.json').write_text(json.dumps(state, indent=2) + '\n')
print('classes', dict(cnt), 'projected', proj, 'certified', proj['A'] + proj['B'])
