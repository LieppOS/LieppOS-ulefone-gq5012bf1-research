# CAMERA-EEPROMS — STATUS: DONE (static)

| item | result |
|---|---|
| shipped EEPROM/calibration modules | **1**: `camera_eeprom_v4l2.ko` (vendor_dlkm, modules.load #107, no deps). `imgsensor.ko` is a second, direct EEPROM reader (closed scope). `rt6421_eeprom` / `dw9828s_eeprom` / `lars2_eeprom` **RETRACTED** (nonexistent) |
| fitted EEPROMs | 4 external module EEPROMs: cam0 imx989 `7-0050`, cam1 s5kjn1 `4-0050`, cam2 s5kjn1main2 `2-0050`, cam3 ov64b `4-0053` (DT clients 7-0051/4-0050/2-0050/4-0051 are placeholders) |
| source | NothingOSS nkm `mt6878/Tetris/u` `5f75a3b` + 5 GQ5012BF1 commits (mtkcam `133c6c1`) + kdm headers `f6e1549`/`703d473`. 23 objects donor-unchanged, 6 donor-modified, 14 ODM-only (no public donor; binary-reconstructed) |
| whole file | stock == rebuild except `.note.gnu.build-id` (`cmp` after removal); B1 == B2 |
| functions | **126/126** byte-identical (115 unique names; 11 static duplicates). History: 33 EXACT / 43 DIFF / 50 MISSING (`5983d78`) → 126/126 (`54f9504`); re-verified here from a clean isolated build |
| data | **141/141** objects byte-identical (78/78 by-name in the shared parity tool) |
| ABI | imports 38/38 name+CRC, `__versions` order equal; exports 0/0; modinfo 10/10; vermagic equal; KCFI 126/126 (117 independently matched to prototypes by the xxHash64 oracle); relocations 3098/3098; strings 147/147; sections 47/48 (build-id) |
| mismatch classes A–G | none open. Historical: A (14 ODM layouts missing), C (calibration struct ABI: PartNumber 48→24, FuseId removed), D (layout tables, g_camCalList), B (donor imx989/ov64b layouts replaced). E/F/G: none |
| calibration formats | header 0x77006901 @0; AWB 0x0b/0x13; LSC 0x1d+0x74c; AF 0x76b/0x76d; PDAF 0x771+0x5dc; imgsensor QSC / 4-cell blocks |
| checksums | **none** in the stock kernel. Validation = header magic, nonzero AWB, AF ordering |
| read path | ioctl GKI_READ → layout search → preload (once per device index, never freed) → 1024 B I2C chunks, no retry, per-device mutex, global layout state unlocked |
| write path | **READ-ONLY IN STOCK** (`Common_write_region` = `mov w0,#0; ret`; no write hooks; `write()` → -EFAULT) |
| AF | 0x76d → S2aAf[0] (HAL AFInf), 0x76b → S2aAf[1] (HAL AFMacro), raw 10-bit DAC, no scaling |
| OIS | no OIS calibration read or consumed anywhere |
| HAL boundary | `libfeatureiodrv_mem.so` CamCalHelper (QUERY / NEED_POWER_ON / GKI_READ; S_SENSOR_INFO + read) |
| firmware | none |
