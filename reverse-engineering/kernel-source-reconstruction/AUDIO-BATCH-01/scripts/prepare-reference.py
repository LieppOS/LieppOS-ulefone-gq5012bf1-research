#!/usr/bin/env python3
"""Derive the audio recipe's stock reference data from frozen stock operands.

Writes into <recipe>/reference/:
  stock-normalized.tsv      stock size/sha and GNU-build-ID-zeroed sha for each of the 21 targets
  provider-boundaries.json  every external (non-batch, non-GKI) import: stock CRC, export bucket,
                            namespace, symbol type and stock KCFI prefix word of the stock provider
  external-provider.symvers the stock boundary in Module.symvers syntax; build only emits a slot
                            whose CRC/licence/namespace/KCFI is reproduced by genuine compiled source
Stock bytes are read from the canonical checkout (read-only); nothing is copied into the recipe.
"""
import csv, json, hashlib, struct, sys, importlib.util
from pathlib import Path

B = Path(__file__).resolve().parents[1]
R = B.parents[2]
CANON = R.parent / 'ulefone-gq5012bf1-research'
REC = Path(sys.argv[1]).resolve()
sp = importlib.util.spec_from_file_location('norm', REC / 'scripts/normalize.py')
norm = importlib.util.module_from_spec(sp); sys.path.insert(0, str(REC / 'scripts')); sp.loader.exec_module(norm)
kpp = norm.kpp
man = list(csv.DictReader((B / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
ids = {r['module_id'] for r in man}
allr = {r['module_id']: r for r in csv.DictReader((R / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').open(), delimiter='\t')}

rows = []
for r in sorted(man, key=lambda r: r['filename']):
    p = CANON / r['stock_paths'].split(';')[0]
    ko = kpp.KO(str(p)); b, d, n = norm.normalized(ko)
    assert hashlib.sha256(ko.b).hexdigest() == r['stock_sha256']
    rows.append(dict(module=r['filename'][:-3], bytes=len(ko.b), stock_sha256=r['stock_sha256'],
                     normalized_sha256=hashlib.sha256(b).hexdigest(), build_id_offset=hex(d), build_id_size=n))
with (REC / 'reference/stock-normalized.tsv').open('w') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)

need = {}
for e in csv.DictReader((B / 'DEPENDENCIES.tsv').open(), delimiter='\t'):
    ps = [p for p in e['provider_module_ids'].split(';') if p and p != 'GKI_CORE' and p not in ids]
    if not ps: continue
    assert len(ps) == 1, e
    old = need.setdefault(e['symbol'], (ps[0], e['required_crc']))
    assert old == (ps[0], e['required_crc']), ('inconsistent consumer CRC', e)

bound = {}
for s, (pid, crc) in sorted(need.items()):
    pr = allr[pid]; ko = kpp.KO(str(CANON / pr['stock_paths'].split(';')[0]))
    crcsym = next(y for y in ko.syms if y['n'] == '__crc_' + s and 0 < y['shndx'] < len(ko.secs))
    sec = ko.secs[crcsym['shndx']]; val, = struct.unpack_from('<I', ko.b, sec['off'] + crcsym['val'])
    assert val == int(crc, 16), (s, hex(val), crc)
    lic = 'EXPORT_SYMBOL_GPL' if '_gpl' in sec['n'] else 'EXPORT_SYMBOL'
    sym = next(y for y in ko.syms if y['n'] == s and 0 < y['shndx'] < len(ko.secs))
    typ = sym['info'] & 15
    word = None
    if typ == 2:
        word = hex(struct.unpack_from('<I', ko.b, ko.secs[sym['shndx']]['off'] + sym['val'] - 4)[0])
    ns = next((y for y in ko.syms if y['n'] == '__kstrtabns_' + s and 0 < y['shndx'] < len(ko.secs)), None)
    namespace = ko.b[ko.secs[ns['shndx']]['off'] + ns['val']:].split(b'\0')[0].decode() if ns else ''
    bound[s] = dict(crc=f'0x{val:08x}', licence=lic, namespace=namespace, provider_id=pid,
                    provider_module=pr['filename'][:-3], provider_source_class=pr['source_status'],
                    stock_kcfi_prefix_word=word, symbol_type=typ)
(REC / 'reference/provider-boundaries.json').write_text(json.dumps(bound, indent=2, sort_keys=True) + '\n')
(REC / 'reference/external-provider.symvers').write_text(''.join(
    f"{v['crc']}\t{s}\t{v['provider_module']}\t{v['licence']}\t{v['namespace']}\n" for s, v in sorted(bound.items())))
print('targets', len(rows), 'external boundaries', len(bound), 'providers', len({v['provider_module'] for v in bound.values()}))
