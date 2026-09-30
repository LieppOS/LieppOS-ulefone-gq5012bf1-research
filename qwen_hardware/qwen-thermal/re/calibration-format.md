# Calibration and file formats

## Exact module paths (`CommonParams.SdFilePath`)
- `user_data/user_eeprom_data.bin`
- high/low `default_data/{high_gain,low_gain}/tpd_kt1.bin`, `tpd_bt1.bin`, `tpd_nuc_t.bin`
- `system_cfg.bin`, `default_cfg.bin`, `default_data/dual_fusion.bin`
- `secd_cali_data/manufacturer_temporary_data.bin`
- high/low `secd_cali_data/.../tpd_kt1.bin`, `tpd_bt1.bin`, `tpd_nuc_t.bin`

`advFileRead`/write transfers these through vdcmd; `SingleFileType` distinguishes normal=0 and calibration=1.

## Integrity marker
FactoryMode reads `secd_cali_data/manufacturer_temporary_data.bin` to private app storage. A valid record is at least 192 bytes; byte 0 == 1 means calibrated, byte 0 != 1 means not calibrated. This is the strongest direct evidence of module-resident, per-unit second-calibration state.

## APK seed assets
- `k_data_{high,low}.bin`, `b_data_{high,low}.bin`, `rmvc_data_*`: 38,400 bytes = 160x120x16-bit generic seed arrays.
- `dp.bin`: 6,144-byte DPC seed.
- `ooc_data_*`: 9,600 bytes.
- generic KT/BT arrays: 7,202 bytes each; NUC-T: 32,768 bytes each.
- WN-family UUID-named KT/BT: 2,402 bytes; `nuc_table_*`: 16,384 bytes = 8192 shorts, exactly matching the Java WN640 V2 length check; `priv_*`: 1,201 bytes.
- dual calibration: 192-byte parameter blobs; `focals.bin` contains little-endian doubles.
- `system_cfg*.bin`: 327,680 bytes in M170infDlp; test IR frame 98,304 bytes = 256x192x16-bit.

These are multi-product SDK assets, not proof of shipping detector geometry. Do not overwrite module-resident data with APK examples.

## Per-unit preservation
Before ROM work, preserve all `/mnt/vendor/nvcfg/infiray` content where present, module files reachable only through read-only `advFileRead`, APK versions/hashes and firmware package metadata. Preserve permissions, SELinux labels and hashes. Calibration is detector-, lens-, gain- and module-specific; loss can destroy radiometric accuracy and bad-pixel correction.

Exact binary field layouts beyond the 192-byte status/flag and known array lengths remain unknown; no unsupported struct claims are made.
