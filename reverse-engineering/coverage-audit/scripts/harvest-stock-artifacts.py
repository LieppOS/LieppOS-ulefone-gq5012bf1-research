#!/usr/bin/env python3
"""Harvest the shipped userspace/firmware/boot universe from the stock image.

This is raw evidence collection for audit axes 4-8; it classifies nothing.  Every
row records where it came from so a later builder can resolve ownership against
what the RE components themselves assert.

Outputs (coverage-audit/audit-evidence/):
  raw-vintf.tsv          every <manifest> / <matrix-overrides> HAL record declared
                         by vendor/odm VINTF documents
  raw-init-services.tsv  every `service` block in vendor/odm/system_ext init rc,
                         with class, seclabel, credentials and declared interfaces
  raw-legacy-hw.tsv      every vendor/odm lib*/hw module and hardware backend .so
  raw-firmware.tsv       device firmware metadata only (path, partition, bytes,
                         sha256) - no firmware bytes are copied into the repo
  raw-partitions.tsv     the scatter-declared raw partition table plus the
                         dynamic-partition layout of `super`

No proprietary payload is written to the repository: firmware rows carry metadata
only, and the modem/TEE/secure-applet binaries are recorded as size+digest.
"""
from __future__ import annotations

import csv
import glob
import hashlib
import os
import re
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
CA = os.path.abspath(os.path.join(HERE, ".."))
EV = os.path.join(CA, "audit-evidence")
WS = os.environ.get("RE_WORKSPACE", os.path.abspath(os.path.join(CA, "..", "..", "..")))
STOCK = os.path.join(WS, "ulefone-gq5012bf1-research/workspace/gq5012bf1/stock")
P = os.path.join(STOCK, "partitions")
FW = os.path.join(STOCK, "firmware")

STATUSES = ("DONE", "PARTIAL", "BLOCKED", "TODO")


def write(name: str, rows: list[dict]) -> None:
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(os.path.join(EV, name), "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields or ["empty"],
                          delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- VINTF
def vintf() -> list[dict]:
    rows = []
    for part in ("vendor", "odm", "product", "system", "system_ext"):
        base = os.path.join(P, part, "etc/vintf")
        for dirpath, _d, files in os.walk(base):
            for fn in sorted(files):
                if not fn.endswith(".xml"):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    root = ET.parse(path).getroot()
                except ET.ParseError:
                    continue
                kind = root.tag                                # manifest|compatibility_matrix
                doc = os.path.relpath(path, P)
                for hal in root.iter("hal"):
                    fq = (hal.findtext("name") or "").strip()
                    insts = [i.text.strip() for i in hal.iter("instance")
                             if (i.text or "").strip()]
                    fqn = [f.text.strip() for f in hal.findall("fqname")
                           if (f.text or "").strip()]
                    if fqn and not insts:
                        insts = fqn
                    iface = (hal.get("format") or "").strip().upper() or "?"
                    rows.append({
                        "doc": doc, "doc_kind": kind, "partition": part,
                        "interface": fq,
                        "instance": ",".join(dict.fromkeys(insts))[:200],
                        "version": (hal.findtext("version") or "").strip(),
                        "iface_class": iface,
                        "optional": hal.get("optional", ""),
                        "transport": ";".join(t.text.strip() for t in hal.findall("transport")
                                              if (t.text or "").strip()),
                        "updatable": (hal.findtext("updatable") or "").strip()})
    return rows


# ---------------------------------------------------------------- init services
SVC_KEYS = ("class", "seclabel", "user", "group", "capabilities", "disabled",
            "oneshot", "critical", "interface", "socket", "override", "ioprio",
            "rlimit", "writepid", "setenv")


def init_services() -> list[dict]:
    rows = []
    for part in ("vendor", "odm", "system_ext", "system", "product"):
        base = os.path.join(P, part, "etc/init")
        if not os.path.isdir(base):
            continue
        for dirpath, _d, files in os.walk(base):
            for fn in sorted(files):
                if not fn.endswith(".rc"):
                    continue
                path = os.path.join(dirpath, fn)
                cur = None
                sec = ""
                for line in open(path, encoding="utf8", errors="ignore"):
                    line = line.rstrip("\n")
                    if not line.strip() or line.lstrip().startswith("#"):
                        continue
                    m = re.match(r"^\s*service\s+(\S+)\s+(.*)$", line)
                    if m:
                        cur = {"rc": os.path.relpath(path, P), "partition": part,
                               "service": m.group(1), "exec": m.group(2).strip(),
                               "interface": "", "triggers": ""}
                        rows.append(cur)
                        continue
                    if not line[0].isspace():               # section header at column 0
                        m2 = re.match(r"^on\s+(.*)$", line)
                        sec = m2.group(1).strip() if m2 else ""
                        cur = None
                        continue
                    if cur is not None:
                        pass
                    else:
                        # command executed from an `on` trigger section
                        m4 = re.match(r"^\s+(exec|exec_start|exec_background|write_desc)\s+(\S+)\s*(.*)$", line)
                        if m4 and m4.group(1) != "write_desc" and sec:
                            rows.append({"rc": os.path.relpath(path, P), "partition": part,
                                         "service": f"[trigger] {sec[:60]}",
                                         "exec": (m4.group(2) + " " + m4.group(3)).strip(),
                                         "interface": "", "triggers": m4.group(1)})
                        continue
                    m3 = re.match(r"^\s+(interface)\s+(.*)$", line)
                    if m3:
                        cur["interface"] = (cur["interface"] + " | "
                                           + m3.group(2).strip())[:400]
                        continue
                    for k in SVC_KEYS:
                        if k == "interface":
                            continue
                        if re.match(rf"^\s+{k}\b", line):
                            cur[k] = re.sub(r"\s+", " ", line.strip())[:200]
    for r in rows:
        for k in SVC_KEYS:
            r.setdefault(k, "")
    return rows


# ---------------------------------------------------------------- legacy hw modules
def legacy_hw() -> list[dict]:
    rows = []
    for part in ("vendor", "odm", "product", "system", "system_ext"):
        for sub in ("lib/hw", "lib64/hw"):
            d = os.path.join(P, part, sub)
            if not os.path.isdir(d):
                continue
            for dirpath, _dd, files in os.walk(d):
                for fn in sorted(files):
                    if not fn.endswith(".so"):
                        continue
                    rows.append({"partition": part, "arch": sub.split("/")[1],
                                 "path": os.path.relpath(os.path.join(dirpath, fn), P),
                                 "module": fn})
    return rows


# ---------------------------------------------------------------- firmware
def firmware() -> list[dict]:
    rows = []

    def add(part: str, path: str, klass: str) -> None:
        try:
            size = os.path.getsize(path)
        except OSError:
            return
        if size < 16:
            return
        rows.append({"source": part, "class": klass,
                     "path": os.path.relpath(path, P if part != "scatter" else STOCK),
                     "bytes": str(size), "sha256": sha256(path)})

    # 1. the vendor firmware directory itself: every file is loader-side data
    for d in ("vendor/firmware", "vendor/firmware_mnt", "odm/firmware",
              "vendor/etc/firmware"):
        base = os.path.join(P, d)
        for dirpath, _dirs, files in os.walk(base) if os.path.isdir(base) else []:
            for fn in sorted(files):
                if fn.endswith((".ko", ".rc", ".xml", ".json", ".tef")):
                    continue
                add("vendor", os.path.join(dirpath, fn), "firmware-dir")

    # 2. calibration / DSP data outside the firmware directory
    for pat in ("vendor/etc/*.bin", "vendor/etc/*.dat", "vendor/etc/wifi/nvram/*.bin",
                "vendor/etc/camera/eis/*.bin", "vendor/etc/smartpa_param/*.bin",
                "vendor/etc/camera/*.bin"):
        for path in sorted(glob.glob(os.path.join(P, pat), recursive=True)):
            add("vendor", path, "calibration-data")

    # 3. the vendor DSP/ADSP library set (Little Kernel / MDPIMG side is absent on
    #    a shipped image, so the audio/voice DSP payload shows up only as .so)
    for path in sorted(glob.glob(os.path.join(P, "vendor/lib*/mt6878/*.so"))):
        if re.search(r"(dsp|vtservice|speech|aud|sml|mcdt|mmlwvr)", path, re.I):
            add("vendor", path, "dsp-library")
    # 4. scatter/raw images: firmware-class partitions, metadata only
    for name in ("modem", "connsys_bt", "connsys_wifi", "connsys_gnss", "scp", "ccu",
                 "dpm", "sspm", "mcupm", "vcp", "gz", "tee", "gpueb", "pi_img",
                 "apusys", "spmfw", "lk", "logo", "dtbo", "preloader_k6878v1_64",
                 "vbmeta", "vbmeta_system", "vbmeta_vendor", "boot", "init_boot",
                 "vendor_boot", "super", "userdata", "mcf_ota"):
        for ext in (".img", ".bin"):
            cand = os.path.join(FW, name + ext)
            if os.path.exists(cand):
                add("scatter", cand, "image-partition")
                break
    return rows



# ---------------------------------------------------------------- partitions
SCATTER_KEYS = ("partition_index", "partition_name", "file_name", "is_download",
                "type", "linear_start_addr", "physical_start_addr", "partition_size",
                "region", "storage", "operation_type", "is_upgradable",
                "empty_boot_needed", "is_reserved", "reserved")


def partitions() -> list[dict]:
    """The raw (UFS/LU) layout exactly as the stock scatter download-agent table
    declares it, plus the logical (super) members actually present."""
    rows: list[dict] = []
    scatter = os.path.join(FW, "MT6878_Android_scatter.txt")
    if os.path.exists(scatter):
        for line in open(scatter, encoding="utf8", errors="ignore"):
            m = re.match(r"\s*-?\s*partition_name\s*:\s*(\S+)", line)
            if m:
                rows.append({"partition": m.group(1)})
                continue
            if not rows:
                continue
            for key in SCATTER_KEYS[1:]:
                m2 = re.match(rf"\s*{key}\s*:\s*(.*)", line)
                if m2:
                    rows[-1][key] = m2.group(1).strip()
                    break
    imgs = os.path.join(STOCK, "images")
    for fn in sorted(os.listdir(imgs)) if os.path.isdir(imgs) else []:
        if not fn.endswith(".img"):
            continue
        rows.append({"partition": fn[:-4], "part_size": str(os.path.getsize(
            os.path.join(imgs, fn))), "operation_type": "LOGICAL-SUPER-IMAGE",
            "file_name": fn})
    return rows


def main() -> None:
    os.makedirs(EV, exist_ok=True)
    v = vintf()
    write("raw-vintf.tsv", v or [{"empty": ""}])
    s = init_services()
    write("raw-init-services.tsv", s or [{"empty": ""}])
    h = legacy_hw()
    write("raw-legacy-hw.tsv", h or [{"empty": ""}])
    f = firmware()
    write("raw-firmware.tsv", f or [{"empty": ""}])
    p = partitions()
    write("raw-partitions.tsv", p or [{"empty": ""}])
    print(f"distinct vintf interfaces={len({r['interface'] for r in v})}")


if __name__ == "__main__":
    main()
