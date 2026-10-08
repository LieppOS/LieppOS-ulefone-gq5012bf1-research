# Next-RE handoff priorities

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

Accelerator priority follows the authorized dependency-aware roadmap, not unsupported
closure-probability or hour estimates. CAMERA-ISP-KERNEL is now DONE. Mali's remaining
section reflects pre-existing canonical drift: its organized workspace is already DONE,
so that section must not be executed as a new reconstruction task.

## 1. MALI-GPU-KERNEL — PARTIAL

- **kind:** REGISTERED ACCELERATOR / MODULE PARITY
- **scope:** mali_kbase_mt6878_r44.ko, mali_mgm_mt6878_r44.ko, mali_prot_alloc_mt6878_r44.ko, ged.ko, mtk_gpu_hal.ko, mtk_gpu_qos.ko, mtk_gpufreq_wrapper.ko, mtk_gpufreq_mt6878.ko; normal-world kernel/DT/ABI only
- **difficulty:** HIGH
- **probability:** Pinned source candidates and exact stock operands; whole-scope closure probability unmeasured
- **evidence:** Exact module hashes, full ELF metadata, DT/providers, pinned donor files and existing proof-axis citations
- **missing:** All-axes module acceptance; preserve existing camera function/data proofs and close unmeasured residuals
- **closure:** Every explicitly owned module satisfies function/data/CRC/KCFI/relocation/symbol/string/modinfo/vermagic/B1-B2 and observable DT/ABI; algorithms excluded
- **effort:** Large KMD plus coupled platform ABI; donor-to-stock deltas unmeasured
- **dependency:** GKI-KMI-BASELINE; TMEM-FFA; GZ-TRANSPORT; MTK-TINYSYS-IPI; GPUEB client ABI
- **phone:** No for static parity; later hardware/runtime acceptance needs separate authorization
- [Canonical handoff/evidence](../accelerator-preparation/MALI-GPU-KERNEL/CLAUDE-HANDOFF.md).

## 7. DTB-DTBO — PARTIAL

- **kind:** STATIC SOURCE CONTRACT
- **scope:** Selected base DTB/DTBO sources, overlay selection and bootloader mutation contract
- **difficulty:** MEDIUM
- **probability:** Highest: bounded blobs and selection metadata already exist
- **evidence:** Merged/base/overlay DT inventory and exact boot-container/partition ledgers
- **missing:** Reproducible source-complete DTS/DTBO build and explicit reconciliation of observed bootloader changes
- **closure:** All selected blobs rebuild with documented property/phandle/selection equivalence; every observed mutation classified. No unobserved runtime behavior claimed.
- **effort:** Several days to two weeks
- **dependency:** BOOT-IMAGES; PARTITION-OWNERSHIP; proposed Mali contract for GPU-specific source details
- **phone:** No for static closure using existing dumps; yes only for new runtime/boot acceptance
- [Canonical handoff/evidence](../../docs/dt-module-matching.md).

## 8. FT3680-TOUCH — PARTIAL

- **kind:** KERNEL MODULE PARITY
- **scope:** focaltech_touch_spi_ft3680.ko host driver (not proprietary embedded firmware)
- **difficulty:** MEDIUM/HARD
- **probability:** Good but uncertain: bounded, buildable 166-function reconstruction
- **evidence:** 166/166 functions; 105/105 import CRCs; 67 raw, 69 normalized and 29 order-only functions
- **missing:** 40 size-different functions; 68 outside normalized/order-only classes; FHP/FWDBG, flash, IRQ and cleanup residuals
- **closure:** All function/data/ABI/relocation differences closed against stock, with independently reproducible build and only explicitly proved build-provenance/firmware boundary residuals.
- **effort:** One to several weeks
- **dependency:** SPI-MT65XX; YFT-TPD-GESTURE; retained firmware metadata
- **phone:** No for module parity; hardware tests remain a separate acceptance gate
- [Canonical handoff/evidence](../display-input/ft3680/parity-report.md).

## 9. YFT-DEVINFO — PARTIAL

- **kind:** KERNEL MODULE PARITY
- **scope:** yft_devinfo.ko provider, exported registry ABI and probe/sysfs logic
- **difficulty:** HARD (not a quick enum edit)
- **probability:** Moderate: small residual but unknown enum spelling may resist exact closure
- **evidence:** 54/72 byte-identical functions, 61/72 KCFI IDs, 40/40 import CRCs, 17/27 export CRCs; large enum-search exclusions already recorded
- **missing:** Vendor enum identity affecting ten device_add exports plus probe/sysfs codegen residuals
- **closure:** 72/72 function behavior/bytes and all data, 27 export CRCs and KCFI identities proven; reproduce from source with explicit provenance residuals only.
- **effort:** Days to weeks; unbounded donor/enum risk
- **dependency:** Existing registry consumers; source/donor ABI evidence (not more documentation)
- **phone:** No for static parity; runtime registry validation is separate
- [Canonical handoff/evidence](../../kernel/phase4-yft-devinfo-kcfi-typeid.md).

## Separate ROM integration queue

| Component | Status | Remaining action |
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

[Accelerator roadmap](../accelerator-re-roadmap.md): all six registered scopes are workspace-DONE; Mali's older canonical-PARTIAL entry is stale, not a new module-parity target. Runtime/HAL/SELinux, proprietary and inventory tracking are not module-parity shortcuts.
