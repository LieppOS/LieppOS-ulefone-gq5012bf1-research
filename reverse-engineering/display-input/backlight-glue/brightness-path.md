# Main display (VTDR6115) brightness path — end to end

Every kernel hop below is byte-identical to stock (see `parity/`), except
`mediatek-drm.ko` (not rebuilt; 5.7 MB) and the VTDR6115 panel (20/24, DONE).

```
Settings / DisplayPowerController (float 0..1, mBacklightAdapter useSurfaceControl=true)
  -> SurfaceFlinger -> HWC AIDL setDisplayBrightness            [hwcomposer.mtk_common.so: HWCDisplay::setBrightness,
                                                                  BrightnessWrap, LedDevice::setBrightnessInfo]
  -> /sys/class/leds/lcd-backlight/brightness (0..2047)          [init.mt6878.rc chown/chmod; also lights HAL path]
  -> leds-mtk.ko  led_classdev "lcd-backlight"                   [mtk_set_brightness -> limit_hw_brightness clamp]
       debug: "[Light] Set lcd-backlight directly ... L:821 map:821" (live dmesg)
  -> leds-mtk-disp.ko  of_disp_leds_match "mediatek,disp-leds" -> led_disp_set()
  -> mediatek-drm.ko  mtkfb_set_backlight_level() -> mtk_drm_setbacklight()
  -> mtk_panel_ext funcs->set_backlight_cmdq
  -> panel-ky-vtdr6115-dphy-cmd.ko  lcm_setbacklight_cmdq()
  -> DSI DCS 0x51, payload {level>>8 & 0x0F, level & 0xFF}
       live: "lcm_setbacklight_cmdq 821 3 53"  (821 = 0x335 -> 0x03, 0x35)
```

## DT (live capture, `/mtk-leds/backlight`)

| property | value | meaning |
|---|---|---|
| compatible (parent) | `mediatek,disp-leds` | selects `led_disp_set` (mtkfb path), not conn/i2c/virtual |
| label | `lcd-backlight` | |
| led-mode | 4 | `MT_LED_MODE_CUST_LCM` (panel DCS), not BLS PWM (5) or I2C (6) |
| max-brightness / max-hw-brightness | 0x7FF / 0x7FF | 11-bit range; 1:1 map to DCS value |
| min-brightness | 4 | |
| gate-enable | 1 | not read by any GQ5012BF1 driver (no consumer of the string) |
| pwm-config | `<0 1 0 0 0>` | legacy; not read by leds-mtk(-disp) |
| reg-bat-percent-pt | **absent** | `register_bp_thl_notify(mt_leds_bat_low_cb)` is **not** called: no battery-percent backlight throttle |

The VTDR6115 accepts 12 bits; the LED class limits normal operation to
0..2047. HBM is the panel-driver override `0x51 0x0F 0xFF` (on) /
`0x51 0x03 0xFF` (off); the DisplayDeviceConfig reports HBM disabled
(`isHighBrightnessModeEnabled=false`). No CABC, no doze or AOD brightness, no
separate HBM register (VTDR6115 closure).

## What is **not** in the path (proven)

| candidate | finding |
|---|---|
| pwm-backlight / `backlight` class | no `pwm-backlight` or `backlight` node in DT; no GKI backlight device; `mBacklightAdapter backlight=null` |
| DISP_PWM (`pwm-mtk-disp.ko`) | both DISP_PWM0/1 pwmchips register, but no DT property references either phandle (0x21c/0x21d) |
| `mtk-pwm.ko` (pwm@11008000) | consumers are only `leds-ln2403` (camplight) and `mtk_irtx_pwm` (IR); no display consumer |
| gate-IC / bias IC | `rt4831a_drv` never probes (no `mediatek,gate-ic-i2c*` node); `mediatek-drm-gateic` gate-IC drivers have no node and `panel1@0 gate-ic = <0>`; `lcd_ocp2131@3e` (`mediatek,i2c_lcd_bias`) binds the gateic panel-I2C client, but no module imports `mtk_panel_i2c_write_*` -> the OCP2131 LCD bias IC is stale board metadata for an AMOLED panel |
| `mediatek-drm-panel-drv` | no `mediatek,mtk-drm-panel-drv-*` node; unused |
| vendor brightness helper | none in vendor_dlkm; YFT modules do not touch backlight |
| battery-percent throttle | compiled in (leds-mtk 164442952094) but not enabled (DT property absent) |
| low-battery / charger / camera-open | no backlight import in charger/power modules; `yft_cam_open_flag` gates charging only |

## Thermal / power interaction (only actual dependencies)

- `backlight_cooling.ko` registers cooling device `lcd-backlight`
  (`/backlight-cooler`, `#cooling-cells = 2`), whose `set_cur_state` calls
  `setMaxBrightness(connector, percent, enable)` in leds-mtk. That
  `limit_hw_brightness` clamp is what `mtk_set_brightness` applies.
- No kernel thermal zone references the cooler phandle (0x29c), so the kernel
  never throttles it. Live `CoolingDevice{mValue=0, mType=6, mName=lcd-backlight}`.
- Userspace `thermal_core` has a backlight-cooler policy parser
  (`backlight_cooler_parser`, "backlight limit from source %d to state %d",
  "limit backlight fail"). The 15 shipped `/vendor/etc/thermal/*.conf` are
  obfuscated (per-byte `+(i mod 10)` shift). Decoded section names
  (`[charger-cooler]`, `[mtk-skin-control]`, `[vtskin-param]`, …) contain no
  backlight section. Some lines decode imperfectly, so treat this as
  **no backlight policy found**, not as proven absent.
- `thermal_interface.ko` and `met_backlight_api.ko` only register
  `mtk_leds_register_notifier` observers; neither writes brightness.
