# ov64b_mipi_raw (stock) vs ov64b_mipi_raw (donor)

* sensor id: stock 0x566442 / donor 0x566442
* pw_seq: stock [('HW_ID_MCLK', 24, 0), ('HW_ID_PDN', 0, 0), ('HW_ID_RST', 0, 0), ('HW_ID_AVDD', 2800000, 0), ('HW_ID_AFVDD', 2800000, 0), ('HW_ID_DVDD', 1100000, 0), ('HW_ID_DOVDD', 1800000, 1), ('HW_ID_MCLK_DRIVING_CURRENT', 8, 1), ('HW_ID_PDN', 1, 1), ('HW_ID_RST', 1, 1)]
* pw_seq: donor [('11', 24, 0), ('10', 0, 0), ('0', 2800000, 0), ('3', 3100000, 0), ('4', 1800000, 0), ('1', 1100000, 0), ('2', 1800000, 1), ('16', 3100000, 0), ('17', 3100000, 0), ('12', 8, 1), ('10', 1, 1)]

## static_ctx field deltas

| field | stock | donor |
|---|---|---|
| i2c_addr_table | `['0x20', '0x44', '0xff', '0x00', '0x00']` | `['0x44', '0xff', '0x00', '0x00', '0x00']` |
| eeprom_info | `` | `eeprom_info` |
| eeprom_num | `0` | `1` |
| sensor_output_dataformat | `3` | `37` |
| s_cali | `` | `set_sensor_cali` |
| init_setting_len | `5612` | `5604` |
| mode | `mode_struct@2af88` | `mode_struct` |
| sensor_mode_num | `5` | `12` |
| list | `feature_control_list@2b820` | `feature_control_list` |
| list_len | `2` | `3` |

77 static_ctx fields identical.

## Mode table

stock modes: 5, donor modes: 12

| idx | scenario | stock out | donor out | identical fields | differing fields | reg table |
|---|---|---|---|---|---|---|
| 0 | preview | 4624x3472 | 4624x3472 | 27 | setting_len: 320→392, seamless_group: 0→1, seamless_len: 0→330, linelength: 1056→936, framelength: 3636→4108, mipi_pixel_rate: 600800000→1200000000, read_margin: 0→10, ae_binning_ratio: 1000→1467, num_entries: 1→2, vc, dpc_enabled: 0→1, pdc_enabled: 0→1 | DIFFERENT (stock 160 pairs, donor 196 pairs; 146 common pairs, 21 addr not shared) |
| 1 | capture | 4624x3472 | 4624x3472 | 26 | setting_len: 326→390, seamless_group: 0→1, seamless_len: 0→330, linelength: 1056→936, framelength: 3636→4108, mipi_pixel_rate: 600800000→1200000000, read_margin: 0→10, ae_binning_ratio: 1000→1467, delay_frame: 2→3, num_entries: 1→2, vc, dpc_enabled: 0→1, pdc_enabled: 0→1 | DIFFERENT (stock 163 pairs, donor 195 pairs; 146 common pairs, 20 addr not shared) |
| 2 | normal_video | 4624x3472 | 4624x2604 | 25 | setting_len: 320→390, seamless_group: 0→2, seamless_len: 0→208, linelength: 1056→936, framelength: 3636→4108, mipi_pixel_rate: 600800000→1200000000, read_margin: 0→10, winsize, ae_binning_ratio: 1000→1467, delay_frame: 2→3, num_entries: 1→2, vc, dpc_enabled: 0→1, pdc_enabled: 0→1 | DIFFERENT (stock 160 pairs, donor 195 pairs; 137 common pairs, 20 addr not shared) |
| 3 | hs_video | 1920x1080 | 4624x2604 | 32 | setting_len: 320→388, linelength: 600→528, framelength: 1600→3660, max_framerate: 1200→600, winsize, ae_binning_ratio: 1000→2940, dpc_enabled: 0→1 | DIFFERENT (stock 160 pairs, donor 194 pairs; 48 common pairs, 19 addr not shared) |
| 4 | slim_video | 1920x1080 | 4624x2604 | 23 | setting_len: 320→388, seamless_group: 0→2, seamless_len: 0→206, hdr_mode: NONE→RAW_STAGGER, raw_cnt: 1→2, exp_cnt: 1→2, linelength: 600→528, framelength: 1600→7264, max_framerate: 1200→300, readout_length: 0→5208, read_margin: 10→96, framelength_step: 0→8, coarse_integ_step: 0→4, winsize, ae_binning_ratio: 1000→2940, dpc_enabled: 0→1 | DIFFERENT (stock 160 pairs, donor 194 pairs; 45 common pairs, 19 addr not shared) |
| 5 | custom1 | — | [4624, 3472] | | only in donor | |
| 6 | custom2 | — | [4624, 2604] | | only in donor | |
| 7 | custom3 | — | [4624, 3472] | | only in donor | |
| 8 | custom4 | — | [4624, 3472] | | only in donor | |
| 9 | custom5 | — | [4624, 3472] | | only in donor | |
| 10 | custom6 | — | [9248, 6944] | | only in donor | |
| 11 | custom7 | — | [9248, 6944] | | only in donor | |

## Init / seamless tables

* init: DIFFERENT (stock 2806 pairs, donor 2802 pairs; 1954 common pairs, 4 addr not shared)
* mode 0 seamless `` vs `ov64b_seamless_normal_preview`: missing
* mode 1 seamless `` vs `ov64b_seamless_normal_preview`: missing
* mode 2 seamless `` vs `ov64b_seamless_normal_video`: missing
* mode 4 seamless `` vs `ov64b_seamless_slim_video`: missing
