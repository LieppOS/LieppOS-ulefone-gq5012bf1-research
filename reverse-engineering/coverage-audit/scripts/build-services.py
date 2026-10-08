#!/usr/bin/env python3
"""Coverage audit axes 4-6: VINTF HALs, legacy HAL libraries, init services, firmware.

Inputs are the raw harvests in ``audit-evidence/`` (see
``harvest-stock-artifacts.py``); outputs are the per-axis coverage tables in
``coverage-audit/``::

    hals-services.tsv    axis 4: every declared VINTF interface + every legacy
                         ``android.hardware.*`` backend library
    vendor-services.tsv  axis 5: every init-declared service and every binary
                         launched from an ``on`` trigger section
    firmware.tsv         axis 6: every firmware/calibration payload and every
                         partition payload that is a firmware image

Coverage codes are shared with axes 1-3 (``kernel-modules.tsv``,
``device-tree.tsv``, ``hardware.tsv``):

    A  a dedicated RE component owns this artifact
    B  a broader/parent RE component owns it
    C  generic AOSP/GKI/MTK platform infrastructure - no dedicated device RE needed
    D  shipped but dead / reference-board or example-stub baggage
    E  currently missing coverage (no component owns it)

Ownership is a curated judgement: an exact-match table first, then ordered family
rules, never text mining against the component folder names.  Every row keeps its
raw evidence columns (declaring document, init rc file, VINTF class, size, sha256)
so any judgement can be re-checked against the stock image.  Anything that cannot
be resolved confidently stays ``UNKNOWN`` with coverage ``E``; nothing here
silently defaults to ``not needed``.

Component names referenced here must exist under one of the canonical workspace
status directories; ``scripts/check-component-names.py`` validates that.
"""
from __future__ import annotations

import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CA = os.path.dirname(HERE)
AUDIT = os.path.dirname(CA)
RAW = os.path.join(CA, "audit-evidence")

GEN = "GENERIC-PLATFORM-INFRASTRUCTURE"
BLOB = "VENDOR-BLOB-HAL-INVENTORY"
V = r"vendor\.mediatek\.hardware\."


def read_raw(name: str) -> list[dict]:
    with open(os.path.join(RAW, name), newline="", encoding="utf8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_rows(name: str, header: list[str], rows: list[list]) -> None:
    with open(os.path.join(CA, name), "w", newline="", encoding="utf8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def join(vals) -> str:
    return " ".join(sorted({v for v in vals if v}))


def component_statuses() -> dict[str, str]:
    return {r["component"]: r["status"] for r in read_raw("pack-identity.tsv")}


def kernel_dependency(component: str) -> str:
    deps = {
        "AUDIO-DSP": "MT6878-AFE + AUDIO-DSP-KERNEL",
        "AW2013-RGB-LED": "aw2013 + MTK PWM/LED class",
        "BLUETOOTH": "MT6637-BT-KERNEL + CONNINFRA-KERNEL",
        "CAMERA-HAL-ISP": "camsys/seninf/imgsys/imgsensor/CCU kernel stack",
        "CO5300-REAR-DISPLAY": "spi_tiny_lcd + MTK display glue",
        "CONNINFRA-KERNEL": "conninfra/connscp/connfem modules",
        "DTB-DTBO": "bootloader-selected DTB/DTBO",
        "FT3680-TOUCH": "FocalTech SPI touch + TPD gesture path",
        "GNSS": "GNSS-KERNEL-TRANSPORT + CONNINFRA-KERNEL",
        "HAPTICS": "PMIC vibrator/regulator path",
        "IMS": "RADIO-HAL-RIL + CCCI/CCMNI/DPMAIF",
        "IR-BLASTER": "irtx PWM + AW36515 illumination path",
        "KEYSTORE-VOLD-KEYMINT": "TKCORE-DRV + UFS-RPMB-KERNEL",
        "MADEV-FINGERPRINT": "Madev/MicroArray SPI fingerprint + TKCORE-DRV",
        "MEDIATEK-DRM": "mediatek-drm + TMEM/FFA secure memory",
        "MT6637-WIFI": "MT6637-WIFI-KERNEL + CONNINFRA-KERNEL",
        "NFC-SECURE-ELEMENT": "ST21NFC + TKCORE/RPMB where secure applets apply",
        "NVRAM-CALIBRATION": "NVRAM partitions + per-device drivers",
        "RADIO-HAL-RIL": "CCCI-KERNEL + CCMNI-KERNEL + DPMAIF-KERNEL",
        "REAR-RUGGED-FEATURES": "YFT board sysfs/procfs glue",
        "SENSOR-HUB": "SENSOR-HUB-KERNEL + MTK-TINYSYS-IPI",
        "THERMAL-POWER-HAL": "thermal zones + charger/fuel-gauge/power drivers",
        "TRUSTKERNEL-TEE": "TKCORE-DRV + FFA-V10 + TMEM-FFA",
        "USB-TYPEC": "MTU3-SSUSB + TCPC-MT6375 + USB-PHY/EXTCON",
        "UNMAPPED": "Mali Valhall KMD (currently uncovered)",
        BLOB: "vendor graphics/media kernel ABI; see component-specific blobs",
        GEN: "generic AOSP/MTK platform ABI",
    }
    return deps.get(component, component)


def device_access(component: str) -> str:
    access = {
        "CAMERA-HAL-ISP": "/dev/video*; /dev/mtk-cam*; camera sysfs/ioctls",
        "MADEV-FINGERPRINT": "/dev/madev*; fingerprint sysfs; TKCORE client",
        "RADIO-HAL-RIL": "/dev/ccci*; /dev/ccmni*; modem sysfs",
        "MODEM-KERNEL-TRANSPORT": "/dev/ccci*; modem control sysfs",
        "IMS": "/dev/ccci* via vendor RIL/IMS IPC",
        "GNSS": "/dev/gps*; connsys GNSS IPC",
        "CONNINFRA-KERNEL": "/dev/wmt* and connsys debug/control sysfs",
        "BLUETOOTH": "HCI/UART/connsys control nodes",
        "MT6637-WIFI": "nl80211/cfg80211 + Wi-Fi driver private ioctls",
        "SENSOR-HUB": "/dev/sensorhub*; SCP/IPI sensor sysfs",
        "THERMAL-POWER-HAL": "/sys/class/thermal; /sys/class/power_supply; power HAL sysfs",
        "MT6375-CHARGER": "/sys/class/power_supply; charger device ioctls",
        "SH366003-FUEL-GAUGE": "/sys/class/power_supply",
        "TRUSTKERNEL-TEE": "/dev/tkcore*; /dev/tee*; TrustKernel IPC",
        "KEYSTORE-VOLD-KEYMINT": "/dev/tkcore*; RPMB; /metadata and userdata block devices",
        "UFS-STORAGE": "UFS block devices; /sys/class/scsi_host; Trusty storage IPC",
        "NVRAM-CALIBRATION": "/dev/block/by-name/nv*; NVRAM binder service",
        "USB-TYPEC": "/sys/class/typec; configfs USB gadget; USB role/TCPC sysfs",
        "EXTERNAL-USB": "USB-OTG block devices and FUSE mount path",
        "IR-BLASTER": "/dev/consumerir*; PWM/IR sysfs",
        "FT3680-TOUCH": "/dev/input/event*; FocalTech/TPD sysfs",
        "YFT-TPD-GESTURE": "YFT TPD wake-gesture sysfs",
        "CO5300-REAR-DISPLAY": "rear-display SPI/TinyLCD sysfs/HAL",
        "REAR-RUGGED-FEATURES": "YFT board-specific sysfs/procfs nodes",
        "YFT-DEVINFO": "YFT vendor/device-info sysfs/procfs nodes",
        "HAPTICS": "/sys/class/leds/vibrator or vibrator HAL sysfs",
        "AW2013-RGB-LED": "/sys/class/leds/*",
        "BOOT-CONTROL-SLOTS": "/dev/block/by-name/misc; boot-control metadata",
        "OTA-AB-UPDATE": "dynamic-partition/snapshot block devices",
        "DTB-DTBO": "boot device-tree paths (no runtime device node)",
        "UNMAPPED": "Mali device node/sysfs (exact ABI not yet assigned)",
        GEN: "N/A (generic framework/platform service)",
        BLOB: "UNKNOWN per closed binary; owned by vendor blob/HAL inventory",
    }
    return access.get(component, "see owning component; no per-service runtime trace captured")


def firmware_parties(component: str, basename: str) -> tuple[str, str, str]:
    parties = {
        "AW883XX-SPEAKER-AMP": ("Awinic / AW88394", "aw883xx kernel driver + audio HAL", "smart-speaker DSP"),
        "BLUETOOTH": ("MediaTek / MT6637 BT", "wmt_loader/connsys firmware loader", "Bluetooth controller"),
        "SENSOR-HUB": ("MediaTek / MT6878 tinysys", "mtk_tinysys_ipi remoteproc path", "SCP/CCU/DPM/SSPM/MCUPM"),
        "FM-RADIO-HEADSET": ("MediaTek / MT6637 FM", "fmloader/connsys loader", "FM receiver"),
        "NFC-SECURE-ELEMENT": ("STMicroelectronics / ST21NFC", "STFlashTool/NFC HAL", "NFC controller"),
        "MT6637-WIFI": ("MediaTek / MT6637 Wi-Fi", "conninfra/Wi-Fi firmware loader", "Wi-Fi controller"),
        "CONNINFRA-KERNEL": ("MediaTek / connsys", "wmt_loader/conninfra", "connectivity coprocessor"),
        "CAMERA-HAL-ISP": ("MediaTek/OEM camera tuning", "camera HAL + CCU loader", "ISP/CCU/image sensors"),
        BLOB: ("ARM/MediaTek vendor", "vendor graphics/media driver", "GPU/display/media block"),
        'MALI-GPU-KERNEL': ('ARM/MediaTek', 'Kbase CSF firmware request/loading interface', 'GPU CSF; algorithms excluded'),
        'APUSYS-NPU-KERNEL': ('MediaTek', 'APU host remoteproc/boot interface; exact signed-image loading provenance to trace', 'APU algorithms excluded'),
        'GPU-AI-AUX-KERNEL-INTERFACES': ('MediaTek', 'GPUEB/VCP host and boot-chain interface; mechanism per processor, not universal request_firmware', 'GPUEB/VCP algorithms excluded'),
        "MODEM-FIRMWARE": ("MediaTek/OEM modem", "preloader/CCCI modem loader", "MD1 baseband"),
        "GNSS": ("MediaTek / connsys GNSS", "GNSS/connsys loader", "GNSS coprocessor"),
        "GZ-TRANSPORT": ("MediaTek / GenieZone", "bootloader/hypervisor loader", "GenieZone secure world"),
        "TRUSTKERNEL-TEE": ("TrustKernel/MediaTek", "bootloader secure-image loader", "TEE/secure world"),
        "DRAM-MEMORY": ("MediaTek/OEM boot chain", "BootROM/preloader", "DRAM controller/training"),
        "DTB-DTBO": ("OEM/AOSP build", "bootloader", "Linux kernel device tree"),
        "AVB-SIGNING-CHAIN": ("OEM build/signing keys", "AVB boot verifier", "boot-chain partitions"),
        "BOOT-IMAGES": ("OEM/AOSP build", "bootloader", "Linux kernel/ramdisks"),
        "AB-SUPER-GEOMETRY": ("OEM/AOSP build", "dynamic partition loader", "logical partitions"),
        "KEYSTORE-VOLD-KEYMINT": ("per-device Android install", "vold/keystore", "userdata FBE"),
        GEN: ("MediaTek platform", "platform remoteproc/boot loader", "MT6878 auxiliary processor"),
        "PARTITION-OWNERSHIP": ("OEM boot chain", "bootloader", "boot/branding payload"),
    }
    return parties.get(component, ("UNKNOWN", "UNKNOWN", basename))


# --------------------------------------------------------------------------
# axis 4a: exact VINTF interface family -> (component, coverage, subsystem, why)
# --------------------------------------------------------------------------
VINTF_EXACT: dict[str, tuple[str, str, str, str]] = {
    "vendor.yft.hardware.changenode": ("REAR-RUGGED-FEATURES", "A", "Board glue",
        "YFT change-node factory service; declared in sensorcali_manifest/CommandService.xml"),
    "vendor.yft.hardware.gesturewake": ("YFT-TPD-GESTURE", "A", "Input",
        "YFT wake-gesture HAL over the TPD touch gesture kernel path"),
    "vendor.yft.hardware.obtainvendor": ("YFT-DEVINFO", "A", "Board glue",
        "YFT vendor-info retrieval HAL over the YFT registry sysfs/procfs nodes"),
    "vendor.yft.hardware.tinylcd": ("CO5300-REAR-DISPLAY", "A", "Display",
        "rear mini-LCD control HAL: declared 1.0 service implements @1.2"),
    "vendor.yft.hardware.sensorcali": ("NVRAM-CALIBRATION", "A", "Calibration",
        "YFT sensor-calibration HAL v1+v2 - the factory calibration door"),
    "android.system.net.netd": (GEN, "C", "Framework", "AOSP netd client declaration"),
    "android.system.suspend": ("THERMAL-POWER-HAL", "B", "Power",
        "system-suspend service: suspend/resume behaviour rides the power/thermal scope"),
    "android.hidl.allocator": (GEN, "C", "Framework", "hidl_memory allocator service"),
    "android.frameworks.cameraservice": ("CAMERA-HAL-ISP", "B", "Camera",
        "framework camera-service client declaration"),
    "vendor.mediatek.version-info": ("PARTITION-OWNERSHIP", "A", "Identity",
        "MTK platform version-info HAL: the platform-version contract used by VINTF"),
    "vendor.mediatek.camera.ldchr": ("CAMERA-HAL-ISP", "B", "Camera", "MTK LDCHDR camera hook"),
    "vendor.mediatek.camera.infra": ("CAMERA-HAL-ISP", "B", "Camera", "MTK camera infra HAL"),
    "vendor.mediatek.hardware.pq_aidl": ("VENDOR-BLOB-HAL-INVENTORY", "B", "Display",
        "MTK PQ picture-quality AIDL HAL sits behind the closed display stack"),
    "vendor.mediatek.hardware.apusys_para": ('APUSYS-NPU-KERNEL', 'B', 'NPU',
        'Proprietary APUSYS consumer; normal-world kernel interface owner now registered, execution unproved'),
    "vendor.vthal.cardApplet": ("NFC-SECURE-ELEMENT", "B", "Secure element",
        "vTuner applet client of the eSE/UICC scope"),
    "vendor.vt.eid": ("ESIM-EUICC-ABSENCE", "A", "Secure element",
        "vTuner eUICC EID service: the evidence basis for the eSIM-absence finding"),
    "vendor.oplus.hardware.fp": ("MADEV-FINGERPRINT", "B", "Fingerprint",
        "vendor fingerprint extension service"),
    "netutils-wrapper": (GEN, "C", "Framework", "AOSP netutils wrapper service"),
    "vendor.mediatek.framework.mtksf_ext": (BLOB, "B", "Graphics",
        "SurfaceFlinger extension owned by the vendor blob/HAL inventory"),
    "vendor.mediatek.hardware.apmonitor": (GEN, "C", "Performance", "MTK platform application monitor"),
    "vendor.mediatek.hardware.avm": (GEN, "C", "Performance", "MTK platform adaptive-voltage monitor"),
    "vendor.mediatek.hardware.clientapi": (BLOB, "B", "Graphics", "MTK multimedia client API"),
    "vendor.mediatek.hardware.composer_ext": (BLOB, "B", "Graphics", "MTK composer extension"),
    "vendor.mediatek.hardware.dfps": (BLOB, "B", "Graphics", "MTK dynamic frame-rate extension"),
    "vendor.mediatek.hardware.dmc": (GEN, "C", "Performance", "MTK dynamic memory-control platform service"),
    "vendor.mediatek.hardware.dplanner": (BLOB, "B", "Graphics", "MTK display planner"),
    "vendor.mediatek.hardware.dplanner2": (BLOB, "B", "Graphics", "MTK display planner v2"),
    "vendor.mediatek.hardware.gnss": ("GNSS", "B", "GNSS", "MTK GNSS extension"),
    "vendor.mediatek.hardware.gnss.batching": ("GNSS", "B", "GNSS", "MTK GNSS batching extension"),
    "vendor.mediatek.hardware.gpu": ('MALI-GPU-KERNEL', 'B', 'Graphics',
        'Proprietary GPU HAL; registered normal-world GPU kernel-facing boundary'),
    "vendor.mediatek.hardware.gpuserv": ('MALI-GPU-KERNEL', 'B', 'Graphics',
        'Proprietary GPU service; registered normal-world GPU platform boundary'),
    "vendor.mediatek.hardware.imsa": ("IMS", "B", "Modem", "MTK IMS extension"),
    "vendor.mediatek.hardware.keymanage": ("KEYSTORE-VOLD-KEYMINT", "B", "Security", "TEE-backed key management"),
    "vendor.mediatek.hardware.keymaster_attestation": ("KEYSTORE-VOLD-KEYMINT", "B", "Security",
        "TEE-backed key attestation"),
    "vendor.mediatek.hardware.lbs": ("GNSS", "B", "GNSS", "MTK location extension"),
    "vendor.mediatek.hardware.mms": (BLOB, "B", "Media", "MTK multimedia service extension"),
    "vendor.mediatek.hardware.mtkcodecservice": (GEN, "C", "Media", "MTK platform codec service"),
    "vendor.mediatek.hardware.nwk_opt": ("RADIO-HAL-RIL", "B", "Modem", "MTK network optimizer"),
    "vendor.mediatek.hardware.nwk_opt_new": ("RADIO-HAL-RIL", "B", "Modem", "MTK network optimizer v2"),
    "vendor.mediatek.hardware.power": ("THERMAL-POWER-HAL", "B", "Power", "MTK power extension"),
    "vendor.mediatek.hardware.pplagent": ("KEYSTORE-VOLD-KEYMINT", "B", "Security", "privacy/protection-lock agent"),
    "vendor.mediatek.hardware.presence": ("IMS", "B", "Modem", "RCS presence service"),
    "vendor.mediatek.hardware.rcs": ("IMS", "B", "Modem", "RCS service"),
    "vendor.mediatek.hardware.sfs": ("TRUSTKERNEL-TEE", "B", "Security", "secure-file-system client"),
    "vendor.mediatek.hardware.thp": ("THERMAL-POWER-HAL", "B", "Power", "thermal-headroom predictor"),
    "vendor.mediatek.hardware.touchll": ("FT3680-TOUCH", "B", "Input", "touch low-latency extension"),
    "vendor.tesiai.hardware.hdcpconnection": ("MEDIATEK-DRM", "B", "DRM", "HDCP connection service"),
    "vendor.tsa.hdcp": ("MEDIATEK-DRM", "B", "DRM", "HDCP service"),
}

# ordered family rules: (regex, component, coverage, subsystem)
VINTF_RULES: list[tuple[str, str, str, str]] = [
    (r"^vendor\.yft\.hardware\.", "REAR-RUGGED-FEATURES", "A", "Board glue"),
    (r"thermal|ThermalSvc|ThermalManager", "THERMAL-POWER-HAL", "A", "Power"),
    (r"^android\.hardware\.power|mtkpower|MtkOptModePowerHAL|IPowerManager|perflock|perfinstance"
     r"|perfservice|mtkperf|powerjinni|mtkpowerservice", "THERMAL-POWER-HAL", "B", "Power"),
    (r"\blights?\b|ILights|lightservice|batt_led|rgb_led", "AW2013-RGB-LED", "A", "Display"),
    (r"vibrat", "HAPTICS", "B", "Input"),
    (r"fingerprint|fpc_|fptool|microarray|swfingerprint|btlfp|biometrics\.face|\bface\b",
     "MADEV-FINGERPRINT", "A", "Fingerprint"),
    (r"cameracore|mtkcam|camsys|imgsys|isphal|rawhdr|senior|vrp\.|p1core|atms|\bBG\b|camera"
     r"|vencseg|mtkpower\.camsync|lib3a|ccuservice|mhal", "CAMERA-HAL-ISP", "A", "Camera"),
    (r"^android\.hardware\.ir|consumerir|iraudiosync|\birm\w*", "IR-BLASTER", "A", "Input"),
    (r"\bnfc\b|st21nfc|se1nfc", "NFC-SECURE-ELEMENT", "A", "NFC"),
    (r"secure_element|snbero|\bweaver\b|\beid\b|cardApplet|vtuner", "NFC-SECURE-ELEMENT", "B", "Secure element"),
    (r"^android\.hardware\.wifi|wlan|hostapd|supplicant|^\Q" + V + r"wifi", "MT6637-WIFI", "A", "Connectivity"),
    (r"^android\.hardware\.bluetooth|btpcmchar|btlpmhal|btmclo|bthfp|btsco|btdm|fm_hfp|btif_client"
     r"|stauth|stp_for", "BLUETOOTH", "B", "Connectivity"),
    (r"conninfra|connsys|\bfm_|fmradio|wmt|cfg80211", "CONNINFRA-KERNEL", "B", "Connectivity"),
    (r"gps|gpsbed|agps|mnld|\bflp\b|geofence|mtk_lbs|lbs_dbg", "GNSS", "B", "GNSS"),
    (r"apuware|apusys|apudla|neuropilot|neurontranslator|neuralnetworks|\bsnpe\b|mbrain|nps\.nos"
     r"|\bvpu\b|tee_trm", GEN, "C", "NPU"),
    (r"^\Q" + V + r"sensor|sensorcali|\bssc\b|sensor_service|sensorlog|\bem_svr\b", "SENSOR-HUB", "B", "Sensors"),
    (r"^android\.hardware\.sensors", "SENSOR-HUB", "B", "Sensors"),
    (r"pgsyshostaux|\bpgs\b|gesture|touch_boost|tpd_launch", "FT3680-TOUCH", "B", "Input"),
    (r"tunnel\.mtk|snapshot|IMergeSession", "OTA-AB-UPDATE", "A", "Boot"),
    (r"bootctl|bootcontrol|mtkbootctl", "BOOT-CONTROL-SLOTS", "A", "Boot"),
    (r"^\Q" + V + r"gz|gzmachtype|gz_tee|trusty|trustonic", "GZ-TRANSPORT", "A", "Security"),
    (r"trustkernel|gatein|gkinfo|kapass|\bagp\b|dtbcmdl|dmabftd|hiftime|kbpb|sys_fac_dmr"
     r"|mstat|auid|gpueb|teecontroller|content security|optee|fingerprintTA", "TRUSTKERNEL-TEE", "B", "Security"),
    (r"\bims\b|vt_service|mtk-ims|vtctl|mimservice", "IMS", "B", "Modem"),
    (r"radio|mtkradioex|MtkRtc|vlw|wsim|sa_?wolf|apusys_config|\batci\b|rild|carrierconfig"
     r"|volte|\bsms\b", "RADIO-HAL-RIL", "B", "Modem"),
    (r"ccci|mdmonitor|md_monitor|meta_tst|wpax|cmcc_md|operator", "MODEM-KERNEL-TRANSPORT", "B", "Modem"),
    (r"^\Q" + V + r"nvram|nvram_daemon|nvm_", "NVRAM-CALIBRATION", "A", "Calibration"),
    (r"gatekeeper|keybox|keystore|rebootescrow", "KEYSTORE-VOLD-KEYMINT", "B", "Security"),
    (r"^\Q" + V + r"otsp|optrusty|IRemotableAuthProxy|\btee\b", "TRUSTKERNEL-TEE", "B", "Security"),
    (r"^\Q" + V + r"aee|^\Q" + V + r"log|mobilelog|mobile_log|pmsg|dmesgd|dumpstate|halsys"
     r"|mipc|mums|netdagent|\bpnm\b|mmsl|\bscl\b|mtkmbip|dmc_core|mtksys|aurisys|mcupm|sspm"
     r"|\bccu\b|\bdpm\b|logging service|kernel\_dmesg", GEN, "C", "Logging"),
    (r"engineermode|factory|meta_|stfolder|flashinfo|permission_check|\bemi\b", "VENDOR-BLOB-HAL-INVENTORY", "B", "Factory"),
    (r"storageproxy|^\Q" + V + r"storage", "UFS-STORAGE", "B", "Storage"),
    (r"audio|hififace|wavesink|wavesource|audiodsp|\bafe\b|soundtrigger|smartpa|audiopolicy", "AUDIO-DSP", "A", "Audio"),
    (r"^android\.hardware\.media|codec2|\bc2-|media\.c2|mmagent|mmlpq|gpud|vcodec|videotelephony"
     r"|mtk_vt|heapprofd|memtrack|weaver$", GEN, "C", "Media"),
    (r"display|hwcomposer|graphics|mapper|vulkan|mali|pq\b|hwcifmw|osip|mmlayer|hdmi|drmservice"
     r"|^\Q" + V + r"mmsla|mtkrrp", BLOB, "B", "Graphics"),
    (r"^android\.hardware\.authsecret|^android\.hardware\.cas|drm|^\Q" + V + r"drm", "MEDIATEK-DRM", "B", "DRM"),
    (r"health|batterywarning|bmtf|batterysaver|mtkbattery|fuelgauge", "THERMAL-POWER-HAL", "B", "Power"),
    (r"usb|typec|usbc", "USB-TYPEC", "B", "USB"),
    (r"gateway|radioauto\w*", "RADIO-HAL-RIL", "B", "Modem"),
]


def classify_vintf(iface: str) -> tuple[str, str, str, str]:
    if iface in VINTF_EXACT:
        return VINTF_EXACT[iface]
    for pat, comp, cov, dom in VINTF_RULES:
        if re.search(pat.replace("\\Q", "").replace("\\E", ""), iface):
            return comp, cov, dom, f"family rule `{pat[:80]}`"
    if iface.startswith(("android.", "android.system.")):
        return (GEN, "C", "Framework", "AOSP-side declaration with no device-specific scope")
    return ("UNKNOWN", "E", "Unclassified", "no RE component claims this interface")


# --------------------------------------------------------------------------
# axis 4b: legacy android.hardware.* backend libraries
# --------------------------------------------------------------------------
HW_RULES: list[tuple[str, str, str, str]] = [
    (r"^audio\.primary\.(mt6878|mediatek)\.so$|^audio\.r_submix\.(mt6878|mediatek)\.so$"
     r"|^awinic\.audio\.effect\.so$|^vendor\.mediatek\.hardware\.audio-impl\.so$",
     "AUDIO-DSP", "A", "Audio"),
    (r"^android\.hardware\.audio|^android\.hardware\.soundtrigger|^audio\.primary\.(mt6878|mediatek)"
     r"|^audio\.r_submix\.(mt6878|mediatek)|^awinic\.audio\.effect", "AUDIO-DSP", "A", "Audio"),
    (r"^audio\.|^audio_policy\.stub|^sound_trigger\.primary", GEN, "C", "Audio"),
    (r"bluetooth", "BLUETOOTH", "B", "Connectivity"),
    (r"camera|atms|bgservice|isphal|provider@2\.6", "CAMERA-HAL-ISP", "A", "Camera"),
    (r"gnss|^gps\.default|local_time|mtkflp|mtkgeofence", "GNSS", "B", "GNSS"),
    (r"sensors", "SENSOR-HUB", "B", "Sensors"),
    (r"gralloc|mapper|allocator|hwcomposer|vulkan|pq_aidl|renderscript", BLOB, "B", "Graphics"),
    (r"microarray|fpc|fptool|fingerprint", "MADEV-FINGERPRINT", "A", "Fingerprint"),
    (r"^face\.default\.so$", "MADEV-FINGERPRINT", "D", "Fingerprint"),
    (r"^change_node\.", "REAR-RUGGED-FEATURES", "A", "Board glue"),
    (r"^gesturewake\.", "YFT-TPD-GESTURE", "A", "Input"),
    (r"^tinylcd\.", "CO5300-REAR-DISPLAY", "A", "Display"),
    (r"thermal|^power\.default|mtkpower", "THERMAL-POWER-HAL", "B", "Power"),
    (r"vibrator", "HAPTICS", "B", "Input"),
    (r"consumerir", "IR-BLASTER", "A", "Input"),
    (r"nvram", "NVRAM-CALIBRATION", "A", "Calibration"),
    (r"videotelephony", "IMS", "B", "Modem"),
]


def classify_hw(lib: str) -> tuple[str, str, str, str]:
    for pat, comp, cov, dom in HW_RULES:
        if re.search(pat, lib):
            return comp, cov, dom, f"library family rule `{pat[:70]}`"
    return ("UNKNOWN", "E", "Unclassified", "no RE component claims this HAL backend library")


# --------------------------------------------------------------------------
# axis 5: init services / trigger executables
# --------------------------------------------------------------------------
SERVICE_EXACT: dict[str, tuple[str, str, str, str]] = {
    "camerahalserver": ("CAMERA-HAL-ISP", "A", "Camera",
        "MTK camera HAL provider process: the whole ISP/3A/p2g user pipeline lives behind it"),
    "cameradeployd": ("CAMERA-HAL-ISP", "B", "Camera", "vendor camera helper daemon"),
    "camerahaltest_p1": ("CAMERA-HAL-ISP", "D", "Camera",
        "camera P1 bring-up self-test service still enabled on a production image"),
    "ylog_lite": (GEN, "C", "Logging", "vendor log-collection agent"),
    "gpud": (GEN, "C", "Media", "vendor GPU/video governor daemon"),
    "akmd8963": ("ICM4N607-IMU", "D", "Sensors",
        "AKM8963 compass service is still shipped and enabled while the documented IMU is TDK ICM4N603: "
        "stale vendor userspace carried from a reference board"),
    "virtual_camera": ("CAMERA-HAL-ISP", "D", "Camera",
        "AOSP virtual-camera example service still enabled on a production image"),
    "btlfpserver": ("MADEV-FINGERPRINT", "B", "Fingerprint",
        "fourth fingerprint service in init.fingerprint.rc; provider identity unverified"),
    "mtk_storageproxyd": ("UFS-STORAGE", "B", "Storage",
        "storage proxy daemon launched against /dev/trusty-ipc-dev0 (secure storage path)"),
    "meta_tst": ("MODEM-KERNEL-TRANSPORT", "B", "Modem",
        "META-mode test server over the modem transport; production applicability unverified"),
    "permission_check": ("VENDOR-BLOB-HAL-INVENTORY", "B", "Factory",
        "factory/META-mode permission gate daemon; production applicability unverified"),
    "factory_no_image": ("VENDOR-BLOB-HAL-INVENTORY", "B", "Factory",
        "factory-mode calibration image stub; production applicability unverified"),
    "eara-io": (GEN, "C", "Media", "vendor EAR-A I/O service (display/video pipeline helper)"),
    "dmc_core": (GEN, "C", "Power", "vendor DVFS/memory-clock control agent"),
    "gbe": (GEN, "C", "Performance", "vendor GPU-boost engine"),
    "magt": (GEN, "C", "Performance", "vendor MATE performance collector"),
    "osi": (GEN, "C", "Performance", "vendor MTK OSI (online scheduling) perf agent"),
    "usp_service": (GEN, "C", "Performance", "vendor unified scheduling policy daemon"),
    "bip_ap": (GEN, "C", "Performance", "vendor boot-time IPAP perf tuner"),
    "frs": (BLOB, "B", "Factory", "factory reset switch daemon declared by init.frs.rc; no dedicated component owns it"),
    "kpoc_charger": ("MT6375-CHARGER", "B", "Power", "system_ext charging daemon on top of the MT6375/SC85xx kernel stack"),
    "fuelgauged": ("SH366003-FUEL-GAUGE", "B", "Power", "MTK fuel-gauge user daemon"),
    "fuelgauged_nvram": ("NVRAM-CALIBRATION", "B", "Calibration", "battery-profile NVRAM agent"),
    "charger": ("THERMAL-POWER-HAL", "B", "Power", "recovery charging UI service"),
    "msensord": ("SENSOR-HUB", "B", "Sensors", "MTK sensor hub daemon over the tinysys IPI transport"),
    "slog_test": ("SENSOR-HUB", "D", "Sensors", "sensor logging self-test service: diagnostic, not a product path"),
    "akmd": ("ICM4N607-IMU", "D", "Sensors", "AKM compass daemon variant shipped for the same reference-board path"),
    "agpsd": ("GNSS", "B", "GNSS", "AGPS/RILP agent (closed binary)"),
    "mnld": ("GNSS", "B", "GNSS", "MTK network-location daemon"),
    "gnss_daemon": ("GNSS", "B", "GNSS", "GNSS driver daemon for the FMSS/ulp path"),
    "uart_launcher": ("CONNINFRA-KERNEL", "B", "Connectivity", "connsys UART HCI launcher (BT/FM over /dev/ttyS*)"),
    "fmloader": ("FM-RADIO-HEADSET", "B", "Connectivity", "connsys FM firmware loader"),
    "fmsvtlp_svc": ("FM-RADIO-HEADSET", "B", "Connectivity", "FM service-loopback pairing test service"),
    "wmt_loader": ("CONNINFRA-KERNEL", "B", "Connectivity", "connsys MT66xx download + platform_init.sh launcher"),
    "fuse_usbotg": ("EXTERNAL-USB", "B", "USB", "USB-OTG mass-storage FUSE bridge (usbotg.sh)"),
    "btsrvr": ("BLUETOOTH", "B", "Connectivity", "connsys BT server launcher"),
    "gps_irda_loader": ("IR-BLASTER", "B", "Input", "connsys IR/IRDA download service"),
    "insmod_sh": ("INIT-INSMOD", "A", "Boot", "init.insmod.${ro.hardware}.cfg module loader"),
    "insmod_pstore_blk": ("UFS-STORAGE", "B", "Storage", "boot-time pstore/blk setup helper"),
    "vold": ("KEYSTORE-VOLD-KEYMINT", "B", "Security", "adoptable-storage/encryption volume daemon"),
    "gatekeeperd": ("KEYSTORE-VOLD-KEYMINT", "B", "Security", "gatekeeper daemon riding the keymaster path"),
    "tee_check_keybox": ("TRUSTKERNEL-TEE", "B", "Security", "normal-world TEE client"),
    "chipinfo": ("PARTITION-OWNERSHIP", "B", "Boot", "chipinfo: the SoC/board identity reader feeding ro.boot.* props"),
    "mtk_plpath_utils": ("DTB-DTBO", "B", "Storage", "peripheral path resolution helper used by storage/sdcard policy"),
    "blank_screen": (GEN, "C", "Display", "AOSP blank-screen surfaceflinger helper"),
    "batterywarning": (GEN, "C", "Power", "AOSP/MTK low-battery boot-animation text helper"),
    "android-hardware-media-c2-hal-1-2": (GEN, "C", "Media", "generic MTK Codec2 HAL service"),
    "bluetooth-1-1": ("BLUETOOTH", "B", "Connectivity", "legacy MTK Bluetooth HIDL service"),
    "bluetooth_hal_service": ("BLUETOOTH", "B", "Connectivity", "MTK Bluetooth AIDL service"),
    "changenode_hal": ("REAR-RUGGED-FEATURES", "A", "Board glue", "YFT change-node HAL"),
    "emhal_user": (BLOB, "B", "Factory", "MTK engineering-mode HAL"),
    "emsvr_user": (BLOB, "B", "Factory", "MTK engineering-mode server"),
    "gesturewake_hal": ("YFT-TPD-GESTURE", "A", "Input", "YFT wake-gesture HAL"),
    "ipsec_mon": ("RADIO-HAL-RIL", "B", "Modem", "vendor IPsec/telephony monitor"),
    "md_monitor": ("MODEM-KERNEL-TRANSPORT", "B", "Modem", "modem state monitor"),
    "mtk.plpath.utils.link": ("DTB-DTBO", "B", "Storage", "MTK peripheral-path resolver"),
    "mtk_secure_element_hal_service": ("NFC-SECURE-ELEMENT", "B", "NFC", "MTK secure-element HAL"),
    "neuralnetworks_hal_service_shim_mtk": (GEN, "C", "NPU", "generic MTK Neural Networks shim"),
    "nfc_hal_service": ("NFC-SECURE-ELEMENT", "A", "NFC", "ST NFC HAL service"),
    "nvram-aidl": ("NVRAM-CALIBRATION", "A", "Calibration", "MTK NVRAM AIDL service"),
    "nvram_daemon": ("NVRAM-CALIBRATION", "A", "Calibration", "MTK NVRAM daemon"),
    "obtainvendor_hal": ("YFT-DEVINFO", "A", "Board glue", "YFT board/vendor identity HAL"),
    "rss_hwm_reset": (GEN, "C", "Framework", "AOSP resident-set high-water reset helper"),
    "stflashtool": ("NFC-SECURE-ELEMENT", "B", "NFC", "ST controller firmware flash tool"),
    "system_suspend": ("THERMAL-POWER-HAL", "B", "Power", "AOSP suspend service with MTK hooks"),
    "tetheroffloadservice": (GEN, "C", "Connectivity", "standard tether-offload HAL service"),
    "tinylcd_hal": ("CO5300-REAR-DISPLAY", "A", "Display", "YFT rear-display HAL"),
    "touch_boost": ("FT3680-TOUCH", "B", "Input", "MTK touch performance booster"),
    "ueventd": (GEN, "C", "Framework", "AOSP uevent device-node manager"),
    "vender.mediatek.hardware.pq_aidl-default": (BLOB, "B", "Graphics", "MTK picture-quality HAL"),
    "vendor.audio-hal": ("AUDIO-DSP", "A", "Audio", "MTK audio HAL service"),
    "vendor.bip_ap": (GEN, "C", "Performance", "MTK boot-time performance agent"),
    "vendor.boot-default": ("BOOT-CONTROL-SLOTS", "B", "Boot", "MTK boot-control HAL"),
    "vendor.cas-default": (GEN, "C", "DRM", "AOSP example CAS service; no board-specific RE"),
    "vendor.drm-clearkey-service": (GEN, "C", "DRM", "AOSP ClearKey reference service"),
    "vendor.face-default": ("MADEV-FINGERPRINT", "D", "Fingerprint", "AOSP face example service; no matching face hardware"),
    "vendor.gatekeeper": ("KEYSTORE-VOLD-KEYMINT", "B", "Security", "TrustKernel-backed gatekeeper HAL"),
    "vendor.gnss-default": ("GNSS", "B", "GNSS", "MTK GNSS HAL"),
    "vendor.gpuserv-default": ('MALI-GPU-KERNEL', 'B', 'Graphics', 'Proprietary service; registered GPU kernel-facing boundary'),
    "vendor.gralloc-v1": (BLOB, "B", "Graphics", "MTK gralloc allocator service v1"),
    "vendor.gralloc-v2": (BLOB, "B", "Graphics", "MTK gralloc allocator service v2"),
    "vendor.health-default": ("THERMAL-POWER-HAL", "B", "Power", "health/battery HAL integration"),
    "vendor.hwcomposer-3-2": (BLOB, "B", "Graphics", "MTK hardware-composer service"),
    "vendor.ir-default": ("IR-BLASTER", "B", "Input", "consumer-IR HAL service"),
    "vendor.keymint-3-0-trustkernel": ("KEYSTORE-VOLD-KEYMINT", "B", "Security", "TrustKernel KeyMint service"),
    "vendor.light-default": ("AW2013-RGB-LED", "B", "Display", "MTK lights HAL over board LED drivers"),
    "vendor.mali_platform-mediatek": ('MALI-GPU-KERNEL', 'B', 'Graphics', 'Proprietary service; registered Mali platform ABI boundary'),
    "vendor.mediatek.hardware.mmagent-default": (GEN, "C", "Media", "MTK multimedia memory agent"),
    "vendor.memtrack-default": (GEN, "C", "Graphics", "standard MTK memtrack HAL"),
    "vendor.mmlpq-default": (BLOB, "B", "Graphics", "MTK MML picture-quality HAL"),
    "vendor.mtkgnss-service": ("GNSS", "B", "GNSS", "MTK GNSS vendor extension service"),
    "vendor.mtkpower-service.mediatek": ("THERMAL-POWER-HAL", "B", "Power", "MTK power HAL"),
    "vendor.mtkpower_applist-default": ("THERMAL-POWER-HAL", "B", "Power", "MTK power application-list service"),
    "vendor.sensors-hal-multihal": ("SENSOR-HUB", "B", "Sensors", "Android Sensors multi-HAL over SCP sensorhub"),
    "vendor.usb_default": ("USB-TYPEC", "B", "USB", "MTK USB HAL"),
    "vendor.usb_gadget_default": ("USB-TYPEC", "B", "USB", "MTK USB gadget HAL"),
    "vendor.vibrator-default": ("HAPTICS", "B", "Input", "MTK vibrator HAL"),
    "vendor.wifi_hal_legacy": ("MT6637-WIFI", "B", "Connectivity", "legacy Wi-Fi HAL service"),
    "vndservicemanager": (GEN, "C", "Framework", "standard vendor binder service manager"),
    "wificond": (GEN, "C", "Connectivity", "AOSP Wi-Fi control daemon"),
    "zygote": (GEN, "C", "Framework", "AOSP runtime process launcher"),
    "zygote_HBT": (GEN, "C", "Framework", "MTK/HBT binary-translation zygote"),
    "[exec] e2fsck": (GEN, "C", "Storage", "standard ext-filesystem checker invoked by init"),
    "[exec] tune2fs": (GEN, "C", "Storage", "standard ext-filesystem feature tuner invoked by init"),
    "[exec] killall": (GEN, "C", "Framework", "standard process-control helper invoked by init"),
    "[exec] chattr": (GEN, "C", "Storage", "standard filesystem attribute helper invoked by init"),
    "[exec] linkerconfig": (GEN, "C", "Framework", "AOSP linker namespace/configuration generator"),
    "[exec] preloads_copy.sh": (GEN, "C", "Framework", "AOSP runtime preload-copy helper"),
    "[exec] rm": (GEN, "C", "Framework", "standard file-removal helper invoked by init"),
    "[exec] tzdatacheck": (GEN, "C", "Framework", "AOSP timezone-data validation helper"),
}

SERVICE_RULES: list[tuple[str, str, str, str, str]] = [
    (r"^(fingerprint|fpc_|fptool|goodix_|fingeprint_|swfpserv|swfingerprint|microarray|gt11pm"
     r"|vendor\.fingerprint|btlfp|face\.)|fingerprint", "MADEV-FINGERPRINT", "B", "Fingerprint",
     "stock fingerprint HAL service (several providers coexist; only one can be live)"),
    (r"^(thermal|hifthermal|mtkTpdLaunch|mtkPowerScript|powerperfservice|powerjinni|thermal_core"
     r"|thermal_manager|thermald|kpoc_|charger|healthd|batt|mtkpower|vdecision|perfservic)"
     r"|thermal|powerhal", "THERMAL-POWER-HAL", "B", "Power",
     "thermal/power userspace policy engine or charging helper"),
    (r"^(ccci|mdlogger|emdlogger|dualmdlogger|atcid|mtkfusionrild|rild|audio-daemon"
     r"|audio_parameter_parser|muxreport|wpax_test|carrier_config|volte_|vtservice|mdnsd"
     r"|netdagent|ril-daemon)", "RADIO-HAL-RIL", "B", "Modem",
     "modem-side daemon riding the CCCI transport and vendor RIL"),
    (r"^(agpsd|mnld|gnss|lbs_dbg|gps_dump|mtk_lbs|halzoo|slpd)", "GNSS", "B", "GNSS",
     "GNSS/agps userspace agent"),
    (r"^(wlan_|wpa_supplicant|hostapd|conninfra|connsyslogger|bt_dump|wifi_dump|stp|wmt_|mcupm"
     r"|btpcmchar|btlfs_server|stauth)", "CONNINFRA-KERNEL", "B", "Connectivity",
     "connsys loader / supplicant glue over the closed connectivity stack"),
    (r"^(sens|sensor|ssc|slog_test|haptic|msensor)", "SENSOR-HUB", "B", "Sensors",
     "MTK/YFT sensor daemon family"),
    (r"^(camera|mtkcam|camerad|vencseg|vtm|mtk-hdmi-cecf|mtksharedpybind|m4u)", "CAMERA-HAL-ISP", "B", "Camera",
     "vendor camera/CEC service"),
    (r"^(tee|gkinfo|terservice|rpmbd|keylibd|mtk_pkm|provisionx|mbra|spdaemon|prems|tst_keyb"
     r"|teec|drmservice|keyboxd|widevine)", "TRUSTKERNEL-TEE", "B", "Security",
     "normal-world TEE / secure-storage client (TA side unverified)"),
    (r"^(update_engine|update_verifier|snapuserd|uncrypt|(setup|clear)-bcb|cppreopts|postinstall"
     r"|otapreopt_slot|snapshotctl|vdc|gsid|derive_|art_boot|flags_health_check|fsverity_init"
     r"|recovery-persist|bootstat)", "OTA-AB-UPDATE", "B", "Boot",
     "A/B update, snapshot and dynamic-partition boot plumbing"),
    (r"(modprobe|insmod|pstore|bootanim|banim|bootlogo|init\.|chipinfo|kernel_panic|kpanic"
     r"|fec_codec|spm_|bootperf|ddr|kud)" , "ANDROID-INIT", "B", "Boot",
     "boot-path init script or first-stage module/clock helper"),
    (r"^(aconfigd|adbd|apexd|boringssl_self_test|bpfloader|bugreport|dumpstate|dmesgd|credstore"
     r"|drm$|drmserver|heapprofd|traced|perfetto|boottrace|stopboottracetrigger|categories"
     r"|simpleperf|hidl_memory|hwservicemanager|idmap2d|incidentd|installd|keystore|llkd|lmkd"
     r"|logd|lpdumpd|media|audioserver|mediametrics|mediaextractor|misctrl|mm_events|mobile_log_d"
     r"|netd|odsign|prng_seeder|servicemanager|stats|storaged|surfaceflinger|tombstoned|uprobestats"
     r"|usbd|virtualizationservice|vrp-|mtectrl|kcmdlinectrl|extra_free_kbytes|partition_permission"
     r"|loghidl|console|sh$|exec$|bootstrap|wait_for_keymaster|aee|anrdump|aeedump|aeev"
     r"|bsplogstart|cplogstart|connsyslogger|trace_buf_off|bt_dump|gps_dump|dmesg)"
     r"|^aee|apexd-|logd-|llkd-|heapprofd_|aconfigd-|^media[36]$|^media$|helper", GEN, "C", "Framework",
     "AOSP/system-side service or vendor log-dump infrastructure: no board-specific behaviour to RE"),
    (r"^(fpsgo|gpu$|gpuservice|mtkpower_|dmd|md_aee|gpshosted|mobile_log)", GEN, "C", "Performance",
     "vendor performance/logging engine with no dedicated device RE component"),
]


def classify_service(svc: str, exes: str) -> tuple[str, str, str, str]:
    if svc in SERVICE_EXACT:
        return SERVICE_EXACT[svc]
    base = exes.split(" ")[0].split("/")[-1] if exes else ""
    for pat, comp, cov, dom, note in SERVICE_RULES:
        if re.search(pat, svc) or (base and re.search(pat, base)):
            return comp, cov, dom, f"{note} (rule `{pat[:60]}`)"
    return ("UNKNOWN", "E", "Unclassified", "no RE component claims this service")


# --------------------------------------------------------------------------
# axis 6: firmware / calibration payloads
# --------------------------------------------------------------------------
FW_RULES: list[tuple[str, str, str, str, str, str]] = [
    (r"^aw883xx_acf\.bin$|^awinic_|^AW_DSP\.bin$", "AW883XX-SPEAKER-AMP", "A", "BINARY-ONLY", "Audio",
     "Awinic smart-amp DSP/param payloads consumed by aw883xx_driver"),
    (r"^BT_FW\.cfg$|^soc7_0_ram_bt", "BLUETOOTH", "A", "SIGNED-BINARY", "Connectivity",
     "connsys BT RAM firmware + cfg"),
    (r"^soc7_0_ram_mcu|^remoteproc_scp$", "SENSOR-HUB", "B", "SIGNED-BINARY", "Sensors",
     "connsys MCU (Wi-Fi/BT/GNSS coprocessor) RAM code loaded through the tinysys IPI transport"),
    (r"^fm_cust|^mt66[0-9]{2}_fm|^soc_fm", "FM-RADIO-HEADSET", "A", "BINARY-ONLY", "Connectivity",
     "FM receiver patch/coeff for the mt66xx FM family"),
    (r"^st21nfc_fw", "NFC-SECURE-ELEMENT", "A", "SIGNED-BINARY", "NFC", "ST21NFC controller firmware"),
    (r"^wifi\.cfg$|^wfnv_desc", "MT6637-WIFI", "A", "BINARY-ONLY", "Connectivity",
     "Wi-Fi NVRAM descriptor + cfg consumed by the MT6637 host driver"),
    (r"^conninfra\.cfg$", "CONNINFRA-KERNEL", "B", "BINARY-ONLY", "Connectivity", "connsys infra config"),
    (r"morphoEISCalibration_DOOGEE", "CAMERA-HAL-ISP", "D", "BINARY-ONLY", "Camera",
     "EIS calibration payload still carries another OEM's product name (DOOGEE_M24PS) on a Ulefone image: "
     "carried-over reference-board tuning data"),
    (r"^lib3a\.ccu|morphoEIS|^uw_calib|^default_pd_calibration|^dvs_config|^pixsmart_|^aw_undistort",
     "CAMERA-HAL-ISP", "B", "BINARY-ONLY", "Camera",
     "MTK/pixsmart 3A + EIS + distortion image-tuning payload owned by the camera HAL scope"),
    (r"^mali_csffw\.bin$", 'MALI-GPU-KERNEL', 'B', 'BINARY-ONLY', 'Graphics', 'CSF payload retained; kernel loader interface only, algorithm excluded'),
    (r"^modem\.img$|^mcf_ota\.img$", "MODEM-FIRMWARE", "A", "SIGNED-BINARY", "Modem",
     "MD1 modem + carrier-config images"),
    (r'^ccu\.img$', 'CAMERA-HAL-ISP', 'B', 'SIGNED-BINARY', 'Camera', 'CCU firmware algorithm boundary; host loader owned by CAMERA-ISP-KERNEL'),
    (r'^vcp\.img$|^gpueb\.img$', 'GPU-AI-AUX-KERNEL-INTERFACES', 'B', 'SIGNED-BINARY', 'Kernel', 'Remote signed binary excluded; normal-world host/loading boundary only'),
    (r'^apusys\.img$', 'APUSYS-NPU-KERNEL', 'B', 'SIGNED-BINARY', 'NPU', 'Signed APU algorithm binary excluded; host interface only'),
    (r"^scp\.img$|^dpm\.img$|^mcupm\.img$|^sspm\.img$", "SENSOR-HUB", "B", "SIGNED-BINARY", "Kernel",
     "SCP/DPM/MCUPM/SSPM/CCU runtime images loaded through mtk_tinysys_ipi"),
    (r"^vcp\.img$|^apusys\.img$|^spmfw\.img$|^pi_img\.img$", GEN, "C", "SIGNED-BINARY", "Kernel",
     "generic MTK remote-processor runtime image carried verbatim by the port"),
    (r"^connsys_bt\.img$", "BLUETOOTH", "A", "SIGNED-BINARY", "Connectivity", "connsys BT partition image"),
    (r"^connsys_wifi\.img$", "MT6637-WIFI", "A", "SIGNED-BINARY", "Connectivity", "connsys Wi-Fi partition image"),
    (r"^connsys_gnss\.img$", "GNSS", "A", "SIGNED-BINARY", "GNSS", "connsys GNSS partition image"),
    (r"^gz\.img$", "GZ-TRANSPORT", "A", "SIGNED-BINARY", "Security", "GenieZone hypervisor image"),
    (r"^tee\.img$", "TRUSTKERNEL-TEE", "A", "SIGNED-BINARY", "Security", "Trustonic/TrustKernel TEE image"),
    (r"^gpueb\.img$", "TRUSTKERNEL-TEE", "B", "SIGNED-BINARY", "Security",
     "GPB (generic parameter block) secure-boot image consumed by the TEE loader path"),
    (r"^lk\.img$|^logo\.img$", "PARTITION-OWNERSHIP", "B", "SIGNED-BINARY", "Boot",
     "LK bootloader + logo images: owned by partition/boot scope, source not reconstructable"),
    (r"^preloader", "DRAM-MEMORY", "B", "SIGNED-BINARY", "Boot",
     "preloader carries the DRAM init/Training code owned by DRAM-MEMORY"),
    (r"^dtbo\.img$", "DTB-DTBO", "A", "SOURCE-AVAILABLE", "Boot", "device-tree overlay image built by DTB-DTBO"),
    (r"^vbmeta", "AVB-SIGNING-CHAIN", "A", "SOURCE-AVAILABLE", "Boot", "AVB hash-descriptor chain"),
    (r"^boot\.img$|^init_boot\.img$|^vendor_boot\.img$", "BOOT-IMAGES", "A", "SOURCE-AVAILABLE", "Boot",
     "boot/vendor_boot/init_boot image layout owned by BOOT-IMAGES"),
    (r"^super\.img$", "AB-SUPER-GEOMETRY", "A", "SOURCE-AVAILABLE", "Storage", "super/dynamic-partition geometry"),
    (r"^userdata\.img$", "KEYSTORE-VOLD-KEYMINT", "B", "DEVICE-INTERNAL", "Security",
     "userdata carries the FBE metadata/key ring"),
]


def classify_firmware(path: str) -> tuple[str, str, str, str, str]:
    base = os.path.basename(path)
    for pat, comp, cov, fwclass, dom, why in FW_RULES:
        if re.search(pat, base):
            return comp, cov, fwclass, dom, why
    return ("UNKNOWN", "E", "UNKNOWN", "Unclassified", "no rule claims this payload")


# --------------------------------------------------------------------------
# axis 8: partitions
# --------------------------------------------------------------------------
PART_RULES: list[tuple[str, str, str, str]] = [
    (r"^preloader", "DRAM-MEMORY", "B", "Boot"),
    (r"^lk$|^lk2$|^logo$|^proinfo$|^otp$|^boot_para$|^para$|^pgpt$|^sgpt$|^expdb$|^sec1$|^vb$",
     "PARTITION-OWNERSHIP", "B", "Boot"),
    (r"^vbmeta", "AVB-SIGNING-CHAIN", "A", "Boot"),
    (r"^boot$|^init_boot$|^vendor_boot$|^recovery$", "BOOT-IMAGES", "A", "Boot"),
    (r"^dtbo$", "DTB-DTBO", "A", "Boot"),
    (r"^super$", "AB-SUPER-GEOMETRY", "A", "Storage"),
    (r"^vendor_dlkm$", "VENDOR-DLKM", "A", "Storage"),
    (r"^odm_dlkm$", "OEM-KERNEL-MODULES", "B", "Storage"),
    (r"^system_dlkm$", "SYSTEM-DLKM", "A", "Storage"),
    (r"^odm$|^product$|^system$|^system_ext$|^vendor$", "PARTITION-OWNERSHIP", "B", "Storage"),
    (r"^tee$|^seccfg$", "TRUSTKERNEL-TEE", "B", "Security"),
    (r"^gz$|^pvmfw$", "GZ-TRANSPORT", "B", "Security"),
    (r"^gpueb$", "MTK-TINYSYS-IPI", "B", "Kernel"),
    (r"^modem$|^mcf_ota$|^md_sec$|^mrdump$|^pi_img$", "MODEM-FIRMWARE", "B", "Modem"),
    (r"^spmfw$|^scp$|^ccu$|^dpm$|^sspm$|^mcupm$|^vcp$", "SENSOR-HUB", "B", "Kernel"),
    (r"^apusys$", GEN, "C", "NPU"),
    (r"^connsys_", "CONNINFRA-KERNEL", "A", "Connectivity"),
    (r"^nvram|^nvcfg|^nvdata|^persist|^protect", "NVRAM-CALIBRATION", "A", "Calibration"),
    (r"^userdata$|^metadata$|^frp$", "KEYSTORE-VOLD-KEYMINT", "B", "Security"),
    (r"^misc$|orangefox|recovery", "RECOVERY-ORANGEFOX", "B", "Recovery"),
    (r"^flashinfo$", "UFS-STORAGE", "B", "Storage"),
    (r"^pstore$", "PARTITION-OWNERSHIP", "B", "Storage"),
    (r"^dram_para$", "DRAM-MEMORY", "A", "Boot"),
]


def classify_partition(name: str) -> tuple[str, str, str]:
    for pat, comp, cov, dom in PART_RULES:
        if re.match(pat, name):
            return comp, cov, dom
    return ("UNKNOWN", "E", "Unclassified")


# --------------------------------------------------------------------------
# axis 7: secure world (curated; one row per secure-world surface)
# --------------------------------------------------------------------------
SECURE_WORLD = [
    ["GenieZone hypervisor", "gz_trusty_mod, gz_ipc_mod, gz_irq_mod, gz_log_mod, gz_virtio_mod",
     "vendor/bin/hw gz services", "gz.img", "gz_a/b", "GZ-TRANSPORT", "A",
     "transport and IPC contract closed; hypervisor payload is signed",
     "5 gz modules + gz_a/gz_b scatter slots"],
    ["TrustKernel TEE (secure world)", "tkcore, tkcore_rfs", "teed, tee_check_keybox, terservice",
     "tee.img", "tee_a/b", "TRUSTKERNEL-TEE", "D",
     "secure-world payload is vendor-signed and unobservable; normal-world side is TKCORE-DRV",
     "tee_a/tee_b scatter slots; teed init service"],
    ["TrustKernel ABI island", "tkcore FFA/SMC contract", "vendor/lib64/libtkcore*", "-", "-",
     "TRUSTKERNEL-ABI-ISLAND", "D",
     "ABI island cannot be reconstructed without vendor island source", "existing BLOCKED component"],
    ["KeyMint 3 / secure clock / shared secret", "tkcore",
     "android.hardware.security.keymint@3.0-service.trustkernel", "tee.img", "tee_a/b",
     "KEYSTORE-VOLD-KEYMINT", "C",
     "AIDL client side closed to the extent possible; TA implementation proprietary",
     "VINTF keymint/secureclock/sharedsecret + gatekeeper declarations"],
    ["Gatekeeper", "tkcore", "android.hardware.gatekeeper-service.trustkernel", "tee.img", "tee_a/b",
     "KEYSTORE-VOLD-KEYMINT", "C", "client side mapped; TA proprietary",
     "VINTF gatekeeper declaration"],
    ["RPMB secure storage", "ufsjtag/rpmb driver in UFS stack", "vold, keymaster clients",
     "RPMB partition on the UFS device", "internal to UFS", "UFS-RPMB-KERNEL", "A",
     "kernel RPMB path closed; key material and vendor provisioning remain out of reach",
     "UFS-RPMB-KERNEL pack + teed/rpmb witnesses"],
    ["Fingerprint secure world (MicroArray)", "microarray_fp_tee, fingerprint",
     "microarray.fingerprint.default.so, vendor.focaltech.fingerprint@1.0-service",
     "TA inside tee.img", "tee_a/b", "MICROARRAY-FP-TEE", "C",
     "normal-world driver closed; the sensor TA and template store are proprietary",
     "microarray_fp_tee.ko + fingerprint HAL service"],
    ["Trusted memory allocation", "mem_gpu/tmem FFA glue", "-", "-", "-", "TMEM-FFA", "A",
     "normal-world FFA memory-share contract closed", "existing DONE component"],
    ["FF-A v1.0 transport", "ffa_v10 modules", "-", "-", "-", "FFA-V10", "A",
     "transport contract closed; callee payload out of scope", "existing DONE component"],
    ["DRM client stack (ClearKey + Widevine-class)", "mediatek-drm display DRM is separate",
     "android.hardware.drm-service.clearkey, drmserver32/64, vendor.cas-default", "-", "-",
     "COVERED-GENERIC", "C",
     "example/clearkey services are generic; the OEM Widevine L1 TA path is proprietary",
     "VINTF drm/cas declarations + drm init services"],
    ["pVM / protected VM firmware", "gz/trusty pvmfw consumer", "-", "pvmfw.img", "pvmfw_a/b",
     "PARTITION-OWNERSHIP", "B",
     "protected VM payload is AOSP-signed; ownership tracked as a partition", "pvmfw_a/pvmfw_b scatter slots"],
    ["Keystore2 / vold metadata key", "vold, metadata_encryption", "keystore2, credstore, odsign",
     "-", "metadata", "KEYSTORE-VOLD-KEYMINT", "A",
     "FBE/metadata-key integration; runtime validation open",
     "keystore2/credstore/odsign init services"],
    ["Modem secure boot / md_sec", "ccci/md modules", "ccci_mdinit, ccci_rpcd", "md_sec", "md_sec",
     "MODEM-FIRMWARE", "C", "modem security image is vendor-signed and not reconstructable",
     "md_sec scatter slot + ccci services"],
]


# --------------------------------------------------------------------------
def main() -> int:
    status_by_component = component_statuses()
    status_of = lambda comp: status_by_component.get(comp, "MISSING" if comp == "UNMAPPED" else "N/A")

    # ---- axis 4: VINTF interfaces + legacy HAL libraries -----------------
    vintf: dict[str, dict] = {}
    for r in read_raw("raw-vintf.tsv"):
        fam = r["interface"].split("@")[0].split("::")[0].strip() or r["interface"]
        d = vintf.setdefault(fam, {"docs": set(), "parts": set(), "vers": set(),
                                   "inst": set(), "cls": set(), "opt": set(), "n": 0, "man": 0})
        d["docs"].add(r["doc"])
        d["parts"].add(r["partition"])
        d["cls"].add(r["iface_class"])
        d["opt"].add(r["optional"])
        d["n"] += 1
        d["man"] += 1 if r["doc_kind"] == "manifest" else 0
        m = re.search(r"@(\d+(?:\.\d+)+)", r["interface"])
        if m:
            d["vers"].add(m.group(1))
        if r["instance"]:
            d["inst"].add(f"{r['interface'].split('::')[-1].split('/')[0]}/{r['instance']}"
                          if "::" in r["interface"] else r["instance"])

    svcs = read_raw("raw-init-services.tsv")
    svc_by_iface: dict[str, set] = {}
    bin_by_iface: dict[str, set] = {}
    for s in svcs:
        for piece in filter(None, s["interface"].split("|")):
            fam = piece.strip().split("@")[0].split("::")[0].strip()
            svc_by_iface.setdefault(fam, set()).add(s["service"])
            m = re.search(r"(?:^|\s)(/[^\s]+)", s["exec"])
            if m:
                bin_by_iface.setdefault(fam, set()).add(m.group(1))

    libs = read_raw("raw-legacy-hw.tsv")
    lib_by_fam: dict[str, set] = {}
    for l in libs:
        fam = l["module"].split("@")[0].split(".impl")[0].replace(".default", "").replace("-impl-mediatek", "")
        lib_by_fam.setdefault(fam, set()).add(l["path"])

    rows: list[list] = []
    for fam in sorted(vintf):
        d = vintf[fam]
        comp, cov, dom, why = classify_vintf(fam)
        rows.append(["vintf-interface", fam, "/".join(sorted(x for x in d["cls"] if x)),
                     ",".join(sorted(d["vers"])) or "-", join(d["inst"])[:300] or "-",
                     join(d["parts"]), " ".join(sorted(d["docs"]))[:400],
                     join(svc_by_iface.get(fam, set()))[:200], join(bin_by_iface.get(fam, set()))[:300],
                     join(lib_by_fam.get(fam, set()))[:200], dom, comp, status_of(comp), cov,
                     kernel_dependency(comp), why, "manifest" if d["man"] else "matrix-only",
                     f"raw-vintf.tsv: {d['n']} declarations ({d['man']} in a manifest)"])
    for l in libs:
        comp, cov, dom, why = classify_hw(l["module"])
        rows.append(["hw-backend-lib", l["module"], "native", "-", "-", l["partition"],
                     l["path"], "-", "-", l["path"], dom, comp, status_of(comp), cov,
                     kernel_dependency(comp), why, "n/a",
                     "raw-legacy-hw.tsv: android.hardware.* backend library"])
    write_rows("hals-services.tsv",
               ["artifact_type", "artifact", "iface_class", "versions", "instances", "partition",
                "declaring_docs", "init_services", "binaries", "hw_libraries", "subsystem", "component",
                "component_status", "coverage", "kernel_dependency", "boundary", "optional", "evidence"], rows)

    # ---- axis 5: init services + trigger executables --------------------
    grouped: dict[str, dict] = {}
    for s in svcs:
        raw_ex = s["exec"].strip()
        seclabel = ""
        if raw_ex.startswith("u:r:"):
            seclabel, _, raw_ex = raw_ex.partition(" -- ")
        # Trigger-time ``exec`` syntax may start with uid/gid/options (for
        # example ``- system system -- /system/bin/vdc``).  The first absolute
        # path is the executable; treating the first token as the executable
        # created fake ``[exec] -`` and ``[exec] --`` rows.
        path_match = re.search(r"(?:^|\s)(/[^\s]+)", raw_ex)
        exe = path_match.group(1) if path_match else ""
        if s["service"].startswith("[trigger]"):
            if not exe:
                # Preserve the evidence without inventing an artifact name.
                continue
            key = "[exec] " + os.path.basename(exe)
        else:
            key = s["service"]
        d = grouped.setdefault(key, {"exe": set(), "rc": set(), "sec": set(), "iface": set(),
                                    "user": set(), "flag": set(), "present": set()})
        if seclabel:
            d["sec"].add(seclabel.strip())
        if exe:
            d["exe"].add(exe)
        d["present"].add(s.get("exec_present", "unknown"))
        d["rc"].add(s["rc"])
        d["iface"].add(s["interface"])
        d["user"].add(s["user"])
        for k in ("class", "disabled", "oneshot", "critical", "socket", "override"):
            if s.get(k):
                d["flag"].add(s[k])
        if s["triggers"]:
            d["flag"].add(f"{s['triggers']}")
    rows = []
    for name in sorted(grouped):
        d = grouped[name]
        exes = " ".join(sorted(x for x in d["exe"] if x))
        comp, cov, dom, why = classify_service(name, exes)
        binary_present = "/".join(sorted(d["present"]))
        if binary_present == "no" and not name.startswith("[exec]"):
            cov = "D"
            why = ("init declaration points to an executable absent from every extracted stock partition; "
                   "reference-board/stale rc baggage unless runtime evidence proves an alternate mount")
        rows.append([name, exes[:200], binary_present, " ".join(sorted(d["rc"]))[:400],
                     " ".join(sorted(d["sec"])), join(d["iface"])[:200],
                     " ".join(sorted(x for x in d["user"] if x))[:120],
                     " ".join(sorted(f[:40] for f in d["flag"]))[:300], dom, comp, status_of(comp), cov,
                     device_access(comp), why, "raw-init-services.tsv"])
    write_rows("vendor-services.tsv",
               ["service", "executable", "binary_present", "rc_files", "seclabel", "declared_interface", "user",
                "flags", "subsystem", "component", "component_status", "coverage", "device_access",
                "purpose", "evidence"], rows)

    # ---- axis 6: firmware -----------------------------------------------
    rows = []
    for f in read_raw("raw-firmware.tsv"):
        comp, cov, fwclass, dom, why = classify_firmware(f["path"])
        producer, loader, consumer = firmware_parties(comp, os.path.basename(f["path"]))
        rows.append([f["path"], f["source"], f["source"], f["class"], f["bytes"], f["sha256"],
                     producer, loader, consumer, dom, comp, status_of(comp), cov, fwclass, why,
                     "no", f"{f['source']}:{f['class']} payload"])
    write_rows("firmware.tsv",
               ["artifact", "source", "partition_or_source", "class", "bytes", "sha256",
                "producer_device", "loader", "consumer", "subsystem", "component", "component_status",
                "coverage", "firmware_class", "boundary", "payload_copied", "evidence"], rows)

    # ---- axis 7: secure world ------------------------------------------
    secure_rows = [r[:6] + [status_of(r[5])] + r[6:] for r in SECURE_WORLD]
    write_rows("secure-world.tsv",
               ["area", "normal_world_driver", "userspace", "ta_or_blob", "partition", "component",
                "component_status", "coverage", "boundary", "evidence"], secure_rows)

    # ---- axis 8: partitions --------------------------------------------
    parts = read_raw("raw-partitions.tsv")
    seen: dict[str, dict] = {}
    for p in parts:
        name = p["partition"]
        base = re.sub(r"_[ab]$", "", name)
        d = seen.setdefault(base, {"slots": set(), "files": set(), "size": set(), "region": set(),
                                  "storage": set(), "dl": set(), "up": set(), "res": set()})
        d["slots"].add("a/b" if name != base else "single")
        if p["file_name"] and p["file_name"] != "NONE":
            d["files"].add(p["file_name"])
        for k, col in (("size", "partition_size"), ("region", "region"), ("storage", "storage"),
                       ("dl", "is_download"), ("up", "is_upgradable"), ("res", "is_reserved")):
            if p[col]:
                d[k].add(p[col])
    rows = []
    for base in sorted(seen):
        d = seen[base]
        comp, cov, dom = classify_partition(base)
        why = ("scatter/ABOTA row owned by this component" if cov != "E"
               else "no RE component claims this partition")
        rows.append(["partition", base, join(d["region"]) or "super (dynamic)",
                     "/".join(sorted(d["slots"])), join(d["size"]), join(d["storage"]),
                     join(d["dl"]), join(d["up"]), join(d["res"]), dom, comp, status_of(comp), cov,
                     why + "; raw-partitions.tsv"])
    write_rows("boot-storage.tsv",
               ["artifact_type", "artifact", "partition_or_source", "slot_pair", "size_bytes",
                "storage", "downloadable", "upgradable", "reserved", "subsystem", "component",
                "component_status", "coverage", "evidence"], rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
