#!/usr/bin/env python3
"""Freeze SCP-CONNECTIVITY-BATCH-01 from the last stable canonical audit before any build.

Selection rule (not a hand list): every uncertified identity whose audit source_group is
PRESERVE:SENSOR-HUB or PRESERVE:CONNECTIVITY. Asserted disjoint from Codex AUDIO-BATCH-01
and Claude PLATFORM-BATCH-04. Modem (PRESERVE:MODEM), charging/USB and audio identities are
not pulled in to reach a quota; providers outside the selection stay external.
"""
from pathlib import Path
import csv, json, hashlib, subprocess, collections

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
A = R / 'reverse-engineering/kernel-source-parity-audit'
CANON = R.parent / 'ulefone-gq5012bf1-research'  # read-only stock operands (gitignored workspace/)
AUDIO = R.parent / 'ulefone-gq5012bf1-research-codex-audio/reverse-engineering/kernel-source-reconstruction/AUDIO-BATCH-01/BATCH-MANIFEST.tsv'
BASELINE = '548526fc711cf9943a20d2daad42158ee1543842'   # last audit-changing commit
BASE_HEAD = 'bb370374f4d53f4860b0f7df88a40a3107e6d83c'  # recorded canonical master commit (worktree base)
assert not (P / 'BATCH-MANIFEST.tsv').exists(), 'Frozen manifest is immutable'
assert subprocess.check_output(['git', 'merge-base', '--is-ancestor', BASE_HEAD, 'HEAD'], cwd=R) == b''
for n in ['ALL-457-MODULES.tsv', 'SOURCE-GAPS.tsv', 'SOURCE-OWNERSHIP.tsv', 'DEPENDENCY-EDGES.tsv', 'evidence/audit-summary.json']:
    for c in (BASELINE, BASE_HEAD):
        want = subprocess.check_output(['git', 'show', f'{c}:reverse-engineering/kernel-source-parity-audit/{n}'], cwd=R)
        assert (A / n).read_bytes() == want, f'audit drift: {n} vs {c}'

allr = list(csv.DictReader((A / 'ALL-457-MODULES.tsv').open(), delimiter='\t'))
summ = json.loads((A / 'evidence/audit-summary.json').read_text())
assert len(allr) == 458 and summ['verified_A_B'] == 220
assert collections.Counter(r['source_status'] for r in allr) == dict(A=219, B=1, C=9, D=98, G=131)
selected = [r for r in allr if r['source_group'] in ('PRESERVE:SENSOR-HUB', 'PRESERVE:CONNECTIVITY') and r['source_status'] not in ('A', 'B')]
assert len(selected) == 20 and len({r['filename'] for r in selected}) == 20
ids = {r['module_id'] for r in selected}
b4 = {r['module_id'] for r in csv.DictReader((R / 'reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-04/BATCH-MANIFEST.tsv').open(), delimiter='\t')}
au = {r['module_id'] for r in csv.DictReader(AUDIO.open(), delimiter='\t')}
assert len(b4) == 30 and len(au) == 21 and not (b4 | au) & ids, 'overlap with concurrent batch'

ALPS = '5e415e059253ce0d2e61c97108e5f5785d71f06f'
NKM = '2115d278396fe63bd7d021e46091f3c44af64011'
COMMON = '6b18f0b574ab3267615ae6ce642d5a7c3c21ac09'
KDM_URL = 'https://github.com/NothingOSS/android_kernel_device_modules_6.1_nothing_mt6878'
NKM_URL = 'https://github.com/NothingOSS/android_kernel_modules_nothing_mt6878'
ACK_URL = 'https://android.googlesource.com/kernel/common'
# module: (dependency_group, tree, directory, config, historical delta / expectation)
SPEC = {
    'scp': ('SCP-SENSORHUB', 'kdm', 'drivers/misc/mediatek/scp/rv', 'CONFIG_MTK_TINYSYS_SCP_SUPPORT',
            'Historical 957dac1+0001 scp/rv tree is byte-identical to pristine ALPS 5e41 scp/rv; full ELF acceptance incl. 208 stock FUNC symbols'),
    'hf_manager': ('SCP-SENSORHUB', 'kdm', 'drivers/misc/mediatek/sensor/2.0/core', 'CONFIG_MTK_SENSOR_SUPPORT',
                   'Historical YFT devinfo hooks + hf_sensor_type enum reshape re-expressed against ALPS; full ELF acceptance'),
    'sensorhub': ('SCP-SENSORHUB', 'kdm', 'drivers/misc/mediatek/sensor/2.0/sensorhub', 'CONFIG_MTK_SENSORHUB',
                  'Historical transceiver display-notifier delta re-expressed against ALPS; full ELF acceptance'),
    'connadp': ('CONN-KDM', 'kdm', 'drivers/misc/mediatek/connectivity', 'CONFIG_MTK_COMBO', 'ALPS 5e41 tree == historical 6df3204 tree; full ELF acceptance'),
    'connscp': ('CONN-KDM', 'kdm', 'drivers/misc/mediatek/conn_scp', 'CONFIG_MTK_CONN_SCP', 'ALPS 5e41 tree == historical 6df3204 tree; full ELF acceptance'),
    'uarthub_drv': ('CONN-KDM', 'kdm', 'drivers/misc/mediatek/uarthub', 'CONFIG_MTK_UARTHUB', 'ALPS 5e41 tree == historical 957dac1 tree; full ELF acceptance'),
    'wifi_cooling': ('CONN-KDM', 'kdm', 'drivers/thermal/mediatek', 'CONFIG_MTK_WIFI_THERMAL', 'ALPS 5e41 file == historical 6df3204 file; full ELF acceptance'),
    'mtk-btcvsd': ('CONN-KDM', 'kdm', 'sound/soc/mediatek/common', 'CONFIG_DEVICE_MODULES_SND_SOC_MTK_BTCVSD', 'ALPS 5e41 file == historical e380922 file; full ELF acceptance'),
    'conninfra': ('CONN-NKM', 'nkm', 'connectivity/conninfra', 'Kbuild (CONFIG_MTK_COMBO)', 'Historical tree == NothingOSS kernel_modules 2115d27; __FILE__ path + TARGET_BUILD_VARIANT unset'),
    'connfem': ('CONN-NKM', 'nkm', 'connectivity/connfem', 'Kbuild', 'Historical tree == 2115d27; full ELF acceptance'),
    'wmt_chrdev_wifi_connac2': ('CONN-NKM', 'nkm', 'connectivity/wlan/adaptor/build/connac2x', 'Kbuild', 'Historical tree == 2115d27; full ELF acceptance'),
    'wlan_drv_gen4m_6878': ('CONN-NKM', 'nkm', 'connectivity/wlan/core/gen4m', 'Kbuild.6878 (MODULE_NAME=wlan_drv_gen4m_6878 SEGMENT=SP)',
                            'Historical 2115d27 + 13-hunk ALPS V11.24 backport patch; DRIVER_BUILD_DATE recipe input; full ELF acceptance'),
    'bt_drv_6878': ('CONN-NKM', 'nkm', 'connectivity/bt/mt66xx/6878', 'Kbuild', 'Historical tree == 2115d27; full ELF acceptance'),
    'fmradio_drv_connac2x': ('CONN-NKM', 'nkm', 'connectivity/fmradio/Build/connac2x', 'Kbuild', 'Historical tree == 2115d27; full ELF acceptance'),
    'gps_drv_dl_v051': ('CONN-NKM', 'nkm', 'connectivity/gps/data_link/plat/v051', 'Kbuild', 'Historical tree == 2115d27; full ELF acceptance'),
    'gps_pwr': ('CONN-NKM', 'nkm', 'connectivity/gps/gps_pwr', 'Kbuild', 'Historical tree == 2115d27; full ELF acceptance'),
    'gps_scp': ('CONN-NKM', 'nkm', 'connectivity/gps/gps_scp', 'Kbuild', 'Historical tree == 2115d27; full ELF acceptance'),
    'cfg80211': ('GKI-INTREE', 'common', 'net/wireless', 'CONFIG_CFG80211=m (vendor in-tree)',
                 'Vendor in-tree build (intree=Y, scmversion g945dff7bc1bf) with split .BTF over the OEM vmlinux; historical modinfo re-link superseded by a genuine in-tree build; BTF base lineage is the known Batch03 blocker'),
    'mac80211': ('GKI-INTREE', 'common', 'net/mac80211', 'CONFIG_MAC80211=m (vendor in-tree)', 'As cfg80211'),
    'bluetooth': ('GKI-INTREE', 'common', 'net/bluetooth', 'CONFIG_BT=m (vendor in-tree)', 'As cfg80211'),
}
assert set(SPEC) == {r['filename'][:-3] for r in selected}
REPO = {'SCP-SENSORHUB': '../android_kernel_modules_scp_sensorhub_ulefone_gq5012bf1'}
TREE = {'kdm': (f'NothingOSS ALPS {ALPS}', KDM_URL), 'nkm': (f'NothingOSS kernel_modules {NKM}', NKM_URL), 'common': (f'ACK common {COMMON}', ACK_URL)}
edges = [e for e in csv.DictReader((A / 'DEPENDENCY-EDGES.tsv').open(), delimiter='\t') if e['consumer_module_id'] in ids]
fields = ['module_id', 'filename', 'initial_class', 'canonical_owner', 'component_status', 'source_owner', 'initial_source_group', 'dependency_group',
          'candidate_directory', 'candidate_configs', 'stock_partitions', 'stock_sha256', 'stock_size', 'stock_paths', 'load_phase', 'load_order',
          'stock_functions', 'stock_data_objects', 'stock_imports', 'stock_exports', 'stock_kcfi_abs_ids', 'stock_relocations', 'stock_btf',
          'historical_source_location', 'historical_build_script', 'historical_parity_evidence', 'historical_parity',
          'donor_candidate', 'public_source_url', 'build_dependencies', 'external_providers', 'planned_repository', 'expected_parity_work']
GORDER = ['SCP-SENSORHUB', 'CONN-KDM', 'CONN-NKM', 'GKI-INTREE']
with (P / 'BATCH-MANIFEST.tsv').open('w') as o:
    w = csv.DictWriter(o, fieldnames=fields, delimiter='\t', lineterminator='\n'); w.writeheader()
    for r in sorted(selected, key=lambda r: (GORDER.index(SPEC[r['filename'][:-3]][0]), r['filename'])):
        m = r['filename'][:-3]; g, tree, d, conf, exp = SPEC[m]
        b = None
        for p in r['stock_paths'].split(';'):
            b = (CANON / p).read_bytes(); assert hashlib.sha256(b).hexdigest() == r['stock_sha256'] and len(b) == int(r['stock_size']), p
        es = [e for e in edges if e['consumer_module_id'] == r['module_id']]
        provs = sorted({p for e in es for p in e['provider_module_ids'].split(';') if p})
        w.writerow(dict(
            module_id=r['module_id'], filename=r['filename'], initial_class=r['source_status'], canonical_owner=r['component_owner'],
            component_status=r['component_status'], source_owner=r['source_owner'], initial_source_group=r['source_group'], dependency_group=g,
            candidate_directory=d, candidate_configs=conf, stock_partitions=r['partitions'], stock_sha256=r['stock_sha256'], stock_size=r['stock_size'],
            stock_paths=r['stock_paths'], load_phase=r['load_phase'], load_order=r['load_order'], stock_functions=r['stock_functions'],
            stock_data_objects=r['stock_data_objects'], stock_imports=r['stock_imports'], stock_exports=r['stock_exports'],
            stock_kcfi_abs_ids=r['stock_kcfi_abs_ids'], stock_relocations=r['stock_relocations'], stock_btf='yes' if b'.BTF\0' in b else 'no',
            historical_source_location=r['source_snapshot_path'], historical_build_script=r['build_script'] or ('reverse-engineering/connectivity/scripts/rebuild_all.sh' if g != 'SCP-SENSORHUB' else 'reverse-engineering/sensors (KDM 7d3c303)'),
            historical_parity_evidence=r['parity_evidence'], historical_parity=r['historical_parity'],
            donor_candidate=TREE[tree][0] + ':' + d, public_source_url=TREE[tree][1],
            build_dependencies=';'.join(sorted({p.split('@')[0] for p in provs if p in ids})) or 'NONE_IN_BATCH',
            external_providers=';'.join(p for p in provs if p not in ids) or 'GKI_CORE_ONLY',
            planned_repository=REPO.get(g, '../android_kernel_modules_connectivity_ulefone_gq5012bf1'), expected_parity_work=exp))
E = P / 'evidence/baseline'; E.mkdir(parents=True, exist_ok=True)
for n in ['ALL-457-MODULES.tsv', 'SOURCE-OWNERSHIP.tsv', 'evidence/audit-summary.json']:
    (E / Path(n).name).write_bytes((A / n).read_bytes())
(E / 'selected-original-rows.json').write_text(json.dumps(selected, indent=2) + '\n')
with (P / 'DEPENDENCIES.tsv').open('w') as o:
    w = csv.DictWriter(o, fieldnames=list(edges[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(edges)
h = hashlib.sha256((P / 'BATCH-MANIFEST.tsv').read_bytes()).hexdigest()
(P / 'BATCH-MANIFEST.sha256').write_text(h + '  BATCH-MANIFEST.tsv\n')
print('FROZEN20', h, 'edges', len(edges), dict(collections.Counter(r['source_status'] for r in selected)),
      dict(collections.Counter(SPEC[r['filename'][:-3]][0] for r in selected)))
