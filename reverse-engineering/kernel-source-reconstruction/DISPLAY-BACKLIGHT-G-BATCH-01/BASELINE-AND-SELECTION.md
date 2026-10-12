# Baseline and selection

## Baseline

- **Canonical master:** `1e87ca06` (G-CANONICAL-INTEGRATION-01 applied). Validator PASS, 0 errors:
  **A412 B1 C11 D3 E0 F0 G31 = 413/458**. Inventory 458/471.
- **Remaining Category G:** 31 identities, listed with source, provider, load and BTF facts in
  `G-REMAINING-INVENTORY.tsv`. No branch manifest and no maintained repository owns any of them.

## Frozen (8 identities; manifest sha256 in BATCH-MANIFEST.sha256)

These are exactly the eight display/backlight candidates named in Codex's G-SOURCE-RECOVERY-BATCH-01
`NEXT-BATCH.md`, verified as current canonical G rows by exact identity:

| Module | Domain | Directory |
|---|---|---|
| mtk-pwm | KDM | `drivers/misc/mediatek/pwm` |
| pwm-mtk-disp | KDM | `drivers/pwm` |
| rt4831a_drv | KDM | `drivers/misc/mediatek/gate_ic` |
| mediatek-drm-gateic | KDM | `drivers/gpu/drm/panel` |
| mediatek-drm-panel-drv | KDM | `drivers/gpu/drm/panel` |
| leds-mtk-disp | KDM | `drivers/leds` |
| mtk_disp_sec | KDM | `drivers/gpu/drm/mediatek/mediatek_v2` |
| met_backlight_api | EXT (Nothing `kernel_modules/met_drv_v3`) | `met_api/met_backlight_api` |

- **No BTF:** none of the eight stock files carries `.BTF`, so no OEM BTF base is needed.
- **Provider ownership:** the providers `mediatek-drm`, `mtk_panel_ext` and `leds-mtk` are certified A in
  `android_kernel_modules_audio_shared_infrastructure` @ 4697eac3 (ALPS 5e415e05 + 10 historical DRM patches).
  `met`, `mtk_printk_ctrl`, `cmdq-sec-drv`, `mtk-cmdq-drv-ext` and `mtk_sec_heap` are A in their own repositories.
  This batch uses them only as compile-time ABI witnesses; their ownership does not change.
- **Prior work:** byte-identical isolated rebuilds already existed for all eight (`Reverse Engineer - DONE/BACKLIGHT-DISPLAY-GLUE`
  and `MEDIATEK-DRM`, 2026-10-04). Those builds took provider CRCs from stock `__kcrctab` and were not independently
  pinned, which is why the rows stayed G. They are used here as lineage evidence, never as build inputs.
