# Review of the committed ELF proofs

## Stage A — REMAINING-KERNEL-SOURCE-BATCH-01

- **Commits:** research `026ee41047a84f2252f0c724008c7eb3ab43e2d8`, source
  `7e07384a96580bef13ff3f075355c20b4305a4da` (clean).
- **Bundle:** a fresh `--no-hardlinks` clone of `remaining-kernel-source.bundle` gives the same tree as the repo,
  with `fsck --full` clean.
- **Rows:** the five audit rows were D with matching stock SHA256 before the CAS.
- **Proof:** B1/B2 5/5 whole-file acceptance; 69 + 69 ELF mutations; 10/10 outputs and 13/13 intermediates
  identical; the source-built OEM BTF base `cafe5987…` identical in both builds.

## Stage B — G-SOURCE-RECOVERY-BATCH-01

| Family | Repo commit | Bundle sha256 OK | Fresh clone == repo tree | B1 == B2 outputs | B1 == B2 intermediates | Objects compared | Whole-stock | ELF mutations B1/B2 |
|---|---|---|---|---|---|---:|---|---|
| camera_lens | 082e1a29fbe7… | yes | yes | 14/14 | 16/16 | 93 | 7/7 PASS | 91/91 PASS |
| modem_interfaces | 152ba718f988… | yes | yes | 14/14 | 69/69 | 146 | 7/7 PASS | 93/93 PASS |
| secure_transport | 009294902944… | yes | yes | 18/18 | 57/57 | 134 | 8 PASS + tmem_ffa REJECT (not waived) | 109/109 PASS |

Totals: 46 output files, 373 compared objects and **586 mutation controls**, matching Codex's report.

- **No packaged machine code:** none of the three repositories tracks any `.ko`, `.o`, `.o_shipped`, `.a`, `.bin`
  or `.elf` file (28, 27 and 34 tracked files respectively). Every A target is compiled from pinned source.
- **Exact fields:** every A row in `BATCH-PARITY.tsv` reads `CRC_AND_KCFI_EXACT`,
  `<n>_RAW_AND_SEMANTIC_EXACT` and `GNU20_ONLY`. CRCs, KCFI type IDs, modinfo and relocations are compared byte for
  byte by the unchanged strict verifier.
- **Builds:** every build uses vendor config `b826d842…`; target source trees are identical between B1 and B2 in
  each family.
- **tmem_ffa:** 141/141 functions byte-identical; 59/60 data objects (only `____versions` differs); KCFI and 2,208
  raw and semantic relocations exact. The whole-stock check **rejects** it; it is recorded as C with
  `FOUR_NATURAL_IMPORT_CRCS_NOT_WAIVED` (see TRUSTKERNEL-ABI-BOUNDARY.md).
