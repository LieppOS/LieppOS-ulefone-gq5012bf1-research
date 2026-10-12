# KDM-INTEGRATION-01

This integrates KDM-MEDIA-SECURITY-BATCH-01 (10 D→A) into canonical research using that batch's validated
identity-keyed compare-and-swap delta. No audit table was copied wholesale. `flashlight.ko`, the batch's 11th
frozen target, stays **D**: its row is byte-identical.

| | |
|---|---|
| Initial canonical | `ee1803b7` (A375 B1 C10 D18 E0 F0 G54 = 376/458); unchanged validator PASS, 0 errors, before integration (`evidence/canonical-validate-pre.json`) |
| Recovery | tag `pre-kdm-integration-01` → ee1803b7; bundle `kernel-work/kdm-integration-01/pre-integration-master-ee1803b7.bundle` (sha256 `6d854456b07609fe2966c12b9100dce2556f408b11b58d8c9cd0b7ecb4557c04`, verified) |
| Merged | `claude/kdm-media-security-batch-01` @ `2dbf70e5`; source `android_kernel_modules_kdm_media_security_ulefone_gq5012bf1` @ `973eb04a`, which is clean. The bundle (sha256 `c12a5623…`) clones fresh to 973eb04a with tree `2c06a5bd` equal to the repo and `fsck --full` clean |
| Applied | 190 fields over 10 identities, all D→A. The audit diff is byte-equal to `PROPOSED-AUDIT.patch` (sha256 `97b846cc20fabde8…`) |
| Result | validator PASS, 0 errors, **A385 B1 C10 D8 E0 F0 G54 = 386 certified / 72 remaining (84.3%)**; 14/14 audit mutations (applier) and `test_validate.py` 14/14; inventory PASS 458/471 (60 signed system_dlkm, 196 vendor_boot, 215 vendor_dlkm) |
| Worktree | the clean `ulefone-gq5012bf1-research-boot-lowpower-integration` worktree (new branch `integration/kdm-01`). Its 471-operand sha256 list and `nothing-module-index.csv` equal canonical |

## Ownership preflight

- **Canonical:** at ee1803b7, clean, no locks, no agent processes.
- **Codex G-SOURCE-RECOVERY-BATCH-01:**
  - Its branch `codex/g-source-recovery-batch-01` was at 2a1bd515 with uncommitted completion work. Its private
    audit scratch worktrees (`-codex-g-source-audit`, `-codex-g-source-replay`) are at ee1803b7.
  - Its `final-canonical-check.json` records canonical as untouched with `overlap_with_Claude_KDM: []`. Its own
    merge instructions forbid a blind merge into canonical and require a CAS re-plan on the current HEAD.
  - No Codex file, worktree or branch was touched.
- **The 11 frozen identities:** all were canonical D with stock sha256 equal to the manifest.

## Invariants (`evidence/invariants.txt`)

- **Scope:** exactly the 10 certified rows changed in ALL-457-MODULES, and the flashlight row is unchanged. No row
  outside the 10 changed in SOURCE-OWNERSHIP, SOURCE-GAPS (82→72), DONE-SOURCE-EVIDENCE-DISCREPANCIES (69→64),
  OPTIONAL-15-REVIEW, REPRODUCIBILITY-RISKS, source-reviews or review-input-hashes.
- **Preserved rows:** stock sha256/size/filename/paths unchanged for 458/458; 0 A/B demotions; the 10 C rows and
  all 54 G rows (including Codex's 23 frozen identities) are byte-identical; both `bluetooth.ko` identities are
  kept.
- **Source proofs:** 10/10 consistent (audit A at 973eb04a, B1 rebuild == B2 rebuild, stock sha matches).

## Provenance preserved in the audit rows and the research package

- **Source:** 9 targets use unmodified ALPS 5e415e05. `mtk_irtx_pwm` carries a 9-line **reconstructed** OEM delta
  (the `dma-mask-bit` DT property sets the DMA mask before TX). It came from historical LieppOS commit 3b995377 and
  is corroborated by the stock ELF and the stock DT, but it is not recovered verbatim OEM text.
- **Architecture findings, all retained:**
  - `mtk-composite` is the V4L2 flashlight composite, not USB.
  - The stock DT has a JPEG encoder node only.
  - Secure heaps depend on tmem_ffa (G).
  - `widevine_driver` is a normal-world buffer-to-secure-handle interface.
  - `tui-common` holds the touch hand-over hooks.
  - `sapu` uses GenieZone KREE and an APU rpmsg power lock.
  - The efuse driver is read-only.
- **Claims not made:** no secure-world, DRM, TUI or hardware-security claim.

The applier's scratch output was moved to `evidence/apply/`, and the committed research package was restored
unchanged.

## Applied

Canonical was fast-forwarded from ee1803b7 to `ec46467a` after re-checking that it was still idle (clean, no
locks). Live post-integration checks (`evidence/live-post/`):

- inventory PASS 458/471, with all 471 stock `.ko` sha256 unchanged;
- validator PASS_WITH_EXPLICIT_UNRESOLVED_SOURCE_CLASSES, 0 errors, A385 B1 C10 D8 E0 F0 G54;
- `test_validate.py` 14/14 OK.

## Unmerged branches after integration

- **`codex/g-source-recovery-batch-01`:** 22 G→A and 1 G→C proposals, planned against ee1803b7. They must be
  re-planned by identity on ec46467a. The rows are disjoint from these 10, but the RECONSTRUCTION-QUEUE header
  anchor changed.
- Older merged or superseded integration branches were left as-is.
