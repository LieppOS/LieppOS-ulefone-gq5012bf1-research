# Owner integration procedure (narrow compare-and-swap)

Canonical was **not** modified in Stage B. The proposal has three parts:

- **`AUDIT-DELTA.tsv`:** 190 field rows over the 10 certified identities, 19 fields each, against canonical
  `ee1803b7`. Each row has `expected_before` and `proposed_after`, keyed by module_id + stock SHA256 + size +
  path. The frozen 11th target `flashlight.ko` is excluded (`BLOCKED` in the applier), so its D row is not touched.
- **`scripts/audit-delta.py apply <worktree> --expected-head <HEAD>`:** refuses canonical and this worktree, and
  stops before writing on any CAS, identity, hash or size mismatch. It then:
  1. updates source-reviews and review-input-hashes for the 10 only;
  2. runs the reviewed `regenerate()` unmodified;
  3. appends this batch to the queue header after the PERFORMANCE-POWERHAL-BATCH-01 text;
  4. runs the unchanged validator and the 14 mutation tests.
- **`PROPOSED-AUDIT.patch`** (SHA256 `97b846cc20fabde88b9fbaf0b5fa0a76c0587580257cac9e8450edff09bce6e5`): the exact diff from a disposable scratch (this branch on ee1803b7,
  verified operands).
  - Validator PASS, 0 errors, **A385 B1 C10 D8 E0 F0 G54 = 386 certified / 72 remaining**.
  - 14/14 audit mutations; inventory 458/471.
  - 0 rows, reviews or input hashes changed outside the 10. flashlight, all 10 C rows and all 54 G rows are
    byte-identical (`evidence/audit-scratch/kdm-invariants.txt`).

## Steps

1. **Check canonical.** It must be idle and clean. Codex G-SOURCE-RECOVERY-BATCH-01 may have advanced it.
   - If canonical is not at `ee1803b7`, rerun `audit-delta.py plan --canonical-base <new>`. A changed
     `expected_before` on any of the 10 is a conflict and needs explicit reconciliation. This batch is D-only and
     Codex is G-only, so overlap is not expected.
   - If Codex changed the queue header, adjust only the single header anchor in `audit-delta.py`.
2. **Check the source repo.** `../android_kernel_modules_kdm_media_security_ulefone_gq5012bf1` must be at
   `973eb04ac0d0…` and clean. If it is absent, clone it from `bundles/kdm-media-security.bundle` (sha256 `c12a5623…`)
   and run `bundle verify` and `fsck --full`.
3. **Check the inventory.** `STOCK-INVENTORY-INTEGRITY/scripts/verify-inventory.py <canonical>` must PASS 458/471.
4. **Apply in a private integration worktree.** Use verified operands and `kernel/nothing-module-index.csv`
   (06f48542…). Merge `claude/kdm-media-security-batch-01` (new directory only), then run the applier from this
   branch's worktree against the integration worktree. The audit diff must equal `PROPOSED-AUDIT.patch` when the
   base is ee1803b7.
5. **Land it.** Move the applier's scratch output into an integration package and restore the committed copy.
   Commit, fast-forward canonical, and rerun the inventory, validator and `test_validate.py` live. Do not push.

## What the integration does not do

- It makes no DRM, TEE, TUI, secure-memory, efuse, IR, flash or USB claim.
- Provider ownership does not change. tmem_ffa, gz_trusty_mod and gz_tz_system stay with Codex as G, and mtk-pwm
  stays G.
