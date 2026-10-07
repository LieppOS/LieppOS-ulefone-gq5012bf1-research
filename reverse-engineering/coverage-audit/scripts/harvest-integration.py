#!/usr/bin/env python3
"""Harvest metadata for axes 9 (Android integration) and 10 (native libraries).

Only paths, sizes, hashes and ELF string-level dependency witnesses are committed.
No proprietary file content is copied.
"""
from __future__ import annotations

import csv
import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CA = HERE.parent
RAW = CA / "audit-evidence"
REPO = CA.parent.parent
WORKSPACE = REPO.parent
STOCK = REPO / "workspace/gq5012bf1/stock"
PARTS = STOCK / "partitions"
DEVICE = WORKSPACE / "android_device_ulefone_gq5012bf1"
VENDOR = WORKSPACE / "vendor_ulefone_gq5012bf1"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stock_rel(p: Path) -> str:
    return str(p.relative_to(STOCK))


def current_index() -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for root in (DEVICE, VENDOR):
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file():
                out[p.name].append(f"{root.name}/{p.relative_to(root)}")
    return out


def integration_category(p: Path) -> str | None:
    try:
        rel = stock_rel(p)
    except ValueError:
        rel = str(p)
    s = "/" + rel.lower()
    n = p.name.lower()
    if "/overlay/" in s and p.suffix.lower() in {".apk", ".xml"}:
        return "overlay-rro"
    if ("/permissions/" in s or "/sysconfig/" in s) and p.suffix.lower() == ".xml":
        return "permissions-features"
    if n.startswith("fstab") or "/fstab." in s:
        return "fstab"
    if "manifest" in n or "compatibility_matrix" in n or "/vintf/" in s:
        if p.suffix.lower() == ".xml":
            return "vintf"
    if n.endswith(".cil") or "/sepolicy/" in s or n in {
        "file_contexts", "property_contexts", "service_contexts", "hwservice_contexts",
        "vndservice_contexts", "seapp_contexts", "mac_permissions.xml"
    }:
        return "sepolicy"
    if n.endswith(".prop") or n in {"build.prop", "default.prop", "prop.default"}:
        return "properties"
    if n.endswith(".rc"):
        return "init-rc"
    if p.suffix.lower() not in {".xml", ".conf", ".json", ".ini", ".cfg", ".txt"}:
        return None
    if "audio" in n or "mixer_path" in n or "sound_trigger" in n:
        return "audio-config"
    if "media" in n or "codec" in n:
        return "media-config"
    if "camera" in n or "camerax" in n:
        return "camera-config"
    if "sensor" in n or "sensors" in s:
        return "sensor-config"
    if "usb" in n or "typec" in n:
        return "usb-config"
    if any(x in n for x in ("thermal", "power", "health", "battery", "charger")):
        return "thermal-power-config"
    if "light" in n or "vibrator" in n:
        return "lights-haptics-config"
    return None


LIB_DOMAINS: list[tuple[str, re.Pattern[str]]] = [
    ("thermal-camera", re.compile(r"infis|thermov|radiometr|advirtemp|ac020|dualuvc|usbuvccamera020|irtemp|fm781", re.I)),
    ("camera", re.compile(r"camera|mtkcam|camsys|imgsensor|seninf|isp|lib3a|eis|ccu|morpho|pixsmart|featurepipe|camalgo", re.I)),
    ("fingerprint", re.compile(r"fingerprint|focaltech|madev|microarray|goodix|swfp|fptool", re.I)),
    ("radio-ims", re.compile(r"(^|lib)(ims|ril|volte|vtservice|telephony|ipsec|ccci|c2k|carrier)", re.I)),
    ("gnss", re.compile(r"gnss|gps|agps|geofence|flp|lbs|libmnl", re.I)),
    ("nfc", re.compile(r"nfc|st21|secure[_-]?element", re.I)),
    ("audio", re.compile(r"audio|aurisys|soundtrigger|smartpa|awinic|speaker|headset", re.I)),
    ("sensor", re.compile(r"sensor|hfmanager|fusion|compass|magnet|gyro|acceler|barometer", re.I)),
    ("charging-power", re.compile(r"charger|charging|fuel|battery|powerhal|thermal|health", re.I)),
    ("nvram-calibration", re.compile(r"nvram|calibrat|sensorcali|custparam", re.I)),
    ("security-drm", re.compile(r"keymint|keymaster|gatekeeper|keystore|trustkernel|tkcore|widevine|oemcrypto|drm|hdcp|rpmb|(^|lib)tee", re.I)),
    ("wifi", re.compile(r"wifi|wlan|supplicant|hostapd", re.I)),
    ("bluetooth", re.compile(r"bluetooth|libbt|btif|btsock|bta_", re.I)),
    ("connectivity", re.compile(r"conninfra|connsys|connfem|fmradio|libfm", re.I)),
    ("graphics-gpu", re.compile(r"mali|gpu|gralloc|hwcomposer|composer|memtrack|vulkan|gles|libpq|mmlpq", re.I)),
    ("usb", re.compile(r"usb|typec|gadget", re.I)),
    ("board-glue", re.compile(r"tinylcd|gesturewake|changenode|obtainvendor|yft|touch|tpd", re.I)),
]


def library_domain(p: Path) -> str | None:
    name = p.name
    low = name.lower()
    # Generated AIDL/HIDL ABI libraries are contracts already counted on axis 4,
    # not implementations encoding device behavior.
    if low.startswith("android.hardware.") or low.startswith("vendor.mediatek.hardware."):
        return None
    target = name + " " + stock_rel(p)
    for dom, pat in LIB_DOMAINS:
        if pat.search(target):
            return dom
    return None


def partition_of(p: Path) -> str:
    rel = p.relative_to(PARTS)
    return rel.parts[0] if rel.parts else "unknown"


def write_raw_integration(cur: dict[str, list[str]]) -> int:
    rows = []
    roots = [PARTS, STOCK / "vendor_boot-unpacked", STOCK / "vendor-ramdisks", STOCK / "init_boot-unpacked"]
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            cat = integration_category(p)
            if not cat:
                continue
            rel = stock_rel(p)
            part = partition_of(p) if PARTS in p.parents else rel.split("/", 1)[0]
            matches = cur.get(p.name, [])
            rows.append([cat, rel, part, p.stat().st_size, sha256(p),
                         "present" if matches else "stock-only", ";".join(matches)])
    # Also expose device/vendor-tree-only integration files.  A same-name
    # current counterpart is already attached to its stock row; only truly
    # current-only names become additional rows.
    stock_names = {Path(r[1]).name for r in rows}
    for root, part in ((DEVICE, "current-device-tree"), (VENDOR, "current-vendor-tree")):
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.name in stock_names:
                continue
            cat = integration_category(p)
            if not cat:
                continue
            rel = f"current/{root.name}/{p.relative_to(root)}"
            rows.append([cat, rel, part, p.stat().st_size, sha256(p),
                         "current-only", f"{root.name}/{p.relative_to(root)}"])
    rows.sort(key=lambda x: (x[0], x[1]))
    out = RAW / "raw-android-integration.tsv"
    with out.open("w", newline="", encoding="utf8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["category", "path", "partition", "bytes", "sha256", "current_tree_state", "current_matches"])
        w.writerows(rows)
    return len(rows)


def elf_needed_names(p: Path) -> set[str]:
    try:
        if p.stat().st_size > 100 * 1024 * 1024:
            return set()
        data = p.read_bytes()
    except OSError:
        return set()
    if not data.startswith(b"\x7fELF"):
        return set()
    return {m.decode("ascii", "ignore") for m in re.findall(rb"lib[A-Za-z0-9_.+@-]+\.so", data)}


def write_raw_libraries(cur: dict[str, list[str]]) -> int:
    candidates: dict[str, list[Path]] = defaultdict(list)
    for p in PARTS.rglob("*.so"):
        if p.is_file() and library_domain(p):
            candidates[p.name].append(p)

    # Main consumers are service executables and other significant libraries.
    scan_files: set[Path] = set()
    for part in ("vendor", "system_ext", "system"):
        base = PARTS / part
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and ("/bin/" in str(p) or p.suffix == ".so"):
                scan_files.add(p)
    reverse: dict[str, set[str]] = defaultdict(set)
    wanted = set(candidates)
    for p in sorted(scan_files):
        for needed in elf_needed_names(p) & wanted:
            # A library commonly embeds its own SONAME; that is not a consumer.
            if p.name != needed:
                reverse[needed].add(stock_rel(p))

    rows = []
    for name, paths in candidates.items():
        dom = library_domain(paths[0]) or "unknown"
        rels = [stock_rel(p) for p in paths]
        parts = sorted({partition_of(p) for p in paths})
        hashes = sorted({sha256(p) for p in paths})
        sizes = sorted({str(p.stat().st_size) for p in paths})
        consumers = sorted(reverse.get(name, set()))
        matches = cur.get(name, [])
        rows.append([name, dom, ";".join(parts), ";".join(rels), ";".join(sizes),
                     ";".join(hashes), ";".join(consumers),
                     "present" if matches else "stock-only", ";".join(matches)])
    rows.sort(key=lambda x: (x[1], x[0]))
    out = RAW / "raw-userspace-libraries.tsv"
    with out.open("w", newline="", encoding="utf8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["library", "domain", "partitions", "paths", "bytes", "sha256",
                    "consumers", "current_tree_state", "current_matches"])
        w.writerows(rows)
    return len(rows)


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    cur = current_index()
    a = write_raw_integration(cur)
    b = write_raw_libraries(cur)
    print(f"raw-android-integration.tsv: {a} rows")
    print(f"raw-userspace-libraries.tsv: {b} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
