# MTK-MDP-KERNEL — reconstruction report

Measured 2026-10-08 on a clean checkout of
`android_kernel_modules_mdp_ulefone_gq5012bf1` @ `060689b`, built twice (B1, B2) and
compared against the four stock modules from
`workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/`.

## 1. Acceptance

| module | stock bytes | functions | data objects | imports | exports | KCFI abs ids | relocations | raw differing bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `clk-mt6878-mdpsys.ko` | 15 176 | 3 | 15 | 7 | 0 | 0 | 82 | 20 |
| `mdp_drv_mt6878.ko` | 763 384 | 644 | 135 | 223 | 1 | 8 | 13 581 | 20 |
| `mtk-mml.ko` | 1 894 280 | 695 | 996 | 249 | 36 | 26 | 36 717 | 20 |
| `mtk-mml-mt6878.ko` | 23 128 | 5 | 25 | 15 | 0 | 0 | 209 | 20 |
| **total** | **2 695 968** | **1 347** | **1 171** | **494** | **37** | **34** | **50 589** | **80** |

Every differing byte of every module lies inside `.note.gnu.build-id`
(`clk-mt6878-mdpsys` @0x1fd0, `mdp_drv_mt6878` @0x4ddd0, `mtk-mml` @0xc60d0,
`mtk-mml-mt6878` @0x2ed0; 20 bytes each). `unresolved = 0` for all four.

Classification: **BYTE_EXACT** for all code, data, section content, relocation and ABI
axes; **BUILD_METADATA_ONLY** for the four build IDs; **UNRESOLVED: none**. No
`PROVEN_SEMANTIC_EQUIVALENT` or `COMPILER_ONLY` class was needed — nothing differed.

Machine ledgers: [`function-parity.tsv`](function-parity.tsv) (1 347 rows),
[`data-parity.tsv`](data-parity.tsv) (1 171), `evidence/reconstruction/acceptance/`
→ `sections-parity.tsv` (195 rows: 191 IDENTICAL + 4 BUILD_ID_ONLY),
`abi-parity.tsv` (938 rows), `relocations-parity.tsv.xz` (50 589 rows,
raw **and** semantic), `acceptance.json`.

## 2. What was compared

* **Functions** — every `STT_FUNC` symbol keyed by (section, offset, name, size); byte
  content of each compared. 1 347/1 347 byte-identical; no control-flow difference to
  analyse because no instruction byte differs.
* **Data** — every `STT_OBJECT` keyed the same way, including `.bss` (layout-identical),
  read-only tables, golden/tuning tables, parameter blocks. 1 171/1 171 identical.
* **Sections** — type, flags, size, align, entsize, offset, link, info and full content for
  all 195 sections across the four modules.
* **Relocations** — raw `.rela*` bytes *and* the decoded (offset, type, target symbol name,
  addend) tuples, per section, in both directions.
* **ABI** — 494 `__versions` import CRCs, 37 export CRCs (read through `__crc_<name>` so
  exported *data* is covered, with the `__kcrctab` / `__kcrctab_gpl` licence bucket),
  34 absolute `__kcfi_typeid_*` values, every `.modinfo` key, `vermagic`, `srcversion`.
* **Whole file** — sha256 of the normalized (build-ID-zeroed) image.

`srcversion` is identical for all four modules, so no normalization was needed anywhere
except the build ID.

## 3. Source

Unmodified public ALPS `5e415e059253` (tree `9c61acc3cb0d…`). See [SOURCE.md](SOURCE.md).
Two patches, **9 added files, 0 modified files, 0 C/header edits**:

* `0001-owned-module-build-scope.patch` — 3 `Kbuild` wrappers selecting only the four owned
  modules from the unchanged vendor Makefiles. The mml wrapper also restates
  `mtk-mml-mt6878-objs := mtk-mml-tp-mt6878.o` because the Makefile guards that assignment
  with `$(wildcard $(srctree)/$(src)/…)`, which cannot resolve in an out-of-tree `M=` build.
* `0002-provider-abi-witness-scope.patch` — 6 `Kbuild` files scoping a compile of only the
  sources that *define* the 111 external exports, so their CRCs are produced by genksyms.

Patched tree ids are pinned: `src/kdm` `d715f99efb3e…`, `src/prov` `98fe646c134c…`.

## 4. Determinism

B1 and B2 (each regenerating source trees, kernel output tree and provider ABI from
scratch) are identical for: all 4 raw `.ko`, all 4 stripped `.ko`, all **54** target object
files (including composite and `.mod.o`), the three per-directory `Module.symvers`, the
provider symvers, the CRC witness table, the kout `.config` sha256 and both source tree ids.

## 5. External ABI

111 externally provided exports are consumed; **111/111 CRCs were regenerated from public
source by genksyms and equal the CRCs the stock modules record in `__versions`**. No
symvers file was copied. The remaining 7 cross-module imports (`mtk-mml-mt6878` →
`mtk-mml`) are satisfied inside this component's own modpost run. See
[abi-parity.md](abi-parity.md).

## 6. Scope retained

MDP/MML hardware is reconstructed only at kernel level. The MDP/MML *picture-quality*
algorithms live in vendor userspace (`vendor.mediatek.hardware.mmlpq`,
`pq_aidl-impl.so`, `libaispq.so`) and are **not** reverse engineered. CMDQ, SMI, IOMMU,
MMQoS/ICC, SLBC, mmprofile, AEE, TinySys SCMI, `mtk_sync` and `clk-common` keep their own
owners; only their export ABI was verified here. See
[firmware-boundary.md](firmware-boundary.md).

## 7. Not established

Nothing was executed on hardware. No probe, no DMA, no CMDQ submission, no tile pass, no
interrupt, no reset/timeout path and no power transition was observed. See
[source-to-userspace-contract.md](source-to-userspace-contract.md) §4 for the runtime
acceptance list.
