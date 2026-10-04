# Display / input scope survey (entry point)

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

## Status after the mediatek-drm pass (2026-10-04)

See [`mediatek-drm/`](mediatek-drm/).

- **`mediatek-drm.ko` is exact.** It rebuilds as 2376/2376 functions,
  2072/2072 data, 542/542 imports, 52/52 exports with 51/51 export CRCs, and
  569/569 modinfo. All 70 sections match except `.note.gnu.build-id`, the
  symtab is identical, and B1==B2 is file-identical.
- Base is MTK ALPS `5e415e059253` (NothingOSS mt6878 history, 2025-02-25)
  plus 10 proven GQ5012BF1 patches: the FP-HBM `ddic_dsi_send_cmd_for_fp`
  (`__weak`, exported), the `DSI_GET_AOD_STATE` io_cmd with ESD skip in AOD
  doze, the AOD `force_high_step`, the doze DSI buffer/mmclk handling, disp-pwm0/1
  with PWM0, the DP AUX refine, MT6989 dead-code variants, and source-line padding.
- Object composition is 66 objects, all mapped by symbol name and link order,
  and all exact.
- **`mediatek-drm-panel-drv` is 123/123 and exact except build-id.** The
  "private `mtk_lcm_*` layout" was `struct mtk_panel_params` from the wrong
  (Nothing-tip) `mtk_panel_ext.h`.
- **`mtk_panel_ext.ko` export CRCs are now 9/9.** Five used to mismatch. With
  the ALPS header, every section except build-id matches.
- Workspace: new DONE component `MEDIATEK-DRM`.

## Status after the backlight/display-glue pass (2026-10-04)

See [`backlight-glue/`](backlight-glue/) and
[`yft-display-glue-deltas.md`](yft-display-glue-deltas.md).

- Eleven modules are byte-identical to stock except build-id, with B1==B2:
  - display glue: `leds-mtk` (MTK `164442952094`), `leds-mtk-disp`,
    `pwm-mtk-disp` (+mt6878 match entries and probe logs), `backlight_cooling`,
    `rt4831a_drv`, `mediatek-drm-gateic`, `mtk_disp_sec`, `met_backlight_api`;
  - PWM, IR and haptics: `mtk-pwm`, `mtk_irtx_pwm` (+`dma-mask-bit`),
    `regulator-vibrator`.
- `aw36518` and `aw36518_v2` are 22/23 each.
- Main brightness is leds-mtk `lcd-backlight` → mtkfb → VTDR6115 DCS 0x51. No
  PWM backlight exists, and DISP_PWM has no consumer.
- Rear brightness is CO5300 DCS 0x51 only. The DT has no backlight GPIO.
- `mediatek-drm-panel-drv` is unused on this board (111/123 at this pass;
  closed to 123/123 in the mediatek-drm pass above).
- Workspace: `MTK-PWM`, `IR-BLASTER`, `HAPTICS`, `AW36518-FLASH` and
  `AW36518-V2-FLASH` moved to DONE, and `BACKLIGHT-DISPLAY-GLUE` was added as
  DONE. Totals are now 54 / 72 / 4 (130).
- Remaining display kernel module: `mediatek-drm.ko` (5.7 MB). Closed in the pass above.

## Status after the second pass (2026-10-04)

- **`mtk_panel_ext` — EXACT** (12/12 functions) after the stock
  `mtk_panel_funcs` layout was pinned: donor minus `set_backlight_pack` and
  `hbm_set_pack`.
- **`panel-ky-vtdr6115-dphy-cmd` — 20/24 functions byte-identical, 83/83 data
  objects and the full 199 816-byte `.data` byte-identical, 45/45 import CRCs,
  `.modinfo`/`vermagic` identical.** Component `VTDR6115-DISPLAY` moved
  **BLOCKED → DONE**. See [`vtdr6115/`](vtdr6115/).
- Reusable technique: build `Module.symvers` from the **stock** providers'
  `__kcrctab` (`vtdr6115/source/mk_symvers.py`) instead of rebuilding
  providers — this is what fixed the vendor-symbol CRC mismatches.

## Status after the first pass

- **`mtk_disp_notify` — EXACT and moved PARTIAL → DONE** in the workspace
  (`MTK-DISP-NOTIFY`). See [`kernel/notes.md`](kernel/notes.md).
- **`mtk_panel_ext` — 11/12 byte-identical**, one `ldr` immediate short; stays
  PARTIAL. See [`kernel/notes.md`](kernel/notes.md).
- The `dummy_drm` blocker below is **retired**: the shipped `mtk_disp_notify`
  is the `mediatek_v2` variant, and both modules build in isolation from a
  scratch `M=` directory.

## Build-system finding (original blocker, now retired)

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

1. ~~`mtk_disp_notify`~~ — **done, exact.**
2. ~~`mtk_panel_ext`~~ — **done bar one struct-offset field**; to finish it,
   resolve which two `struct mtk_panel_funcs` members the stock header lacks
   (needs a second MTK 6.1 panel header or `mediatek-drm.ko` call-site offsets).
3. ~~`panel-ky-vtdr6115-dphy-cmd`~~ — **done** (`VTDR6115-DISPLAY`, DONE).
4. `focaltech_touch_spi_ft3680` — existing work: `lieppos/focaltech-ft3680-recon`
   plus two analysis scripts.
5. `spi_tiny_co5300_lcd` (rear display) — pairs with the already-DONE
   `HYNITRON-REAR-TOUCH`.
6. ~~`mediatek-drm`~~ (5.7 MB, 25 dependencies) is **done and exact**. See
   [`mediatek-drm/`](mediatek-drm/).
