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
    '8250_mtk.ko': 'drivers/tty/serial/8250', 'i2c-mt65xx.ko': 'drivers/i2c/busses',
    'mtk-mminfra-imax.ko': 'drivers/misc/mediatek/mminfra', 'mtk-swpm-perf-arm-pmu.ko': 'drivers/misc/mediatek/swpm',
    'mtk-vmm-spm.ko': 'drivers/misc/mediatek/vmm_spm', 'mtk_dpc.ko': 'drivers/gpu/drm/mediatek/dpc',
    'nvmem_mtk-devinfo.ko': 'drivers/nvmem', 'regulator-vibrator.ko': 'drivers/leds', 'reset-ti-syscon.ko': 'drivers/reset',
    'rtc-mt6685.ko': 'drivers/rtc', 'sec.ko': 'drivers/misc/mediatek/masp', 'teeperf.ko': 'drivers/tee/teeperf',
    'timer-mediatek.ko': 'drivers/clocksource'}
NATIVE_DIR = {'arm_dsu_pmu.ko': 'drivers/perf', 'kfifo_buf.ko': 'drivers/iio/buffer', 'industrialio-triggered-buffer.ko': 'drivers/iio/buffer'}
FAMILY = {
    'PLATFORM-TIMEKEEPING-IO': ['timer-mediatek.ko', '8250_mtk.ko', 'i2c-mt65xx.ko', 'reset-ti-syscon.ko', 'rtc-mt6685.ko', 'regulator-vibrator.ko'],
    'NVMEM-DEVINFO': ['nvmem_mtk-devinfo.ko'],
    'MM-POWER-INFRA': ['mtk-vmm-spm.ko', 'mtk-mminfra-imax.ko', 'mtk_dpc.ko', 'mtk-swpm-perf-arm-pmu.ko'],
    'SECURITY-TEE-PERF': ['sec.ko', 'teeperf.ko'],
    'CORE-INTREE-BTF': ['arm_dsu_pmu.ko', 'kfifo_buf.ko', 'industrialio-triggered-buffer.ko']}
# Provider source directories (from the owning maintained repositories' manifests) and modules.
PROVIDER_DIR = {
    'mtk-uart-apdma.ko': 'drivers/dma/mediatek', 'uarthub_drv.ko': 'drivers/misc/mediatek/uarthub',
    'pinctrl-mtk-common-v2_debug.ko': 'drivers/pinctrl/mediatek', 'mtk-cmdq-drv-ext.ko': 'drivers/misc/mediatek/cmdq/mailbox',
    'mtk_slbc.ko': 'drivers/misc/mediatek/slbc', 'mdp_drv_mt6878.ko': 'drivers/misc/mediatek/mdp',
    'mediatek-drm.ko': 'drivers/gpu/drm/mediatek/mediatek_v2', 'mmprofile.ko': 'drivers/misc/mediatek/mmp/src',
    'mtk-mmdvfs-v3.ko': 'drivers/soc/mediatek', 'mtk-mml.ko': 'drivers/gpu/drm/mediatek/mml', 'aee_aed.ko': 'drivers/misc/mediatek/aee/aed'}
# Duplicate exporters inside one external-module modpost run: modpost 6.1 sym_add_exported/hash_add_symbol
# (head insertion) means the last module read (modules.order == genuine Makefile obj-m order) is recorded.
# provider-witness.py re-derives this from the pristine Makefile and refuses a mismatch.
DUPLICATE_EXPORT_MODULES = {'drivers/misc/mediatek/mdp': ['mdp_drv_mt6878', 'mdp_drv_mt6897', 'mdp_drv_mt6985', 'mdp_drv_mt6989']}  # only variants whose mdp_mtXXXX.c exists (Makefile wildcard guards)

man = list(csv.DictReader((P / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
fam = {f: k for k, v in FAMILY.items() for f in v}
assert sorted(fam) == sorted(m['filename'] for m in man) and sorted(set(KDM_DIR) | set(NATIVE_DIR)) == sorted(fam)
ref = REPO / 'reference'
rows = []
for m in man:
    f = m['filename']
    rows.append(dict(module_id=m['module_id'], filename=f, initial_class=m['canonical_class'], family=fam[f],
                     source_owner_before=m['source_owner'], stock_sha256=m['stock_sha256'], stock_size=m['stock_size'],
                     stock_partitions=m['partition'], stock_paths=m['stock_path'], selection_evidence='P0_BOOT first-stage load contract; frozen BOOT-DEPENDENCY-BATCH-01 manifest',
                     candidate_configs=m['candidate_configs'], build_domain='KDM' if f in KDM_DIR else 'NATIVE',
                     candidate_directory=KDM_DIR.get(f) or NATIVE_DIR[f]))
with (ref / 'BATCH-MANIFEST.tsv').open('w') as fh:
    w = csv.DictWriter(fh, list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)
VB = STOCK / 'vendor-ramdisks/platform-extracted/lib/modules'
with (ref / 'stock-normalized.tsv').open('w') as fh:
    fh.write('module\tstock_sha256\tbytes\tnormalized_sha256\n')
    for r in rows:
        k = kpp.KO(str(VB / r['filename'])); b, d, n = norm.normalized(k)
        assert hashlib.sha256(k.b).hexdigest() == r['stock_sha256']
        fh.write(f"{r['filename'][:-3]}\t{r['stock_sha256']}\t{len(k.b)}\t{hashlib.sha256(b).hexdigest()}\n")
graph = [g for g in csv.DictReader(GRAPH.open(), delimiter='\t') if g['provider_kind'] == 'VENDOR_BOOT_MODULE'
         and g['provider'] not in fam]  # in-batch kfifo_buf is resolved by the same native modpost run
bounds, units, symvers = {}, {}, []
for g in sorted(graph, key=lambda g: g['symbol']):
    s, prov = g['symbol'], g['provider']
    k = kpp.KO(str(VB / prov))
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
    batch='BOOT-DEPENDENCY-BATCH-01', families={k: sorted(next(r['module_id'] for r in rows if r['filename'] == f) for f in v) for k, v in FAMILY.items()},
    owned_module_ids=sorted(r['module_id'] for r in rows),
    not_owned='All providers (CMDQ, SLBC, MDP, DRM, MMP, MMDVFS, MML, AEE, UART APDMA, UARTHUB, pinctrl debug) remain owned by their certified repositories; witnesses here are compile-only ABI checks.'),
    indent=2) + '\n')
print('manifest', len(rows), 'boundaries', len(bounds), 'provider dirs', len(units))
