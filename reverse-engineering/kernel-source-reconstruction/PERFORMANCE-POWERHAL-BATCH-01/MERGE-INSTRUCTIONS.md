# Owner integration procedure (narrow compare-and-swap)

This branch leaves canonical master and the canonical audit unchanged. The proposal is:

- `AUDIT-DELTA.tsv`: 266 field rows over 14 identities, 19 fields each, computed against canonical `63f12972`. Each
  row has `expected_before` and `proposed_after` and is keyed by module_id + stock SHA256 + size + path.
- `scripts/audit-delta.py apply <worktree> --expected-head <HEAD>`. It refuses canonical and this worktree, and
  stops before writing on any CAS, identity, hash or size mismatch. It then:
  1. updates source-reviews and review-input-hashes for the 14 only;
  2. runs the reviewed `regenerate()` unmodified;
  3. appends this batch to the integrated queue header after the LOW-POWER-BATCH-01 text;
  4. runs the unchanged validator and the 14 mutation tests.
- `PROPOSED-AUDIT.patch` (SHA256 `85b318726dbb3577…`) is the exact audit diff. It was produced in a disposable scratch
  (this branch on 63f12972, with verified operands):
  - validator PASS, 0 errors;
  - **A375 B1 C10 D18 E0 F0 G54 = 376 certified / 82 remaining**;
  - 14/14 audit mutations; inventory 458/471 PASS;
  - 0 rows, reviews or input hashes changed outside the 14 (`evidence/audit-scratch/`).

## Steps

1. **Check canonical.** It must be idle, clean and at `63f12972`. A concurrent Codex G-SOURCE-RECOVERY-BATCH-01
   may advance it.
   - If canonical advanced, rerun `audit-delta.py plan --canonical-base <new>`. Any changed `expected_before` for
     these 14 rows is a conflict and must be reconciled explicitly. This batch is D-only and the G batch is G-only,
     so overlap is not expected.
   - If a G batch changed the queue header, adjust the single header anchor in `audit-delta.py`; no other change
     is allowed.
2. **Check the source repository.** `../android_kernel_modules_performance_ulefone_gq5012bf1` must be at `7a1a1e298a2a…` and
   clean. If it is absent, clone it from `bundles/performance.bundle` and run `git bundle verify` and
   `fsck --full`.
3. **Check the inventory.** `STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py <canonical>` must PASS 458/471.
4. **Apply in a private integration worktree.** Use one with verified operands and
   `kernel/nothing-module-index.csv` (06f48542…). Merge `claude/performance-powerhal-batch-01` (new directory
   only), then run the applier **from this branch's worktree**, with the target set to the integration worktree. The
   audit diff must equal `PROPOSED-AUDIT.patch` when the base is 63f12972.
5. **Apply to canonical and re-check.** Move the applier's `evidence/audit-scratch` output into an integration package
   and restore the committed one. Commit, fast-forward canonical, then rerun the inventory, validator and
   `test_validate.py` live. Do not push.

No runtime, scheduler-behaviour, PowerHAL-service or hardware behaviour is claimed, and no provider ownership
changes. fpsgo.ko and msync2_frd.ko stay D (prebuilt shipped objects); hbt.ko and scheduler_ext.ko stay D
(separate `_cus` batch).
