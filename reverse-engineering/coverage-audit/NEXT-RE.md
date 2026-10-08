# Final next-RE priority list

Final snapshot: **2026-10-08**, source HEAD `3abc5643e539b3f2c8565d8197091d3bb50856ff`; workspace directories are authoritative. This report is reproducible from committed metadata, not a claim that later concurrent closures never occur.

Ranked by qualitative probability of defensible closure of the entire named **static** scope, not document-writing speed. Effort is an estimate, not a guarantee. No reconstruction is performed by this audit. A matched source donor is not assumed where none is proved.

Only remaining registered PARTIAL static targets and the two proposed kernel scopes appear below. A newly DONE target is automatically omitted. Static DTS contract closure is distinct from module parity; init/policy assembly, boot, SELinux, HAL registration and hardware acceptance are separate integration work.

## 1. DTB-DTBO — PARTIAL

- **Work type:** STATIC SOURCE CONTRACT
- **Scope:** Selected base DTB/DTBO sources, overlay selection and bootloader mutation contract
- **Difficulty / closure outlook:** MEDIUM; Highest: bounded blobs and selection metadata already exist
- **Existing evidence:** Merged/base/overlay DT inventory and exact boot-container/partition ledgers. [Canonical report](../../docs/dt-module-matching.md).
- **Missing source/behavior:** Reproducible source-complete DTS/DTBO build and explicit reconciliation of observed bootloader changes
- **Closure criterion:** All selected blobs rebuild with documented property/phandle/selection equivalence; every observed mutation classified. No unobserved runtime behavior claimed.
- **Expected effort:** Several days to two weeks
- **Dependency:** BOOT-IMAGES; PARTITION-OWNERSHIP; proposed Mali contract for GPU-specific source details
- **Phone necessary:** No for static closure using existing dumps; yes only for new runtime/boot acceptance

## 2. FT3680-TOUCH — PARTIAL

- **Work type:** KERNEL MODULE PARITY
- **Scope:** focaltech_touch_spi_ft3680.ko host driver (not proprietary embedded firmware)
- **Difficulty / closure outlook:** MEDIUM/HARD; Good but uncertain: bounded, buildable 166-function reconstruction
- **Existing evidence:** 166/166 functions; 105/105 import CRCs; 67 raw, 69 normalized and 29 order-only functions. [Canonical report](../display-input/ft3680/parity-report.md).
- **Missing source/behavior:** 40 size-different functions; 68 outside normalized/order-only classes; FHP/FWDBG, flash, IRQ and cleanup residuals
- **Closure criterion:** All function/data/ABI/relocation differences closed against stock, with independently reproducible build and only explicitly proved build-provenance/firmware boundary residuals.
- **Expected effort:** One to several weeks
- **Dependency:** SPI-MT65XX; YFT-TPD-GESTURE; retained firmware metadata
- **Phone necessary:** No for module parity; hardware tests remain a separate acceptance gate

## 3. YFT-DEVINFO — PARTIAL

- **Work type:** KERNEL MODULE PARITY
- **Scope:** yft_devinfo.ko provider, exported registry ABI and probe/sysfs logic
- **Difficulty / closure outlook:** HARD (not a quick enum edit); Moderate: small residual but unknown enum spelling may resist exact closure
- **Existing evidence:** 54/72 byte-identical functions, 61/72 KCFI IDs, 40/40 import CRCs, 17/27 export CRCs; large enum-search exclusions already recorded. [Canonical report](../../kernel/phase4-yft-devinfo-kcfi-typeid.md).
- **Missing source/behavior:** Vendor enum identity affecting ten device_add exports plus probe/sysfs codegen residuals
- **Closure criterion:** 72/72 function behavior/bytes and all data, 27 export CRCs and KCFI identities proven; reproduce from source with explicit provenance residuals only.
- **Expected effort:** Days to weeks; unbounded donor/enum risk
- **Dependency:** Existing registry consumers; source/donor ABI evidence (not more documentation)
- **Phone necessary:** No for static parity; runtime registry validation is separate

## 4. CAMERA-ISP-KERNEL — PROPOSED

- **Work type:** PROPOSED SPLIT / KERNEL MODULE PARITY
- **Scope:** CAMERA-HAL-ISP's ISP7sp/imgsensor framework kernel modules and DT/normal-world ABI only
- **Difficulty / closure outlook:** HARD; Moderate/lower: source coverage exists, but entire ISP set has not been parity-built
- **Existing evidence:** Existing ISP module/source-coverage ledger and imgsensor framework 507/532 byte-identical with one struct delta. [Canonical report](../camera-stack/notes/isp-stack.md).
- **Missing source/behavior:** ISP framework/provider source builds and module-by-module ABI/function/data parity; explicit ownership transfer list
- **Closure criterion:** Enumerated ISP kernel set closes with reproducible parity and DT/platform contract; HAL, 3A, tuning DB and signed CCU remain explicitly outside scope.
- **Expected effort:** Several weeks to months
- **Dependency:** Approved split; existing camera sensor/VCM/OIS/EEPROM children; source donors and exact GKI
- **Phone necessary:** No for static kernel closure; camera runtime/quality validation needs phone later

## 5. MALI-GPU-KERNEL — PROPOSED

- **Work type:** PROPOSED ADD / KERNEL MODULE PARITY
- **Scope:** Active r44 Valhall KMD, MGM/protected allocator, Mali/G3D DT and normal-world GPU platform ABI
- **Difficulty / closure outlook:** HARD / source availability uncertain; Lowest of this list: ownership absent and matched platform source/parity not established
- **Existing evidence:** Three shipped KMD/support modules, three enabled DT compatibles, two GPU HAL families and two init services. [Canonical report](MISSING-COVERAGE.md).
- **Missing source/behavior:** Matched r44/MT6878 KMD and board glue source, builds, ABI and function/data parity; do not assume a source donor exists
- **Closure criterion:** All three active modules and GPU DT/platform ABI reproducibly reconstructed; proprietary userspace/CSF firmware retained and not claimed open.
- **Expected effort:** Several weeks to months; source-access risk
- **Dependency:** Approved ADD; GKI-KMI-BASELINE; TMEM-FFA; retained GPU userspace/CSF firmware
- **Phone necessary:** No for static parity if stock operands/source suffice; required later for graphics/secure-buffer/runtime tests

## Separate ROM integration queue (not ranked RE)

DONE here means named-scope static closure, not a finished LieppOS feature.

| Component | Current status | Remaining ROM/acceptance action |
|---|---|---|
| SYSTEM-DLKM | DONE | Use the 60/60 reproducible GKI module ELF-body baseline; match custom GKI/KMI, signing, packaging and load order. A stock rebuild does not prove a custom kernel boots. |
| BOOT-IMAGES | DONE | Use the exact recorded container geometry; test custom boot separately. Slot B is the stock-integrity anchor, not a disposable development slot. |
| VENDOR-PROPERTIES | DONE | Preserve externally applied device commit 24afa6b: 327 vendor keys, 16 documented exclusions and one EGL rewrite from the original 343-key missing ledger. Verify generated/inherited definitions, emitted-image precedence, SELinux and runtime; do not reinstall blindly. No integration change made by audit. |
| VINTF-HAL-MANIFEST | DONE | Preserve externally applied bluetooth_audio.xml inclusion (not EXTRACT_ONLY) and vendor prebuilt module. The refreshed ledger is 146 present/48 SKU-only/5 source-built/0 dropped. Assemble/check VINTF and validate actual HAL registration under enforcing SELinux. |
| PARTITION-OWNERSHIP | DONE | Use the 61-group consumer and rollback-location ledger for FBE/OTA/recovery integration; do not overwrite private calibration or bootloader-owned metadata. |
| USB-CHARGER-INTEGRATION | DONE | Kernel parity is closed; validate USB/PD/reverse-power arbitration and safety using suitable hardware, without inferring 120 W acceptance from filenames. |
| INTERNAL-THERMAL-USB | DONE | Integrate UVC/command/viewer paths; validate power/suspend and thermal-camera behavior separately from the closed USB/power kernel contract. |
| ANDROID-INIT | PARTIAL | Finish the static service/property graph and assembly, then test real boot ordering; this is integration-contract closure, not module parity. |
| VENDOR-SEPOLICY | PARTIAL | Reconstruct/build device policy and contexts, review neverallows, then resolve enforcing runtime denials; static compilation alone is not daily-driver validation. |
| OTA-AB-UPDATE | PARTIAL | End-to-end signing/snapshot/merge/rollback acceptance is runtime-gated, not a static PARTIAL-to-DONE shortcut. |
| RECOVERY-ORANGEFOX | PARTIAL | Backup/restore/flashing/FBE/USB acceptance remains runtime-gated; do not put the stock anchor at risk. |

## Proprietary or runtime-only boundaries

`AUDIO-DSP`, `BATTERY-PACK`, `BLUETOOTH`, `COOLING-HARDWARE`, `DRAM-MEMORY`, `FM-RADIO-HEADSET`, `GNSS`, `ICM4N607-IMU`, `IMS`, `KEYSTORE-VOLD-KEYMINT`, `MICROPHONES`, `MMC5603-MAGNETOMETER`, `MODEM-FIRMWARE`, `MT6637-WIFI`, `NFC-SECURE-ELEMENT`, `NVRAM-CALIBRATION`, `OTA-AB-UPDATE`, `RADIO-HAL-RIL`, `RECOVERY-ORANGEFOX`, `SENSOR-HUB`, `SPL07-BAROMETER`, `STK3A5X-ALS-PS`, `THERMAL-POWER-HAL`, `THERMAL-RADIOMETRY`, `THERMOVUE-T2`

Do not convert these into kernel-module parity targets or claim whole-scope closure by updating documentation.

## Umbrella/tracking scopes

`FIRMWARE-INVENTORY`, `OEM-KERNEL-MODULES`, `REAR-RUGGED-FEATURES`, `VENDOR-BLOB-HAL-INVENTORY`, `VENDOR-DLKM`

Do not convert these into kernel-module parity targets or claim whole-scope closure by updating documentation.
