# Calibration boundary

## 8-003c

Touches no calibration. The only data read is the 2-byte chip ID. No radiometry,
bad-pixel, shutter, KT/BT, NUC or factory data is stored in or read through the
I2C endpoint by any stock component.

## Where thermal calibration actually lives (ownership only; no values copied)

| data | storage | format owner | consumer |
|---|---|---|---|
| per-module factory calibration (NUC-T, KT/BT, DPC, RMVC, OOC, gain tables), firmware data `whole_data.bin` | module flash | InfiRay/Raytron | module ASIC; read/written over UVC vendor commands (`flash_read`, `adv_cfg_file_*`) by `libircmd020.so` |
| generic default calibration templates | `M170infisens.apk!assets/calibration/**` (17 entries: `b_calibration`, `k_calibration`, `dp_data`, `ktbt_array`, `nuc_t_array`, `ooc_data`, `rmvc_calibration`, high/low gain) | InfiRay SDK | `libadvirtempac020.so` / `libcommonsdk.so` in M170infisens; identical in every APK copy → not per-device |
| dead-pixel correction session | M170infDlp `DeadPixelCorFragment` | InfiRay SOP tool | written to module over UVC |
| visible/thermal fusion alignment | `INIT_ALIGN_DATA`, `libdualcalibration.so`; the visible camera EEPROM path `2-0050/eeprom` is referenced in Const but unused for thermal | YFT/InfiRay | M170infisens fusion |
| fm78100 thermometer factors (objectFactor, mems_cali) | FactoryMode SharedPreferences | YFT | `libthermometerTemp78102.so`; dead on GQ5012BF1 |

Details of radiometry formats stay with AC020-UVC / THERMOVUE-T2 (`qwen_hardware/qwen-thermal/re/calibration*`).
