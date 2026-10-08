#!/usr/bin/env python3
"""Axis 3: physical hardware inventory for GQ5012BF1 -> RE coverage.

Universe (union, deduplicated by device):
  1. every bus-attached device-tree client of the merged live DT
     (`lib_fdt`: i2c/spmi/spi children with unit address and status);
  2. every row of the existing hardware inventory `docs/hardware-map.md`;
  3. every spec category of the audit brief (SoC ... secure hardware), so a
     category with no evidence anywhere is reported instead of silently absent.

Ownership is never invented: it is taken from axis 2 (`device-tree.tsv`, by
compatible) and axis 1 (`kernel-modules.tsv`, by module name), and the physical
identity from the owning pack's own `**Hardware identity:**` line
(`audit-evidence/pack-identity.tsv`).

Coverage classes (hardware axis)
  A a dedicated component pack owns the device
  B covered as part of a broader documented scope (broad pack / generic parent)
  C generic platform block - nothing board-specific to reverse-engineer
  D hardware not fitted / dead: declared by the DTB but no device answers
  E unmapped - no component and no written justification

Output: coverage-audit/hardware.tsv (+ notes/HARDWARE.md summary).
"""
from __future__ import annotations

import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib_fdt as libfdt  # noqa: E402

ROOT = "/home/armol/androido_dalykai/LieppOS custom ROM"
REPO = os.path.join(ROOT, "ulefone-gq5012bf1-research")
AUDIT = os.path.join(REPO, "reverse-engineering/coverage-audit")
DTB = os.path.join(REPO, "workspace/phase4-connfem-hardware/offline-dt/"
                         "gq5012bf1-merged.dtb")
HWMAP = os.path.join(REPO, "docs/hardware-map.md")
DT_ROWS = os.path.join(AUDIT, "device-tree.tsv")
MOD_ROWS = os.path.join(AUDIT, "kernel-modules.tsv")
IDENTITY = os.path.join(AUDIT, "audit-evidence/pack-identity.tsv")
OUT = os.path.join(AUDIT, "hardware.tsv")

# category, device label, kind, matchers (dt node-name regex, compatible regex,
# module regex, inventory-subsystem regex)
CATEGORY = [
    ("soc", "MediaTek MT6878T (Dimensity 7400 family)", "soc",
     r"^(cpus|soc|pinctrl|gic|pmu|apmixed|infracfg)", r"", r"", r"^SoC"),
    ("power", "MediaTek MT6375 main PMIC (charger/PE/PD/regulators/TCPC)", "pmic",
     r"mt6375", r"mediatek,mt6375|mediatek,charger,", r"mt6375", r""),
    ("power", "MediaTek MT6363 / MT6369 / MT6319 / MT6685 secondary PMICs", "pmic",
     r"mt63(19|63|69)|mt6685", r"mediatek,mt63(19|63|69)|mediatek,mt6685",
     r"mt63(19|63|69)|mt6685", r"^Fuel gauges"),
    ("power", "Richtek RT6160 PMIC debug/IBAT interface", "ic",
     r"rt6160", r"richtek,rt6160", r"rt6160", r""),
    ("power", "Richtek RT5133 reference LDO client (unbound; physical population unproved)", "ic",
     r"rt5133", r"richtek,rt5133", r"rt5133", r""),
    ("power", "Sino Wealth SH366003 2S pack fuel gauge (3rd gauge)", "ic",
     r"sh366003", r"sh,sh366003", r"sh366003", r""),
    ("power", "SC8571 2:1 direct-charge pump (master + slave)", "ic",
     r"sc8571", r"sc,sc8571", r"sc8571", r"Charge pumps"),
    ("power", "SC8510 bidirectional charge pump", "ic",
     r"sc851", r"sc,sc8510", r"sc8510", r""),
    ("storage", "UFS 3.1 storage host + RPMB", "storage",
     r"ufshci|ufsphy", r"ufshci", r"ufshci|mtk-ufs|ufshcd", r"^SoC"),
    ("storage", "MTK MSDCMMC host (microSD slot)", "storage",
     r"mmc@|msdc", r"mtk,mt(67|81|27)?.*(mmc|msdc)|mediatek,mtk-sd", r"mtk_sd|msdc", r""),
    ("display", "Main panel (YFT vtdr6115 DSI)", "display",
     r"dsi0|panel|lcm|touch-panel", r"vtdr6115|truly,td4330|jdi,nt36672e|disp_dsi",
     r"vtdr6115|mtk_drm|mtk_disp", r"Main panel"),
    ("display", "Rear 340x340 auxiliary display (CO5300 SPI)", "display",
     r"tiny_lcd", r"spi_tiny_lcd", r"co5300|spi_tiny_lcd", r"Rear display"),
    ("display", "OCP2131 display bias IC", "ic", r"ocp2131", r"i2c_lcd_bias", r"ocp2131", r""),
    ("display", "SH366003/Hynitron rear touch (CST820)", "touch",
     r"hynitron", r"hynitron", r"hynitron", r"Rear touch"),
    ("display", "FocalTech FT3680 SPI touch", "touch",
     r"focaltech", r"focaltech", r"fts|focaltech", r"Main touch"),
    ("display", "Ilitek ILI / Chipone TDDI touch candidates (unproven)", "touch",
     r"ilitek|chipone", r"ilitek|chipone", r"$^", r""),
    ("led", "Awinic AW2013 RGB notification LED", "ic",
     r"aw2013", r"awinic,rgb", r"aw2013", r"Notification RGB"),
    ("led", "Awinic AW36515 flash/IR driver (main camera + IR blaster)", "ic",
     r"aw36515", r"aw36515", r"aw36515", r"Consumer IR"),
    ("led", "Awinic AW36518 / AW36518-V2 flash LED drivers", "ic",
     r"aw36518", r"aw36518", r"aw3651[58]", r""),
    ("led", "LN2403 camp light / red-blue light controller (PWM)", "ic",
     r"camplight|yft", r"camplight", r"ln2403", r"Work/warning lights"),
    ("led", "MediaTek backlight / disp-leds glue", "display",
     r"disp-leds|backlight", r"disp-leds|disp-notify", r"mtk_disp_led|aat1425|ktz8866", r""),
    ("audio", "MediaTek MT6369 audio codec (headset + 2 AMIC mics)", "codec",
     r"codec|afe|audio", r"mt63(69|63)-sound|afe-pcm", r"mt63(69|63)_codec|audiofled|audio_dsp",
     r"^Audio"),
    ("audio", "Awinic AW88394 smart speaker amplifier", "ic",
     r"speaker_amp", r"speaker_amp", r"aw883xx|aw88394|tfa98xx", r"^Audio"),
    ("thermal", "ThermoVue T2 / AC020 thermal camera assembly", "camera",
     r"tiny2c|yft_tiny2c", r"tiny2c_usb", r"tiny2c|uvc", r"Thermal camera"),
    ("camera", "Image sensors (IMX989 / S5KJN1 / S5KJN1MAIN2 / OV64B)", "camera",
     r"sensor\d|imgsensor|cam-|camsys|seninf", r"imgsensor|seninf|camera",
     r"imgsensor|imx989|ov64b|s5kjn1|camsys", r"^Cameras"),
    ("camera", "Camera VCM autofocus drivers (main / main2 / main4)", "actuator",
     r"camera-af", r"_vcm", r"dw9714|dw9763|dw9768|bk6f|aw8651|gt9762|lm3644|rt9455", r""),
    ("camera", "DW9781C camera OIS", "actuator",
     r"camera-ois", r"dw9781c", r"dw9781c", r""),
    ("camera", "Camera module EEPROMs (4 instances)", "ic",
     r"camera-eeprom", r"camera_eeprom", r"camera_eeprom|laser_eeprom", r""),
    ("camera", "Camera analogue/digital supplies (AVDD/DOVDD/OISVDD LDOs)", "power",
     r"camera-common|avdd|dovdd|oisvdd", r"mt6363.*ldo|wl2864", r"wl2864|wl2868", r""),
    ("usb", "USB2/USB3 MTU3 + Type-C TCPC + extcon path", "usb",
     r"usb0|xhci|mtu3|tcpc|extcon|typec", r"mtu3|tcpc|xhci|extcon", r"mtu3|typec_extcon", r"USB / uSmart"),
    ("secure", "SPI fingerprint sensor (Microarray/Madev) + TrustKernel TEE path", "secure",
     r"fingerprint|finger", r"madev_finger|yft_finger|trustkernel|goodix-fp",
     r"madev|microarray|tkcore", r"^Fingerprint"),
    ("secure", "ST21NFC controller + NFC secure element", "secure",
     r"st21nfc|nfc", r"st21nfc|st21dfm", r"st21nfc|nfn_usb|nfc", r"^NFC"),
    ("connectivity", "MT6637 Wi-Fi/BT/FM combo (connac) + connscp/connfem FEM", "rf",
     r"conn|wcn|gps|bt", r"connac|conn_scp|connfem|mt6637|gps",
     r"wcn|connac|cfg80211|bluetooth|fm|mtk-76x2|wmt", r"^Sensors|Fingerprint|Work"),
    ("connectivity", "Modem (MD1/MD3) + SIM1/SIM2 hot-plug + smart PA", "rf",
     r"ccci|md1|md3|sim|smart-pa", r"ccci|md1_sim|mddriver|smart[-_]pa",
     r"ccci|mddriver|dpmaif|ccmni", r"Work/warning"),
    ("positioning", "SoC GNSS receiver (mtk,mt6878-gps)", "soc",
     r"gps", r"gps", r"gpsv4l|gnss|sts_?core|mnld", r"Sensors"),
    ("input", "PMIC keys + two YFT programmable keys", "input",
     r"keys|gpio-keys", r"mt6363-keys|yft-gpio-keys|kp", r"mtk_kpd|mt6363keys", r"Physical action keys"),
    ("ir", "Consumer IR emitter path (/irtx-pwm, PWM0)", "input",
     r"irtx", r"irtx", r"irtx", r"Consumer IR"),
    ("haptics", "Board vibration/haptics path (PMIC vibrator regulator)", "actuator",
     r"vibr", r"regulator-vibrator|vibr", r"mt6369_vibr|ltr5xx|aw8697", r"^SoC"),
    ("sensors", "SCP/sensor-hub owned sensors (ICM4N607, MMC5603, STK3A5X, SPL07)", "sensor",
     r"scp|sensor", r"scp|sensor", r"scp|sensorhub|jcl|gs", r"^Sensors"),
    ("secure", "TEE / secure world (GenieZone + Trusty + FF-A + MTEE + RPMB)", "secure",
     r"gz|trusty|nebula|mtee|ffa|tee|rproc", r"gz|trusty|ffa|smc|tee|mobicore|utos",
     r"gz|trusty|ffa|tmem|tkcore|rpmb", r"^NFC"),
    ("rugged", "Rear rugged services (YFT devinfo/TPD gesture/Tiny2C)", "input",
     r"yft", r"yft", r"yft", r"Work/warning"),
    ("rf", "RF front-end / antennas (software-relevant control only)", "rf",
     r"connfem|smart-pa|ant", r"connfem|smart[-_]pa", r"", r""),
]

# Audit overrides where no document quotes the device but the ownership is a
# written decision rather than a gap: (category, device-prefix) -> component/class.
OVERRIDES = {
    ("soc", "MediaTek MT6878T"): ("COVERED-GENERIC", "C",
                                 "the SoC itself is not a RE target: every "
                                 "board-specific block around it is owned per "
                                 "row on axes 1-3 (GKI/KMI baseline, vendor BSP "
                                 "modules, MTK platform glue)"),
    ("display", "Ilitek ILI"): ("COVERED-GENERIC", "D",
                                "two TDDI touch endpoints declared on i2c-2 "
                                "(ilitek@41, chipone_tddi@48) have no shipped "
                                "driver: main touch is FT3680 (SPI3) and rear "
                                "touch is Hynitron CST820, so these are inactive "
                                "reference-board DT baggage and require no RE component"),
}

# Categories the audit brief demands even when no device-tree node exists.
EXTRA = [
    ("connectivity", "eSIM/eUICC (not fitted)", "ABSENT"),
    ("power", "Wireless charging (not fitted)", "ABSENT"),
]


def dt_index() -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = collections.defaultdict(list)
    rows = list(csv.DictReader(open(DT_ROWS), delimiter="\t"))
    for r in rows:
        idx[r["compatible"]].append(r)
    return idx


def main() -> int:
    nodes = libfdt.walk(DTB)
    by_path = {n["path"]: n for n in nodes}
    dtr = dt_index()
    mods = list(csv.DictReader(open(MOD_ROWS), delimiter="\t"))
    ident = {r["component"]: r for r in csv.DictReader(open(IDENTITY), delimiter="\t")}

    inv = []
    for line in open(HWMAP, encoding="utf-8"):
        m = re.match(r"^\| *([^|]+?) *\| *([^|]+?) *\| *([^|]+?) *\|", line)
        if m and m.group(1).strip() not in {"Subsystem", "---"}:
            inv.append({"subsystem": m.group(1).strip(), "evidence": m.group(2).strip(),
                       "status": m.group(3).strip()})

    def tokens(text: str) -> set[str]:
        return {t for t in re.split(r"[^A-Za-z0-9]+", text.lower()) if len(t) >= 4}

    def owners_from(comps: set[str], modules: set[str], label: str = ""
                    ) -> tuple[str, str, str]:
        """resolve (component, coverage, evidence) from axes 1+2 evidence."""
        ev: list[str] = []
        cls: list[tuple[str, str]] = []
        for c in sorted(comps):
            for r in dtr.get(c, []):
                if r["component"] != "UNMAPPED":
                    cls.append((r["component"], r["coverage"]))
                    ev.append(f"dt:{c}->{r['component']}({r['coverage']})")
        for m in sorted(modules):
            for r in mods:
                if r["module"][:-3] == m and r["component"] != "UNMAPPED":
                    cls.append((r["component"], r["coverage"]))
                    ev.append(f"ko:{r['module']}->{r['component']}({r['coverage']})")
        ltoks = tokens(label)
        packy = [(c, k) for c, k in cls if not c.startswith(("COVERED-GENERIC", "research:"))]
        if packy:
            def score(ck: tuple[str, str]) -> int:
                ctoks = tokens(ck[0].replace("-", " ")) | tokens(ck[0].replace("-", ""))
                return len(ltoks & ctoks) * 10 - (ck[1] not in "AD")
            best = max(packy, key=score)
            if score(best) >= 10:
                co = ";".join(sorted({c for c, _ in packy})[:4])
                return best[0], best[1], (f"{';'.join(ev[:4])};co-owners:{co}")[:400]
        if packy:
            narrow = min(packy, key=lambda ck: (ck[1] not in "AD", ck[1], ck[0]))
            co = ";".join(sorted({c for c, _ in packy})[:4])
            return narrow[0], narrow[1], f"{';'.join(ev[:4])};co-owners:{co}"[:400]
        # nothing quotes the device: fall back to a dedicated pack whose declared
        # hardware identity names the same device (still evidence, not invention)
        cand = [c for c in ident if ltoks & (tokens(c.replace("-", " ")) | tokens(c.replace("-", "")))]
        if cand:
            best = min(cand, key=lambda c: (ident[c]["status"] != "DONE", len(c), c))
            return best, "A", (f"dedicated-pack:{best}({ident[best]['status']});"
                               f"identity:{ident[best]['hardware_identity'][:120] or best}")[:400]
        if cls:
            narrow = min(cls, key=lambda ck: (ck[1] not in "AD", ck[1], ck[0]))
            return narrow[0], narrow[1], f"{';'.join(ev[:4])};only-broad-scope"[:400]
        return "UNMAPPED", "E", "no-component-claims-device"

    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for cat, label, kind, dtp, cmp_, modp, invp in CATEGORY:
        paths = sorted({n["path"] for n in nodes if re.search(dtp, n["name"], re.I)})
        comps = {c for c in dtr if re.search(cmp_, c, re.I)} if cmp_ else set()
        kos = sorted({r["module"][:-3] for r in mods
                      if re.search(modp, r["module"][:-3], re.I)}) if modp else []
        inv_hits = [i for i in inv if re.search(invp, i["subsystem"], re.I)] if invp else []
        if not (paths or comps or kos or inv_hits):
            comp, cov, ev = "UNMAPPED", "E", "no-evidence-for-category"
            bus = addr = state = ""
        else:
            comp, cov, ev = owners_from(comps, set(kos[:12]), label)
            for (oc, oprefix), (ocomp, ocov, oev) in OVERRIDES.items():
                if cat == oc and label.startswith(oprefix):
                    comp, cov, ev = ocomp, ocov, oev
            bus = ",".join(sorted({p.split("/")[-2].split("@")[0] for p in paths
                                   if len(p.split("/")) > 2})[:6])
            addr = ",".join(sorted({libfdt.unit_addr(p.split("/")[-1]) for p in paths})
                           [:8])
            state = ("DISABLED" if paths and all(
                by_path[p]["props"].get("status", [""])[0].lower() == "disabled"
                for p in paths) else "ACTIVE")
        seen.add((cat, label))
        absent = bool(re.search(r"not fitted", label, re.I))
        rows.append({
            "category": cat, "device": label, "kind": kind,
            "buses": bus or "-", "addresses": addr or "-", "dt_nodes": str(len(paths)),
            "dt_state": state or "-", "drivers": ",".join(kos[:6]) or "-",
            "component": comp, "coverage": cov,
            "presence": ("ABSENT-ON-BOARD" if absent else
                         "PROVEN" if paths and (kos or inv_hits) else
                         "DT-ONLY" if paths else "INVENTORY-ONLY" if inv_hits or kos
                         else "UNSEEN"),
            "inventory": ";".join(f"{i['subsystem']}={i['status']}" for i in inv_hits)[:200],
            "evidence": ev,
            "sample_node": paths[0] if paths else "-",
        })

    # DT presence + a shipped driver is not proof of a successful probe. Keep
    # static coverage separate from the observed board runtime state.
    rt = next(r for r in rows if "RT5133" in r["device"])
    rt.update(component="RT5133-POWER-IC", coverage="A", presence="PRESENT-NOT-BOUND",
              evidence="stock-20260831:buses.txt:79-82 unresolved driver link; "
                       "pstore-20260829:rt5133-gpio1/2/3 deferred; no registered rails; "
                       "camera LDO is bound WL2864C at 11-0029; "
                       "see notes/RT5133-CORRECTION.md")

    # every bus-attached DT client must appear somewhere: cross-check the spine
    for n in nodes:
        par = by_path[n["parent"]]["name"]
        if not re.match(r"^(i2c|spi\d*|spmi)\b", par):
            continue
        cs = n["props"].get("compatible", [])
        if any(c in dtr and dtr[c][0]["component"] != "UNMAPPED" for c in cs):
            continue
        rows.append({
            "category": "unclaimed", "device": ",".join(cs) or n["name"], "kind": "ic",
            "buses": par.split("@")[0], "addresses": libfdt.unit_addr(n["name"]) or "-",
            "dt_nodes": "1",
            "dt_state": ("DISABLED" if n["props"].get("status", [""])[0].lower()
                         == "disabled" else "ACTIVE"),
            "drivers": "-", "component": "UNMAPPED", "coverage": "E",
            "presence": "DT-ONLY", "inventory": "",
            "evidence": f"bus-client-without-owner:{n['path']}",
            "sample_node": n["path"],
        })

    for cat, label, presence in EXTRA:
        comp, cov, ev = owners_from(set(), set(), label)
        rows.append({"category": cat, "device": label, "kind": "feature",
                     "buses": "-", "addresses": "-", "dt_nodes": "0",
                     "dt_state": "-", "drivers": "-", "component": comp, "coverage": cov,
                     "presence": presence, "inventory": "",
                     "evidence": ev, "sample_node": "-"})

    rows.sort(key=lambda r: (r["coverage"], r["category"], r["device"].lower()))
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"hardware rows={len(rows)} coverage={dict(collections.Counter(r['coverage'] for r in rows))}")
    for r in rows:
        if r["coverage"] == "E":
            print("  E:", r["category"], "|", r["device"][:70], "|", r["presence"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
