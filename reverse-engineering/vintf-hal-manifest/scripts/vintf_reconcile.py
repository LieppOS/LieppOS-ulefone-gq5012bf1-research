#!/usr/bin/env python3
"""Instance-level VINTF reconciliation: stock vendor+odm manifests vs the HAL set the LieppOS device
tree would assemble (DEVICE_MANIFEST_FILE + ODM_MANIFEST_FILES + installed fragment blobs from
proprietary-files.txt), plus the init-service payload check for every declared HAL.
usage: vintf_reconcile.py <stock-partitions> <device-tree> <out-dir>"""
import collections, os, re, sys
import xml.etree.ElementTree as ET
P, DT, OUT = sys.argv[1:4]

def instances(path):
    out = set()
    try: root = ET.parse(path).getroot()
    except ET.ParseError as e: return {("PARSE-ERROR", str(e), "", "", "")}
    for hal in root.iter("hal"):
        fmt = hal.get("format", "hidl"); name = (hal.findtext("name") or "").strip()
        vers = [v.text.strip() for v in hal.findall("version")] or [""]
        fq = [f.text.strip() for f in hal.findall("fqname")]
        for itf in hal.findall("interface"):
            iname = (itf.findtext("name") or "").strip()
            for inst in itf.findall("instance"):
                for v in vers: out.add((fmt, name, v, iname, inst.text.strip()))
        for f in fq:
            m = re.match(r"(?:@([\d.]+)::)?(\w+)/(.+)", f)
            if m: out.add((fmt, name, m.group(1) or vers[0], m.group(2), m.group(3)))
    return out

pf = [l.strip() for l in open(os.path.join(DT, "proprietary-files.txt")) if l.strip() and not l.startswith("#")]
installed = {l.split(";")[0].lstrip("-") for l in pf if "EXTRACT_ONLY" not in l}
bc = open(os.path.join(DT, "BoardConfig.mk")).read()
dmf = re.findall(r"\$\(DEVICE_PATH\)/(vintf/[\w.\-]+\.xml)", bc)

stock_files = []
for d in ("vendor/etc/vintf", "vendor/etc/vintf/manifest", "vendor/odm/etc/vintf"):
    for f in sorted(os.listdir(os.path.join(P, d))):
        if f.endswith(".xml") and "compatibility_matrix" not in f:
            stock_files.append(f"{d}/{f}")
stock = collections.defaultdict(set)
for f in stock_files:
    for i in instances(os.path.join(P, f)): stock[i].add(f)
target = collections.defaultdict(set)
for f in dmf: 
    for i in instances(os.path.join(DT, f)): target[i].add("devtree:" + f)
for f in stock_files:
    if f in installed:
        for i in instances(os.path.join(P, f)): target[i].add("blob:" + f)

# AOSP source modules in PRODUCT_PACKAGES that carry vintf_fragments for the same instance
dmk = open(os.path.join(DT, "device.mk")).read()
SRC = {k: m for k, m in {("android.hardware.drm", "clearkey"): "android.hardware.drm-service.clearkey",
       ("android.hardware.health", "default"): "android.hardware.health-service.example",
       ("android.hardware.ir", "default"): "android.hardware.ir-service.example",
       ("android.hardware.sensors", "default"): "android.hardware.sensors-service.multihal",
       ("android.hardware.wifi", "default"): "android.hardware.wifi-service-lazy"}.items() if m in dmk}
# SIM-config ODM variants: stock picks one of ss/dsds/tsts/qsqs at runtime via ro.boot.product.hardware.sku
odm_variant = lambda fs: all(re.search(r"odm/etc/vintf/manifest_(ss|dsds|tsts|qsqs)\.xml", f) for f in fs)
rows = []
for i in sorted(stock | target.keys() if False else set(stock) | set(target)):
    s, t = stock.get(i, set()), target.get(i, set())
    if s and t: v = "PRESENT"
    elif s and odm_variant(s) and not any("dsds" in f for f in s): v = "ODM-SKU-VARIANT (non-DSDS SKU only)"
    elif s and (i[1], i[4]) in SRC: v = "SOURCE-BUILT: AOSP module " + SRC[(i[1], i[4])] + " ships its own vintf_fragment"
    elif s: v = "DROPPED from LieppOS manifest"
    else: v = "LIEPPOS-ONLY (not in stock)"
    rows.append((*i, ";".join(sorted(s)), ";".join(sorted(t)), v))
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "vintf-instance-ledger.tsv"), "w") as o:
    o.write("format\tpackage\tversion\tinterface\tinstance\tstock_documents\tlieppos_sources\tverdict\n")
    for r in rows: o.write("\t".join(r) + "\n")

# payload check: every rc service in stock vendor/odm init whose binary is absent from stock
missing = []
for d in ("vendor/etc/init", "vendor/etc/init/hw", "vendor/odm/etc/init"):
    dd = os.path.join(P, d)
    if not os.path.isdir(dd): continue
    for f in sorted(os.listdir(dd)):
        if not f.endswith(".rc"): continue
        for m in re.finditer(r"^\s*service\s+(\S+)\s+(\S+)", open(os.path.join(dd, f), errors="replace").read(), re.M):
            b = m.group(2)
            if b.startswith(("/vendor/", "/odm/")):
                loc = os.path.join(P, "vendor", b[len("/vendor/"):]) if b.startswith("/vendor/") else os.path.join(P, "vendor/odm", b[len("/odm/"):])
                if not os.path.lexists(loc): missing.append((f"{d}/{f}", m.group(1), b))
with open(os.path.join(OUT, "absent-service-payloads.tsv"), "w") as o:
    o.write("rc\tservice\tbinary\n")
    for r in missing: o.write("\t".join(r) + "\n")
c = collections.Counter(r[-1] for r in rows)
print(f"stock manifest documents: {len(stock_files)}; stock instances: {len(stock)}; LieppOS instances: {len(target)}")
print(f"LieppOS manifest sources: devtree {dmf}; installed stock fragment blobs: {sum(1 for f in stock_files if f in installed)}")
for k, n in c.most_common(): print(f"  {n:4d}  {k}")
print(f"absent stock service payloads: {len(missing)}")
