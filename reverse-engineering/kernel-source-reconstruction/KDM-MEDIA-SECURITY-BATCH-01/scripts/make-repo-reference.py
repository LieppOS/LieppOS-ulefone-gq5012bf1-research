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
    'mtk-composite.ko': 'drivers/misc/mediatek/flashlight',
    'mtk_jpeg.ko': 'drivers/media/platform/mtk-jpeg', 'mtk-mmdvfs-v3-start.ko': 'drivers/misc/mediatek/mmdvfs',
    'mtk_sec_heap.ko': 'drivers/dma-buf/heaps', 'mtk_heap_debug.ko': 'drivers/dma-buf/heaps',
    'widevine_driver.ko': 'drivers/misc/mediatek/widevine_drm', 'tui-common.ko': 'drivers/input/touchscreen',
    'sapu.ko': 'drivers/misc/mediatek/apusys/sapu', 'mtk_irtx_pwm.ko': 'drivers/misc/mediatek/irtx',
    'nvmem-mt635x-efuse.ko': 'drivers/nvmem'}
NATIVE_DIR = {}
FAMILY = {
    'FLASHLIGHT': ['mtk-composite.ko'],
    'MEDIA': ['mtk_jpeg.ko', 'mtk-mmdvfs-v3-start.ko'],
    'DMA-HEAP': ['mtk_sec_heap.ko', 'mtk_heap_debug.ko'],
    'SECURITY': ['widevine_driver.ko', 'tui-common.ko', 'sapu.ko'],
    'PLATFORM-IO': ['mtk_irtx_pwm.ko', 'nvmem-mt635x-efuse.ko']}
# Provider source directories (pinned ALPS 5e415e05 Makefile locations; owners in ABI-PROVIDERS.tsv).
# tmem_ffa / gz_trusty_mod / gz_tz_system (Codex G targets) and mtk-pwm (G) are compile-only witnesses.
PROVIDER_DIR = {
    'mtk_pbm.ko': 'drivers/misc/mediatek/pbm', 'mtk_peak_power_budget.ko': 'drivers/misc/mediatek/pbm',
    'mtk_low_battery_throttling.ko': 'drivers/misc/mediatek/power_throttling', 'mtk_bp_thl.ko': 'drivers/misc/mediatek/power_throttling',
    'mtk-icc-core.ko': 'drivers/misc/mediatek/mtk-interconnect', 'mtk-mmdvfs-v3.ko': 'drivers/soc/mediatek',
    'mtk-mmdvfs-debug.ko': 'drivers/misc/mediatek/mmdvfs', 'system_heap.ko': 'drivers/dma-buf/heaps',
    'mrdump.ko': 'drivers/misc/mediatek/aee/mrdump', 'monitor_hang.ko': 'drivers/misc/mediatek/monitor_hang',
    'tmem_ffa.ko': 'drivers/misc/mediatek/trusted_mem', 'gz_trusty_mod.ko': 'drivers/misc/mediatek/geniezone/gz-trusty',
    'gz_tz_system.ko': 'drivers/misc/mediatek/geniezone', 'mtk-pwm.ko': 'drivers/misc/mediatek/pwm'}
DUPLICATE_EXPORT_MODULES = {}

man = list(csv.DictReader((P / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
# Frozen research targets that remain blocked are NOT built or owned by this recipe (see BLOCKERS.tsv):
BLOCKED = {'flashlight.ko': 'OEM flashlight-core.c variant unavailable (extra flashlight_drvctrl/flashlight_sw_ctrl_*; no pt_over_cur/pt_oc_callback)'}
man = [m for m in man if m['filename'] not in BLOCKED]
fam = {f: k for k, v in FAMILY.items() for f in v}
assert sorted(fam) == sorted(m['filename'] for m in man) and sorted(set(KDM_DIR) | set(NATIVE_DIR)) == sorted(fam)
ref = REPO / 'reference'
rows = []
for m in man:
    f = m['filename']
    rows.append(dict(module_id=m['module_id'], filename=f, initial_class=m['canonical_class'], family=fam[f],
                     source_owner_before=m['source_owner'], stock_sha256=m['stock_sha256'], stock_size=m['stock_size'],
                     stock_partitions=m['partition'], stock_paths=m['stock_path'], selection_evidence='frozen KDM-MEDIA-SECURITY-BATCH-01 manifest (vendor_dlkm)',
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
graph = [g for g in csv.DictReader(GRAPH.open(), delimiter='\t') if g['provider_kind'] == 'VENDOR_MODULE' and g['target'] not in BLOCKED
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
    batch='KDM-MEDIA-SECURITY-BATCH-01', families={k: sorted(next(r['module_id'] for r in rows if r['filename'] == f) for f in v) for k, v in FAMILY.items()},
    owned_module_ids=sorted(r['module_id'] for r in rows), blocked_not_owned=BLOCKED,
    not_owned='All 14 external providers remain with their owners: mtk_pbm, mtk_peak_power_budget, mtk_low_battery_throttling, mtk_bp_thl, mtk-icc-core, mtk-mmdvfs-v3, mtk-mmdvfs-debug, system_heap, mrdump, monitor_hang (canonical A) and tmem_ffa, gz_trusty_mod, gz_tz_system (Codex G-SOURCE-RECOVERY-BATCH-01 targets), mtk-pwm (G). Witnesses here are compile-only ABI checks with no ownership or certification transfer.'),
    indent=2) + '\n')
print('manifest', len(rows), 'boundaries', len(bounds), 'provider dirs', len(units))
