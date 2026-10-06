# camera_eeprom_v4l2 — runtime read path, write path, interfaces

Everything here is the behaviour of the byte-identical source
(`../source/mtkcam/cam_cal/`), cross-checked against stock machine code where noted.

## Device creation (probe)

* One `i2c_driver` `"mediatek,camera_eeprom"` (OF compatible `mediatek,camera_eeprom`).
* `eeprom_probe`: the node name must be `camera-eeprom<N>`, otherwise `-EINVAL`.
  `alloc_chrdev_region` "camera_eeprom<N>", `cdev_add`, class
  `camera_eepromdrv<N>`, device `/dev/camera_eeprom<N>`. A per-device
  `eeprom_mutex` is created. **No I2C access at probe.**
* First probe also creates class `camera_otp` with attribute `camera_otp`
  (0444) → `/sys/class/camera_otp/camera_otp` (YFT addition).
* GQ5012BF1: N = 0, 1, 2, 4 (see `../hardware/`).

## Interfaces

| entry | number / mode | behaviour |
|---|---|---|
| `open` | — | kmalloc per-fd `{pdrv, sensor_info.sensor_id = 0}` |
| `ioctl CAM_CALIOC_S_SENSOR_INFO` | `0x4004690A` | sets the per-fd sensor_id; used only by the raw `read()` path |
| `ioctl CAM_CALIOC_G_GKI_QUERY` | `0xAA886914` | returns 0 (capability probe; nothing copied out) |
| `ioctl CAM_CALIOC_G_GKI_NEED_POWER_ON` | `0xC0106919` | layout lookup; `needPowerOn = has_stored_data && layout item Include` |
| `ioctl CAM_CALIOC_G_GKI_READ` | `0xEA88690F` (struct 0x2a88 B) | `get_cal_data()` → parser → `copy_to_user` on success. Returns the **positive** CAM_CAL error code otherwise |
| other ioctl | — | `-EPERM` ("No such command"). `_IOC_NONE` gives `-EFAULT`. Legacy `G_READ` 0xC0186905 and `S_WRITE` are rejected |
| `compat_ioctl` | — | stub, returns 0 for every command (32-bit callers get "success" with no data) |
| `read` | — | raw read through `g_camCalList` (see below) |
| `write` | — | **disabled** (see write path) |
| `llseek` | — | SEEK_SET/CUR; SEEK_END = 16192 + off |
| module param | `cam_eeprom_debug` (0644) | only enables `debug_log`, which is `pr_debug` (compiled out without dynamic debug) |

The ioctl allocates a `kzalloc(_IOC_SIZE(cmd))` bounce buffer per call and
copies from user only for `_IOC_WRITE` commands.

## Parsed read path (what the HAL uses)

```
HAL CamCalHelper::getCamCalData (libfeatureiodrv_mem.so)
  open /dev/camera_eeprom<getEepromDevIdx(sensorDev)>
  ioctl QUERY → ioctl NEED_POWER_ON
      ok   → ioctl GKI_READ
      fail → (global flag) CamCalHelper::sensorPowerOn → ioctl GKI_READ
kernel get_cal_data(cmd, sensorID, deviceID)
  cmd < 9, idx = IMGSENSOR_SENSOR_DUAL2IDX(deviceID) in 0..6
  layout search if sensorID != last_sensor_id || DataVer == CAM_CAL_TYPE_NUM || no layout yet:
      cached layout index for idx? (mp_layout_preload[idx], kmalloc 2 B) → reuse
      else for each of 37 configs in cam_cal_config_list order:
           check_layout_function → layout_check: sensor_id equal AND
           read_data_region(header_addr, 4) == header_id   (direct I2C, not cached)
  DataVer = layout->data_ver; item = layout->cal_layout_tbl[cmd]
  item.Include && parser → parser(pdata, start_addr, block_size, out)
parser → read_data(offset, len)
  preload enabled: first call per idx kmallocs min(preload_size, max_size)
  and reads it in one read_data_region(base, size); later reads are memcpy
  from RAM. Preload failure → buffer freed, falls back to direct reads
read_data_region: bounds [base, base+max_size) (0 → 0x2000 default)
  mutex_lock(eeprom_mutex); client->addr = i2c_write_id >> 1
  Common_read_region → iReadData_CAM_CAL: chunks of ≤ 1024 B, each one
  i2c_transfer of 2 msgs {write 2-byte big-endian offset, read n}
  restore client->addr; mutex_unlock
  pr_info("[common_read_time]Profile = %llu ns")   (only surviving log line)
```

| property | stock behaviour |
|---|---|
| read frequency | once per device index per boot (preload), then served from RAM. The header check reads 4 B directly each time a layout search runs |
| caching | `mp_eeprom_preload[7]`, `mp_layout_preload[7]`, keyed by device index (not sensor ID). **Never freed or invalidated**, even at remove |
| max transfer | 1024 B per I2C read message (`EEPROM_I2C_READ_MSG_LENGTH_MAX`) |
| page segmentation | none beyond the 1024 B chunking. 16-bit linear offsets |
| retry | **none**. One failed `i2c_transfer` fails the whole region (returns 0) |
| locking | per-device `eeprom_mutex` around the address swap + transfer only. The globals `cam_cal_config`, `cam_cal_index` and `last_sensor_id` are shared by all four device nodes and are unlocked |
| error reporting | parsers return `CamCalReturnErr[cmd]` (positive codes `0x1`…`0x800000`). The ioctl returns them as a positive long |
| custom paged reader | `Custom_read_region` (8-bit offset, page in the I2C address, 256 B pages) is linked but **referenced by no config and no list entry** (dead code) |

## Raw read path (`read()`)

`read_region()`: `g_camCalList` entry selected by the per-fd sensor_id (from
`S_SENSOR_INFO`). Limit `maxEepromSize` (0 in every entry, so **0x2000**).
Address swapped to `slaveID >> 1`, then `Common_read_region`. With no sensor ID
set, the sentinel entry is selected, so it reads at the **DT client address**
(for example 0x51 on i2c-7, where nothing is expected). HAL user:
`CamCalHelper::readDataFromEeprom` (`S_SENSOR_INFO` + `lseek` + `read`).

## Write path — **READ-ONLY IN STOCK**

* `write()` → `write_region()` → `g_camCalList[].writeCamCalData` is NULL in
  all 11 entries (decoded from stock `.data`, no relocation) → `Common_write_region`.
* Stock `Common_write_region` machine code is `mov w0, wzr ; ret` (8 bytes):
  `EEPROM_WRITE_EN = 0`. `Write_I2C_CAM_CAL` / `iWriteData_CAM_CAL` are not
  linked, and no write ioctl exists (`S_WRITE` falls to `-EPERM`).
* Result: every `write()` returns `-EFAULT` with no I2C traffic.
* Exposure only: `/dev/camera_eeprom*` 0660 `system:camera`. SELinux grants
  `write` on `camera_eeprom_device` to `factory`, `mediaserver`,
  `mtk_hal_camera` and `atci_service`, but the kernel refuses all writes.

## YFT `camera_otp` status

`/sys/class/camera_otp/camera_otp` prints `"%d %d %d %d"` =
`yft_otp_state_main sub main2 main3`. Each starts at −1 and is set by the
parsers when the HAL requests data: 1 = AWB/AF read OK and ordered, 0 =
failure or ordering violation.

| flag | set by |
|---|---|
| main | imx989 / imx989cts / imx989ryyb / s5kgn1sp parsers |
| sub | s5kjn1 |
| main2 | s5kjn1main2 |
| main3 | ov64b |

The SELinux label is `yft_fmt_device` (factory test). No reader was found in
the vendor/system/product/system_ext images.

## Stock quirks preserved (not fixed)

* `eeprom_remove` calls `unregister_chrdev_region` before `device_destroy`,
  never calls `cdev_del`, and destroys the shared `camera_otp` class on the
  first device removal.
* The LSC validity check in the ODM parsers can never fire (see `../calibration/checksum-map.tsv`).
* Dead 1-byte reads at 0x0a and 0x76a in the ODM 2A parsers.
* AWB channel values are u16 in the EEPROM but stored into u8 `rValue*/rGolden*` (truncated).
* The ODM 2A parsers ignore the layout item's `start_addr`/`block_size` (0x7/0xe) and use fixed offsets.
* Positive error codes returned from `unlocked_ioctl`.
