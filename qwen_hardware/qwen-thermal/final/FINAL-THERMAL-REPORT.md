# Final thermal report — Ulefone Armor 29 Pro Thermal / GQ5012BF1

## Scope and confidence
This is an offline-first reconstruction from stock partitions, three OEM APKs, arm64 ELFs, DT, kernel modules, a boot/live filesystem snapshot and independent donor implementations. No undocumented command, forced FFC, firmware update, DFU entry or calibration write was performed.

Confidence terms: **PROVEN** = direct local code/data; **HIGH** = independent local evidence converges; **SUPPORTED** = product/public evidence plus compatible local stack; **DONOR** = independently reversed related module, not yet captured on this device; **UNKNOWN** = exact live evidence absent.

## Executive chain

```text
stock UI/factory test
 -> write platform rail node + extcon route node
 -> yft_tiny2c: four rails + I2C 0x3c ID (expected 0x4c59)
 -> extcon-mtk-usb: delayed internal USB routing
 -> Android USB permission/file descriptor
 -> bundled libusb/libuvc over /dev/bus/usb
 -> UVC image/radiometric stream + vdcmd vendor controls
 -> K/B, DPC/RMVC, FFC B/OOC, NUC-T, gain and environment correction
 -> uint16 absolute-temperature plane (classic path: 1/64 K)
 -> point/line/ROI/global measurement and AGC/palette display
```

---

## 1. Exact thermal hardware architecture
The module is not an Android Camera HAL sensor. It is a separately rail-gated InfiRay/InfiSense thermal assembly on an internal USB2 host route. A small I2C-visible front-end on MTK I2C8 exists only for presence/chip ID and power glue; imaging and commands use USB.

Local topology:
- DT bus `i2c@11e03000`, SCL GPIO ID 141, SDA 142.
- child `fm78100@0x3c`, compatible `mediatek,tiny2c_usb` / ID `tiny2c_usb-sensor`.
- `yft_tiny2c_usb.ko`: 1.8 V, 3.3 V, 5 V and 3.3 V-I/O enable GPIOs; mode and sensor-ID sysfs.
- `extcon-mtk-usb.ko`: internal USB/OTG route state through a separate class node.
- InfiRay module: detector, shutter, lens, processing/command firmware, flash/calibration and UVC device.

See `../re/hardware-map.md` and `../findings/kernel-tiny2c-usb-driver.md`.

## 2. Detector/module identity and confidence
Product/prior-hardware evidence identifies an InfiRay/InfiSense **Mini640-class**, 640x512, 12 um, radiometric 25 Hz module branded by Ulefone as **ThermoVue T2**. Confidence is **STRONGLY_SUPPORTED**, not silicon-proven in this offline corpus.

Important counter-evidence is preserved: FactoryMode has an exact 256x192 combined-stream test; M170infDlp has 256x386 factory/SOP constants; APK seed calibration also includes 160x120 arrays. This is a multi-product SDK carrying TC1/Eco/WN/P2/dual families. Such code baggage does not prove the fitted detector. A powered USB descriptor/frame or module label is still required to elevate 640x512 to PROVEN.

The expected I2C/front-end ID is **`0x4c59`**: `InfiraySmtTest` enables Pass only when the `sensor_id` sysfs string equals this value. It is not itself a detector model number.

## 3. AC020 role
`AC020` is exact in Java package/library names (`com.energy.ac020library`, `libAC020sdk.so`, `libircmd020.so`, `libadvirtempac020.so`). It denotes the vendor processing/SDK generation responsible for handle lifecycle, command dispatch, UVC integration, radiometry and firmware packaging. It is highly likely the module processing ASIC/firmware family, but no package string proves a physical die marking. Therefore the correct statement is **AC020-class module controller/SDK stack**, HIGH confidence.

## 4. Complete power-up/power-down path
FactoryMode provides the authoritative sequence.

Power up:
1. write `1` to `/sys/devices/platform/yft_tiny2c_usb/tiny2c_usb_mode`;
2. write `1` to `/sys/class/yft_extcon/tiny2c_mode`;
3. register `USBMonitor`, request Android USB permission, receive `UsbControlBlock`/fd;
4. create UVC/Ircam handle and start/initialize stream processing.

The platform driver sets all four rails high and sets external `yft_usb_flag=1`. Its I2C read performs a one-byte register-pointer write and two-byte read, combines big-endian ID, retries up to six attempts and returns `-ENODEV` on failure. The extcon driver parses 0/1 and queues delayed route work.

Power down:
1. stop/cancel UVC transfers and unregister USBMonitor;
2. release native handles/interfaces;
3. write `0` to both nodes. The platform driver sets all rails low and clears `yft_usb_flag`.

No per-rail sequencing delay exists in the recovered helper. Exact module settle and extcon-work delays remain UNKNOWN.

## 5. Internal USB topology
Userspace receives an Android USB device and passes fd, bus/address, VID/PID, USBFS root, DFU flag and format type to `libusbuvccamera020.so`. That library bundles InfiRay's Android libusb/libuvc fork and opens `/dev/bus/usb/<bus>/<device>`; it claims control/stream interfaces, chooses altsettings, submits transfers and handles detach/reclaim/status events.

The module is absent from boot dmesg because it is normally unpowered/unrouted until the app runs. The actual Armor VID:PID and USB speed are UNKNOWN. The donor P2 Pro's `0bda:5830` must not be assigned to this module.

## 6. Complete UVC descriptor/stream map
Available local map:

| Item | Recovered value | Confidence |
|---|---|---|
| access | Android USBFS/libusb | PROVEN |
| protocol | UVC stream + vendor control transfers | PROVEN |
| host formats | YUYV=0, NV12=1, NV12+temp=2, YUYV+temp=3 | PROVEN |
| factory mode | 256x384, 25 fps, bandwidth 1.0, YUYV+temperature | PROVEN for Eco test |
| SOP geometry | 256x386; two metadata lines | PROVEN for calibration tool |
| SDK families | 256x384, WN384x288, WN640x512 and V2 variants | PROVEN SDK |
| stream validation | expected versus actual byte count | PROVEN |
| interface/endpoint/altsettings | not captured | UNKNOWN |
| shipping frame geometry/offset | not captured | UNKNOWN |

The 256x384 mode is consistent with a 256x192 YUYV plane followed by a 256x192 LE16 thermal plane; M170infDlp's extra two lines are metadata. This interpretation is HIGH for that path. A true complete hardware descriptor table requires passive powered descriptors; static libraries cannot supply the instance-specific negotiated descriptors.

## 7. Command transport mechanism
Java `IrcmdEngine` calls JNI in `libAC020sdk`/`libircmd020`; `vdcmd.c` builds **standard**, **short** and **long** commands with read/write, polling, timeout and CRC8/16/32 helpers. A driver abstraction sends them by USB, SPI, MIPI-I2C, dual or omni transport.

OEM UVC disassembly corroborates control bRequests `0x44`/`0x45`, `wValue=0x78` and one-byte busy/status `wIndex=0x0200`. Independent P2 Pro USB-trace code gives the family mapping:
- standard header `0x1d00`, standard data/result `0x1d08`;
- long header/chunk `0x9d00`/`0x9d08`, long result `0x1d10`;
- OUT `0x41/0x45`, IN `0xC1/0x44`;
- poll ready when status bits 0 and 1 are both clear; upper status bits signal error.

This selector/header mapping is DONOR/HIGH family evidence until an Armor capture confirms it. Full wire detail: `../re/protocol/vdcmd-uvc-transport.md`.

## 8. Reconstructed command table
Exact semantic API is much larger than the numeric table. Numeric values below are donor-derived and must not be sent unverified.

| Meaning | Donor opcode | Local semantic evidence |
|---|---:|---|
| reset to ROM | `0x0805` | DFU engine + `fail to switch to rom status` |
| SPI transfer | `0x8201` | transport/flash APIs |
| device info | `0x8405` | `get_device_info`, DeviceInfoType |
| pseudo-color | `0x8409` | palette get/set APIs |
| shutter virtual temperature | `0x840c` | shutter/temp APIs |
| environmental/TPD parameter | `0x8514` | `prop_tpd_params`, EMS/TAU/Ta/Tu |
| current virtual temperature | `0x8b0d` | real-time temp/status APIs |
| Y16 preview start | `0x010a` | raw/radiometric stream support |
| preview start/stop | `0xc10f` / `0x020f` | Ircam stream lifecycle |
| write direction | OR `0x4000` | donor GET/SET convention |

Exact local symbol groups cover FFC/shutter, gain, palette, DPC, RMVC, KBC/TNR/HBC/VBC/SNR/DDE/AGC/gamma, zoom/mirror/cursor/ISO line, environmental correction, files/flash, firmware and diagnostics. Their names are archived under `evidence/binaries/symbols/`. Numeric AC020 opcode assignment remains UNKNOWN rather than fabricated.

## 9. Radiometric data format
`LibIRTemp(width,height)` allocates exactly `width*height*2` bytes. Point and region functions consume LE16 samples. For the classic path the exact stock conversion is:

```text
T_kelvin = raw_u16 / 64.0
T_celsius = raw_u16 / 64.0 - 273.15
```

Java `char` carries the unsigned 16-bit result. Point, line, rectangle, circle and global reducers return min/max/average and extrema coordinates. Some WN convenience overloads accept integer arrays already scaled to kelvin-like values; they should not be mixed with raw 1/64-K paths.

## 10. Temperature-conversion architecture
Pipeline:
1. parse detector/temperature plane and module metadata;
2. select high/low gain calibration;
3. apply pixel K/B, DPC/RMVC, FFC-derived B/OOC and temperature-dependent NUC-T;
4. derive environment factor from emissivity (`EMS`), transmission (`TAU`), ambient/background (`Ta`) and reflected/user temperature (`Tu`), humidity and distance;
5. apply `K_E/B_E` or newer NUC-T-aware correction;
6. produce corrected absolute-temperature plane;
7. reduce regions and convert to user units.

Exact symbols include `calculate_tau`, `calculate_vapor_pressure`, distance-table generation, emissivity tables, `calculate_KE_and_BE`, `calculate_new_KE_and_BE_with_nuc_t`, `temp_correct`, reverse correction and hot-mode methods. Internal polynomial constants/fixed-point scales remain UNKNOWN.

## 11. FFC/NUC/shutter behavior
Recovered exact enums:
- auto FFC enable; temperature threshold, min interval, max interval;
- manual shutter close/open and shutter closed/open/unknown status;
- all-FFC available/unavailable/cancel;
- FFC update B only, OOC only or both.

The shutter supplies a uniform field. FFC updates additive B and/or OOC; NUC-T and gain-specific KT/BT compensate detector/module drift. The SDK supports manual update/cancel/status, but production LieppOS should retain stock automatic cadence and guard manual operation.

## 12. AGC/image-processing behavior
Independent enum and JSON evidence yields:

```text
IR -> KBC -> TNR -> HBC/DPC -> VBC -> SNR -> DDE -> AGC -> gamma -> TPD -> mirror -> picture
```

The bundled profile enables KBC, DPC, RMVC, HBC, VBC, TNR, GPU SNR3, AGC, DDE, brightness/contrast, temperature processing, KTBT, NUCT and second correction/calibration. ISP pseudo-color, crop, transform and zoom are disabled in that profile but present as capabilities. High/low profiles contain exact calibration/filter thresholds documented in `../re/agc-image-processing.md`.

## 13. Palette implementation
Eleven 768-byte files are 256-entry RGB888 LUTs: Aurora, Black Hot, Glory Hot, Ironbow, Jungle, Medical, Night, Rainbow, Red Hot, Sepia and White Hot. `libcolormapping.so` provides RGB/RGBA, gray, stretch and temperature-clamp variants. Module-side pseudo-color also exists. Host-side palette rendering from the corrected plane is safest and allows stable range locking.

## 14. Measurement features
SDK supports:
- point;
- line, horizontal, vertical and slope line;
- rectangle and circle;
- full-frame min/max/average;
- coordinates of extrema;
- neighborhood point size 3..15;
- over-hot/over-cold alarms;
- auto gain and overexposure avoidance.

Results are radiometric, not reconstructed from RGB. UI-exposure detail for the exact stock build is incomplete because the captured live userspace was a LieppOS GSI, but application/JPEG/album code proves user measurement/media infrastructure.

## 15. Calibration files and structures
Exact module paths include:
- `user_data/user_eeprom_data.bin`;
- default and `secd_cali_data` high/low `tpd_kt1.bin`, `tpd_bt1.bin`, `tpd_nuc_t.bin`;
- `system_cfg.bin`, `default_cfg.bin`, `default_data/dual_fusion.bin`;
- `secd_cali_data/manufacturer_temporary_data.bin`.

FactoryMode proves the manufacturer temporary record must be at least 192 bytes and byte 0 is the calibrated flag. WN640 V2 Java requires each high/low NUC table to contain 8192 shorts. Generic APK seed arrays include 38,400-byte 160x120 K/B/RMVC data, 6,144-byte DPC, 9,600-byte OOC, 7,202-byte KT/BT, 32,768-byte generic NUC-T, 16,384-byte WN tables and 192-byte dual parameters. These are SDK examples, not replacement per-unit data.

## 16. Per-unit irreplaceable data
Preserve before any ROM experiment:
- runtime `/mnt/vendor/nvcfg/infiray` if present (not captured in extracted readonly partitions);
- module user EEPROM, serial/config, `system_cfg`/`default_cfg`;
- all default and second-calibration KT/BT/NUC-T, B/OOC, DPC and RMVC;
- manufacturer temporary/status and dual-fusion data;
- stock APKs, native libraries, permissions, SELinux labels and hashes.

Use read-only backup paths and hash every file. Never substitute APK generic assets. Loss can preserve a picture while destroying temperature accuracy.

## 17. Firmware/update mechanism
`libAC020sdk.so` contains DFU/DFUse, firmware download, CRC/hash, cJSON manifests and package handling. Names include `update.json`, `whole_package.json`, `update_package.json`, `split_package.json`, `dataread.bin` and `EXT.bin`. Upgrade modes are whole ZIP, update ZIP, single firmware and system config. Status progresses through init, ROM reset, firmware start/finish and whole-data start/finish.

Normal and DFU open share the USB routine (`is_dfu`, VID/PID, fd, bus/address). ROM entry likely re-enumerates. No DFU VID:PID/package signature was recovered and no update was attempted. Production integration must omit this path.

## 18. OEM app architecture
- **M170infisens**: user TC2C thermal app and complete shared InfiRay stack.
- **M170infDlp**: TC2C SOP/manufacturing calibration, high/low K/temp/lid corrections, dual registration, autofocus/calibration iterations, MNN support and firmware manager.
- **FactoryMode**: `InfiraySmtTest` checks ID `0x4c59`; `InfirayEcoTest` powers/routes USB, opens UVC, initializes libraries, validates calibration and launches either `com.energy.tc2c` or `com.infisense.eco` preview according to resource configuration.

## 19. JNI/native library graph

```text
IrcamEngine / IrcmdEngine / LibIRTemp / LibIRProcess / LibIRParse
  -> libAC020sdk.so                 JNI, handle lifecycle, DFU/package, pixel conversion
  -> libircmd020.so                 vdcmd and typed adv/basic commands
       -> libusbuvccamera020.so     USBFS/libusb/libuvc
       -> libdualuvccamera020.so    dual USB
       -> libomniircamera020.so     omni USB
  -> libircam.so                    C control/video handles and callbacks
  -> libadvirparse/process*.so      frame parse + ISP
  -> libadvirtempac020/advirtemp.so radiometry and measurement
  -> libcommonsdk.so                product-specific get_tempinfo dispatch
  -> libcolormapping.so             palettes
  -> libdualcalibration/common/gpudual.so
  -> libframecache.so / libirpack_tool.so
  -> libcommon_utils.so             package/certificate gate
  -> libencrypt_comm.so             AES/hash/signature/config support
```

There are 338 Java native declarations across 16 SDK classes; exact export inventories and hashes are archived.

## 20. Ulefone-exposed features
Confirmed stock/factory exposure: power/preview, calibration status, module ID, palettes, radiometric measurements, image/media infrastructure and automatic correction. Factory/SOP exposes calibration and firmware operations. Exact user-visible toggles for humidity/distance/reflected temperature, manual FFC and gain need an exact stock UI trace. Matrix: `../findings/feature-matrix.md`.

## 21. Hidden SDK/module capabilities
Bundled but not necessarily user-exposed: raw intermediate stage taps, Y16/raw frame, manual gain/FFC, detailed automatic-FFC parameters, source-stage selection, DPC/RMVC clear/save/restore, environmental tables, advanced alarms, host palette clamping, diagnostics/logs, file/flash access, firmware/DFU, dual UVC/native-camera fusion and factory recalibration. Module support for each must be queried safely; library presence alone is not enough.

## 22. Safe LieppOS integration architecture
Recommended **hybrid** approach:
- privileged broker owns both sysfs nodes and a strict lifecycle;
- narrow USB daemon opens only the measured thermal VID:PID/interface;
- initially reuse original signed vendor SDK for radiometry/calibration;
- Binder/AIDL exposes separate image and corrected temperature planes;
- open UI implements host palettes, spot/ROI/global measurement, safe alarms and metadata export;
- calibration vault performs read-only backup/hash checks;
- firmware, raw flash, calibration writes/clears and ROM entry are unavailable in normal builds.

State machine: `OFF -> ROUTING -> RAILS_ON -> WAIT_ENUM -> USB_OPEN -> STREAMING -> STOPPING -> USB_RELEASED -> RAILS_OFF`. All failures release/cancel USB before dropping rails. Compare strategies in `../re/lieppos-integration-design.md`.

## 23. Remaining unknowns
1. installed detector model/resolution/pitch and actual module label;
2. normal and DFU VID:PID, USB speed, interface/endpoint/altsetting descriptors;
3. shipping frame offsets and metadata-line fields;
4. complete AC020 numeric opcode table;
5. exact native calibration/environment fixed-point math;
6. complete per-unit binary structures/checksums;
7. power/mux/settle timing;
8. stock firmware FFC cadence and exact gain thresholds;
9. exact Ulefone user UI feature exposure;
10. measured radiometric accuracy/range/NETD of this unit.

## 24. Exact evidence required to resolve each unknown
- **Identity/geometry:** power through stock lifecycle; capture readonly USB product/manufacturer/serial/descriptors and one untouched frame; photograph module label only during authorized teardown.
- **USB map:** save raw descriptors and `/sys/bus/usb/devices/*` attributes after stock enumeration; no vendor writes.
- **Frame/metadata:** capture one frame for each mode and correlate offsets against stock `LibIRParse` outputs and byte counts.
- **Opcodes:** usbmon trace one harmless stock UI action at a time (palette/status/read-only settings), diff packets, repeat; never start with flash/ROM/FFC.
- **Radiometry math:** decompile named `libadvirtempac020` exports with Ghidra/rizin and verify with controlled blackbody/reference temperatures, emissivity and distance changes.
- **Calibration layout:** authorized read-only `advFileRead` from multiple units, hashes and structural differential analysis; never write back during RE.
- **Timing:** timestamp sysfs writes, kernel logs and enumeration/removal events during stock operation.
- **FFC/gain:** observe status and frame discontinuities over warm-up and scene range; use automatic stock behavior only.
- **Firmware:** obtain official package/docs or use an authorized spare module; production unit must not enter ROM.
- **UI:** record screenshots/settings/export metadata from the exact stock userspace build.
- **Accuracy:** controlled reference targets across gain range before and after FFC, compared to stock baseline.

---

## Handoff index
- Hardware/power: `../re/hardware-map.md`, `../re/power-sequencing.md`, `../findings/kernel-tiny2c-usb-driver.md`
- USB/UVC/protocol: `../re/usb-transport.md`, `../re/uvc-stream.md`, `../re/protocol/vdcmd-uvc-transport.md`
- API: `../re/reconstructed-ac020-api.h`, `../evidence/apk/java-native-signatures.txt`
- Algorithms: `../re/radiometry.md`, `../re/temperature-algorithms.md`, `../re/ffc-nuc.md`, `../re/agc-image-processing.md`, `../re/palettes.md`
- Calibration: `../re/calibration-format.md`, `../re/calibration/native-api-inventory.md`
- Software/security/integration: `../re/stock-app-behaviour.md`, `../re/libs/native-stack.md`, `../re/security-integrity.md`, `../re/lieppos-integration-design.md`
- Caveats/follow-up: `../findings/contradictions.md`, `../findings/unresolved.md`, `../progress/TODO.md`
