#!/usr/bin/env python3
"""Regression tests for the 60/60 stock-operand incident (signature-stripping in-place llvm-objcopy).

Run from an operand root whose stock tree is intact (the isolated repaired worktree):
    PYTHONDONTWRITEBYTECODE=1 python3 test_stock_operand_integrity.py -v
Environment:
    OPERAND_ROOT  research checkout with intact stock operands (default: this worktree)
    IMAGE, FSCK_EROFS  authenticated system_dlkm_a.img and pinned fsck.erofs (restore tests)
    SCRATCH       btrfs scratch directory for reflinked temporary trees

Every test works on reflinked temporary copies.  No test writes to OPERAND_ROOT,
the canonical checkout, the partition image or any audit table.  The canonical
validator is used unchanged; nothing is normalized.
"""
import csv, hashlib, importlib, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('OPERAND_ROOT', HERE.parents[3])).resolve()
AUDIT_SCRIPTS = ROOT / 'reverse-engineering/kernel-source-parity-audit/scripts'
SCRATCH = Path(os.environ.get('SCRATCH', '/home/armol/kernel-work/codex-inventory-integrity/tests-tmp'))
IMAGE = Path(os.environ.get('IMAGE', '/home/armol/kernel-work/codex-inventory-integrity/system_dlkm_a.img'))
FSCK = Path(os.environ.get('FSCK_EROFS', '/home/armol/kernel-work/codex-conn-batch-01/conn-dev/ws/kernel-build-tools/linux-x86/bin/fsck.erofs'))
OBJCOPY = shutil.which('llvm-objcopy')
REL = {'system_dlkm': 'workspace/gq5012bf1/stock/partitions/system_dlkm',
       'vendor_dlkm': 'workspace/gq5012bf1/stock/partitions/vendor_dlkm',
       'vendor_boot_platform': 'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted'}
INCIDENT = HERE.parent / 'evidence/before/validator.stdout.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0, str(AUDIT_SCRIPTS))
inventory = importlib.import_module('inventory'); validate_mod = importlib.import_module('validate')
ROWS = list(csv.DictReader((ROOT / 'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').open(), delimiter='\t'))


class Operands(unittest.TestCase):
    """A reflinked private copy of the three stock roots, swapped into the unchanged validator."""

    @classmethod
    def setUpClass(cls):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        cls.saved = (inventory.ROOT, dict(inventory.STOCK_ROOTS))

    @classmethod
    def tearDownClass(cls):
        inventory.ROOT, roots = cls.saved; inventory.STOCK_ROOTS.clear(); inventory.STOCK_ROOTS.update(roots)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=SCRATCH))
        for rel in REL.values():
            (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['cp', '-a', '--reflink=always', str(ROOT / rel), str(self.tmp / rel)], check=True)
        inventory.ROOT = self.tmp
        inventory.STOCK_ROOTS.clear(); inventory.STOCK_ROOTS.update({k: self.tmp / v for k, v in REL.items()})

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def codes(self, result):
        out = {}
        for e in result['errors']:
            out.setdefault(e['code'], []).append(e['message'])
        return out

    def objcopy_in_place(self, path):
        """The exact command shape that caused both incidents (no output operand)."""
        subprocess.run([OBJCOPY, '--dump-section', '.BTF=/dev/stdout', str(path)], capture_output=True)

    def first_path(self, filename, partition):
        r = next(r for r in ROWS if r['filename'] == filename and r['partitions'] == partition)
        return r, self.tmp / r['stock_paths'].split(';')[0]

    # --- baseline -------------------------------------------------------------------------------------
    def test_intact_operands_pass(self):
        res = validate_mod.validate()
        self.assertEqual(res['errors'], [])
        self.assertEqual((res['distinct_stock_identities'], res['stock_occurrences']), (458, 471))

    # --- actual failure mode --------------------------------------------------------------------------
    def test_in_place_objcopy_strips_signature_and_is_rejected(self):
        row, p = self.first_path('6lowpan.ko', 'system_dlkm')
        self.objcopy_in_place(p)
        self.assertEqual(p.stat().st_size, int(row['stock_size']) - 721)
        self.assertEqual(sha(p), '6d239276a32eab16c22c68a10b4c692b27fbe12f3e3d8779ff2507aede44d278')  # incident bytes
        c = self.codes(validate_mod.validate())
        self.assertEqual(c['MISSING_IDENTITY'], ['6lowpan.ko@6d239276a32eab16c22c68a10b4c692b27fbe12f3e3d8779ff2507aede44d278'])
        self.assertEqual(c['UNEXPECTED_IDENTITY'], [row['module_id']])
        self.assertIn('STALE_FROZEN_INVENTORY', c)

    def test_full_incident_reproduces_exact_60_60_failure(self):
        for r in ROWS:
            self.objcopy_in_place(self.tmp / r['stock_paths'].split(';')[0])   # same loop as the incident census
        res = validate_mod.validate()
        expected = json.loads(INCIDENT.read_text())
        self.assertEqual(res['errors'], expected['errors'])
        c = self.codes(res)
        self.assertEqual((len(c['MISSING_IDENTITY']), len(c['UNEXPECTED_IDENTITY'])), (60, 60))
        # the 11 unsigned vendor BTF modules are rewritten byte-identically, hence undetectable and harmless
        for r in ROWS:
            if r['partitions'] != 'system_dlkm':
                for p in r['stock_paths'].split(';'):
                    self.assertEqual(sha(self.tmp / p), r['stock_sha256'])

    def test_vendor_bluetooth_not_confused_with_system_bluetooth(self):
        row, p = self.first_path('bluetooth.ko', 'system_dlkm')
        self.objcopy_in_place(p)
        c = self.codes(validate_mod.validate())
        vendor = next(r for r in ROWS if r['filename'] == 'bluetooth.ko' and r['partitions'] == 'vendor_dlkm')
        self.assertEqual(c['UNEXPECTED_IDENTITY'], [row['module_id']])
        self.assertNotIn(vendor['module_id'], c['UNEXPECTED_IDENTITY'])

    def test_truncation_only_rejected(self):
        row, p = self.first_path('can.ko', 'system_dlkm')
        b = p.read_bytes(); p.write_bytes(b[:-721])
        self.assertIn('UNEXPECTED_IDENTITY', self.codes(validate_mod.validate()))

    def test_same_size_signature_corruption_rejected(self):
        row, p = self.first_path('can.ko', 'system_dlkm')
        b = bytearray(p.read_bytes()); b[-100] ^= 1; p.write_bytes(bytes(b))
        self.assertEqual(p.stat().st_size, int(row['stock_size']))
        c = self.codes(validate_mod.validate())
        self.assertEqual(c['UNEXPECTED_IDENTITY'], [row['module_id']])

    def test_rebuilt_module_substitution_rejected(self):
        # same-filename substitution: vendor_dlkm bluetooth.ko bytes placed at the system_dlkm bluetooth.ko path
        row, p = self.first_path('bluetooth.ko', 'system_dlkm')
        vrow, vp = self.first_path('bluetooth.ko', 'vendor_dlkm')
        p.write_bytes(vp.read_bytes())
        c = self.codes(validate_mod.validate())
        self.assertEqual(c['UNEXPECTED_IDENTITY'], [row['module_id']])
        self.assertIn('STOCK_PATHS_OMITTED_OR_DUPLICATED', c)   # vendor identity now appears at two paths

    # --- independent inventory verifier --------------------------------------------------------------
    def verify(self):
        return subprocess.run([sys.executable, str(HERE / 'verify-inventory.py'), str(self.tmp), '--git-root', str(ROOT)], capture_output=True, text=True)

    def test_verifier_passes_intact_and_rejects_stripped(self):
        self.assertEqual(self.verify().returncode, 0)
        _, p = self.first_path('6lowpan.ko', 'system_dlkm'); self.objcopy_in_place(p)
        out = self.verify()
        self.assertEqual(out.returncode, 1)
        brief = json.loads(out.stdout)
        self.assertEqual(brief['error_kinds'], {'SIZE': 1, 'SHA256': 1, 'SIGNATURE_TRAILER': 1})

    # --- fail-closed restoration tool ----------------------------------------------------------------
    def restore_root(self):
        """A minimal target root: committed tables + the private stock tree."""
        for rel in ['reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv',
                    'reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json', 'kernel/stock-module-master.csv']:
            (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT / rel, self.tmp / rel)
        return self.tmp

    def restore(self, *extra, image=IMAGE):
        q = self.tmp / 'q'
        return subprocess.run([sys.executable, str(HERE / 'restore-operands.py'), '--target-root', str(self.restore_root()), '--image', str(image),
                               '--fsck-erofs', str(FSCK), '--quarantine', str(q), '--manifest', str(self.tmp / 'm.tsv'), *extra],
                              capture_output=True, text=True, env=dict(os.environ, TMPDIR=str(SCRATCH)))

    @unittest.skipUnless(IMAGE.is_file() and FSCK.is_file(), 'image/fsck.erofs unavailable')
    def test_restore_repairs_only_stripped_and_quarantines(self):
        row, p = self.first_path('6lowpan.ko', 'system_dlkm'); self.objcopy_in_place(p); damaged = sha(p)
        out = self.restore('--apply')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(sha(p), row['stock_sha256'])
        self.assertEqual(sha(self.tmp / 'q/6lowpan.ko'), damaged)
        with (self.tmp / 'm.tsv').open() as fh:
            m = list(csv.DictReader(fh, delimiter='\t'))
        self.assertEqual([r['filename'] for r in m if r['action'] == 'RESTORED'], ['6lowpan.ko'])
        self.assertEqual(validate_mod.validate()['errors'], [])

    @unittest.skipUnless(IMAGE.is_file() and FSCK.is_file(), 'image/fsck.erofs unavailable')
    def test_restore_refuses_non_signature_damage_without_writing(self):
        _, a = self.first_path('6lowpan.ko', 'system_dlkm'); self.objcopy_in_place(a)
        _, b = self.first_path('can.ko', 'system_dlkm')
        x = bytearray(b.read_bytes()); x[5000] ^= 1; b.write_bytes(bytes(x))      # code change, not a strip
        before = (sha(a), sha(b))
        out = self.restore('--apply')
        self.assertEqual(out.returncode, 2); self.assertIn('unknown state', out.stderr)
        self.assertEqual((sha(a), sha(b)), before)                              # nothing written, not even the strippable one
        self.assertFalse((self.tmp / 'q').exists())

    @unittest.skipUnless(IMAGE.is_file() and FSCK.is_file(), 'image/fsck.erofs unavailable')
    def test_restore_refuses_unauthenticated_image(self):
        bad = self.tmp / 'bad.img'; b = bytearray(IMAGE.read_bytes()); b[-1] ^= 1; bad.write_bytes(bytes(b))
        out = self.restore('--apply', image=bad)
        self.assertEqual(out.returncode, 2); self.assertIn('image sha256', out.stderr)


if __name__ == '__main__':
    unittest.main()
