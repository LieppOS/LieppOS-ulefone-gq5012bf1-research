# Validation before / after

Validator: unchanged canonical `reverse-engineering/kernel-source-parity-audit/scripts/validate.py`
(sha256 `32e3f01d…`, `inventory.py` `664892fa…`, `test_validate.py` `9bc1accc…`, all at `f61ebf03`), run with
`PYTHONDONTWRITEBYTECODE=1 python3 validate.py` from the script directory. Python 3.14.8. The audit directory in
the isolated worktree is byte-identical to `f61ebf03` (`git diff --quiet f61ebf03 -- reverse-engineering/kernel-source-parity-audit`).

| Run | Operands | Validator | Errors | Audit mutation tests (`test_validate.py`) | `verify-inventory.py` |
|---|---|---|---|---|---|
| **Before, canonical** (`evidence/before/`) | canonical shared tree, read-only, `f61ebf03`, clean | exit 1, FAIL | MISSING_IDENTITY 60, UNEXPECTED_IDENTITY 60, STALE_FROZEN_INVENTORY 1, OWNERSHIP_IDENTITY_SET 1 | 10/14 (4 fail: baseline-dependent) | FAIL: SIZE 60, SHA256 60, SIGNATURE_TRAILER 60; 411/471 occurrences match |
| USB-TYPEC-CLOSURE record (`7e196c32`) | same | FAIL | identical JSON to the run above (`evidence/before/closure-vs-reproduction.txt`) | 10/14 | n/a |
| **Before, isolated** (`evidence/isolated-before/`) | reflinked copy, unrepaired | exit 1 | byte-identical JSON to canonical | n/a | n/a |
| **After, isolated** (`evidence/after/`) | 60 restored from authenticated image | **exit 0, `PASS_WITH_EXPLICIT_UNRESOLVED_SOURCE_CLASSES`** | **0** | **14/14 OK** | **PASS**: 471/471 occurrences match committed SHA and size |

After-repair inventory facts (`evidence/after/verify-inventory-isolated.json`, expected values read from `git show f61ebf03:`):

| Check | Result |
|---|---|
| Distinct binary identities | **458** |
| Stock occurrences | **471** (system_dlkm 60, vendor_dlkm 215, vendor_boot_platform 196) |
| Unique filenames | 457. The only collision is `bluetooth.ko` = 2 identities (system_dlkm vs vendor_dlkm); no filename-based deduplication |
| On-disk `.ko` path set == committed path set | yes, no unlisted or absent path |
| Partition assignment | unchanged for every occurrence |
| Signature census | system_dlkm 60/60 signed (721-byte PKCS#7 trailer); vendor 411/411 unsigned |
| Audit, frozen inventory, stock master, ownership sets | all equal |
| Canonical SHA-256 / size values | unchanged (audit directory byte-identical to `f61ebf03`) |
| Source classifications | A244 B1 C14 D91 E0 F0 G108 = 245 certified / 213 remaining (unchanged) |
| Ownership | `SOURCE-OWNERSHIP.tsv` unchanged |
| Isolated vs canonical | differs in exactly the 60 repaired files |
| Warnings | `SOURCE_CLASSIFICATIONS_UNRESOLVED` (G = 108, pre-existing) and `PREEXISTING_WORKSPACE_DRIFT` (pre-existing informational) |

Nothing was waived: the validator, its tests and every expected value are unchanged. The validator was not
disabled or loosened. It passes because the operands are authentic again.

**The canonical shared operand tree still FAILs** until its owner applies the restoration procedure in
`MERGE-INSTRUCTIONS.md`. This task deliberately did not overwrite that shared path.
