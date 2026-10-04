# Status: backlight + display glue (2026-10-04)

| axis | result |
|---|---|
| stock semantic map | main path framework -> leds-mtk -> leds-mtk-disp -> mediatek-drm -> VTDR6115 DCS 0x51; rear path CO5300 DCS 0x51; no PWM/LED/backlight-class/gate-IC in either |
| stock binary parity (A vs B) | 11 modules exact except build-id; AW36518/V2 22/23 plus characterized residual; panel-drv (unused) 123/123 exact except build-id (2026-10-04) |
| clean rebuild reproducibility | B1==B2 file-identical for all 12 rebuilt-twice modules |
| runtime validation | none (offline) |

Moved PARTIAL -> DONE in the workspace: MTK-PWM, IR-BLASTER, HAPTICS,
AW36518-FLASH, AW36518-V2-FLASH. New DONE component: BACKLIGHT-DISPLAY-GLUE.

Open:
- ~~`mediatek-drm-panel-drv` private `mtk_lcm_dsi_params` layout~~. Closed on
  2026-10-04: the layout was not private. It was `struct mtk_panel_params`
  (embedded as `mtk_lcm_mode_dsi::ext_param`) built from the wrong
  `mtk_panel_ext.h`. With the ALPS `5e415e059253` header the result is
  123/123, all sections except build-id, B1==B2. See `../mediatek-drm/`.
- ~~`mediatek-drm.ko` (5.7 MB) not rebuilt~~. Closed on 2026-10-04:
  2376/2376, all 70 sections except build-id, B1==B2. See `../mediatek-drm/`.
- AW36518 scheduling/`.data` order trigger.
- Runtime/physical: brightness curve, IR emitter part, motor part, flash LEDs.

Both former next targets (`mediatek-drm.ko` and `mediatek-drm-panel-drv`) are
closed. See `../mediatek-drm/README.md`.
