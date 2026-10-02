#!/usr/bin/env python3
"""Stock vendor camera userspace dependency map (static, offline).

Starting from the camera service roots (camerahalserver + every vendor ELF whose
name matches the camera patterns) it builds:
  * the DT_NEEDED closure (hard link-time edges),
  * dlopen-style edges: any "lib*.so" string inside a reachable ELF that names
    an existing vendor library (soft edges, MTK loads most feature/3A/tuning
    blobs this way),
and classifies every reached library.

Usage: camera_userspace_deps.py <vendor_root> <system_root|-> <out_dir>
Outputs: camera-userspace-dependencies.tsv, camera-userspace-edges.tsv,
         camera-sensor-specific-files.tsv
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys

CAM_PAT = re.compile(r"(cam|isp|3a|_3a|imgsensor|tuning|mfnr|ainr|aisr|hdr|eis|pdaf|ccu|"
                     r"fdvt|fd_|facedet|bokeh|depth|zsl|lsc|awb|_ae|_af|nvram|dip|wpe|mfb|dpe|"
                     r"aie|mtkcam|hal3a|halsensor|seninf|remosaic|4cell|lpcnr|dce|vsdof|"
                     r"camalgo|camera)", re.I)
SENSORS = ["imx989", "ov64b", "s5kjn1", "s5kjn1main2", "s5kgn1", "s5kgm2", "ov32b40", "imx989cts",
           "s5kjn1cts", "dw9781", "main_vcm", "main2_vcm", "main4_vcm"]
SO_RE = re.compile(rb"(lib[A-Za-z0-9_.+\-]+\.so)\b")


def is_elf(p):
    try:
        with open(p, "rb") as f:
            return f.read(4) == b"\x7fELF"
    except OSError:
        return False


def needed(p):
    out = subprocess.run(["llvm-readelf", "-d", p], capture_output=True, text=True).stdout
    return re.findall(r"\(NEEDED\)\s+Shared library: \[(.+?)\]", out)


def classify(name, path):
    n = name.lower()
    if "/system/" in path or path.startswith("system:"):
        return "SYSTEM/AOSP"
    if n.startswith(("android.hardware.camera", "android.hardware.graphics", "libbinder", "libhidl", "libutils",
                     "libcutils", "liblog", "libc++", "libbase", "libfmq", "libui", "libhardware",
                     "libcamera_metadata", "libsync", "libion", "libdmabufheap", "libvndksupport",
                     "android.hardware.common", "libnativewindow", "libjsoncpp", "libz", "libexpat",
                     "libcrypto", "libssl", "libprocessgroup", "libdl_android", "libtinyxml2", "libsqlite")):
        return "AOSP_VNDK_or_NDK"
    if any(s in n for s in SENSORS):
        return "SENSOR_SPECIFIC"
    if any(k in n for k in ("tuning", "nvram", "camera_custom", "cameracustom", "custom")):
        return "MTK_TUNING_CUSTOM"
    if any(k in n for k in ("3a", "_ae", "_af", "awb", "lsc", "flicker", "aaa", "pdaf", "ccu", "ae_", "af_")):
        return "MTK_3A"
    if any(k in n for k in ("mfnr", "ainr", "aisr", "hdr", "bokeh", "vsdof", "depth", "eis", "fd", "face",
                            "remosaic", "4cell", "lpcnr", "dce", "clearzoom", "dre", "cfb", "mfll", "nr",
                            "algo", "neuron", "apu", "nn")):
        return "MTK_FEATURE_ALGO"
    if any(k in n for k in ("isp", "dip", "imgsys", "p2", "wpe", "mfb", "dpe", "aie", "imgstream", "imgio",
                            "drv", "seninf", "sensor")):
        return "MTK_ISP_DRV"
    if "mtkcam" in n or "camera" in n or "cam" in n:
        return "MTK_CAMERA_HAL_CORE"
    if "vendor.mediatek" in n:
        return "MTK_HIDL_AIDL_IFACE"
    return "OTHER_VENDOR"


def main():
    vroot, sroot, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    libs: dict[str, str] = {}
    allfiles = []
    for base in ("lib64", "lib", "bin", "bin/hw", "lib64/hw", "lib64/egl", "lib64/mt6878", "lib/mt6878"):
        d = os.path.join(vroot, base)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p) and is_elf(p):
                key = f if base.startswith("lib64") or base.startswith("bin") else f"lib32:{f}"
                if base == "lib64/mt6878":
                    key = f"mt6878/{f}"
                libs.setdefault(key, p)
                allfiles.append((key, p))
    # also apex payloads with camera libs are ignored on purpose (none observed)
    sys_libs = set()
    if sroot != "-":
        for d in ("lib64", "apex"):
            pass
        for dp, dn, fn in os.walk(os.path.join(sroot)):
            for f in fn:
                if f.endswith(".so"):
                    sys_libs.add(f)
    roots = ["camerahalserver"] + sorted(k for k, p in libs.items()
                                         if CAM_PAT.search(k) and not k.startswith("lib32:"))
    edges = []
    reach = {}
    queue = list(roots)
    while queue:
        k = queue.pop()
        if k in reach or k not in libs:
            continue
        p = libs[k]
        nd = needed(p)
        reach[k] = nd
        for n in nd:
            tgt = n if n in libs else (f"mt6878/{n}" if f"mt6878/{n}" in libs else n)
            edges.append((k, tgt, "DT_NEEDED"))
            if tgt in libs:
                queue.append(tgt)
        blob = open(p, "rb").read()
        for m in set(SO_RE.findall(blob)):
            s = m.decode()
            tgt = s if s in libs else (f"mt6878/{s}" if f"mt6878/{s}" in libs else None)
            if tgt and tgt != k and s not in nd:
                edges.append((k, tgt, "STRING_REF(dlopen?)"))
                if CAM_PAT.search(s):
                    queue.append(tgt)
    needed_by = {}
    for a, b, t in edges:
        needed_by.setdefault(b, set()).add(f"{a}[{'N' if t == 'DT_NEEDED' else 'S'}]")
    with open(os.path.join(out, "camera-userspace-dependencies.tsv"), "w") as f:
        f.write("file\tvendor_path\tsize\tsha256_12\tclass\tdt_needed\tneeded_by(N=DT_NEEDED,S=string)\n")
        for k in sorted(reach):
            p = libs[k]
            h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]
            rel = os.path.relpath(p, vroot)
            f.write(f"{k}\t/vendor/{rel}\t{os.path.getsize(p)}\t{h}\t{classify(k, rel)}\t"
                    f"{','.join(reach[k])}\t{','.join(sorted(needed_by.get(k, [])))}\n")
    with open(os.path.join(out, "camera-userspace-edges.tsv"), "w") as f:
        f.write("from\tto\tkind\tto_location\n")
        for a, b, t in sorted(set(edges)):
            loc = "vendor" if b in libs else ("system" if b in sys_libs else "unresolved")
            f.write(f"{a}\t{b}\t{t}\t{loc}\n")
    # sensor-specific files anywhere in vendor (libs, tuning, configs)
    with open(os.path.join(out, "camera-sensor-specific-files.tsv"), "w") as f:
        f.write("sensor_token\tvendor_path\tsize\n")
        for dp, dn, fn in os.walk(vroot):
            for x in fn:
                lx = x.lower()
                for s in SENSORS:
                    if s in lx:
                        p = os.path.join(dp, x)
                        f.write(f"{s}\t/vendor/{os.path.relpath(p, vroot)}\t{os.path.getsize(p)}\n")
                        break
    cls = {}
    for k in reach:
        c = classify(k, os.path.relpath(libs[k], vroot))
        cls[c] = cls.get(c, 0) + 1
    print(f"reachable vendor ELFs: {len(reach)}; edges: {len(set(edges))}; by class: {cls}")


if __name__ == "__main__":
    main()
