# BOOT-LOWPOWER-INTEGRATION-01

This integration brings the two completed, independently proven batches into canonical research. Each was
applied with its own validated, identity-keyed compare-and-swap (CAS) delta, in the order
BOOT-DEPENDENCY-BATCH-01 then LOW-POWER-BATCH-01. No audit table was copied wholesale.

| | Commit |
|---|---|
| Canonical base | `21ec8901` (A333 B1 C10 D60 E0 F0 G54 = 334/458) |
| Recovery | tag `pre-boot-lowpower-integration-01` → 21ec8901; bundle `kernel-work/boot-lowpower-integration-01/pre-integration-master-21ec8901.bundle` (sha256 `d39c9240…`, verified) |
| Merge 1 | `codex/boot-dependency-batch-01` @ `a4de67d5` (source `android_kernel_modules_boot_dependencies_ulefone_gq5012bf1` @ `8e7a66e1`) |
| Stage 1 | 304 fields / 16 identities D→A. Audit diff byte-equal to the boot batch's `PROPOSED-AUDIT.patch` (`ecc89333…`). Validator PASS 0 errors, A349 B1 C10 D44 G54, 14/14 audit mutations |
| Merge 2 | `codex/low-power-batch-01` @ `45f93633` (source `android_kernel_modules_low_power_ulefone_gq5012bf1` @ `18562149`) |
| Stage 2 | 228 fields / 12 identities D→A. Cumulative diff vs 21ec8901 byte-equal to `PROPOSED-AUDIT-COMBINED.patch` (`f8907081…`). Validator PASS 0 errors, **A361 B1 C10 D32 E0 F0 G54 = 362 certified / 96 remaining**, 14/14 |

## Preflight (ownership evidence)

- **Canonical state:** canonical was on `master` at 21ec8901, clean, with no `.lock` files. The last index write
  was 2026-10-12 01:34 and the integration started at 12:35.
- **Other sessions:** two other `pi` agent sessions have the canonical path as their cwd. Neither had any child
  process, and the only other session log last wrote at 2026-10-11 23:10. Idleness was therefore probable but
  not proven, so all edits were made in the isolated worktree
  `ulefone-gq5012bf1-research-boot-lowpower-integration` (branch `integration/boot-lowpower-01`). Canonical
  was only fast-forwarded after a re-check.
- **Source and stock:** both maintained repos were at their recorded commits and clean. Both bundles cloned
  fresh (`--no-hardlinks`) to the exact commits with `fsck --full` clean. Inventory PASS 0 errors, 458 identities
  / 471 occurrences (60 system_dlkm signed-721, 196 vendor_boot, 215 vendor_dlkm). The operand copy in the
  integration worktree has the same SHA256 for all 471 `.ko` as canonical.
- **Targets:** all 28 targets were still canonical D (candidate-only), with stock SHA256 equal to their
  manifests. The two target sets are disjoint.

## Invariants verified independently after stage 2 (`evidence/invariant-check.txt`)

- **Scope:** 458 identities; exactly the 28 selected rows changed in ALL-457-MODULES (all D→A). No other row
  changed in SOURCE-OWNERSHIP, SOURCE-GAPS (124→96), DONE-SOURCE-EVIDENCE-DISCREPANCIES (73→70),
  OPTIONAL-15-REVIEW, REPRODUCIBILITY-RISKS, source-reviews or review-input-hashes.
- **Preserved:** stock SHA256 and filenames unchanged for 458/458, with 0 A/B demotions. All 10 C rows are
  byte-identical (aw883xx_driver, charger_class, focaltech_touch_spi_ft3680, mtk_chg_type_det, rt_pd_manager,
  st21nfc, tcpc_class, tcpc_mt6375, tkcore, yft_devinfo). Both distinct `bluetooth.ko` identities (2df021ea…,
  d2659fb3…) are kept.
- **Proofs:** 28/28 source proofs are consistent: audit row A, stock SHA256, B1 rebuild == B2 rebuild,
  acceptance-normalized B1 == B2, and every `parity_evidence` path present.

## Provenance disclosures preserved (`PROVENANCE-DISCLOSURES.tsv`)

The audit schema has no free-text provenance field, and the validator is kept unchanged. The disclosures
therefore live in the source patches themselves, in BOOT-DEPENDENCY-BATCH-01 `BLOCKERS.tsv` /
`SOURCE-LINEAGE.md`, and in the register in this package:

- **i2c-mt65xx:** reconstructed OEM difference, a single DT-property literal. It was re-verified here against the
  read-only stock module (`.rodata`) and the stock merged DT.
- **regulator-vibrator:** 27 non-code placeholder comment lines. They reproduce only the proven line count, and
  their in-source text states that the original OEM text is not recoverable. No code, data, ABI or metadata
  depends on them beyond the `__LINE__` constants, which equal stock.

The original packages are preserved unchanged. The applier's scratch logs were written into this package
(`evidence/stage1-*`, `evidence/stage2-*`), and the originals were restored or left untouched.
