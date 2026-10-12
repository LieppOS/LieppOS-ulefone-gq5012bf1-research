# Hardware and runtime contract (static, read-only)

## Evidence sources

- **Device tree:** the stock merged DT `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`.
- **Source:** pinned ALPS 5e415e05 and NothingOSS 5f75a3b1.
- **Load capture:** `reverse-engineering/boot/module-loading/module-classification.tsv`.
- **Not done:** no backlight, PWM, panel, gate-IC, TEE or display operation was performed. "Loaded" means present
  in the saved module-load capture, not that the hardware was exercised.

## Labels

- `PROVEN_RUNTIME` — loaded in the saved capture.
- `ENABLED_IN_STOCK_DT` — a matching node exists in the stock DT.
- `STOCK_BINARY_IMPLEMENTATION` — the behaviour is implemented in the stock module.
- `PUBLIC_SOURCE_ONLY` — the code exists, but nothing in this device's DT binds it.
- `UNKNOWN`

| Module | Driver match (source) | Stock DT node | Labels | Load |
|---|---|---|---|---|
| mtk-pwm | `mediatek,pwm` | `pwm@11008000`: reg 0x11008000+0x1000, SPI 0x1d5, clocks PWM1–4-main/PWM-HCLK-main/PWM-main, topclk-ctl 0x20, bclk offsets 0x04–0x0c | ENABLED_IN_STOCK_DT, PROVEN_RUNTIME | 284 (second stage); provider of `pwm_set_spec_config` for the certified mtk_irtx_pwm |
| pwm-mtk-disp | `mediatek,mt6878-disp-pwm0/1` (**GQ5012BF1 delta**) | `disp-pwm0@1100e000` and `disp-pwm1@1100f000`: SPI 0xfe, `#pwm-cells = <2>`, clocks main/mm/pwm_src | ENABLED_IN_STOCK_DT, PROVEN_RUNTIME | 160 (first stage) |
| leds-mtk-disp | `mediatek,disp-leds` (also mtk-leds, i2c-leds, disp-conn-leds) | `/mtk-leds/backlight` "lcd-backlight": max 0x7ff, min 0x04, max-hw 0x7ff, `led-mode = <4>` (CUST_LCM: brightness via the DRM/DDIC path), `gate-enable = <1>`, `pwm-config = <0 1 0 0 0>`; no `reg-bat-percent-pt` | ENABLED_IN_STOCK_DT, PROVEN_RUNTIME | 161 (first stage) |
| rt4831a_drv | `mediatek,gate-ic-i2c`, `-i2c0` | **no matching node**; panel2/panel3 reference phandle 0x12df, which has no target in the merged DT | STOCK_BINARY_IMPLEMENTATION, PUBLIC_SOURCE_ONLY (no DT binding) | 94 (first stage; loaded as a provider for leds-mtk-disp) |
| mediatek-drm-gateic | `mediatek,i2c_lcd_bias`, `mtk-drm-gateic-drv-rt4801h/-rt4831a` | `lcd_ocp2131@3e` (`mediatek,i2c_lcd_bias`, id 6, okay) on an I2C bus. The production panel1 (`hx,vtdr6115,cmd,120hz,ky`) has `gate-ic = <0>` | ENABLED_IN_STOCK_DT (bias node), PROVEN_RUNTIME (load); AMOLED panel use is UNKNOWN | 91 (first stage) |
| mediatek-drm-panel-drv | `mediatek,mtk-drm-panel-drv-dsi/-dbi/-dpi` | no matching node; the board panel is driven by the separate G module `panel-ky-vtdr6115-dphy-cmd` | PROVEN_RUNTIME (load); PUBLIC_SOURCE_ONLY for binding | 92 (first stage) |
| mtk_disp_sec | `mediatek,disp-sec-aidctl` (also disp-sec, disp_sec) | `disp-sec { compatible = "mediatek,disp-sec-aidctl"; }` | ENABLED_IN_STOCK_DT, PROVEN_RUNTIME | 428 (second stage) |
| met_backlight_api | none | — | STOCK_BINARY_IMPLEMENTATION | never loaded (MET profiler baggage) |

## Implementation facts

- **Brightness path.**
  - `leds-mtk-disp` registers the `lcd-backlight` LED class device. In CUST_LCM mode (`led-mode = 4`) it forwards
    brightness to `mtkfb_set_backlight_level` in mediatek-drm, and on to the panel/DDIC (DCS 0x51 on the AMOLED).
  - It imports gate-IC hooks from mediatek-drm-gateic and rt4831a_drv. The stock DT sets `gate-enable = 1`, but
    the production panel has no gate IC.
  - The display PWM (`pwm-mtk-disp`) is a separate path that the DT also describes.
- **pwm-mtk-disp delta:**
  - Two GQ5012BF1 compatibles (`mt6878-disp-pwm0/1`) were added before mt6897, plus `"%s start"`/`"%s end"`
    probe logs.
  - The mt6878 entries use `mt6799_pwm_data`.
  - The clock/enable behaviour is the unmodified ALPS 5e415e05 behaviour (equal to MTK e46af0f79a1a).
- **mtk_disp_sec:** a normal-world secure-display helper. It uses cmdq-sec (secure GCE packets),
  `mtk_sec_heap`'s `dmabuf_to_secure_handle` and mediatek-drm. It makes no claim about secure-display isolation or
  TEE behaviour. Its CMDQ provider CRCs match only with the GQ5012BF1 TEE configuration (Microtrust disabled,
  TrustKernel device).
- **met_backlight_api:** sets `met_backlight_api_ready` and registers a leds-mtk notifier so the MET profiler can
  trace backlight changes. It is a pure profiler hook.

## Not claimed

- No physical backlight brightness range, PWM frequency, panel timing or bias voltage was exercised.
- Only the DT values above are recorded. They are not altered and not interpreted as proof of runtime success.
- Panel stub nodes (`jdi,nt36672e`, `truly,td4330`) have no driver in the stock image.
