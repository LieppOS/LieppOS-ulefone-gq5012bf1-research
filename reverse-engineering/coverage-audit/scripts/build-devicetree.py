#!/usr/bin/env python3
"""Axis 2: map every device-tree compatible on GQ5012BF1 to RE coverage.

Universe
  The merged *live* device tree
  `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`, rebuilt
  offline from the vendor_boot FDT (`fdt-00-off-03b76040.dtb`) plus the single
  dtbo entry (`entry-00-id-00000000-rev-00000000.dtbo`); see
  `extraction-manifest.txt` beside it.  Nodes are reconstructed by brace
  nesting; `status` is tracked so inert hardware stays distinguishable.

Ownership resolution (every step records its evidence in the row)
  1. CURATED   audit override for a compatible worth naming individually
  2. PACK      a workspace component quotes the compatible in its own prose or
               inventory -> narrowest scope wins, co-owners recorded
  3. RESEARCH  only a research-repo document quotes it -> class B
  4. DRIVER    unquoted, but it resolves to a shipped kernel module already
               classified on axis 1 (`kernel-modules.tsv`) -> that class travels
  5. FAMILY    unquoted platform-internals; `FAMILIES` names the owner/class and
               carries the per-family justification into the row
  6. DISABLED  node present but every instance `status="disabled"` -> D
  6. otherwise class E (real coverage gap)

Coverage classes (device-tree axis)
  A dedicated component documents this compatible (claims <=3 compatibles)
  B covered as part of a broader documented subsystem scope
  C generic platform-internals: no board-specific behaviour to reverse-engineer
  D node shipped but disabled on this board - no port work implied
  E unmapped - genuine coverage gap

Output: coverage-audit/device-tree.tsv (+ summary block appended to
notes/DEVICE-TREE.md by --summary).
"""
from __future__ import annotations

import collections
import csv
import os
import re
import sys

ROOT = "/home/armol/androido_dalykai/LieppOS custom ROM"
AUDIT = os.path.join(ROOT, "ulefone-gq5012bf1-research/reverse-engineering/"
                            "coverage-audit")
MERGED_DTS = os.path.join(
    ROOT, "ulefone-gq5012bf1-research/workspace/phase4-connfem-hardware/"
          "offline-dt/gq5012bf1-merged.dts")
CLAIMS = os.path.join(AUDIT, "audit-evidence/harvested-pack-dt-claims.tsv")
MODULES = os.path.join(AUDIT, "kernel-modules.tsv")
OUT = os.path.join(AUDIT, "device-tree.tsv")

NODE = re.compile(r"^([a-zA-Z0-9_@][\w,.@+-]*|/)\s*\{")
PROP = re.compile(r'^([a-zA-Z_][\w,-]*)\s*=\s*(.*)$')

# Families for compatibles that no pack quotes and that do not resolve to a
# shipped module name (regex, owner, class, justification).  Each family names the owner (or COVERED-GENERIC) plus the
# justification that is written into the row's `evidence` field, so a reader can
# audit *why* the node needed no dedicated reverse-engineering work.
FAMILIES = [
    (r"^(disp[-_]|mdp_|mml|drm_wv$|mtkfb$|vout|vdin|vdo$|rdma\d|wrot|wdma|"
     r"mmsys|cmdq|gce$|mu3d|vdec|venc|fdu$|g2d$|mju$|dsi\d|mipi_tx_config\d?"
     r"|disp-sec-aidctl$|mtk_sec_video_path_support$|mtk_svp_on_mtee_support$|"
     r"mdp$|mmlw|mmsys|jpgenc|mtk-jpgenc)",
     "MEDIATEK-DRM", "B",
     "MTK DDI/MDP display-pipeline block - travels with the vendor mtk-drm/DDP "
     "stack (DONE/MEDIATEK-DRM, DONE/BACKLIGHT-DISPLAY-GLUE); panel-specific work "
     "lives in VTDR6115-DISPLAY / CO5300-REAR-DISPLAY / HYNITRON-REAR-TOUCH"),
    (r"^(cam[-_]|camsv|mraw|ccd|ccucammain|seninf|hcp\d+sp|imgsensor|"
     r"mtk[-_](cam|imgsensor|v4l2)|pda|ccam\d|rms?\d)",
     "CAMERA-HAL-ISP", "B",
     "MTK camera pipe sub-block (FE/seninf/RMS/CCU) - the kernel side is owned at "
     "module level by PARTIAL/CAMERA-HAL-ISP and the sensor sub-drivers by "
     "DONE/CAMERA-IMX989, CAMERA-OV64B, CAMERA-S5KJN1*, DW9781C-OIS, CAMERA-EEPROMS"),
    (r"^(smi[-_]larb|smi[-_](pd|testcase)|smi$|larb|m4u|infracfg|mcucfg|topckgen|"
     r"topmisc|apmixed|.*cldma.*|infra_|mbist|lastbus|emi[-_]|bpi|bsi|pwrmcu_partition|"
     r"ccu_rproc|sspm$|mcupm|gpueb|adsp|slcmtsys|mtcmos|wakeup|cpu[-_]otp|nvmem|"
     r"efuse|pinctrl|gpio$|eint|gic|sys_cirq|sys_timer|mtk[-_]mbox|mbox_ipid|"
     r"i2c$|mt6\d{3}-(uart|eint|emicen|usb)|i3c|spi|uarthub|early_port_dma|cqdma|masp$)",
     "COVERED-GENERIC", "C",
     "MTK EMI/SMMU/infracfg/clkgen/pinctrl/tinysys doorbell platform glue - "
     "reference-board platform source, no GQ5012BF1-specific behaviour to recover"),
    (r"^(pwrmcu|scp[-_]|lpm|cpupm|sramrom|srclken|sleep$|eas-info|mtk-pmsr|pbm$|"
     r"mtk-lkg|dvfsrc|dvfs|perfobj|cpu_bw|cpu_cost|proc_thread|scheduler|qos|"
     r"mt6893-qos|mt6877-emicen|cache_power_mgmt|idle_debug|speech-usip-mem|"
     r"apcldma|apu[-_](mem|top)|apusys|mdla|mcusys|.*larb|gpu_(qos|fdvfs)|"
     r"operating-points)",
     "COVERED-GENERIC", "C",
     "MTK power/performance framework node (PMPUF/PBM/SCPSYS/LPM/DVFSRC/cpufreq "
     "OPP) - platform tuning, carried as vendor source; device thermal policy is a "
     "separate axis (PARTIAL/THERMAL-POWER-HAL, COOLING-HARDWARE)"),
    (r"^(dbg_|dfd|tracker|bus_(dbg|tracer)|met_|mrdump|mtk_ctd$|sram_dbg|md2md|"
     r".*_dbg$|ccci_dbg)",
     "COVERED-GENERIC", "C",
     "vendor debug/trace instrumentation (MET/DFD/bustracer/CTD) - same never-loaded "
     "debug-eng class as the axis-1 `met_*` modules"),
    (r"^(svp$|.*sec-page.*|.*sec-region.*|devapc|security_ao|trusted_mem|"
     r"memory-ffa|memory-ssmr|page-based-v2|tee-mmap-by-page|"
     r"protected-memory-allocator|vcp-io-sec)",
     "COVERED-GENERIC", "C",
     "secure-memory / TEE-side glue behind the GenieZone + FF-A boundary already "
     "documented by DONE/GZ-*, FFA-V10, TMEM-FFA and PARTIAL/KEYSTORE-VOLD-KEYMINT, "
     "MICROARRAY-FP-TEE; the proprietary TEE OS internals are not a ROM-port target"),
    (r"^((ap|md)_ccif|md2md|ccci_md_scp|mddriver|md1_sim\d_hot_plug|.*sim\d.*eint)",
     "CCCI-KERNEL", "B",
     "AP<->MD chip-interface / modem IPCI / SIM hot-plug EINT - transport documented "
     "by DONE/CCCI-KERNEL, CCMNI-KERNEL, DPMAIF-KERNEL, MODEM-KERNEL-TRANSPORT and "
     "PARTIAL/ESIM-EUICC-ABSENCE (no eSIM fitted)"),
    (r"^(therm_intf|.*cooler|thermal_|mtk[-_]ts)",
     "COVERED-GENERIC", "C",
     "MTK in-kernel thermal interface / software-cooler node; the device thermal "
     "design itself is a separate axis (PARTIAL/THERMAL-POWER-HAL, COOLING-HARDWARE, "
     "INTERNAL-THERMAL-USB)"),
    (r"^vcp-io-", "VENDOR-BLOB-HAL-INVENTORY", "C",
     "MediaTek VCP/VPU media-codec IOMMU domain - same classification as the "
     "mtk_vcodec-*/mtk-vcu modules on the kernel axis: carried as the vendor media "
     "stack, no board-specific RE"),
    (r"^charger,|^pmic_tia$|^kp$|^sleep$|^kbd$", "MT6375-CHARGER", "B",
     "PMIC charger-mode / misc-input node - PMIC register side documented by "
     "PARTIAL/MT6375-CHARGER and PARTIAL/BATTERY-PACK, PD/PPS side by PD-PPS-UFCS, "
     "pumps by SC8571-CHARGE-PUMP / SC8510-BIDIRECTIONAL-CHARGE-PUMP"),
    (r"^(arm,|psci|pci|smc-invoker|trusted-keys|firmware|reserved$|memory$|"
     r"chosen|soc$|clk_|clock|fixed-|regulator|syscon|simple-|mmio-sram|"
     r"shared-dma-pool|android,)",
     "COVERED-GENERIC", "C",
     "Arm/GKI/Android core-infra node (GIC/PMU/PSI/bus/clock/regulator/firmware "
     "image map) - nothing board-specific to reverse-engineer"),
]

# Individual compatibles worth naming explicitly.
CURATED = {
    "arm,mali-valhall": ("UNMAPPED", "E",
                         "GPU KMD/DT scope is an open decision: kernel axis left "
                         "mali_kbase_mt6878_r44.ko with only a prose mention in "
                         "TMEM-FFA (see notes/KERNEL-MODULES.md conclusion 3)"),
    "mediatek,mali": ("UNMAPPED", "E", "see arm,mali-valhall - GPU stack has no owner"),
    "mediatek,g3d_brisket": ("UNMAPPED", "E",
                            "GPU DVFS/brisket companion of arm,mali-valhall"),
    "microtrust,utos": ("COVERED-GENERIC", "C",
                        "MicroTrust UTOs TEE OS instance; CA-side interface documented "
                        "by DONE/GZ-TRANSPORT, FFA-V10, TMEM-FFA and PARTIAL/"
                        "KEYSTORE-VOLD-KEYMINT + MICROARRAY-FP-TEE (TrustKernel TA)"),
    "trustonic,mobicore": ("COVERED-GENERIC", "C",
                           "legacy Mobicore TEE compat retained by the vendor DTB; no "
                           "Mobicore driver ships in vendor_dlkm - live TEE is MicroTrust "
                           "UTOs (see microtrust,utos)"),
}


def parse(path: str):
    """return {node_path: {"c": [compatibles], "st": status}}"""
    stack: list[str] = []
    nodes: dict[str, dict] = {}
    buf: str | None = None
    for raw in open(path, encoding="utf-8", errors="replace"):
        s = raw.strip()
        if not s or s.startswith(("//", "/*", "*", "#")):
            continue
        m = NODE.match(s)
        if m and not s.startswith("}"):
            stack.append(m.group(1))
            nodes.setdefault("/".join(stack), {"c": [], "st": ""})
            buf = None
            continue
        if s.startswith("}"):
            if stack:
                stack.pop()
            buf = None
            continue
        key = "/".join(stack) or "/"
        if buf is not None:
            nodes[buf]["c"] += re.findall(r'"([^"]+)"', s)
            if s.rstrip().endswith(";"):
                buf = None
            continue
        if s.startswith("compatible"):
            node = nodes.setdefault(key, {"c": [], "st": ""})
            node["c"] += re.findall(r'"([^"]+)"', s)
            buf = None if s.rstrip().endswith(";") else key
            continue
        pm = PROP.match(s.rstrip(";"))
        if pm and pm.group(1) == "status":
            mm = re.match(r'^"([^"]*)"', pm.group(2))
            if mm and key in nodes:
                nodes[key]["st"] = mm.group(1)
    return {k: v for k, v in nodes.items() if v["c"]}


def main() -> int:
    nodes = parse(MERGED_DTS)
    uni: dict[str, dict] = {}
    for path, info in nodes.items():
        for c in info["c"]:
            r = uni.setdefault(c, {"n": 0, "enabled": 0, "disabled": 0, "sample": path})
            r["n"] += 1
            st = info["st"].lower()
            if st.startswith("disabled"):
                r["disabled"] += 1
            else:
                r["enabled"] += 1

    claims: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for r in csv.DictReader(open(CLAIMS), delimiter="\t"):
        claims[r["compatible"]].append((r["component"], r["kind"]))

    modtoks: dict[str, set[str]] = collections.defaultdict(set)
    modrow: dict[str, dict] = {}
    for r in csv.DictReader(open(MODULES), delimiter="\t"):
        base = r["module"][:-3].lower()
        modrow[base] = r
        for t in {x for x in re.split(r"[-_]", base) if len(x) >= 5} | {base.replace("-", "_")}:
            modtoks[t].add(base)

    breadth = collections.Counter()
    for c, cs in claims.items():
        for comp_name in {k for k, kind in cs}:
            breadth[comp_name] += 1

    rows = []
    for c, info in sorted(uni.items()):
        vendor, _, dev = c.partition(",")
        vendors, last = [vendor.strip()], (dev or c).strip().lower()
        cur = CURATED.get(c)
        owners = sorted({k for k, kind in claims.get(c, [])
                         if not k.startswith("research:")})
        researchers = sorted({k for k, kind in claims.get(c, [])
                             if k.startswith("research:")})
        drv = sorted({m for t in {x for x in re.split(r"[_.\-]", last.lower()) if len(x) >= 5}
                      | {last.lower().replace("-", "_").replace(".", "_")}
                      for m in modtoks.get(t, set())})
        ev: list[str] = []
        if cur:
            comp, cls = cur[0], cur[1]
            ev.append("curated:" + cur[2])
            if owners:
                ev.append("also-claimed-by:" + ";".join(owners[:3])[:120])
        elif owners:
            narrowest = min(owners, key=lambda p: (breadth[p], p))
            n = breadth[narrowest]
            comp, cls = narrowest, "A" if n <= 3 else "B"
            ev.append(f"pack-claims:{narrowest}({n}-compatibles)")
            if len(owners) > 1:
                ev.append("co-owners:" + ";".join(p for p in owners if p != narrowest)[:150])
            if researchers:
                ev.append("research-docs:" + str(len(researchers)))
        elif researchers:
            comp, cls = researchers[0], "B"
            ev.append(f"research-doc:{researchers[0]}({len(researchers)}-docs)")
        elif drv:
            owner = modrow[drv[0]]
            comp = ("COVERED-GENERIC" if owner["component"] == "COVERED-GENERIC"
                    else owner["component"])
            cls = owner["coverage"] if owner["coverage"] in "ABC" else "C"
            ev.append(f"driver:{','.join(drv[:3])}({owner['coverage']})")
        elif any(re.match(p, c) or re.match(p, last) for p, _, _, _ in FAMILIES):
            owner, fcls, why = next((o, cl, w) for p, o, cl, w in FAMILIES
                                   if re.match(p, c) or re.match(p, last))
            comp, cls = owner, fcls
            ev.append("family:" + why)
        elif info["disabled"] and not info["enabled"]:
            comp, cls = "DISABLED-ON-BOARD", "D"
            ev.append("status=disabled-on-all-instances")
        else:
            comp, cls = "", "E"
            ev.append("no-claim-no-driver-no-family")
        rows.append({
            "compatible": c,
            "vendor": vendors[0],
            "device": last,
            "coverage": cls,
            "component": comp or "UNMAPPED",
            "nodes": str(info["n"]),
            "nodes_enabled": str(info["enabled"]),
            "nodes_disabled": str(info["disabled"]),
            "sample_node": info["sample"],
            "driver_candidates": ",".join(drv[:4]),
            "claim_count": str(len(claims.get(c, []))),
            "evidence": ";".join(ev),
        })
    rows.sort(key=lambda r: (r["coverage"], r["compatible"]))
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    cov = collections.Counter(r["coverage"] for r in rows)
    print(f"compatibles={len(rows)} nodes={sum(int(r['nodes']) for r in rows)} "
          f"coverage={dict(cov)}")
    for k in ("D", "E"):
        print(k, [r["compatible"] for r in rows if r["coverage"] == k][:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
