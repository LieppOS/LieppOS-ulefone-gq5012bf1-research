# HAL → kernel lens selection path

```
Camera HAL 3A (mtkcam-core aaa)
  └─ libcam.hal3a.lensdrv.so   (sha256 17cf1852932c482b2d024f0b731f73e5fece7a3134806db285f9bb6a8cf7af02)
       class VCMDrv  [source path string: vendor/mediatek/proprietary/hardware/mtkcam-core/aaa/peripheraldriver/lens/vcm_drv.cpp]
       ├─ Init(sensorDev, sensorIdx) / IsVcmSupported
       ├─ dlopen libcameracustom.lens.so → GetVcmDriverName(dev, sensor_id, module_id, &lens_id, name[32], &VcmDriverConfig)
       │      "[sensor id] 0x%x [module id] 0x%x [vcm id] 0x%x"  /  "the current module isn't support VCM"  /  "dummy lens"
       ├─ GetV4l2MediaDevice: scan /dev/media%d, enumerate entities ("driver name:%s entity name:%s")
       ├─ GetV4l2SubDevName / GetV4l2SubDevice: /sys/dev/char/%u:%u readlink → /dev/v4l-subdevN of the entity named <name>
       ├─ ioctl VIDIOC_MTK_S_LENS_INFO(&cfg)            ("VIDIOC_MTK_S_LENS_INFO, error %s")
       ├─ SetInitFocusPos / SetFocusPosition → VIDIOC_S_CTRL V4L2_CID_FOCUS_ABSOLUTE
       └─ standby: "standby mode vcm power on/off" via close/reopen
```

## `libcameracustom.lens.so` (sha256 `8d5abd97…bf1e`, 50 176 bytes)

Exports `GetVcmDriverName`, `I2CSettingForMovePos`, `GetOisDriverName`,
`GetIrisDriverName`, `GetIrcutDriverName`, `GetOzoomProfile`, `isCommonDriver`,
and tables `vcm_list_0..5` (21 × 0x108-byte records each), `ois_list_0..5`,
`iris_list_0`, `ircut_list_0`, `ozoom_list_0`, `focus_profile`, `zoom_profile`.

* `GetVcmDriverName` reads **only `vcm_list_0`** (single GOT slot `0x21e0` →
  `vcm_list_0`); `arg0` (sensor dev) is only checked for `< 0`. `vcm_list_1..5`
  contain just the `Dummy` sentinel and are never consulted.
* Match: first record with `sensor_id == arg1` and (`module_id == 0` or `== arg2`).
  All stock records use `module_id = 0`, so the module/EEPROM vendor id does not
  influence selection.
* `I2CSettingForMovePos(lens_id, idx)` rewrites the record's `I2CSendNum`/`I2Cfmt`
  in place before the copy; for `0x9800` (also `0x9763/0x9764/0x9772/0x9773`) it
  produces the `[03,pos>>8] [04,pos&0xff]` format.

Decoded table: [`vcm-list-decoded.tsv`](vcm-list-decoded.tsv)
(static product configuration from the vendor image — no per-unit data).

| sensor_id | sensor | subdev opened by HAL | camera |
|---|---|---|---|
| 0x989 | imx989 | `main_vcm` | 0 |
| 0x988 | imx989cts | `main_vcm` | 0 (CTS variant) |
| 0x8e1 | s5kgn1sp | `main_vcm` | 0 slot alternate |
| 0x38e2 | s5kjn1main2 | `main4_vcm` | 2 |
| 0x566442 | ov64b | `main2_vcm` | 3 |
| 0x38e1 / 0x38e0 / ov32b40 | front sensors | — (`isn't support VCM`) | 1 |

## OIS on the same path

`ois_list_0..5` contain only the `Dummy` sentinel, so `GetOisDriverName`
resolves **no OIS driver for any sensor** → the HAL never opens the DW9781C
through the lens library, matching `availableOpticalStabilization = [0]` on all
cameras. The DW9781C is a separate chip on `4-000e` (DT port 3 of the
composite); camera 0's AF goes to `7-000c` through `main_vcm`, on a different
bus. AF is **not** integrated into or routed through the DW9781C on this product.
