# Baseline and selection

## Baseline

- **Canonical master:** `0390534d` (KDM-INTEGRATION-01 applied via `ec46467a`). Validator PASS with 0 errors:
  **A385 B1 C10 D8 E0 F0 G54 = 386/458**. Inventory 458/471.
- **Remaining Category D (8):** flashlight, fpsgo, hbt, mali_dmabuf_test_mt6878_r44, msync2_frd, reboot-mode,
  scheduler_ext, syscon-reboot-mode.
- **Concurrent work:**
  - Codex `G-SOURCE-RECOVERY-BATCH-01` (manifest sha256 `9a22e49c…`) freezes 23 **Category G** identities; none of
    the 8 D rows is among them.
  - No other branch manifest lists any of these identities as a target. Substring hits were `mtk_fpsgo.ko` and
    `mtk_mbraink.ko`.

## Frozen (5 identities; manifest sha256 in BATCH-MANIFEST.sha256)

| Module | Domain | Source located |
|---|---|---|
| reboot-mode | NATIVE in-tree, split BTF | `drivers/power/reset/reboot-mode.c`, blob `b4076b10` (identical in GKI 6b18f0b5 and MTK ACK c364c39a) |
| syscon-reboot-mode | NATIVE in-tree, split BTF | `drivers/power/reset/syscon-reboot-mode.c`, blob `e0772c9f` (identical in both) |
| hbt | EXT (`vendor/mediatek/kernel_modules/hbt_driver`) | MiCode `MTK_kernel_modules` `hbt_driver/` (4 public revisions). The Nothing tree has only `hbt_driver_cus/hbt_driver/*` **dangling symlinks** to `../../hbt_driver`. Its `hbt_driver_cus/src/hbt.c` stub (one `hbt` device, no `vhbt`, no `iterate_dir`) is **not** the stock implementation |
| scheduler_ext | EXT (`vendor/mediatek/kernel_modules/sched_cus`) | Nothing kernel_modules `sched_cus/src/sched_main.c` (pure C, MediaTek proprietary licence header, `MODULE_LICENSE("Proprietary")`). It is distinct from the certified in-tree `scheduler.ko` (ALPS `drivers/misc/mediatek/sched`) |
| mali_dmabuf_test_mt6878_r44 | EXT (`vendor/mediatek/kernel_modules/gpu`) | Nothing kernel_modules 580d08ea `gpu/…/mali-r44p1/drivers/base/arm/dma_buf_test_exporter`, the same pin as the certified GPU repo |

## Excluded (with reason)

| Module | Reason |
|---|---|
| flashlight | Retained D. The OEM `flashlight-core.c` variant is unavailable (KDM-MEDIA-SECURITY-BATCH-01 BLOCKERS); the exhausted search is not repeated |
| fpsgo | **Project decision:** `fpsgo_cus` links the MediaTek prebuilt `xgf_v3_ko_quark*.o_shipped`, and only `fpsgo_main.c` is C source. Prebuilt-object repackaging is not source reconstruction, so the row stays D |
| msync2_frd | **Project decision:** `msync2_frd_cus` links the prebuilt `mtk_disp_msync.o_shipped`. Same rule; stays D |

`sched_cus` also contains `cpuqos_ext` and `eas_ext`, which link `*_shipped` objects. They are not stock GQ5012BF1
targets, and the build scope excludes them, so no shipped object enters any output.
