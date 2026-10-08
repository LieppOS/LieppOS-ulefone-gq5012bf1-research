# MALI-GPU-KERNEL — final report (2026-10-08)

## Module table

| Module | Stock functions | Exact functions | Semantic-equivalent residuals | Unresolved | Data parity | CRC/KCFI | Deterministic build | Status |
|---|---|---|---|---|---|---|---|---|
| mali_kbase_mt6878_r44 | 1826 | 1826 | 0 | 0 | 672/672 objects + all sections; `.modinfo` `srcversion` differs (provenance) | 443+145 CRC, 98 KCFI = | B1 == B2 | DONE |
| mali_mgm_mt6878_r44 | 58 | 58 | 0 | 0 | 34/34; srcversion = | 43 CRC, 3 KCFI = | B1 == B2 | DONE |
| mali_prot_alloc_mt6878_r44 | 8 | 8 | 0 | 0 | 17/17; srcversion = | 16 CRC = | B1 == B2 | DONE |
| ged | 666 | 666 | 0 | 0 | 756/756 | 230+100 CRC, 9 KCFI = | B1 == B2 | DONE |
| mtk_gpu_hal | 46 | 46 | 0 | 0 | 52/52 | 10+44 CRC = | B1 == B2 | DONE |
| mtk_gpu_qos | 12 | 12 | 0 | 0 | 22/22 | 32+4 CRC, 4 KCFI = | B1 == B2 | DONE |
| mtk_gpufreq_wrapper | 93 | 93 | 0 | 0 | 70/70 | 69+40 CRC, 5 KCFI = | B1 == B2 | DONE |
| mtk_gpufreq_mt6878 | 39 | 39 | 0 | 0 | 49/49 | 31 CRC = | B1 == B2 | DONE |

"Exact" means byte-identical bodies at identical section offsets. No function needed a
semantic-equivalence argument.

## 1. Donors

* **NothingOSS `android_kernel_modules_nothing_mt6878`** `580d08eac018`, mali r44p1, with
  `mali_kbase_mem_migrate.[ch]`, `mmu/mali_kbase_mmu.c` and
  `backend/gpu/mali_kbase_pm_driver.c` taken from `c3d070e9f373`.
* **NothingOSS `android_kernel_device_modules_6.1_nothing_mt6878`** `957dac185efe` for
  hal and gpu_bm.
* **MT6878 ALPS `5e415e059253`** (local archive `2ae742fda9cd`) for ged, gpufreq, and the
  external-provider CRC derivation.

Details: `source-lineage.md`.

## 2. Toolchain

* clang `r487747c` 17.0.2 / lld; GKI common `6b18f0b574ab`.
* Config: `gki_defconfig` + `mgk_64_k61_defconfig`, release
  `6.1.115-android14-11-g945dff7bc1bf`.
* KCFLAGS: `-D__ANDROID_COMMON_KERNEL__ -faddrsig` plus `-fmacro-prefix-map` to the stock
  `../kernel_device_modules-6.1` and `../vendor/mediatek/kernel_modules/gpu`.
* Install step: `--strip-debug`.

Details: `build-reproduction.md`.

## 3. Device-specific patches

None in code (`board-specific-deltas.md`). The MediaTek integration is entirely in the
public donors. The only reconstruction step beyond picking a revision is the file-level
graft of MTK's own rc-V11.24 page-migration fix and `pm_driver.c` onto 580d08e.

## 4. Function and data parity

* 2748/2748 function symbols are byte-identical.
* All data objects are identical, as are all sections except build-id, plus kbase
  `.modinfo`.

Ledgers: `function-parity.tsv`, `data-parity.tsv`, `parity/acceptance/section-parity.tsv`.

## 5. Imports, exports and modversions

* 874 imports, 333 exports and the `__versions` bytes are identical.
* All 30 external-provider CRCs are regenerated from public source and equal stock.
* All stock consumers outside the component import owned exports with matching CRCs.

Details: `abi-kmi-parity.md`.

## 6. KCFI

* 119/119 `__kcfi_typeid_*` match.
* The per-function type hashes and call-site check constants are inside the byte-identical
  `.text`.

## 7. Relocations, sections and modinfo

* 104 RELA sections and 48 981 entries are identical, both semantically and as raw bytes.
* `.modinfo` is identical except kbase `srcversion`.

Details: `relocation-parity.md`.

## 8. DT, clock, power and MMU contract

| node | role |
|---|---|
| mali@13000000 | 5 DT IRQs; the CSF driver uses JOB/MMU/GPU |
| mgm | memory group manager |
| protected-memory-allocator@13c3f000 | GPUEB GPR 0xd1c/6, 2 MiB reserve, 4 MiB GMPU |
| ged | GED driver node |
| gpufreq-wrapper | `gpueb-support=1` |
| gpufreq@13fbf000 | 15 MFG reg ranges; vgpu = mt6319 vbuck2, vsram = vsram-cpum |
| gpu-qos / gpu-fdvfs | looked up, not bound |
| g3d-brisket ×3 | unused by Linux |

* OPP table: 46 points.
* The GPU MMU is kbase-internal; there is no SMMU.

Details: `dt-hardware-contract.md`, `gpu-power-management.md`.

## 9. Android userspace ABI

* `/dev/mali0` (0666 system:graphics, `gpu_device`): 54 dispatched kbase ioctls, UK 1.21.
* `/proc/ged` bridge: `_IOWR('g', id, GED_BRIDGE_PACKAGE)`, ids 0–16, 100–107, 200.
* `/d/ged/hal/*`, `/proc/gpufreqv2`, and the kbase sysfs attributes.

Details: `userspace-kernel-abi.md`, `abi/kbase-ioctls.tsv`.

## 10. Firmware and proprietary boundaries

* `mali_csffw.bin` (sha256 `81bef764…`, header magic `0xC3F13A6E` v0.3) is loaded and
  header-checked by kbase. There is no kernel signature check; integrity comes from
  vendor verity.
* GPUEB firmware and its IPI protocol, `gpueb.ko` (GPU-AI-AUX-KERNEL-INTERFACES), the Mali
  userspace blobs and secure-memory components are retained or owned elsewhere.

Details: `firmware-boundary.md`.

## 11. Reachability (existing read-only capture, no new device interaction)

| module | `/proc/modules` | bound device / interface |
|---|---|---|
| mali_kbase | Live, refcount 49 | `mali` → `13000000.mali`, `/dev/mali0`, devfreq, IRQs 437–439 |
| mali_mgm | Live, 1 | `physical-memory-group-manager` → `mgm` |
| mali_prot_alloc | Live, 1 | → `13c3f000.protected-memory-allocator` |
| ged | Live, 4 users | → `soc:ged`, `/proc/ged` |
| mtk_gpu_hal | Live, 8 users | function-pointer hub, no DT |
| mtk_gpu_qos | Live, 1 user (ged) | DT lookup only |
| mtk_gpufreq_wrapper | Live, 7 users | → `gpufreq-wrapper`, `/proc/gpufreqv2` |
| mtk_gpufreq_mt6878 | Live, 0 | → `13fbf000.gpufreq` |

## 12. Remaining differences

* Build-id: 20 bytes per module.
* kbase `srcversion`: a source-text hash. It needs MTK's unpublished rc-V10.29 text, which
  differs from the reconstruction only in non-compiled text.

## 13. B1/B2

`scripts/build_b1_b2.sh` wipes the trees and rebuilds from `git archive`. All `.ko`,
stripped `.ko` and `Module.symvers` are identical
(`parity/b1b2/B{1,2}.SHA256SUMS`).

## 14. Commits

* Research repository: see the git log (checkpoints 1–3).
* Source trees: isolated git repos at
  `/home/armol/kernel-work/accelerator-mali-gpu-kernel/build/{kdm,gpu}`; their patches are
  copied into `patches/`.

## 18. Runtime-only validation still open

* GPU_ID and core mask;
* DVFS, thermal and low-battery behaviour;
* protected-mode execution, suspend/resume and fault recovery on hardware;
* loading the rebuilt modules (not done, by policy).
