#!/usr/bin/env python3
"""Generate the maintained repository's reference/ expectations for DISPLAY-BACKLIGHT-G-BATCH-01 from
the frozen manifest and read-only stock operands. Stock bytes are only *read*: hashes, export
CRC/licence/namespace and KCFI prefix words become acceptance expectations, never build inputs.

usage: make-repo-reference.py <stock-root> <repo> <dependency-graph.tsv>
"""
import csv, hashlib, json, struct, sys, importlib.util
from pathlib import Path

P = Path(__file__).resolve().parents[1]
STOCK, REPO, GRAPH = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / 'scripts'))
sp = importlib.util.spec_from_file_location('norm', REPO / 'scripts/normalize.py')
norm = importlib.util.module_from_spec(sp); sp.loader.exec_module(norm)
kpp = norm.kpp

# ALPS 5e415e05 KDM provider directories (owners recorded in ABI-PROVIDERS.tsv; witness-only here).
PROVIDER_DIR = {
    'leds-mtk.ko': 'drivers/leds',
    'mediatek-drm.ko': 'drivers/gpu/drm/mediatek/mediatek_v2',
    'mtk_panel_ext.ko': 'drivers/gpu/drm/mediatek/mediatek_v2',
    'cmdq-sec-drv.ko': 'drivers/misc/mediatek/cmdq/mailbox',
    'mtk-cmdq-drv-ext.ko': 'drivers/misc/mediatek/cmdq/mailbox',
    'mtk_sec_heap.ko': 'drivers/dma-buf/heaps',
    'mtk_printk_ctrl.ko': 'drivers/misc/mediatek/mtprintk',
}
# met.ko exports are produced by the genuine NKM met_drv_v3 core build in the same run (its own
# Module.symvers), not by a KDM witness.
NKM_PROVIDERS = {'met.ko'}

man = list(csv.DictReader((P / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
targets = {m['filename'] for m in man}
ref = REPO / 'reference'
rows = []
for m in man:
    dom = 'KDM' if m['build_domain'] == 'KDM' else 'NKM'
    d = m['candidate_directory']
    rows.append(dict(module_id=m['module_id'], filename=m['filename'], initial_class=m['initial_class'], family=m['family'],
                     stock_sha256=m['stock_sha256'], stock_size=m['stock_size'], partitions=m['partitions'], stock_paths=m['stock_paths'],
                     source_provenance=m['source_provenance'], candidate_configs=m['candidate_configs'], build_domain=dom, candidate_directory=d))
with (ref / 'BATCH-MANIFEST.tsv').open('w') as fh:
    w = csv.DictWriter(fh, list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)

def stock_file(r):
    return STOCK / r['stock_paths'].split(';')[0].removeprefix('workspace/gq5012bf1/stock/')

with (ref / 'stock-normalized.tsv').open('w') as fh:
    fh.write('module\tstock_sha256\tbytes\tnormalized_sha256\n')
    for r in rows:
        k = kpp.KO(str(stock_file(r))); b, d, n = norm.normalized(k)
        assert hashlib.sha256(k.b).hexdigest() == r['stock_sha256']
        fh.write(f"{r['filename'][:-3]}\t{r['stock_sha256']}\t{len(k.b)}\t{hashlib.sha256(b).hexdigest()}\n")

PV = [STOCK / 'vendor-ramdisks/platform-extracted/lib/modules', STOCK / 'partitions/vendor_dlkm/lib/modules']
graph = [g for g in csv.DictReader(GRAPH.open(), delimiter='\t') if g['provider_kind'] == 'VENDOR_MODULE'
         and g['provider'] not in targets and g['provider'] not in NKM_PROVIDERS]
bounds, units, symvers = {}, {}, []
for g in sorted(graph, key=lambda g: g['symbol']):
    s, prov = g['symbol'], g['provider']
    k = kpp.KO(str(next(d / prov for d in PV if (d / prov).exists())))
    y = next(y for y in k.syms if y['n'] == s and 0 < y['shndx'] < len(k.secs))
    word = None
    if y['info'] & 15 == 2:
        word = hex(struct.unpack_from('<I', k.b, k.secs[y['shndx']]['off'] + y['val'] - 4)[0])
    d = PROVIDER_DIR[prov]
    e = dict(candidate_directory=d, crc=g['provider_crc'], licence=g['licence'], namespace=g['namespace'], provider_module=prov[:-3],
             provider_module_id=f"{prov}@{hashlib.sha256(k.b).hexdigest()}", stock_kcfi_prefix_word=word, symbol_type=y['info'] & 15,
             symvers_module=prov[:-3])
    assert bounds.get(s, e) == e
    if s not in bounds:
        bounds[s] = e
        symvers.append(f"{g['provider_crc']}\t{s}\t{prov[:-3]}\t{g['licence']}\t{g['namespace']}\n")
    units.setdefault(d, set()).add(prov[:-3])
(ref / 'provider-boundaries.json').write_text(json.dumps(bounds, indent=2, sort_keys=True) + '\n')
(ref / 'provider-build-units.json').write_text(json.dumps({k: sorted(v) for k, v in sorted(units.items())}, indent=2) + '\n')
(ref / 'external-provider.symvers').write_text(''.join(symvers))
fam = REPO / 'families/DISPLAY-BACKLIGHT'
fam.mkdir(parents=True, exist_ok=True)
(fam / 'OWNERSHIP.json').write_text(json.dumps(dict(
    family='DISPLAY-BACKLIGHT', batch='DISPLAY-BACKLIGHT-G-BATCH-01',
    targets=sorted(r['module_id'] for r in rows),
    manifest_sha256=hashlib.sha256((P / 'BATCH-MANIFEST.tsv').read_bytes()).hexdigest(),
    witness_only_providers={d: sorted(v) for d, v in sorted(units.items())},
    nkm_witness_only=['met (met_drv_v3 core; owned by android_kernel_modules_met_instrumentation_ulefone_gq5012bf1)'],
    not_owned='mediatek-drm, mtk_panel_ext, leds-mtk (audio_shared_infrastructure), cmdq-sec-drv, mtk-cmdq-drv-ext (cmdq), mtk_sec_heap (kdm_media_security), mtk_printk_ctrl (platform_diagnostics), met (met_instrumentation) stay with their owners; compile-only ABI witnesses here.'),
    indent=2) + '\n')
print('manifest', len(rows), 'boundaries', len(bounds), 'provider dirs', len(units))
