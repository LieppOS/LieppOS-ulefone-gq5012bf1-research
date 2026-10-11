# USB-TYPEC-CLOSURE revalidation

Script: `scripts/revalidate-usb-closure.py` → `evidence/usb-closure/revalidation.json`
(logs: `revalidation-logs.tar.xz` + `revalidation-logs.SHA256SUMS`).

Inputs:
- Closure research: `codex/usb-typec-closure` @ `7e196c3242ecb7bc0d203ddb3669c97e86e24655`. The scripts ran on a
  `git archive` copy placed temporarily in this worktree and removed afterwards; the closure worktree was never written.
- Preserved four-build proof root: `/home/armol/kernel-work/usb-typec-closure-proof-debugmapped/` (read only).
- Stock operands: the independently verified, repaired isolated tree. It is independent of the damaged
  canonical tree, although all 30 Batch04 targets are vendor_boot (27) or vendor_dlkm (3) and none was damaged.

| Check | Result |
|---|---|
| Type-C source `758f9edc78c7…` | worktree HEAD == commit, clean, `git fsck --full` OK, 2/2 bundles verify |
| Charging source `b2a343a9d866…` | same: HEAD, clean, fsck OK, bundles verify |
| B1/B2 determinism (4 fresh builds F0/F1 × B1/B2) | 30 raw + 30 stripped modules byte-identical (own hashing). Committed `validate-cleancheck.py`: PASS, 157 intermediate objects identical, 437 ABI records exact, read-only mirror unchanged |
| Strict stock acceptance, **re-run** with the unchanged recovered `verify.py` (30 modules × 4 builds = 120 runs) | every build: **25 accepted**; rejected exactly `charger_class`, `mtk_chg_type_det`, `rt_pd_manager`, `tcpc_mt6375`, `tcpc_class`. Identical to the recorded outcomes |
| Five-target comparison recomputed (`compare-five.py`, F0-B1 and F1-B1) | identical between families and to the committed `evidence/final/full-acceptance/summary.json` axes |
| `tcpc_class` | **709/709** functions body-and-position exact; data 113/114 (only `__UNIQUE_ID_srcversion336` unmatched); import/export CRC and KCFI exact; strict verifier exit 1 → **C** |
| `charger_class` / `mtk_chg_type_det` / `rt_pd_manager` | functions 90/90, 8/8, 11/11; srcversion data object only → **C** |
| `tcpc_mt6375` | functions 66/66; data 21/28: 7 `.modinfo`/addressable `__UNIQUE_ID_*` objects whose compiler counter suffixes and srcversion differ (13 distinct names across stock and source) → **C** |
| ELF mutation tests (`test-acceptance.py`, committed) | **23/23 PASS** |
| `validate-preserved-evidence.py` (committed) | PASS (retained-evidence scope). Its embedded live-validator field records the historical FAIL, as committed |
| Regenerated closure evidence vs committed branch | **0 files differ, 0 new** (`evidence/usb-closure/archive-copy-rewrites.txt`) |
| Audit proposal `AUDIT-DELTA.tsv` | 22 field rows: `blocker`, `exact_functions`, `parity_evidence`, `source_commit`, `unresolved_functions`, `verified_difference_classification`. Every `expected_before` equals the `f61ebf03` canonical value; the closure baseline file is byte-identical to `f61ebf03`; no `source_status` change; **0 promotions; not applied** |

**New certifications: none.** All five remain C. Restoring inventory integrity removes the closure's stated
integration blocker (live validator drift) but does not certify any module. The 22-field delta stays a separately
reviewed change.
