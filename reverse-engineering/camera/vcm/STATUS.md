# CAMERA-VCMS — STATUS: DONE (static)

| item | result |
|---|---|
| shipped lens modules | 6: `main_vcm`, `main2_vcm`, `main3_vcm`, `main4_vcm`, `sub_vcm`, `camera_af_media` (+ `dw9781c`, OIS scope, already closed) |
| fitted actuators | 3 × DW9800W command set, lens_id 0x9800, 7-bit 0x0C |
| association | cam0 imx989 → `7-000c` `main_vcm`; cam2 s5kjn1main2 → `2-000c` `main4_vcm`; cam3 ov64b → `4-000c` `main2_vcm`; cam1 s5kjn1 fixed focus |
| power | AFVDD 2.8 V from WL2864C custom-LDO channels 5 (cam0, cam3) / 6 (cam2), switched by imgsensor; no actuator GPIO/regulator/pinctrl |
| source | ALPS `5e415e059253` (content = `7fe884aeb2a6`), DIRECT_SOURCE_MATCH |
| function / data parity | 57/57 functions, 143/143 data objects |
| ABI | imports 168/168 with CRC and order; no exports; KCFI 57/57; modinfo exact |
| residual | `.note.gnu.build-id` only; B1 == B2 |
| protocol | binary-proven from the HAL table: init `02/06/07`, move `03/04`, park to 512 by 100/5 ms, release `02=20`; no reads |
| HAL boundary | `libcam.hal3a.lensdrv.so` VCMDrv → `libcameracustom.lens.so` `GetVcmDriverName` (`vcm_list_0` only) → `VIDIOC_MTK_S_LENS_INFO` + `V4L2_CID_FOCUS_ABSOLUTE` |
| OIS | separate chip/bus; HAL OIS table empty |
| calibration | module EEPROM AF block (AFInf/AFMacro) via `camera_eeprom_v4l2`; HAL consumes |
| firmware | **NO FIRMWARE BOUNDARY** |

## Workspace

Moved `Reverse Engineer - PARTIAL/CAMERA-VCMS` → `Reverse Engineer - DONE/CAMERA-VCMS` on 2026-10-06 (index totals 67/63/3 → 68/62/3; 81 manifest entries hash-verified).
