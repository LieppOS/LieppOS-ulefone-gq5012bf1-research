# Calibration / radiometry boundary

USB TRANSPORT (closed here) vs THERMAL RADIOMETRY ALGORITHM (proprietary, THERMOVUE-T2 scope).

## Where calibration lives and how it moves (ownership + transport only; no values)

| data | storage | transport | stock consumer |
|---|---|---|---|
| factory NUC-T / KT / BT (high & low gain), manufacturer temporary data, user OEM data, dual-fusion data, system/default config | **module internal flash** as SDK "files" (`CommonParams.SdFilePath`: `default_data/{high,low}_gain/tpd_{kt1,bt1,nuc_t}.bin`, `secd_cali_data/…`, `user_data/user_eeprom_data.bin`, `default_data/dual_fusion.bin`, `system_cfg.bin`, `default_cfg.bin`) | USB vdcmd `adv_cfg_file_open/read/write/close` (frame 0x10, module 0x08) via `adv_file_read`/`file_write` in libAC020sdk, copied to app storage (`getExternalFilesDir(DOCUMENTS)`) | M170infisens reads `SECD_CALI_MANUFACTURER_TEMPORARY` (fusion cal, `user_oem_data.bin`) and `DEFAULT_DATA_NUC_T_HIGH` (`TempCompensation`/`GainCompensation`) |
| on-module calibration procedures (DPC, RMCover, K-value, TPD 1/2-point) | module | vdcmd (module 0x06/0x11; `vendor-opcodes.tsv`) | M170infDlp service tool |
| generic default tables | `M170infisens.apk!assets/calibration/**` (identical in every copy) | none (app assets) | libadvirtemp* |
| radiometric frame data | per-frame temperature plane + info lines | UVC iso stream (`frame-format.md`) | TempCompensation, libadvirtemp*, libcommonsdk |
| 8-003c I2C | none | – | – |
| separate EEPROM | none for the thermal module (the `2-0050` visible-camera EEPROM reference is unused for thermal) | – | – |

Per-unit calibration content is not copied or published.

## Out of scope (does not block AC020-UVC)

Temperature conversion of the u16 plane, NUC/KT/BT application, gain-dependent
compensation, emissivity/distance/environment correction, AGC/ISP processing, MNN
super-resolution and visible/thermal fusion.
