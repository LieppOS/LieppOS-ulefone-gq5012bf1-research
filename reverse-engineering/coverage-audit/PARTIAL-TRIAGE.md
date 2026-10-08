# PARTIAL triage

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

The canonical ledger contains **37** PARTIAL records with one A–F class; the organized
workspace has **36** PARTIAL directories after camera promotion. Mali's pre-existing
canonical-PARTIAL/workspace-DONE discrepancy is not repaired here. The camera kernel
child is now statically DONE; HAL/3A/firmware algorithms remain C. Existing static DONE
scopes stay DONE.

| Component | Class | Remaining boundary | Next action | Difficulty | Dependencies |
|---|---|---|---|---|---|
| ANDROID-INIT | A | Reconcile stock/current service ordering and validate property-trigger behavior. | KEEP PARTIAL; Diff generated service graph against LieppOS init and test one boot. | MEDIUM | BOOT-IMAGES, VENDOR-PROPERTIES, VENDOR-SEPOLICY |
| AUDIO-DSP | B | Kernel AFE/DSP transport is closed; DSP protocol, firmware, routing and calibration remain proprietary. | KEEP PARTIAL; Map HAL-to-DSP messages and preserve stock firmware/calibration. | HARD | AUDIO-DSP-KERNEL, MT6878-AFE, MT6369-AUDIO-CODEC |
| BATTERY-PACK | D | Cell/BMS identity, connector topology, calibration and ageing model need teardown/runtime evidence. | KEEP PARTIAL; Photograph labels/connectors and capture read-only gauge/health data. | HARD | SH366003-FUEL-GAUGE, MT6375-CHARGER |
| BLUETOOTH | B | Kernel transport is closed; controller firmware, vendor HAL internals and LE Audio behavior remain proprietary/runtime-gated. | KEEP PARTIAL; Retain signed firmware; run HCI/LE Audio feature validation. | HARD | MT6637-BT-KERNEL, CONNINFRA-KERNEL |
| CAMERA-HAL-ISP | C | HAL/3A/tuning/calibration interpretation and firmware algorithms remain proprietary; normal-world kernel ownership transferred to child. | KEEP PARTIAL proprietary HAL/3A scope; authorized kernel split APPLIED to CAMERA-ISP-KERNEL | PROPRIETARY-GATED | CAMERA-ISP-KERNEL; camera sensor/VCM/EEPROM/OIS/rail DONE scopes |
| COOLING-HARDWARE | D | Material stack, heat spreaders, contact paths and measured thermal model require physical inspection. | KEEP PARTIAL; Teardown and correlate sustained-load temperatures with thermal zones. | HARD | THERMAL-POWER-HAL, BATTERY-PACK |
| DRAM-MEMORY | D | Exact package/topology/timings and training firmware cannot be recovered from normal Android artifacts alone. | KEEP PARTIAL; Read package markings or schematics; retain signed preloader/training data. | HARD | BOOT-IMAGES, PARTITION-OWNERSHIP |
| DTB-DTBO | A | Effective tree is inventoried; source-complete DTS and bootloader mutation/runtime validation remain. | KEEP PARTIAL; Decompile/normalize each selected DTB/DTBO and reconcile the three Mali nodes after GPU ownership is added. | MEDIUM | BOOT-IMAGES, PARTITION-OWNERSHIP |
| FIRMWARE-INVENTORY | F | Persistent cross-subsystem inventory; payload ownership changes whenever stock/vendor extraction changes. | KEEP PARTIAL; Regenerate metadata hashes on each stock drop; do not attempt source parity for signed payloads. | QUICK | all firmware-owning components |
| FM-RADIO-HEADSET | B | Kernel/headset path is closed; FM app/JNI/patch, LNA/antenna identity and RF performance remain. | KEEP PARTIAL; Read-only runtime FM validation and teardown-only LNA/antenna confirmation. | HARD | FM-KERNEL, FM78100-COMPANION, MT6369-AUDIO-CODEC |
| FT3680-TOUCH | A | Core contract is recovered, but 40 functions remain size-different and 68 remain outside normalized parity classes. | KEEP PARTIAL; Continue static parity on FHP/FWDBG/flash/IRQ residuals without modifying live firmware. | MEDIUM | SPI-MT65XX, YFT-TPD-GESTURE |
| GNSS | B | Kernel transport is closed; connsys GNSS firmware, mnld/libmnl and live L1/L5 behavior remain proprietary/runtime-gated. | KEEP PARTIAL; Retain signed image and capture read-only constellation/L5 behavior. | HARD | GNSS-KERNEL-TRANSPORT, CONNINFRA-KERNEL |
| ICM4N607-IMU | C | The physical sensor driver lives inside signed SCP firmware; exact register protocol and calibration are unavailable. | KEEP PARTIAL; Do not invent a Linux I2C driver; validate Android sensor outputs and preserve SCP firmware. | PROPRIETARY-GATED | SENSOR-HUB, SENSOR-HUB-KERNEL |
| IMS | C | VoLTE/VoWiFi/RCS/video-telephony implementation is a proprietary modem/RIL/IMS island. | KEEP PARTIAL; Map service/property contracts and validate carrier behavior using retained vendor blobs. | PROPRIETARY-GATED | RADIO-HAL-RIL, MODEM-FIRMWARE |
| KEYSTORE-VOLD-KEYMINT | B | Normal-world FBE/RPMB/KeyMint integration is mapped; TA semantics, keys and provisioning remain proprietary. | KEEP PARTIAL; Validate FBE, credential unlock and OTA key continuity on the target ROM. | HARD | TKCORE-DRV, UFS-RPMB-KERNEL, TRUSTKERNEL-TEE |
| MALI-GPU-KERNEL | A | Complete every owned module on function/data/CRC/KCFI/relocation/ABI/B1-B2 axes; no new parity measured by preparation. | KEEP PARTIAL; Follow canonical accelerator CLAUDE-HANDOFF; preserve already exact source/proofs. | HIGH | GKI-KMI-BASELINE; TMEM-FFA; GZ-TRANSPORT; MTK-TINYSYS-IPI; GPUEB client ABI |
| MICROPHONES | D | Package/acoustic-port confirmation plus enforcing-SELinux and full Audio HAL tests remain. | KEEP PARTIAL; Teardown/board-view inspection, then end-to-end recording/call tests. | HARD | MT6369-AUDIO-CODEC, MT6878-AFE, AUDIO-DSP |
| MMC5603-MAGNETOMETER | C | Register driver and fusion/calibration are inside signed SCP firmware. | KEEP PARTIAL; Validate Android heading/calibration; preserve SCP firmware. | PROPRIETARY-GATED | SENSOR-HUB, SENSOR-HUB-KERNEL |
| MODEM-FIRMWARE | C | MD1 code, carrier configuration, RF calibration and signing keys are proprietary. | KEEP PARTIAL; Hash/retain stock images and map version/band metadata without payload redistribution. | PROPRIETARY-GATED | MODEM-KERNEL-TRANSPORT, RADIO-HAL-RIL |
| MT6637-WIFI | B | Kernel path is closed; controller firmware, NVRAM/calibration and vendor HAL internals remain proprietary. | KEEP PARTIAL; Preserve firmware/NVRAM and validate bands, 6E, roaming and suspend. | HARD | MT6637-WIFI-KERNEL, CONNINFRA-KERNEL, CONNFEM |
| NFC-SECURE-ELEMENT | B | ST21 controller kernel is closed; NCI HAL, secure-element applets/access rules and firmware stay proprietary. | KEEP PARTIAL; Validate NCI/eSE flows with retained blobs; do not claim applet source closure. | PROPRIETARY-GATED | ST21NFC, TRUSTKERNEL-TEE |
| NVRAM-CALIBRATION | C | Partition/consumer paths are mapped; per-unit values and vendor calibration logic are private/device-specific. | KEEP PARTIAL; Complete ownership labels and back up values; never publish or synthesize per-unit calibration. | PROPRIETARY-GATED | PARTITION-OWNERSHIP and all calibrated subsystems |
| OEM-KERNEL-MODULES | F | Persistent whole-module-set tracker; child components have mixed closure. Its documented 471 count is stale versus the measured 457-module universe. | KEEP PARTIAL; Regenerate inventory from kernel-modules.tsv and keep only unresolved children actionable. | QUICK | VENDOR-DLKM, SYSTEM-DLKM, MTK-MODULE-LOADER |
| OTA-AB-UPDATE | D | Payload signing, update_engine application, slot switch, snapshot merge and rollback need an end-to-end test. | KEEP PARTIAL; Build one signed test payload and validate entirely on the development slot. | MEDIUM | BOOT-CONTROL-SLOTS, AB-SUPER-GEOMETRY, AVB-SIGNING-CHAIN |
| RADIO-HAL-RIL | B | Static service/AIDL/device boundary is mapped; vendor RIL implementation is proprietary. | KEEP PARTIAL; Preserve vendor RIL and validate calls/data/SMS/SIM/e911/carrier properties. | PROPRIETARY-GATED | MODEM-KERNEL-TRANSPORT, MODEM-FIRMWARE, IMS |
| REAR-RUGGED-FEATURES | F | Intentional integration umbrella over rear display/touch, keys, lights and YFT services; children have mixed closure. | KEEP PARTIAL; Keep as an integration checklist, not as a duplicate source-reconstruction target. | QUICK | CO5300-REAR-DISPLAY, HYNITRON-REAR-TOUCH, PROGRAMMABLE-KEYS, LN2403-CAMPLIGHT |
| RECOVERY-ORANGEFOX | D | Core recovery works, but package flashing, backup/restore matrix, Magisk and USB identity behavior are not fully tested. | KEEP PARTIAL; Run a non-destructive recovery acceptance matrix on Slot B. | MEDIUM | BOOT-IMAGES, OTA-AB-UPDATE, MICROSD |
| SENSOR-HUB | B | Linux transport is closed; SCP physical drivers, fusion, batching and calibration are inside signed firmware. | KEEP PARTIAL; Preserve SCP image and validate Android sensor semantics; do not create fake Linux drivers. | PROPRIETARY-GATED | SENSOR-HUB-KERNEL, MTK-TINYSYS-IPI, physical sensor scopes |
| SPL07-BAROMETER | C | Calibration coefficients and register driver live in signed SCP firmware. | KEEP PARTIAL; Validate pressure/altitude output and preserve SCP firmware. | PROPRIETARY-GATED | SENSOR-HUB, SENSOR-HUB-KERNEL |
| STK3A5X-ALS-PS | C | Exact sub-variant, calibration and register driver are hidden in signed SCP firmware. | KEEP PARTIAL; Use runtime sensor behavior/physical markings only; preserve SCP firmware. | PROPRIETARY-GATED | SENSOR-HUB, SENSOR-HUB-KERNEL |
| THERMAL-POWER-HAL | B | Kernel dependencies are mapped; thresholds, policy engines and full runtime parity remain vendor-specific. | KEEP PARTIAL; Extract all thermal/power configs and validate throttling/idle/charging states. | HARD | COOLING-HARDWARE, MT6375-CHARGER, SH366003-FUEL-GAUGE |
| THERMAL-RADIOMETRY | C | Radiometry algorithms and per-unit calibration schema are proprietary; temperature parity needs reference measurements. | KEEP PARTIAL; Map calibration schema and compare against stock/reference targets without publishing per-unit data. | PROPRIETARY-GATED | THERMOVUE-T2, AC020-UVC |
| THERMOVUE-T2 | B | USB/UVC/power path is closed; command protocol, application, calibration ownership and replacement UI remain. | KEEP PARTIAL; Finish read-only command protocol map and integrate a replacement viewer around UVC. | HARD | AC020-UVC, INTERNAL-THERMAL-USB, YFT-TINY2C-USB, THERMAL-RADIOMETRY |
| VENDOR-BLOB-HAL-INVENTORY | F | Persistent cross-subsystem inventory of retained proprietary services/libraries and replacement verdicts. | KEEP PARTIAL; Regenerate from the stock extraction and close ownership, not source parity, for every blob. | QUICK | VINTF-HAL-MANIFEST, FIRMWARE-INVENTORY |
| VENDOR-DLKM | F | Packaging/whole-image tracker; actual source closure belongs to child driver components. | KEEP PARTIAL; Rebuild image deterministically and reconcile against the 457-module audit universe. | MEDIUM | OEM-KERNEL-MODULES, MTK-MODULE-LOADER |
| VENDOR-SEPOLICY | A | Stock domains/contexts are inventoried; policy reconstruction, neverallow review and runtime denial closure remain. | KEEP PARTIAL; Map every device-specific daemon to domain/devices, build policy, then triage enforcing denials. | MEDIUM | VINTF-HAL-MANIFEST, ANDROID-INIT |
| YFT-DEVINFO | A | One vendor enum spelling still shifts exported CRC/KCFI identities; probe/sysfs path is not byte-exact. | KEEP PARTIAL; Finish the remaining enum/probe parity without disturbing the active owner workspace. | HARD | ANDROID-INIT, VENDOR-PROPERTIES |

## Classification totals

| Classification | Count |
|---|---:|
| A — Actionable static RE; runtime acceptance separate | 11 |
| B — Closed kernel/source boundary; proprietary integration remains | 11 |
| C — Proprietary boundary | 9 |
| D — Hardware/runtime/teardown gated | 6 |
| E — Stale/duplicate/wrong scope | 0 |
| F — Umbrella/tracking scope | 5 |
| **Total PARTIAL** | **42** |

## Ranked static targets

1. **MALI-GPU-KERNEL** — REGISTERED ACCELERATOR / MODULE PARITY; [handoff/evidence](../accelerator-preparation/MALI-GPU-KERNEL/CLAUDE-HANDOFF.md).
3. **CAMERA-ISP-KERNEL** — REGISTERED ACCELERATOR / MODULE PARITY; [handoff/evidence](../accelerator-preparation/CAMERA-ISP-KERNEL/CLAUDE-HANDOFF.md).
7. **DTB-DTBO** — STATIC SOURCE CONTRACT; [handoff/evidence](../../docs/dt-module-matching.md).
8. **FT3680-TOUCH** — KERNEL MODULE PARITY; [handoff/evidence](../display-input/ft3680/parity-report.md).
9. **YFT-DEVINFO** — KERNEL MODULE PARITY; [handoff/evidence](../../kernel/phase4-yft-devinfo-kcfi-typeid.md).
