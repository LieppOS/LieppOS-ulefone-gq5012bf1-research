"""Final audit decisions, not filesystem migrations or component reconstruction.

Ranking is qualitative closure probability for the entire named static scope, not
a runtime-readiness score. Effort ranges are estimates, not measured promises.
"""

# In priority order; generation drops any registered candidate no longer PARTIAL.
CANDIDATES = [
    {
        "component": "DTB-DTBO", "kind": "STATIC SOURCE CONTRACT", "scope": "Selected base DTB/DTBO sources, overlay selection and bootloader mutation contract",
        "difficulty": "MEDIUM", "probability": "Highest: bounded blobs and selection metadata already exist",
        "evidence": "Merged/base/overlay DT inventory and exact boot-container/partition ledgers",
        "research_path": "docs/dt-module-matching.md",
        "missing": "Reproducible source-complete DTS/DTBO build and explicit reconciliation of observed bootloader changes",
        "closure": "All selected blobs rebuild with documented property/phandle/selection equivalence; every observed mutation classified. No unobserved runtime behavior claimed.",
        "effort": "Several days to two weeks", "dependency": "BOOT-IMAGES; PARTITION-OWNERSHIP; proposed Mali contract for GPU-specific source details",
        "phone": "No for static closure using existing dumps; yes only for new runtime/boot acceptance",
    },
    {
        "component": "FT3680-TOUCH", "kind": "KERNEL MODULE PARITY", "scope": "focaltech_touch_spi_ft3680.ko host driver (not proprietary embedded firmware)",
        "difficulty": "MEDIUM/HARD", "probability": "Good but uncertain: bounded, buildable 166-function reconstruction",
        "evidence": "166/166 functions; 105/105 import CRCs; 67 raw, 69 normalized and 29 order-only functions",
        "research_path": "reverse-engineering/display-input/ft3680/parity-report.md",
        "missing": "40 size-different functions; 68 outside normalized/order-only classes; FHP/FWDBG, flash, IRQ and cleanup residuals",
        "closure": "All function/data/ABI/relocation differences closed against stock, with independently reproducible build and only explicitly proved build-provenance/firmware boundary residuals.",
        "effort": "One to several weeks", "dependency": "SPI-MT65XX; YFT-TPD-GESTURE; retained firmware metadata",
        "phone": "No for module parity; hardware tests remain a separate acceptance gate",
    },
    {
        "component": "YFT-DEVINFO", "kind": "KERNEL MODULE PARITY", "scope": "yft_devinfo.ko provider, exported registry ABI and probe/sysfs logic",
        "difficulty": "HARD (not a quick enum edit)", "probability": "Moderate: small residual but unknown enum spelling may resist exact closure",
        "evidence": "54/72 byte-identical functions, 61/72 KCFI IDs, 40/40 import CRCs, 17/27 export CRCs; large enum-search exclusions already recorded",
        "research_path": "kernel/phase4-yft-devinfo-kcfi-typeid.md",
        "missing": "Vendor enum identity affecting ten device_add exports plus probe/sysfs codegen residuals",
        "closure": "72/72 function behavior/bytes and all data, 27 export CRCs and KCFI identities proven; reproduce from source with explicit provenance residuals only.",
        "effort": "Days to weeks; unbounded donor/enum risk", "dependency": "Existing registry consumers; source/donor ABI evidence (not more documentation)",
        "phone": "No for static parity; runtime registry validation is separate",
    },
    {
        "component": "CAMERA-ISP-KERNEL", "kind": "PROPOSED SPLIT / KERNEL MODULE PARITY", "scope": "CAMERA-HAL-ISP's ISP7sp/imgsensor framework kernel modules and DT/normal-world ABI only",
        "difficulty": "HARD", "probability": "Moderate/lower: source coverage exists, but entire ISP set has not been parity-built",
        "evidence": "Existing ISP module/source-coverage ledger and imgsensor framework 507/532 byte-identical with one struct delta",
        "research_path": "reverse-engineering/camera-stack/notes/isp-stack.md",
        "missing": "ISP framework/provider source builds and module-by-module ABI/function/data parity; explicit ownership transfer list",
        "closure": "Enumerated ISP kernel set closes with reproducible parity and DT/platform contract; HAL, 3A, tuning DB and signed CCU remain explicitly outside scope.",
        "effort": "Several weeks to months", "dependency": "Approved split; existing camera sensor/VCM/OIS/EEPROM children; source donors and exact GKI",
        "phone": "No for static kernel closure; camera runtime/quality validation needs phone later",
    },
    {
        "component": "MALI-GPU-KERNEL", "kind": "PROPOSED ADD / KERNEL MODULE PARITY", "scope": "Active r44 Valhall KMD, MGM/protected allocator, Mali/G3D DT and normal-world GPU platform ABI",
        "difficulty": "HARD / source availability uncertain", "probability": "Lowest of this list: ownership absent and matched platform source/parity not established",
        "evidence": "Three shipped KMD/support modules, three enabled DT compatibles, two GPU HAL families and two init services",
        "research_path": "reverse-engineering/coverage-audit/MISSING-COVERAGE.md",
        "missing": "Matched r44/MT6878 KMD and board glue source, builds, ABI and function/data parity; do not assume a source donor exists",
        "closure": "All three active modules and GPU DT/platform ABI reproducibly reconstructed; proprietary userspace/CSF firmware retained and not claimed open.",
        "effort": "Several weeks to months; source-access risk", "dependency": "Approved ADD; GKI-KMI-BASELINE; TMEM-FFA; retained GPU userspace/CSF firmware",
        "phone": "No for static parity if stock operands/source suffice; required later for graphics/secure-buffer/runtime tests",
    },
]

# Separate queue: completion here is ROM integration, NOT fresh module RE.
INTEGRATION = {
    "SYSTEM-DLKM": "Use the 60/60 reproducible GKI module ELF-body baseline; match custom GKI/KMI, signing, packaging and load order. A stock rebuild does not prove a custom kernel boots.",
    "BOOT-IMAGES": "Use the exact recorded container geometry; test custom boot separately. Slot B is the stock-integrity anchor, not a disposable development slot.",
    "VENDOR-PROPERTIES": "Preserve externally applied device commit 24afa6b: 327 vendor keys, 16 documented exclusions and one EGL rewrite from the original 343-key missing ledger. Verify generated/inherited definitions, emitted-image precedence, SELinux and runtime; do not reinstall blindly. No integration change made by audit.",
    "VINTF-HAL-MANIFEST": "Preserve externally applied bluetooth_audio.xml inclusion (not EXTRACT_ONLY) and vendor prebuilt module. The refreshed ledger is 146 present/48 SKU-only/5 source-built/0 dropped. Assemble/check VINTF and validate actual HAL registration under enforcing SELinux.",
    "PARTITION-OWNERSHIP": "Use the 61-group consumer and rollback-location ledger for FBE/OTA/recovery integration; do not overwrite private calibration or bootloader-owned metadata.",
    "USB-CHARGER-INTEGRATION": "Kernel parity is closed; validate USB/PD/reverse-power arbitration and safety using suitable hardware, without inferring 120 W acceptance from filenames.",
    "INTERNAL-THERMAL-USB": "Integrate UVC/command/viewer paths; validate power/suspend and thermal-camera behavior separately from the closed USB/power kernel contract.",
    "ANDROID-INIT": "Finish the static service/property graph and assembly, then test real boot ordering; this is integration-contract closure, not module parity.",
    "VENDOR-SEPOLICY": "Reconstruct/build device policy and contexts, review neverallows, then resolve enforcing runtime denials; static compilation alone is not daily-driver validation.",
    "OTA-AB-UPDATE": "End-to-end signing/snapshot/merge/rollback acceptance is runtime-gated, not a static PARTIAL-to-DONE shortcut.",
    "RECOVERY-ORANGEFOX": "Backup/restore/flashing/FBE/USB acceptance remains runtime-gated; do not put the stock anchor at risk.",
}

PROPOSALS = [
    ("PC-001", "ADD", "MALI-GPU-KERNEL", "ACCEPT RECOMMENDATION", 1,
     "Ten E rows converge on one active source-actionable kernel/DT/platform scope, not ten components.",
     "Keep proprietary CSF firmware and GPU userspace outside closure; preserve source claims/metadata and add only after approval."),
    ("PC-002", "SPLIT", "CAMERA-HAL-ISP → CAMERA-HAL-ISP + CAMERA-ISP-KERNEL", "ACCEPT RECOMMENDATION", 1,
     "Existing ISP source/module ledger proves actionable kernel work is mixed with permanently proprietary HAL/3A/tuning/CCU.",
     "Transfer an explicit module/DT ownership ledger to the new child without duplicating primary ownership; retain HAL scope and historical evidence."),
    ("PC-003", "MERGE", "GZ-IPC-MOD, GZ-MAIN-MOD, GZ-TRUSTY-MOD, GZ-TZ-SYSTEM → GZ-TRANSPORT", "ACCEPT RECOMMENDATION", -4,
     "Four exact-source transport children and their parent share a coherent normal-world transport boundary.",
     "Preserve all per-module parity/source/ABI subreports and provenance; do not imply signed hypervisor/TA source closure."),
    ("PC-004", "MERGE", "AW36518-V2-FLASH → AW36518-FLASH", "ACCEPT RECOMMENDATION", -1,
     "Sibling reports distinguish two shipped source variants of the AW36518 family.",
     "Keep both stock module variants, topology, source and parity reports as named subscopes."),
    ("PC-005", "MERGE", "USB3-FEASIBILITY → USB-TYPEC", "ACCEPT RECOMMENDATION", -1,
     "The resolved-negative SuperSpeed board capability study is a finding under Type-C ownership.",
     "Preserve the USB3-port absence proof and do not discard evidence just because the component is retired."),
    ("PC-006", "MERGE", "VENDOR-ALL-MODULES-READY → INIT-INSMOD", "ACCEPT RECOMMENDATION", -1,
     "The sole setter/consumer property timeline belongs to module-loader/init ordering.",
     "Keep the complete setter/consumer and boot-phase evidence under INIT-INSMOD; redirect old links."),
    ("PC-007", "REMOVE", "ESIM-EUICC-ABSENCE", "ACCEPT RECOMMENDATION", -1,
     "A proven absence is a negative hardware finding, not an implementation target.",
     "Archive the original reports and retain an explicit not-fitted finding; reassign the hardware row to negative-inventory ownership before retiring its registered name."),
    ("PC-008", "REMOVE", "WIRELESS-CHARGING-ABSENCE", "ACCEPT RECOMMENDATION", -1,
     "No fitted wireless-charging implementation scope is established; wired reverse power is separate.",
     "Archive original negative evidence in power/hardware inventory and migrate references/ownership before retirement."),
    ("PC-009", "RENAME", "RT5133-POWER-IC → RT5133-CAMERA-LDO-INTEGRATION", "REJECT", 0,
     "The claimed successful binding was a client-name misread; no newer success capture exists. The observed client is unbound and camera rails use WL2864C.",
     "Keep the existing name, two-module static DONE scope and GPIO1 safety warning. Physical population needs evidence; do not rename on an inferred reference-board role."),
    ("PC-010", "METADATA", "OEM-KERNEL-MODULES, VENDOR-DLKM and inventory/umbrella labels", "ACCEPT RECOMMENDATION", 0,
     "Use the measured module universe and current child closures; tracking is not reconstruction. SYSTEM-DLKM is now DONE for its measured 60-module baseline, not an unfinished umbrella.",
     "Refresh stale metadata/checklists only after approval; preserve all registers/provenance, with no automatic status or ownership move."),
]
