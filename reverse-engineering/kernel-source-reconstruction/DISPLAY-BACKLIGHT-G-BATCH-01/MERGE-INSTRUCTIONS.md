# Owner integration procedure (narrow compare-and-swap)

Canonical was **not** modified by this batch. Integration needs a fresh exclusive-access check.

## The proposal

- **`AUDIT-DELTA.tsv`:** 145 field rows over the 8 identities against canonical `1e87ca06`. Rows are keyed by
  module_id + stock SHA256 + size + paths.
  - The status/ABI/CRC/KCFI/source fields change exactly as in Codex's reviewed G→A delta.
  - In addition, `exact_functions` goes UNKNOWN→123 for mediatek-drm-panel-drv.
- **Applier:** `scripts/audit-delta.py apply <worktree> --expected-head <HEAD>` refuses canonical and the research
  worktree, and stops before writing on any CAS or identity mismatch. It then updates source-reviews and
  review-input-hashes for the 8 only, runs the reviewed `regenerate()` unchanged, and appends this batch after
  the G-SOURCE-RECOVERY-BATCH-01 queue-header text. Finally it runs the unchanged validator and the 14 audit
  mutation tests.
- **`PROPOSED-AUDIT.patch`** (sha256 `670c332dd2a3d8472c13e9fe097b5c2c848f69d8e77c59f1834060af36ad86d2`): the exact diff from a disposable scratch.
  - Validator PASS, 0 errors: **A420 B1 C11 D3 E0 F0 G23 = 421 certified / 37 remaining (91.9%)**.
  - 14/14 audit mutations; inventory 458/471.
  - Nothing outside the 8 changed: all 413 A/B rows, 11 C rows (including tmem_ffa), 3 D rows and 23 other G
    rows are byte-identical (`evidence/audit-scratch/invariants.txt`).

## Steps

1. **Check canonical** is clean and idle. If it is no longer `1e87ca06`, rerun
   `audit-delta.py plan --canonical-base <new>` and treat any changed `expected_before` as a conflict.
2. **Check the source repo:** `../android_kernel_modules_display_backlight_ulefone_gq5012bf1` must be at
   `c0b39b61…` and clean. If it is absent, clone `bundles/display-backlight.bundle` (`4b98dbd2…`) and run
   `bundle verify` and `fsck --full`.
3. **Apply in a private integration worktree** with verified stock operands: merge
   `claude/display-backlight-g-batch-01`, then run the applier. On base 1e87ca06 the diff must equal
   `PROPOSED-AUDIT.patch`.
4. **Land it:** move the applier's scratch output into an integration package, restore the committed copy, commit,
   fast-forward canonical only. Rerun the inventory check, the validator and `test_validate.py` live. Do not push.

## Note on the source repository HEAD

The certified recipe commit is `c0b39b61bf23f18d30c25f8cdb7ec8cb6b7b2c7f`; the proof bundle and both B1/B2 runs
used it. The repository HEAD is `9ec1a1609935987b26b1c51dd0defae43aa58a88`, a single documentation-only child that rewrites `README.md`:
`git diff --name-only c0b39b61 HEAD` lists only README.md, and no recipe path (scripts/, reference/, patches/,
families/, SOURCE-PINS.tsv) changed. Step 2 therefore accepts HEAD == c0b39b61 or this docs-only child.
