# Owner integration procedure (narrow compare-and-swap)

This batch did not modify canonical. The proposal:

- **`AUDIT-DELTA.tsv`:** 95 field rows over the 5 certified identities, 19 fields each, against canonical
  `0390534d`. Rows are keyed by module_id + stock SHA256 + size + paths, with `expected_before` and
  `proposed_after`.
- **`scripts/audit-delta.py apply <worktree> --expected-head <HEAD>`:** refuses canonical and the research
  worktree and stops before writing on any CAS, identity, hash or size mismatch. It updates source-reviews and
  review-input-hashes for the five only, runs the reviewed `regenerate()` unmodified, appends this batch to the
  RECONSTRUCTION-QUEUE header after the KDM-MEDIA-SECURITY-BATCH-01 text, then runs the unchanged validator and the
  14 audit mutation tests.
- **`PROPOSED-AUDIT.patch`** (sha256 `2e6e76a14e5a402478be2c217ff8e6b8a12dee1a761579e4455f320b4b655067`): the exact diff produced in a disposable scratch on research HEAD
  fc251398, whose audit equals canonical 0390534d.
  - Validator PASS, 0 errors, **A390 B1 C10 D3 E0 F0 G54 = 391 certified / 67 remaining**.
  - 14/14 audit mutations; inventory 458/471 (60 signed system_dlkm, 196 vendor_boot, 215 vendor_dlkm).
  - Nothing outside the five changed. All C and G rows (including Codex's 23 frozen identities), flashlight, fpsgo
    and msync2_frd are byte-identical; both bluetooth identities are kept (`evidence/audit-scratch/invariants.txt`).

## Steps

1. **Check canonical.** It must be clean, with no locks and no agent writing.
   - If it is no longer at `0390534d` (Codex's G batch may integrate first), rerun
     `audit-delta.py plan --canonical-base <new>`. A changed `expected_before` on any of the five is a conflict
     that needs explicit reconciliation. This batch is D-only and Codex is G-only, so overlap is not expected.
   - If the queue header changed, adjust only the single header anchor in `audit-delta.py`.
2. **Check the source repo.** `../android_kernel_modules_remaining_ulefone_gq5012bf1` must be at
   `7e07384a96580bef13ff3f075355c20b4305a4da` and clean. If absent, clone `bundles/remaining-kernel-source.bundle`
   (sha256 `9ceed647…`) and run `bundle verify` and `fsck --full`.
3. **Check the inventory:** `STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py <canonical>` must PASS 458/471.
4. **Apply in a private integration worktree** with verified stock operands and `kernel/nothing-module-index.csv`.
   Merge `claude/remaining-kernel-source-batch-01` (new directory only), then run the applier from this branch's
   worktree against the integration worktree. On base 0390534d the audit diff must equal `PROPOSED-AUDIT.patch`.
5. **Land it.** Move the applier's scratch output into an integration package, restore the committed copy, commit,
   fast-forward canonical, and rerun inventory, validator and `test_validate.py` live. Do not push.

## What the integration does not do

- It makes no claim about reboot behaviour on hardware, GPU runtime, GPU firmware or scheduling policy.
- It does not certify fpsgo or msync2_frd (prebuilt objects) or flashlight (OEM source unavailable).
