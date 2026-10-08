#!/usr/bin/env python3
"""Build axes 9-10 and the all-axis artifact map."""
from __future__ import annotations

import csv
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CA = os.path.dirname(HERE)
RAW = os.path.join(CA, "audit-evidence")
GEN = "GENERIC-PLATFORM-INFRASTRUCTURE"
BLOB = "VENDOR-BLOB-HAL-INVENTORY"


def read(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def raw(name: str) -> list[dict]:
    return read(os.path.join(RAW, name))


def write(name: str, header: list[str], rows: list[list[str]]) -> None:
    with open(os.path.join(CA, name), "w", newline="", encoding="utf8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header); w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def status_map() -> dict[str, str]:
    d = {r["component"]: r["status"] for r in raw("pack-identity.tsv")}
    d.update({GEN: "N/A", "COVERED-GENERIC": "N/A", "UNMAPPED": "MISSING"})
    return d


def name_owner(name: str) -> tuple[str, str, str, str]:
    """component, coverage, subsystem, reason for config/overlay names."""
    n = name.lower()
    rules = [
        (r"mali|gpu", "UNMAPPED", "E", "Graphics", "GPU integration converges on the missing Mali kernel/DT ownership scope"),
        (r"camera|camerax|isphal|mtkcam", "CAMERA-HAL-ISP", "B", "Camera", "camera HAL/framework configuration"),
        (r"audio|mixer|soundtrigger|sound_trigger", "AUDIO-DSP", "B", "Audio", "audio policy/routing/DSP integration"),
        (r"finger|biometric", "MADEV-FINGERPRINT", "B", "Fingerprint", "fingerprint/biometric integration"),
        (r"nfc|secure.?element", "NFC-SECURE-ELEMENT", "B", "NFC", "NFC/secure-element integration"),
        (r"gnss|gps|location", "GNSS", "B", "GNSS", "GNSS/location integration"),
        (r"wifi|wlan", "MT6637-WIFI", "B", "Connectivity", "Wi-Fi framework integration"),
        (r"bluetooth", "BLUETOOTH", "B", "Connectivity", "Bluetooth framework integration"),
        (r"radio|telephony|ims|volte|carrier", "RADIO-HAL-RIL", "B", "Modem", "telephony/RIL framework integration"),
        (r"sensor", "SENSOR-HUB", "B", "Sensors", "Android sensor-hub integration"),
        (r"thermal|power|health|battery|charger", "THERMAL-POWER-HAL", "B", "Power", "thermal/power/health configuration"),
        (r"vibrator|haptic", "HAPTICS", "B", "Input", "vibrator/haptics integration"),
        (r"light|led", "AW2013-RGB-LED", "B", "Display", "lights/LED integration"),
        (r"usb|typec", "USB-TYPEC", "B", "USB", "USB/Type-C framework integration"),
        (r"display|surfaceflinger|hwcomposer|graphics|refresh", BLOB, "B", "Graphics", "vendor display/graphics integration"),
        (r"storage|vold|sdcard|ufs", "PARTITION-OWNERSHIP", "B", "Storage", "storage framework integration"),
        (r"keymint|keymaster|gatekeeper|keystore|trust|tee", "KEYSTORE-VOLD-KEYMINT", "B", "Security", "secure credential integration"),
        (r"yft|rugged|tinylcd|gesturewake|changenode|obtainvendor", "REAR-RUGGED-FEATURES", "B", "Board glue", "YFT board integration"),
    ]
    for pat, comp, cov, sub, why in rules:
        if re.search(pat, n):
            return comp, cov, sub, why
    return GEN, "C", "Framework", "generic AOSP/MTK framework configuration"


def normalize_rc(path: str) -> str:
    return re.sub(r"^(partitions/|vendor-ramdisks/[^/]+/)", "", path)


def build_android() -> list[dict]:
    services = read(os.path.join(CA, "vendor-services.tsv"))
    rc_owners: dict[str, Counter] = defaultdict(Counter)
    for s in services:
        for rc in s["rc_files"].split():
            # A missing service/KMD owner cannot own a config as class B.
            # The existing ANDROID-INIT scope owns assembly of such rc files;
            # this does not close the GPU kernel-facing service ABI gap.
            if s["component"] not in {GEN, "UNKNOWN", "UNMAPPED"}:
                rc_owners[rc][s["component"]] += 1
    statuses = status_map()
    out = []
    for r in raw("raw-android-integration.tsv"):
        cat, path = r["category"], r["path"]
        active = "SHIPPED"
        if re.search(r"(?i)test|example|virtual", path):
            active = "REFERENCE/TEST"
        if cat == "vintf":
            comp, cov, sub, why = "VINTF-HAL-MANIFEST", "A", "Android integration", "VINTF declaration/matrix ownership"
        elif cat == "sepolicy":
            comp, cov, sub, why = "VENDOR-SEPOLICY", "A", "Security", "SELinux/property/service context ownership"
        elif cat == "properties":
            comp, cov, sub, why = "VENDOR-PROPERTIES", "A", "Android integration", "device/property surface ownership"
        elif cat == "fstab":
            comp, cov, sub, why = "PARTITION-OWNERSHIP", "A", "Storage", "mount, encryption and logical-partition contract"
        elif cat == "init-rc":
            norm = normalize_rc(path)
            ctr = rc_owners.get(norm)
            if ctr:
                comp = ctr.most_common(1)[0][0]
                cov = "B"; sub = "Boot/init"; why = "owner inferred from services declared by this exact rc file"
            else:
                comp, cov, sub, why = "ANDROID-INIT", "B", "Boot/init", "device init script not narrowed to one child service"
        elif cat == "audio-config":
            comp, cov, sub, why = "AUDIO-DSP", "B", "Audio", "audio policy/routing/calibration configuration"
        elif cat == "camera-config":
            comp, cov, sub, why = "CAMERA-HAL-ISP", "B", "Camera", "camera framework/HAL configuration"
        elif cat == "sensor-config":
            comp, cov, sub, why = "SENSOR-HUB", "B", "Sensors", "sensor HAL/configuration"
        elif cat == "usb-config":
            comp, cov, sub, why = "USB-TYPEC", "B", "USB", "USB/gadget/Type-C configuration"
        elif cat == "thermal-power-config":
            comp, cov, sub, why = "THERMAL-POWER-HAL", "B", "Power", "thermal/power/health policy configuration"
        elif cat == "lights-haptics-config":
            comp, cov, sub, why = name_owner(path)
        elif cat == "media-config":
            comp, cov, sub, why = name_owner(path)
            if comp == GEN:
                why = "generic codec/media capability configuration; no device-specific RE scope"
        else:
            comp, cov, sub, why = name_owner(path)
            if cat == "overlay-rro" and comp == GEN and r["partition"] in {"vendor", "odm", "system_ext"}:
                comp, cov, sub, why = BLOB, "B", "Android integration", "vendor RRO retained and tracked by blob/HAL inventory"
        port = r["current_tree_state"].upper()
        if port == "PRESENT":
            boundary = "current device/vendor tree has a same-name counterpart"
        elif port == "CURRENT-ONLY":
            boundary = "current port addition with no same-name shipped stock artifact; validate necessity and compatibility"
        else:
            boundary = "stock-only metadata: carry through extraction or author an explicit replacement"
        out.append({**r, "subsystem": sub, "active_state": active, "component": comp,
                    "component_status": statuses.get(comp, "N/A"), "coverage": cov,
                    "purpose": why, "port_boundary": boundary})
    return out


LIB_OWNER = {
    "thermal-camera": ("THERMAL-RADIOMETRY", "B", "Thermal camera", "radiometry/UVC conversion and calibration behavior"),
    "camera": ("CAMERA-HAL-ISP", "B", "Camera", "camera HAL/ISP/3A/tuning behavior"),
    "fingerprint": ("MADEV-FINGERPRINT", "B", "Fingerprint", "fingerprint HAL/protocol behavior"),
    "radio-ims": ("RADIO-HAL-RIL", "B", "Modem", "vendor RIL/IMS/telephony behavior"),
    "gnss": ("GNSS", "B", "GNSS", "GNSS location engine/HAL behavior"),
    "nfc": ("NFC-SECURE-ELEMENT", "B", "NFC", "NCI/secure-element userspace behavior"),
    "audio": ("AUDIO-DSP", "B", "Audio", "audio HAL, routing, effects or DSP protocol behavior"),
    "sensor": ("SENSOR-HUB", "B", "Sensors", "sensor HAL/fusion/calibration behavior"),
    "charging-power": ("THERMAL-POWER-HAL", "B", "Power", "thermal/power/charging userspace policy"),
    "nvram-calibration": ("NVRAM-CALIBRATION", "B", "Calibration", "NVRAM/calibration serialization and access"),
    "security-drm": ("TRUSTKERNEL-TEE", "B", "Security", "TEE/DRM/key provisioning client behavior"),
    "wifi": ("MT6637-WIFI", "B", "Connectivity", "Wi-Fi HAL/vendor behavior"),
    "bluetooth": ("BLUETOOTH", "B", "Connectivity", "Bluetooth HAL/vendor behavior"),
    "connectivity": ("CONNINFRA-KERNEL", "B", "Connectivity", "connsys/FM/connectivity userspace behavior"),
    "graphics-gpu": (BLOB, "B", "Graphics", "proprietary graphics/GPU allocation/composition behavior"),
    "usb": ("USB-TYPEC", "B", "USB", "USB/gadget/Type-C userspace behavior"),
    "board-glue": ("REAR-RUGGED-FEATURES", "B", "Board glue", "YFT board-specific userspace behavior"),
}


def build_libraries() -> list[dict]:
    statuses = status_map()
    out = []
    for r in raw("raw-userspace-libraries.tsv"):
        comp, cov, sub, purpose = LIB_OWNER[r["domain"]]
        paths = r["paths"].split(";")
        all_system = all(p.startswith("partitions/system/") for p in paths)
        # Plain system libraries matching a broad name rule are usually AOSP API
        # helpers, except OEM app JNI shipped under system/app or system/priv-app.
        if all_system and not any("/app/" in p or "/priv-app/" in p for p in paths):
            comp, cov, sub = GEN, "C", "Framework"
            purpose = "AOSP/system helper library; no device-specific implementation ownership"
        if r["domain"] == "radio-ims" and re.search(r"(?i)ims|volte|ipsec", r["library"]):
            comp = "IMS"
        if r["domain"] == "security-drm" and re.search(r"(?i)widevine|oemcrypto|drm|hdcp", r["library"]):
            comp = BLOB
            purpose = "proprietary DRM/HDCP client; secure TA/source is not reconstructable"
        boundary = ("source-equivalent replacement requires vendor algorithm/protocol knowledge; retain the compatible blob"
                    if cov != "C" else "source is generic/upstream; no dedicated device RE needed")
        out.append({**r, "subsystem": sub, "component": comp,
                    "component_status": statuses.get(comp, "N/A"), "coverage": cov,
                    "purpose": purpose,
                    "kernel_only_enough": "no" if cov != "C" else "n/a",
                    "proprietary_boundary": boundary})
    return out


def build_artifact_map(android: list[dict], libs: list[dict]) -> None:
    statuses = status_map()
    rows: list[list[str]] = []
    def add(t, a, src, sub, active, comp, cov, evidence, notes):
        rows.append([t, a, src, sub, active, comp, statuses.get(comp, "N/A"), cov, evidence, notes])

    for r in read(os.path.join(CA, "kernel-modules.tsv")):
        active = "DEAD/REFERENCE" if r["coverage"] == "D" else ("CONFIGURED" if r["in_modules_load"] == "yes" else "SHIPPED")
        if r["loaded_in_capture"].lower() in {"y", "yes", "true", "1"}: active = "ACTIVE"
        if r["coverage"] == "E": active = "CONFIGURED/UNMAPPED"
        add("kernel-module", r["module"], r["partitions"], r["subsystem"], active,
            r["component"], r["coverage"], r["evidence"], f"depends={r['depends']}; load_order={r['load_order']}")
    for r in read(os.path.join(CA, "device-tree.tsv")):
        active = r["node_state"] or ("ACTIVE" if int(r["nodes_enabled"] or 0) else "DISABLED")
        add("dt-compatible", r["compatible"], r["dt_source"], r["physical_function"], active,
            r["component"], r["coverage"], r["evidence"], f"sample={r['sample_node']}; drivers={r['driver_candidates']}")
    for r in read(os.path.join(CA, "hardware.tsv")):
        add("physical-hardware", r["device"], r["inventory"], r["category"], r["presence"],
            r["component"], r["coverage"], r["evidence"], f"buses={r['buses']}; drivers={r['drivers']}")
    for r in read(os.path.join(CA, "hals-services.tsv")):
        active = "DECLARED" if r["artifact_type"] == "vintf-interface" else "SHIPPED"
        if r["coverage"] == "D": active = "REFERENCE/EXAMPLE"
        source = r["declaring_docs"] if r["artifact_type"] == "hw-backend-lib" else r["partition"]
        add(r["artifact_type"], r["artifact"], source, r["subsystem"], active,
            r["component"], r["coverage"], r["evidence"], r["boundary"])
    for r in read(os.path.join(CA, "vendor-services.tsv")):
        active = "DISABLED" if "disabled" in r["flags"] else "DECLARED"
        if r["coverage"] == "D": active = "REFERENCE/TEST"
        add("init-service", r["service"], r["rc_files"], r["subsystem"], active,
            r["component"], r["coverage"], r["evidence"], r["purpose"])
    for r in read(os.path.join(CA, "firmware.tsv")):
        active = "REFERENCE" if r["coverage"] == "D" else "SHIPPED"
        add("firmware", r["artifact"], r["partition_or_source"], r["subsystem"], active,
            r["component"], r["coverage"], r["evidence"], f"{r['firmware_class']}; {r['boundary']}")
    for r in read(os.path.join(CA, "secure-world.tsv")):
        add("secure-world", r["area"], r["partition"], "Security", "SHIPPED",
            r["component"], r["coverage"], r["evidence"], r["boundary"])
    for r in read(os.path.join(CA, "boot-storage.tsv")):
        add("partition", r["artifact"], r["partition_or_source"], r["subsystem"], "SHIPPED",
            r["component"], r["coverage"], r["evidence"], f"slots={r['slot_pair']}; size={r['size_bytes']}")
    for r in android:
        add("android-integration", r["path"], r["partition"], r["subsystem"], r["active_state"],
            r["component"], r["coverage"], f"sha256={r['sha256']}", f"{r['category']}; {r['port_boundary']}")
    for r in libs:
        add("userspace-library", r["library"], r["partitions"], r["subsystem"], "SHIPPED",
            r["component"], r["coverage"], f"sha256={r['sha256']}", r["proprietary_boundary"])
    write("artifact-map.tsv", ["artifact_type", "artifact", "partition_or_source", "subsystem",
          "active_state", "component", "component_status", "coverage", "evidence", "notes"], rows)


def main() -> int:
    android = build_android()
    libs = build_libraries()
    write("android-integration.tsv",
          ["category", "artifact", "partition", "bytes", "sha256", "current_tree_state", "current_matches",
           "subsystem", "active_state", "component", "component_status", "coverage", "purpose", "port_boundary"],
          [[r["category"], r["path"], r["partition"], r["bytes"], r["sha256"], r["current_tree_state"],
            r["current_matches"], r["subsystem"], r["active_state"], r["component"],
            r["component_status"], r["coverage"], r["purpose"], r["port_boundary"]] for r in android])
    write("userspace-libraries.tsv",
          ["library", "domain", "partitions", "paths", "bytes", "sha256", "consumers",
           "current_tree_state", "current_matches", "subsystem", "component", "component_status",
           "coverage", "purpose", "kernel_only_enough", "proprietary_boundary"],
          [[r[k] for k in ["library", "domain", "partitions", "paths", "bytes", "sha256", "consumers",
                           "current_tree_state", "current_matches", "subsystem", "component", "component_status",
                           "coverage", "purpose", "kernel_only_enough", "proprietary_boundary"]] for r in libs])
    build_artifact_map(android, libs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
