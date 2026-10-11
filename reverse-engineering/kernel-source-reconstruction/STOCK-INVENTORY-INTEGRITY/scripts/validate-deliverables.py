#!/usr/bin/env python3
"""Cross-check the STOCK-INVENTORY-INTEGRITY deliverables against each other and the committed baseline (read-only)."""
import csv, hashlib, io, json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]; R = P.parents[2]
BASE = 'f61ebf03275ba2d3f6aa4f9d5aebe18e12922263'
def ok(c, m):
    if not c: sys.exit('INVALID: ' + m)
tsv = lambda n: list(csv.DictReader((P / n).open(), delimiter='\t'))
for n in ['ROOT-CAUSE.md', 'MISSING-IDENTITIES.tsv', 'UNEXPECTED-IDENTITIES.tsv', 'EXPECTED-VS-OBSERVED.tsv', 'STOCK-OPERAND-PROVENANCE.md',
          'SIGNATURE-ANALYSIS.md', 'REPAIR-MANIFEST.tsv', 'VALIDATION-BEFORE-AFTER.md', 'REGRESSION-TESTS.md', 'USB-CLOSURE-REVALIDATION.md', 'MERGE-INSTRUCTIONS.md']:
    ok((P / n).stat().st_size > 1000, 'missing/placeholder ' + n)
audit_now = (R / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').read_bytes()
audit_base = subprocess.check_output(['git', 'show', f'{BASE}:reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'], cwd=R)
ok(audit_now == audit_base, 'canonical audit changed on this branch')
ok(subprocess.run(['git', 'diff', '--quiet', BASE, '--', 'reverse-engineering/kernel-source-parity-audit', 'kernel/stock-module-master.csv'], cwd=R).returncode == 0, 'audit dir changed')
rows = {r['module_id']: r for r in csv.DictReader(io.StringIO(audit_base.decode()), delimiter='\t')}
before = json.loads((P / 'evidence/before/validator.stdout.json').read_text())
mi, un, ev, rm = tsv('MISSING-IDENTITIES.tsv'), tsv('UNEXPECTED-IDENTITIES.tsv'), tsv('EXPECTED-VS-OBSERVED.tsv'), tsv('REPAIR-MANIFEST.tsv')
ok(sorted(r['module_identity_key'] for r in mi) == sorted(e['message'] for e in before['errors'] if e['code'] == 'MISSING_IDENTITY'), 'missing table')
ok(sorted(r['module_identity_key'] for r in un) == sorted(e['message'] for e in before['errors'] if e['code'] == 'UNEXPECTED_IDENTITY'), 'unexpected table')
ok(len(mi) == len(un) == len(ev) == len(rm) == 60, 'row counts')
for e in ev:
    r = rows[e['module_identity_key']]
    ok(e['expected_sha256'] == r['stock_sha256'] and int(e['expected_size']) == int(r['stock_size']) and e['relative_path'] == r['stock_paths'], 'expected values ' + e['filename'])
    ok(int(e['size_delta']) == 721 and e['image_member_equals_expected'] == 'True' and e['observed_equals_image_unsigned_prefix'] == 'True', 'strip proof ' + e['filename'])
for m in rm:
    ok(m['action'] == 'RESTORED' and m['state'] == 'SIGNATURE_STRIPPED' and m['after_sha256'] == m['expected_sha256'] == rows[m['module_id']]['stock_sha256'], 'repair ' + m['filename'])
    ok(m['before_sha256'] == next(e['observed_sha256'] for e in ev if e['module_identity_key'] == m['module_id']), 'repair before ' + m['filename'])
after = json.loads((P / 'evidence/after/validator.stdout.json').read_text())
ok(after['errors'] == [] and after['distinct_stock_identities'] == 458 and after['stock_occurrences'] == 471, 'after validator')
ok((P / 'evidence/after/validator.exit').read_text().strip() == 'exit=0' and (P / 'evidence/after/mutation-tests.exit').read_text().strip() == 'exit=0', 'after exits')
inv = json.loads((P / 'evidence/after/verify-inventory-isolated.json').read_text())
ok(inv['result'] == 'PASS' and inv['occurrences_matching_committed_sha_and_size'] == 471 and sorted(inv['differs_from_compare_root']) == sorted(m['destination'] for m in rm), 'inventory')
reg = (P / 'evidence/regression/regression-tests.log').read_text()
ok('Ran 11 tests' in reg and '\nOK\n' in reg and 'exit=0' in reg, 'regression tests')
usb = json.loads((P / 'evidence/usb-closure/revalidation.json').read_text())
ok(usb['result'].startswith('PASS') and usb['newly_certified'] == 0 and usb['five_targets']['tcpc_class']['functions'] == '709/709'
   and all(v['accepted'] == 25 for v in usb['strict_acceptance'].values()) and not usb['audit_delta']['applied'], 'usb closure')
dry = list(csv.DictReader((P / 'evidence/repair/canonical-dry-run.tsv').open(), delimiter='\t'))
ok(len(dry) == 60 and all(d['action'] == 'WOULD_RESTORE' for d in dry), 'canonical dry run')
print('STOCK-INVENTORY-INTEGRITY VALID: 60/60 reproduced and explained; 60 isolated restorations; after 458/471, 0 errors; audit untouched; USB closure 25A/5C, 0 new')
