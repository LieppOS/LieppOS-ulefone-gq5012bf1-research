# G-CANONICAL-INTEGRATION-01

This package covers two consecutive identity-keyed CAS integrations into canonical research. No full audit
snapshot was copied.

| Stage | Package | Rows | Fields | Result |
|---|---|---|---:|---|
| A | REMAINING-KERNEL-SOURCE-BATCH-01 (Claude, research `026ee410`, source `7e07384a`) | 5 D→A | 95 | A390 B1 C10 D3 G54 = 391/458 |
| B | G-SOURCE-RECOVERY-BATCH-01 (Codex, research `468a226e`, sources camera `082e1a29`, modem `152ba718`, secure `00929490`) | 22 G→A, 1 G→C | 430 | **A412 B1 C11 D3 G31 = 413/458 (90.2%), 45 remaining** |

## Stage A

- **Where:** integration worktree `-boot-lowpower-integration`, new branch `integration/g-canonical-01` from
  0390534d.
- **Merge and apply:** merged `claude/remaining-kernel-source-batch-01`, then ran its `audit-delta.py apply`. The
  audit diff is **byte-equal to `PROPOSED-AUDIT.patch`** (`2e6e76a1…`).
- **Checks:** validator 0 errors, 14/14 audit mutations, inventory 458/471.
- **Preserved rows:** only the 5 rows changed; all C/G rows and the remaining D rows (flashlight, fpsgo, msync2_frd)
  are byte-identical (`evidence/stageA/`).
- **Landed:** canonical fast-forwarded to `e66cfcf7`; live validator A390.

## Stage B

1. **Merge:** a new owner worktree `-owner-g-source` (branch `owner/g-source-final`) from e66cfcf7 merged
   `codex/g-source-recovery-batch-01` (package directory only; the audit tree is unchanged by the merge). The
   stale-snapshot branch `codex/g-source-audit-proposal` (6c12da0e) was **not** merged.
2. **Reconciliation:** Codex's 430-field delta was checked field by field against current master (e66cfcf7). None
   of the 23 rows had changed since Codex's ee1803b7 baseline: **430/430 `MATCH_APPLY`, 0 conflicts, 0 newer A/B
   rows protected** (`DELTA-RECONCILIATION.tsv`). The regenerated delta is therefore the same 430 operations.
3. **Apply:** `reconcile-owner.py` (Codex's reviewed, dry-run-by-default CAS) ran a dry run, then `--apply`, which
   runs the reviewed regenerator, the unchanged validator and the 14 audit mutation tests.
4. **Correction:** the regenerator reset the RECONSTRUCTION-QUEUE "Completed integration" header to an old default
   and dropped the newer integration history. I restored the canonical header and appended this batch, exactly as
   earlier appliers do; no other line was edited. The validator and tests were rerun afterwards.
5. **Invariants** (`evidence/stageB/invariants.txt`):
   - Exactly the 23 selected rows changed.
   - All 391 prior A/B rows, all 10 prior C rows, all 3 D rows and the 31 unselected G rows are byte-identical.
   - No stock identity field changed.
   - Review JSON changed only for the 23 identities.
   - Derived tables changed nothing outside the 23.

| Family | Source | Final |
|---|---|---|
| Camera/lens | android_kernel_modules_camera_lens @ 082e1a29fbe79e1ca3fce2ce0b2d7687c0aacadc | camera_af_media, dw9781c, main_vcm, main2_vcm, main3_vcm, main4_vcm, sub_vcm → **A** |
| Modem interfaces | android_kernel_modules_modem_interfaces @ 152ba718f988a3a72daba1855d301740dc6f0969 | c2k_usb, c2k_usb_f_via_atc, c2k_usb_f_via_ets, c2k_usb_f_via_modem, md_cooling_all, mddp, mtk_md_power_throttling → **A** |
| Secure transport | android_kernel_modules_secure_transport @ 009294902944237123e5561bd0361167692a9a02 | ffa_v10, gz_ipc_mod, gz_irq_mod, gz_log_mod, gz_main_mod, gz_trusty_mod, gz_tz_system, gz_virtio_mod → **A**; **tmem_ffa → C** |

`tmem_ffa` is **not** promoted. Its four TrustKernel import CRCs remain unresolved and unwaived
(TRUSTKERNEL-ABI-BOUNDARY.md).

## Evidence

CANONICAL-BASELINE.md, SOURCE-REPOSITORIES.tsv, CHANGED-IDENTITIES.tsv (28 rows), DELTA-RECONCILIATION.tsv,
CLASSIFICATIONS-BEFORE-AFTER.tsv, STOCK-INVENTORY.md, ELF-PROOF-VERIFICATION.md, MUTATION-TESTS.md,
TRUSTKERNEL-ABI-BOUNDARY.md, MERGE-INSTRUCTIONS.md, and `evidence/{stageA,stageB,live-post}`. Codex's original
G-SOURCE-RECOVERY-BATCH-01 package is merged unchanged.
