#!/usr/bin/env python3
"""Read-only ELF ABI graph; copies stock only into own immutable reference set.
Never calls objcopy, strip, firmware, phone, or rewrites canonical stock/audit.
"""
from pathlib import Path
import csv, hashlib, importlib.util, json, struct, collections

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[3]
R = ROOT / 'ulefone-gq5012bf1-research'
W = Path('/home/armol/kernel-work/codex-audio-dependencies-batch-02')
S = W / 'stock-identities'
S.mkdir(exist_ok=True)
TOOLS = W / 'audio-tools/scripts'
spec = importlib.util.spec_from_file_location('kpp', TOOLS / 'ko-pair-parity.py')
kpp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kpp)
read = lambda p: list(csv.DictReader(p.open(), delimiter='\t'))
sha = lambda b: hashlib.sha256(b).hexdigest()
rows = read(R / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv')
byid = {r['module_id']: r for r in rows}
assert len(byid) == 458
manifest = read(P / 'evidence/foundation/audio-BATCH-MANIFEST.tsv')
audio_ids = {r['module_id'] for r in manifest}
assert len(audio_ids) == 21
pending = {}
for worktree, batch in [('ulefone-gq5012bf1-research-codex-audio', 'AUDIO-BATCH-01'),
                        ('ulefone-gq5012bf1-research-codex-connectivity', 'SCP-CONNECTIVITY-BATCH-01')]:
    base = ROOT / worktree / 'reverse-engineering/kernel-source-reconstruction' / batch
    mm = {r['filename']: r['module_id'] for r in read(base / 'BATCH-MANIFEST.tsv')}
    for r in read(base / 'BATCH-PARITY.tsv'):
        pending[mm[r['module']]] = r

exports = collections.defaultdict(list)
imports = {}
provenance_path = P / 'evidence/private-stock-provenance.json'
provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else []
for row in rows:
    target = S / (row['filename'] + '.' + row['stock_sha256'])
    if not target.exists():
        candidates = [R / p for p in row['stock_paths'].split(';')]
        candidates.append(Path('/home/armol/kernel-work/codex-inventory-integrity/extract-system_dlkm/lib/modules') / row['filename'])
        source = next((p for p in candidates if p.is_file() and sha(p.read_bytes()) == row['stock_sha256']), None)
        assert source, ('no authentic stock identity', row['module_id'])
        target.write_bytes(source.read_bytes())
        target.chmod(0o444)
        provenance.append({'module_id': row['module_id'], 'source': str(source), 'private_copy': str(target), 'sha256': row['stock_sha256']})
    assert sha(target.read_bytes()) == row['stock_sha256']
    ko = kpp.KO(target)
    versions, _ = kpp.versions(ko)
    imports[row['module_id']] = versions
    symbols = {s['n']: s for s in ko.syms}
    for y in ko.syms:
        if not y['n'].startswith('__crc_') or not 0 < y['shndx'] < len(ko.secs):
            continue
        sec = ko.secs[y['shndx']]
        if 'kcrctab' not in sec['n']:
            continue
        name = y['n'][6:]
        crc, = struct.unpack_from('<I', ko.b, sec['off'] + y['val'])
        license = 'EXPORT_SYMBOL_GPL' if '_gpl' in sec['n'] else 'EXPORT_SYMBOL'
        ns = symbols.get('__kstrtabns_' + name)
        namespace = ko.cstr(ko.secs[ns['shndx']]['off'] + ns['val']) if ns and 0 < ns['shndx'] < len(ko.secs) else 'UNKNOWN'
        symbol = symbols.get(name)
        prefix = 'NOT_FUNCTION_OR_UNAVAILABLE'
        if symbol and symbol['info'] & 15 == 2 and 0 < symbol['shndx'] < len(ko.secs) and symbol['val'] >= 4:
            offset = ko.secs[symbol['shndx']]['off'] + symbol['val'] - 4
            prefix = ko.b[offset:offset + 4].hex()
        exports[name].append({'provider_id': row['module_id'], 'crc': crc, 'license': license,
                              'namespace': namespace, 'type': symbol['info'] & 15 if symbol else 'UNKNOWN',
                              'kcfi_prefix': prefix})
core = W / 'audio-tools/reference/gki-12901745-vmlinux.symvers.xz'
import lzma
for line in lzma.decompress(core.read_bytes()).decode().splitlines():
    f = line.split('\t')
    assert len(f) >= 4
    exports[f[1]].append({'provider_id': 'GKI_CORE', 'crc': int(f[0], 16), 'license': f[3],
                          'namespace': f[4] if len(f) > 4 else '', 'type': 'UNKNOWN', 'kcfi_prefix': 'UNKNOWN'})

witnesses = {r['symbol']: r for r in read(P / 'evidence/foundation/audio-PROVIDER-BOUNDARIES.tsv')}
headers = ['consumer_module_id', 'consumer', 'symbol', 'required_crc', 'provider_module_id', 'provider',
           'canonical_class', 'pending_class', 'export_crc', 'export_license', 'namespace', 'symbol_type',
           'stock_provider_kcfi_prefix', 'kcfi_compatibility_evidence', 'source_owner', 'source_repository',
           'source_commit', 'source_location', 'runtime_load_evidence', 'complete_provider_source_certified',
           'edge_kind', 'resolution', 'nonmatching_provider_candidates']
graph = []
adjacency = collections.defaultdict(set)
for consumer, symbols in imports.items():
    for symbol, required in sorted(symbols.items()):
        candidates = exports.get(symbol, [])
        matches = [r for r in candidates if r['crc'] == required]
        assert matches, ('unresolved stock import', consumer, symbol, hex(required))
        for provider in matches:
            pid = provider['provider_id']
            if pid != 'GKI_CORE':
                adjacency[consumer].add(pid)
            pr = byid.get(pid, {})
            pp = pending.get(pid, {})
            witness = witnesses.get(symbol)
            kcfi = 'UNKNOWN_CALLSITE_TYPE_NOT_PROVEN_BY_CRC'
            if witness and witness['provider_module'] + '.ko' == pr.get('filename') and witness['result'] == 'MATCH':
                kcfi = 'AUDIO_SOURCE_WITNESS_PREFIX_MATCH;CALLSITE_CRC_NOT_TYPE_PROOF'
            elif pr.get('source_status') in ['A', 'B'] or pp.get('final_class') == 'A':
                kcfi = 'COMPLETE_PROVIDER_PARITY_EVIDENCE;CALLSITE_TYPE_NOT_INFERRED'
            graph.append(dict(zip(headers, [consumer, byid[consumer]['filename'], symbol, f'0x{required:08x}', pid,
                pr.get('filename', 'GKI_CORE'), pr.get('source_status', 'PINNED_GKI_CORE'), pp.get('final_class', 'NONE'),
                f"0x{provider['crc']:08x}", provider['license'], provider['namespace'], provider['type'], provider['kcfi_prefix'],
                kcfi, pr.get('source_owner', 'GKI_COMMON'), pp.get('source_repository', pr.get('source_repo', 'kernel/common')),
                pp.get('source_commit', pr.get('source_commit', '6b18f0b574ab3267615ae6ce642d5aebe18e12922263')),
                pr.get('candidate_path', 'PINNED_GKI_COMMON'), pr.get('load_phase', 'BUILTIN') + ':' + pr.get('load_order', ''),
                'CANONICAL' if pr.get('source_status') in ['A', 'B'] else ('PENDING_UNMERGED' if pp.get('final_class') == 'A' else 'NO'),
                'DIRECT_ELF_IMPORT', 'CRC_MATCH' if len(matches) == 1 else 'MULTIPLE_CRC_MATCHES',
                ';'.join(r['provider_id'] for r in candidates if r['crc'] != required) or 'NONE'])))

def write(path, rows, fields):
    with path.open('w') as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(rows)

write(P / 'AUDIO-DEPENDENCY-GRAPH.tsv', [r for r in graph if r['consumer_module_id'] in audio_ids], headers)
write(P / 'evidence/all-module-abi-graph.tsv', graph, headers)
reachable = set(audio_ids)
while True:
    expanded = reachable | {p for c in reachable for p in adjacency[c]}
    if expanded == reachable:
        break
    reachable = expanded
eligible = sorted(pid for pid in reachable - audio_ids if pid not in pending and byid[pid]['source_status'] not in ['A', 'B', 'C'])
report = {'identities': len(rows), 'audio_consumers': len(audio_ids), 'direct_audio_import_edges': sum(r['consumer_module_id'] in audio_ids for r in graph),
          'direct_audio_provider_identities': sorted({r['provider_module_id'] for r in graph if r['consumer_module_id'] in audio_ids}),
          'reachable_module_identities': len(reachable), 'eligible_reachable_uncertified': [byid[p] for p in eligible],
          'pending_assigned_scopes_excluded': len(pending), 'no_stock_operand_modified': True,
          'core_symvers_sha256': sha(lzma.decompress(core.read_bytes()))}
(P / 'evidence/graph-selection.json').write_text(json.dumps(report, indent=2) + '\n')
(P / 'evidence/private-stock-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
print('Audio ABI edges', report['direct_audio_import_edges'], 'reachable modules', len(reachable))
print('Eligible reachable uncertified:', [(byid[p]['filename'], byid[p]['source_status'], byid[p]['source_owner']) for p in eligible])
