# Display / input scope survey (entry point, not yet closed)

Started immediately after the NFC scope closed. This file records only what was
established in the survey so the next session does not redo it.

## Stock module inventory

| module | partition | size | depends |
|---|---|---:|---|
| `mtk_disp_notify` | vendor ramdisk | 14568 | — |
| `mtk_panel_ext` | vendor ramdisk | 17880 | — |
| `pwm-mtk-disp` | vendor ramdisk | 25200 | — |
| `dbgtop-drm` | vendor ramdisk | 19648 | — |
| `drm_dma_helper` | vendor ramdisk | 30720 | — |
| `drm_display_helper` | vendor ramdisk | 256536 | — |
| `mediatek-drm` | vendor ramdisk | **5719712** | tinysys-scmi, mmprofile, mtk-mml, mtk-icc-core, mtk-cmdq-drv-ext, mtk_dramc, mtk-smi, mtk-mminfra-debug, leds-mtk, aee_aed, mtk-smi-dbg, mmqos-common, mtk_slbc, mtk_sync, vcp_status, mtk-afe-external, iommu_debug, system_heap, drm_dma_helper, mtk_panel_ext, mtk_disp_notify, clk-common, mrdump, mtk-mmdvfs, drm_display_helper |
| `mediatek-drm-gateic` | vendor ramdisk | 78256 | mediatek-drm, leds-mtk |
| `mediatek-drm-panel-drv` | vendor ramdisk | 358856 | mediatek-drm, mediatek-drm-gateic, mtk_panel_ext |
| `panel-ky-vtdr6115-dphy-cmd` | vendor ramdisk | 246288 | mtk_panel_ext, mediatek-drm |
| `leds-mtk-disp` | vendor ramdisk | 19216 | mediatek-drm, mtk_panel_ext, mediatek-drm-gateic, rt4831a_drv, leds-mtk |
| `focaltech_touch_spi_ft3680` | vendor_dlkm | 400936 | yft_tpd_gesture, **mtk_disp_notify**, yft_devinfo |
| `hynitron` | vendor_dlkm | 142528 | yft_devinfo |
| `spi_tiny_co5300_lcd` | vendor_dlkm | 323128 | yft_devinfo, **hynitron** |
| `mtk_disp_sec` | vendor_dlkm | 27880 | mtk-cmdq-drv-ext, cmdq-sec-drv, mediatek-drm, mtk_sec_heap |
| `backlight_cooling` | vendor_dlkm | 16232 | leds-mtk |
| `leds-ln2403` | vendor_dlkm | 39344 | mtk-pwm |
| `touch_boost` / `mtk_ioctl_touch_boost` | vendor_dlkm | 111080 / 18416 | scheduler, powerhal_cpu_ctrl, mtk_perf_ioctl… |
| `met_backlight_api` | vendor_dlkm | 11320 | met, leds-mtk, mtk_printk_ctrl |

Notable structure facts:

- the **main panel driver is `panel-ky-vtdr6115-dphy-cmd`** (KY VTDR6115, DSI
  command mode), sitting on `mtk_panel_ext` + `mediatek-drm`;
- the **rear display is `spi_tiny_co5300_lcd`**, and it **depends on
  `hynitron`** — i.e. the rear panel driver and the rear touch controller are
  coupled in one SPI/I²C sub-stack (already a DONE component:
  `HYNITRON-REAR-TOUCH`);
- the **main touch is `focaltech_touch_spi_ft3680`** and it depends on
  `mtk_disp_notify` + the YFT gesture/devinfo modules (both already DONE:
  `YFT-TPD-GESTURE`, and `YFT-DEVINFO` is PARTIAL);
- `mtk_disp_notify` is the glue every suspend/resume-aware driver uses
  (sensorhub, focaltech touch) and has **no dependencies** — the cheapest
  first target.

## Build-system finding (blocking the first target)

`mtk_disp_notify.c` exists twice in the KDM tree:

- `drivers/gpu/drm/mediatek/dummy_drm/mtk_disp_notify.c`
- `drivers/gpu/drm/mediatek/mediatek_v2/mtk_disp_notify.c`

Building `M=.../dummy_drm` with the vendor config fails because the same
directory also builds `mtk_panel_ext.o`, which does not compile in that
configuration (`1 error generated` on `mtk_panel_ext.o`). The shipped
`mtk_disp_notify.ko` has `depends=` empty, so it is a standalone single-object
module — the next step is to build it in isolation (scratch Kbuild dir with
`obj-m := mtk_disp_notify.o` plus the right include/`ccflags`), or to fix the
`mtk_panel_ext` configuration first and build the whole `dummy_drm` set.

## Suggested order for the next session

1. `mtk_disp_notify` (14.5 KB, no deps) — unblocks the `MTK-DISP-NOTIFY`
   PARTIAL component and is a dependency of touch and sensorhub.
2. `mtk_panel_ext` (17.9 KB, no deps) — needed by the panel and backlight path.
3. `panel-ky-vtdr6115-dphy-cmd` — panel command tables, power/reset sequencing,
   modes/refresh rates, ESD recovery (existing work: `lieppos/panel-vtdr6115-recon`,
   `panel-vtdr6115-donor-red`, `panel-vtdr6115-provider-harness`).
4. `focaltech_touch_spi_ft3680` — existing work: `lieppos/focaltech-ft3680-recon`
   plus two analysis scripts.
5. `spi_tiny_co5300_lcd` (rear display) — pairs with the already-DONE
   `HYNITRON-REAR-TOUCH`.
6. `mediatek-drm` (5.7 MB, 25 dependencies) — last; it is the largest single
   module on the device.
