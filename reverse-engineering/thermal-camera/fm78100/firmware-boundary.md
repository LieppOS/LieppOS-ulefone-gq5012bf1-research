# Firmware boundary

## 8-003c (I2C side)

None. The stock kernel performs only two single-byte reads; no ROM patch, firmware file,
EEPROM/OTP access or boot-mode change ever goes over I2C. `yft_tiny2c_usb.ko` calls no
`request_firmware*`. There is no fm78100 firmware (the part is not fitted).

## Thermal module (USB side, owned by AC020-UVC)

The module ASIC boots from its own flash (USB enumeration ≈0.73 s after rails on, with no
host download). Stock carries update images that are written over USB vendor commands
(`sys_reset_to_rom 0x0805`, `adv_cfg_file_*`, `UpgradeMode`), never over I2C.

| path (inside APK) | size | sha256 | loader | consumer | expected device |
|---|---:|---|---|---|---|
| `system/app/M170infDlp/M170infDlp.apk!assets/RS300_TC2C_00.00.04.07_01.46_whole_package_202412191140_EXT.zip` | 705137 | `ec075727a035c25ab644eee78af79741fdde608be275f0bfed0d128ee975608c` | `libAC020sdk.so` DFU / whole-package upgrade (UpgradeMode WHOLE_PACKAGE_ZIP) | module flash | `"device_name":"TINY2-C"`, firmware 00.00.04.07 (`firmware_EXT.bin`, 701644 B), data 01.46 (`whole_data.bin`, 2813952 B) |
| `…M170infDlp.apk!assets/system_cfg.bin` | 327680 | `c295daf4c8814d99b5fc7cff3a6c7aafe3e74237a37c8d036d6a310fa160115c` | SDK system-config write (UpgradeMode SYSTEM_CONFIG_FILE) | module flash | Tiny2-C |
| `…M170infDlp.apk!assets/system_cfg_burn.bin` | 327680 | `6d58c029036547d908be8b351ca850686855095236dcc925c34fe50feee67aea` | same (factory burn variant) | module flash | Tiny2-C |

APK hashes: M170infDlp.apk `dc9765c3…c875` (93564746 B), M170infisens.apk `255ec1ab…8b30`
(140254014 B). The images are **not** copied into this repository.

No vendor/odm/firmware partition file targets the thermal module; GKI and vendor modules
contain no thermal firmware.
