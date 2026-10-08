#!/usr/bin/env python3
"""Build the canonical one-row-per-component coverage database.

The workspace folder names/statuses are authoritative.  Scope/state judgements are
curated here; artifact columns are measured from axes 1-8.  This script recommends
changes but never moves a workspace folder.
"""
from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict
from accelerator_owners import SCOPES, COMPONENTS as ACCELERATOR_COMPONENTS

HERE = os.path.dirname(os.path.abspath(__file__))
CA = os.path.dirname(HERE)
RAW = os.path.join(CA, "audit-evidence")
OUT = os.path.join(CA, "components.tsv")
NOTE = os.path.join(CA, "notes", "COMPONENT-AUDIT.md")
DATE = "2026-10-08"


def read_tsv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def compact(values: set[str]) -> str:
    return ", ".join(sorted(v for v in values if v and v != "-"))


# class, kernel, userspace, firmware, hardware, remaining/boundary,
# best next action, difficulty, dependencies
P: dict[str, tuple[str, str, str, str, str, str, str, str, str]] = {
    "ANDROID-INIT": ("A", "N/A", "PARTIAL", "N/A", "N/A",
        "Reconcile stock/current service ordering and validate property-trigger behavior.",
        "Diff generated service graph against LieppOS init and test one boot.", "MEDIUM", "BOOT-IMAGES, VENDOR-PROPERTIES, VENDOR-SEPOLICY"),
    "AUDIO-DSP": ("B", "CLOSED", "PROPRIETARY", "SIGNED/BINARY", "PROVEN",
        "Kernel AFE/DSP transport is closed; DSP protocol, firmware, routing and calibration remain proprietary.",
        "Map HAL-to-DSP messages and preserve stock firmware/calibration.", "HARD", "AUDIO-DSP-KERNEL, MT6878-AFE, MT6369-AUDIO-CODEC"),
    "BATTERY-PACK": ("D", "CLOSED", "PARTIAL", "DEVICE-INTERNAL", "TEARDOWN",
        "Cell/BMS identity, connector topology, calibration and ageing model need teardown/runtime evidence.",
        "Photograph labels/connectors and capture read-only gauge/health data.", "HARD", "SH366003-FUEL-GAUGE, MT6375-CHARGER"),
    "BLUETOOTH": ("B", "CLOSED", "PROPRIETARY", "SIGNED", "PROVEN",
        "Kernel transport is closed; controller firmware, vendor HAL internals and LE Audio behavior remain proprietary/runtime-gated.",
        "Retain signed firmware; run HCI/LE Audio feature validation.", "HARD", "MT6637-BT-KERNEL, CONNINFRA-KERNEL"),
    "BOOT-IMAGES": ("A", "PARTIAL", "N/A", "SOURCE/BINARY", "N/A",
        "Stock geometry is known; booting a custom kernel/GKI ramdisk within the exact image contract remains open.",
        "Produce a reproducible stock-size boot/vendor_boot/init_boot set and boot-test Slot B.", "MEDIUM", "AVB-SIGNING-CHAIN, DTB-DTBO, ANDROID-INIT"),
    "CAMERA-HAL-ISP": ("A", "PARTIAL", "PROPRIETARY", "SIGNED/BINARY", "PROVEN",
        "Actionable ISP kernel parity is not closed (A, pending approved split); whole HAL/3A/tuning/CCU scope cannot close statically and remains proprietary.",
        "Split actionable ISP-kernel closure from the permanently proprietary HAL/tuning scope.", "HARD", "CAMERA-* sensors, CAMERA-VCMS, CAMERA-EEPROMS, DW9781C-OIS"),
    "COOLING-HARDWARE": ("D", "CLOSED", "PARTIAL", "N/A", "TEARDOWN",
        "Material stack, heat spreaders, contact paths and measured thermal model require physical inspection.",
        "Teardown and correlate sustained-load temperatures with thermal zones.", "HARD", "THERMAL-POWER-HAL, BATTERY-PACK"),
    "DRAM-MEMORY": ("D", "PARTIAL", "N/A", "SIGNED", "TEARDOWN",
        "Exact package/topology/timings and training firmware cannot be recovered from normal Android artifacts alone.",
        "Read package markings or schematics; retain signed preloader/training data.", "HARD", "BOOT-IMAGES, PARTITION-OWNERSHIP"),
    "DTB-DTBO": ("A", "PARTIAL", "N/A", "SOURCE", "PARTIAL",
        "Effective tree is inventoried; source-complete DTS and bootloader mutation/runtime validation remain.",
        "Decompile/normalize each selected DTB/DTBO and reconcile the three Mali nodes after GPU ownership is added.", "MEDIUM", "BOOT-IMAGES, PARTITION-OWNERSHIP"),
    "FIRMWARE-INVENTORY": ("F", "MIXED", "MIXED", "MIXED", "N/A",
        "Persistent cross-subsystem inventory; payload ownership changes whenever stock/vendor extraction changes.",
        "Regenerate metadata hashes on each stock drop; do not attempt source parity for signed payloads.", "QUICK", "all firmware-owning components"),
    "FM-RADIO-HEADSET": ("B", "CLOSED", "PROPRIETARY", "BINARY", "PARTIAL",
        "Kernel/headset path is closed; FM app/JNI/patch, LNA/antenna identity and RF performance remain.",
        "Read-only runtime FM validation and teardown-only LNA/antenna confirmation.", "HARD", "FM-KERNEL, FM78100-COMPANION, MT6369-AUDIO-CODEC"),
    "FT3680-TOUCH": ("A", "PARTIAL", "N/A", "DEVICE-INTERNAL", "PROVEN",
        "Core contract is recovered, but 40 functions remain size-different and 68 remain outside normalized parity classes.",
        "Continue static parity on FHP/FWDBG/flash/IRQ residuals without modifying live firmware.", "MEDIUM", "SPI-MT65XX, YFT-TPD-GESTURE"),
    "GNSS": ("B", "CLOSED", "PROPRIETARY", "SIGNED", "PROVEN",
        "Kernel transport is closed; connsys GNSS firmware, mnld/libmnl and live L1/L5 behavior remain proprietary/runtime-gated.",
        "Retain signed image and capture read-only constellation/L5 behavior.", "HARD", "GNSS-KERNEL-TRANSPORT, CONNINFRA-KERNEL"),
    "ICM4N607-IMU": ("C", "CLOSED (transport)", "PROPRIETARY", "SIGNED (SCP)", "PROVEN",
        "The physical sensor driver lives inside signed SCP firmware; exact register protocol and calibration are unavailable.",
        "Do not invent a Linux I2C driver; validate Android sensor outputs and preserve SCP firmware.", "PROPRIETARY-GATED", "SENSOR-HUB, SENSOR-HUB-KERNEL"),
    "IMS": ("C", "CLOSED (kernel transport)", "PROPRIETARY", "SIGNED", "PROVEN",
        "VoLTE/VoWiFi/RCS/video-telephony implementation is a proprietary modem/RIL/IMS island.",
        "Map service/property contracts and validate carrier behavior using retained vendor blobs.", "PROPRIETARY-GATED", "RADIO-HAL-RIL, MODEM-FIRMWARE"),
    "KEYSTORE-VOLD-KEYMINT": ("B", "CLOSED (normal world)", "PROPRIETARY", "SIGNED (TEE)", "N/A",
        "Normal-world FBE/RPMB/KeyMint integration is mapped; TA semantics, keys and provisioning remain proprietary.",
        "Validate FBE, credential unlock and OTA key continuity on the target ROM.", "HARD", "TKCORE-DRV, UFS-RPMB-KERNEL, TRUSTKERNEL-TEE"),
    "MADEV-FINGERPRINT": ("B", "CLOSED (kernel)", "PROPRIETARY", "SIGNED (TA)", "PROVEN",
        "Kernel/TEE-client drivers are closed; sensor protocol, HAL, templates and secure TA remain proprietary.",
        "Treat stock HAL/TA as a binary island and validate enroll/auth after ROM integration.", "PROPRIETARY-GATED", "MICROARRAY-FP-TEE, FINGERPRINT-PLATFORM-SHIM, TRUSTKERNEL-TEE"),
    "MICROPHONES": ("D", "CLOSED", "PARTIAL", "N/A", "TEARDOWN",
        "Package/acoustic-port confirmation plus enforcing-SELinux and full Audio HAL tests remain.",
        "Teardown/board-view inspection, then end-to-end recording/call tests.", "HARD", "MT6369-AUDIO-CODEC, MT6878-AFE, AUDIO-DSP"),
    "MMC5603-MAGNETOMETER": ("C", "CLOSED (transport)", "PROPRIETARY", "SIGNED (SCP)", "PROVEN",
        "Register driver and fusion/calibration are inside signed SCP firmware.",
        "Validate Android heading/calibration; preserve SCP firmware.", "PROPRIETARY-GATED", "SENSOR-HUB, SENSOR-HUB-KERNEL"),
    "MODEM-FIRMWARE": ("C", "CLOSED (loader)", "PROPRIETARY", "SIGNED", "PROVEN",
        "MD1 code, carrier configuration, RF calibration and signing keys are proprietary.",
        "Hash/retain stock images and map version/band metadata without payload redistribution.", "PROPRIETARY-GATED", "MODEM-KERNEL-TRANSPORT, RADIO-HAL-RIL"),
    "MT6375-CHARGER": ("A", "PARTIAL", "PARTIAL", "N/A", "PROVEN",
        "Provider/source parity and live charger/protocol behavior remain incomplete.",
        "Close static provider parity, then run read-only charging-state validation.", "MEDIUM", "TCPC-MT6375, PD-PPS-UFCS, SC8571-CHARGE-PUMP"),
    "MT6637-WIFI": ("B", "CLOSED", "PROPRIETARY", "SIGNED/BINARY", "PROVEN",
        "Kernel path is closed; controller firmware, NVRAM/calibration and vendor HAL internals remain proprietary.",
        "Preserve firmware/NVRAM and validate bands, 6E, roaming and suspend.", "HARD", "MT6637-WIFI-KERNEL, CONNINFRA-KERNEL, CONNFEM"),
    "NFC-SECURE-ELEMENT": ("B", "CLOSED", "PROPRIETARY", "SIGNED", "PROVEN",
        "ST21 controller kernel is closed; NCI HAL, secure-element applets/access rules and firmware stay proprietary.",
        "Validate NCI/eSE flows with retained blobs; do not claim applet source closure.", "PROPRIETARY-GATED", "ST21NFC, TRUSTKERNEL-TEE"),
    "NVRAM-CALIBRATION": ("C", "CLOSED (paths)", "PROPRIETARY", "DEVICE-INTERNAL", "PROVEN",
        "Partition/consumer paths are mapped; per-unit values and vendor calibration logic are private/device-specific.",
        "Complete ownership labels and back up values; never publish or synthesize per-unit calibration.", "PROPRIETARY-GATED", "PARTITION-OWNERSHIP and all calibrated subsystems"),
    "OEM-KERNEL-MODULES": ("F", "MIXED", "N/A", "N/A", "N/A",
        "Persistent whole-module-set tracker; child components have mixed closure. Its documented 471 count is stale versus the measured 457-module universe.",
        "Regenerate inventory from kernel-modules.tsv and keep only unresolved children actionable.", "QUICK", "VENDOR-DLKM, SYSTEM-DLKM, MTK-MODULE-LOADER"),
    "OTA-AB-UPDATE": ("D", "N/A", "PARTIAL", "N/A", "RUNTIME",
        "Payload signing, update_engine application, slot switch, snapshot merge and rollback need an end-to-end test.",
        "Build one signed test payload and validate entirely on the development slot.", "MEDIUM", "BOOT-CONTROL-SLOTS, AB-SUPER-GEOMETRY, AVB-SIGNING-CHAIN"),
    "PARTITION-OWNERSHIP": ("A", "N/A", "N/A", "N/A", "PROVEN",
        "Most ownership is mapped; minor persistent partitions and rollback-index ownership remain undocumented.",
        "Resolve vb/pstore/otp/sec1/proinfo semantics from read-only metadata and consumers.", "MEDIUM", "AB-SUPER-GEOMETRY, NVRAM-CALIBRATION"),
    "PD-PPS-UFCS": ("B", "CLOSED (providers)", "PARTIAL", "N/A", "RUNTIME",
        "Provider stack is mapped; negotiation policy and live protocol traces remain.",
        "Capture safe read-only PD/PPS/UFCS state transitions with a compliant analyzer.", "HARD", "TCPC-MT6375, MT6375-CHARGER, USB-CHARGER-INTEGRATION"),
    "RADIO-HAL-RIL": ("B", "CLOSED (kernel)", "PROPRIETARY", "SIGNED", "PROVEN",
        "Static service/AIDL/device boundary is mapped; vendor RIL implementation is proprietary.",
        "Preserve vendor RIL and validate calls/data/SMS/SIM/e911/carrier properties.", "PROPRIETARY-GATED", "MODEM-KERNEL-TRANSPORT, MODEM-FIRMWARE, IMS"),
    "REAR-RUGGED-FEATURES": ("F", "MIXED", "MIXED", "MIXED", "PROVEN",
        "Intentional integration umbrella over rear display/touch, keys, lights and YFT services; children have mixed closure.",
        "Keep as an integration checklist, not as a duplicate source-reconstruction target.", "QUICK", "CO5300-REAR-DISPLAY, HYNITRON-REAR-TOUCH, PROGRAMMABLE-KEYS, LN2403-CAMPLIGHT"),
    "RECOVERY-ORANGEFOX": ("D", "N/A", "PARTIAL", "N/A", "RUNTIME",
        "Core recovery works, but package flashing, backup/restore matrix, Magisk and USB identity behavior are not fully tested.",
        "Run a non-destructive recovery acceptance matrix on Slot B.", "MEDIUM", "BOOT-IMAGES, OTA-AB-UPDATE, MICROSD"),
    "SENSOR-HUB": ("B", "CLOSED (transport)", "PROPRIETARY", "SIGNED", "PROVEN",
        "Linux transport is closed; SCP physical drivers, fusion, batching and calibration are inside signed firmware.",
        "Preserve SCP image and validate Android sensor semantics; do not create fake Linux drivers.", "PROPRIETARY-GATED", "SENSOR-HUB-KERNEL, MTK-TINYSYS-IPI, physical sensor scopes"),
    "SPL07-BAROMETER": ("C", "CLOSED (transport)", "PROPRIETARY", "SIGNED (SCP)", "PROVEN",
        "Calibration coefficients and register driver live in signed SCP firmware.",
        "Validate pressure/altitude output and preserve SCP firmware.", "PROPRIETARY-GATED", "SENSOR-HUB, SENSOR-HUB-KERNEL"),
    "STK3A5X-ALS-PS": ("C", "CLOSED (transport)", "PROPRIETARY", "SIGNED (SCP)", "PROVEN",
        "Exact sub-variant, calibration and register driver are hidden in signed SCP firmware.",
        "Use runtime sensor behavior/physical markings only; preserve SCP firmware.", "PROPRIETARY-GATED", "SENSOR-HUB, SENSOR-HUB-KERNEL"),
    "SYSTEM-DLKM": ("F", "MIXED", "N/A", "N/A", "N/A",
        "Packaging/whole-image tracker; module closure belongs to child components and GKI baseline.",
        "Regenerate image/module parity after each kernel build.", "QUICK", "GKI-KMI-BASELINE, OEM-KERNEL-MODULES"),
    "THERMAL-POWER-HAL": ("B", "CLOSED (kernel dependencies)", "PROPRIETARY", "N/A", "PROVEN",
        "Kernel dependencies are mapped; thresholds, policy engines and full runtime parity remain vendor-specific.",
        "Extract all thermal/power configs and validate throttling/idle/charging states.", "HARD", "COOLING-HARDWARE, MT6375-CHARGER, SH366003-FUEL-GAUGE"),
    "THERMAL-RADIOMETRY": ("C", "N/A", "PROPRIETARY", "DEVICE-INTERNAL", "PROVEN",
        "Radiometry algorithms and per-unit calibration schema are proprietary; temperature parity needs reference measurements.",
        "Map calibration schema and compare against stock/reference targets without publishing per-unit data.", "PROPRIETARY-GATED", "THERMOVUE-T2, AC020-UVC"),
    "THERMOVUE-T2": ("B", "CLOSED (USB/power)", "PROPRIETARY", "BINARY", "PROVEN",
        "USB/UVC/power path is closed; command protocol, application, calibration ownership and replacement UI remain.",
        "Finish read-only command protocol map and integrate a replacement viewer around UVC.", "HARD", "AC020-UVC, INTERNAL-THERMAL-USB, YFT-TINY2C-USB, THERMAL-RADIOMETRY"),
    "USB-CHARGER-INTEGRATION": ("D", "CLOSED (components)", "PARTIAL", "N/A", "RUNTIME",
        "Static architecture is mapped; 120 W sink/reverse-power policy, limits and safety transitions require hardware runtime tests.",
        "Use a USB-PD analyzer and safe programmable source/load; do not infer limits from filenames.", "PHYSICAL/RUNTIME-GATED", "PD-PPS-UFCS, MT6375-CHARGER, charge pumps"),
    "VENDOR-BLOB-HAL-INVENTORY": ("F", "N/A", "MIXED/PROPRIETARY", "MIXED", "N/A",
        "Persistent cross-subsystem inventory of retained proprietary services/libraries and replacement verdicts.",
        "Regenerate from the stock extraction and close ownership, not source parity, for every blob.", "QUICK", "VINTF-HAL-MANIFEST, FIRMWARE-INVENTORY"),
    "VENDOR-DLKM": ("F", "MIXED", "N/A", "N/A", "N/A",
        "Packaging/whole-image tracker; actual source closure belongs to child driver components.",
        "Rebuild image deterministically and reconcile against the 457-module audit universe.", "MEDIUM", "OEM-KERNEL-MODULES, MTK-MODULE-LOADER"),
    "VENDOR-PROPERTIES": ("A", "N/A", "PARTIAL", "N/A", "N/A",
        "Shipped property surface is inventoried; LieppOS allowlist/override/runtime contamination controls remain.",
        "Generate the device property allowlist and validate a clean non-stock boot.", "QUICK", "ANDROID-INIT, VENDOR-SEPOLICY"),
    "VENDOR-SEPOLICY": ("A", "N/A", "PARTIAL", "N/A", "N/A",
        "Stock domains/contexts are inventoried; policy reconstruction, neverallow review and runtime denial closure remain.",
        "Map every device-specific daemon to domain/devices, build policy, then triage enforcing denials.", "MEDIUM", "VINTF-HAL-MANIFEST, ANDROID-INIT"),
    "VINTF-HAL-MANIFEST": ("A", "N/A", "PARTIAL", "N/A", "N/A",
        "Declarations are mapped; complete LieppOS assembly, compatibility checks and per-HAL SELinux remain.",
        "Generate manifests/matrices from hals-services.tsv and run vintf compatibility checks.", "QUICK", "VENDOR-BLOB-HAL-INVENTORY, VENDOR-SEPOLICY"),
    "YFT-DEVINFO": ("A", "PARTIAL", "PARTIAL", "N/A", "PROVEN",
        "One vendor enum spelling still shifts exported CRC/KCFI identities; probe/sysfs path is not byte-exact.",
        "Finish the remaining enum/probe parity without disturbing the active owner workspace.", "HARD", "ANDROID-INIT, VENDOR-PROPERTIES"),
}

for accelerator in SCOPES:
    name = accelerator['component']
    P[name] = ('A', 'PARTIAL (existing measured axes preserved)', 'PROPRIETARY CONSUMERS / kernel ABI',
               'BINARY/SIGNED (excluded)', 'DT/STATIC; execution unproved',
               'Complete every owned module on function/data/CRC/KCFI/relocation/ABI/B1-B2 axes; no new parity measured by preparation.',
               'Follow canonical accelerator CLAUDE-HANDOFF; preserve already exact source/proofs.',
               accelerator['difficulty'], accelerator['prerequisites'])
P['CAMERA-HAL-ISP'] = ('C', 'OWNED BY CAMERA-ISP-KERNEL', 'PROPRIETARY', 'SIGNED/BINARY', 'EXISTING CAMERA CAPTURES',
    'HAL/3A/tuning/calibration interpretation and firmware algorithms remain proprietary; normal-world kernel ownership transferred to child.',
    'Retain vendor userspace/firmware and integrate against CAMERA-ISP-KERNEL; do not duplicate module ownership.', 'PROPRIETARY-GATED', 'CAMERA-ISP-KERNEL; camera sensor/VCM/EEPROM/OIS/rail DONE scopes')

SCOPE = {
    "AB-SUPER-GEOMETRY": "A/B physical and dynamic-super geometry",
    "AUDIO-DSP-KERNEL": "Linux ADSP/SCP audio transport modules and ABI",
    "AVB-SIGNING-CHAIN": "AVB keys, descriptors, rollback and vbmeta topology",
    "BACKLIGHT-DISPLAY-GLUE": "Main/rear brightness, bias and thermal-backlight kernel glue",
    "BOOT-CONTROL-SLOTS": "A/B slot metadata and safe Slot-B development contract",
    "CCCI-KERNEL": "CCCI core/control/CCIF/AUXADC/SCP bridge modules",
    "CCMNI-KERNEL": "Mobile-data Linux netdev layer",
    "CONNFEM": "Connectivity RF front-end selection and no-FEM board contract",
    "CONNINFRA-KERNEL": "CONNSYS core, connscp and platform transport",
    "DPMAIF-KERNEL": "Modem packet-data DMA host interface",
    "FM-KERNEL": "MT6637 FM receiver kernel driver path",
    "GNSS-KERNEL-TRANSPORT": "GNSS kernel transport and connsys interface",
    "INIT-INSMOD": "init.insmod configuration and first-stage module loading",
    "IR-BLASTER": "Consumer IR PWM/emitter kernel and board path",
    "MEDIATEK-DRM": "MT6878 DRM core and generic panel driver modules",
    "MICROARRAY-FP-TEE": "MicroArray fingerprint TEE client kernel driver",
    "MICROSD": "Android/recovery removable-storage contract",
    "MODEM-KERNEL-TRANSPORT": "Aggregate reconstructable Linux modem transport boundary",
    "MT6637-BT-KERNEL": "MT6637 Bluetooth Linux transport",
    "MT6637-WIFI-KERNEL": "MT6637 Wi-Fi Linux driver stack",
    "MTK-MODULE-LOADER": "MediaTek kernel module loader behavior",
    "SENSOR-HUB-KERNEL": "SCP sensorhub Linux transport, not sensor register drivers",
    "VENDOR-ALL-MODULES-READY": "vendor.all.modules.ready init property lifecycle",
    "BOOT-IMAGES": "boot, vendor_boot and init_boot image geometry/content contract",
    "FIRMWARE-INVENTORY": "Cross-subsystem firmware/calibration metadata inventory",
    "FT3680-TOUCH": "FocalTech FT3680 SPI main-touch kernel driver",
    "IMS": "Proprietary IMS/VoLTE/VoWiFi/RCS/video-telephony stack",
    "MICROPHONES": "Board microphone topology and audio routing",
    "MODEM-FIRMWARE": "Signed MT6878 MD1 firmware and carrier configuration",
    "NVRAM-CALIBRATION": "NVRAM partitions, consumers and per-unit calibration boundaries",
    "OTA-AB-UPDATE": "A/B OTA payload, snapshots, merge and rollback",
    "PARTITION-OWNERSHIP": "Boot/storage/persistent partition ownership map",
    "RADIO-HAL-RIL": "Android radio HAL and proprietary vendor RIL boundary",
    "RECOVERY-ORANGEFOX": "OrangeFox recovery device integration and acceptance",
    "VENDOR-BLOB-HAL-INVENTORY": "Retained proprietary HAL/service/library ownership inventory",
    "VENDOR-PROPERTIES": "Device-specific vendor property surface and override policy",
    "VINTF-HAL-MANIFEST": "Device VINTF manifests, matrices and HAL declaration contract",
}

SCOPE.update({s['component']: s['title']+' normal-world kernel / exact module, DT and observable ABI parity; proprietary algorithms excluded' for s in SCOPES})
SCOPE['CAMERA-HAL-ISP']='Proprietary CameraProvider/HAL, 3A, tuning/calibration interpretation and ISP/CCU algorithms; kernel owned by CAMERA-ISP-KERNEL'

SUBSYSTEM = {
    "AB-SUPER-GEOMETRY": "BOOT/STORAGE", "AVB-SIGNING-CHAIN": "BOOT/SECURITY",
    "BOOT-CONTROL-SLOTS": "BOOT/OTA", "BOOT-IMAGES": "BOOT",
    "FIRMWARE-INVENTORY": "FIRMWARE", "FT3680-TOUCH": "DISPLAY/INPUT",
    "MICROARRAY-FP-TEE": "FINGERPRINT/SECURITY", "MICROPHONES": "AUDIO",
    "NVRAM-CALIBRATION": "NVRAM/CALIBRATION", "RECOVERY-ORANGEFOX": "BOOT/RECOVERY",
    "VENDOR-PROPERTIES": "ANDROID INTEGRATION", "VINTF-HAL-MANIFEST": "ANDROID INTEGRATION",
}

# Recommendations only; no folder is moved by this audit.
TAXONOMY = {
    "GZ-IPC-MOD": "MERGE into GZ-TRANSPORT",
    "GZ-MAIN-MOD": "MERGE into GZ-TRANSPORT",
    "GZ-TRUSTY-MOD": "MERGE into GZ-TRANSPORT",
    "GZ-TZ-SYSTEM": "MERGE into GZ-TRANSPORT",
    "GZ-TRANSPORT": "KEEP as canonical survivor of GZ merge",
    "AW36518-V2-FLASH": "MERGE into AW36518-FLASH as a shipped driver variant",
    "AW36518-FLASH": "KEEP as canonical survivor of AW36518 variant merge",
    "ESIM-EUICC-ABSENCE": "REMOVE as component; preserve negative finding in hardware/audit docs",
    "WIRELESS-CHARGING-ABSENCE": "REMOVE as component; preserve negative finding in hardware/audit docs",
    "USB3-FEASIBILITY": "MERGE negative capability finding into USB-TYPEC",
    "VENDOR-ALL-MODULES-READY": "MERGE init-property finding into INIT-INSMOD",
    "RT5133-POWER-IC": "KEEP name; REJECT unverified camera-LDO rename; static DONE, client unbound",
    "CAMERA-HAL-ISP": "KEEP PARTIAL proprietary HAL/3A scope; authorized kernel split APPLIED to CAMERA-ISP-KERNEL",
}


def subsystem_for(comp: str, raw: str) -> str:
    if comp in ACCELERATOR_COMPONENTS:
        return 'ACCELERATOR KERNEL'
    if comp in SUBSYSTEM:
        return SUBSYSTEM[comp]
    u = (comp + " " + raw).upper()
    groups = [
        ("THERMAL CAMERA", ("THERMOVUE", "RADIOMETRY", "AC020", "FM78100", "INTERNAL-THERMAL", "TINY2C")),
        ("CAMERA", ("CAMERA", "DW9781", "WL2868", "CUSTOM-LDO", "AW3651")),
        ("AUDIO", ("AUDIO", "MT6369", "MT6878-AFE", "AW883", "MICROPHONE")),
        ("POWER/CHARGING", ("BATTERY", "CHARG", "SC8510", "SC8571", "SH366", "PD-PPS", "COOLING", "THERMAL-POWER", "RT5133")),
        ("USB/TYPE-C", ("USB", "TCPC", "MTU3", "EXTCON")),
        ("DISPLAY/INPUT", ("DISPLAY", "TOUCH", "HAPTIC", "PWM", "RGB", "BACKLIGHT", "PROGRAMMABLE", "TPD")),
        ("MODEM/TELEPHONY", ("MODEM", "CCCI", "CCMNI", "DPMAIF", "RADIO", "IMS")),
        ("GNSS", ("GNSS",)),
        ("CONNECTIVITY", ("WIFI", "BLUETOOTH", "CONN", "FM-RADIO", "FM-KERNEL")),
        ("SENSORS/TINYSYS", ("SENSOR", "ICM", "MMC5603", "SPL07", "STK3", "TINYSYS", "MBOX", "RPMSG")),
        ("STORAGE", ("UFS", "MICROSD")),
        ("NFC", ("NFC", "ST21")),
        ("FINGERPRINT", ("FINGERPRINT", "MADEV", "MICROARRAY")),
        ("SECURITY/TEE", ("TRUST", "TKCORE", "FFA", "TMEM", "GZ-", "KEYSTORE")),
        ("IR/RUGGED", ("IR-BLASTER", "REAR-RUGGED", "CAMPLIGHT")),
        ("ANDROID INTEGRATION", ("VENDOR-BLOB", "VENDOR-SEPOLICY", "VENDOR-PROPERTIES", "VINTF", "ANDROID-INIT")),
        ("BOOT/KERNEL PACKAGING", ("BOOT", "DLKM", "KMI", "MODULE", "DTB", "PARTITION", "RECOVERY", "OTA", "AVB")),
        ("RF/PHYSICAL", ("RF-ANTENNAS",)),
    ]
    for name, needles in groups:
        if any(n in u for n in needles):
            return name
    return raw.split("/")[0].strip().upper() if raw else "OTHER BOARD GLUE"


def research_for(comp: str, sub: str) -> str:
    # Prefer an existing dedicated authoritative research directory (including
    # new closures) over the historical subsystem fallback.
    repo = os.path.dirname(os.path.dirname(CA))
    if comp in ACCELERATOR_COMPONENTS:
        return f'reverse-engineering/accelerator-preparation/{comp}/STATUS.md'
    if comp == 'CAMERA-HAL-ISP':
        return 'reverse-engineering/camera-stack/accelerator-kernel-split.md'
    for leaf in ("STATUS.md", "README.md"):
        dedicated = f"reverse-engineering/{comp.lower()}/{leaf}"
        if os.path.isfile(os.path.join(repo, dedicated)):
            return dedicated
    exact = {
        "AVB-SIGNING-CHAIN": "slot-b-investigation/untouched-b-early-boot-forensics/FIRST-STAGE-AVB-KEY-CONCLUSION.md",
        "ANDROID-INIT": "docs/service-map.md",
        "BOOT-CONTROL-SLOTS": "reverse-engineering/storage/ab-ota/boot-control.md",
        "DRAM-MEMORY": "qwen_hardware/verification/findings/dram.md",
        "DTB-DTBO": "docs/dt-module-matching.md",
        "FIRMWARE-INVENTORY": "docs/blob-map.md",
        "GKI-KMI-BASELINE": "kernel/exact-gki-build-inputs.md",
        "INIT-INSMOD": "reverse-engineering/boot/module-loading/README.md",
        "IR-BLASTER": "docs/ir-blaster.md",
        "LN2403-CAMPLIGHT": "kernel/phase4-leds-ln2403-reconstruction.md",
        "MTK-MODULE-LOADER": "reverse-engineering/boot/module-loading/README.md",
        "NVRAM-CALIBRATION": "reverse-engineering/modem/nvram/boundary.md",
        "OEM-KERNEL-MODULES": "docs/module-map.md",
        "OTA-AB-UPDATE": "reverse-engineering/storage/ab-ota/boot-control.md",
        "REAR-RUGGED-FEATURES": "reverse-engineering/display-input/rear-display-input/README.md",
        "RECOVERY-ORANGEFOX": "reverse-engineering/boot/module-loading/recovery-module-loading.md",
        "SPI-MT65XX": "kernel/phase4-spi-mt65xx-reconstruction.md",
        "VENDOR-ALL-MODULES-READY": "reverse-engineering/boot/module-loading/vendor-all-modules-ready.md",
        "VENDOR-BLOB-HAL-INVENTORY": "docs/blob-map.md",
        "VENDOR-DLKM": "reverse-engineering/boot/module-loading/README.md",
        "VENDOR-SEPOLICY": "reverse-engineering/boot/module-loading/sepolicy.md",
        "YFT-DEVINFO": "kernel/phase4-yft-devinfo-reconstruction.md",
        "CAMERA-EEPROMS": "reverse-engineering/camera/eeprom/STATUS.md",
        "CAMERA-VCMS": "reverse-engineering/camera/vcm/STATUS.md",
        "CAMERA-OV64B": "reverse-engineering/camera-stack/ov64b/STATUS.md",
        "CAMERA-S5KJN1": "reverse-engineering/camera-stack/s5kjn1/STATUS.md",
        "CAMERA-S5KJN1MAIN2": "reverse-engineering/camera-stack/s5kjn1main2/STATUS.md",
        "DW9781C-OIS": "reverse-engineering/camera-stack/dw9781c-ois/STATUS.md",
        "FT3680-TOUCH": "reverse-engineering/display-input/ft3680/README.md",
        "MEDIATEK-DRM": "reverse-engineering/display-input/mediatek-drm/README.md",
        "VTDR6115-DISPLAY": "reverse-engineering/display-input/vtdr6115/README.md",
        "CO5300-REAR-DISPLAY": "reverse-engineering/display-input/rear-display-input/co5300/README.md",
        "HYNITRON-REAR-TOUCH": "reverse-engineering/display-input/rear-display-input/hynitron/README.md",
        "GZ-TRANSPORT": "reverse-engineering/geniezone/transport/README.md",
        "MICROARRAY-FP-TEE": "reverse-engineering/microarray-fp-tee/STATUS.md",
        "RT5133-POWER-IC": "reverse-engineering/power/rt5133/STATUS.md",
        "SH366003-FUEL-GAUGE": "reverse-engineering/power-charging/sh366003/STATUS.md",
        "UFS-STORAGE": "reverse-engineering/storage/ufs/README.md",
        "MICROSD": "reverse-engineering/storage/microsd/README.md",
        "AC020-UVC": "reverse-engineering/thermal-camera/ac020/STATUS.md",
        "FM78100-COMPANION": "reverse-engineering/thermal-camera/fm78100/STATUS.md",
        "INTERNAL-THERMAL-USB": "reverse-engineering/thermal-camera/internal-usb/STATUS.md",
    }
    if comp in exact:
        return exact[comp]
    mapping = [
        ("CAMERA", "reverse-engineering/camera-stack/STATUS.md"),
        ("AUDIO", "reverse-engineering/audio/STATUS.md"),
        ("CONNECTIVITY", "reverse-engineering/connectivity/STATUS.md"),
        ("GNSS", "reverse-engineering/connectivity/gnss/README.md"),
        ("MODEM", "reverse-engineering/modem/STATUS.md"),
        ("SENSORS", "reverse-engineering/sensors/STATUS.md"),
        ("TINYSYS", "reverse-engineering/tinysys/STATUS.md"),
        ("STORAGE", "reverse-engineering/storage/STATUS.md"),
        ("NFC", "reverse-engineering/nfc/STATUS.md"),
        ("SECURITY", "reverse-engineering/tkcore/STATUS.md"),
        ("FINGERPRINT", "reverse-engineering/microarray-fp-tee/STATUS.md"),
        ("USB", "reverse-engineering/usb/STATUS.md"),
        ("POWER", "reverse-engineering/power-charging/README.md"),
        ("THERMAL CAMERA", "reverse-engineering/thermal-camera/STATUS.md"),
        ("DISPLAY", "reverse-engineering/display-input/SURVEY.md"),
    ]
    for key, path in mapping:
        if key in sub:
            return path
    raise ValueError(f"no canonical research path for {comp} ({sub})")


def main() -> int:
    identity = read_tsv(os.path.join(RAW, "pack-identity.tsv"))
    mods = read_tsv(os.path.join(CA, "kernel-modules.tsv"))
    dt = read_tsv(os.path.join(CA, "device-tree.tsv"))
    hw = read_tsv(os.path.join(CA, "hardware.tsv"))
    hals = read_tsv(os.path.join(CA, "hals-services.tsv"))
    svcs = read_tsv(os.path.join(CA, "vendor-services.tsv"))
    fw = read_tsv(os.path.join(CA, "firmware.tsv"))
    secure = read_tsv(os.path.join(CA, "secure-world.tsv"))

    modules: dict[str, set[str]] = defaultdict(set)
    services: dict[str, set[str]] = defaultdict(set)
    devices: dict[str, set[str]] = defaultdict(set)
    firmwares: dict[str, set[str]] = defaultdict(set)
    for r in mods:
        # Modules column is primary ownership, not dependency/umbrella references.
        modules[r['component']].add(r['module'])
    for r in hals:
        services[r["component"]].add(r["artifact"])
    for r in svcs:
        services[r["component"]].add(r["service"])
    for r in dt:
        devices[r["component"]].add(r["compatible"])
    for r in hw:
        devices[r["component"]].add(r["device"])
    for r in fw:
        firmwares[r["component"]].add(r["artifact"])
    for r in secure:
        devices[r["component"]].add(r["area"])

    header = ["component", "status", "workspace_path", "subsystem", "scope", "partial_class",
              "kernel_state", "userspace_state", "firmware_state", "hardware_state", "blocker",
              "recommended_action", "research_path", "modules", "services", "devices", "notes",
              "difficulty", "dependencies", "firmware_artifacts", "status_justified"]
    rows = []
    for r in sorted(identity, key=lambda x: x["component"]):
        comp, status = r["component"], r["status"]
        sub = subsystem_for(comp, r["subsystem"])
        scope = SCOPE.get(comp) or r["hardware_identity"] or r["stock_artifact"] or comp.replace("-", " ").title()
        if status == "PARTIAL":
            if comp not in P:
                raise SystemExit(f"missing PARTIAL triage: {comp}")
            cls, ks, us, fs, hs, remain, nxt, diff, deps = P[comp]
            blocker = remain
            action = TAXONOMY.get(comp, "KEEP PARTIAL; " + nxt)
            justified = "yes — open boundary is explicit"
            notes = f"Remaining: {remain} Next: {nxt}"
        elif status == "BLOCKED":
            cls = "BLOCKED"
            if comp == "RF-ANTENNAS":
                ks, us, fs, hs = "N/A", "N/A", "N/A", "TEARDOWN"
                blocker = "Requires teardown, schematic/board view, continuity or RF measurements."
                deps, diff = "CONNFEM, modem/connectivity scopes", "PHYSICAL/RUNTIME-GATED"
            elif comp == "TRUSTKERNEL-ABI-ISLAND":
                ks, us, fs, hs = "BLOCKED", "PROPRIETARY", "SIGNED", "N/A"
                blocker = "Required stock ABI functions are absent from available donor/source; private vendor island is unavailable."
                deps, diff = "TKCORE-DRV, TRUSTKERNEL-TEE", "PROPRIETARY-GATED"
            else:
                ks, us, fs, hs = "N/A (TKCORE separate)", "PROPRIETARY", "SIGNED", "N/A"
                blocker = "Private TA/helper semantics and authorized secure-world runtime evidence are unavailable."
                deps, diff = "TKCORE-DRV, TRUSTKERNEL-ABI-ISLAND", "PROPRIETARY-GATED"
            action = TAXONOMY.get(comp, "KEEP BLOCKED; preserve the proven normal-world boundary")
            notes = blocker
            justified = "yes — blocker still exists"
        else:
            cls = "SCOPE-CLOSED"
            no_kernel_scope = {
                "AB-SUPER-GEOMETRY", "AC020-UVC", "AVB-SIGNING-CHAIN",
                "BOOT-CONTROL-SLOTS", "BOOT-IMAGES", "PARTITION-OWNERSHIP",
                "VENDOR-PROPERTIES", "VINTF-HAL-MANIFEST", "ESIM-EUICC-ABSENCE", "MICROSD",
                "USB3-FEASIBILITY", "VENDOR-ALL-MODULES-READY",
                "WIRELESS-CHARGING-ABSENCE",
            }
            # The canonical project is primarily a kernel reconstruction corpus;
            # a missing direct owner join does not turn a sensor/IC's proven
            # driver scope into N/A.  Only explicitly non-kernel scopes are N/A.
            ks = "N/A" if comp in no_kernel_scope else "CLOSED"
            us = "PROPRIETARY (outside scope)" if services.get(comp) else "N/A"
            fwclasses = {x["firmware_class"] for x in fw if x["component"] == comp}
            fs = "/".join(sorted(fwclasses)) if fwclasses else "N/A"
            hs = "PROVEN" if devices.get(comp) or r["hardware_identity"] else "N/A"
            blocker = ""
            action = TAXONOMY.get(comp, "KEEP")
            rem = r["remaining"] or "Named static scope closed; runtime/system integration is outside this DONE scope."
            # DONE claims must describe the actual closed named scope, not
            # promote integration inventories into kernel/source parity.
            overrides = {
                "SYSTEM-DLKM": ("CLOSED (60 GKI module ELF bodies)", "N/A", "N/A", "N/A",
                    "60/60 stock ELF bodies incl. build-id reproduced; appended signing key differs. Custom-kernel/KMI packaging and boot remain integration."),
                "BOOT-IMAGES": ("N/A (image containers)", "N/A", "N/A", "N/A",
                    "Six stock container round-trips byte-identical; Slot B stock verified, Slot A modified. Custom-kernel boot/recovery acceptance is NOT closed."),
                "VENDOR-PROPERTIES": ("N/A", "CLOSED (747-key ledger)", "N/A", "N/A",
                    "747-key ledger closed; external 24afa6b installs 327 vendor keys with 16 exclusions/one EGL rewrite from the original 343-key gap. Verify emitted-image/generated definitions and SELinux/runtime; not applied by audit."),
                "VINTF-HAL-MANIFEST": ("N/A", "CLOSED (instance reconciliation)", "PROPRIETARY (outside scope)", "N/A",
                    "199 instances reconciled: 146 present, 48 SKU-only, 5 source-built, 0 dropped after external 24afa6b includes bluetooth_audio.xml. checkvintf/SELinux/HAL runtime remain; not applied by audit."),
                "PARTITION-OWNERSHIP": ("N/A", "CLOSED (consumer/rollback ledger)", "SIGNED (bootloader-private)", "N/A",
                    "61 partition groups and rollback locations 0/2/3/4 mapped. Private payload semantics and destructive rollback/OTA tests outside scope."),
                "RT5133-POWER-IC": ("CLOSED (two modules)", "N/A", "N/A", "PRESENT-NOT-BOUND",
                    "Inactive reference capability: probe unsuccessful, no registered/consumed rails; physical population unproved. GPIO1 conflicts with bound WL2864C camera LDO; no rename."),
                "USB-CHARGER-INTEGRATION": ("CLOSED (charger arbitration modules)", "PARTIAL (ROM integration)", "N/A", "PROVEN (topology only)",
                    "Framework/class/type-detect module parity closed; 120 W/reverse-power negotiation and safety transitions NOT runtime-validated."),
                "INTERNAL-THERMAL-USB": ("CLOSED (USB/power path)", "PARTIAL (viewer integration)", "PROPRIETARY (radiometry)", "PROVEN (topology only)",
                    "Kernel USB/UVC/power contract closed; viewer/command/radiometry and runtime thermal-camera acceptance remain separate scopes."),
            }
            ks, us, fs, hs, notes = overrides.get(comp, (ks, us, fs, hs, rem))
            diff, deps = "N/A", ""
            justified = "yes — scope-specific static closure"
        rows.append({
            "component": comp, "status": status, "workspace_path": r["path"], "subsystem": sub,
            "scope": scope, "partial_class": cls, "kernel_state": ks, "userspace_state": us,
            "firmware_state": fs, "hardware_state": hs, "blocker": blocker,
            "recommended_action": action, "research_path": research_for(comp, sub),
            "modules": compact(modules.get(comp, set())), "services": compact(services.get(comp, set())),
            "devices": compact(devices.get(comp, set())), "notes": notes, "difficulty": diff,
            "dependencies": deps, "firmware_artifacts": compact(firmwares.get(comp, set())),
            "status_justified": justified,
        })

    with open(OUT, "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, delimiter="\t", lineterminator="\n", fieldnames=header)
        w.writeheader(); w.writerows(rows)
    write_note(rows)
    print(f"components={len(rows)} partials={sum(r['status']=='PARTIAL' for r in rows)}")
    return 0


CLASS_MEANING = {
    "A": "actionable / statically closeable",
    "B": "kernel/source closed, broader proprietary scope remains",
    "C": "proprietary boundary",
    "D": "hardware/runtime/teardown gated",
    "E": "stale/duplicate/wrong PARTIAL scope",
    "F": "intentional umbrella/tracking scope",
}


def write_note(rows: list[dict]) -> None:
    """Regenerate notes/COMPONENT-AUDIT.md so workspace closures cannot leave stale numbers."""
    total = len(rows)
    status = Counter(r["status"] for r in rows)
    partials = [r for r in rows if r["status"] == "PARTIAL"]
    classes = Counter(r["partial_class"] for r in partials)
    closed = status["DONE"] - 71
    blocked_rows = sorted((r for r in rows if r["status"] == "BLOCKED"), key=lambda r: r["component"])
    status_rows = "\n".join(f"| {s} | {status[s]} |" for s in ("DONE", "PARTIAL", "BLOCKED", "TODO"))
    class_rows = "\n".join(f"| {c} | {CLASS_MEANING[c]} | {classes[c]} |" for c in "ABCDEF")
    blocked_text = "\n".join(
        f"- `{r['component']}`: {r['blocker'] or r['notes'] or 'blocker not recorded'}"
        for r in blocked_rows)
    with open(NOTE, "w", encoding="utf8") as fh:
        fh.write(f"""# Axis 11: canonical component-folder audit

Audit date: {DATE}

`components.tsv` is generated from the actual canonical workspace folders, not from
the old typed totals. The measured current workspace is:

| Status | Count |
|---|---:|
{status_rows}
| **Total** | **{total}** |

This supersedes the 71/59/3 snapshot in the original audit request. The total stayed
{total} while {closed} folders have since moved from PARTIAL to DONE through
independently verified closures; each moved folder carries its own closure README
with measured parity evidence.

## PARTIAL classification

| Class | Meaning | Count |
|---|---|---:|
{class_rows}

Every PARTIAL row in `components.tsv` has an explicit boundary, next action,
difficulty and dependency list, and each is expanded individually in
[PARTIAL-TRIAGE.md](../PARTIAL-TRIAGE.md). The SCP-owned physical sensors are class
C—not missing Linux drivers—because their register drivers and calibration live in
the signed SCP image.

## DONE audit

DONE is interpreted as **named-scope static closure**, never as a claim that every
proprietary firmware/HAL/runtime behavior is open. The module, DT, HAL/service,
firmware and hardware axes were joined back to every component row to expose
boundaries.

No evidence justifies an automatic DONE → PARTIAL move in this audit. Several DONE
rows still have runtime or physical follow-up, but their READMEs explicitly exclude
it from the closed static scope. Examples include MediaTek DRM runtime validation,
microSD insertion/format behavior and RT5133 physical population confirmation (not an active camera LDO). These
must remain visible as boundaries; they are not silently treated as source gaps.

Taxonomy quality is a separate question. Some DONE folders are valid findings but
poor canonical ownership boundaries (GZ per-module children, negative-absence
findings, USB3 feasibility and the `vendor.all.modules.ready` property). They are
recommendations in [PROPOSED-CHANGES.md](../PROPOSED-CHANGES.md); no folder was
moved or deleted by this audit.

## BLOCKED audit

All {len(blocked_rows)} blockers still exist:

{blocked_text}

None should be moved automatically.

## Measured joins

`components.tsv` includes, per component:

- directly owned and umbrella-recorded kernel modules from `kernel-modules.tsv`;
- VINTF/HAL interfaces and init services from axes 4–5;
- DT compatibles plus physical devices from axes 2–3;
- firmware/calibration artifacts from axis 6;
- best available research-repository report path;
- recommended taxonomy action, if any.

The generator fails if any current PARTIAL lacks a curated A–F decision. This
prevents a newly added/moved folder from silently disappearing from triage.
""")


if __name__ == "__main__":
    raise SystemExit(main())
