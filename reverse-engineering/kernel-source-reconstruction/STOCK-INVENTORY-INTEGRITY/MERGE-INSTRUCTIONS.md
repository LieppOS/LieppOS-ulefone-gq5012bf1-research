# Integration instructions

This branch (`codex/stock-inventory-integrity`, based on canonical `f61ebf03`) adds only
`reverse-engineering/kernel-source-reconstruction/STOCK-INVENTORY-INTEGRITY/`. It changes no audit table, stock
hash, classification, ownership, validator or source repository, so it can be merged at any time without conflict.
Do not merge it while Claude is actively committing, and do not push without approval.

## 1. Owner-applied restoration of the shared canonical operands (required)

The shared tree `ulefone-gq5012bf1-research/workspace/gq5012bf1/stock/partitions/system_dlkm/lib/modules/` still
holds the 60 signature-stripped copies. It was deliberately **not** overwritten, because it is a shared live
path that PLATFORM-BATCH-05 may use. Only the canonical checkout owner should apply the fix, at a moment when no
agent is running in that checkout:

```sh
cd "/home/armol/androido_dalykai/LieppOS custom ROM"
T=ulefone-gq5012bf1-research
R=ulefone-gq5012bf1-research-codex-inventory/reverse-engineering/kernel-source-reconstruction/STOCK-INVENTORY-INTEGRITY
IMG="/home/armol/androido_dalykai/Ulefone_Armor_29_Thermal/Ka as turiu/m170b-gq-gq5012-512g16g-fhdp-V0-bom103-cts-eu_GQ5012BF1_EEA_V15_user_20251022/extracted/system_dlkm_a.img"
FS=/home/armol/kernel-work/codex-conn-batch-01/conn-dev/ws/kernel-build-tools/linux-x86/bin/fsck.erofs   # pinned build-tools e905be25, sha256 3059e2f0…
export PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/armol/kernel-work
# a) dry run: must print identities 60, to_restore 60 (or already_intact 60 if repaired meanwhile)
python3 $R/scripts/restore-operands.py --target-root $T --image "$IMG" --fsck-erofs $FS \
  --quarantine /home/armol/kernel-work/canonical-unsigned-stock-quarantine-$(date +%Y%m%d%H%M) --manifest /home/armol/kernel-work/canonical-restore-dry-run.tsv
# b) apply (aborts before any write if any file is not exactly intact or exactly signature-stripped)
python3 $R/scripts/restore-operands.py --target-root $T --image "$IMG" --fsck-erofs $FS \
  --quarantine /home/armol/kernel-work/canonical-unsigned-stock-quarantine-$(date +%Y%m%d%H%M) --manifest /home/armol/kernel-work/canonical-restore-manifest.tsv --apply
# c) verify
python3 $R/scripts/verify-inventory.py $T                         # PASS, 458/471, 60/60 signed
(cd $T/reverse-engineering/kernel-source-parity-audit/scripts && python3 validate.py >/dev/null && python3 test_validate.py)
```

The expected dry-run plan against canonical is preserved in `evidence/repair/canonical-dry-run.tsv`: 60
`SIGNATURE_STRIPPED → WOULD_RESTORE`, with the before hashes equal to `EXPECTED-VS-OBSERVED.tsv`. Expected result:
the validator exits 0 with 0 errors and the mutation tests pass 14/14, as already demonstrated on the isolated
copy (`VALIDATION-BEFORE-AFTER.md`). Keep the new quarantine directory and commit the manifest under this research
directory if you want the canonical restoration recorded.

## 2. Merge order / concurrency

| Branch | Head | Contents | Effect on certified count |
|---|---|---|---|
| master (canonical) | `f61ebf03` | committed state | **245 certified / 213 remaining** (A244 B1 C14 D91 G108) |
| `codex/stock-inventory-integrity` | this branch | integrity research only | 0 |
| `codex/usb-typec-closure` | `7e196c32` | 22-field audit proposal for 5 C (revalidated here) | 0 (no promotions) |
| `codex/scp-connectivity-batch-01` | `40bfedda` | 20 rows: 17 G→A, 3 G→C | +17 |
| `codex/audio-batch-01` | `f00bd8af` | 21 rows: 20 G→A, 1 G→C | +20 |
| PLATFORM-BATCH-05 | not yet committed | — | unknown |

- **Committed canonical status (exact): 245 / 213.**
- **Projected** if both Codex batch deltas apply after re-checking on the then-current HEAD: 282 / 176
  (measured in `SCP-CONNECTIVITY-BATCH-01/evidence/audit-delta-test-on-f61ebf03.json`). Each `module_id` is counted
  once; the three sets are disjoint. The USB closure adds 0. Batch05 is excluded.
- Order:
  1. Restore the canonical operands (§1).
  2. Re-run the live validator: it must pass with no delta applied.
  3. Integrate Batch05 when Claude commits it.
  4. Integrate the audio and connectivity deltas, each following its own `MERGE-INSTRUCTIONS.md`.
  5. Then review the USB closure's 22-field delta separately. Its `expected_before` values match `f61ebf03`, so check them again against the HEAD at integration time, and do not let it change `source_status`.
- After every integration step, run `validate.py`, `test_validate.py` and `scripts/verify-inventory.py <checkout>`.

## 3. Follow-ups for other owners (not done here; other branches untouched)

- SCP-CONNECTIVITY-BATCH-01: add a note that its `oem-base-census.txt` was produced by the incident-2 command (values valid, procedure unsafe).
- PLATFORM-BATCH-04: `stock-operand-drift/recovery-verified.json` records the cause as unknown. The cause is now
  established (`ROOT-CAUSE.md`, incident 1).
- Add `verify-inventory.py` (or an equivalent signature census) to the standard pre/post-batch checklist.
