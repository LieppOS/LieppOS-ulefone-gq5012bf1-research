#!/usr/bin/env python3
"""Read-only forensic comparison of the 60/60 stock identity mismatch.

usage: analyze-drift.py CANONICAL_ROOT VALIDATOR_JSON IMAGE_EXTRACT_DIR OUT_DIR

Reads (never writes) the canonical checkout, its stock workspace, the committed
PLATFORM-BATCH-04 drift evidence, the Batch04 quarantine and an independent
read-only extraction of the authenticated system_dlkm_a.img.  Writes only OUT_DIR.
"""
import csv, hashlib, json, struct, subprocess, sys
from pathlib import Path

C, VJ, X, OUT = (Path(a) for a in sys.argv[1:5])
MAGIC = b'~Module signature appended~\n'
B4 = C / 'reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-04/evidence/stock-operand-drift'
B4Q = Path('/home/armol/kernel-work/platform-batch-04-unsigned-stock-quarantine')
sha = lambda b: hashlib.sha256(b).hexdigest()

def sig(b):
    """Parse the kernel appended-signature trailer (include/linux/module_signature.h)."""
    if not b.endswith(MAGIC):
        return dict(present=False)
    algo, hsh, id_type, signer_len, key_id_len, p0, p1, p2, sig_len = struct.unpack('>BBBBBBBBI', b[-len(MAGIC) - 12:-len(MAGIC)])
    total = sig_len + 12 + len(MAGIC)
    start = len(b) - total
    return dict(present=True, id_type=id_type, id_type_name={2: 'PKEY_ID_PKCS7'}.get(id_type, str(id_type)),
                algo=algo, hash=hsh, signer_len=signer_len, key_id_len=key_id_len, sig_len=sig_len,
                trailer_bytes=total, unsigned_len=start, pkcs7_sha256=sha(b[start:start + sig_len]),
                pkcs7_der_starts_0x30=b[start] == 0x30)

def elf_end(b):
    """Largest byte covered by the ELF header, program/section header tables and section contents."""
    shoff, = struct.unpack_from('<Q', b, 0x28); shentsize, shnum = struct.unpack_from('<HH', b, 0x3a)
    end = shoff + shentsize * shnum
    for i in range(shnum):
        o = shoff + i * shentsize
        typ, = struct.unpack_from('<I', b, o + 4); off, size = struct.unpack_from('<QQ', b, o + 0x18)
        if typ != 8:  # SHT_NOBITS occupies no file bytes
            end = max(end, off + size)
    return end

rows = {r['module_id']: r for r in csv.DictReader((C / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').open(), delimiter='\t')}
frozen = json.loads((C / 'reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json').read_text())
master = {(r['filename'], r['sha256']) for r in csv.DictReader((C / 'kernel/stock-module-master.csv').open())}
res = json.loads(VJ.read_text())
missing = [e['message'] for e in res['errors'] if e['code'] == 'MISSING_IDENTITY']
unexpected = [e['message'] for e in res['errors'] if e['code'] == 'UNEXPECTED_IDENTITY']
b4rest = {c['destination']: c for c in json.loads((B4 / 'restoration-result.json').read_text())['changes']}
b4before = {e['message'] for e in json.loads((B4 / 'validator-before-restoration.json').read_text())['errors'] if e['code'] == 'MISSING_IDENTITY'}
b4unexp = {e['message'] for e in json.loads((B4 / 'validator-before-restoration.json').read_text())['errors'] if e['code'] == 'UNEXPECTED_IDENTITY'}

by_path = {}
for u in unexpected:
    r = rows[u]
    paths = r['stock_paths'].split(';')
    assert len(paths) == 1, u
    by_path[paths[0]] = r
pairs = []
for m in missing:
    name, digest = m.split('@')
    hits = [p for p, r in by_path.items() if r['filename'] == name and sha((C / p).read_bytes()) == digest]
    assert len(hits) == 1, m
    pairs.append((m, by_path[hits[0]], hits[0]))
assert len(pairs) == len(missing) == len(unexpected) == 60 and len({p[2] for p in pairs}) == 60

table = []
for observed_id, r, rel in sorted(pairs, key=lambda x: x[1]['filename']):
    obs = (C / rel).read_bytes()
    img_member = X / Path(rel).relative_to('workspace/gq5012bf1/stock/partitions/system_dlkm')
    img = img_member.read_bytes()
    s = sig(img)
    q = B4Q / r['filename']
    qb = q.read_bytes() if q.is_file() else None
    b4 = b4rest.get(rel, {})
    table.append(dict(
        module_identity_key=r['module_id'], observed_identity_key=observed_id,
        stock_partition=r['partitions'], relative_path=rel, filename=r['filename'],
        expected_size=int(r['stock_size']), observed_size=len(obs), size_delta=int(r['stock_size']) - len(obs),
        expected_sha256=r['stock_sha256'], observed_sha256=sha(obs),
        expected_in_frozen_inventory=frozen.get(r['module_id'], {}).get('stock_sha256') == r['stock_sha256'],
        expected_in_stock_module_master=(r['filename'], r['stock_sha256']) in master,
        image_member=str(img_member.relative_to(X)), image_member_size=len(img), image_member_sha256=sha(img),
        image_member_equals_expected=sha(img) == r['stock_sha256'] and len(img) == int(r['stock_size']),
        signature_present_in_image=s['present'], signature_trailer_bytes=s.get('trailer_bytes'),
        signature_id_type=s.get('id_type_name'), pkcs7_len=s.get('sig_len'), pkcs7_sha256=s.get('pkcs7_sha256'),
        image_elf_end=elf_end(img), observed_elf_end=elf_end(obs),
        unsigned_prefix_sha256=sha(img[:s['unsigned_len']]) if s['present'] else None,
        observed_equals_image_unsigned_prefix=s['present'] and obs == img[:s['unsigned_len']],
        observed_has_signature=sig(obs)['present'],
        same_as_batch04_before=b4.get('before_sha256') == sha(obs) and b4.get('before_size') == len(obs),
        same_as_batch04_after=b4.get('after_sha256') == r['stock_sha256'],
        same_as_batch04_quarantine=qb is not None and sha(qb) == sha(obs),
        observed_id_in_batch04_validator_failure=observed_id in b4before,
        expected_id_in_batch04_validator_failure=r['module_id'] in b4unexp,
        source_of_expected='ALL-457-MODULES.tsv@f61ebf03 + evidence/stock-identities.json + kernel/stock-module-master.csv',
        evidence_of_observed='sha256 of CANONICAL_ROOT/' + rel + ' (read-only)'))

OUT.mkdir(parents=True, exist_ok=True)
cols = list(table[0])
def write(name, records, fields):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fields, delimiter='\t', lineterminator='\n', extrasaction='ignore'); w.writeheader(); w.writerows(records)
base = ['stock_partition', 'relative_path', 'filename', 'expected_size', 'observed_size', 'expected_sha256', 'observed_sha256', 'source_of_expected', 'evidence_of_observed']
write('MISSING-IDENTITIES.tsv', [dict(t, validator_code='MISSING_IDENTITY', module_identity_key=t['observed_identity_key'], paired_audit_identity=t['module_identity_key']) for t in table],
      ['validator_code', 'module_identity_key', 'paired_audit_identity'] + base)
write('UNEXPECTED-IDENTITIES.tsv', [dict(t, validator_code='UNEXPECTED_IDENTITY', paired_observed_identity=t['observed_identity_key']) for t in table],
      ['validator_code', 'module_identity_key', 'paired_observed_identity'] + base)
write('EXPECTED-VS-OBSERVED.tsv', table, cols)
summary = dict(
    pairs=len(table),
    one_to_one_by_path=True,
    partitions=sorted({t['stock_partition'] for t in table}),
    size_deltas=sorted({t['size_delta'] for t in table}),
    signature_trailer_bytes=sorted({t['signature_trailer_bytes'] for t in table}),
    pkcs7_lengths=sorted({t['pkcs7_len'] for t in table}),
    distinct_pkcs7_blobs=len({t['pkcs7_sha256'] for t in table}),
    all_expected_consistent=all(t['expected_in_frozen_inventory'] and t['expected_in_stock_module_master'] for t in table),
    all_image_members_equal_expected=all(t['image_member_equals_expected'] for t in table),
    all_observed_equal_unsigned_prefix=all(t['observed_equals_image_unsigned_prefix'] for t in table),
    all_observed_unsigned=not any(t['observed_has_signature'] for t in table),
    elf_content_ends_at_unsigned_prefix=all(t['image_elf_end'] == t['observed_size'] for t in table),
    same_files_as_batch04_incident=all(t['same_as_batch04_before'] and t['same_as_batch04_after'] for t in table),
    same_bytes_as_batch04_quarantine=all(t['same_as_batch04_quarantine'] for t in table),
    same_validator_identities_as_batch04_failure=all(t['observed_id_in_batch04_validator_failure'] and t['expected_id_in_batch04_validator_failure'] for t in table),
    image_kos=len(list(X.rglob('*.ko'))))
(OUT / 'evidence').mkdir(exist_ok=True)
(OUT / 'evidence/drift-analysis-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
