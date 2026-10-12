# Owner integration procedure (narrow compare-and-swap)

Canonical master is not edited, and this branch leaves the canonical audit unchanged. The proposal is:

- `AUDIT-DELTA.tsv`: 228 field rows over 12 identities, 19 fields each. Each row has `expected_before` (canonical
  21ec8901) and `proposed_after`, and is keyed by module_id + stock SHA256 + size + path. None of the 12 rows is
  touched by the staged BOOT-DEPENDENCY-BATCH-01 delta, so the CAS holds in either order.
- `scripts/audit-delta.py apply <worktree> --expected-head <HEAD>`: refuses canonical and this worktree, and
  stops on any CAS mismatch. It updates source-reviews and review-input-hashes for the 12 only, runs the reviewed
  `regenerate()` unmodified, updates the queue header (with or without the boot text), then runs the
  unchanged validator and the 14 mutation tests.

Validated outcomes (disposable scratch worktrees with verified operands):

| Order | Result | Patch |
|---|---|---|
| canonical + BOOT-DEPENDENCY-BATCH-01 + this batch (recommended) | PASS 0 errors, A361 B1 C10 D32 E0 F0 G54 = 362/458, 14/14 | `PROPOSED-AUDIT-COMBINED.patch` (`f8907081…`) |
| canonical + this batch only | PASS 0 errors, A345 B1 C10 D48 E0 F0 G54 = 346/458, 14/14 | `PROPOSED-AUDIT-STANDALONE.patch` (`2d4d1e3a…`) |

In the combined scratch, stage 1 (the boot delta) reproduced the boot batch's `PROPOSED-AUDIT.patch` byte-for-byte.
Only the 28 batch identities changed, with 0 other rows, reviews or input hashes affected.

## Steps

1. Confirm canonical is idle, clean and still at `21ec8901`. If it advanced, rerun `audit-delta.py plan
   --canonical-base <new>` and reconcile any changed `expected_before` explicitly.
2. Maintained source must be present and clean at the exact commits:
   - `../android_kernel_modules_low_power_ulefone_gq5012bf1` @ `185621496e49…`. If missing, clone it from
     `bundles/low-power.bundle` and check `bundle verify` and `fsck --full`.
   - For the combined order, also `../android_kernel_modules_boot_dependencies_ulefone_gq5012bf1` @ `8e7a66e1`.
3. `STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py <canonical>` must PASS 458/471.
4. In a private integration worktree with verified operands and `kernel/nothing-module-index.csv` (06f48542…):
   - Merge `codex/boot-dependency-batch-01` and apply its delta (its MERGE-INSTRUCTIONS).
   - Merge `codex/low-power-batch-01` and apply this delta.
   - The audit diff must equal `PROPOSED-AUDIT-COMBINED.patch` when the base is 21ec8901.
5. Commit, fast-forward canonical, and rerun the inventory, validator and `test_validate.py` live. No push.

No runtime, power-state, firmware or hardware behaviour is claimed, and no provider ownership changes.
`mtk_fpsgo` stays Category D.
