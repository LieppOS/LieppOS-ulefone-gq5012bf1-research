# Source lineage — MALI-GPU-KERNEL (measured, 2026-10-08)

Every module is rebuilt from **public** source with a pinned revision. The parity column
is measured on the stripped clean build B1 against stock (`function-parity.tsv`,
`data-parity.tsv`, `parity/acceptance/`).

| Module | Classification | Donor (exact) | Parity |
|---|---|---|---|
| `mtk_gpu_hal.ko` | DIRECT_SOURCE_MATCH | NothingOSS `android_kernel_device_modules_6.1_nothing_mt6878` `957dac185efe` `drivers/gpu/mediatek/hal` (identical in ALPS 5e41) | whole file = stock except the build-id |
| `mtk_gpu_qos.ko` | DIRECT_SOURCE_MATCH | same tree, `drivers/gpu/mediatek/gpu_bm` (identical in ALPS 5e41) | whole file = stock except the build-id |
| `mtk_gpufreq_wrapper.ko` | DIRECT_SOURCE_MATCH | MT6878 ALPS `5e415e059253` (NothingOSS device_modules, mt6878/*/16b) `drivers/gpu/mediatek/gpufreq` | whole file = stock except the build-id |
| `mtk_gpufreq_mt6878.ko` | DIRECT_SOURCE_MATCH | same as above | whole file = stock except the build-id |
| `ged.ko` | DIRECT_SOURCE_MATCH | ALPS `5e415e059253` `drivers/gpu/mediatek/ged` | whole file = stock except the build-id |
| `mali_mgm_mt6878_r44.ko` | DIRECT_SOURCE_MATCH | NothingOSS `android_kernel_modules_nothing_mt6878` `580d08eac018` `gpu/gpu_mali/mali_avalon/mali-r44p1/drivers/base/arm/memory_group_manager` | whole file = stock except the build-id; **srcversion reproduced** |
| `mali_prot_alloc_mt6878_r44.ko` | DIRECT_SOURCE_MATCH | same tree, `.../protected_memory_allocator` | whole file = stock except the build-id; **srcversion reproduced** |
| `mali_kbase_mt6878_r44.ko` | DONOR_PLUS_DEVICE_PATCHES (file-level graft of two public revisions) | `580d08eac018` + 4 files from `c3d070e6155c` (`mali_kbase_mem_migrate.[ch]`, `mmu/mali_kbase_mmu.c`, `backend/gpu/mali_kbase_pm_driver.c`) | every function/data/relocation/ABI byte = stock; residue is the build-id plus `srcversion` (see below) |

**Maintained source:** `android_kernel_modules_gpu_ulefone_gq5012bf1`, which holds the pins,
the complete patch series and a clean-checkout build. See `SOURCE.md`, for full commit ids
(`c3d070e` = `c3d070e6155c9f373224fa2b17027d07583c37bc`) and the verification record.

The original working trees (`/home/armol/kernel-work/accelerator-mali-gpu-kernel/build/{kdm,gpu}`)
and their exported patches (`patches/`) are historical; `parity/source-manifest.tsv` records
their files by git blob. `evidence/source-preservation/tree-equivalence.md` shows that they
equal the pins + patches.

## How each lineage was established

* **Qwen's starting candidate was wrong for 5 of 8 modules.**
  * NothingOSS `kernel_modules@5f75a3b` (Tetris/u, the only branch checked out locally)
    gives MGM 26/58 and kbase 1122/1819 identical functions.
  * NothingOSS `device_modules@957dac` misses 6 exports in `ged` and `mtk_gpufreq_wrapper`
    (`ged_gpu_is_heavy`, `ged_set_apo_wakeup_ns[_nolock]`, `gpufreq_get_cur_temperature`,
    `gpufreq_pdca_polling_ack`), and gives a CRC-mismatched `gpufreq_register_gpufreq_fp`
    import.
* **ALPS 5e41** (Qwen's "alternative pinned candidate") is exact for `ged` and `gpufreq`.
  The `hal` and `gpu_bm` sources are identical in both trees.
* **Mali r44p1.** The local bare clone `public-mtk/nkm.git` holds every published NothingOSS
  branch. I built every revision that touched `mali-r44p1`, all 7 that compile:

  | revision | MGM identical | kbase identical |
  |---|---|---|
  | 2115d27 / 2ed40ed / 0c8f774 / 393d30c | 46/58 | 1763–1767/1819 |
  | **580d08e** | **58/58** | 1812/1819 |
  | c3d070e / 02bc041 | 58/58 | 1783/1819 |
  | 9e2df1f / 59690e7 / d1fba3b | — | do not compile (`MIN`/`MAX`) |

  The seven kbase residues at 580d08e were exactly the page-migration functions changed in
  c3d070e (`kbase_mmu_init`, `kbase_mmu_insert_single_page`, `mmu_teardown_pages`, …, plus
  the export `kbase_migrate_page_allocated_mapped`). The other c3d070e changes
  (GPU-frequency trace, `idle_on_stop`, freezing checks, 500 ms dump timeouts) are absent
  from stock. Grafting the c3d070e `mem_migrate`/`mmu` files gave 1819/1819 functions.
  The c3d070e `pm_driver.c` (a `lockdep_assert_held` + 2 lines) moves every later
  `__bug_table` line by exactly the stock offset (+2 for line ≥ 1166), which made
  `__bug_table` byte-identical.
* Stock kbase `.modinfo` says `version=r44p1-01eac0`. The stock vendor `build.prop` declares
  `ro.vendor.mediatek.version.release=alps-mp-u0.mp1.rc-V10.29_esun.u0mp1rc.k6989v1.64_P8`
  (no module string carries it). That release is not published. The two NothingOSS
  revisions bracket it: 580d08e is V9.9-era, c3d070e is rc-V11.24.
* The external MiCode trees `MTK_kernel_modules` `malachite-u-oss` (62e229f) and
  `lapis-v-oss` (9f8716d) were fetched only to test the srcversion residue. Both are
  further from stock (kbase 1121 and 1137 identical functions), so they are not the lineage.

## kbase `srcversion`: exactly what remains

`srcversion` is modpost's MD4 over the *source text* (whitespace and `/* */` stripped;
`//` comments, string literals and `#if 0` text count).

* `scripts/srcversion.py` reproduces modpost bit-for-bit, validated on 9 builds and against
  a harness compiled from the exact GKI `sumversion.c`
  (`tools/sv/build.sh`; note that modpost's MD4 is byte-swapped relative to RFC 1320).
* The stock MGM and prot_alloc srcversions are reproduced exactly. kbase is `0BDF5EC8…` vs
  stock `2DB292FC…`.
* `parity/srcversion-search.txt` records the 4096 + 360 file-combination searches over
  every published revision; none reproduces it.
* **Proven consequence:** every compiled byte is identical. That covers all 1826 function
  symbols, all 672 other data objects, all sections except `.modinfo`/build-id, all 21
  relocation sections, 443 import and 145 export CRCs, and 98 KCFI type IDs. So the
  unpublished V10.29 text differs from the reconstruction only in text this configuration
  does not compile: comments, `#if`-disabled code, and the `CONFIG_PAGE_MIGRATION_SUPPORT=n`
  stubs.
* **Not proven:** the exact wording of that text. It has no behavioural effect in the
  stock build configuration.

## Toolchain and provenance

* Android clang `r487747c` (17.0.2, build 10087095); stock `.comment` is identical.
* GKI common `6b18f0b574ab`. Vendor kout: `gki_defconfig + mgk_64_k61_defconfig`, stamped
  `6.1.115-android14-11-g945dff7bc1bf` (= stock vermagic).

See `build-reproduction.md`.
