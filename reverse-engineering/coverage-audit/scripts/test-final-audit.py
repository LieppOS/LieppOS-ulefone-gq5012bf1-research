#!/usr/bin/env python3
"""Regression tests for final audit corrections; never modify real audit tables."""
import copy
import importlib.util
import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load(filename, name):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reports = load("build-reports.py", "audit_reports")
checks = load("check-audit.py", "audit_checks")


class FinalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics = reports.metrics()
        cls.tables = {p.name: checks.rows(p.name) for p in checks.CA.glob("*.tsv")}

    def test_completed_targets_are_not_ranked(self):
        m = copy.deepcopy(self.metrics)
        for r in m["components"]:
            if r["component"] in {x["component"] for x in reports.CANDIDATES}:
                r["status"] = "DONE"
        ranked = reports.next_targets(m)
        self.assertEqual(ranked, [])  # registered accelerator scopes must not survive DONE filtering
        names = {r["component"] for r in reports.next_targets(self.metrics)}
        self.assertFalse(names & {"VINTF-HAL-MANIFEST", "VENDOR-PROPERTIES", "BOOT-IMAGES"})

    def test_reports_are_deterministic(self):
        # Replaying reports from the same committed tables must not consult HEAD
        # or incorporate wall-clock time. All output is temporary.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ca = root / "coverage-audit"; ca.mkdir(); (ca / "notes").mkdir()
            (ca/'notes/ANDROID-USERSPACE.md').write_text('## Unified artifact map\n\nhistorical\n')
            with patch.object(reports, "CA", ca), patch.object(reports, "RE", root), redirect_stdout(io.StringIO()):
                functions = (reports.build_next, reports.build_partial, reports.build_missing,
                             reports.build_changes, reports.build_readiness, reports.build_summary,
                             reports.build_index, reports.build_manifest_note, reports.build_readme, reports.build_axis_notes)
                for fn in functions:
                    fn(self.metrics)
                a = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                for fn in functions:
                    fn(self.metrics)
                b = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(a, b)

    def test_percent_encoded_links_and_broken_links(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "with spaces.tsv").write_text("metadata\n")
            md = root / "report.md"
            md.write_text("[ok](with%20spaces.tsv)\n[also ok](<with spaces.tsv>)\n")
            self.assertEqual(checks.check_links(md), [])
            md.write_text("[broken](missing-component/README.md)\n")
            self.assertEqual(len(checks.check_links(md)), 1)

    def reject_mutation(self, table, mutate, message):
        original = checks.rows
        changed = copy.deepcopy(self.tables[table]); mutate(changed)
        def fake(name):
            return changed if name == table else original(name)
        with patch.object(checks, "rows", side_effect=fake), redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(AssertionError, message):
                checks.main()

    def test_rt5133_bound_claim_is_rejected(self):
        def mutate(data):
            next(r for r in data if "RT5133" in r["device"])["presence"] = "PROVEN"
        self.reject_mutation("hardware.tsv", mutate, "RT5133 client-name misread")

    def test_normalized_axis_drift_is_rejected(self):
        def mutate(data):
            next(r for r in data if r["artifact_type"] == "physical-hardware")["artifact"] += "-invented"
        self.reject_mutation("artifact-map.tsv", mutate, "normalized map disagrees")

    def test_partial_must_have_one_valid_class(self):
        def mutate(data):
            next(r for r in data if r["status"] == "PARTIAL")["partial_class"] = "AB"
        self.reject_mutation("components.tsv", mutate, "exactly one A–F")

    def test_kernel_parent_duplicate_is_rejected(self):
        def mutate(data):
            parent=next(r for r in data if r['component']=='CAMERA-HAL-ISP')
            parent['modules']=next(r for r in data if r['component']=='CAMERA-ISP-KERNEL')['modules']
        self.reject_mutation('components.tsv',mutate,'duplicate whole-module ownership')

    def test_accdet_is_not_a_ccd_match(self):
        scopes=json.loads((checks.RE/'accelerator-preparation/scopes.json').read_text())['scopes']
        cam=next(s for s in scopes if s['component']=='CAMERA-ISP-KERNEL')
        self.assertFalse(re.search(cam['dt_pattern'],'mediatek,mt6369-accdet'))
        self.assertTrue(re.search(cam['dt_pattern'],'mediatek,ccd'))
        gpu=next(s for s in scopes if s['component']=='MALI-GPU-KERNEL')
        self.assertTrue(re.search(gpu['dt_pattern'],'mediatek,ged'))

    def test_existing_transports_and_hosts_not_duplicated(self):
        scopes=json.loads((checks.RE/'accelerator-preparation/scopes.json').read_text())['scopes']
        new={m for s in scopes for m in s['modules']}
        protected={'scp.ko','sensorhub.ko','hf_manager.ko','adsp.ko','mtk_tinysys_ipi.ko','mtk-mbox.ko','mtk-rpmsg-mbox.ko'}
        self.assertFalse(new & protected)

    def test_unsupported_rename_is_rejected_not_applied(self):
        rt = next(p for p in reports.PROPOSALS if p[0] == "PC-009")
        self.assertEqual((rt[3], rt[4]), ("REJECT", 0))
        self.assertEqual(sum(p[4] for p in reports.PROPOSALS if p[3] == 'ACCEPT RECOMMENDATION'), -9)
        applied=[p for p in reports.PROPOSALS if p[3]=='APPLIED (AUTHORIZED PREPARATION)']
        self.assertEqual(len(applied),6)
        self.assertTrue(all(p[4]==0 for p in applied))


if __name__ == "__main__":
    unittest.main()
