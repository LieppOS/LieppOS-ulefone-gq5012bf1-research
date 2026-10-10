#!/usr/bin/env python3
"""Freeze AUDIO-BATCH-01 from the last stable canonical audit before any build.

Selection rule (not a hand list): every identity whose audit source_group is
PRESERVE:AUDIO or PRESERVE:AW883XX-SPEAKER-AMP. Already-certified audio-adjacent
identities (mtk-spmi-pmic, mtk-spmi-pmic-adc: A in Batch03) and Claude's
PLATFORM-BATCH-04 identities are excluded and asserted disjoint.
"""
from pathlib import Path
import csv, json, hashlib, subprocess, collections, sys

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
A = R / 'reverse-engineering/kernel-source-parity-audit'
CANON = R.parent / 'ulefone-gq5012bf1-research'  # read-only stock operands (gitignored)
BASELINE = '548526fc711cf9943a20d2daad42158ee1543842'
assert not (P / 'BATCH-MANIFEST.tsv').exists(), 'Frozen manifest is immutable'

# The audit files must be byte-identical to the last stable audit commit.
for n in ['ALL-457-MODULES.tsv', 'SOURCE-GAPS.tsv', 'SOURCE-OWNERSHIP.tsv', 'DEPENDENCY-EDGES.tsv', 'evidence/audit-summary.json']:
    want = subprocess.check_output(['git', 'show', f'{BASELINE}:reverse-engineering/kernel-source-parity-audit/{n}'], cwd=R)
    assert (A / n).read_bytes() == want, f'audit drift from baseline: {n}'

allr = list(csv.DictReader((A / 'ALL-457-MODULES.tsv').open(), delimiter='\t'))
summ = json.loads((A / 'evidence/audit-summary.json').read_text())
assert len(allr) == 458 and summ['verified_A_B'] == 220
assert collections.Counter(r['source_status'] for r in allr) == dict(A=219, B=1, C=9, D=98, G=131)

selected = [r for r in allr if r['source_group'] in ('PRESERVE:AUDIO', 'PRESERVE:AW883XX-SPEAKER-AMP')]
assert len(selected) == 21 and len({r['filename'] for r in selected}) == 21
b4 = {r['module_id'] for r in csv.DictReader((R / 'reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-04/BATCH-MANIFEST.tsv').open(), delimiter='\t')}
assert not b4 & {r['module_id'] for r in selected}, 'overlap with Claude PLATFORM-BATCH-04'

FAM = {
    'AFE-ASOC': 'snd-soc-mtk-common snd-soc-mt6878-afe mt6878-mt6369 mtk-afe-external mtk-sp-spk-amp clk-mt6878-adsp mt6685-audclk'.split(),
    'CODEC-AMP': 'snd-soc-mt6369 mt6369-accdet mt6369-regulator snd-soc-tfa98xx aw883xx_driver'.split(),
    'DSP-HOST': 'adsp audio_ipi snd-soc-audiodsp-common mtk-soc-offload-common mtk-scp-audiocommon mtk-scp-vow mtk-vow snd-soc-mtk-scp-ultra mtk-scp-ultra'.split(),
}
fam = {m + '.ko': f for f, ms in FAM.items() for m in ms}
assert set(fam) == {r['filename'] for r in selected}
DIRS = {
    'snd-soc-mtk-common': 'sound/soc/mediatek/common', 'mtk-afe-external': 'sound/soc/mediatek/common', 'mtk-sp-spk-amp': 'sound/soc/mediatek/common',
    'snd-soc-mt6878-afe': 'sound/soc/mediatek/mt6878', 'mt6878-mt6369': 'sound/soc/mediatek/mt6878',
    'clk-mt6878-adsp': 'drivers/clk/mediatek', 'mt6685-audclk': 'drivers/mfd', 'mt6369-regulator': 'drivers/regulator',
    'snd-soc-mt6369': 'sound/soc/codecs', 'mt6369-accdet': 'sound/soc/codecs', 'snd-soc-tfa98xx': 'sound/soc/codecs/tfa98xx',
    'aw883xx_driver': 'sound/soc/codecs/aw883xx',
    'adsp': 'drivers/misc/mediatek/adsp', 'audio_ipi': 'drivers/misc/mediatek/audio_ipi', 'mtk-vow': 'drivers/misc/mediatek/vow/ver02',
    'snd-soc-audiodsp-common': 'sound/soc/mediatek/audio_dsp', 'mtk-soc-offload-common': 'sound/soc/mediatek/audio_dsp',
    'mtk-scp-audiocommon': 'sound/soc/mediatek/audio_scp', 'mtk-scp-vow': 'sound/soc/mediatek/vow',
    'snd-soc-mtk-scp-ultra': 'sound/soc/mediatek/ultrasound/ultra_scp', 'mtk-scp-ultra': 'sound/soc/mediatek/ultrasound/ultra_common',
}
HIST = {  # genuine historical source, recovered rather than discarded
    'mt6878-mt6369': 'reverse-engineering/audio/afe/source/mt6878/mt6878-mt6369.c (AW883XX/AW882XX speaker types; RT5512-only throttle helper guarded)',
    'mtk-sp-spk-amp': 'reverse-engineering/audio/afe/source/mtk-sp-spk-amp.[ch] (MTK_SPK_AW_AW883XX dispatch to aw883xx_i2c_probe/remove)',
    'mt6369-accdet': 'reverse-engineering/audio/mt6369/source/mt6369-accdet.c (YFT FM-switch GPIO, forced EINT0 HIRENB comment, HL5280 wrapper)',
    'aw883xx_driver': '../Reverse Engineer - DONE/AW883XX-SPEAKER-AMP/source + patches/phase4-aw883xx-donor-to-recon.diff (v1.7.1 reconstruction, 235/236 byte-exact)',
}
EXPECT = {
    'aw883xx_driver': 'Close historical aw883xx_dev_cfg_load register-allocation residual or prove semantic equivalence; full ELF acceptance',
    'mtk-vow': 'Stock user config (MTK_TINYSYS_SCP_DEBUG_SUPPORT off) must be source-recorded; full ELF acceptance',
    'mt6369-accdet': 'Historical YFT delta re-applied as full source patch; HL5280 off; full ELF acceptance',
    'mt6878-mt6369': 'Historical delta + RT5512 off; full ELF acceptance',
}
CONF = {
    'snd-soc-mtk-common': 'CONFIG_DEVICE_MODULES_SND_SOC_MEDIATEK', 'mtk-afe-external': 'obj-m (unconditional)', 'mtk-sp-spk-amp': 'obj-m (unconditional)',
    'snd-soc-mt6878-afe': 'CONFIG_DEVICE_MODULES_SND_SOC_MT6878', 'mt6878-mt6369': 'CONFIG_DEVICE_MODULES_SND_SOC_MT6878_MT6369',
    'clk-mt6878-adsp': 'CONFIG_COMMON_CLK_MT6878_ADSP', 'mt6685-audclk': 'CONFIG_MT6685_AUDCLK', 'mt6369-regulator': 'CONFIG_REGULATOR_MT6369',
    'snd-soc-mt6369': 'CONFIG_DEVICE_MODULES_SND_SOC_MT6369', 'mt6369-accdet': 'CONFIG_SND_SOC_MT6369_ACCDET', 'snd-soc-tfa98xx': 'CONFIG_SND_SOC_TFA9874',
    'aw883xx_driver': 'out-of-ALPS Awinic Kbuild (obj-m)', 'adsp': 'CONFIG_MTK_AUDIODSP_SUPPORT', 'audio_ipi': 'CONFIG_MTK_AUDIO_IPI', 'mtk-vow': 'CONFIG_MTK_VOW_SUPPORT',
    'snd-soc-audiodsp-common': 'CONFIG_SND_SOC_MTK_AUDIO_DSP', 'mtk-soc-offload-common': 'CONFIG_SND_SOC_MTK_OFFLOAD', 'mtk-scp-audiocommon': 'CONFIG_SND_SOC_MTK_AUDIO_DSP',
    'mtk-scp-vow': 'CONFIG_MTK_VOW_SUPPORT', 'snd-soc-mtk-scp-ultra': 'CONFIG_MTK_ULTRASND_PROXIMITY', 'mtk-scp-ultra': 'CONFIG_MTK_ULTRASND_PROXIMITY',
}
ids = {r['module_id'] for r in selected}
edges = [e for e in csv.DictReader((A / 'DEPENDENCY-EDGES.tsv').open(), delimiter='\t') if e['consumer_module_id'] in ids]
fields = ['module_id', 'filename', 'initial_class', 'canonical_owner', 'component_status', 'source_owner', 'initial_source_group', 'dependency_group',
          'candidate_directory', 'candidate_configs', 'stock_partitions', 'stock_sha256', 'stock_size', 'stock_paths', 'load_phase', 'load_order',
          'stock_functions', 'stock_data_objects', 'stock_imports', 'stock_exports', 'stock_kcfi_abs_ids', 'stock_relocations',
          'historical_source_location', 'historical_build_script', 'historical_parity_evidence', 'historical_parity',
          'donor_candidate', 'public_source_url', 'build_dependencies', 'external_providers', 'planned_repository', 'expected_parity_work']
with (P / 'BATCH-MANIFEST.tsv').open('w') as o:
    w = csv.DictWriter(o, fieldnames=fields, delimiter='\t', lineterminator='\n'); w.writeheader()
    for r in sorted(selected, key=lambda r: (fam[r['filename']], r['filename'])):
        m = r['filename'][:-3]
        for p in r['stock_paths'].split(';'):
            b = (CANON / p).read_bytes(); assert hashlib.sha256(b).hexdigest() == r['stock_sha256'] and len(b) == int(r['stock_size']), p
        es = [e for e in edges if e['consumer_module_id'] == r['module_id']]
        provs = sorted({p for e in es for p in e['provider_module_ids'].split(';') if p})
        aw = m == 'aw883xx_driver'
        w.writerow(dict(
            module_id=r['module_id'], filename=r['filename'], initial_class=r['source_status'], canonical_owner=r['component_owner'],
            component_status=r['component_status'], source_owner=r['source_owner'], initial_source_group=r['source_group'], dependency_group=fam[r['filename']],
            candidate_directory=DIRS[m], candidate_configs=CONF[m], stock_partitions=r['partitions'], stock_sha256=r['stock_sha256'], stock_size=r['stock_size'],
            stock_paths=r['stock_paths'], load_phase=r['load_phase'], load_order=r['load_order'], stock_functions=r['stock_functions'],
            stock_data_objects=r['stock_data_objects'], stock_imports=r['stock_imports'], stock_exports=r['stock_exports'],
            stock_kcfi_abs_ids=r['stock_kcfi_abs_ids'], stock_relocations=r['stock_relocations'],
            historical_source_location=HIST.get(m, r['source_snapshot_path'] + ' (research copy byte-identical to ALPS 5e41 where present)'),
            historical_build_script=r['build_script'], historical_parity_evidence=r['parity_evidence'], historical_parity=r['historical_parity'],
            donor_candidate=('awinic-driver/aw883xx@4f52a107e82b88512124a14cc69601cdefd40b9e + preserved v1.7.1 reconstruction delta' if aw else
                             'NothingOSS ALPS 5e415e059253ce0d2e61c97108e5f5785d71f06f:' + DIRS[m]),
            public_source_url=('https://github.com/awinic-driver/aw883xx' if aw else 'https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878'),
            build_dependencies=';'.join(sorted({p.split('@')[0] for p in provs if p in ids})) or 'NONE_IN_BATCH',
            external_providers=';'.join(p for p in provs if p not in ids) or 'GKI_CORE_ONLY',
            planned_repository='../android_kernel_modules_audio_ulefone_gq5012bf1',
            expected_parity_work=EXPECT.get(m, 'Unchanged ALPS candidate; independent pinned rebuild and full ELF acceptance (code/data/CRC/KCFI/relocations/sections/modinfo)')))
E = P / 'evidence/baseline'; E.mkdir(parents=True, exist_ok=True)
for n in ['ALL-457-MODULES.tsv', 'SOURCE-OWNERSHIP.tsv', 'evidence/audit-summary.json']:
    (E / Path(n).name).write_bytes((A / n).read_bytes())
(E / 'selected-original-rows.json').write_text(json.dumps(selected, indent=2) + '\n')
with (P / 'DEPENDENCIES.tsv').open('w') as o:
    w = csv.DictWriter(o, fieldnames=list(edges[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(edges)
h = hashlib.sha256((P / 'BATCH-MANIFEST.tsv').read_bytes()).hexdigest()
(P / 'BATCH-MANIFEST.sha256').write_text(h + '  BATCH-MANIFEST.tsv\n')
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
print('FROZEN21', h, 'edges', len(edges), dict(collections.Counter(r['source_status'] for r in selected)), 'worktree HEAD', head)
