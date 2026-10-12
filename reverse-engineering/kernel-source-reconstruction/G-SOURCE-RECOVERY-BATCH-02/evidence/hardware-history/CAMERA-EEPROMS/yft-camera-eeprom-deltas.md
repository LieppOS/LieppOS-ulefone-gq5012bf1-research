# camera_eeprom_v4l2 — Ulefone/YFT (GQ5012BF1) deltas vs donor

Donor: NothingOSS kernel modules `nkm.git` `mt6878/Tetris/u` `5f75a3b` (its
`mtkcam/cam_cal` tree is identical to `mt6878/Galaxian/v` `18d138b`). Of the
seven Nothing refs, these two are closest to stock: 26 differing files, all of
which are the deltas below. The other refs differ in 30–37 files.

Every delta is **proven by the byte-identical rebuild**: stock `.ko` equals
the rebuild except `.note.gnu.build-id`. No public source exists for the
YFT/ODM parts. Exact-string searches of all local mirrors (nkm, kdm, nt6878,
volla6878; every ref) and of the public web found nothing. Patch series:
`source/patches/0001..0005`.

| # | area | donor behaviour | GQ5012BF1 stock behaviour | evidence | source difference | confidence |
|---|---|---|---|---|---|---|
| 1 | calibration ABI `cam_cal_format.h` | header actually used by the build (kdm `drivers/misc/mediatek/cam_cal/inc`, Nothing `957dac1`): `CAMERA_CAM_CAL_DATA_FUSE_ID` command, `FuseId[32]`, `PartNumber[48]`; the mtkcam copy had `PartNumber[48]` | `PartNumber[24]`, `sensorID` @0x20, no `FuseId`; `sizeof(STRUCT_CAM_CAL_DATA_STRUCT) = 0x2a88` | ioctl constant `0xEA88690F` in stock code and HAL; HAL offsets (sensorID @0x20, S2aAf @0x878) | kdm `f6e1549` (resolved first via `-I`, see `.cmd` deps) + same edit in mtkcam copy | proven |
| 2 | `eeprom_driver.c` | no OTP status export | `yft_otp_state_main/sub/main2/main3` globals (init −1); `camera_otp` class with `camera_otp` attr (0444, `"%d %d %d %d"`); probe path as stock | stock symbols, strings, data | DONOR-MODIFIED | proven |
| 3 | `cam_cal_list.c` | Nothing sensor list | 11 entries: 0x989, 0x98a, 0x38e1, 0x38e2, 0x566442 (**0xA6**), 0xa042, 0x616, 0x1b74, 0x1b75, 0x350, 0x8e1; no write hooks | decoded `g_camCalList` | DONOR-MODIFIED | proven |
| 4 | `cam_cal_config.c/.h` | Nothing generic parsers | stock `layout_check`, `do_part_number` (24 B), `do_single_lsc`, `do_2a_gain`; `yft_otp_state_*` externs | function parity | DONOR-MODIFIED | proven |
| 5 | layout set | Nothing set incl. gc16b3c, gc16b3ctxd, imx882, imx882txd | those 4 **removed**; 14 ODM layouts **added** (hi847, imx616, imx989cts, imx989ryyb, ova0b40, ova0b40cts, s5kgn1sp, s5khp2sp, s5khp3sp, s5khp3sp03, s5khp3sp23, s5khp3spcts, s5kjn1, s5kjn1main2) | stock symbol table: 37 `{cal_layout_table, <cfg>}` pairs; `cam_cal_config_list` = 37 pointers in wildcard order | layout/*.c | proven |
| 6 | `imx989_cust_eeprom.c` | Nothing MTK-format imx989 layout | ODM layout: header 0x77006901 @0, LSC 0x1d/0x74c, AWB u16×4 at 0x0b/0x13, AF u16 at 0x76d→S2aAf[0] and 0x76b→S2aAf[1], PDAF 0x771/0x5dc, no part number/lens id, `has_stored_data = 0` | decoded config/layout + parity | DONOR-MODIFIED (rewritten) | proven |
| 7 | `ov64b_cust_eeprom.c` | Nothing ov64b layout at 0xA0 | ODM AF-only layout at **0xA6**, preload 0x1500, `has_stored_data = 1`, LSC/PDAF/stereo declared but disabled | decoded | DONOR-MODIFIED (rewritten) | proven |
| 8 | `imx989lite_cust_eeprom.c` | `.sensor_id = IMX989LITE_SENSOR_ID` (0x098A in the GQ5012BF1 `kd_imgsensor.h`) | `.sensor_id = 0x098B` literal; 0x98A is matched by `imx989ryyb_cust_eeprom` instead | parity | DONOR-MODIFIED | proven |
| 9 | `eeprom_driver.c` probe | `devm_kzalloc` failure → `dev_info("kcalloc memory faill")` + `vmalloc` fallback | no fallback (returns `-ENOMEM`) | string absent from stock; byte parity | patch 0001 (4 lines in cam_cal) | proven |

Unchanged donor sources (DIRECT_SOURCE_MATCH):
* `eeprom_i2c_common_driver.c` (`EEPROM_WRITE_EN = 0`), `eeprom_utils.c`, `eeprom_i2c_custom_driver.c`
* the 20 other donor layouts
* all kd/cam_cal headers except `cam_cal_format.h` (kdm `f6e1549`) and `kd_imgsensor.h` (kdm `703d473`, GQ5012BF1 sensor IDs, shared with the imgsensor closure)
