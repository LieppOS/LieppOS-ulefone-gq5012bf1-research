#!/usr/bin/env python3
"""Check retained closure artifacts, not certify the five C targets or live audit.
Uses actual committed-source build files when available. No phone/source/stock/audit
mutation; writes only this research directory's explicit verification report/log.
"""
import argparse
import ast
import csv
import hashlib
import json
import lzma
import os
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[3]
CANONICAL = ROOT / 'ulefone-gq5012bf1-research'
EXPECTED = {'charger_class', 'mtk_chg_type_det', 'rt_pd_manager', 'tcpc_mt6375', 'tcpc_class'}
SHA = lambda data: hashlib.sha256(data).hexdigest()


def table(path):
    with path.open() as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)
        assert all(None not in row and all(v is not None for v in row.values()) for row in rows), path
        return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof-root', type=Path,
                        default=Path('/home/armol/kernel-work/usb-typec-closure-proof-debugmapped'))
    args = parser.parse_args()
    required = ['CLOSURE-SUMMARY.md', 'MODULE-PARITY.tsv', 'SRCVERSION-INVESTIGATION.md',
                'TCPC-METADATA-INVESTIGATION.md', 'TCPC-CLASS-FUNCTION-DIFFS.md',
                'SOURCE-LINEAGE.md', 'EXPERIMENTS.tsv', 'BLOCKERS.tsv',
                'BUILD-REPRODUCTION.md', 'AUDIT-DELTA.tsv', 'MERGE-INSTRUCTIONS.md']
    for name in required:
        assert (P / name).is_file(), name
    scripts = list((P / 'scripts').glob('*.py'))
    for path in scripts:
        ast.parse(path.read_text(), filename=str(path))

    state = json.loads((P / 'STATE.json').read_text())
    summary = json.loads((P / 'evidence/final/full-acceptance/summary.json').read_text())
    parity = {row['module']: row for row in table(P / 'MODULE-PARITY.tsv')}
    frozen = {row['module_id']: row for row in table(P / 'evidence/baseline/ALL-458-MODULES.tsv')}
    assert len(frozen) == 458 and len(summary) == 5 and set(parity) == EXPECTED
    assert not state['mission_complete'] and state['newly_certified'] == 0
    for row in summary:
        module = row['module']
        assert row['original_class'] == row['final_class'] == parity[module]['final_class'] == 'C'
        assert row['strict_stock_verifier_exit'] != 0 and not row['whole_permitted_stock_parity']
        assert row['module_id'] == parity[module]['module_id']
        for name, actual in [('exact_functions', row['axes']['functions']['body_and_position_exact']),
                             ('stock_functions', row['axes']['functions']['stock_count']),
                             ('exact_data_objects', row['axes']['data']['body_and_position_exact']),
                             ('stock_data_objects', row['axes']['data']['stock_count'])]:
            assert int(parity[module][name]) == actual, (module, name)
        for name in ['section_layout_exact', 'raw_relocations_exact', 'semantic_relocations_exact',
                     'import_crc_exact', 'whole_permitted_stock_parity']:
            assert parity[module][name] == str(row[name]).lower(), (module, name)
        assert row['import_crc_exact'] and row['export_crc_and_license_exact'] and row['kcfi_abs_exact']
        assert parity[module]['export_crc_license_exact'] == parity[module]['kcfi_exact'] == 'true'
        assert all(not b['stock_present'] and not b['source_present'] for b in row['btf'].values())
        assert (P / parity[module]['evidence']).is_dir()
        base = frozen[row['module_id']]
        assert base['source_status'] == 'C' and base['stock_sha256'] == row['stock_sha256']
        for relative in base['stock_paths'].split(';'):
            assert SHA((CANONICAL / relative).read_bytes()) == row['stock_sha256'], relative

    for name, evidence_field in [('EXPERIMENTS.tsv', 'retained_evidence'), ('BLOCKERS.tsv', 'evidence')]:
        for row in table(P / name):
            assert (P / row[evidence_field]).exists(), row
    delta = table(P / 'AUDIT-DELTA.tsv')
    assert len(delta) == 22
    assert {r['module_id'] for r in delta} == {r['module_id'] for r in summary}
    assert not any(r['field'] in ['source_status', 'runtime_status', 'component_owner', 'source_owner'] for r in delta)
    audit = json.loads((P / 'evidence/audit-delta.json').read_text())
    assert audit['newly_certified'] == 0 and not audit['live_audit_edited']
    assert SHA((CANONICAL / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').read_bytes()) == audit['canonical_audit_sha256']

    operands = json.loads((P / 'evidence/compiled-operands/manifest.json').read_text())
    assert len(operands) == 60
    assert len({(r['stage'], r['module'], r['form']) for r in operands}) == 60
    for row in operands:
        packed = (P / row['file']).read_bytes()
        assert SHA(packed) == row['archive_sha256']
        raw = lzma.decompress(packed)
        assert len(raw) == row['bytes'] and SHA(raw) == row['sha256'], row['file']
    for row in summary:
        compiled = next(r for r in operands if r['stage'] == 'final' and r['module'] == row['module'] and r['form'] == '.stripped')
        assert compiled['sha256'] == row['source_sha256'], row['module']

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    proc = subprocess.run(['python3', str(P / 'scripts/validate-cleancheck.py'), str(args.proof_root)],
                          capture_output=True, text=True, env=env)
    (P / 'evidence/final-independent-revalidation.log').write_text(proc.stdout + proc.stderr)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    proof = json.loads((P / 'evidence/fresh-clones/result.json').read_text())
    assert proof['all_30_raw_and_stripped_modules_deterministic']
    assert proof['all_157_actual_intermediate_objects_deterministic']
    assert proof['readonly_mirror_unchanged'] and len(proof['runs']) == 4
    for repo_name, commit in [('android_kernel_modules_usb_typec_ulefone_gq5012bf1-usb-typec-closure', state['typec_commit']),
                              ('android_kernel_modules_charging_battery_ulefone_gq5012bf1-usb-typec-closure', state['charging_commit'])]:
        repo = ROOT / repo_name
        assert subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip() == commit
        assert not subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'], text=True).strip()
        for bundle in (P / 'evidence/bundles').glob(repo_name.removesuffix('-usb-typec-closure') + '*.bundle'):
            p = subprocess.run(['git', '-C', str(repo), 'bundle', 'verify', str(bundle)], capture_output=True, text=True)
            assert p.returncode == 0, p.stderr
    mutations = json.loads((P / 'evidence/mutation-tests/result.json').read_text())
    assert mutations['all_pass'] and mutations['count'] == 23
    live = json.loads((P / 'evidence/audit-validation/baseline-result.json').read_text())
    assert live['result'] == 'FAIL' and live['errors']
    assert state['integration_blocked']
    result = {'result': 'PASS_RETAINED_EVIDENCE_ONLY_FULL_CLOSURE_BLOCKED',
              'required_deliverables': len(required), 'python_scripts_syntax_checked': len(scripts),
              'selected_stock_identities_sha_verified': 5, 'all_five_remain_C': True,
              'parity_tables_match_actual_ledgers': True, 'compressed_operands_verified': 60,
              'fresh_source_builds_actual_files_revalidated': 4,
              'raw_and_stripped_modules_byte_identical': 30, 'intermediate_objects_byte_identical': 157,
              'source_worktrees_clean_and_bundle_verified': True, 'elf_mutation_tests_pass': 23,
              'canonical_audit_byte_unchanged': True, 'unapplied_field_delta_entries': 22,
              'live_canonical_validator': 'FAIL_UNRELATED_STOCK_IDENTITY_DRIFT',
              'integration_blocked': True, 'newly_certified': 0,
              'no_live_audit_or_module_acceptance_waiver': True}
    (P / 'evidence/final-validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
