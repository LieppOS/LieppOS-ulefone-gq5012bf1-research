# Hynitron struct layouts (proven by byte-identical code)

These offsets were taken from the DWARF of the exact rebuild. They are
authoritative because all 65 functions using them are byte-identical to stock.
Representative stock evidence is cited.

## `struct hynitron_ts_data` (584 B, kzalloc in `hyn_probe`)

| off | field | stock evidence |
|---:|---|---|
| 0 | `pdata` | `ldr x?, [x?]` then `+0x8` reset gpio in `hyn_reset_proc` |
| 8 | `client` | `ldr x0,[x19,#0x8]` before every I2C helper |
| 16 | `dev` | probe |
| 24 | `input_dev` | report/gesture |
| 32 | `thread_tpd`, 40 `timer` (hrtimer 72) | unused, layout only |
| 112 | `work` (48) | `INIT_WORK` in `hyn_input_dev_int` |
| 160 | `hyn_workqueue` | IRQ handler `queue_work` |
| 168 | `device_id`; 169 `irq_is_disable` | `hyn_irq_enable/disable` |
| 172 | `use_irq` (s32) | `enable_irq/disable_irq_nosync` |
| 176 | `int_trigger_type`, 177 `sensor_tx`, 178 `sensor_rx`, 179 `hyn_irq_flag`, 180 `report_flag`, 181 `key_index` | |
| 182 | `work_mode` | resume/boot update |
| 183 | `suspended` | `hyn_suspend/resume` |
| 184 | esd bitfields (mode/running/i2c_lock) | |
| 188..196 | esd counters | |
| 200 | `hyn_esd_lock` (mutex 48) | |
| 248 | `hyn_esd_check_work` (delayed_work 136) | |
| 384 | `hyn_esd_workqueue` | |
| 392 | `chip_ic_type` u16, 394 `chip_ic_series`, 396 `chip_ic_product_line` | `hyn_find_fw_idx` |
| 400 | `chip_ic_checksum`, 404 `chip_ic_checkcode`, 408 `chip_ic_fw_version` | `cst*_firmware_info` |
| 412 | `chip_ic_project_id`, 414 `chip_ic_module_id`, 416 `chip_ic_workmode` | |
| 418 | `chip_ic_bootloader_addr`, 419 `chip_ic_main_addr` | `hyn_detect_bootloader` addr swaps |
| 420 | `config_chip_type`, 422 `config_chip_series`, 424 `config_chip_product_line` (`0x1a8`) | `ldrb w8,[x19,#0x1a8]` in gesture/readdata |
| 425 | `fw_updating`; 432 `fw_name`; 440 `fw_length`; 448 `p_hynitron_upgrade_firmware` | `hyn_boot_update_fw` |
| 456 | `apk_upgrade_flag`, 457 `apk_rdwr_flag`, 458 `in_glove_mode`, 459 `power_on` | |
| 464 | `k_obj`; 472 `vdd`; 480 `vcc_i2c`; 488 `fb_notif` (24); 512 `resume_work` (48); 560 `ts_pinctrl`; 568/576 pinctrl states | layout-only (unused in stock config) |

## `struct hynitron_ts_platform_data` (148 B)

`irq_gpio`@0, `irq_gpio_flags`@4, `reset_gpio`@8, `reset_gpio_flags`@12,
`vdd_gpio`@16, `vdd_gpio_flags`@20, `x_resolution`@24, `y_resolution`@28,
`max_key_num`@32, `max_touch_num`@36, `key_x_coords[8]`@40,
`key_y_coords[8]`@72, `key_code[8]`@104, bools `xy_exchange`@136
`x_overturn`@137 `y_overturn`@138 `have_key`@139 `report_key_position`@140
`i2c_pull_up`@141 `enable_power_off`@142 `enable_slot_report`@143
`enable_esd`@144.

## Tables

- `struct hynitron_fw_array` (24 B): `name`@0, `fw`@8, `project_id`@16,
  `module_id`@18, `chip_type`@20, `fw_length` (u16)@22.
  `hynitron_fw_grp[10]` = 240 B, with 3 populated entries.
- `struct hynitron_chip_type_array` (6 B): `chip_type`, `chip_series`,
  `chip_product_line`, `chip_boot_addr`. `hynitron_chip_type_grp[33]` = 198 B.
- `struct touch_info` (20 B; `HYN_MAX_POINTS`=1): `y`@0 `x`@4 `p`@8 `id`@12
  `count`@16.
- `struct hyn_gesture_st hyn_gesture_data` (1034 B .bss): `header[8]`@0,
  `coordinate_x[255]`@8, `coordinate_y[255]`@518, `report_key`@1028,
  `gestrue_id`@1030, `mode`@1031 (stock `ldrb [hyn_gesture_data+0x407]` in
  `hyn_gesture_readdata`), `active`@1032.
- `tiny_tpgesture_status` (int, .bss 4) is the display-owned gesture flag.
