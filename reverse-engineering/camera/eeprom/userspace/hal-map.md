# HAL ↔ camera_eeprom_v4l2 boundary

| library (vendor/lib64/mt6878) | sha256 (prefix) | role |
|---|---|---|
| `libfeatureiodrv_mem.so` | `f924a9f09f20cf22` | `NSCam::CamCalHelper` + `CamCalDrv`: the **only** opener of `/dev/camera_eeprom*` (strings `/dev/camera_eeprom`, `/dev/CAM_CAL_DRV`) |
| `libcam.peripheralcontroller.so`, `libfeature.stereo.provider.so`, `libcam.hal3a.v3.dng.so` | — | call `CamCalDrvBase::createInstance` / `GetCamCalCalData` |
| `libcameracustom.camera_calibration.core.so` | `3942b87b9af8fb83` | userspace copy of the MTK parsers (`DoCamCal2AGain` …, `[AFInf]` at +0x878, `[AFMacro]` at +0x87a). Same struct ABI as the kernel. Used through `ICamCalCustom` |
| `libcam.hal3a.lscMgrApi.so` | `ffdd9af97188f510` | LSC consumer (`loadEEPromDataFlow`, `CAM_CAL_SINGLE_EEPROM_DATA`, "MTK OTP: Do shading align") |
| `libcam.hal3a.v3.nvram.v4l2.so` | `d9f65d7453ee4bd6` | `NvramDrv::readModuleIdFromEEPROM` |
| `libmtkcam_calibration_provider.so` | `ae00a60ea7fd2cf5` | stereo/EEPROM dump provider (`/data/vendor/camera_dump/EEPROM_STEREO`) |

## Calls (from `libfeatureiodrv_mem.so` disassembly)

| HAL function | kernel interface | notes |
|---|---|---|
| `CamCalHelper::getEepromDevIdx(sensorDev)` | — | index = `IHalSensorList::querySensorStaticInfo(dev)` field at +0x64; with no sensor list, `ctz(sensorDev)` (or 13 if dev ≥ 0x801) |
| `CamCalHelper::getCamCalData(pCamCalData)` | open `/dev/camera_eeprom<idx>`; `ioctl 0xAA886914` (QUERY); `ioctl 0xC0106919` (NEED_POWER_ON, 16-byte arg `{Command, sensorID, deviceID, needPowerOn}`); `ioctl 0xEA88690F` (GKI_READ, 0x2a88-byte struct) | if NEED_POWER_ON fails and a global flag is set: `sensorPowerOn(sensorID, deviceID)`, then GKI_READ, then `sensorPowerOff` |
| `CamCalHelper::readDataFromEeprom(...)` | `ioctl 0x4004690A` (S_SENSOR_INFO) + `lseek` + `read`, or legacy `ioctl 0xC0186905` (G_READ) | the legacy path is rejected by the stock kernel (`-EPERM`) |
| `CamCalDrv::dumpEepromToFile / readEepromFromFile / compareFiles` | — | debug/virtual mode (`/data/eeprom_virtual_dump_`, `/sdcard/EEPROM/SensorDev%d`, `vendor.debug.eeprom.dumpsize`) |

The ioctl numbers in the HAL equal the stock kernel's `eeprom_ioctl`
comparisons (`0xEA88690E` range check, `0xAA886914`, `0xC0106919`,
`0xEA88690F`, `0x4004690A`), so HAL and kernel agree on the struct ABI size
(0x2a88) and on the command set.

## Consumers of parsed data

* 3A_GAIN: AWB unit/golden gains and the AF infinity/macro slots → HAL 3A
  (see `../calibration/af-boundary.md`).
* SHADING_TABLE: LSC manager.
* PDAF: HAL PDAF.
* Not consumed (no stock layout enables them on fitted sensors): PART_NUMBER,
  MODULE_VERSION, LENS_ID, STEREO, DUMP, SHADING_TABLE_16_9.
* OIS: none (`../calibration/ois-boundary.md`).
* `/sys/class/camera_otp/camera_otp`: no reader found in the stock images
  (SELinux type `yft_fmt_device`, which points to a factory tool).
