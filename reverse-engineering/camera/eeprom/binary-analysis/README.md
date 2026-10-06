# binary-analysis

Decoded directly from stock `camera_eeprom_v4l2.ko` (sha256 `0423196d…ee10a`) by `../scripts/decode_cam_cal.py`. Data bytes and relocations only; no source is involved.

* `cam-cal-list.tsv`: `g_camCalList[12]` (raw `read()` path): sensor_id → 8-bit slave address, read hook, size, write hook (all NULL)
* `cam-cal-configs.tsv`: `cam_cal_config_list[37]` in search order, with every `STRUCT_CAM_CAL_CONFIG_STRUCT` field and the header magic
* `cam-cal-layouts.tsv`: 37 × 9 layout items (Include, start, size, parser)

`kd_imgsensor_h_name` is the name the GQ5012BF1 `kd_imgsensor.h` gives to an ID. The authoritative label is the stock config name; for example 0x98A is matched by `imx989ryyb_cust_eeprom`.
