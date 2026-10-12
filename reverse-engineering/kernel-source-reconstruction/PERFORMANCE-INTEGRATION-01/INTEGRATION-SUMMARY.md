# PERFORMANCE-INTEGRATION-01

This integrates PERFORMANCE-POWERHAL-BATCH-01 (14 D→A) into canonical research. It uses that batch's validated
identity-keyed compare-and-swap delta; no audit table was copied wholesale.

| | |
|---|---|
| Initial canonical | `63f12972` (A361 B1 C10 D32 E0 F0 G54 = 362/458); unchanged validator PASS, 0 errors, before integration |
| Recovery | tag `pre-performance-integration-01` → 63f12972; bundle `kernel-work/performance-integration-01/pre-integration-master-63f12972.bundle` (sha256 `104d35d3…`, verified) |
| Merged | `claude/performance-powerhal-batch-01` @ `026bf42a` (source `android_kernel_modules_performance_ulefone_gq5012bf1` @ `7a1a1e29`). The bundle clones fresh to 7a1a1e29 with `fsck --full` clean; the repo is clean at that commit |
| Applied | 266 fields over 14 identities, all D→A. The audit diff is byte-equal to `PROPOSED-AUDIT.patch`, sha256 `85b318726dbb3577399bf31ea5ff08405d6ff127e5634e5705729f50de85d6cd` |
| Result | validator PASS, 0 errors, **A375 B1 C10 D18 E0 F0 G54 = 376 certified / 82 remaining**; 14/14 audit mutations; inventory PASS 458/471 (60 signed system_dlkm, 196 vendor_boot, 215 vendor_dlkm) |
| Worktree | reused the clean `ulefone-gq5012bf1-research-boot-lowpower-integration` worktree (new branch `integration/performance-01`). Its 471-operand sha256 list equals canonical and is unchanged since BOOT-LOWPOWER-INTEGRATION-01 |

## Ownership preflight

- **Canonical:** at 63f12972, clean, no locks.
- **Concurrent Codex activity:** G-SOURCE-RECOVERY-BATCH-01 was active (extracting its own toolchain under
  `kernel-work/g-source-recovery-batch-01`). Its manifest (branch `codex/g-source-recovery-batch-01` @ 59ee0113)
  freezes 23 Category G identities; none is among these 14 D rows. Its assignment forbids writing canonical and
  states that Claude may advance it.
- **Approach:** all edits were made in the isolated worktree, and canonical was only fast-forwarded.
- **Pre-checks:** all 14 targets were canonical D with candidate owners, and their stock SHA256 matched the
  manifest.

## Invariants (`evidence/invariants.txt`)

- **Scope:** exactly the 14 selected rows changed in ALL-457-MODULES. No row outside them changed in
  SOURCE-OWNERSHIP, SOURCE-GAPS (96→82), DONE-SOURCE-EVIDENCE-DISCREPANCIES (70→69), OPTIONAL-15-REVIEW,
  REPRODUCIBILITY-RISKS, source-reviews or review-input-hashes.
- **Preserved rows:** stock sha256/size/filename/paths unchanged for 458/458; 0 A/B demotions; the 10 C rows and
  all 54 G rows (Codex scope) are byte-identical; both `bluetooth.ko` identities (2df021ea…, d2659fb3…) are kept.
- **Source proofs:** 14/14 consistent (audit A at 7a1a1e29, B1 rebuild == B2 rebuild, normalized B1 == B2, stock
  sha matches, evidence paths exist).

The original research package is unchanged. The applier's scratch log was moved to `evidence/apply/`, and the
committed original was restored.
