#!/usr/bin/env python3
"""Derive one family recipe's stock reference data from frozen stock operands.

  prepare-reference.py <recipe-repo> <dependency_group>[,<dependency_group>...]

Writes into <recipe>/reference/:
  BATCH-MANIFEST.tsv        the frozen manifest rows owned by this recipe (verbatim)
  stock-normalized.tsv      stock size/sha and GNU-build-ID-zeroed sha for each owned target
  provider-boundaries.json  every import not satisfied by GKI core or by a module owned by this
                            recipe: stock CRC, export bucket, namespace, symbol type and stock KCFI
                            prefix word, read from the stock *provider* module (never the consumer)
  external-provider.symvers the boundary in Module.symvers syntax; the build only emits a slot whose
                            CRC/licence/namespace/KCFI is reproduced by genuine compiled source, except
                            slots whose witness_class is STOCK_PROVIDER_EXPORT (ODM-private provider
                            without public source; canonical camera precedent, CAMERA-ISP-KERNEL)
Stock bytes are read from the canonical checkout (read-only); nothing is copied into the recipe.
"""
import csv, json, hashlib, struct, sys, importlib.util
from pathlib import Path

B = Path(__file__).resolve().parents[1]
R = B.parents[2]
CANON = R.parent / 'ulefone-gq5012bf1-research'
REC = Path(sys.argv[1]).resolve(); GROUPS = set(sys.argv[2].split(','))
sp = importlib.util.spec_from_file_location('norm', REC / 'scripts/normalize.py')
norm = importlib.util.module_from_spec(sp); sys.path.insert(0, str(REC / 'scripts')); sp.loader.exec_module(norm)
kpp = norm.kpp
# Provider modules with no public source: their export slots are STOCK_PROVIDER_EXPORT.
ODM_PRIVATE = {'yft_devinfo'}
allman = list(csv.DictReader((B / 'BATCH-MANIFEST.tsv').open(), delimiter='\t'))
man = [r for r in allman if r['dependency_group'] in GROUPS]
assert man and {r['dependency_group'] for r in man} == GROUPS
ids = {r['module_id'] for r in man}
allr = {r['module_id']: r for r in csv.DictReader((B / 'evidence/baseline/ALL-457-MODULES.tsv').open(), delimiter='\t')}
(REC / 'reference').mkdir(exist_ok=True)
with (REC / 'reference/BATCH-MANIFEST.tsv').open('w') as f:
    w = csv.DictWriter(f, fieldnames=list(allman[0]), delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(man)

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
    if e['consumer_module_id'] not in ids: continue
    ps = [p for p in e['provider_module_ids'].split(';') if p and p != 'GKI_CORE' and p not in ids]
    if not ps: continue
    # Several identical-CRC stock identities may exist (e.g. system_dlkm vs vendor_dlkm bluetooth.ko);
    # all are recorded, the first sorted identity is the CRC operand and every one must agree.
    old = need.setdefault(e['symbol'], (tuple(sorted(ps)), e['required_crc']))
    assert old == (tuple(sorted(ps)), e['required_crc']), ('inconsistent consumer CRC', e)

bound = {}
for s, (pids, crc) in sorted(need.items()):
    recs = []
    for pid in pids:
        pr = allr[pid]; ko = kpp.KO(str(CANON / pr['stock_paths'].split(';')[0]))
        crcsym = next(y for y in ko.syms if y['n'] == '__crc_' + s and 0 < y['shndx'] < len(ko.secs))
        sec = ko.secs[crcsym['shndx']]; val, = struct.unpack_from('<I', ko.b, sec['off'] + crcsym['val'])
        assert val == int(crc, 16), (s, hex(val), crc)
        lic = 'EXPORT_SYMBOL_GPL' if '_gpl' in sec['n'] else 'EXPORT_SYMBOL'
        sym = next(y for y in ko.syms if y['n'] == s and 0 < y['shndx'] < len(ko.secs))
        typ = sym['info'] & 15
        word = hex(struct.unpack_from('<I', ko.b, ko.secs[sym['shndx']]['off'] + sym['val'] - 4)[0]) if typ == 2 else None
        ns = next((y for y in ko.syms if y['n'] == '__kstrtabns_' + s and 0 < y['shndx'] < len(ko.secs)), None)
        namespace = ko.b[ko.secs[ns['shndx']]['off'] + ns['val']:].split(b'\0')[0].decode() if ns else ''
        recs.append(dict(crc=f'0x{val:08x}', licence=lic, namespace=namespace, provider_id=pid,
                         provider_module=pr['filename'][:-3], provider_source_class=pr['source_status'],
                         provider_in_batch=pid in {x['module_id'] for x in allman},
                         stock_kcfi_prefix_word=word, symbol_type=typ,
                         witness_class='STOCK_PROVIDER_EXPORT' if pr['filename'][:-3] in ODM_PRIVATE else 'SOURCE_WITNESS_REQUIRED'))
    first = dict(recs[0])
    for k in ('crc', 'licence', 'namespace', 'symbol_type', 'stock_kcfi_prefix_word'):
        assert all(x[k] == first[k] for x in recs), (s, k, recs)
    first['all_provider_ids'] = [x['provider_id'] for x in recs]
    bound[s] = first
(REC / 'reference/provider-boundaries.json').write_text(json.dumps(bound, indent=2, sort_keys=True) + '\n')
(REC / 'reference/external-provider.symvers').write_text(''.join(
    f"{v['crc']}\t{s}\t{v['provider_module']}\t{v['licence']}\t{v['namespace']}\n" for s, v in sorted(bound.items())))
cls = {}
for v in bound.values(): cls[v['witness_class']] = cls.get(v['witness_class'], 0) + 1
print('targets', len(rows), 'external boundaries', len(bound), 'providers', len({v['provider_module'] for v in bound.values()}), cls)
