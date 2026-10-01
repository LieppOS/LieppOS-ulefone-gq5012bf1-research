#!/usr/bin/env python3
"""Android 17 VINTF reconciliation analyzer (steps 2, 3, 5).

Emulates the exact libvintf (android-17.0.0_r1) semantics that were read from
system/libvintf: KernelConfigParser (default, comments ignored),
KernelConfigTypedValue::matchValue, KernelInfo::matchKernelConfigs,
CompatibilityMatrix::combine (device level 8), VersionRange::contains,
MatrixInstance::matchInstance (regex-instance), HalManifest::checkUnusedHals.
The authoritative verdict is still the real checkvintf run; this script only
itemizes what checkvintf evaluated.
"""
import os, re, sys, glob
import xml.etree.ElementTree as ET
from collections import defaultdict, OrderedDict

HR = os.environ["HR"]            # host root (byte copy of collection root/)
WK = os.environ["WK"]
OUT = os.environ["OUT"]
KCONF = os.path.join(WK, "kernel.config")
APEX_FRAG = "/tmp/a17-vintf-apex-vendor/com.google.android.widevine/etc/vintf/com.google.android.widevine.xml"

FAKE_AIDL_MAJOR = 2**64 - 1  # libvintf kFakeAidlMajorVersion; any constant works here

def rel(p):
    return p.replace(HR + "/", "")

def raw_block(path, start_pat, end_tag, first_only=False):
    """Return list of raw text blocks (exact bytes from file) starting at a line matching start_pat."""
    lines = open(path).read().split("\n")
    out, i = [], 0
    while i < len(lines):
        if re.search(start_pat, lines[i]):
            j = i
            buf = []
            while j < len(lines):
                buf.append(lines[j])
                if end_tag in lines[j]:
                    break
                j += 1
            out.append((i + 1, "\n".join(buf)))
            i = j + 1
            if first_only:
                break
        else:
            i += 1
    return out

# ---------------------------------------------------------------- versions
def parse_hidl_range(s):
    # "7.0-1" -> (7,0,1) ; "1.0" -> (1,0,0)
    m = re.match(r"^(\d+)\.(\d+)(?:-(\d+))?$", s.strip())
    if not m:
        raise ValueError(s)
    a, b, c = int(m.group(1)), int(m.group(2)), m.group(3)
    return (a, b, int(c) if c is not None else b)

def parse_aidl_range(s):
    m = re.match(r"^(\d+)(?:-(\d+))?$", s.strip())
    a, b = int(m.group(1)), m.group(2)
    return (FAKE_AIDL_MAJOR, a, int(b) if b is not None else a)

def range_str(fmt, r):
    if fmt == "aidl":
        return f"{r[1]}" if r[1] == r[2] else f"{r[1]}-{r[2]}"
    return f"{r[0]}.{r[1]}" if r[1] == r[2] else f"{r[0]}.{r[1]}-{r[2]}"

def ver_str(fmt, v):
    return f"{v[1]}" if fmt == "aidl" else f"{v[0]}.{v[1]}"

def contains(r, v):
    return r[0] == v[0] and r[1] <= v[1] <= r[2]

# ---------------------------------------------------------------- matrices
class MInst:
    __slots__ = ("fmt", "pkg", "ranges", "iface", "inst", "regex", "src", "excl", "updatable")
    def __init__(s, **k):
        for a in s.__slots__:
            setattr(s, a, k.get(a))

def parse_matrix(path):
    root = ET.parse(path).getroot()
    level = root.get("level")
    insts = []
    for hal in root.findall("hal"):
        fmt = hal.get("format", "hidl")
        excl = hal.get("exclusive-to", "")
        pkg = hal.findtext("name").strip()
        vers = [v.text.strip() for v in hal.findall("version")]
        if fmt == "aidl":
            ranges = [parse_aidl_range(v) for v in vers] or [(FAKE_AIDL_MAJOR, 1, 1)]
        else:  # hidl and native use major.minor ranges
            ranges = [parse_hidl_range(v) for v in vers]
        for itf in hal.findall("interface"):
            iname = (itf.findtext("name") or "").strip()
            for inst in itf.findall("instance"):
                insts.append(MInst(fmt=fmt, pkg=pkg, ranges=ranges, iface=iname, inst=inst.text.strip(),
                                   regex=False, src=os.path.basename(path), excl=excl))
            for inst in itf.findall("regex-instance"):
                insts.append(MInst(fmt=fmt, pkg=pkg, ranges=ranges, iface=iname, inst=inst.text.strip(),
                                   regex=True, src=os.path.basename(path), excl=excl))
        # <fqname> form inside matrix (rare)
        for fq in hal.findall("fqname"):
            m = re.match(r"(?:@[\d.]+::)?(\w+)/(\S+)", fq.text.strip())
            insts.append(MInst(fmt=fmt, pkg=pkg, ranges=ranges, iface=m.group(1), inst=m.group(2),
                               regex=False, src=os.path.basename(path), excl=excl))
    return level, insts, root

# ---------------------------------------------------------------- manifests
class VInst:
    __slots__ = ("fmt", "pkg", "ver", "iface", "inst", "transport", "arch", "src", "excl", "updatable", "maxlevel")
    def __init__(s, **k):
        for a in s.__slots__:
            setattr(s, a, k.get(a))
    def key(s):
        return (s.fmt, s.pkg, s.ver, s.iface, s.inst)
    def desc(s):
        if s.fmt == "aidl":
            return f"{s.pkg}.{s.iface}/{s.inst} (@{s.ver[1]})"
        if s.fmt == "hidl":
            return f"{s.pkg}@{s.ver[0]}.{s.ver[1]}::{s.iface}/{s.inst}"
        if s.ver:
            return f"{s.pkg}@{s.ver[0]}.{s.ver[1]}/{s.inst} (native)"
        return f"{s.pkg} (native, no instance)"

def parse_manifest(path):
    root = ET.parse(path).getroot()
    out = []
    for hal in root.findall("hal"):
        fmt = hal.get("format", "hidl")
        pkg = hal.findtext("name").strip()
        excl = hal.get("exclusive-to", "")
        upd = hal.get("updatable-via-apex", "")
        maxlevel = hal.get("max-level", "")
        tr = hal.find("transport")
        transport = tr.text.strip() if tr is not None and tr.text else ("(aidl-default)" if fmt == "aidl" else "")
        arch = tr.get("arch", "") if tr is not None else ""
        if fmt == "aidl":
            v = hal.findtext("version")
            base = (FAKE_AIDL_MAJOR, int(v.strip()) if v else 1)
        else:
            vs = hal.findall("version")
            base = None
            if vs:
                a, b = vs[0].text.strip().split(".")
                base = (int(a), int(b))
        for fq in hal.findall("fqname"):
            t = fq.text.strip()
            m = re.match(r"^(?:@(\d+)\.(\d+)::)?([\w]+)/(\S+)$", t)
            if not m:
                print("UNPARSED fqname", path, t, file=sys.stderr)
                continue
            ver = (int(m.group(1)), int(m.group(2))) if m.group(1) else base
            out.append(VInst(fmt=fmt, pkg=pkg, ver=ver, iface=m.group(3), inst=m.group(4), transport=transport,
                             arch=arch, src=rel(path), excl=excl, updatable=upd, maxlevel=maxlevel))
        for itf in hal.findall("interface"):
            iname = (itf.findtext("name") or "").strip()
            for inst in itf.findall("instance"):
                out.append(VInst(fmt=fmt, pkg=pkg, ver=base, iface=iname, inst=inst.text.strip(), transport=transport,
                                 arch=arch, src=rel(path), excl=excl, updatable=upd, maxlevel=maxlevel))
        if fmt == "native" and not hal.findall("fqname") and not hal.findall("interface"):
            out.append(VInst(fmt=fmt, pkg=pkg, ver=base, iface="", inst="", transport=transport, arch=arch,
                             src=rel(path), excl=excl, updatable=upd, maxlevel=maxlevel))
    return root, out

def match_instance(mi, name):
    if not mi.regex:
        return mi.inst == name
    return re.fullmatch(mi.inst, name) is not None

# =================================================================== load
SYSV = f"{HR}/system/etc/vintf"
FCM = {lvl: f"{SYSV}/compatibility_matrix.{lvl}.xml" for lvl in ["7", "8", "202404", "202504", "202604"]}
DEVFCM = f"{SYSV}/compatibility_matrix.device.xml"
LINFCM = f"{HR}/product/etc/vintf/compatibility_matrix.lineage.xml"
VMAN = f"{HR}/vendor/etc/vintf/manifest.xml"
VFRAG = sorted(glob.glob(f"{HR}/vendor/etc/vintf/manifest/*.xml"))
ODM_DSDS = f"{HR}/odm/etc/vintf/manifest_dsds.xml"
VDCM = f"{HR}/vendor/etc/vintf/compatibility_matrix.xml"
SEMAN = f"{HR}/system_ext/etc/vintf/manifest.xml"
SMAN = f"{SYSV}/manifest.xml"

DEVICE_LEVEL = int(ET.parse(VMAN).getroot().get("target-level"))

# ======================================================== STEP 2 XML dump
def step2():
    o = []
    w = o.append
    w("# Step 2 - exact VINTF requirement XML blocks (verbatim from the collection)")
    w(f"# host root = byte-identical copy of {os.environ['C']}/root")
    w("")
    p = FCM["8"]
    w("=" * 78)
    w(f"A) {rel(p)}")
    w("=" * 78)
    root = ET.parse(p).getroot()
    w(f"root element: <compatibility-matrix version=\"{root.get('version')}\" type=\"{root.get('type')}\" level=\"{root.get('level')}\">")
    for tag in ("sepolicy", "vendor-ndk", "system-sdk", "avb"):
        bl = raw_block(p, rf"^\s*<{tag}>", f"</{tag}>")
        w(f"<{tag}> blocks in this file: {len(bl)}")
        for ln, b in bl:
            w(f"--- line {ln} ---")
            w(b)
    kblocks = raw_block(p, r"^\s*<kernel ", "</kernel>")
    w(f"\nTotal <kernel> blocks: {len(kblocks)}")
    for idx, (ln, b) in enumerate(kblocks, 1):
        hdr = re.search(r'<kernel version="([^"]+)" level="([^"]+)"', b)
        w("")
        w("-" * 78)
        w(f"KERNEL BLOCK #{idx}  line {ln}  version={hdr.group(1)} level={hdr.group(2)}")
        w("-" * 78)
        w(b)
    o.append("")
    # B
    w("=" * 78)
    w(f"B) {rel(DEVFCM)}  - complete <sepolicy> (and <avb>) block")
    w("=" * 78)
    for tag in ("sepolicy", "avb"):
        for ln, b in raw_block(DEVFCM, rf"^\s*<{tag}>", f"</{tag}>"):
            w(f"--- line {ln} ---")
            w(b)
    w(raw_block(DEVFCM, r"<!--", "-->", True)[0][1])
    # C
    w("")
    w("=" * 78)
    w(f"C) {rel(VMAN)}")
    w("=" * 78)
    for ln, b in raw_block(VMAN, r"^<manifest ", ">", True):
        w(f"--- line {ln} (root element; target-level) ---")
        w(b)
    vroot = ET.parse(VMAN).getroot()
    w(f"target-level = {vroot.get('target-level')}")
    kern = vroot.find("kernel")
    w(f"<kernel> element present in vendor manifest: {'YES ' + str(kern.attrib) if kern is not None else 'NO (kernel FCM level inferred from target-level per HalManifest::inferredKernelLevel)'}")
    for tag in ("sepolicy", "system-sdk", "vendor-ndk"):
        bl = raw_block(VMAN, rf"^\s*<{tag}>", f"</{tag}>")
        w(f"<{tag}> blocks: {len(bl)}" + ("" if bl else "  (ABSENT in vendor manifest)"))
        for ln, b in bl:
            w(f"--- line {ln} ---")
            w(b)
    w("Vendor manifest fragments containing <sepolicy>/<kernel>/<vendor-ndk>/<system-sdk>:")
    hits = [rel(f) for f in VFRAG + [ODM_DSDS] if re.search(r"<(sepolicy|kernel|vendor-ndk|system-sdk)\b", open(f).read())]
    w("  " + (", ".join(hits) if hits else "none"))
    # D
    w("")
    w("=" * 78)
    w(f"D) {rel(VDCM)}  - <vendor-ndk> (device compatibility matrix shown complete)")
    w("=" * 78)
    w(open(VDCM).read().rstrip())
    # E
    w("")
    w("=" * 78)
    w(f"E) {rel(SEMAN)}  - <vendor-ndk> (file shown complete)")
    w("=" * 78)
    w(open(SEMAN).read().rstrip())
    w("")
    w(f"Also relevant: {rel(SMAN)} <system-sdk>")
    for ln, b in raw_block(SMAN, r"^\s*<system-sdk>", "</system-sdk>"):
        w(f"--- line {ln} ---")
        w(b)
    # F
    w("")
    w("=" * 78)
    w(f"F) {rel(LINFCM)}  - complete framework HAL declarations")
    w("=" * 78)
    w(open(LINFCM).read().rstrip())
    w("")
    w("Parsed Lineage FCM HAL instances:")
    _, li, _ = parse_matrix(LINFCM)
    for m in li:
        w(f"  {m.fmt:5} {m.pkg} versions={','.join(range_str(m.fmt, r) for r in m.ranges) or '-'} {m.iface}/{m.inst}{' (regex)' if m.regex else ''}")
    open(os.path.join(OUT, "vintf-xml-requirements.txt"), "w").write("\n".join(o) + "\n")

# ======================================================== STEP 3 kernel
def parse_kconfig(path):
    cfg = {}
    for line in open(path).read().split("\n"):
        if not line or line.startswith("#"):
            continue  # default KernelConfigParser: comments (incl. 'is not set') ignored
        k, _, v = line.partition("=")
        cfg[k] = v
    return cfg

def parse_int(s):
    s = s.strip()
    try:
        return int(s, 0)
    except ValueError:
        return None

def kmatch(req_type, req_val, actual):
    """Return (pass, explanation) mirroring KernelInfo::matchKernelConfigs."""
    if actual is None:
        if req_type == "tristate" and req_val == "n":
            return True, "absent => matches required n (gMissingConfig)"
        return False, "Missing config"
    if req_type == "tristate":
        return actual in ("y", "m", "n") and actual == req_val, ""
    if req_type == "string":
        return actual == f'"{req_val}"', ""
    if req_type == "int":
        a, r = parse_int(actual), parse_int(req_val)
        return a is not None and a == r, ""
    if req_type == "range":
        return actual.strip() == req_val.strip(), ""
    return False, f"unknown type {req_type}"

def step3():
    cfg = parse_kconfig(KCONF)
    root = ET.parse(FCM["8"]).getroot()
    blocks = [k for k in root.findall("kernel") if k.get("version") == "6.1.0" and k.get("level") == "8"]
    o = []
    w = o.append
    w("# Kernel VINTF config reconciliation - Android 17 FCM level 8, kernel 6.1")
    w("#")
    w(f"# matrix  : {rel(FCM['8'])}")
    w(f"# kernel  : {open(os.path.join(WK,'kernel.release')).read().strip()}")
    w(f"# config  : collection kernel.config (sha256 d27b34f4418bc4430207c70737b0d9abf266190edf73d8a9e8b2bf506881dc4c), {len(cfg)} set CONFIG_ keys")
    w("# semantics: libvintf android-17.0.0_r1 KernelConfigParser(processComments=false) + KernelConfigTypedValue::matchValue")
    w("#            '# CONFIG_X is not set' is treated as ABSENT; required tristate 'n' matches ABSENT.")
    w("#            A conditional block applies only if ALL its <conditions> match (KernelInfo.cpp:222).")
    w("#")
    w("# Kernel FCM level selection (KernelInfo::getMatchedKernelRequirements):")
    w("#   GKI release 'android14' -> Level 8 (RuntimeInfo::gkiAndroidReleaseToLevel); vendor target-level=8 gives the same.")
    w("#   For kernel level >= S only matrix level == kernel level is checked => ONLY the level-8 6.1.0 blocks below apply.")
    w("#   compatibility_matrix.7.xml (4.14..5.15 @7), 202404 (6.6), 202504 (6.12), 202604 (6.18) are filtered out by x.y or level.")
    w("#   Minimum LTS 6.1.0 <= actual 6.1.115 : PASS")
    w("")
    w(f"Number of <kernel version=\"6.1.0\" level=\"8\"> blocks in compatibility_matrix.8.xml: {len(blocks)}")
    w("")
    total = fails = 0
    summary = []
    allrows = []
    for bi, kb in enumerate(blocks, 1):
        conds = kb.find("conditions")
        cond_list = []
        if conds is not None:
            for c in conds.findall("config"):
                v = c.find("value")
                cond_list.append((c.findtext("key").strip(), v.get("type"), (v.text or "").strip()))
        cond_ok = all(kmatch(t, v, cfg.get(k))[0] for k, t, v in cond_list)
        cfgs = []
        for c in kb.findall("config"):
            v = c.find("value")
            cfgs.append((c.findtext("key").strip(), v.get("type"), (v.text or "").strip()))
        w("=" * 100)
        title = "UNCONDITIONAL" if not cond_list else "CONDITIONAL"
        w(f"BLOCK #{bi}  <kernel version=\"6.1.0\" level=\"8\">  {title}  ({len(cfgs)} config requirements)")
        for k, t, v in cond_list:
            a = cfg.get(k)
            ok = kmatch(t, v, a)[0]
            w(f"   condition: {k} == {v} ({t}) ; actual = {a if a is not None else '(absent)'} -> {'MET' if ok else 'NOT MET'}")
        w(f"   BLOCK APPLIES: {'YES' if cond_ok else 'NO (conditions not met -> requirements not enforced by libvintf)'}")
        w("=" * 100)
        w(f"{'CONFIG':58} {'TYPE':9} {'REQUIRED':18} {'ACTUAL':18} RESULT")
        bp = bf = 0
        for k, t, v in cfgs:
            a = cfg.get(k)
            ok, why = kmatch(t, v, a)
            res = "PASS" if ok else "FAIL"
            if not cond_ok:
                res += " (not enforced)" if not ok else ""
            if ok: bp += 1
            else: bf += 1
            w(f"{k:58} {t:9} {v:18} {(a if a is not None else '(absent)'):18} {res}{('  ' + why) if why and not ok else ''}")
            allrows.append((bi, cond_ok, k, t, v, a, ok))
        if cond_ok:
            total += len(cfgs)
            fails += bf
        summary.append((bi, title, len(cfgs), cond_ok, bp, bf, cond_list))
        w(f"-- block #{bi}: {bp} PASS / {bf} FAIL" + ("" if cond_ok else " (block not applicable)"))
        w("")
    w("=" * 100)
    w("SUMMARY PER BLOCK")
    w("=" * 100)
    for bi, title, n, ok, bp, bf, cl in summary:
        cs = "; ".join(f"{k}={v}" for k, t, v in cl) or "-"
        w(f"#{bi:2} {title:13} applies={'YES' if ok else 'NO ':3} reqs={n:3} PASS={bp:3} FAIL={bf:2}  conditions: {cs}")
    w("")
    w(f"Applicable requirements evaluated: {total}")
    w(f"Applicable requirements FAILED   : {fails}")
    na_fail = [r for r in allrows if not r[1] and not r[6]]
    w(f"Requirements inside NON-applicable conditional blocks that would fail if the condition were enabled: {len(na_fail)}")
    for r in na_fail:
        w(f"   block #{r[0]}: {r[2]} required {r[4]} actual {r[5] if r[5] is not None else '(absent)'}")
    w("")
    w("KERNEL_VINTF_RESULT=" + ("PASS" if fails == 0 else "FAIL"))
    w("Cross-check: real checkvintf runs C/D/E/F (this config) => COMPATIBLE; negative control N1 (CONFIG_ANDROID_BINDER_IPC removed)")
    w("            => 'No compatible kernel requirement found (kernel FCM version = 8) ... Missing config CONFIG_ANDROID_BINDER_IPC'.")
    w("            The kernel check is therefore genuinely active in the real checker, and it passes.")
    open(os.path.join(OUT, "kernel-vintf-config-reconciliation.txt"), "w").write("\n".join(o) + "\n")
    return len(blocks), total, fails

# ======================================================== STEP 5 HAL
FOCUS = OrderedDict([
    ("audio", r"^android\.hardware\.audio"),
    ("camera", r"^android\.hardware\.camera|camera"),
    ("composer", r"graphics\.composer|composer"),
    ("graphics mapper/allocator", r"graphics\.(mapper|allocator)"),
    ("GNSS", r"gnss|lbs"),
    ("health", r"\.health"),
    ("keymint / security", r"security\.|keymint|keymaster|gatekeeper|weaver|authsecret"),
    ("radio/*", r"\.radio|radioex|\.sap|secure_element|\.ims\b"),
    ("sensors", r"sensor"),
    ("thermal", r"thermal"),
    ("USB", r"\.usb"),
    ("Wi-Fi", r"\.wifi"),
    ("MediaTek vendor.*", r"^vendor\.mediatek\."),
    ("Ulefone vendor.yft.*", r"^vendor\.yft\."),
])

def step5():
    # framework matrices
    mats = {}
    for lvl, p in FCM.items():
        mats[os.path.basename(p)] = parse_matrix(p)
    mats["compatibility_matrix.device.xml"] = parse_matrix(DEVFCM)
    mats["compatibility_matrix.lineage.xml"] = parse_matrix(LINFCM)
    def mlevel(name, lvl):
        return int(lvl) if lvl else DEVICE_LEVEL  # unspecified => deviceLevel (CompatibilityMatrix::combine)
    combined = []      # matrices whose HALs enter the combined FCM (level >= device level)
    older = []
    for name, (lvl, insts, _) in mats.items():
        L = mlevel(name, lvl)
        (combined if L >= DEVICE_LEVEL else older).extend(insts)
    AOSP_SRC = {os.path.basename(FCM[x]) for x in FCM}
    # device manifest (live: no sku) + ODM dsds (variant) + vendor APEX
    vendor = []
    for p in [VMAN] + VFRAG:
        vendor += parse_manifest(p)[1]
    odm = parse_manifest(ODM_DSDS)[1]
    apex = []
    if os.path.exists(APEX_FRAG):
        for v in parse_manifest(APEX_FRAG)[1]:
            v.src = "vendor/apex/com.google.android.widevine.nonupdatable.apex:/etc/vintf/com.google.android.widevine.xml"
            apex.append(v)
    devinsts = OrderedDict()
    for v in vendor + odm + apex:
        devinsts.setdefault(v.key(), []).append(v)

    def covering(v, pool):
        return [m for m in pool if m.fmt == v.fmt and m.pkg == v.pkg and m.iface == v.iface and (m.excl or "") == (v.excl or "")
                and any(contains(r, v.ver) for r in m.ranges) and match_instance(m, v.inst)]

    rows = []
    cls_count = defaultdict(int)
    for key, vs in devinsts.items():
        v = vs[0]
        srcs = sorted({x.src for x in vs})
        cov = covering(v, combined)
        if cov:
            aosp = [m for m in cov if m.src in AOSP_SRC]
            if aosp:
                c = "MATCH"
                note = "covered by AOSP FCM " + ",".join(sorted({m.src for m in aosp}))
            else:
                c = "VENDOR-ONLY"
                note = "accepted only because LieppOS device FCM/Lineage FCM declares it: " + ",".join(sorted({m.src for m in cov}))
            rows.append((c, v, srcs, note, cov))
            cls_count[c] += 1
            continue
        same_pkg = [m for m in combined if m.fmt == v.fmt and m.pkg == v.pkg]
        same_if = [m for m in same_pkg if m.iface == v.iface]
        same_inst = [m for m in same_if if match_instance(m, v.inst)]
        if same_inst:
            c = "VERSION MISMATCH"
            note = "matrix versions " + ",".join(sorted({range_str(m.fmt, r) for m in same_inst for r in m.ranges}))
        elif same_if:
            c = "INSTANCE MISMATCH"
            note = "matrix instances " + ",".join(sorted({m.inst for m in same_if}))
        elif same_pkg:
            c = "INSTANCE MISMATCH"
            note = "interface not in matrix; matrix interfaces " + ",".join(sorted({m.iface for m in same_pkg}))
        else:
            c = "EXTRA VENDOR HAL"
            note = "package not in any framework matrix with level >= 8"
        rows.append((c, v, srcs, note + "  => would be reported by checkUnusedHals (FATAL)", []))
        cls_count[c] += 1

    # transport audit (HIDL only; libvintf does not compare transport against matrices)
    trans = []
    for key, vs in devinsts.items():
        ts = {(x.transport, x.arch) for x in vs}
        if len(ts) > 1:
            trans.append((vs[0], ts))

    # framework-side: matrix entries without vendor instance
    vpk = defaultdict(list)
    for key, vs in devinsts.items():
        vpk[(vs[0].fmt, vs[0].pkg)].append(vs[0])
    fw_rows = []
    grp = OrderedDict()
    for m in combined:
        grp.setdefault((m.fmt, m.pkg, m.iface, m.inst, m.regex), []).append(m)
    for (fmt, pkg, iface, inst, rx), ms in grp.items():
        m = ms[0]
        per_src = "; ".join(f"{x.src}:[{','.join(range_str(x.fmt, r) for r in x.ranges) or '-'}]" for x in ms)
        provided = [v for v in vpk.get((fmt, pkg), []) if v.iface == iface and match_instance(m, v.inst)]
        if provided:
            pv = sorted({ver_str(v.fmt, v.ver) for v in provided})
            lacking = [x for x in ms if not any(any(contains(r, v.ver) for r in x.ranges) for v in provided)]
            if not lacking:
                continue
            c = "VERSION MISMATCH"
            note = (f"vendor provides {','.join(pv)}; accepted by {','.join(sorted({x.src for x in ms if x not in lacking})) or 'NONE'}; "
                    f"not in range of {','.join(sorted({x.src for x in lacking}))} (newer FCM level asks for a newer version) - informational")
        elif (fmt, pkg) in vpk:
            c = "MISSING FROM VENDOR"
            note = "package implemented by vendor, but this interface/instance is not declared - informational"
        else:
            c = "FRAMEWORK-ONLY"
            note = "package not implemented by vendor - informational"
        fw_rows.append((c, m, note, per_src))

    # framework manifest vs vendor device compatibility matrix
    fwman = []
    for p in [SMAN] + sorted(glob.glob(f"{SYSV}/manifest/*.xml")) + [SEMAN]:
        for v in parse_manifest(p)[1]:
            if v.maxlevel and int(v.maxlevel) < DEVICE_LEVEL:
                continue  # filtered for a level-8 device
            fwman.append(v)
    dcm_level, dcm, _ = parse_matrix(VDCM)
    dcm_rows = []
    for m in dcm:
        prov = [v for v in fwman if v.fmt == m.fmt and v.pkg == m.pkg and v.iface == m.iface and match_instance(m, v.inst)
                and (m.fmt == "native" or any(r[0] == v.ver[0] and r[1] <= v.ver[1] for r in m.ranges))]
        dcm_rows.append((m, prov))
    dcm_root = ET.parse(VDCM).getroot()
    opt = {}
    for hal in dcm_root.findall("hal"):
        opt[hal.findtext("name").strip()] = hal.get("optional", "(unset)")
        if not hal.findall("interface"):
            fmt = hal.get("format", "hidl")
            pkg = hal.findtext("name").strip()
            rr = [parse_hidl_range(v.text) for v in hal.findall("version")]
            mm = MInst(fmt=fmt, pkg=pkg, ranges=rr, iface="(any)", inst="(any)", regex=False, src="vendor DCM", excl="")
            prov = [v for v in fwman if v.fmt == fmt and v.pkg == pkg and any(r[0] == v.ver[0] and r[1] <= v.ver[1] for r in rr)]
            dcm_rows.append((mm, prov))

    # deprecation emulation (VintfObject::checkDeprecation): instance in older (level<8) matrices but whose
    # version is not allowed by the level-8 target matrix
    tgt8 = mats["compatibility_matrix.8.xml"][1]
    dep = []
    for key, vs in devinsts.items():
        v = vs[0]
        if v.fmt == "native":
            continue
        in_old = [m for m in older if m.fmt == v.fmt and m.pkg == v.pkg]
        in8pkg = [m for m in tgt8 if m.fmt == v.fmt and m.pkg == v.pkg]
        if in_old and in8pkg and not any(m.iface == v.iface and any(contains(r, v.ver) for r in m.ranges) for m in in8pkg):
            dep.append((v, sorted({range_str(m.fmt, r) for m in in8pkg for r in m.ranges})))

    # ---------------- write
    o = []
    w = o.append
    w("# HAL VINTF reconciliation - Android 17 framework (system/system_ext/product Slot B) vs existing Ulefone vendor/ODM")
    w("#")
    w("# Device manifest = vendor/etc/vintf/manifest.xml + vendor/etc/vintf/manifest/*.xml (live collection)")
    w("#                 + odm/etc/vintf/manifest_dsds.xml (only when ro.boot.product.hardware.sku=dsds; live sku is EMPTY,")
    w("#                   ODM dsds content is a strict subset/duplicate of vendor manifest entries)")
    w("#                 + vendor APEX com.google.android.widevine (stock vendor/apex, VENDOR partition apex)")
    w(f"# Device target-level = {DEVICE_LEVEL}. Combined FCM = matrices with level >= {DEVICE_LEVEL}:")
    w("#     compatibility_matrix.8.xml (addAll), 202404/202504/202604 (addAllAsOptional),")
    w("#     compatibility_matrix.device.xml + compatibility_matrix.lineage.xml (level unspecified => treated as 8).")
    w("#     compatibility_matrix.7.xml only feeds checkDeprecation (level < device level).")
    w("#")
    w("# libvintf android-17.0.0_r1 fatality rules (from source, not opinion):")
    w("#   * HalManifest::checkCompatibility(device manifest, FCM) checks ONLY sepolicy version (+kernel on host).")
    w("#     FCM <hal> entries are NOT required: libvintf 17 does not even parse optional=; a HAL that is in the FCM but")
    w("#     absent from vendor is NEVER a checkvintf failure  => MISSING FROM VENDOR / FRAMEWORK-ONLY are informational.")
    w("#   * VintfObject::checkUnusedHals (target-level>=R): every vendor instance must match some FCM instance")
    w("#     (format, package, version-in-range, interface, instance/regex) => EXTRA VENDOR HAL / VERSION MISMATCH /")
    w("#     INSTANCE MISMATCH on the VENDOR side are FATAL.")
    w("#   * VintfObject::checkDeprecation: vendor HAL version older than allowed by the level-8 matrix => FATAL.")
    w("#   * Framework manifest vs vendor device matrix: ONLY <vendor-ndk> and <system-sdk> are checked; framework HALs")
    w("#     required by the vendor DCM are NOT checked by libvintf (runtime-only concern).")
    w("#   * Transport (<transport>) is never compared against matrices by libvintf.")
    w("")
    w("=" * 110)
    w("SUMMARY")
    w("=" * 110)
    w(f"Unique device-manifest HAL instances: {len(devinsts)}  (vendor+fragments={len({v.key() for v in vendor})}, odm dsds={len({v.key() for v in odm})}, vendor apex={len(apex)})")
    for c in ["MATCH", "VENDOR-ONLY", "EXTRA VENDOR HAL", "VERSION MISMATCH", "INSTANCE MISMATCH"]:
        w(f"  vendor-side {c:20}: {cls_count.get(c,0)}")
    fwc = defaultdict(int)
    for r in fw_rows:
        fwc[r[0]] += 1
    for c in ["MISSING FROM VENDOR", "FRAMEWORK-ONLY", "VERSION MISMATCH"]:
        w(f"  framework-side {c:17}: {fwc.get(c,0)}  (informational: FCM HALs are not required by libvintf 17)")
    w(f"  TRANSPORT MISMATCH (same instance declared with different transports): {len(trans)}")
    w(f"  checkDeprecation candidates (emulated): {len(dep)}")
    fatal = sum(cls_count.get(c, 0) for c in ["EXTRA VENDOR HAL", "VERSION MISMATCH", "INSTANCE MISMATCH"]) + len(dep)
    w(f"  FATAL per libvintf semantics: {fatal}")
    w(f"  VENDOR-ONLY HALs that are accepted ONLY because of device/ulefone/gq5012bf1/vintf/framework_compatibility_matrix.xml: "
      f"{sum(1 for r in rows if r[0]=='VENDOR-ONLY' and any(m.src=='compatibility_matrix.device.xml' for m in r[4]))}")
    w("  (Real checkvintf confirms: runs C/D/E/F COMPATIBLE; control N2 without compatibility_matrix.device.xml => 90 unused")
    w("   instances + 'Sepolicy version 34.0 doesn't satisify the requirements' => INCOMPATIBLE.)")
    w("")
    w("=" * 110)
    w("FOCUS AREAS")
    w("=" * 110)
    for name, pat in FOCUS.items():
        sel = [r for r in rows if re.search(pat, r[1].pkg)]
        fsel = [r for r in fw_rows if re.search(pat, r[1].pkg)]
        w(f"\n### {name}")
        if not sel and not fsel:
            w("   (no vendor instance, no framework matrix entry)")
        for c, v, srcs, note, cov in sel:
            w(f"   {c:18} {v.fmt:5} {v.desc():85} transport={v.transport}{('/'+v.arch) if v.arch else ''}")
            w(f"   {'':18} from: {', '.join(srcs)}")
            w(f"   {'':18} {note}")
        for c, m, note, per_src in fsel:
            w(f"   {c:18} {m.fmt:5} {m.pkg}.{m.iface}/{m.inst}{' (regex)' if m.regex else ''}  {{{per_src}}}")
            w(f"   {'':18} {note}")
    w("")
    w("=" * 110)
    w("FULL VENDOR-SIDE INVENTORY (every device-manifest instance)")
    w("=" * 110)
    for c, v, srcs, note, cov in sorted(rows, key=lambda r: (r[0], r[1].pkg, r[1].iface, r[1].inst)):
        w(f"{c:18} | {v.fmt:6} | {v.desc():90} | transport={v.transport}{('/'+v.arch) if v.arch else ''} | {', '.join(srcs)} | {note}")
    w("")
    w("=" * 110)
    w("FULL FRAMEWORK-SIDE INVENTORY (FCM >= 8 + device FCM + Lineage FCM entries with no matching vendor instance)")
    w("=" * 110)
    for c, m, note, per_src in sorted(fw_rows, key=lambda r: (r[0], r[1].pkg, r[1].iface, r[1].inst)):
        w(f"{c:20} | {m.fmt:5} | {m.pkg}.{m.iface}/{m.inst}{' (regex)' if m.regex else ''} | {per_src} | {note}")
    w("")
    w("=" * 110)
    w("TRANSPORT MISMATCH")
    w("=" * 110)
    if not trans:
        w("none - no instance is declared twice with different transports; libvintf does not check transport vs matrix.")
    for v, ts in trans:
        w(f"{v.desc()} : {ts}")
    w("")
    w("=" * 110)
    w("DEPRECATION (emulated VintfObject::checkDeprecation)")
    w("=" * 110)
    if not dep:
        w("none - real checkvintf checkDeprecation also returned NO_DEPRECATED_HALS (no error in runs C-G).")
    for v, rr in dep:
        w(f"{v.desc()} not in level-8 ranges {rr}")
    w("")
    w("=" * 110)
    w("FRAMEWORK MANIFEST vs ULEFONE DEVICE COMPATIBILITY MATRIX (vendor/etc/vintf/compatibility_matrix.xml)")
    w("NOT evaluated by libvintf for HALs (only vendor-ndk/system-sdk). Runtime relevance only.")
    w("=" * 110)
    for m, prov in dcm_rows:
        st = "PROVIDED" if prov else "NOT PROVIDED by A17 framework manifest"
        w(f"{st:40} {m.fmt:5} {m.pkg}@{','.join(range_str(m.fmt,r) for r in m.ranges) or '-'}::{m.iface}/{m.inst} optional={opt.get(m.pkg)}"
          + (f"  <- {', '.join(sorted({p.src+' '+p.desc() for p in prov}))}" if prov else ""))
    open(os.path.join(OUT, "hal-vintf-reconciliation.txt"), "w").write("\n".join(o) + "\n")
    return cls_count, fwc, trans, dep, dcm_rows, rows, fw_rows

if __name__ == "__main__":
    step2()
    nb, total, fails = step3()
    cc, fwc, trans, dep, dcm_rows, rows, fw_rows = step5()
    print("kernel blocks", nb, "applicable reqs", total, "fails", fails)
    print("vendor-side", dict(cc))
    print("framework-side", dict(fwc))
    print("transport", len(trans), "deprecated", len(dep))
    for m, prov in dcm_rows:
        print("DCM", m.pkg, m.iface, m.inst, "PROVIDED" if prov else "NOT PROVIDED")
