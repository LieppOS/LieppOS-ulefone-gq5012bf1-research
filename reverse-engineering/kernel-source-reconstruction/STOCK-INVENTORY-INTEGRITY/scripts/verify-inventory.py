#!/usr/bin/env python3
"""Independent 458-identity / 471-occurrence stock inventory check (read-only).

usage: verify-inventory.py OPERAND_ROOT [--compare CANONICAL_ROOT] [--json OUT]

Expected values come only from the COMMITTED f61ebf03 blobs (git show), never from the
files being checked.  Every occurrence must exist at its committed path with the committed
size and SHA-256; nothing is normalized.  Signed system_dlkm modules must carry an intact
PKCS#7 appended-signature trailer.
"""
import argparse, collections, csv, hashlib, io, json, struct, subprocess, sys
from pathlib import Path

BASE = 'f61ebf03275ba2d3f6aa4f9d5aebe18e12922263'
MAGIC = b'~Module signature appended~\n'
ROOTS = {'system_dlkm': 'workspace/gq5012bf1/stock/partitions/system_dlkm',
         'vendor_dlkm': 'workspace/gq5012bf1/stock/partitions/vendor_dlkm',
         'vendor_boot_platform': 'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted'}
sha = lambda b: hashlib.sha256(b).hexdigest()

ap = argparse.ArgumentParser(); ap.add_argument('root', type=Path); ap.add_argument('--compare', type=Path); ap.add_argument('--json', type=Path)
ap.add_argument('--git-root', type=Path, help='repository providing the committed expectations (default: root)')
a = ap.parse_args(); root = a.root.resolve()
git = lambda p: subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=(a.git_root or root))
rows = list(csv.DictReader(io.StringIO(git('reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').decode()), delimiter='\t'))
frozen = json.loads(git('reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json'))
master = {(r['filename'], r['sha256']) for r in csv.DictReader(io.StringIO(git('kernel/stock-module-master.csv').decode()))}
own = list(csv.DictReader(io.StringIO(git('reverse-engineering/kernel-source-parity-audit/SOURCE-OWNERSHIP.tsv').decode()), delimiter='\t'))
errors = []; err = lambda c, m: errors.append(f'{c}: {m}')

ids = [r['module_id'] for r in rows]
if len(ids) != 458 or len(set(ids)) != 458: err('IDENTITY_COUNT', len(set(ids)))
if set(ids) != set(frozen): err('FROZEN_SET', 'audit vs stock-identities.json')
if {(r['filename'], r['stock_sha256']) for r in rows} != master: err('MASTER_SET', 'audit vs stock-module-master.csv')
if sorted(r['module_id'] for r in own) != sorted(ids): err('OWNERSHIP_SET', 'SOURCE-OWNERSHIP.tsv')
occ = []; part_occ = collections.Counter(); sig = collections.Counter(); per_path = {}
for r in rows:
    if r['module_id'] != r['filename'] + '@' + r['stock_sha256']: err('IDENTITY_KEY', r['module_id'])
    f = frozen[r['module_id']]
    if f['stock_sha256'] != r['stock_sha256'] or int(f['stock_size']) != int(r['stock_size']) or sorted(f['stock_paths']) != sorted(r['stock_paths'].split(';')):
        err('FROZEN_ROW', r['module_id'])
    for p in r['stock_paths'].split(';'):
        part = next(k for k, v in ROOTS.items() if p.startswith(v + '/'))
        if part not in r['partitions'].split(';'): err('PARTITION_ASSIGNMENT', p)
        part_occ[part] += 1; occ.append(p)
        f2 = root / p
        if not f2.is_file() or f2.is_symlink(): err('MISSING_OCCURRENCE', p); continue
        b = f2.read_bytes(); per_path[p] = sha(b)
        if len(b) != int(r['stock_size']): err('SIZE', f'{p} {len(b)} != {r["stock_size"]}')
        if sha(b) != r['stock_sha256']: err('SHA256', f'{p} {sha(b)} != {r["stock_sha256"]}')
        if part == 'system_dlkm':
            ok = b.endswith(MAGIC) and b[-len(MAGIC) - 12 + 2] == 2 and struct.unpack('>I', b[-len(MAGIC) - 4:-len(MAGIC)])[0] + 40 == 721
            sig['system_dlkm_signed_721' if ok else 'system_dlkm_BAD_SIGNATURE'] += 1
            if not ok: err('SIGNATURE_TRAILER', p)
        else:
            sig[part + ('_signed' if b.endswith(MAGIC) else '_unsigned')] += 1
on_disk = sorted(str(p.relative_to(root)) for v in ROOTS.values() for p in (root / v).rglob('*.ko'))
if sorted(occ) != on_disk: err('PATH_SET', f'{len(set(on_disk) - set(occ))} unlisted, {len(set(occ) - set(on_disk))} absent')
if len(occ) != 471 or len(set(occ)) != 471: err('OCCURRENCE_COUNT', len(occ))
if dict(part_occ) != {'system_dlkm': 60, 'vendor_dlkm': 215, 'vendor_boot_platform': 196}: err('PARTITION_COUNTS', dict(part_occ))
names = collections.Counter(r['filename'] for r in rows)
collisions = {n: sorted(r['partitions'] for r in rows if r['filename'] == n) for n, c in names.items() if c > 1}
if collisions != {'bluetooth.ko': ['system_dlkm', 'vendor_dlkm']}: err('FILENAME_COLLISIONS', collisions)
diff_vs_compare = None
if a.compare:
    c = a.compare.resolve()
    diff_vs_compare = sorted(p for p in occ if (c / p).is_file() and sha((c / p).read_bytes()) != per_path.get(p))
out = dict(operand_root=str(root), expected_from=f'git {BASE}', identities=len(set(ids)), occurrences=len(occ), unique_filenames=len(names),
           partition_occurrences=dict(part_occ), filename_collisions=collisions, signature_census=dict(sig),
           occurrences_matching_committed_sha_and_size=sum(1 for r in rows for p in r['stock_paths'].split(';') if per_path.get(p) == r['stock_sha256']),
           differs_from_compare_root=diff_vs_compare, errors=errors, result='PASS' if not errors else 'FAIL')
text = json.dumps(out, indent=2) + '\n'
brief = {k: v for k, v in out.items() if k not in ('errors', 'differs_from_compare_root')}
brief['error_count'] = len(errors); brief['error_kinds'] = dict(collections.Counter(e.split(':')[0] for e in errors))
brief['differs_from_compare_root_count'] = None if diff_vs_compare is None else len(diff_vs_compare)
print(json.dumps(brief, indent=2))
if a.json: a.json.write_text(text)
sys.exit(1 if errors else 0)
