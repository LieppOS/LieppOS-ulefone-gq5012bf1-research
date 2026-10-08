# Evidence index — GPU-AI-AUX-KERNEL-INTERFACES

Authoritative source: `ulefone-gq5012bf1-research/reverse-engineering/accelerator-preparation/GPU-AI-AUX-KERNEL-INTERFACES/`.
TSV files at the pack root are derived metadata, not payloads.

## Preparation (2026-10-08, source HEAD `3bb6db32de2c5f312be31265482a7f8539145b62`)

Coverage-audit tables, stock ELF modules and merged DT, pinned source candidates, processor
inventory and file fingerprints: [handoff](../CLAUDE-HANDOFF.md),
[module inventory](../stock-modules.tsv), [source lineage](../source-lineage.md),
[processors](../processors.tsv). No historical file was moved or deleted.

## Reconstruction (`reconstruction/`)

| Path | Content |
|---|---|
| `acceptance/acceptance.json` | per-module acceptance summary (bytes, hashes, axis counts, residue, `unresolved: 0`) |
| `acceptance/abi-parity.tsv` | 294 rows: every import CRC, export CRC + licence bucket, KCFI type id and `.modinfo` record |
| `acceptance/sections-parity.tsv` | 142 rows: every section header field and content hash, stock vs rebuild (139 IDENTICAL, 3 BUILD_ID_ONLY) |
| `acceptance/relocations-parity.tsv.xz` | 7 867 relocation rows, raw **and** semantic identical |
| `build/clean-checkout-bootstrap.log` | pin fetch + tree-id/sha256 verification of every input |
| `build/b1b2-clean-checkout.log` | full clean-checkout B1/B2 + acceptance transcript |
| `build/B1-SHA256SUMS.txt`, `build/B2-SHA256SUMS.txt` | module and symvers hashes of both builds |
| `build/B1-INTERMEDIATE-SHA256SUMS.txt` | all 22 target `.o`, including composite and `.mod.o` |
| `build/natural-external-provider.symvers` | the 16 externally provided CRCs, source-derived |
| `build/provider-crc-witnesses.tsv` | the exact `.cmd` record each provider CRC came from |
| `build/source-tree-ids.txt` | git tree ids of both assembled source trees |

Root-level measured ledgers: [function-parity.tsv](../function-parity.tsv) (183 rows),
[data-parity.tsv](../data-parity.tsv) (222 rows),
[cross-component-abi.tsv](../cross-component-abi.tsv) (67 consumer→provider edges with
stock consumer CRC vs rebuilt provider CRC, all MATCH).

Maintained source repository: `LieppOS custom ROM/android_kernel_modules_gpu_ai_aux_ulefone_gq5012bf1`
(local only, never pushed). No stock binary, firmware blob or Android payload is stored in
any repository; stock operands and the retained `gpueb.img` / `vcp.img` are referenced by
path and hash only.
