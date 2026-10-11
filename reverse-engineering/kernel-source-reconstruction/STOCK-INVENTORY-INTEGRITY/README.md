# STOCK-INVENTORY-INTEGRITY

Diagnosis and fail-closed repair of the canonical stock-module validator failure
(60 `MISSING_IDENTITY` / 60 `UNEXPECTED_IDENTITY`) found during USB-TYPEC-CLOSURE.

**Result.**
- **Root cause:** in-place `llvm-objcopy --dump-section … /dev/stdout <stock.ko>` calls made by Codex during
  SCP-CONNECTIVITY-BATCH-01 stripped the 721-byte appended signatures of the same 60 signed `system_dlkm` analysis
  copies, twice. The first time explains the earlier Batch04 incident.
- **Expectations and validator:** both were correct and are unchanged.
- **Repair:** the 60 copies were restored from the authenticated `system_dlkm_a.img` into an isolated operand set.
  There the unchanged validator passes with 0 errors at 458 identities / 471 occurrences, and its mutation tests pass 14/14.
- **USB closure:** revalidated, 25 A preserved and 5 C unchanged, with no promotion.
- **Canonical shared tree:** not modified. The owner procedure is in `MERGE-INSTRUCTIONS.md`.

| File | Content |
|---|---|
| `ROOT-CAUSE.md` | mechanism, timeline, alternative causes excluded |
| `MISSING-IDENTITIES.tsv` / `UNEXPECTED-IDENTITIES.tsv` | the 60 + 60 validator records, paired by path |
| `EXPECTED-VS-OBSERVED.tsv` | per module: sizes, hashes, image member, unsigned prefix, signature, Batch04 comparison |
| `STOCK-OPERAND-PROVENANCE.md` | trust anchors, image authentication, extraction, isolated set |
| `SIGNATURE-ANALYSIS.md` | measured trailer format and signer |
| `REPAIR-MANIFEST.tsv` | 60 isolated restorations: before/after hashes, inode, quarantine |
| `VALIDATION-BEFORE-AFTER.md` | validator, mutation tests and inventory before/after |
| `REGRESSION-TESTS.md` | 11 regression tests of the real failure mode |
| `USB-CLOSURE-REVALIDATION.md` | closure revalidation |
| `MERGE-INSTRUCTIONS.md` | owner restoration procedure, merge order, exact vs projected totals |
| `STATE.json` | machine-readable state |
| `scripts/` | `analyze-drift.py`, `restore-operands.py`, `verify-inventory.py`, `reproduce-mechanism.sh`, `test_stock_operand_integrity.py`, `revalidate-usb-closure.py`, `validate-deliverables.py` |
| `evidence/` | `before/`, `isolated-before/`, `after/`, `repair/`, `root-cause/`, `provenance/`, `regression/`, `usb-closure/` |

Offline only: no phone access and no push. No other agent's checkout or branch was modified.
