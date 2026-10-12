# DISPLAY-INTEGRATION-01 — DISPLAY-BACKLIGHT-G-BATCH-01 into canonical

**Result:** 8 G→A, giving canonical **A420 B1 C11 D3 E0 F0 G23 = 421/458 certified (91.9%), 37 uncertified**.

## Baseline and safety

- Canonical master `1e87ca06b8c6a472eae7c01da4762791a46b1589` was clean, with no git locks and no build or
  validator processes.
- The validator passed beforehand (A412 B1 C11 D3 G31, 0 errors). Inventory passed 458/471, and the 471 stock
  `.ko` hashes matched the G-CANONICAL-INTEGRATION-01 operand list.
- **Codex** is active only in its own worktree, `codex/g-source-recovery-batch-02` (`128677b6`, based on
  e66cfcf7). Its frozen manifest (`6f78615b…`) excludes these eight identities as `CLAUDE:DISPLAY8_RESERVED`.
- **Recovery point:** tag `pre-display-integration-01` → 1e87ca06, and bundle
  `/home/armol/kernel-work/display-integration-01/pre-display-integration-01.bundle` (sha256 `f041f5e8ad835a17dda28adff22e55bcb739e902cd3a5a06e94003265d29db6b`, verified).

## Source evidence verified

- **Research branch** `claude/display-backlight-g-batch-01` = `db3ddc4bd3519e59dd1a92bc9ff0851425ec7793`. It is a
  descendant of 1e87ca06, so the merge is a fast-forward, and its audit tree equals canonical's.
- **Source repository:** `android_kernel_modules_display_backlight_ulefone_gq5012bf1`.
  - Certified recipe: `c0b39b61bf23f18d30c25f8cdb7ec8cb6b7b2c7f`, tree `f892960f…`.
  - HEAD: `9ec1a1609935987b26b1c51dd0defae43aa58a88`, a docs-only child (parent c0b39b61; changes only
    README.md). The repository is clean.
- **Bundle** `display-backlight.bundle` (`4b98dbd2…`): a fresh `--no-hardlinks` clone at c0b39b61 gives the same
  tree.
- **Committed B1/B2 proof (unchanged):**
  - 8/8 whole-file acceptance in each build, with only the GNU build ID differing.
  - 106/106 ELF mutations rejected per build.
  - 16 outputs and 155 intermediates identical between B1 and B2.
  - 31/31 provider witnesses compiled from pinned source.

## Audit reconciliation

- **Plan:** `audit-delta.py plan --canonical-base 1e87ca06` regenerated exactly the committed AUDIT-DELTA.tsv:
  145 field changes over 8 identities, 0 CAS conflicts.
- **Apply:** `audit-delta.py apply` in the isolated worktree `ulefone-gq5012bf1-research-display-integration`
  (branch `integration/display-01`). The resulting audit diff is **byte-identical** to the reviewed
  `PROPOSED-AUDIT.patch` (sha256 `670c332d…`).
- **Invariants** (`evidence/invariants.txt`):
  - Exactly the 8 manifest identities changed, all G→A.
  - 412 A, 1 B, 11 C (including tmem_ffa and tkcore), 3 D and 23 unselected G rows are byte-identical.
  - No demotion. Stock sha256, size, path and partition are unchanged for 458/458.
  - Both `bluetooth.ko` identities stay distinct (2df021ea…, d2659fb3…).
- **Tests:**
  - Validator PASS, 0 errors.
  - `test_validate.py` 14/14.
  - Inventory PASS 458/471 (60 signed system_dlkm).
  - 471 stock hashes unchanged.

## Provenance preserved, unchanged from the batch package

- ALPS 5e415e05 for seven modules; NothingOSS kernel_modules 5f75a3b1 for `met_backlight_api`.
- The unchanged, previously certified GQ5012BF1 DRM series 0001–0010.
- The **reconstructed** `pwm-mtk-disp` OEM delta: `mediatek,mt6878-disp-pwm0/1` matches plus probe
  start/end logs. It is backed by the stock strings and stock DT nodes, and is not verbatim OEM text.
- The TrustKernel-vs-Microtrust TEE config dependency for the cmdq-sec provider CRCs.
- The DT hardware contract:
  - CUST_LCM backlight, 0x7ff range;
  - display PWMs at 0x1100e000 and 0x1100f000; generic PWM at 0x11008000;
  - panel1 `gate-ic = 0`;
  - `disp-sec` `mediatek,disp-sec-aidctl`.

  None of this is a runtime claim.

## Applied to canonical

The integration branch was committed as `e115fbd4`. Canonical was re-checked idle (still 1e87ca06, clean, no
locks) and **fast-forwarded to `e115fbd4`**; nothing was forced and nothing pushed.

Live post-checks on canonical (`evidence/live-post/`):

- validator PASS, 0 errors, A420 B1 C11 D3 E0 F0 G23;
- 14/14 `test_validate.py`;
- inventory PASS 458/471;
- 471 stock `.ko` hashes unchanged.

The integration worktree (`ulefone-gq5012bf1-research-display-integration`) is kept for audit.
