#!/usr/bin/env python3
"""Generate text-only inventories from the frozen GSI and final split build."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

DEFAULT_GSI = Path("/mnt/SamsungSSD/TIER3/phase5/android17/reference-gsi-lineage_gsi_arm64-cp2a-userdebug-erofs/installed-files.json")
DEFAULT_SPLIT = Path("/mnt/SamsungSSD/TIER3/phase5/android17/out-lineage_gsi_arm64-erofs/target/product/gq5012bf1")
DEFAULT_VNDK = Path("/mnt/SamsungSSD/TIER3/phase5/android17/analysis/vndk-apex")

OPTIONAL = {
    "AudioFX", "Backgrounds", "Camelot", "Etar", "Glimpse", "Jelly",
    "Recorder", "Seedvault", "ThemePicker", "Twelve", "Updater",
}
NORMAL = {
    "Aperture", "DeskClock", "LatinIME", "Launcher3QuickStep",
    "LineageSetupWizard", "Settings", "SystemUI", "webview",
}
CORE = {
    "ContactsProvider", "DownloadProvider", "ExternalStorageProvider",
    "LineageSettingsProvider", "MediaProvider", "PermissionController",
    "TelephonyProvider",
}


def load(path: Path):
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_tsv(path: Path, header, rows):
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def bundle_key(name: str) -> str:
    bits = name.strip("/").split("/")
    if not bits:
        return name
    partition = bits[0]
    rest = bits[1:]
    if not rest:
        return "/" + partition
    if rest[0] in ("app", "priv-app") and len(rest) > 1:
        return f"/{partition}/{rest[0]}/{rest[1]}"
    if rest[0] == "apex" and len(rest) > 1:
        return f"/{partition}/apex/{rest[1]}"
    if rest[0] == "framework" and len(rest) > 1:
        if rest[1] == "oat":
            return f"/{partition}/framework/oat"
        return f"/{partition}/framework/{rest[1]}"
    if rest[0] == "overlay" and len(rest) > 1:
        return f"/{partition}/overlay/{rest[1]}"
    if rest[0] == "media" and len(rest) > 1:
        if rest[1] == "audio" and len(rest) > 2:
            return f"/{partition}/media/audio/{rest[2]}"
        return f"/{partition}/media/{rest[1]}"
    return f"/{partition}/{rest[0]}"


def classify(path: str):
    leaf = path.rsplit("/", 1)[-1].removesuffix(".apex").removesuffix(".capex")
    if leaf in OPTIONAL:
        return "NO", "Optional Lineage application retained because all partitions already fit."
    if leaf in NORMAL:
        return "YES", "Required for normal phone setup or expected daily phone functionality."
    if leaf in CORE:
        return "YES", "Core Android or Lineage provider/service."
    if "/apex/" in path:
        if leaf == "com.android.vndk.v34":
            return "YES", "VNDK 34 snapshot required by the captured vendor contract."
        if leaf == "com.android.virt":
            return "YES", "Small AVF-disabled API APEX; full Microdroid payload is not selected."
        if leaf == "com.android.hardware.biometrics.fingerprint.virtual":
            return "INVESTIGATE", "Base product package retained; stock manifest declares the virtual fingerprint instance."
        return "YES", "Android 17 modular platform component selected by the standard product."
    if "/framework/" in path or path.endswith("/bin") or path.endswith("/lib") or path.endswith("/lib64"):
        return "YES", "Core framework/native runtime payload."
    if path.endswith("/fonts"):
        return "YES", "Measured broad font set retained; no language coverage was removed."
    if "/media/" in path:
        return "NO", "Normal media catalog, not required for boot; retained after fit succeeded."
    if path.endswith("/etc") or path.endswith("/usr"):
        return "YES", "Partition configuration and runtime data."
    return "INVESTIGATE", "Aggregate installed-file category; inspect members before changing."


def package_inventory(rows_by_partition, out: Path):
    grouped = defaultdict(lambda: [0, 0])
    for partition, rows in rows_by_partition.items():
        for row in rows:
            grouped[(partition, bundle_key(row["Name"]))][0] += int(row["Size"])
            grouped[(partition, bundle_key(row["Name"]))][1] += 1
    result = []
    for (partition, path), (size, count) in sorted(grouped.items()):
        required, reason = classify(path)
        result.append((path, partition, size, required, reason, f"final installed-files JSON; {count} path(s)"))
    write_tsv(out / "PARTITION-PACKAGE-MAP.tsv",
              ["package/path", "partition", "size", "required", "reason", "source"], result)


def app_bundles(rows):
    groups = defaultdict(lambda: [0, 0])
    for row in rows:
        key = bundle_key(row["Name"])
        if "/app/" in key or "/priv-app/" in key:
            groups[key][0] += int(row["Size"])
            groups[key][1] += 1
    return groups


def reference_lists(gsi, split_rows, out: Path):
    g_apps = app_bundles(gsi)
    write_tsv(out / "REFERENCE-GSI-PACKAGES.tsv",
              ["package_path", "payload_bytes", "installed_paths"],
              [(k, v[0], v[1]) for k, v in sorted(g_apps.items())])
    for filename, rows in (("REFERENCE-GSI-APEX.tsv", gsi), ("FINAL-APEX.tsv", split_rows)):
        apex = [r for r in rows if "/apex/" in r["Name"] and r["Name"].endswith((".apex", ".capex"))]
        write_tsv(out / filename, ["path", "bytes", "sha256"],
                  [(r["Name"], r["Size"], r["SHA256"]) for r in sorted(apex, key=lambda x: x["Name"])])


def optional_inventory(rows_by_partition, out: Path):
    specs = [
        ("Updater", "SYSTEM_EXT", "NO", "NO", "KEEP", "OTA client; restore/removal is easy but no size pressure remains."),
        ("LineageSetupWizard", "SYSTEM_EXT", "NO", "YES", "KEEP", "Coherent first-use provisioning."),
        ("Recorder", "PRODUCT", "NO", "NO", "KEEP", "Optional recorder."),
        ("Backgrounds", "PRODUCT", "NO", "NO", "KEEP", "Optional wallpapers."),
        ("ThemePicker", "SYSTEM_EXT", "NO", "NO", "KEEP", "Lineage customization UI."),
        ("Twelve", "PRODUCT", "NO", "NO", "KEEP", "Music application."),
        ("Etar", "PRODUCT", "NO", "NO", "KEEP", "Calendar application."),
        ("Jelly", "PRODUCT", "NO", "YES", "KEEP", "Browser; WebView remains separate and mandatory."),
        ("Glimpse", "PRODUCT", "NO", "YES", "KEEP", "Gallery/image viewing."),
        ("Aperture", "PRODUCT", "NO", "YES", "KEEP", "Camera UI for normal phone use."),
        ("Seedvault", "SYSTEM_EXT", "NO", "NO", "KEEP", "Optional backup provider."),
        ("AudioFX", "SYSTEM_EXT", "NO", "NO", "KEEP", "Optional audio effects UI."),
        ("Camelot", "PRODUCT", "NO", "NO", "KEEP", "Optional Lineage app."),
        ("Profiles", "SYSTEM_EXT", "NO", "NO", "KEEP", "Small Lineage profiles UI."),
        ("DeskClock", "PRODUCT", "NO", "YES", "KEEP", "Alarm/timer functionality."),
        ("LatinIME", "PRODUCT", "NO", "YES", "KEEP", "Keyboard required for usable setup."),
    ]
    result = []
    for pkg, expected, boot, normal, decision, reason in specs:
        total = count = 0
        found_parts = set()
        for part, rows in rows_by_partition.items():
            marker1 = f"/{part.lower()}/app/{pkg}/"
            marker2 = f"/{part.lower()}/priv-app/{pkg}/"
            for row in rows:
                if marker1 in row["Name"] or marker2 in row["Name"]:
                    total += int(row["Size"]); count += 1; found_parts.add(part)
        result.append((pkg, ",".join(sorted(found_parts)) or expected, total, boot, normal, decision, reason))
    # Developer shell payload is not an APK bundle.
    vim_rows = [r for r in rows_by_partition["SYSTEM_EXT"] if "/bin/vim" in r["Name"] or "/usr/share/vim/" in r["Name"]]
    result.append(("Vim runtime", "SYSTEM_EXT", sum(int(r["Size"]) for r in vim_rows), "NO", "NO", "KEEP", "Developer utility retained because the successful build already fits; easy later removal."))
    # Media and boot animations.
    all_rows = [r for rows in rows_by_partition.values() for r in rows]
    for name, needles, part, reason in [
        ("Audio catalog", ["/product/media/audio/"], "PRODUCT", "Normal ringtone/alarm/notification choices; no random language/media trim."),
        ("Boot animations", ["/product/media/bootanimation"], "PRODUCT", "Light/dark normal boot visuals."),
    ]:
        selected = [r for r in all_rows if any(n in r["Name"] for n in needles)]
        result.append((name, part, sum(int(r["Size"]) for r in selected), "NO", "YES", "KEEP", reason))
    write_tsv(out / "OPTIONAL-PACKAGES.tsv",
              ["package", "partition", "size", "required_for_boot", "required_for_normal_phone_use", "decision", "reason"], result)


def vndk_contents(vndk_root: Path, out: Path):
    rows = []
    for generation in (31, 32, 33, 34):
        root = vndk_root / f"v{generation}"
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            rows.append((generation, str(path.relative_to(root)), path.stat().st_size, sha(path)))
    write_tsv(out / "REFERENCE-GSI-VNDK-CONTENTS.tsv",
              ["VNDK_generation", "path", "size", "sha256"], rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gsi", type=Path, default=DEFAULT_GSI)
    ap.add_argument("--split", type=Path, default=DEFAULT_SPLIT)
    ap.add_argument("--vndk", type=Path, default=DEFAULT_VNDK)
    ap.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    rows_by_partition = {
        "SYSTEM": load(args.split / "installed-files.json"),
        "SYSTEM_EXT": load(args.split / "installed-files-system_ext.json"),
        "PRODUCT": load(args.split / "installed-files-product.json"),
    }
    split_rows = sum(rows_by_partition.values(), [])
    gsi = load(args.gsi)
    package_inventory(rows_by_partition, args.output)
    reference_lists(gsi, split_rows, args.output)
    optional_inventory(rows_by_partition, args.output)
    vndk_contents(args.vndk, args.output)


if __name__ == "__main__":
    main()
