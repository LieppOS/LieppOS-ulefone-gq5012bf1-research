# Evidence index — MTK-MDP-KERNEL

Authoritative source: `ulefone-gq5012bf1-research/reverse-engineering/accelerator-preparation/MTK-MDP-KERNEL/`.
TSV files at the pack root are derived metadata, not payloads.

## Preparation (2026-10-08, source HEAD `3bb6db32de2c5f312be31265482a7f8539145b62`)

Coverage-audit tables, stock ELF modules and merged DT, pinned source candidates and file
fingerprints: [handoff](../CLAUDE-HANDOFF.md), [module inventory](../stock-modules.tsv),
[source lineage](../source-lineage.md). No historical file was moved or deleted.

## Reconstruction (`reconstruction/`)

| Path | Content |
|---|---|
| `acceptance/acceptance.json` | per-module acceptance summary (bytes, hashes, axis counts, residue, `unresolved: 0`) |
| `acceptance/abi-parity.tsv` | 938 rows: every import CRC, export CRC + licence bucket, KCFI type id and `.modinfo` record |
| `acceptance/sections-parity.tsv` | 195 rows: every section header field and content hash, stock vs rebuild (191 IDENTICAL, 4 BUILD_ID_ONLY) |
| `acceptance/relocations-parity.tsv.xz` | 50 589 relocation rows, raw **and** semantic identical |
| `build/clean-checkout-bootstrap.log` | pin fetch + tree-id/sha256 verification of every input |
| `build/b1b2-clean-checkout.log` | full clean-checkout B1/B2 + acceptance transcript |
| `build/B1-SHA256SUMS.txt`, `build/B2-SHA256SUMS.txt` | module and symvers hashes of both builds |
| `build/B1-INTERMEDIATE-SHA256SUMS.txt` | all 54 target `.o`, including composite and `.mod.o` |
| `build/natural-external-provider.symvers` | the 111 externally provided CRCs, source-derived |
| `build/provider-crc-witnesses.tsv` | the exact `.cmd` record each provider CRC came from |
| `build/source-tree-ids.txt` | git tree ids of both assembled source trees |

Root-level measured ledgers: [function-parity.tsv](../function-parity.tsv) (1 347 rows),
[data-parity.tsv](../data-parity.tsv) (1 171 rows),
[dt-topology.tsv](../dt-topology.tsv) (22 device-tree nodes, machine-extracted from the
merged DTB).

Maintained source repository: `LieppOS custom ROM/android_kernel_modules_mdp_ulefone_gq5012bf1`
(local only, never pushed). No stock binary, firmware blob or Android payload is stored in
any repository; stock operands are referenced by path and hash.
