# PARTIAL triage

Audit date: 2026-10-07

Every current PARTIAL is classified. Class E is intentionally zero: taxonomy cleanup candidates currently live in DONE and are reported separately; no PARTIAL was silently treated as stale.

| Component | Class | What remains | Can static RE close it? | Best next action | Difficulty | Dependencies |
|---|:---:|---|---|---|---|---|
| ANDROID-INIT | A | Reconcile stock/current service ordering and validate property-trigger behavior. | Yes | Diff generated service graph against LieppOS init and test one boot. | MEDIUM | BOOT-IMAGES, VENDOR-PROPERTIES, VENDOR-SEPOLICY |
| AUDIO-DSP | B | Kernel AFE/DSP transport is closed; DSP protocol, firmware, routing and calibration remain proprietary. | Kernel yes; whole scope no | Map HAL-to-DSP messages and preserve stock firmware/calibration. | HARD | AUDIO-DSP-KERNEL, MT6878-AFE, MT6369-AUDIO-CODEC |
| BATTERY-PACK | D | Cell/BMS identity, connector topology, calibration and ageing model need teardown/runtime evidence. | No, needs runtime/physical evidence | Photograph labels/connectors and capture read-only gauge/health data. | HARD | SH366003-FUEL-GAUGE, MT6375-CHARGER |
| BLUETOOTH | B | Kernel transport is closed; controller firmware, vendor HAL internals and LE Audio behavior remain proprietary/runtime-gated. | Kernel yes; whole scope no | Retain signed firmware; run HCI/LE Audio feature validation. | HARD | MT6637-BT-KERNEL, CONNINFRA-KERNEL |
| CAMERA-HAL-ISP | B | Sensor-side kernel work is closed, but ISP kernel parity remains mixed and HAL/3A/tuning/CCU are proprietary. | Kernel yes; whole scope no | SPLIT actionable CAMERA-ISP-KERNEL from proprietary HAL/3A scope | HARD | CAMERA-* sensors, CAMERA-VCMS, CAMERA-EEPROMS, DW9781C-OIS |
| COOLING-HARDWARE | D | Material stack, heat spreaders, contact paths and measured thermal model require physical inspection. | No, needs runtime/physical evidence | Teardown and correlate sustained-load temperatures with thermal zones. | HARD | THERMAL-POWER-HAL, BATTERY-PACK |
| DRAM-MEMORY | D | Exact package/topology/timings and training firmware cannot be recovered from normal Android artifacts alone. | No, needs runtime/physical evidence | Read package markings or schematics; retain signed preloader/training data. | HARD | BOOT-IMAGES, PARTITION-OWNERSHIP |
| DTB-DTBO | A | Effective tree is inventoried; source-complete DTS and bootloader mutation/runtime validation remain. | Yes | Decompile/normalize each selected DTB/DTBO and reconcile the three Mali nodes after GPU ownership is added. | MEDIUM | BOOT-IMAGES, PARTITION-OWNERSHIP |
| FIRMWARE-INVENTORY | F | Persistent cross-subsystem inventory; payload ownership changes whenever stock/vendor extraction changes. | Not as one umbrella | Regenerate metadata hashes on each stock drop; do not attempt source parity for signed payloads. | QUICK | all firmware-owning components |
| FM-RADIO-HEADSET | B | Kernel/headset path is closed; FM app/JNI/patch, LNA/antenna identity and RF performance remain. | Kernel yes; whole scope no | Read-only runtime FM validation and teardown-only LNA/antenna confirmation. | HARD | FM-KERNEL, FM78100-COMPANION, MT6369-AUDIO-CODEC |
| FT3680-TOUCH | A | Core contract is recovered, but 40 functions remain size-different and 68 remain outside normalized parity classes. | Yes | Continue static parity on FHP/FWDBG/flash/IRQ residuals without modifying live firmware. | MEDIUM | SPI-MT65XX, YFT-TPD-GESTURE |
| GNSS | B | Kernel transport is closed; connsys GNSS firmware, mnld/libmnl and live L1/L5 behavior remain proprietary/runtime-gated. | Kernel yes; whole scope no | Retain signed image and capture read-only constellation/L5 behavior. | HARD | GNSS-KERNEL-TRANSPORT, CONNINFRA-KERNEL |
| ICM4N607-IMU | C | The physical sensor driver lives inside signed SCP firmware; exact register protocol and calibration are unavailable. | No | Do not invent a Linux I2C driver; validate Android sensor outputs and preserve SCP firmware. | PROPRIETARY-GATED | SENSOR-HUB, SENSOR-HUB-KERNEL |
| IMS | C | VoLTE/VoWiFi/RCS/video-telephony implementation is a proprietary modem/RIL/IMS island. | No | Map service/property contracts and validate carrier behavior using retained vendor blobs. | PROPRIETARY-GATED | RADIO-HAL-RIL, MODEM-FIRMWARE |
| KEYSTORE-VOLD-KEYMINT | B | Normal-world FBE/RPMB/KeyMint integration is mapped; TA semantics, keys and provisioning remain proprietary. | Kernel yes; whole scope no | Validate FBE, credential unlock and OTA key continuity on the target ROM. | HARD | TKCORE-DRV, UFS-RPMB-KERNEL, TRUSTKERNEL-TEE |
| MICROPHONES | D | Package/acoustic-port confirmation plus enforcing-SELinux and full Audio HAL tests remain. | No, needs runtime/physical evidence | Teardown/board-view inspection, then end-to-end recording/call tests. | HARD | MT6369-AUDIO-CODEC, MT6878-AFE, AUDIO-DSP |
| MMC5603-MAGNETOMETER | C | Register driver and fusion/calibration are inside signed SCP firmware. | No | Validate Android heading/calibration; preserve SCP firmware. | PROPRIETARY-GATED | SENSOR-HUB, SENSOR-HUB-KERNEL |
| MODEM-FIRMWARE | C | MD1 code, carrier configuration, RF calibration and signing keys are proprietary. | No | Hash/retain stock images and map version/band metadata without payload redistribution. | PROPRIETARY-GATED | MODEM-KERNEL-TRANSPORT, RADIO-HAL-RIL |
| MT6637-WIFI | B | Kernel path is closed; controller firmware, NVRAM/calibration and vendor HAL internals remain proprietary. | Kernel yes; whole scope no | Preserve firmware/NVRAM and validate bands, 6E, roaming and suspend. | HARD | MT6637-WIFI-KERNEL, CONNINFRA-KERNEL, CONNFEM |
| NFC-SECURE-ELEMENT | B | ST21 controller kernel is closed; NCI HAL, secure-element applets/access rules and firmware stay proprietary. | Kernel yes; whole scope no | Validate NCI/eSE flows with retained blobs; do not claim applet source closure. | PROPRIETARY-GATED | ST21NFC, TRUSTKERNEL-TEE |
| NVRAM-CALIBRATION | C | Partition/consumer paths are mapped; per-unit values and vendor calibration logic are private/device-specific. | No | Complete ownership labels and back up values; never publish or synthesize per-unit calibration. | PROPRIETARY-GATED | PARTITION-OWNERSHIP and all calibrated subsystems |
| OEM-KERNEL-MODULES | F | Persistent whole-module-set tracker; child components have mixed closure. Its documented 471 count is stale versus the measured 457-module universe. | Not as one umbrella | Regenerate inventory from kernel-modules.tsv and keep only unresolved children actionable. | QUICK | VENDOR-DLKM, SYSTEM-DLKM, MTK-MODULE-LOADER |
| OTA-AB-UPDATE | A | Payload signing, update_engine application, slot switch, snapshot merge and rollback need an end-to-end test. | Yes | Build one signed test payload and validate entirely on the development slot. | MEDIUM | BOOT-CONTROL-SLOTS, AB-SUPER-GEOMETRY, AVB-SIGNING-CHAIN |
| RADIO-HAL-RIL | B | Static service/AIDL/device boundary is mapped; vendor RIL implementation is proprietary. | Kernel yes; whole scope no | Preserve vendor RIL and validate calls/data/SMS/SIM/e911/carrier properties. | PROPRIETARY-GATED | MODEM-KERNEL-TRANSPORT, MODEM-FIRMWARE, IMS |
| REAR-RUGGED-FEATURES | F | Intentional integration umbrella over rear display/touch, keys, lights and YFT services; children have mixed closure. | Not as one umbrella | Keep as an integration checklist, not as a duplicate source-reconstruction target. | QUICK | CO5300-REAR-DISPLAY, HYNITRON-REAR-TOUCH, PROGRAMMABLE-KEYS, LN2403-CAMPLIGHT |
| RECOVERY-ORANGEFOX | A | Core recovery works, but package flashing, backup/restore matrix, Magisk and USB identity behavior are not fully tested. | Yes | Run a non-destructive recovery acceptance matrix on Slot B. | MEDIUM | BOOT-IMAGES, OTA-AB-UPDATE, MICROSD |
| SENSOR-HUB | B | Linux transport is closed; SCP physical drivers, fusion, batching and calibration are inside signed firmware. | Kernel yes; whole scope no | Preserve SCP image and validate Android sensor semantics; do not create fake Linux drivers. | PROPRIETARY-GATED | SENSOR-HUB-KERNEL, MTK-TINYSYS-IPI, physical sensor scopes |
| SPL07-BAROMETER | C | Calibration coefficients and register driver live in signed SCP firmware. | No | Validate pressure/altitude output and preserve SCP firmware. | PROPRIETARY-GATED | SENSOR-HUB, SENSOR-HUB-KERNEL |
| STK3A5X-ALS-PS | C | Exact sub-variant, calibration and register driver are hidden in signed SCP firmware. | No | Use runtime sensor behavior/physical markings only; preserve SCP firmware. | PROPRIETARY-GATED | SENSOR-HUB, SENSOR-HUB-KERNEL |
| THERMAL-POWER-HAL | B | Kernel dependencies are mapped; thresholds, policy engines and full runtime parity remain vendor-specific. | Kernel yes; whole scope no | Extract all thermal/power configs and validate throttling/idle/charging states. | HARD | COOLING-HARDWARE, MT6375-CHARGER, SH366003-FUEL-GAUGE |
| THERMAL-RADIOMETRY | C | Radiometry algorithms and per-unit calibration schema are proprietary; temperature parity needs reference measurements. | No | Map calibration schema and compare against stock/reference targets without publishing per-unit data. | PROPRIETARY-GATED | THERMOVUE-T2, AC020-UVC |
| THERMOVUE-T2 | B | USB/UVC/power path is closed; command protocol, application, calibration ownership and replacement UI remain. | Kernel yes; whole scope no | Finish read-only command protocol map and integrate a replacement viewer around UVC. | HARD | AC020-UVC, INTERNAL-THERMAL-USB, YFT-TINY2C-USB, THERMAL-RADIOMETRY |
| VENDOR-BLOB-HAL-INVENTORY | F | Persistent cross-subsystem inventory of retained proprietary services/libraries and replacement verdicts. | Not as one umbrella | Regenerate from the stock extraction and close ownership, not source parity, for every blob. | QUICK | VINTF-HAL-MANIFEST, FIRMWARE-INVENTORY |
| VENDOR-DLKM | F | Packaging/whole-image tracker; actual source closure belongs to child driver components. | Not as one umbrella | Rebuild image deterministically and reconcile against the 457-module audit universe. | MEDIUM | OEM-KERNEL-MODULES, MTK-MODULE-LOADER |
| VENDOR-SEPOLICY | A | Stock domains/contexts are inventoried; policy reconstruction, neverallow review and runtime denial closure remain. | Yes | Map every device-specific daemon to domain/devices, build policy, then triage enforcing denials. | MEDIUM | VINTF-HAL-MANIFEST, ANDROID-INIT |
| YFT-DEVINFO | A | One vendor enum spelling still shifts exported CRC/KCFI identities; probe/sysfs path is not byte-exact. | Yes | Finish the remaining enum/probe parity without disturbing the active owner workspace. | QUICK | ANDROID-INIT, VENDOR-PROPERTIES |

## Classification totals

| Classification | Count |
|---|---:|
| A — Actionable / statically closeable | 7 |
| B — Kernel/source closed; broader proprietary scope remains | 12 |
| C — Proprietary boundary | 8 |
| D — Hardware/runtime/teardown gated | 4 |
| E — Stale/duplicate/wrong scope | 0 |
| F — Broad umbrella/tracking scope | 5 |

## Ranked next targets

1. **YFT-DEVINFO** — Quick static parity: one enum spelling plus probe/sysfs residual.
2. **VINTF-HAL-MANIFEST** — Generate final manifests/matrices and run VINTF checks.
3. **VENDOR-PROPERTIES** — Generate the property allowlist and validate contamination controls.
4. **FT3680-TOUCH** — Continue the bounded 40/68-function static residual.
5. **MT6375-CHARGER** — Close source/provider parity before runtime charging tests.
6. **DTB-DTBO** — Finish source-complete DTS and bootloader-mutation reconciliation.
7. **BOOT-IMAGES** — Produce exact-geometry custom images and validate Slot B boot.
8. **CAMERA-ISP-KERNEL (proposed split)** — Isolate actionable ISP kernel parity from proprietary HAL/3A.
9. **MALI-GPU-KERNEL (proposed add)** — Own the active Valhall KMD, MGM/protected allocator and three DT compatibles.
10. **VENDOR-SEPOLICY** — Build the device policy and close enforcing-runtime denials.

## Work tiers

### QUICK

`FIRMWARE-INVENTORY`, `OEM-KERNEL-MODULES`, `REAR-RUGGED-FEATURES`, `VENDOR-BLOB-HAL-INVENTORY`, `YFT-DEVINFO`

### MEDIUM

`ANDROID-INIT`, `DTB-DTBO`, `FT3680-TOUCH`, `OTA-AB-UPDATE`, `RECOVERY-ORANGEFOX`, `VENDOR-DLKM`, `VENDOR-SEPOLICY`

### HARD

`AUDIO-DSP`, `BATTERY-PACK`, `BLUETOOTH`, `CAMERA-HAL-ISP`, `COOLING-HARDWARE`, `DRAM-MEMORY`, `FM-RADIO-HEADSET`, `GNSS`, `KEYSTORE-VOLD-KEYMINT`, `MICROPHONES`, `MT6637-WIFI`, `THERMAL-POWER-HAL`, `THERMOVUE-T2`

### PROPRIETARY GATED

`ICM4N607-IMU`, `IMS`, `MMC5603-MAGNETOMETER`, `MODEM-FIRMWARE`, `NFC-SECURE-ELEMENT`, `NVRAM-CALIBRATION`, `RADIO-HAL-RIL`, `SENSOR-HUB`, `SPL07-BAROMETER`, `STK3A5X-ALS-PS`, `THERMAL-RADIOMETRY`

### PHYSICAL/RUNTIME GATED

None.

Physical/runtime gates take precedence over any static subtask for: `BATTERY-PACK`, `COOLING-HARDWARE`, `DRAM-MEMORY`, `MICROPHONES`.
