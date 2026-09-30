# Findings log

1. Stock ships three relevant APKs: user thermal (`M170infisens`), factory/SOP calibration (`M170infDlp`) and platform FactoryMode.
2. FactoryMode bundles the canonical AC020/InfiRay arm64 stack; hashes, symbols and strings were archived.
3. Data path is internal USB UVC through bundled libusb/USBFS, not Android Camera HAL.
4. Power is a coordinated two-node operation: yft platform rail/presence driver plus extcon USB routing.
5. `yft_tiny2c_usb.ko` controls four rails, sets `yft_usb_flag`, probes I2C 0x3c and exposes mode/sensor ID.
6. Factory SMT expected ID is exactly `0x4c59`.
7. Factory Eco path opens USB 256x384@25 as YUYV+temperature and verifies second-calibration status.
8. Classic radiometric samples are unsigned LE16, 1/64 kelvin; exact stock conversion is `raw/64-273.15`.
9. Module file API exposes default and per-unit high/low KT, BT and NUC-T, user EEPROM, system/default config and dual fusion.
10. Per-unit second-calibration record is >=192 bytes; byte 0 equals 1 when calibrated.
11. ISP pipeline and high/low JSON profiles cover KBC/DPC/RMVC/HBC/VBC/TNR/SNR/DDE/AGC/gamma/TPD.
12. Eleven 256xRGB888 palette LUTs are embedded; native host rendering supports clamp/stretch/gray.
13. `libircmd020` implements transport-independent standard/short/long vdcmd with polling and CRC; USB packetization is in UVC libraries.
14. OEM UVC disassembly corroborates vendor requests 0x44/0x45, wValue 0x78 and status selector 0x200; donor traces provide remaining selector/header mapping.
15. Native package/signature gates whitelist multiple InfiRay OEM packages and SHA-1 certificates.
16. Firmware engine supports DFU/DFUse and whole/update/split packages; no update was attempted.
17. Static SDK is multi-product and includes 160x120, 256x192, 384x288 and 640x512 artifacts. Bundled support does not identify the installed detector by itself.
