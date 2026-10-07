# Firmware boundary (thermal module, USB side)

| question | answer | class |
|---|---|---|
| host download at power-up? | **No.** The module boots from its own flash and enumerates ≈0.73 s after rails on with no host traffic beforehand (no DFU/ROM device appears first). | PROVEN (capture timeline) |
| external firmware file loaded by the kernel? | No `request_firmware` path, no firmware file in vendor/odm/firmware partitions targets the module. | PROVEN |
| USB firmware upload capability | Yes, explicit update only: `libAC020sdk` whole-package / single-firmware / system-config upgrade (M170infDlp `FirmwareUpgradeManager`, `UpgradeMode`). Normal mode: vdcmd `basic_firmware_download` (expands to `basic_reset_to_rom` 0x01/0x01/0x42, write-without-status) and `adv_cfg_file_*` (module 0x08) file writes; ROM/bootloader mode: USB DFU 1.1/DfuSe class requests + vendor 0x41/0x00, 0x41/0x01. | PROVEN (code); not exercised |
| internal flash | firmware + data (`whole_data.bin`) + module files (`default_data/…`, `secd_cali_data/…`, `user_data/…`, `system_cfg.bin`, `default_cfg.bin`) | PROVEN (SDK path enum, package) |
| ROM-mode USB identity | ROM-resident, not in any local artifact | UNKNOWN (update path only; does not affect streaming transport) |

## Stock-shipped images (metadata only; not copied)

| path | size | sha256 | loader | target |
|---|---:|---|---|---|
| `system/app/M170infDlp/M170infDlp.apk!assets/RS300_TC2C_00.00.04.07_01.46_whole_package_202412191140_EXT.zip` | 705 137 | `ec075727a035c25ab644eee78af79741fdde608be275f0bfed0d128ee975608c` | libAC020sdk whole-package upgrade | Tiny2-C module flash |
| ↳ `whole_package.json` | 365 | – | – | `"device_name":"TINY2-C"`, firmware 00.00.04.07 (md5 `b62475d9…7d02`), data 01.46 (md5 `ce51928b…630c`) |
| ↳ `firmware_EXT.bin` | 701 644 | `111e20d822f991eae42b08084f403bf6c75188dc5002869d19e404d20792a8a4` | same | module firmware; **contains the USB/UVC descriptor tables decoded in `usb-descriptors.md`** and the string literals "Thermal Cam Co.,Ltd", "202206223" |
| ↳ `whole_data.bin` | 2 813 952 | `401eb8bc00a038d269436b19bd692e172a0a6a8adced89f39ac5d350e3a15a09` | same | module data area (no USB descriptors) |
| `…M170infDlp.apk!assets/system_cfg.bin` | 327 680 | `c295daf4c8814d99b5fc7cff3a6c7aafe3e74237a37c8d036d6a310fa160115c` | system-config write | module flash |
| `…M170infDlp.apk!assets/system_cfg_burn.bin` | 327 680 | `6d58c029036547d908be8b351ca850686855095236dcc925c34fe50feee67aea` | same (factory burn) | module flash |

The descriptor analysis reads only the descriptor tables (fields printed by
`scripts/parse_fw_usb_desc.py`); firmware code/data are not reproduced. The unit's
running firmware version was not read live; the descriptor identity fields the unit
reported (S) equal those of 00.00.04.07, which is the version the stock updater installs.
