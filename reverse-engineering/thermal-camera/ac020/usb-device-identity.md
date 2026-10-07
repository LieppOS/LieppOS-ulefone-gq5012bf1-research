# AC020 / thermal module — USB device identity

## Verdict on "AC020"

| question | answer | class |
|---|---|---|
| Is AC020 a USB bridge/controller chip? | **No.** No bridge, hub or second USB device exists: the module enumerates directly on xHCI root port `1-1` and its firmware carries its own device/UVC descriptors. | PROVEN |
| Is AC020 the thermal-sensor interface ASIC? | **Not as a part number.** "AC020" is the InfiRay/Raytron **SDK generation name** (`ANDROID_RS300_SDK`, `libAC020sdk.so`, `libircmd020.so`, `libusbuvccamera020.so`, `com.energy.ac020library`) for modules driven through the "020" vdcmd command set. The silicon is the module's own LY-series ASIC (`0x4c59` "LY" at 8-003c). | PROVEN (naming) / STRONGLY SUPPORTED (ASIC tag) |
| Stale identifier? | It is a **software-family name**, valid for the SDK; it must not be read as a chip. The component folder keeps the name. | PROVEN |
| Module | Raytron/InfiRay **Tiny2-C (TC2-C)**, 256×192 LWIR, 25 Hz | PROVEN (fw package `device_name` TINY2-C; descriptors below) |

## Normal (application) mode — one configuration

| field | value | source |
|---|---|---|
| idVendor:idProduct | **3474:4321** | S (stock capture), F (firmware descriptor) |
| bcdDevice | 2.00 | S, F |
| bcdUSB / speed | 2.00 / high-speed 480 Mbit/s | S, F |
| bDeviceClass/Sub/Proto | EF/02/01 (Misc, IAD) | S, F |
| bMaxPacketSize0 | 64 | F (P agrees) |
| iManufacturer / iProduct / iSerialNumber | 1 "Thermal Cam Co.,Ltd" / 2 "Camera" / 3 "202206223" | S; both strings are literals in firmware 00.00.04.07 (F) |
| serial behaviour | **firmware constant**, not per-unit (literal in the shipped firmware image; identical on unrelated public units) | PROVEN |
| bNumConfigurations | 1 (S: Linux bound config 1; firmware template byte is patched at run time) | S |
| configuration | wTotalLength **0x00DF (223)** = 9 + 214 descriptor bytes in F; 2 interfaces | F (P agrees) |
| interfaces | if0 VideoControl (1 EP), if1 VideoStreaming (alt0 0 EP, alt1 1 EP) | S, F |
| device qualifier | present (F), bNumConfigurations patched at run time | F |
| Android/host view | `UsbHostManager: vidpid 3474:4321 … hasAudio/HID/Storage: false/false/false` | S |

Sources: **S** = `usb-research/evidence/thermal-camera-*` (stock unit, 2026-09-23, read-only
sysfs + logcat); **F** = USB descriptor tables inside the stock-shipped module firmware
`firmware_EXT.bin` 00.00.04.07 (`M170infDlp.apk!assets/RS300_TC2C_00.00.04.07_01.46_whole_package_202412191140_EXT.zip`,
md5 matches `whole_package.json`), decoded by `scripts/parse_fw_usb_desc.py`
(`firmware-descriptor-dump.txt`); **P** = public `lsusb -v` of another unit with identical
identity (PyThermalCamera issue #22). F and P agree field-for-field; S agrees on every field
it records.

## Firmware-update (ROM/DFU) mode — separate, not on the streaming path

Entered only by `basic_reset_to_bootloader` / `basic_reset_to_rom` from the SDK upgrade or
`check_device_mode` paths (M170infDlp `FirmwareUpgradeManager`, `DriverType.USB`). After
re-enumeration `libAC020sdk.so` speaks USB DFU 1.1/DfuSe (class requests 0x21/0xA1
bRequest 0–6, DFU functional descriptor 0x21) plus two vendor requests (0x41/0x00
flash-type select v2, 0x41/0x01 reset). The ROM-mode VID/PID/descriptors are ROM-resident
and appear in no local artifact: **UNKNOWN**, outside normal transport (see
`firmware-boundary.md`).

## Stock host matching

The apps do not pin VID/PID: `res/xml/device_filter.xml` (M170infisens, M170infDlp)
matches class 14, 239/2, 14/9, 2/0, 6, 39/0 plus five unrelated VID/PIDs (template from
the UVCCamera library); FactoryMode matches class 239/2 only.
