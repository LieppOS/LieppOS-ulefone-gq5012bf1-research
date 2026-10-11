#!/usr/bin/env python3
"""Mutation tests: the validator must reject each class of unsupported audit claim."""
import copy
import json
import unittest
from inventory import AUDIT, read_table, scan
from validate import validate

ACTUAL = scan()
BASE = {name: read_table(AUDIT/name) for name in
        ['ALL-457-MODULES.tsv','SOURCE-GAPS.tsv','SOURCE-OWNERSHIP.tsv','RECONSTRUCTION-PROJECTS.tsv']}


def run(mutate):
    tables = copy.deepcopy(BASE)
    mutate(tables)
    return {e['code'] for e in validate(overrides=tables, actual=ACTUAL)['errors']}


def first(tables, status, name='ALL-457-MODULES.tsv'):
    return next(r for r in tables[name] if r['source_status'] == status)


def sync(tables, row):
    """Keep gap/ownership/project copies consistent so only the intended defect is tested."""
    for name in ['SOURCE-GAPS.tsv']:
        for i, r in enumerate(tables[name]):
            if r['module_id'] == row['module_id']:
                tables[name][i] = row


class ValidatorRejects(unittest.TestCase):
    def test_baseline_passes(self):
        self.assertEqual(run(lambda t: None), set())

    def test_missing_identity(self):
        self.assertIn('MISSING_IDENTITY', run(lambda t: t['ALL-457-MODULES.tsv'].pop()))

    def test_duplicate_identity(self):
        self.assertIn('DUPLICATE_IDENTITY', run(lambda t: t['ALL-457-MODULES.tsv'].append(dict(t['ALL-457-MODULES.tsv'][0]))))

    def test_omitted_stock_path(self):
        def m(t):
            row = next(r for r in t['ALL-457-MODULES.tsv'] if ';' in r['stock_paths'])
            row['stock_paths'] = row['stock_paths'].split(';')[0]
        self.assertIn('STOCK_PATHS_OMITTED_OR_DUPLICATED', run(m))

    def test_conflicting_owner(self):
        def m(t):
            t['SOURCE-OWNERSHIP.tsv'][0]['source_owner'] = 'SOMETHING-ELSE'
        self.assertIn('CONFLICTING_SOURCE_OWNERS', run(m))

    def test_duplicate_owner(self):
        self.assertIn('CONFLICTING_SOURCE_OWNERS', run(lambda t: t['SOURCE-OWNERSHIP.tsv'].append(dict(t['SOURCE-OWNERSHIP.tsv'][0]))))

    def test_invalid_status(self):
        def m(t): first(t, 'D')['source_status'] = 'Z'
        self.assertIn('INVALID_SOURCE_STATUS', run(m))

    def test_ab_without_parity(self):
        def m(t): first(t, 'A')['parity_evidence'] = 'UNKNOWN'
        self.assertIn('VERIFIED_WITHOUT_PARITY', run(m))

    def test_ab_without_pin_or_script(self):
        def m(t):
            r = first(t, 'A'); r['source_pin'] = 'UNKNOWN'; r['build_script'] = 'UNKNOWN'
        codes = run(m)
        self.assertIn('MISSING_SOURCE_PIN', codes)
        self.assertIn('MISSING_REPRODUCTION_SCRIPT', codes)

    def test_promoting_g_to_a_without_proof(self):
        def m(t):
            r = first(t, 'G'); r['source_status'] = 'A'
        codes = run(m)
        self.assertTrue({'SOURCE_REVIEW_CONFLICT', 'VERIFIED_WITHOUT_ABI_KCFI', 'VERIFIED_WITHOUT_CLEAN_BUILD'} & codes)

    def test_f_without_justification(self):
        def m(t):
            r = first(t, 'D'); r['source_status'] = 'F'; r['exclusion_justification'] = 'UNKNOWN'
        self.assertIn('EXCLUDED_WITHOUT_JUSTIFICATION', run(m))

    def test_stale_component(self):
        def m(t):
            r = next(r for r in t['ALL-457-MODULES.tsv'] if r['component_owner'] != 'COVERED-GENERIC')
            r['component_owner'] = 'NO-SUCH-COMPONENT'
        self.assertIn('STALE_COMPONENT_REFERENCE', run(m))

    def test_invalid_evidence_path(self):
        def m(t): first(t, 'A')['parity_evidence'] = 'reverse-engineering/does-not-exist.tsv'
        self.assertIn('INVALID_EVIDENCE_PATH', run(m))

    def test_dropping_gap_to_look_clean(self):
        self.assertIn('SOURCE_GAPS_COMPLEMENT', run(lambda t: t['SOURCE-GAPS.tsv'].pop()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
