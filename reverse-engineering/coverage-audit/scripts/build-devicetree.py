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

Output: coverage-audit/device-tree.tsv plus notes/DEVICE-TREE.md, which is
regenerated from the TSV on every run so its totals cannot drift from the data.
"""
from __future__ import annotations

import collections
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_fdt as libfdt  # noqa: E402
from accelerator_owners import DT_OVERRIDES

ROOT = "/home/armol/androido_dalykai/LieppOS custom ROM"
AUDIT = os.path.join(ROOT, "ulefone-gq5012bf1-research/reverse-engineering/"
                            "coverage-audit")
OFFLINE_DT = os.path.join(
    ROOT, "ulefone-gq5012bf1-research/workspace/phase4-connfem-hardware/offline-dt")
MERGED_DTB = os.path.join(OFFLINE_DT, "gq5012bf1-merged.dtb")
BASE_DTB = os.path.join(OFFLINE_DT, "vendor_boot/fdt-00-off-03b76040.dtb")
OVERLAY_DTBO = os.path.join(
    OFFLINE_DT, "dtbo/entry-00-id-00000000-rev-00000000.dtbo")
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
    "richtek,rt5133": ("RT5133-POWER-IC", "B",
                        "declared MTK reference client at 5-0018; stock capture is unbound, "
                        "no RT5133 rails registered/consumed; static driver scope closed; "
                        "see notes/RT5133-CORRECTION.md"),
    "chipone-tddi": ("COVERED-GENERIC", "D",
                       "enabled reference-board TDDI node has no shipped driver; fitted main/rear touch are FT3680/Hynitron"),
    "tchip,ilitek": ("COVERED-GENERIC", "D",
                       "enabled reference-board TDDI node has no shipped driver; fitted main/rear touch are FT3680/Hynitron"),
    "microtrust,utos": ("COVERED-GENERIC", "C",
                        "MicroTrust UTOs TEE OS instance; CA-side interface documented "
                        "by DONE/GZ-TRANSPORT, FFA-V10, TMEM-FFA and PARTIAL/"
                        "KEYSTORE-VOLD-KEYMINT + MICROARRAY-FP-TEE (TrustKernel TA)"),
    "trustonic,mobicore": ("COVERED-GENERIC", "C",
                           "legacy Mobicore TEE compat retained by the vendor DTB; no "
                           "Mobicore driver ships in vendor_dlkm - live TEE is MicroTrust "
                           "UTOs (see microtrust,utos)"),
}

# Research-document labels are evidence sources, never component names.  If a
# compatible has only a research citation, resolve it through these explicit
# architecture families or classify it generic/reference rather than inventing
# a pseudo-component.
RESEARCH_COMPAT = [
    (r"^(focaltech,fp|mediatek,goodix-fp)$", "COVERED-GENERIC", "D", "alternative fingerprint DT baggage; fitted path is MicroArray/Madev"),
    (r"^focaltech,fts$", "FT3680-TOUCH", "A", "fitted FocalTech touch controller"),
    (r"^mediatek,flashlight_core$", "AW36515-FLASH", "B", "shared camera/IR flashlight framework"),
    (r"regulator-vibrator", "HAPTICS", "B", "PMIC vibrator provider"),
    (r"mt63(19|63|69)|mt6375|mt6685|charger|power-throttling|mtk-bp-thl|auxadc", "THERMAL-POWER-HAL", "B", "PMIC/charger/thermal-power platform node"),
    (r"camera-pda|imgsensor|seninf", "CAMERA-HAL-ISP", "B", "camera ISP/sensor framework node"),
    (r"ccci|md1_|md_auxadc|mdpm|mrdump", "MODEM-KERNEL-TRANSPORT", "B", "modem transport/power/debug node"),
    (r"dsi|disp_dsi|mipi_tx", "MEDIATEK-DRM", "B", "display/DSI platform node"),
    (r"geniezone", "GZ-TRANSPORT", "B", "GenieZone hypervisor transport node"),
    (r"sec_video|svp_|tui_", "TRUSTKERNEL-TEE", "B", "secure display/trusted UI boundary"),
    (r"mt6369-sound", "MT6369-AUDIO-CODEC", "B", "MT6369 audio machine node"),
    (r"gpio_usage_mapping", "DTB-DTBO", "B", "board GPIO ownership map"),
    (r"apusys|iommu|dramc|emichn|emiisu|emimpu|vpu|soc-offload|smi|timer|wdt|simple-mfd|syscon|scpsys", "COVERED-GENERIC", "C", "generic MTK SoC/IOMMU/memory/timer infrastructure"),
]


# Physical function for the board-specific hardware nodes, keyed by compatible.
# Anything not listed gets the honest "see <owner> inventory" placeholder instead
# of an invented function; axis 3 (hardware.tsv) carries the per-device detail.
FUNCTIONS = [
    (r"^mediatek,mt6375$", "main PMIC: charger/PE/PD/regulators/TCPC host"),
    (r"^mediatek,mt6375-(chg|gauge)$", "PMIC charging controller / fuel gauge"),
    (r"^mediatek,mt6375-tcpc$", "USB Type-C Port Controller (PMIC-embedded)"),
    (r"^richtek,rt5133$", "inactive MTK reference LDO capability; declared client unbound, no registered rails or external consumers; physical population unproved"),
    (r"^richtek,rt6160", "RF transceiver aux/IBAT debug interface"),
    (r"^mediatek,mt63(19|63|69)", "secondary PMIC (MT6319/MT6363/MT6369) regulator/keys/audio"),
    (r"^mediatek,mt6685", "core PMIC/clock-buffer/RTC companion"),
    (r"^(chipone-tddi|hynitron,hyn_ts|tchip,ilitek)$", "display touch controller"),
    (r"^mediatek,imgsensor$", "camera image sensor (CCI-probed)"),
    (r"^mediatek,camera_eeprom$", "camera module EEPROM"),
    (r"^mediatek,(main|main2|main4)_vcm$", "camera voice-coil-motor autofocus driver"),
    (r"^mediatek,dw9781c$", "camera OIS/VCM driver (DW9781C)"),
    (r"^sh,sh366003$", "Sino Wealth 2S battery-pack fuel gauge"),
    (r"^awinic,rgb,aw2013$", "RGB indicator LED driver"),
    (r"^will,wl2864c_pmu$", "bound camera-rail LDO/reset provider (WL2864C/WL2868C)"),
    (r"^sc,sc8571", "SC8571 direct-charge pump endpoint (master/slave)"),
    (r"^mediatek,aw3651[58]", "haptic/LED driver (AW3651x family)"),
    (r"^mediatek,i2c_lcd_bias$", "display bias (OCP2131) power IC"),
    (r"^sc,sc8510$", "bidirectional charge pump"),
    (r"^mediatek,speaker_amp$", "smart speaker amplifier"),
    (r"^st,st21nfc$", "NFC controller (ST21NFC)"),
    (r"^mediatek,tiny2c_usb$", "USB2 TinyIPC bridge (FM78100 reader/adapter)"),
    (r"^mediatek,mt63(69|63)-sound$", "audio codec (MT6369)"),
]


def parse(path: str) -> dict[str, dict]:
    """return {node_path: {"c": [compatibles], "st": status, "bus", "addr", "name"}}

    Uses the authoritative binary device tree (`lib-fdt`), so bus/address and
    `status` come from the blob the bootloader actually installs rather than from
    a re-parse of dtc text.
    """
    nodes: dict[str, dict] = {}
    for n in libfdt.walk(path):
        if "compatible" not in n["props"]:
            continue
        par_name = n["path"].rsplit("/", 2)[-2]
        m = re.match(r"^([A-Za-z0-9_\-]+)(@.*)?$", par_name)
        bus = m.group(1).lower() if m else ""
        nodes[n["path"]] = {
            "c": n["props"]["compatible"],
            "st": (n["props"].get("status") or [""])[0],
            "bus": bus if re.match(r"^(i2c|spi|spmi|smbi2c|uart|usb|gpio)", bus) else "",
            "addr": libfdt.unit_addr(n["name"]) or (n["props"].get("reg") or [""])[0],
            "name": n["name"],
        }
    return nodes


# Device-tree state overrides that the blob alone cannot express.
CURATED.update(DT_OVERRIDES)

NODE_STATE = {
    "richtek,rt5133": "PRESENT-NOT-BOUND",
}


def summarise(rows: list[dict]) -> None:
    """Regenerate notes/DEVICE-TREE.md from the rows just written."""
    n = lambda k, pred=lambda r: True: sum(int(r[k]) for r in rows if pred(r))  # noqa: E731
    C = collections.Counter(r["coverage"] for r in rows)
    out = ["# Axis 2 - device-tree coverage (authoritative)", "",
           "Generated by `scripts/build-devicetree.py` from the binary device trees "
           "via `scripts/lib_fdt.py`, with per-compatible claims harvested by "
           "`scripts/harvest-pack-dt-claims.py`. The per-row detail is in "
           f"[`../device-tree.tsv`](../device-tree.tsv) ({len(rows)} rows).", "",
           "Reproduce: `python3 reverse-engineering/coverage-audit/scripts/"
           "harvest-pack-dt-claims.py && python3 reverse-engineering/coverage-audit/"
           "scripts/build-devicetree.py`", "",
           "## Universe", "",
           "| source | nodes | carrying `compatible` | distinct compatibles |",
           "|---|---:|---:|---:|",
       ]
    for label, path in (("`gq5012bf1-merged.dtb` (live, installed tree)", MERGED_DTB),
                       ("`fdt-00-off-03b76040.dtb` (base FDT from `vendor_boot`)", BASE_DTB),
                       ("`entry-00-id-00000000-rev-00000000.dtbo` (the single DTBO table entry)",
                        OVERLAY_DTBO)):
        ns = libfdt.walk(path)
        out.append(f"| {label} | {len(ns)} | {sum(1 for x in ns if 'compatible' in x['props'])}"
                   f" | {len({c for x in ns for c in x['props'].get('compatible', [])})} |")
    out += [f"| workspace claim sources | - | - | "
            f"{sum(1 for r in rows if int(r['claim_count']) > 0)} quoted |", "",
            "Provenance of the merge is `extraction-manifest.txt` beside the blobs: one "
            "valid FDT at `vendor_boot` offset `0x3b76040` (342 331 B) plus a DTBO table "
            "with `entry_count=1`. The bulk dump `docs/dt-module-matching.md` (526 "
            "compatibles) is deliberately not a claim source: a device-tree dump cannot "
            "own the tree it dumps.", "",
            "## Coverage classes", "",
            "| class | meaning | compatibles | node instances |",
            "|---|---|---:|---:|"]
    for k, label in (("A", "dedicated component documents it"),
                    ("B", "covered by a broader documented subsystem scope"),
                    ("C", "generic platform-internals - no device-specific RE needed"),
                    ("D", "disabled or reference-board baggage; DT enablement is not proof of binding"),
                    ("E", "unmapped - genuine coverage gap")):
        out.append(f"| {k} | {label} | {C[k]} | {n('nodes', lambda r, k=k: r['coverage'] == k)} |")
    out += [f"| **total** |  | **{sum(C.values())}** | **{n('nodes')}** |", "",
            "## Node state and provenance", "",
            "| node_state | compatibles |", "|---|---:|"]
    for k, v in collections.Counter(r["node_state"] for r in rows).most_common():
        out.append(f"| `{k}` | {v} |")
    out += ["", "| dt_source | compatibles | meaning |", "|---|---:|---|"]
    mean = {"base": "declared by the base FDT installed by `vendor_boot`",
            "overlay": "added by the board DTBO overlay only",
            "base+overlay": "declared in both (the overlay refines the base node)",
            "merged-only": "visible only after the merge - needs review"}
    for k, v in collections.Counter(r["dt_source"] for r in rows).most_common():
        out.append(f"| `{k}` | {v} | {mean.get(k, '')} |")
    out += ["", "### Bus-attached hardware (the axis-3 seed)", "",
            "| bus | compatibles | node instances |", "|---|---:|---:|"]
    busc = collections.Counter(r["bus"] for r in rows)
    for k, v in busc.most_common():
        out.append(f"| `{k}` | {v} | {n('nodes', lambda r, k=k: r['bus'] == k)} |")
    out += ["", "Overlay-only (board payload) compatibles:", ""]
    out.append(", ".join(f"`{r['compatible']}`" for r in rows
                         if r["dt_source"] == "overlay"))
    out += ["", "## Owners", "",
            "| owner | compatibles | class split |", "|---|---:|---|"]
    byc = collections.defaultdict(collections.Counter)
    for r in rows:
        byc[r["component"]][r["coverage"]] += 1
    for comp, cnt in sorted(((c, x) for c, x in byc.items()
                             if c not in ("COVERED-GENERIC", "UNMAPPED")),
                            key=lambda kv: -sum(kv[1].values())):
        if sum(cnt.values()) < 3:
            continue
        out.append(f"| `{comp}` | {sum(cnt.values())} | "
                   f"{','.join(f'{k}{v}' for k, v in sorted(cnt.items()))} |")
    g = byc["COVERED-GENERIC"]
    out += [f"| `COVERED-GENERIC` (platform-internals families) | {sum(g.values())} | "
            f"{','.join(f'{k}{v}' for k, v in sorted(g.items()))} |",
            f"| `UNMAPPED` (class E) | {sum(byc['UNMAPPED'].values())} | E"
            f"{sum(byc['UNMAPPED'].values())} |", "",
            "Every class-C row carries its family justification verbatim in `evidence`, so "
            "the classification is auditable per row instead of asserted in prose.", "",
            "## Class D and dead-hardware rows", "",
            "| compatible | nodes | enabled/disabled | node_state | sample node |",
            "|---|---:|---|---|---|"]
    for r in rows:
        if r["coverage"] == "D" or r["node_state"] in ("DISABLED", "PRESENT-NOT-BOUND",
                                                      "REFERENCE-BOARD-BAGGAGE", "UNKNOWN"):
            out.append(f"| `{r['compatible']}` | {r['nodes']} | {r['nodes_enabled']}"
                       f"/{r['nodes_disabled']} | `{r['node_state']}` | `{r['sample_node']}` |")
    ev_tier = collections.Counter(r["evidence"].split(":")[0] for r in rows)
    meanings = {
        "pack-claims": "a DONE/PARTIAL pack quotes the compatible in its own "
                       "README/notes/evidence",
        "research-family": "only a research-repo document quoted it, so the audit resolved "
                           "it to a named subsystem through an explicit compatible family",
        "driver": "no document quotes it, but a shipped kernel module name matches "
                  "(axis-1 classification travels)",
        "family": "platform-internals family with a written justification",
        "curated": "audit override (GPU gap, fingerprint/TEE/PMIC instances)",
    }
    out += ["", "## Evidence strength behind the classes", "",
            "| strength | meaning | compatibles |", "|---|---|---:|"]
    out += [f"| `{k}` | {meanings.get(k, '')} | {v} |"
            for k, v in sorted(ev_tier.items(), key=lambda kv: -kv[1])]
    researched = [r for r in rows if r["evidence"].startswith("research-family")]
    widest = [(c, sum(v.values())) for c, v in byc.items()
              if c not in ("COVERED-GENERIC", "UNMAPPED") and sum(v.values()) >= 15]
    widest.sort(key=lambda kv: (-kv[1], kv[0]))
    dtb = sum(byc["DTB-DTBO"].values()) if "DTB-DTBO" in byc else 0
    charging = [r["compatible"] for r in rows
                if re.match(r"^mediatek,(charger|mt6375)", r["compatible"])]
    with open(os.path.join(AUDIT, "kernel-modules.tsv")) as fh:
        mod_d = sum(1 for r in csv.DictReader(fh, delimiter="\t") if r["coverage"] == "D")
    out += ["",
            "`research-family` is the weakest of the documented tiers: it proves the node was "
            "examined during an investigation, not that a component pack maintains it. Those "
            f"{len(researched)} rows are therefore a pack-inventory backlog, not closed "
            "ownership. Widest documented owners: "
            + ", ".join(f"`{c}` ({n})" for c, n in widest[:6]) + ".",
            "",
            "## Conclusions for this axis", "",
            f"1. **No device-tree gap except one.** {len(rows) - C['E']} of {len(rows)} "
            f"compatibles resolve to a documented or justified class. The "
            f"{C['E']} `E` rows are one subsystem: "
            + ", ".join(f"`{r['compatible']}`"
                        for r in rows if r["coverage"] == "E")
            + ". The DT axis therefore independently confirms the kernel axis: the active "
            "Mali Valhall KMD has no owning component. Decision recorded in "
            "[`../MISSING-COVERAGE.md`](../MISSING-COVERAGE.md): add `MALI-GPU-KERNEL` "
            "(PARTIAL, class A).",
            f"2. **The DT axis and module axis agree on the charging stack.** "
            f"{len(charging)} PMIC charging/auxadc sub-nodes (for example "
            + ", ".join(f"`{x}`" for x in charging[:3])
            + ") resolve through family rules rather than a pack quoting them. Same symptom "
            "as conclusion 4 of the kernel axis: the charging stack is covered by several "
            "packs and by none of them as a whole.",
            f"3. **`DTB-DTBO` (PARTIAL) does not inventory the tree it owns.** After the "
            f"narrowest-scope rule it ends up owning only {dtb} of {len(rows)} compatibles; "
            "everything else is claimed by whichever "
            "investigation pack happened to need that node, travels with a driver, or falls "
            "into a platform-internals family. The reproducible artifact exists and is good "
            "(merged DTS + DTBO table + dtc logs), but node-level ownership lives in nobody's "
            "inventory - and this table is its natural home.",
            f"4. **The display and camera pipes are carried, not documented.** "
            f"`MEDIATEK-DRM` owns {sum(byc['MEDIATEK-DRM'].values())} display-pipeline "
            f"compatibles and `CAMERA-HAL-ISP` {sum(byc['CAMERA-HAL-ISP'].values())} "
            "camera-pipe compatibles as class B/C: they travel with the vendor DDI/mtkcam "
            "drivers. That is the right call for a same-BSP port, but it must stay an "
            "explicit decision: a custom display path (or any ISP change) would turn each of "
            "those rows into real work, which is exactly why they are recorded per row rather "
            "than summarised away.",
            f"5. **Research-note-only coverage is resolved but not owned.** "
            f"{len(researched)} compatibles (SMI/APU/display IOMMU banks, TUI, PMIC "
            "charger/auxadc, modem and display platform nodes) were only quoted inside phase-4 "
            "investigation notes; the audit resolved each to a named subsystem through an "
            "explicit rule instead of inventing a pseudo-component. Pack inventories still have "
            "to adopt them.",
            f"6. **Legacy/inert payload is small.** {C['D']} compatibles are class D - the "
            "driverless reference-board TDDI/fingerprint nodes - against "
            f"{mod_d} dead modules on the module axis. The live tree carries no dead board "
            "variant worth stripping.",
            "", "## Follow-ups produced by this axis", "",
            f"- create `MALI-GPU-KERNEL` (decision recorded in `../MISSING-COVERAGE.md`) and "
            f"move the {C['E']} `E` rows onto it;",
            f"- move the {C['A']} class-A \"quoted by a pack\" rows into that pack's inventory "
            "(or into `DTB-DTBO/notes/`) so device-tree ownership is machine-checkable the way "
            "module ownership now is;",
            f"- promote the {len(researched)} `research-family` rows into the owning packs' "
            "inventories, above all the sensor/SMI and PMIC-charger groups;",
            "- add the charging cross-pack view requested by the kernel axis.", ""]
    out = out[:out.index('## Conclusions for this axis')] + ['## Current accelerator ownership', '',
        f"All {len(rows)} compatibles are enumerated; {C['E']} compatible ownership gaps remain.",
        'GPU, APUSYS/MDLA/RPMsg, ISP, codec, MDP/MML and GPUEB/VCP compatibles now have singleton kernel owners. Generic syscon stays shared infrastructure.',
        'DT enablement is not binding or execution. Camera HAL consumers do not own accelerator kernel nodes.',
        '[Exact node/property/provider and source-contract ledgers](../../accelerator-re-roadmap.md).', '']
    doc = os.path.join(AUDIT, "notes", "DEVICE-TREE.md")
    with open(doc, "w") as fh:
        fh.write("\n".join(out).rstrip() + "\n")


def main() -> int:
    nodes = parse(MERGED_DTB)
    in_base = {c for info in parse(BASE_DTB).values() for c in info["c"]}
    in_overlay = {c for info in parse(OVERLAY_DTBO).values() for c in info["c"]}
    uni: dict[str, dict] = {}
    for path, info in nodes.items():
        for c in info["c"]:
            r = uni.setdefault(c, {"n": 0, "enabled": 0, "disabled": 0, "sample": path,
                                   "buses": set(), "addrs": set(), "names": set()})
            r["n"] += 1
            if info["st"].lower().startswith("disabled"):
                r["disabled"] += 1
            else:
                r["enabled"] += 1
            if info["bus"]:
                r["buses"].add(info["bus"])
            if info["addr"]:
                r["addrs"].add(info["addr"] if info["addr"].startswith("0x")
                               else f"0x{int(info['addr'], 16):x}" if re.fullmatch(
                                   r"[0-9a-fA-F]+", info["addr"]) else info["addr"])
            r["names"].add(info["name"].split("@")[0])

    claims: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for r in csv.DictReader(open(CLAIMS), delimiter="\t"):
        claims[r["compatible"]].append((r["component"], r["kind"]))

    modtoks: dict[str, set[str]] = collections.defaultdict(set)
    modrow: dict[str, dict] = {}
    for r in csv.DictReader(open(MODULES), delimiter="\t"):
        modbase = r["module"][:-3].lower()  # noqa: PLW2901
        modrow[modbase] = r
        for t in {x for x in re.split(r"[-_]", modbase) if len(x) >= 5} | {modbase.replace("-", "_")}:
            modtoks[t].add(modbase)

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
            resolved = next(((owner, rcls, why) for pat, owner, rcls, why in RESEARCH_COMPAT
                             if re.search(pat, c)), None)
            if resolved:
                comp, cls, why = resolved
                ev.append(f"research-family:{why}")
            else:
                comp, cls = "COVERED-GENERIC", "C"
                ev.append("research-only citation; no board-specific owner justified")
            ev.append(f"research-docs:{len(researchers)}")
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
            "bus": ",".join(sorted(info["buses"])) or "platform",
            "bus_address": ",".join(sorted(info["addrs"])[:6]),
            "node_names": ",".join(sorted(info["names"]))[:90],
            "dt_source": ("base+overlay" if c in in_base and c in in_overlay else
                          "overlay" if c in in_overlay else
                          "base" if c in in_base else "merged-only"),
            "node_state": NODE_STATE.get(c) or (
                "DISABLED" if info["disabled"] and not info["enabled"]
                else "REFERENCE-BOARD-BAGGAGE" if drv and all(
                    modrow[m]["coverage"] == "D" for m in drv)
                else "ACTIVE" if info["enabled"] else "UNKNOWN"),
            "physical_function": next((f for p, f in FUNCTIONS if re.match(p, c)),
                                      f"see {comp or 'UNMAPPED'} inventory"),
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
    summarise(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
