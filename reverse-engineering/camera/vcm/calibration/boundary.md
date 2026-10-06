# AF calibration and firmware boundary

## Where AF calibration lives

| store | used for AF? | evidence |
|---|---|---|
| lens IC NVM / OTP | **no** | stock protocol has no read command and writes only `0x02/0x03/0x04/0x06/0x07` |
| sensor OTP | not for AF in this path | — |
| **camera module EEPROM** | **yes** | `camera_eeprom_v4l2.ko` contains an `AF CAM_CAL` parser printing `[AFInf]` / `[AFMacro]` (infinity and macro DAC); per-sensor `do_lens_id_*` / `do_2a_gain_*` handlers |
| HAL tuning / calibration libs | consumer | `libcameracustom.camera_calibration.core.so`, `libmtkcam_calibration_provider.so`, `libmtkcam_custom.calibration_convertor.so`; `vcm_list_0` declares `af_calib_bits = 10` (same scale as `vcm_bits = 10`) |

Ownership: EEPROM → `camera_eeprom_v4l2` (kernel, CAMERA-EEPROMS scope) → HAL
3A maps infinity/macro DAC onto the 0..1023 position range → kernel VCM driver
only ever receives absolute positions. The kernel VCM drivers never see
calibration data.

Runtime `android.lens.info.focusDistanceCalibration = UNCALIBRATED` on all four
cameras (focus distances are not metrically calibrated toward the API).

No per-unit calibration values are recorded in this research.

## Firmware

**NO FIRMWARE BOUNDARY** for the AF actuators: no firmware download, patch RAM,
NVM programming or persistent state is touched by any stock software.
