#!/usr/bin/env python3
"""Read-only reconciliation of every extracted stock module occurrence."""
import collections
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'reverse-engineering/kernel-source-parity-audit'
WORKSPACE = ROOT.parent
STOCK_ROOTS = {
    'system_dlkm': ROOT / 'workspace/gq5012bf1/stock/partitions/system_dlkm',
    'vendor_dlkm': ROOT / 'workspace/gq5012bf1/stock/partitions/vendor_dlkm',
    'vendor_boot_platform': ROOT / 'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted',
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_table(path):
    with Path(path).open() as f:
        return list(csv.DictReader(f, delimiter='\t' if str(path).endswith('.tsv') else ','))

def scan():
    result = {}
    for partition, root in STOCK_ROOTS.items():
        assert root.is_dir(), root
        for path in sorted(root.rglob('*.ko')):
            digest = sha(path)
            identity = path.name + '@' + digest
            row = result.setdefault(identity, dict(module_id=identity, filename=path.name,
                stock_sha256=digest, stock_size=path.stat().st_size,
                stock_paths=[], partitions=[]))
            assert row['stock_size'] == path.stat().st_size
            row['stock_paths'].append(str(path.relative_to(ROOT)))
            row['partitions'].append(partition)
    for row in result.values():
        row['stock_paths'].sort()
        row['partitions'] = sorted(set(row['partitions']))
    return dict(sorted(result.items()))

def elf_metadata(path):
    spec = importlib.util.spec_from_file_location('audit_elf', ROOT / 'reverse-engineering/scripts/ko-pair-parity.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ko = mod.KO(str(path))
    imports, _ = mod.versions(ko)
    info = collections.defaultdict(list)
    for entry in ko.data('.modinfo').split(b'\0'):
        if b'=' in entry:
            key, val = entry.decode(errors='replace').split('=', 1)
            info[key].append(val)
    return dict(function_count=sum((s['info'] & 15) == 2 and s['size'] > 0 and s['shndx'] not in (0, 0xfff1) for s in ko.syms),
                data_count=sum((s['info'] & 15) == 1 and s['size'] > 0 and s['shndx'] not in (0, 0xfff1) for s in ko.syms),
                kcfi_abs_count=sum(s['n'].startswith('__kcfi_typeid_') for s in ko.syms),
                relocation_count=sum(s['size'] // 24 for s in ko.secs if s['type'] == 4),
                section_count=len(ko.secs), imports=imports,
                exports=[s['n'][len('__ksymtab_'):] for s in ko.syms if s['n'].startswith('__ksymtab_')],
                modinfo=dict(info))

if __name__ == '__main__':
    AUDIT.joinpath('evidence').mkdir(parents=True, exist_ok=True)
    actual = scan()
    old = read_table(ROOT / 'kernel/stock-module-master.csv')
    assert {(r['filename'], r['stock_sha256']) for r in actual.values()} == {(r['filename'], r['sha256']) for r in old}
    coverage = read_table(ROOT / 'reverse-engineering/coverage-audit/kernel-modules.tsv')
    assert {r['filename'] for r in actual.values()} == {r['module'] for r in coverage}
    for row in actual.values():
        row.update(elf_metadata(ROOT / row['stock_paths'][0]))
    report = dict(distinct_binary_identities=len(actual), unique_filenames=len({r['filename'] for r in actual.values()}),
                  occurrences=sum(len(r['stock_paths']) for r in actual.values()),
                  partition_occurrences=dict(collections.Counter(p for r in actual.values() for p in r['partitions'])),
                  duplicates={r['module_id']:r['stock_paths'] for r in actual.values() if len(r['stock_paths']) > 1},
                  filename_collisions={name:[r['module_id'] for r in actual.values() if r['filename']==name]
                      for name,n in collections.Counter(r['filename'] for r in actual.values()).items() if n>1},
                  recorded_master_identity_reconciliation='PASS', coverage_name_reconciliation='PASS')
    for name, data in [('stock-identities.json', actual), ('inventory-reconciliation.json', report)]:
        (AUDIT / 'evidence' / name).write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['duplicates']}, indent=2))
