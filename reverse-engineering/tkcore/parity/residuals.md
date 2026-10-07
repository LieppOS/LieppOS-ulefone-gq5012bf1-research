# tkcore_drv.ko parity residuals

Operands:

- **A** = stock `vendor_boot:/lib/modules/tkcore_drv.ko`, 63 480 B,
  sha256 `c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d`, build-id `8e73e9f92105915fe497b6c4cfbfffaf7b3fb2d9`.
- **B** = `scripts/build_tkcore_drv.sh clean` (exact GKI 12901745, clang r487747c), then
  `llvm-strip --strip-debug`. Unstripped sha256 `abcc08ea85b7686b2b06e8573c2b6f77618251b62b7f76b7c19f0ecdc0453843`; stripped `29cf90d179219e22d1aa432e75d2d977bf06d21007ca709e17102786db218065`, 63 480 B,
  build-id `4a3780444b4ceb462c57f85ec8007a115b0abb98`.
- Two clean builds through the script: **B1 == B2** (byte-identical, also identical to the
  interactive build).

| axis | result |
|---|---|
| file size | 63 480 = 63 480 |
| whole-file byte diff | 41 bytes: 21 in `.modinfo` (srcversion), 20 in `.note.gnu.build-id` |
| sections | 44/44, same names/sizes/flags; 34/34 content sections byte-identical (ko-pair-parity) |
| functions | **50/50** present, 50/50 same size, **50/50 byte-identical** |
| data objects | 18/18 (ko_parity) / 29/29 (ko-pair-parity) byte-identical except `__UNIQUE_ID_srcversion` |
| strings | `.rodata.str1.1` 65 entries, `.rodata` 581 entries identical; ko-str-refs: 0 A-only / 0 B-only literals |
| imports | 66/66 |
| `__versions` | 67/67 CRC-equal (`parity/modversions.tsv`) |
| exports | 0/0 |
| KCFI | 46/46 type-id preambles equal, all 46 named (`parity/kcfi-parity.tsv`); the 4 others are static, non-address-taken |
| relocations | 717/717 semantically and raw-byte identical across 11 rela sections |
| `__bug_table` | 43/43 entries identical incl. `__LINE__` (`parity/bug-table-parity.tsv`) |
| `.altinstructions` | identical (2 entries; `alt_cb_patch_nops` from LSE atomics in `atomic_inc`/`atomic_dec_if_positive` — resolves the old "codegen residual") |
| `.modinfo` | author, description, version, license, vermagic, name, depends=`tkcore,ffa_v10` identical; **srcversion differs** |
| residue tools | ko-residue-diff: no stock-source residue; ko-str-refs: no literal residue |

## R1 — srcversion: PATH/PROVENANCE

`srcversion` is the MD4 of the armtz sources and same-directory headers as a token stream
(modpost `sumversion.c`: whitespace and `/* */` comments skipped, strings kept). It differs
because our text is the public 7:2.2 file plus a reconstructed delta, not TrustKernel's 6:1.1
text (which may contain different dead code, macros, `#if` branches or `//` comments). It has
no influence on generated code; every code/data/relocation byte is identical.

## R2 — `.note.gnu.build-id`: BUILD-ID

Hash of the linked object; differs by construction (20 bytes).

## R3 — DWARF: DEBUG

Only in the unstripped rebuild; stock is shipped stripped.

## Provider-CRC provenance (not a residual)

The 11 tkcore CRCs in `__versions` are the stock `tkcore.ko` `__kcrctab` values
(`source/stock-tkcore.symvers`), exactly as the stock modpost saw them: a consumer's
modversion is a property of the provider export, and `tkcore.ko` is a separate component
(TRUSTKERNEL-TEE). The 2 `ffa_v10` CRCs come from the source-built FFA-V10 module. 6 of the 11
tkcore CRCs are additionally regenerated naturally from the public 7:2.2 core
(`source-lineage.md`).

No other residual exists. Earlier residuals are closed: `alt_cb_patch_nops` (now imported
naturally), `run_tee_task` KCFI `0xc2052128` = `_ZTSFvP6tee_tzP19invoke_tee_responseP21tee_task_cpu_affinityE`
(the struct tags were `invoke_tee_response` / `tee_task_cpu_affinity`, not in the 3,690 guessed spellings).
