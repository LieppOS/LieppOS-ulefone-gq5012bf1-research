# Status: backlight + display glue (2026-10-04)

| axis | result |
|---|---|
| stock semantic map | main path framework -> leds-mtk -> leds-mtk-disp -> mediatek-drm -> VTDR6115 DCS 0x51; rear path CO5300 DCS 0x51; no PWM/LED/backlight-class/gate-IC in either |
| stock binary parity (A vs B) | 11 modules exact except build-id; AW36518/V2 22/23 plus characterized residual; panel-drv (unused) 111/123 |
| clean rebuild reproducibility | B1==B2 file-identical for all 12 rebuilt-twice modules |
| runtime validation | none (offline) |

Moved PARTIAL -> DONE in the workspace: MTK-PWM, IR-BLASTER, HAPTICS,
AW36518-FLASH, AW36518-V2-FLASH. New DONE component: BACKLIGHT-DISPLAY-GLUE.

Open:
- `mediatek-drm-panel-drv` private `mtk_lcm_dsi_params` layout. The module is
  unused on this board, so this is not blocking.
- `mediatek-drm.ko` (5.7 MB) not rebuilt.
- AW36518 scheduling/`.data` order trigger.
- Runtime/physical: brightness curve, IR emitter part, motor part, flash LEDs.

Next target: `mediatek-drm.ko` (last display kernel module), or the
`mtk_lcm_*` layout so `mediatek-drm-panel-drv` closes too.
