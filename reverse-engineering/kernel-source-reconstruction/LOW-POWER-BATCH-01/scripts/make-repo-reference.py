#!/usr/bin/env python3
"""Generate the maintained repository's reference/ expectations from the frozen manifest and
read-only stock operands.  Stock bytes are only *read*: hashes, export CRC/licence/namespace and
KCFI prefix words become acceptance expectations, never build inputs.

usage: make-repo-reference.py <stock-root> <repo> <dependency-graph.tsv>
"""
import csv, hashlib, json, struct, sys, importlib.util
from pathlib import Path

P = Path(__file__).resolve().parents[1]
STOCK, REPO, GRAPH = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.dont_write_bytecode = True
sp = importlib.util.spec_from_file_location('norm', REPO / 'scripts/normalize.py')
sys.path.insert(0, str(REPO / 'scripts'))
norm = importlib.util.module_from_spec(sp); sp.loader.exec_module(norm)
kpp = norm.kpp

KDM_DIR = {
    'mtk-lpm.ko': 'drivers/misc/mediatek/lpm', 'mtk-lpm-plat-v1.ko': 'drivers/misc/mediatek/lpm/modules/platform/v1',
    'lpm-gov-MHSP.ko': 'drivers/misc/mediatek/lpm/governors/MHSP', 'mtk-lpm-dbg-common-v2.ko': 'drivers/misc/mediatek/lpm/modules/debug/v2',
    'mtk-lpm-dbg-mt6878.ko': 'drivers/misc/mediatek/lpm/modules/debug/mt6878', 'mtk-swpm.ko': 'drivers/misc/mediatek/swpm',
    'mtk-swpm-dbg-common-v1.ko': 'drivers/misc/mediatek/swpm/modules/debug/v1', 'mtk-swpm-dbg-v6878.ko': 'drivers/misc/mediatek/swpm/modules/debug/v6878',
    'mtk-swpm-cpu-dbg-v6878.ko': 'drivers/misc/mediatek/swpm/modules/debug/v6878', 'mtk-ssc.ko': 'drivers/misc/mediatek/ssc',
    'mtk-ssc-dbg-v2.ko': 'drivers/misc/mediatek/ssc/debug/v2', 'mtk_mbraink.ko': 'drivers/misc/mediatek/mbraink'}
NATIVE_DIR = {}
FAMILY = {
    'LPM': ['mtk-lpm.ko', 'mtk-lpm-plat-v1.ko', 'lpm-gov-MHSP.ko', 'mtk-lpm-dbg-common-v2.ko', 'mtk-lpm-dbg-mt6878.ko'],
    'SWPM': ['mtk-swpm.ko', 'mtk-swpm-dbg-common-v1.ko', 'mtk-swpm-dbg-v6878.ko', 'mtk-swpm-cpu-dbg-v6878.ko'],
    'SSC': ['mtk-ssc.ko', 'mtk-ssc-dbg-v2.ko'],
    'MBRAINK': ['mtk_mbraink.ko']}
# Provider source directories (pinned ALPS 5e415e05 Makefile locations; owners in ABI-PROVIDERS.tsv).
PROVIDER_DIR = {
    'aee_aed.ko': 'drivers/misc/mediatek/aee/aed', 'ccci_md_all.ko': 'drivers/misc/mediatek/eccci', 'ged.ko': 'drivers/gpu/mediatek/ged',
    'mtk-dvfsrc-helper.ko': 'drivers/misc/mediatek/dvfsrc', 'mtk_fpsgo.ko': 'drivers/misc/mediatek/performance/fpsgo_v3',
    'mtk-swpm-perf-arm-pmu.ko': 'drivers/misc/mediatek/swpm', 'mtk_gpu_hal.ko': 'drivers/gpu/mediatek/hal',
    'mtk_gpufreq_wrapper.ko': 'drivers/gpu/mediatek/gpufreq/v2', 'mtk_qos.ko': 'drivers/misc/mediatek/qos',
    'pinctrl-mtk-common-v2_debug.ko': 'drivers/pinctrl/mediatek', 'scp.ko': 'drivers/misc/mediatek/scp/rv',
    'sspm_v3.ko': 'drivers/misc/mediatek/sspm/v3', 'thermal_interface.ko': 'drivers/thermal/mediatek',
    'tinysys-scmi.ko': 'drivers/misc/mediatek/tinysys_scmi'}
DUPLICATE_EXPORT_MODULES = {}

man = list(csv.DictReader((P / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
fam = {f: k for k, v in FAMILY.items() for f in v}
assert sorted(fam) == sorted(m['filename'] for m in man) and sorted(set(KDM_DIR) | set(NATIVE_DIR)) == sorted(fam)
ref = REPO / 'reference'
rows = []
for m in man:
    f = m['filename']
    rows.append(dict(module_id=m['module_id'], filename=f, initial_class=m['canonical_class'], family=fam[f],
                     source_owner_before=m['source_owner'], stock_sha256=m['stock_sha256'], stock_size=m['stock_size'],
                     stock_partitions=m['partition'], stock_paths=m['stock_path'], selection_evidence='frozen LOW-POWER-BATCH-01 manifest (vendor_dlkm insmod_sh:vendor)',
                     candidate_configs=m['candidate_configs'], build_domain='KDM' if f in KDM_DIR else 'NATIVE',
                     candidate_directory=KDM_DIR.get(f) or NATIVE_DIR[f]))
with (ref / 'BATCH-MANIFEST.tsv').open('w') as fh:
    w = csv.DictWriter(fh, list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)
VB = STOCK / 'partitions/vendor_dlkm/lib/modules'
PV = [STOCK / 'vendor-ramdisks/platform-extracted/lib/modules', STOCK / 'partitions/vendor_dlkm/lib/modules']
with (ref / 'stock-normalized.tsv').open('w') as fh:
    fh.write('module\tstock_sha256\tbytes\tnormalized_sha256\n')
    for r in rows:
        k = kpp.KO(str(VB / r['filename'])); b, d, n = norm.normalized(k)
        assert hashlib.sha256(k.b).hexdigest() == r['stock_sha256']
        fh.write(f"{r['filename'][:-3]}\t{r['stock_sha256']}\t{len(k.b)}\t{hashlib.sha256(b).hexdigest()}\n")
graph = [g for g in csv.DictReader(GRAPH.open(), delimiter='\t') if g['provider_kind'] == 'VENDOR_MODULE'
         and g['provider'] not in fam]  # in-batch kfifo_buf is resolved by the same native modpost run
bounds, units, symvers = {}, {}, []
for g in sorted(graph, key=lambda g: g['symbol']):
    s, prov = g['symbol'], g['provider']
    k = kpp.KO(str(next(d / prov for d in PV if (d / prov).exists())))
    y = next(y for y in k.syms if y['n'] == s and 0 < y['shndx'] < len(k.secs))
    word = None
    if y['info'] & 15 == 2:
        word = hex(struct.unpack_from('<I', k.b, k.secs[y['shndx']]['off'] + y['val'] - 4)[0])
    d = PROVIDER_DIR[prov]
    symvers_module = DUPLICATE_EXPORT_MODULES[d][-1] if d in DUPLICATE_EXPORT_MODULES else prov[:-3]
    e = dict(candidate_directory=d, crc=g['provider_crc'], licence=g['licence'], namespace=g['namespace'], provider_module=prov[:-3],
             provider_module_id=f"{prov}@{hashlib.sha256(k.b).hexdigest()}", stock_kcfi_prefix_word=word, symbol_type=y['info'] & 15,
             symvers_module=symvers_module)
    assert bounds.get(s, e) == e
    if s not in bounds:
        bounds[s] = e
        symvers.append(f"{g['provider_crc']}\t{s}\t{symvers_module}\t{g['licence']}\t{g['namespace']}\n")
    units.setdefault(d, set()).update(DUPLICATE_EXPORT_MODULES.get(d, [prov[:-3]]))
(ref / 'provider-boundaries.json').write_text(json.dumps(bounds, indent=2, sort_keys=True) + '\n')
(ref / 'provider-build-units.json').write_text(json.dumps({k: sorted(v) for k, v in sorted(units.items())}, indent=2) + '\n')
(ref / 'external-provider.symvers').write_text(''.join(symvers))
(REPO / 'families/OWNERSHIP.json').write_text(json.dumps(dict(
    batch='LOW-POWER-BATCH-01', families={k: sorted(next(r['module_id'] for r in rows if r['filename'] == f) for f in v) for k, v in FAMILY.items()},
    owned_module_ids=sorted(r['module_id'] for r in rows),
    not_owned='All 14 external providers (AEE, CCCI, GED, DVFSRC helper, FPSGO, swpm-perf-arm-pmu, GPU HAL/gpufreq, QoS, pinctrl debug, SCP, SSPM, thermal_interface, tinysys-scmi) remain with their owners; witnesses here are compile-only ABI checks.'),
    indent=2) + '\n')
print('manifest', len(rows), 'boundaries', len(bounds), 'provider dirs', len(units))
