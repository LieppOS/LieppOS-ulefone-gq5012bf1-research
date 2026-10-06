# OIS calibration relationship (DW9781C)

**Result: no OIS calibration is read, parsed or consumed by any stock software path.**

| question | answer | evidence |
|---|---|---|
| OIS field in the kernel calibration ABI? | none. `STRUCT_CAM_CAL_DATA_STRUCT` has no OIS member, and `ENUM_CAMERA_CAM_CAL_TYPE_ENUM` has no OIS command | stock `cam_cal_format.h` ABI (byte-exact build) |
| OIS item in any fitted layout? | no. imx989's layout (the camera behind the DW9781C) enables LSC / 3A / PDAF only | decoded `cal_layout_table`s |
| EEPROM bytes read for camera 0 | 0x0000-3, 0x000a-0x001a, 0x001d-0x0768, 0x076a-0x076e, 0x0771-0x0d4c (kernel); 0x0d4f-0x194e (imgsensor QSC). All are accounted for by header/AWB/LSC/AF/PDAF/QSC | parsers + imgsensor stock data |
| DW9781C driver reads EEPROM? | no. Closed DW9781C driver: no firmware download, no EEPROM access | CAMERA-STACK `notes/dw9781c-ois.md` |
| HAL OIS driver? | none. `ois_list_0..5` contain only `Dummy`, and all cameras report `availableOpticalStabilization = [0]` | CAMERA-VCMS `userspace/hal-lens-map.md` |

Whether the camera-0 module's EEPROM physically holds OIS gyro or Hall
calibration elsewhere (for example above 0x194e) cannot be known offline. No
stock software reads it.
