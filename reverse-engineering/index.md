# GQ5012BF1 Reverse-Engineering Index

## Purpose

Authoritative human-readable ownership/status map for every canonical GQ5012BF1 reverse-engineering component needed by a LieppOS custom ROM and custom-kernel port.

- **Phone:** Ulefone Armor 29 Pro Thermal
- **Board/product:** GQ5012BF1
- **Platform:** MediaTek MT6878T / Dimensity 7400 family
- **Audit date:** 2026-10-07
- **Authoritative workspace:** `/home/armol/androido_dalykai/LieppOS custom ROM/`
- **Machine database:** [`coverage-audit/components.tsv`](coverage-audit/components.tsv)

## Status definitions

- **DONE:** the explicitly named static/source/parity scope is closed. It does **not** imply open proprietary firmware/HAL/TA code or complete runtime validation.
- **PARTIAL:** represented and useful, with an explicit actionable, proprietary, physical or umbrella boundary.
- **BLOCKED:** the required evidence/source/access is unavailable; the blocker is named.
- **TODO:** accepted component with no meaningful work yet. Current count is zero.

## Methodology and evidence precedence

The audit joins every shipped kernel module, effective merged DT compatible, physical hardware row, HAL/interface, init service, firmware/calibration payload, secure-world surface, partition family, Android integration file and significant native library back to the canonical workspace folders. Coverage classes are A dedicated, B broader owner, C generic/no dedicated RE, D dead/reference, E unmapped.

Evidence precedence: (1) current verified stock/runtime captures, (2) newest authoritative research, (3) exact binary parity, (4) active device/vendor tree, (5) older provenance, (6) donor/reference assumptions.

> **DONE is scope-specific.** Read the Kernel/Userspace/Firmware/Hardware columns and boundary; never infer whole-device source parity from the folder status.

RE completeness is separate from pack hygiene. The latest manifest result is recorded in [`coverage-audit/notes/MANIFEST-HYGIENE.md`](coverage-audit/notes/MANIFEST-HYGIENE.md).

## Current totals

| Status | Count |
|---|---:|
| DONE | 94 |
| PARTIAL | 36 |
| BLOCKED | 3 |
| TODO | 0 |
| **TOTAL** | **133** |

## PARTIAL classification

| Classification | Count |
|---|---:|
| A — Actionable / statically closeable | 7 |
| B — Kernel/source closed; broader proprietary scope remains | 12 |
| C — Proprietary boundary | 8 |
| D — Hardware/runtime/teardown gated | 4 |
| E — Stale/duplicate/wrong scope | 0 |
| F — Broad umbrella/tracking scope | 5 |

## Master component table

| Component | Status | Subsystem | Scope | Coverage class | Kernel | Userspace/HAL | Firmware | Hardware | Remaining work / boundary | Research |
|---|---|---|---|---|---|---|---|---|---|---|
| AB-SUPER-GEOMETRY | DONE | BOOT/STORAGE | A/B physical and dynamic-super geometry | SCOPE-CLOSED | N/A | N/A | SOURCE-AVAILABLE | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](storage/STATUS.md) |
| AC020-UVC | DONE | THERMAL CAMERA | Raytron/InfiRay Tiny2-C (TC2-C) module ASIC as USB device 3474:4321 ("AC020" = SDK family name, not a chip) | SCOPE-CLOSED | N/A | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](thermal-camera/ac020/STATUS.md) |
| ANDROID-INIT | PARTIAL | ANDROID INTEGRATION | Android 15 MTK init and Android 16 GSI interaction | A | N/A | PARTIAL | N/A | N/A | Reconcile stock/current service ordering and validate property-trigger behavior. | [report](coverage-audit/SUMMARY.md) |
| AUDIO-DSP | PARTIAL | AUDIO | MTK audio DSP and routing stack | B | CLOSED | PROPRIETARY | SIGNED/BINARY | PROVEN | Kernel AFE/DSP transport is closed; DSP protocol, firmware, routing and calibration remain proprietary. | [report](audio/STATUS.md) |
| AUDIO-DSP-KERNEL | DONE | AUDIO | Linux ADSP/SCP audio transport modules and ABI | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](audio/STATUS.md) |
| AVB-SIGNING-CHAIN | DONE | BOOT/SECURITY | AVB keys, descriptors, rollback and vbmeta topology | SCOPE-CLOSED | N/A | N/A | SOURCE-AVAILABLE | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](tkcore/STATUS.md) |
| AW2013-RGB-LED | DONE | DISPLAY/INPUT | Awinic AW2013 RGB LED controller | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Only integration qualification remains | [report](display-input/SURVEY.md) |
| AW36515-FLASH | DONE | CAMERA | Awinic AW36515 dual-channel flash/IR driver | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](camera-stack/STATUS.md) |
| AW36518-FLASH | DONE | CAMERA | Awinic AW36518 flash driver | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Residual trigger (scheduling/.data order); runtime channel validation | [report](camera-stack/STATUS.md) |
| AW36518-V2-FLASH | DONE | CAMERA | Awinic AW36518 v2 stock variant | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Residual trigger; runtime channel validation | [report](camera-stack/STATUS.md) |
| AW883XX-SPEAKER-AMP | DONE | AUDIO | Awinic AW88394 smart speaker amplifier | SCOPE-CLOSED | CLOSED | N/A | BINARY-ONLY | PROVEN | Board acoustic calibration is integration data, not missing driver RE | [report](audio/STATUS.md) |
| BACKLIGHT-DISPLAY-GLUE | DONE | DISPLAY/INPUT | Main/rear brightness, bias and thermal-backlight kernel glue | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | runtime brightness validation only | [report](display-input/SURVEY.md) |
| BATTERY-PACK | PARTIAL | POWER/CHARGING | GQ5012BF1 battery pack and gauge integration | D | CLOSED | PARTIAL | DEVICE-INTERNAL | TEARDOWN | Cell/BMS identity, connector topology, calibration and ageing model need teardown/runtime evidence. | [report](power-charging/README.md) |
| BLUETOOTH | PARTIAL | CONNECTIVITY | MT6878 CONNSYS BGF MCU + MT6637 A-die BT RF; BTIF transport, /dev/stpbt | B | CLOSED | PROPRIETARY | SIGNED | PROVEN | Kernel transport is closed; controller firmware, vendor HAL internals and LE Audio behavior remain proprietary/runtime-gated. | [report](connectivity/STATUS.md) |
| BOOT-CONTROL-SLOTS | DONE | BOOT/OTA | A/B slot metadata and safe Slot-B development contract | SCOPE-CLOSED | N/A | PROPRIETARY (outside scope) | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](coverage-audit/SUMMARY.md) |
| BOOT-IMAGES | DONE | BOOT | boot, vendor_boot and init_boot image geometry/content contract | SCOPE-CLOSED | CLOSED | N/A | SOURCE-AVAILABLE | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](coverage-audit/SUMMARY.md) |
| CAMERA-EEPROMS | DONE | CAMERA | 4 external camera-module EEPROMs: cam0 7-0050, cam1 4-0050, cam2 2-0050, cam3 4-0053 | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | None for the static kernel/DT/HAL-interface scope; EEPROM die/capacity not electronically identifiable (no ID register), per-unit calibration bytes out of scope | [report](camera/eeprom/STATUS.md) |
| CAMERA-HAL-ISP | PARTIAL | CAMERA | MT6878 ISP7sp + MTK mtkcam AIDL CameraProvider | B | PARTIAL | PROPRIETARY | SIGNED/BINARY | PROVEN | Sensor-side kernel work is closed, but ISP kernel parity remains mixed and HAL/3A/tuning/CCU are proprietary. | [report](camera-stack/STATUS.md) |
| CAMERA-IMX989 | DONE | CAMERA | Sony IMX989 (chip-ID 0x0989 PROVEN on this unit); the same slot also carries the CTS-board sub-driver `imx989cts` reporting **0x0988 = chip-ID − 1**… | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | no driver RE left. The frame-descriptor keep/fix decision is now an explicit build flag, not an unknown; the five family functions the 2026-10-02 donor pass reported `(stock-only)` (`imx989_awb_gain` + four `i… | [report](camera-stack/STATUS.md) |
| CAMERA-OV64B | DONE | CAMERA | OmniVision OV64B, chip-ID 0x566442 (bound on this unit), camera 3 rear, the 64 MP night-vision camera. DT `sensor4` on i2c-4 (`4-0020`), write-IDs 0x… | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](camera-stack/ov64b/STATUS.md) |
| CAMERA-S5KJN1 | DONE | CAMERA | Samsung S5KJN1 front camera (chip-ID 0x38E1) at write-ID 0x7A. DT `sensor1` on i2c-4 (`4-0010`), csi-port-2 D-PHY 4-lane, MCLK CAMTG2 24 MHz, WL2864C… | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](camera-stack/s5kjn1/STATUS.md) |
| CAMERA-S5KJN1MAIN2 | DONE | CAMERA | Samsung S5KJN1 die (0x38E1). The driver pseudo-ID is 0x38E2 (low byte +1, non-CTS boards only). Camera 2, the rear 16 mm ultrawide | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](camera-stack/s5kjn1main2/STATUS.md) |
| CAMERA-VCMS | DONE | CAMERA | 3 × DW9800W-command-set AF actuators at 0x0C (cam0 i2c-7, cam2 i2c-2, cam3 i2c-4); front camera fixed focus | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | None for the static kernel/DT/HAL-interface scope; the actuator die is identified by command set (no chip-ID read exists in the stock protocol), physical part marking not required | [report](camera/vcm/STATUS.md) |
| CCCI-KERNEL | DONE | MODEM/TELEPHONY | CCCI core/control/CCIF/AUXADC/SCP bridge modules | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](modem/STATUS.md) |
| CCMNI-KERNEL | DONE | MODEM/TELEPHONY | Mobile-data Linux netdev layer | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](modem/STATUS.md) |
| CO5300-REAR-DISPLAY | DONE | DISPLAY/INPUT | `vendor_dlkm/lib/modules/spi_tiny_co5300_lcd.ko` (SHA-256 `39eecad8…9742`) plus `tinylcd.default.so` HAL | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](display-input/rear-display-input/co5300/README.md) |
| CONNFEM | DONE | CONNECTIVITY | Connectivity RF front-end selection and no-FEM board contract | SCOPE-CLOSED | CLOSED | N/A | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](connectivity/STATUS.md) |
| CONNINFRA-KERNEL | DONE | CONNECTIVITY | CONNSYS core, connscp and platform transport | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | BINARY-ONLY | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](connectivity/STATUS.md) |
| COOLING-HARDWARE | PARTIAL | POWER/CHARGING | Device cooling stack and thermal limits | D | CLOSED | PARTIAL | N/A | TEARDOWN | Material stack, heat spreaders, contact paths and measured thermal model require physical inspection. | [report](power-charging/README.md) |
| CUSTOM-LDO | DONE | CAMERA | YFT custom LDO forwarding shim | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](camera-stack/STATUS.md) |
| DPMAIF-KERNEL | DONE | MODEM/TELEPHONY | Modem packet-data DMA host interface | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](modem/STATUS.md) |
| DRAM-MEMORY | PARTIAL | MEMORY | LPDDR/DRAM configuration | D | PARTIAL | N/A | SIGNED | TEARDOWN | Exact package/topology/timings and training firmware cannot be recovered from normal Android artifacts alone. | [report](coverage-audit/SUMMARY.md) |
| DTB-DTBO | PARTIAL | BOOT/KERNEL PACKAGING | MT6878 base DTB plus GQ5012BF1 DTBO | A | PARTIAL | N/A | SOURCE | PARTIAL | Effective tree is inventoried; source-complete DTS and bootloader mutation/runtime validation remain. | [report](coverage-audit/SUMMARY.md) |
| DW9781C-OIS | DONE | CAMERA | Dongwoon DW9781C OIS controller as described by the stock DT: `i2c@11c23000` (i2c-4) `camera-ois-main@e`, driver-forced address 0x0A, hf_manager sens… | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](camera-stack/dw9781c-ois/STATUS.md) |
| ESIM-EUICC-ABSENCE | DONE | CONNECTIVITY | eSIM/eUICC capability investigation | SCOPE-CLOSED | N/A | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](connectivity/STATUS.md) |
| EXTCON-MTK-USB | DONE | USB/TYPE-C | MediaTek USB extcon policy provider | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Runtime notify coverage only | [report](usb/STATUS.md) |
| EXTERNAL-USB | DONE | USB/TYPE-C | external USB-C receptacle on the single USB2-only MTU3 / `usb2-phy0` fabric | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](usb/STATUS.md) |
| FFA-V10 | DONE | SECURITY/TEE | Arm FF-A v1.0 MTK implementation | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](tkcore/STATUS.md) |
| FINGERPRINT-PLATFORM-SHIM | DONE | FINGERPRINT | YFT fingerprint platform shim | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](microarray-fp-tee/STATUS.md) |
| FIRMWARE-INVENTORY | PARTIAL | FIRMWARE | Cross-subsystem firmware/calibration metadata inventory | F | MIXED | MIXED | MIXED | N/A | Persistent cross-subsystem inventory; payload ownership changes whenever stock/vendor extraction changes. | [report](coverage-audit/SUMMARY.md) |
| FM-KERNEL | DONE | CONNECTIVITY | MT6637 FM receiver kernel driver path | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](connectivity/STATUS.md) |
| FM-RADIO-HEADSET | PARTIAL | AUDIO | Fitted FM receiver path and 3.5 mm headset jack | B | CLOSED | PROPRIETARY | BINARY | PARTIAL | Kernel/headset path is closed; FM app/JNI/patch, LNA/antenna identity and RF performance remain. | [report](audio/STATUS.md) |
| FM78100-COMPANION | DONE | THERMAL CAMERA | I2C8 `8-003c` = I2C-slave control port of the thermal module's own ASIC (Raytron/InfiRay Tiny2-C / TC2-C, LY-series ASIC). **Not an FM78100** — the n… | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](thermal-camera/fm78100/STATUS.md) |
| FT3680-TOUCH | PARTIAL | DISPLAY/INPUT | FocalTech FT3680 SPI main-touch kernel driver | A | PARTIAL | N/A | DEVICE-INTERNAL | PROVEN | Core contract is recovered, but 40 functions remain size-different and 68 remain outside normalized parity classes. | [report](display-input/ft3680/README.md) |
| GKI-KMI-BASELINE | DONE | BOOT/KERNEL PACKAGING | Android 14 Linux 6.1 GKI ab/12901745 | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Production packaging/runtime qualification, not further identity RE | [report](coverage-audit/SUMMARY.md) |
| GNSS | PARTIAL | GNSS | MT6878 CONNSYS GPS MCU + MT6637 A-die GNSS (L1+L5); no MT6686 on this SKU | B | CLOSED | PROPRIETARY | SIGNED | PROVEN | Kernel transport is closed; connsys GNSS firmware, mnld/libmnl and live L1/L5 behavior remain proprietary/runtime-gated. | [report](connectivity/gnss/README.md) |
| GNSS-KERNEL-TRANSPORT | DONE | GNSS | GNSS kernel transport and connsys interface | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](connectivity/gnss/README.md) |
| GZ-IPC-MOD | DONE | SECURITY/TEE | MediaTek GenieZone IPC provider | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](tkcore/STATUS.md) |
| GZ-MAIN-MOD | DONE | SECURITY/TEE | MediaTek GenieZone main module | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](tkcore/STATUS.md) |
| GZ-TRANSPORT | DONE | SECURITY/TEE | GenieZone transport support layer | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | SIGNED-BINARY | PROVEN | None for the kernel transport scope; GenieZone/TEE secure-world images and payloads are proprietary firmware outside this scope | [report](geniezone/transport/README.md) |
| GZ-TRUSTY-MOD | DONE | SECURITY/TEE | MediaTek GenieZone Trusty transport | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](tkcore/STATUS.md) |
| GZ-TZ-SYSTEM | DONE | SECURITY/TEE | MediaTek GZ TZ system provider | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](tkcore/STATUS.md) |
| HAPTICS | DONE | DISPLAY/INPUT | Board vibration/haptics path | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Motor part number (teardown), drive profile on hardware | [report](display-input/SURVEY.md) |
| HYNITRON-REAR-TOUCH | DONE | DISPLAY/INPUT | Hynitron **CST820** (0xB7, CST8xx self-cap), I2C0 `i2c@11c20000` 0x15 @400 kHz; IRQ GPIO11 falling+ONESHOT (wake), reset GPIO32, VDD-en GPIO119 | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](display-input/rear-display-input/hynitron/README.md) |
| ICM4N607-IMU | PARTIAL | SENSORS/TINYSYS | IvenSense ICM4N607 accelerometer/gyro | C | CLOSED (transport) | PROPRIETARY | SIGNED (SCP) | PROVEN | The physical sensor driver lives inside signed SCP firmware; exact register protocol and calibration are unavailable. | [report](sensors/STATUS.md) |
| IMS | PARTIAL | MODEM/TELEPHONY | Proprietary IMS/VoLTE/VoWiFi/RCS/video-telephony stack | C | CLOSED (kernel transport) | PROPRIETARY | SIGNED | PROVEN | VoLTE/VoWiFi/RCS/video-telephony implementation is a proprietary modem/RIL/IMS island. | [report](modem/STATUS.md) |
| INIT-INSMOD | DONE | BOOT/KERNEL PACKAGING | init.insmod configuration and first-stage module loading | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](coverage-audit/SUMMARY.md) |
| INTERNAL-THERMAL-USB | DONE | THERMAL CAMERA | Raytron/InfiRay Tiny2-C module (USB 3474:4321) on the MT6878 MTU3/xHCI root port 1-1 | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](thermal-camera/internal-usb/STATUS.md) |
| IR-BLASTER | DONE | IR/RUGGED | Consumer IR PWM/emitter kernel and board path | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Physical emitter part + authorized optical test (runtime/physical only) | [report](coverage-audit/SUMMARY.md) |
| KEYSTORE-VOLD-KEYMINT | PARTIAL | SECURITY/TEE | TrustKernel KeyMint/Gatekeeper with Android vold/Keystore2 | B | CLOSED (normal world) | PROPRIETARY | SIGNED (TEE) | N/A | Normal-world FBE/RPMB/KeyMint integration is mapped; TA semantics, keys and provisioning remain proprietary. | [report](tkcore/STATUS.md) |
| LN2403-CAMPLIGHT | DONE | IR/RUGGED | LN2403/PWM camp-light and red/blue light controller | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](coverage-audit/SUMMARY.md) |
| MADEV-FINGERPRINT | DONE | FINGERPRINT | Madev Fingerprint | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](microarray-fp-tee/STATUS.md) |
| MEDIATEK-DRM | DONE | DISPLAY/INPUT | MT6878 DRM core and generic panel driver modules | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Runtime validation; exact text of padded source lines (count proven); VTDR6115 reserved-padding header can now be swapped for the real one (optional) | [report](display-input/mediatek-drm/README.md) |
| MICROARRAY-FP-TEE | DONE | FINGERPRINT/SECURITY | MicroArray fingerprint TEE client kernel driver | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](microarray-fp-tee/STATUS.md) |
| MICROPHONES | PARTIAL | AUDIO | Board microphone topology and audio routing | D | CLOSED | PARTIAL | N/A | TEARDOWN | Package/acoustic-port confirmation plus enforcing-SELinux and full Audio HAL tests remain. | [report](audio/STATUS.md) |
| MICROSD | DONE | STORAGE | Android/recovery removable-storage contract | SCOPE-CLOSED | N/A | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](storage/microsd/README.md) |
| MICROSD-KERNEL | DONE | STORAGE | per-module SUMMARY, function/data/ABI/relocation TSVs, full-module section proofs | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Runtime validation (card insert/remove, eject, format matrix, Android framework); the framework/runtime validation list itself is carried as remaining integration work in `DONE/MICROSD` (named scope closed 202… | [report](storage/STATUS.md) |
| MMC5603-MAGNETOMETER | PARTIAL | SENSORS/TINYSYS | Memsic MMC5603NJ magnetometer | C | CLOSED (transport) | PROPRIETARY | SIGNED (SCP) | PROVEN | Register driver and fusion/calibration are inside signed SCP firmware. | [report](sensors/STATUS.md) |
| MODEM-FIRMWARE | PARTIAL | MODEM/TELEPHONY | Signed MT6878 MD1 firmware and carrier configuration | C | CLOSED (loader) | PROPRIETARY | SIGNED | PROVEN | MD1 code, carrier configuration, RF calibration and signing keys are proprietary. | [report](modem/STATUS.md) |
| MODEM-KERNEL-TRANSPORT | DONE | MODEM/TELEPHONY | Aggregate reconstructable Linux modem transport boundary | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](modem/STATUS.md) |
| MT6369-AUDIO-CODEC | DONE | AUDIO | MT6369 second PMIC, SPMI USID 5 | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | only physical/acoustic and runtime qualification | [report](audio/STATUS.md) |
| MT6375-CHARGER | DONE | POWER/CHARGING | Mt6375 Charger | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](power-charging/README.md) |
| MT6637-BT-KERNEL | DONE | CONNECTIVITY | MT6637 Bluetooth Linux transport | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](connectivity/STATUS.md) |
| MT6637-WIFI | PARTIAL | CONNECTIVITY | MT6878 CONNSYS (SOC7_0/CONNAC2X) Wi-Fi MAC + MT6637 A-die RF (chip id 0x66378a01), 2x2 Wi-Fi 6E | B | CLOSED | PROPRIETARY | SIGNED/BINARY | PROVEN | Kernel path is closed; controller firmware, NVRAM/calibration and vendor HAL internals remain proprietary. | [report](connectivity/STATUS.md) |
| MT6637-WIFI-KERNEL | DONE | CONNECTIVITY | MT6637 Wi-Fi Linux driver stack | SCOPE-CLOSED | CLOSED | N/A | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](connectivity/STATUS.md) |
| MT6878-AFE | DONE | AUDIO | MT6878 AFE at 0x11050000, machine card `mt6878-mt6369` | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | runtime qualification only | [report](audio/STATUS.md) |
| MTK-DISP-NOTIFY | DONE | DISPLAY/INPUT | `mtk_disp_notify.ko` (vendor ramdisk), sha256 `28fb6a324e432547b98f618d7981a4940dc3e5bf9b319b0181b339d3e8bd062b` | SCOPE-CLOSED | CLOSED | N/A | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](display-input/SURVEY.md) |
| MTK-MBOX | DONE | SENSORS/TINYSYS | MT6878 mailbox/IPU doorbell provider under MDDR/mCp/SCP/VCP/GPUEB/MCUPM/SSPM messaging | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](sensors/STATUS.md) |
| MTK-MODULE-LOADER | DONE | BOOT/KERNEL PACKAGING | MediaTek kernel module loader behavior | SCOPE-CLOSED | CLOSED | N/A | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](coverage-audit/SUMMARY.md) |
| MTK-PWM | DONE | DISPLAY/INPUT | MediaTek PWM provider used by rugged lights | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Runtime validation only | [report](display-input/SURVEY.md) |
| MTK-RPMSG-MBOX | DONE | SENSORS/TINYSYS | MediaTek RPMsg mailbox layer | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | None for the kernel scope (runtime traffic not exercised by rule) | [report](sensors/STATUS.md) |
| MTK-TINYSYS-IPI | DONE | SENSORS/TINYSYS | MediaTek tinysys IPI stack | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | None for the kernel scope; per-channel payload semantics belong to client drivers and proprietary SCP/VCP/GPUEB/MCUPM firmware | [report](sensors/STATUS.md) |
| MTU3-SSUSB | DONE | USB/TYPE-C | 11201000.usb0 MTU3 dual-role controller | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Runtime role-transition validation only; proprietary USB/gadget AIDL HAL internals (interface boundary documented) | [report](usb/STATUS.md) |
| NFC-SECURE-ELEMENT | PARTIAL | NFC | Embedded secure-element path behind ST21 | B | CLOSED | PROPRIETARY | SIGNED | PROVEN | ST21 controller kernel is closed; NCI HAL, secure-element applets/access rules and firmware stay proprietary. | [report](nfc/STATUS.md) |
| NVRAM-CALIBRATION | PARTIAL | NVRAM/CALIBRATION | NVRAM partitions, consumers and per-unit calibration boundaries | C | CLOSED (paths) | PROPRIETARY | DEVICE-INTERNAL | PROVEN | Partition/consumer paths are mapped; per-unit values and vendor calibration logic are private/device-specific. | [report](coverage-audit/SUMMARY.md) |
| OEM-KERNEL-MODULES | PARTIAL | BOOT/KERNEL PACKAGING | 471-module GQ5012BF1 OEM set | F | MIXED | N/A | N/A | N/A | Persistent whole-module-set tracker; child components have mixed closure. Its documented 471 count is stale versus the measured 457-module universe. | [report](coverage-audit/SUMMARY.md) |
| OTA-AB-UPDATE | PARTIAL | BOOT/KERNEL PACKAGING | A/B OTA payload, snapshots, merge and rollback | A | N/A | PARTIAL | N/A | RUNTIME | Payload signing, update_engine application, slot switch, snapshot merge and rollback need an end-to-end test. | [report](coverage-audit/SUMMARY.md) |
| PARTITION-OWNERSHIP | DONE | BOOT/KERNEL PACKAGING | Boot/storage/persistent partition ownership map | SCOPE-CLOSED | CLOSED | N/A | SIGNED-BINARY | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](coverage-audit/SUMMARY.md) |
| PD-DBG-INFO | DONE | USB/TYPE-C | MTK PD debug queue provider | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](usb/STATUS.md) |
| PD-PPS-UFCS | DONE | POWER/CHARGING | Pd Pps Ufcs | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](power-charging/README.md) |
| PROGRAMMABLE-KEYS | DONE | DISPLAY/INPUT | Two YFT programmable hardware keys | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](display-input/SURVEY.md) |
| RADIO-HAL-RIL | PARTIAL | MODEM/TELEPHONY | Android radio HAL and proprietary vendor RIL boundary | B | CLOSED (kernel) | PROPRIETARY | SIGNED | PROVEN | Static service/AIDL/device boundary is mapped; vendor RIL implementation is proprietary. | [report](modem/STATUS.md) |
| REAR-RUGGED-FEATURES | PARTIAL | IR/RUGGED | Rear display, lights, programmable keys and rugged services | F | MIXED | MIXED | MIXED | PROVEN | Intentional integration umbrella over rear display/touch, keys, lights and YFT services; children have mixed closure. | [report](coverage-audit/SUMMARY.md) |
| RECOVERY-ORANGEFOX | PARTIAL | BOOT/RECOVERY | OrangeFox recovery device integration and acceptance | A | N/A | PARTIAL | N/A | RUNTIME | Core recovery works, but package flashing, backup/restore matrix, Magisk and USB identity behavior are not fully tested. | [report](coverage-audit/SUMMARY.md) |
| RF-ANTENNAS | BLOCKED | CONNECTIVITY | Board antenna network and nofem ConnFem selection | BLOCKED | N/A | N/A | N/A | TEARDOWN | Requires teardown, schematic/board view, continuity or RF measurements. | [report](connectivity/STATUS.md) |
| RT5133-POWER-IC | DONE | CAMERA | Richtek RT5133/RT5133A declared at I2C 5-0018 by the MT6878 base DTB; no die answers on GQ5012BF1 | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](power/rt5133/STATUS.md) |
| SC8510-BIDIRECTIONAL-CHARGE-PUMP | DONE | POWER/CHARGING | SouthChip SC8510, a 2S↔1S bidirectional switched-capacitor converter (2:1 forward discharge, 1:2 reverse charge) with a load switch | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | integration qualification only | [report](power-charging/README.md) |
| SC8571-CHARGE-PUMP | DONE | POWER/CHARGING | SouthChip SC8571 2S switched-capacitor (2:1) direct charger. Two instances | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | integration qualification only | [report](power-charging/README.md) |
| SENSOR-HUB | PARTIAL | SENSORS/TINYSYS | MTK sensor hub and fusion stack | B | CLOSED (transport) | PROPRIETARY | SIGNED | PROVEN | Linux transport is closed; SCP physical drivers, fusion, batching and calibration are inside signed firmware. | [report](sensors/STATUS.md) |
| SENSOR-HUB-KERNEL | DONE | SENSORS/TINYSYS | SCP sensorhub Linux transport, not sensor register drivers | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](sensors/STATUS.md) |
| SH366003-FUEL-GAUGE | DONE | POWER/CHARGING | Sino Wealth SH366003 2S pack fuel gauge, device type 0x0603, i2c-9 (`/soc/i2c@11c24000`) address 0x55, polled (no IRQ) | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | `sh366003_fg.ko` binary-equivalent: 39/39 functions same size, 38/39 byte-identical; `sh_fg_probe` differs only by a proven register-allocation permutation (11/809 insns, x22↔x25 + two swapped independent adrp… | [report](power-charging/sh366003/STATUS.md) |
| SPI-MT65XX | DONE | KERNEL | MediaTek MT65xx SPI controller | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](coverage-audit/SUMMARY.md) |
| SPL07-BAROMETER | PARTIAL | SENSORS/TINYSYS | Goermicro SPL07-003 barometer | C | CLOSED (transport) | PROPRIETARY | SIGNED (SCP) | PROVEN | Calibration coefficients and register driver live in signed SCP firmware. | [report](sensors/STATUS.md) |
| ST21NFC | DONE | NFC | STMicroelectronics ST21NFC contactless front end (controller-only CLF), I²C6 @ 0x08 | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](nfc/STATUS.md) |
| STK3A5X-ALS-PS | PARTIAL | SENSORS/TINYSYS | Sensortek STK3A5X ALS/proximity | C | CLOSED (transport) | PROPRIETARY | SIGNED (SCP) | PROVEN | Exact sub-variant, calibration and register driver are hidden in signed SCP firmware. | [report](sensors/STATUS.md) |
| SYSTEM-DLKM | DONE | BOOT/KERNEL PACKAGING | System Dlkm | SCOPE-CLOSED | CLOSED | N/A | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](coverage-audit/SUMMARY.md) |
| TCPC-CLASS | DONE | USB/TYPE-C | MediaTek TCPC core 2.0.31_MTK | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification and bounded eight-function byte deltas remain | [report](usb/STATUS.md) |
| TCPC-MT6375 | DONE | USB/TYPE-C | MT6375 TCPC controller | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](usb/STATUS.md) |
| THERMAL-POWER-HAL | PARTIAL | POWER/CHARGING | MTK thermal, health and charging policy stack | B | CLOSED (kernel dependencies) | PROPRIETARY | N/A | PROVEN | Kernel dependencies are mapped; thresholds, policy engines and full runtime parity remain vendor-specific. | [report](power-charging/README.md) |
| THERMAL-RADIOMETRY | PARTIAL | THERMAL CAMERA | ThermoVue calibration/radiometry pipeline | C | N/A | PROPRIETARY | DEVICE-INTERNAL | PROVEN | Radiometry algorithms and per-unit calibration schema are proprietary; temperature parity needs reference measurements. | [report](camera-stack/STATUS.md) |
| THERMOVUE-T2 | PARTIAL | THERMAL CAMERA | ThermoVue T2 / AC020-family thermal assembly | B | CLOSED (USB/power) | PROPRIETARY | BINARY | PROVEN | USB/UVC/power path is closed; command protocol, application, calibration ownership and replacement UI remain. | [report](camera-stack/STATUS.md) |
| TKCORE-DRV | DONE | SECURITY/TEE | `vendor_boot:/lib/modules/tkcore_drv.ko` (sha256 `c13503ba…1235d`), first stage seq 111, depends `tkcore,ffa_v10` | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](tkcore/STATUS.md) |
| TMEM-FFA | DONE | SECURITY/TEE | MediaTek trusted-memory FF-A provider | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](tkcore/STATUS.md) |
| TRUSTKERNEL-ABI-ISLAND | BLOCKED | SECURITY/TEE | TrustKernel proprietary ABI island | BLOCKED | BLOCKED | PROPRIETARY | SIGNED | N/A | Required stock ABI functions are absent from available donor/source; private vendor island is unavailable. | [report](tkcore/STATUS.md) |
| TRUSTKERNEL-TEE | BLOCKED | SECURITY/TEE | TrustKernel TEE used by KeyMint/Gatekeeper/fingerprint | BLOCKED | N/A (TKCORE separate) | PROPRIETARY | SIGNED | N/A | Private TA/helper semantics and authorized secure-world runtime evidence are unavailable. | [report](tkcore/STATUS.md) |
| UFS-RPMB-KERNEL | DONE | STORAGE | per-module SUMMARY, function/data/ABI/relocation TSVs, full-module section proofs | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Runtime validation (negotiated gear/lanes, WriteBooster flush); text of the 69 padded dbg lines (count proven); TEE ownership of RPMB regions 1/2; UFS device firmware internals stay out of scope in `DONE/UFS-S… | [report](storage/STATUS.md) |
| UFS-STORAGE | DONE | STORAGE | UFS storage subsystem — Micron `MT512GBCAV8U31` uMCP (UFS 3.1, FW `0108`, RPMB 16 MiB) | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](storage/ufs/README.md) |
| USB-CHARGER-INTEGRATION | DONE | POWER/CHARGING | Usb Charger Integration | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](power-charging/README.md) |
| USB-PHY | DONE | USB/TYPE-C | MT6878 XS-PHY USB2 child | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | None for the kernel scope (runtime eye-diagram/compliance is out of scope) | [report](usb/STATUS.md) |
| USB-TYPEC | DONE | USB/TYPE-C | MT6375 Type-C/CC controller path | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | rt_pd_manager srcversion (stock source comments/whitespace); runtime role-matrix validation | [report](usb/STATUS.md) |
| USB3-FEASIBILITY | DONE | USB/TYPE-C | Potential MT6878T SuperSpeed capability | SCOPE-CLOSED | N/A | N/A | N/A | PROVEN | None (PCB SS-lane question is moot) | [report](usb/STATUS.md) |
| VENDOR-ALL-MODULES-READY | DONE | BOOT/KERNEL PACKAGING | vendor.all.modules.ready init property lifecycle | SCOPE-CLOSED | N/A | N/A | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](coverage-audit/SUMMARY.md) |
| VENDOR-BLOB-HAL-INVENTORY | PARTIAL | ANDROID INTEGRATION | Retained proprietary HAL/service/library ownership inventory | F | N/A | MIXED/PROPRIETARY | MIXED | N/A | Persistent cross-subsystem inventory of retained proprietary services/libraries and replacement verdicts. | [report](coverage-audit/SUMMARY.md) |
| VENDOR-DLKM | PARTIAL | BOOT/KERNEL PACKAGING | GQ5012BF1 vendor_dlkm module image | F | MIXED | N/A | N/A | N/A | Packaging/whole-image tracker; actual source closure belongs to child driver components. | [report](coverage-audit/SUMMARY.md) |
| VENDOR-PROPERTIES | DONE | ANDROID INTEGRATION | Device-specific vendor property surface and override policy | SCOPE-CLOSED | CLOSED | N/A | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](coverage-audit/SUMMARY.md) |
| VENDOR-SEPOLICY | PARTIAL | ANDROID INTEGRATION | GQ5012BF1 vendor SELinux and property policy | A | N/A | PARTIAL | N/A | N/A | Stock domains/contexts are inventoried; policy reconstruction, neverallow review and runtime denial closure remain. | [report](coverage-audit/SUMMARY.md) |
| VINTF-HAL-MANIFEST | DONE | ANDROID INTEGRATION | Device VINTF manifests, matrices and HAL declaration contract | SCOPE-CLOSED | CLOSED | N/A | N/A | N/A | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](coverage-audit/SUMMARY.md) |
| VTDR6115-DISPLAY | DONE | DISPLAY/INPUT | `panel-ky-vtdr6115-dphy-cmd.ko`, vendor **ramdisk**, 246 288 B, sha256 `1e5778f3612378dd6fc3ba96ca461d8ba0661fc6617290a7c64245ede3f3af07`, build-id `… | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](display-input/vtdr6115/README.md) |
| WIRELESS-CHARGING-ABSENCE | DONE | POWER/CHARGING | No confirmed wireless charging hardware | SCOPE-CLOSED | N/A | N/A | N/A | PROVEN | Named static scope closed; runtime/system integration is outside this DONE scope. | [report](power-charging/README.md) |
| WL2868-CAMERA-LDO | DONE | CAMERA | WL2864C/WL2868 camera LDO | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](camera-stack/STATUS.md) |
| YFT-DEVINFO | PARTIAL | KERNEL | YFT device-information registry | A | PARTIAL | PARTIAL | N/A | PROVEN | One vendor enum spelling still shifts exported CRC/KCFI identities; probe/sysfs path is not byte-exact. | [report](coverage-audit/SUMMARY.md) |
| YFT-TINY2C-USB | DONE | THERMAL CAMERA | YFT tiny2c USB/power controller | SCOPE-CLOSED | CLOSED | N/A | N/A | PROVEN | Only integration qualification remains | [report](camera-stack/STATUS.md) |
| YFT-TPD-GESTURE | DONE | DISPLAY/INPUT | YFT touchscreen gesture provider | SCOPE-CLOSED | CLOSED | PROPRIETARY (outside scope) | N/A | PROVEN | Only integration qualification remains | [report](display-input/SURVEY.md) |

## Subsystem summaries

### 1. Boot / partitions / AVB / OTA

- **Closed:** A/B geometry, AVB topology and slot safety are statically closed.
- **Remains:** Custom-image boot, OTA/snapshot and recovery acceptance remain.
- **Boundary:** OEM signing/rollback state and live update safety cannot be inferred from static files alone.
- **Components:** `AB-SUPER-GEOMETRY`, `AVB-SIGNING-CHAIN`, `BOOT-CONTROL-SLOTS`, `BOOT-IMAGES`, `DTB-DTBO`, `OTA-AB-UPDATE`, `PARTITION-OWNERSHIP`, `RECOVERY-ORANGEFOX`

### 2. Kernel infrastructure

- **Closed:** Loader ordering and GKI/KMI baseline are known.
- **Remains:** Image parity and unresolved child modules remain umbrella work.
- **Boundary:** Tracking scopes must not be mistaken for one source component.
- **Components:** `GKI-KMI-BASELINE`, `INIT-INSMOD`, `MTK-MODULE-LOADER`, `OEM-KERNEL-MODULES`, `SYSTEM-DLKM`, `VENDOR-DLKM`, `VENDOR-ALL-MODULES-READY`

### 3. Power / charging / battery

- **Closed:** Charge pumps, fuel gauge and core providers are mapped/mostly source-closed.
- **Remains:** MT6375 parity, policy/config and live negotiation/thermal behavior remain.
- **Boundary:** Pack identity, cooling stack and high-power safety need physical/runtime evidence.
- **Components:** `BATTERY-PACK`, `COOLING-HARDWARE`, `MT6375-CHARGER`, `PD-DBG-INFO`, `PD-PPS-UFCS`, `RT5133-POWER-IC`, `SC8510-BIDIRECTIONAL-CHARGE-PUMP`, `SC8571-CHARGE-PUMP`, `SH366003-FUEL-GAUGE`, `THERMAL-POWER-HAL`, `USB-CHARGER-INTEGRATION`

### 4. USB / Type-C

- **Closed:** USB2 controller/PHY/extcon/TCPC topology is closed; SuperSpeed absence is proven.
- **Remains:** Runtime role/gadget/charging acceptance remains.
- **Boundary:** USB3 finding should live under USB-TYPEC.
- **Components:** `EXTCON-MTK-USB`, `EXTERNAL-USB`, `MTU3-SSUSB`, `TCPC-CLASS`, `TCPC-MT6375`, `USB-PHY`, `USB-TYPEC`, `USB3-FEASIBILITY`

### 5. Display / touch / LEDs

- **Closed:** Main/rear display, DRM, rear touch, LEDs and haptics have named static closure.
- **Remains:** FT3680 parity and full runtime brightness/touch acceptance remain.
- **Boundary:** Ilitek/Chipone enabled nodes are driverless reference-board baggage.
- **Components:** `AW2013-RGB-LED`, `BACKLIGHT-DISPLAY-GLUE`, `CO5300-REAR-DISPLAY`, `FT3680-TOUCH`, `HAPTICS`, `HYNITRON-REAR-TOUCH`, `MEDIATEK-DRM`, `MTK-DISP-NOTIFY`, `MTK-PWM`, `VTDR6115-DISPLAY`

### 6. Camera

- **Closed:** Sensor/VCM/OIS/EEPROM and power/flash kernel scopes are closed or strongly bounded.
- **Remains:** ISP kernel parity should be split and finished.
- **Boundary:** HAL/3A/tuning/CCU/calibration remain proprietary.
- **Components:** `AW36515-FLASH`, `AW36518-FLASH`, `AW36518-V2-FLASH`, `CAMERA-EEPROMS`, `CAMERA-HAL-ISP`, `CAMERA-IMX989`, `CAMERA-OV64B`, `CAMERA-S5KJN1`, `CAMERA-S5KJN1MAIN2`, `CAMERA-VCMS`, `CUSTOM-LDO`, `DW9781C-OIS`, `WL2868-CAMERA-LDO`

### 7. Thermal camera

- **Closed:** USB/UVC/internal power/companion kernel path is mapped and closed.
- **Remains:** Command protocol and replacement viewer remain.
- **Boundary:** Radiometry algorithms and per-unit calibration are proprietary/device-internal.
- **Components:** `AC020-UVC`, `FM78100-COMPANION`, `INTERNAL-THERMAL-USB`, `THERMAL-RADIOMETRY`, `THERMOVUE-T2`, `YFT-TINY2C-USB`

### 8. Audio

- **Closed:** Codec, AFE, DSP kernel transport and speaker-driver kernel scope are closed.
- **Remains:** Audio HAL routing and microphone runtime integration remain.
- **Boundary:** DSP firmware/algorithms and calibration remain binary.
- **Components:** `AUDIO-DSP`, `AUDIO-DSP-KERNEL`, `AW883XX-SPEAKER-AMP`, `MICROPHONES`, `MT6369-AUDIO-CODEC`, `MT6878-AFE`

### 9. Connectivity

- **Closed:** Conninfra and Wi-Fi/BT/FM Linux sides are closed.
- **Remains:** Live RF/features and HAL integration remain.
- **Boundary:** Controller firmware and radio calibration are proprietary.
- **Components:** `BLUETOOTH`, `CONNFEM`, `CONNINFRA-KERNEL`, `FM-KERNEL`, `FM-RADIO-HEADSET`, `MT6637-BT-KERNEL`, `MT6637-WIFI`, `MT6637-WIFI-KERNEL`

### 10. Modem / telephony / IMS

- **Closed:** The reconstructable Linux modem transport is closed.
- **Remains:** Carrier/runtime RIL and IMS validation remain.
- **Boundary:** MD1 firmware, vendor RIL/IMS and RF calibration are signed/proprietary.
- **Components:** `CCCI-KERNEL`, `CCMNI-KERNEL`, `DPMAIF-KERNEL`, `IMS`, `MODEM-FIRMWARE`, `MODEM-KERNEL-TRANSPORT`, `RADIO-HAL-RIL`

### 11. Sensors / SCP / TinySys

- **Closed:** Mailbox/IPI and sensorhub Linux transport are closed.
- **Remains:** Android sensor behavior/calibration validation remains.
- **Boundary:** Physical sensor register drivers/fusion live in signed SCP firmware; no fake Linux-driver tasks.
- **Components:** `ICM4N607-IMU`, `MMC5603-MAGNETOMETER`, `MTK-MBOX`, `MTK-RPMSG-MBOX`, `MTK-TINYSYS-IPI`, `SENSOR-HUB`, `SENSOR-HUB-KERNEL`, `SPL07-BAROMETER`, `STK3A5X-ALS-PS`

### 12. Storage

- **Closed:** UFS, RPMB and microSD static contracts/kernel stacks are closed.
- **Remains:** Runtime media/gear/OTA interactions remain integration work.
- **Boundary:** Device firmware and secure keys are not reconstructable.
- **Components:** `MICROSD`, `MICROSD-KERNEL`, `UFS-RPMB-KERNEL`, `UFS-STORAGE`

### 13. NFC

- **Closed:** ST21NFC kernel/controller identity is closed.
- **Remains:** NCI/eSE runtime acceptance remains.
- **Boundary:** Secure applets/access-control and controller firmware are proprietary.
- **Components:** `NFC-SECURE-ELEMENT`, `ST21NFC`

### 14. Fingerprint / biometrics

- **Closed:** Platform and normal-world kernel/TEE-client scopes are closed.
- **Remains:** HAL integration and enroll/auth validation remain.
- **Boundary:** Sensor protocol, templates and TA are proprietary; five alternative rc services are dead baggage.
- **Components:** `FINGERPRINT-PLATFORM-SHIM`, `MADEV-FINGERPRINT`, `MICROARRAY-FP-TEE`

### 15. Security / TEE / RPMB

- **Closed:** Normal-world FF-A/GZ/TKCORE/TMEM/RPMB transport is represented and mostly closed.
- **Remains:** FBE/credential runtime and taxonomy consolidation remain.
- **Boundary:** Secure-world payload/TA/private ABI source is blocked.
- **Components:** `FFA-V10`, `GZ-IPC-MOD`, `GZ-MAIN-MOD`, `GZ-TRANSPORT`, `GZ-TRUSTY-MOD`, `GZ-TZ-SYSTEM`, `KEYSTORE-VOLD-KEYMINT`, `TKCORE-DRV`, `TMEM-FFA`, `TRUSTKERNEL-ABI-ISLAND`, `TRUSTKERNEL-TEE`

### 16. GNSS

- **Closed:** Kernel transport and fitted connsys identity are closed.
- **Remains:** L1/L5/runtime validation remains.
- **Boundary:** Firmware and mnld/libmnl engine are proprietary.
- **Components:** `GNSS`, `GNSS-KERNEL-TRANSPORT`

### 17. IR / rugged-device extras

- **Closed:** IR, keys, camp lights and gesture paths are represented; most kernel scopes are closed.
- **Remains:** YFT-DEVINFO residual and end-to-end rugged integration remain.
- **Boundary:** Umbrella should remain a checklist, not duplicate child reconstruction.
- **Components:** `IR-BLASTER`, `LN2403-CAMPLIGHT`, `PROGRAMMABLE-KEYS`, `REAR-RUGGED-FEATURES`, `YFT-DEVINFO`, `YFT-TPD-GESTURE`

### 18. Android HAL / framework integration

- **Closed:** All stock/current integration artifacts are inventoried and owned.
- **Remains:** Generated VINTF/properties/policy/init acceptance remains.
- **Boundary:** 448 significant proprietary libraries require retention or independently demonstrated replacements.
- **Components:** `ANDROID-INIT`, `VENDOR-BLOB-HAL-INVENTORY`, `VENDOR-PROPERTIES`, `VENDOR-SEPOLICY`, `VINTF-HAL-MANIFEST`

### 19. NVRAM / calibration

- **Closed:** Partitions, consumers, hashes and firmware classes are mapped.
- **Remains:** Ownership labels and safe backup/restore validation remain.
- **Boundary:** Per-unit values and vendor algorithms are private/device-internal.
- **Components:** `FIRMWARE-INVENTORY`, `NVRAM-CALIBRATION`

### 20. Other board-specific glue

- **Closed:** SPI glue and negative eSIM/wireless findings are represented.
- **Remains:** DRAM package/training and RF antenna topology remain.
- **Boundary:** These require signed boot firmware, schematics, teardown or RF measurement.
- **Components:** `DRAM-MEMORY`, `ESIM-EUICC-ABSENCE`, `RF-ANTENNAS`, `SPI-MT65XX`, `WIRELESS-CHARGING-ABSENCE`

## Missing components discovered

One: **MALI-GPU-KERNEL**. See [`coverage-audit/MISSING-COVERAGE.md`](coverage-audit/MISSING-COVERAGE.md).

## Duplicate / merge candidates

Four migration records: consolidate four GZ children into GZ-TRANSPORT; AW36518-V2 into AW36518; USB3-FEASIBILITY into USB-TYPEC; VENDOR-ALL-MODULES-READY into INIT-INSMOD.

## Split candidates

One: split actionable **CAMERA-ISP-KERNEL** from proprietary `CAMERA-HAL-ISP`.

## Stale / obsolete component candidates

`ESIM-EUICC-ABSENCE` and `WIRELESS-CHARGING-ABSENCE` should become preserved negative findings rather than canonical components. `USB3-FEASIBILITY` is a resolved-negative merge candidate.

## Components whose status may be wrong

No evidence supports an automatic directory status move. RT5133's DONE static scope remains justified, but its canonical name should reflect the corrected camera-LDO role. OEM/VENDOR module umbrella prose must refresh 471→457 without changing PARTIAL.

## Intentionally persistent PARTIAL scopes

`FIRMWARE-INVENTORY`, `OEM-KERNEL-MODULES`, `REAR-RUGGED-FEATURES`, `SYSTEM-DLKM`, `VENDOR-BLOB-HAL-INVENTORY`, and `VENDOR-DLKM` are class F tracking/integration umbrellas. They should not become DONE merely because children close.

## Generic shipped artifacts not requiring dedicated RE

207 kernel modules, 314 active DT-compatible rows, 188 HAL/service rows and 90 significant-name system libraries are generic/upstream/platform infrastructure. They remain enumerated as C rather than inflating the component count.

## Dead/reference-board artifacts

- 15 modules are dead/debug/reference baggage.
- Enabled Ilitek/Chipone TDDI nodes have no shipped driver; fitted touch is FT3680 + Hynitron.
- Twenty-two non-trigger init declarations point to absent executables, including five alternative fingerprint services and six legacy modem loggers.
- The face example, virtual camera and DOOGEE-named EIS payload are explicit reference/example findings.

## Proposed taxonomy result

If every reviewed ADD/MERGE/SPLIT/REMOVE is accepted, the canonical total becomes **126**. No migration was executed by this audit.

See [`coverage-audit/PROPOSED-CHANGES.md`](coverage-audit/PROPOSED-CHANGES.md) and [`coverage-audit/SUMMARY.md`](coverage-audit/SUMMARY.md).
