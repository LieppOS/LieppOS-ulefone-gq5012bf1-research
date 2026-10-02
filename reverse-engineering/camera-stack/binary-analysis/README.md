# binary-analysis — imgsensor.ko stock vs reconstruction

Stock: `vendor_dlkm/lib/modules/imgsensor.ko` sha256 `9243061cec77e96e…3558`.
Rebuilt: `reconstruction/imgsensor/build/build.sh … parity`, stripped
(`llvm-strip --strip-debug`), same size 1 140 880 B.

| file | what | regenerate |
|---|---|---|
| `imgsensor-function-parity.tsv` | all 619 functions: size, bytes, relocations (symbolic), KCFI hash, class | `scripts/imgsensor_parity.py <stock> <rebuilt.ko> <srcdir> --tsv …` |
| `imgsensor-data-parity.tsv` | all 394 data objects, per object, relocations symbolic | same with `--data` |
| `imgsensor-abi-section-parity.tsv` | every section incl. RELA (normalised by symbol), symtab set, modinfo key/values, KCFI words, `__versions`, ksymtab/kcrctab | `scripts/abi_parity.py <stock> <rebuilt.stripped.ko> --tsv …` |
| `imgsensor-byte-diff.tsv` | every differing byte of the whole file with section/symbol | inline script in session log; trivial `cmp` + section map |
| `imgsensor-framework-before-after.tsv` | the 62 framework-survey functions that were not identical with NothingOSS (+slot): 26 ODM-modified (one, `ov64b_seamless_switch`, is donor-only and absent from stock) and 36 stock-only, with their final class | join of `../kernel-imgsensor-framework-parity-recon.tsv` and the function TSV |
| `imgsensor-corrected-vs-stock-data.tsv` | CORRECTED build vs stock: only `mode_struct` of 7 sensors and the frame-descriptor arrays they reference | `--data` on the corrected build |

## Classes

`EXACT` = identical size, bytes, relocations (by symbol/string content) and KCFI word.
`EXACT-CODE` = identical except intra-TU branch displacement (none left).
`UNRESOLVED` = anything else.

## Totals

* functions 618/619 EXACT; data 394/394 EXACT;
* sections 61/63 identical (normalised), `__versions`, `__ksymtab*`, `__kcrctab`,
  `.modinfo`, `.symtab` (set), `.llvm_addrsig`, KCFI words: identical;
* whole file: 70 bytes differ.

## Residual differences (each explained)

| bytes | where | cause | effect |
|---|---|---|---|
| 49 | `.text` `yft_ctrl_nightled_by_idx` +0x60…+0xa8 | stock compares `nightled_is_open` against the full `int state` (`ccmp`) and stores that predicate; our clang derives `state ∈ {0,1}` from the two constant call sites (identical in stock) and emits `cbz/cmp #1`. Source form that defeats the range proof without altering the caller was not found (see reconstruction README for variants tried). | none — same truth table, same stores, same calls |
| 1 | `.rela.text` | offset of the `nightled_is_open` LDST8 relocation moves by 4 inside that function | none |
| 20 | `.note.gnu.build-id` | content hash: follows the 50 bytes above; additionally lld hashes the *unstripped* image whose DWARF contains build paths | not loaded by the kernel |

No ABI-relevant difference: modversions CRCs, exported symbol + CRC
(`fs_sync_frame`), imported symbol set, vermagic, depends, KCFI type hashes
and every relocation target are identical, so the rebuilt module is a drop-in
for the stock one on the stock GKI kernel.

## Corrected build

`build.sh … corrected` changes data only (see
`../reconstruction/imgsensor/README.md#stock-parity-vs-corrected`). It must not be
used for parity measurements. Its functions compare to stock exactly like the parity
build's (618/619, same single residual), i.e. the correction touches no code.
