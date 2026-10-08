# Binary and ABI parity — APUSYS-NPU-KERNEL

Proof operands are stock vendor_dlkm modules and stripped B1 modules from the fresh clone. The occurrence-aware verifier keys same-named statics by section/offset/name/size; the older name-keyed summary undercounted duplicate local functions.

| Module | Stock SHA-256 | Defined functions | Data objects | Imports | Exports | KCFI IDs | RELA entries | Unresolved |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `apu_top.ko` | `260d2bba5e481bae3228398aa85018c14b09dda795962b379a772daa05758469` | 343 | 330 | 180 | 21 | 19 | 9,752 | 0 |
| `apusys.ko` | `d74f1d4bddef24cea1cbeb36aba906632f3dbede51e8e3957287b7c35d78d8b6` | 1,965 | 1,313 | 375 | 11 | 152 | 46,647 | 0 |

## Verdict by axis

* **Functions:** every defined `STT_FUNC` occurrence is byte-identical; no equivalent/compiler-only/unresolved body.
* **Data:** every defined object, initialized byte, BSS size, operation table, and alignment is identical.
* **Imports/modversions:** names, ordered `__versions` entries, and CRCs are identical (180/180 and 375/375). Thirteen external vendor CRCs were independently generated from provider source and equal the stock consumer records.
* **Exports:** names, GPL bucket, order, and CRCs identical (21/21 and 11/11).
* **KCFI:** every absolute `__kcfi_typeid_*` name/value identical (19 and 152); because normalized files are otherwise identical, instrumented entry and indirect-call bytes also match.
* **Relocations:** every raw RELA byte and semantic tuple `(offset,type,target,addend)` identical across 9,752 and 46,647 entries.
* **Sections/symbols/strings/modinfo:** section headers, offsets, sizes, contents, symbol/string tables, aliases, dependencies, vermagic, compiler record, and source paths identical.
* **Whole file:** equal size; only the 20-byte GNU build-ID descriptor differs (`apu_top` file offset 231632, `apusys` 1024336). Zeroing that descriptor makes the entire files byte-identical. This is build-path provenance, not executable behavior.
* **Determinism:** clean B1/B2 raw and stripped modules, all target object intermediates, target/provider symvers, generated provider CRC witnesses, config, and source tree are byte-identical.

| Module | Stock bytes | B1 stripped SHA-256 | Normalized SHA-256 | Raw differing bytes |
|---|---:|---|---|---:|
| `apu_top.ko` | 538,192 | `0802b9000e9839f4a9c249c8dff335b9cc7ec28096faa083098d76926cd046f1` | `28c552c416a57d4ca60777d8556a4b19ee6c448885ca21556c6c92c6039571ac` | 20 (build ID) |
| `apusys.ko` | 2,465,176 | `69f11c54ff57c7bc7a858dd21a3ecdba5ceef2527896d2b9147909ce4fa8254b` | `efc473e4b2002c66625efcfe8d9ccaa62c4c0c319b46d77e6a7e229e108b0cc9` | 20 (build ID) |

Machine-readable complete ledgers are in `evidence/reconstruction/acceptance/`; build hashes, provider witnesses, and the complete clean-build log are in `evidence/reconstruction/build/`. No stock compiled byte was inserted into any object.
