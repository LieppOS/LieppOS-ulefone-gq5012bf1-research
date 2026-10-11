# Stock operand provenance

## Authority of expected values (unchanged, never edited)

| Source | Commit / date | Role |
|---|---|---|
| `reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv` | `f61ebf03` (system_dlkm rows identical since first commit `ac3a839a`, 2026-10-09) | identity, size, path, partition |
| `reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json` | `ac3a839a` | frozen inventory |
| `kernel/stock-module-master.csv` | `0fdaff28` (2026-09-07) | original stock master |

All three agree for every one of the 458 identities (`scripts/verify-inventory.py`).

## Authentic source of the 60 system_dlkm modules

| Item | Value |
|---|---|
| Path | `/home/armol/androido_dalykai/Ulefone_Armor_29_Thermal/Ka as turiu/m170b-gq-gq5012-512g16g-fhdp-V0-bom103-cts-eu_GQ5012BF1_EEA_V15_user_20251022/extracted/system_dlkm_a.img` |
| Size / mtime | 7 471 104 bytes / 2026-06-04 19:49 |
| SHA-256 | `300f24c5550be110d0161583fa56d3c36ae61b8b2da4b44c128350c6e22b9f2a` |
| Format | EROFS (LZ4, `uuid dbdc9b94-ebb4-5b6f-98b5-d7a548af2b92`) |
| Acquisition | factory V15 EEA user firmware package `…_20251022`, `extracted/` partition images |
| Prior trusted records | `slot-b-investigation/untouched-b-early-boot-forensics/tier3-final-b-diagnosis-context.txt` (commit `f037fed2`, **2026-09-16**): "system_dlkm_b factory V15 exact sha256 300f24c5…". `android17-hidl-fixed-build-20261002/android17-first-stage-mount-contract-20261002.txt` (commit `a0208875`, 2026-10-02) records the same digest for the device's `/dev/block/mapper/system_dlkm_b` from an earlier saved read-only capture. Both predate the incidents. |
| Also used by | PLATFORM-BATCH-04 restoration (`recovery-verified.json`, same digest) |

The image was **not** trusted for its name. It was accepted because:
1. its digest equals two independent records committed before 2026-10-11;
2. all 60 extracted members equal the committed audit SHA-256 and size (SHA-256 preimage).

## Extraction (independent, read-only)

- Tool: AOSP `kernel/prebuilts/build-tools` `e905be252a53d20c52bd9e59df3ff8fdd46b9eab` (tree `e08e74fb`, the pinned
  tree used by the connectivity build), `linux-x86/bin/fsck.erofs`, sha256 `3059e2f0…6e25d`.
- Command: `fsck.erofs --extract=<scratch>/extract-system_dlkm <scratch>/system_dlkm_a.img`, run on a private
  read-only copy (`cp --reflink=never`, `chmod a-w`) under `/home/armol/kernel-work/codex-inventory-integrity/`. Exit 0.
- Result: 68 files, of which 60 are `.ko` under `lib/modules/`. Every member hash is in `evidence/provenance/extract-system_dlkm.SHA256SUMS`.
- `restore-operands.py` repeats the digest check and the extraction itself into a fresh private temporary
  directory every time it runs. It never consumes a pre-existing extraction.

## Other 411 occurrences

vendor_dlkm (215) and vendor_boot platform ramdisk (196) occurrences were never damaged. Their bytes still equal
the committed identities, including the 11 vendor `.BTF` modules that were rewritten byte-identically. They were
reflink-copied unchanged into the isolated operand set and verified there.

## Isolated corrected operand set

- Location: `ulefone-gq5012bf1-research-codex-inventory/workspace/` (git-ignored, worktree-private).
- Built by `cp -a --reflink=always -n` of the canonical `workspace/` and of the 342 other git-ignored canonical
  inputs the validator reads (e.g. `kernel/nothing-module-index.csv`). Copy-on-write means the canonical files were only read.
- Before repair, this isolated tree reproduced the canonical validator result byte-for-byte
  (`evidence/isolated-before/`). After repair it differs from canonical in exactly the 60 restored files
  (`evidence/after/verify-inventory-isolated.json`).

## Damaged copies preserved

- Canonical shared tree: left **as is** (60 stripped files untouched; see `MERGE-INSTRUCTIONS.md`).
- Isolated quarantine: `/home/armol/kernel-work/codex-inventory-integrity/quarantine-isolated/` (60 files) and
  `quarantine-isolated.tar.xz`. Hashes are in `evidence/repair/quarantine-isolated.SHA256SUMS`.
- Batch04 quarantine of the identical bytes: `/home/armol/kernel-work/platform-batch-04-unsigned-stock-quarantine/`.
- The bytes are also deterministically regenerable from authentic stock (`test_in_place_objcopy_strips_signature_and_is_rejected`).
