#!/usr/bin/env python3
"""Generate the human-readable coverage reports and authoritative index."""
from __future__ import annotations

import csv
import json
import os
import textwrap
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CA = HERE.parent
RE = CA.parent
DATE = "2026-10-07"


def read(name: str) -> list[dict]:
    with (CA / name).open(newline="", encoding="utf8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def save(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf8")
    print(path.relative_to(RE.parent))


def esc(s: str) -> str:
    return (s or "-").replace("|", "\\|").replace("\n", " ").strip()


def short(s: str, n: int = 220) -> str:
    s = " ".join((s or "-").split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def metrics() -> dict:
    c = read("components.tsv")
    km = read("kernel-modules.tsv")
    dt = read("device-tree.tsv")
    hs = read("hals-services.tsv")
    vs = read("vendor-services.tsv")
    fw = read("firmware.tsv")
    sw = read("secure-world.tsv")
    art = read("artifact-map.tsv")
    manifest_path = CA / "audit-evidence/manifest-audit-2026-10-07.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    active_dt = [r for r in dt if int(r["nodes_enabled"]) > 0]
    device_hal = [r for r in hs + vs if r["coverage"] != "C"]
    return {
        "components": c, "km": km, "dt": dt, "hs": hs, "vs": vs, "fw": fw,
        "sw": sw, "art": art, "manifest": manifest, "active_dt": active_dt, "device_hal": device_hal,
        "status": Counter(r["status"] for r in c),
        "partial": Counter(r["partial_class"] for r in c if r["status"] == "PARTIAL"),
        "km_cov": Counter(r["coverage"] for r in km),
        "dt_cov": Counter(r["coverage"] for r in dt),
        "active_dt_cov": Counter(r["coverage"] for r in active_dt),
        "hal_cov": Counter(r["coverage"] for r in hs),
        "svc_cov": Counter(r["coverage"] for r in vs),
        "fw_class": Counter(r["firmware_class"] for r in fw),
        "art_cov": Counter(r["coverage"] for r in art),
    }


PARTIAL_MEANING = {
    "A": "Actionable / statically closeable",
    "B": "Kernel/source closed; broader proprietary scope remains",
    "C": "Proprietary boundary",
    "D": "Hardware/runtime/teardown gated",
    "E": "Stale/duplicate/wrong scope",
    "F": "Broad umbrella/tracking scope",
}

BEST_10 = [
    (1, "YFT-DEVINFO", "Quick static parity: one enum spelling plus probe/sysfs residual."),
    (2, "VINTF-HAL-MANIFEST", "Generate final manifests/matrices and run VINTF checks."),
    (3, "VENDOR-PROPERTIES", "Generate the property allowlist and validate contamination controls."),
    (4, "FT3680-TOUCH", "Continue the bounded 40/68-function static residual."),
    (5, "MT6375-CHARGER", "Close source/provider parity before runtime charging tests."),
    (6, "DTB-DTBO", "Finish source-complete DTS and bootloader-mutation reconciliation."),
    (7, "BOOT-IMAGES", "Produce exact-geometry custom images and validate Slot B boot."),
    (8, "CAMERA-ISP-KERNEL (proposed split)", "Isolate actionable ISP kernel parity from proprietary HAL/3A."),
    (9, "MALI-GPU-KERNEL (proposed add)", "Own the active Valhall KMD, MGM/protected allocator and three DT compatibles."),
    (10, "VENDOR-SEPOLICY", "Build the device policy and close enforcing-runtime denials."),
]


def build_partial(m: dict) -> None:
    rows = [r for r in m["components"] if r["status"] == "PARTIAL"]
    out = ["# PARTIAL triage", "", f"Audit date: {DATE}", "",
           "Every current PARTIAL is classified. Class E is intentionally zero: taxonomy cleanup candidates currently live in DONE and are reported separately; no PARTIAL was silently treated as stale.", "",
           "| Component | Class | What remains | Can static RE close it? | Best next action | Difficulty | Dependencies |",
           "|---|:---:|---|---|---|---|---|"]
    for r in rows:
        can = {"A": "Yes", "B": "Kernel yes; whole scope no", "C": "No", "D": "No, needs runtime/physical evidence", "E": "N/A", "F": "Not as one umbrella"}[r["partial_class"]]
        next_action = r["recommended_action"].replace("KEEP PARTIAL; ", "")
        out.append(f"| {esc(r['component'])} | {r['partial_class']} | {esc(short(r['blocker'], 260))} | {can} | {esc(short(next_action, 220))} | {esc(r['difficulty'])} | {esc(short(r['dependencies'], 180))} |")
    out += ["", "## Classification totals", "", "| Classification | Count |", "|---|---:|"]
    for cls in "ABCDEF":
        out.append(f"| {cls} — {PARTIAL_MEANING[cls]} | {m['partial'].get(cls, 0)} |")
    out += ["", "## Ranked next targets", ""]
    for n, comp, why in BEST_10:
        out.append(f"{n}. **{comp}** — {why}")
    out += ["", "## Work tiers", ""]
    tier_order = ["QUICK", "MEDIUM", "HARD", "PROPRIETARY-GATED", "PHYSICAL/RUNTIME-GATED"]
    for tier in tier_order:
        names = [r["component"] for r in rows if r["difficulty"] == tier]
        out += [f"### {tier.replace('-', ' ')}", "", ", ".join(f"`{x}`" for x in names) or "None.", ""]
    # D-class entries have mixed historical difficulty strings; make the physical tier explicit.
    dnames = [r["component"] for r in rows if r["partial_class"] == "D"]
    out += ["Physical/runtime gates take precedence over any static subtask for: " + ", ".join(f"`{x}`" for x in dnames) + "."]
    save(CA / "PARTIAL-TRIAGE.md", "\n".join(out))


def build_missing(m: dict) -> None:
    e = [r for r in m["art"] if r["coverage"] == "E"]
    out = ["# Missing coverage", "", f"Audit date: {DATE}", "",
           "## CONFIRMED MISSING", "",
           "### MALI-GPU-KERNEL", "",
           "1. **Proposed name:** `MALI-GPU-KERNEL`",
           "2. **Subsystem:** Graphics / GPU",
           "3. **Evidence:** active modules and enabled DT nodes plus vendor GPU services have no canonical component.",
           "4. **Owns:** `mali_kbase_mt6878_r44.ko`, `mali_mgm_mt6878_r44.ko`, `mali_prot_alloc_mt6878_r44.ko`; `arm,mali-valhall`, `mediatek,mali`, `mediatek,g3d_brisket`; the kernel-facing ABI of the GPU/gpuserv/mali-platform services.",
           "5. **Why not covered elsewhere:** `TMEM-FFA` owns secure-memory transport and `VENDOR-BLOB-HAL-INVENTORY` owns proprietary userspace/CSF payloads; neither owns KMD source/DT parity.",
           "6. **Suggested initial status:** PARTIAL, class A.",
           "7. **Estimated difficulty:** HARD.",
           "8. **Expected boundary:** reconstruct kernel/DT/platform ABI; retain proprietary Mali userspace and CSF firmware.", "",
           f"The unified map has {len(e)} E rows, all converging on this single scope:", ""]
    for r in e:
        out.append(f"- `{r['artifact_type']}` `{r['artifact']}` — {r['notes']}")
    out += ["", "## POSSIBLE MISSING", "",
            "None currently meets the threshold for a new component. APUSYS/NPU, codec/media, generic MTK performance services and platform remote processors are represented as generic/platform infrastructure or retained vendor-blob boundaries; there is no GQ5012BF1-specific orphan evidence that justifies a new ownership scope.", "",
            "## NOT MISSING / COVERED ELSEWHERE", "",
            "- ICM4N607, MMC5603, STK3A5X and SPL07 register drivers are SCP-firmware-owned; Linux transport is `SENSOR-HUB-KERNEL`, while firmware/HAL behavior is `SENSOR-HUB` plus the physical-sensor scopes.",
            "- Modem, RIL and IMS are deliberately split into Linux transport, signed modem firmware and proprietary userspace scopes.",
            "- Camera sensors/VCM/OIS/EEPROM are closed child scopes; proprietary HAL/3A/tuning are represented by `CAMERA-HAL-ISP`.",
            "- Secure TAs are represented by TrustKernel/KeyMint/fingerprint boundaries; lack of TA source is not an ordinary missing kernel component.",
            "- Thermal-camera UVC/power, command/application and radiometry/calibration layers are separately owned.",
            "- eSIM/eUICC and wireless charging are proven absent, not missing implementation scopes.", "",
            "## GENERIC / NO DEDICATED RE NEEDED", "",
            f"- {m['km_cov']['C']} shipped kernel modules are generic/upstream/platform infrastructure.",
            f"- {m['active_dt_cov']['C']} active DT compatible rows are generic infrastructure.",
            "- AOSP interface libraries, framework services, filesystems, schedulers, standard USB classes and generic MTK platform helpers are `COVERED-GENERIC`/`GENERIC-PLATFORM-INFRASTRUCTURE`.",
            "- Generic classification is evidence-backed per row; it is not a default fallback for unknowns."]
    save(CA / "MISSING-COVERAGE.md", "\n".join(out))


def change_block(cid, typ, comps, reason, evidence, risk, action) -> str:
    return textwrap.dedent(f"""
    ### {cid}

    - **type:** {typ}
    - **component(s):** {comps}
    - **reason:** {reason}
    - **evidence:** {evidence}
    - **risk:** {risk}
    - **suggested action:** {action}
    """).strip()


def build_changes() -> None:
    blocks = [
        change_block("PC-001", "ADD", "MALI-GPU-KERNEL", "One active board-specific kernel/DT ownership scope is absent.", "3 E modules + 3 E DT compatibles + 2 E VINTF families + 2 E init services.", "Medium: do not absorb proprietary userspace/firmware into a source-closure claim.", "Create only after review; start PARTIAL/A and own KMD/DT ABI."),
        change_block("PC-002", "SPLIT", "CAMERA-HAL-ISP → CAMERA-HAL-ISP + CAMERA-ISP-KERNEL", "One PARTIAL mixes statically actionable ISP modules with permanently proprietary HAL/3A/tuning/CCU.", "Component README and camera axis identify mixed kernel parity and proprietary userspace.", "Medium: module ownership and links must move without implying open 3A parity.", "Create CAMERA-ISP-KERNEL (PARTIAL/A); narrow CAMERA-HAL-ISP to proprietary userspace boundary (C)."),
        change_block("PC-003", "MERGE", "GZ-IPC-MOD, GZ-MAIN-MOD, GZ-TRUSTY-MOD, GZ-TZ-SYSTEM → GZ-TRANSPORT", "Four per-module children share one GenieZone transport completion criterion and the parent already summarizes them.", "Each child README cross-links GZ-TRANSPORT; all are DONE exact-source transport pieces.", "Low: preserve per-module parity reports under subdirectories.", "Use GZ-TRANSPORT as survivor; migrate evidence/manifest paths, reducing five components to one."),
        change_block("PC-004", "MERGE", "AW36518-V2-FLASH → AW36518-FLASH", "Two shipped source variants implement one AW36518-family physical ownership boundary.", "Sibling READMEs explicitly compare v1/v2 topology and parity.", "Low: preserve both module/source variants as subreports.", "Keep AW36518-FLASH and add v1/v2 subsections."),
        change_block("PC-005", "MERGE", "USB3-FEASIBILITY → USB-TYPEC", "Resolved-negative capability study is a board fact, not a continuing component.", "Stock boot log proves zero USB3 ports; USB-TYPEC already owns board USB capability.", "Low: preserve the negative proof prominently.", "Move report into USB-TYPEC and retire the standalone component."),
        change_block("PC-006", "MERGE", "VENDOR-ALL-MODULES-READY → INIT-INSMOD", "A single init property lifecycle is part of the module-loader/init ownership boundary.", "README proves sole setter/consumer ordering around insmod_sh.", "Low.", "Move the property timeline into INIT-INSMOD."),
        change_block("PC-007", "REMOVE", "ESIM-EUICC-ABSENCE", "Proven absence is a finding, not an ongoing RE ownership scope.", "No fitted eUICC in hardware/software inventory.", "Low: losing the negative conclusion if not migrated.", "Preserve in hardware.tsv/MISSING-COVERAGE.md, then retire folder."),
        change_block("PC-008", "REMOVE", "WIRELESS-CHARGING-ABSENCE", "Proven absence is a finding, not an ongoing component.", "No wireless charging path in DT/modules/init/hardware evidence.", "Low: preserve distinction from wired reverse charging.", "Preserve in hardware/power reports, then retire folder."),
        change_block("PC-009", "RENAME", "RT5133-POWER-IC → RT5133-CAMERA-LDO-INTEGRATION", "Current name preserves the superseded 4-phase-buck ambiguity.", "Newest runtime evidence has rt5133 bound at I2C 5-0018 as a camera-sensor LDO/power path; exact die/rails remain hardware-gated.", "Medium: update every manifest/link without reopening proven static work.", "Rename only; keep DONE as named static scope and preserve the hardware-checkout boundary."),
        change_block("PC-010", "STATUS", "OEM-KERNEL-MODULES and VENDOR-DLKM metadata", "Their prose still cites a 471-module set while the authoritative union is 457.", "kernel-modules.tsv reconciles all module locations and metadata to 457 distinct .ko names.", "Low; no directory status move.", "Refresh counts/scope prose; remain PARTIAL/F umbrella trackers."),
    ]
    out = ["# Proposed taxonomy changes", "", f"Audit date: {DATE}", "",
           "Recommendations only. No component folder/status was moved by this audit.", ""] + blocks + ["", "## Net component count if accepted", "",
           "Current 133 + one ADD + one split-created child − four GZ children − one AW36518 variant − one USB3 study − one init-property component − two absence components = **126 canonical components**.", "",
           "The rename and metadata/status-text refresh do not change the count. There are **two newly named scopes** after migration: one genuinely missing ADD and one split-created kernel child."]
    save(CA / "PROPOSED-CHANGES.md", "\n\n".join(out))


def build_readiness() -> None:
    rows = [
        ("1. Bootable custom kernel", "NEAR-READY / not runtime-proven", "BOOT-IMAGES exact-geometry boot test; DT source closure; GKI/KMI/vendor-module integration; add Mali KMD ownership."),
        ("2. Full custom Android ROM", "MAPPED / integration incomplete", "VINTF, vendor properties, init, SELinux, blob extraction, camera/audio/radio/sensor/USB/power HAL integration."),
        ("3. Daily-driver Android", "NOT YET VALIDATED", "Calls/data/IMS, camera, suspend, charging/thermal, fingerprint, NFC, sensors, GNSS, Wi-Fi/BT, DRM, OTA and recovery acceptance."),
        ("4. Full hardware feature parity", "PROPRIETARY/PHYSICAL GATED", "Camera 3A/tuning, modem/RIL/IMS, SCP algorithms, DSP, fingerprint/TEE, radiometry/calibration, signed firmware and physical RF/thermal details."),
        ("5. De-Googled LieppOS", "RE-MAPPED / product work remains", "No new hardware-RE gap; Google-free framework choices must retain compatible vendor HAL/blob contracts and decide DRM/attestation behavior."),
        ("6. Stock-integrity secondary slot", "ARCHITECTURE MAPPED / safety validation open", "OTA/snapshot/FBE/shared metadata, boot-control rollback and recovery behavior must be tested without modifying the stock anchor slot."),
        ("7. Future Linux slot", "KERNEL BASELINE STRONG / feature parity hard", "GPU KMD, display/input integration, modem userspace, SCP sensors, camera, DSP, charging policy and signed firmware remain major constraints."),
    ]
    out = ["# Port-readiness matrix", "", f"Audit date: {DATE}", "",
           "This is a coverage/readiness assessment, not a build plan.", "",
           "| Target | Assessment | Remaining RE/validation blockers |",
           "|---|---|---|"]
    out += [f"| {a} | **{b}** | {c} |" for a, b, c in rows]
    out += ["", "## Cross-cutting conclusions", "",
            "- The port is no longer discovering major subsystems ad hoc: every audited axis has an owner or explicit generic/dead/proprietary classification.",
            "- One source-actionable ownership hole remains: Mali GPU KMD/DT.",
            "- Binary compatibility is still required for multiple daily-driver features; mapping a boundary does not make it open source.",
            "- Physical/runtime validation is now the limiting factor for charging, battery, cooling, RF, microphones and end-to-end Android behavior."]
    save(CA / "PORT-READINESS.md", "\n".join(out))


def build_summary(m: dict) -> None:
    s, p, k = m["status"], m["partial"], m["km_cov"]
    mapped_dt = len(m["active_dt"]) - m["active_dt_cov"]["E"]
    mapped_hal = len(m["device_hal"]) - sum(r["coverage"] == "E" for r in m["device_hal"])
    out = ["# Coverage verdict: NEAR-COMPLETE", "",
           f"Audit date: {DATE}", "",
           "The 133-component list is not taxonomy-perfect and has one real coverage hole, but the device is now architecture-mapped across kernel, DT, physical hardware, Android integration, proprietary userspace, firmware, secure world and boot/storage. The only confirmed missing ownership scope is active Mali GPU KMD/DT.", "",
           "## Measured headline", "",
           f"- Current components: **{len(m['components'])}** (DONE {s['DONE']}, PARTIAL {s['PARTIAL']}, BLOCKED {s['BLOCKED']}, TODO {s['TODO']})",
           "- Confirmed missing components: **1**",
           "- Possible missing components: **0**",
           "- Merge candidates: **4**",
           "- Split candidates: **1**",
           "- Stale/remove candidates: **2**",
           "- Rename candidates: **1**",
           f"- Unified artifact rows: **{len(m['art'])}**; E rows: **{m['art_cov']['E']}**, all one GPU gap",
           "",
           "### Kernel modules", "",
           f"- Total distinct shipped `.ko`: **{len(m['km'])}**",
           f"- Device-specific covered (A+B): **{k['A'] + k['B']}** (A={k['A']}, B={k['B']})",
           f"- Generic/no dedicated RE (C): **{k['C']}**",
           f"- Dead/reference/debug baggage (D): **{k['D']}**",
           f"- Unmapped (E): **{k['E']}** — all active Mali KMD support",
           "",
           "### Active device tree", "",
           f"- Distinct compatible rows: **{len(m['dt'])}** across **{sum(int(r['nodes']) for r in m['dt'])}** compatible-bearing nodes",
           f"- Active/enabled compatible rows mapped: **{mapped_dt}/{len(m['active_dt'])}**",
           f"- Active E rows: **{m['active_dt_cov']['E']}** — the same Mali gap",
           f"- Active reference-board TDDI rows (D): **{m['active_dt_cov']['D']}**",
           "",
           "### Vendor HAL/services", "",
           f"- Full harvested HAL/service rows: **{len(m['hs']) + len(m['vs'])}**",
           f"- Device-specific rows (C excluded): **{len(m['device_hal'])}**",
           f"- Device-specific mapped: **{mapped_hal}/{len(m['device_hal'])}**; E={sum(r['coverage']=='E' for r in m['device_hal'])}, all GPU",
           f"- Generic/framework rows: **{sum(r['coverage']=='C' for r in m['hs'] + m['vs'])}**",
           "",
           "### Firmware and secure world", "",
           f"- Firmware/calibration payloads mapped: **{len(m['fw'])}/{len(m['fw'])}** (signed {m['fw_class']['SIGNED-BINARY']}, binary-only {m['fw_class']['BINARY-ONLY']}, source-available {m['fw_class']['SOURCE-AVAILABLE']}, device-internal {m['fw_class']['DEVICE-INTERNAL']})",
           f"- Secure-world surfaces represented: **{len(m['sw'])}/{len(m['sw'])}**",
           "",
           "### PARTIAL triage", ""]
    out += [f"- {cls} = **{p.get(cls, 0)}** — {PARTIAL_MEANING[cls]}" for cls in "ABCDEF"]
    out += ["", "## Explicit answers", "",
            "1. **Is the current list complete?** No: NEAR-COMPLETE. One active GPU ownership scope is missing.",
            "2. **Exactly what is missing?** `MALI-GPU-KERNEL`, owning active Valhall KMD/MGM/protected-allocation modules, GPU DT and kernel-facing service ABI.",
            "3. **How many new components are justified?** One missing ADD; one additional child is justified only by the camera split. Two newly named scopes after migration.",
            "4. **Are there duplicates?** Yes, primarily the four per-module GZ children under GZ-TRANSPORT and the AW36518 v1/v2 folder pair.",
            "5. **Which should merge?** GZ children→GZ-TRANSPORT; AW36518-V2→AW36518; USB3-FEASIBILITY→USB-TYPEC; VENDOR-ALL-MODULES-READY→INIT-INSMOD.",
            "6. **Which should split?** CAMERA-HAL-ISP should split actionable CAMERA-ISP-KERNEL from proprietary HAL/3A/tuning.",
            "7. **Are DONE components incorrectly scoped?** No automatic demotion is proven. DONE is static/named-scope only; several names/taxonomy entries need merge/remove/rename to avoid overbreadth.",
            f"8. **PARTIAL A–F?** A={p['A']}, B={p['B']}, C={p['C']}, D={p['D']}, E={p['E']}, F={p['F']}.",
            f"9. **Module classes?** device-specific covered={k['A'] + k['B']}, generic={k['C']}, dead/reference={k['D']}, unmapped={k['E']}.",
            f"10. **All active DT hardware represented?** {mapped_dt}/{len(m['active_dt'])} active compatible rows mapped; the three unmapped rows are one GPU scope. Physical inventory is 44/44 accounted, including absences/reference baggage.",
            f"11. **All meaningful vendor HAL/services represented?** {mapped_hal}/{len(m['device_hal'])} device-specific rows mapped; four E rows are the GPU scope.",
            f"12. **All firmware owners represented?** Yes, {len(m['fw'])}/{len(m['fw'])}; source availability is classified separately.",
            f"13. **All TEE/security interfaces represented?** Yes, {len(m['sw'])}/{len(m['sw'])} normal-world/secure boundaries; signed TA source is not claimed.",
            "14. **What remains worth static RE?** The ranked A-class list, camera ISP kernel split and Mali KMD; see PARTIAL-TRIAGE.md.",
            "15. **What cannot become open parity without vendor/physical access?** Modem/RIL/IMS, camera 3A/tuning, SCP/DSP algorithms, thermal radiometry/calibration, fingerprint/TEE TAs, DRM/keys, per-unit calibration, signed firmware, RF/thermal/mechanical details.",
            "16. **Best next 10?** YFT-DEVINFO, VINTF, vendor properties, FT3680, MT6375, DTB/DTBO, boot images, camera ISP kernel, Mali GPU kernel, vendor SELinux.",
            "17. **Taxonomy changes?** 1 ADD, 1 SPLIT, 4 MERGE recommendations, 2 REMOVE, 1 RENAME and one metadata/status-text refresh.",
            "18. **Corrected count if accepted?** **126** canonical components.",
            "19. **Can subsystem discovery stop being ad hoc?** Yes for the current stock build: all ten axes now have measured inventories and explicit orphans. Re-run harvesters for any new stock build.",
            "20. **Evidence?** 457 module rows, 580 compatible rows/930 nodes, 44 physical rows, 525 HAL/service rows, 80 firmware rows, 13 secure surfaces, 61 partition families, 654 Android-integration rows, 538 significant libraries and a 2,952-row unified artifact map.",
            "", "## Best next 10 targets", ""]
    out += [f"{n}. **{comp}** — {why}" for n, comp, why in BEST_10]
    a = m["manifest"]
    out += ["", "## Proposed resulting count", "",
            "`133 + 1 ADD + 1 split child − 7 merged-away components − 2 removed absence components = 126`.", "",
            "## Pack/manifest hygiene (separate from RE completeness)", "",
            f"Latest run: {a.get('rows_resolved', 0)}/{a.get('rows_total', 0)} manifest rows resolve; missing={a.get('rows_missing_file', 0)}; malformed={a.get('rows_wrong_field_count', 0)}; stale hash/size={a.get('rows_hash_mismatch', 0)}; unregistered={a.get('unregistered_files_total', 0)}; duplicate paths={len(a.get('duplicate_paths', []))}.",
            "The audit did not fix this unrelated drift. See notes/MANIFEST-HYGIENE.md.", "",
            "## Commits created before this report", "",
            "- `70871bf` — hardware/HAL/firmware/secure/boot axes and the single GPU gap",
            "- `970711f` — all 133 canonical components and PARTIAL A–F triage",
            "- `953b220` — Android integration, userspace libraries and unified artifact map",
            "", "See [PROPOSED-CHANGES.md](PROPOSED-CHANGES.md), [PARTIAL-TRIAGE.md](PARTIAL-TRIAGE.md), [MISSING-COVERAGE.md](MISSING-COVERAGE.md) and [PORT-READINESS.md](PORT-READINESS.md)."]
    save(CA / "SUMMARY.md", "\n".join(out))


def subsystem_sections(c: list[dict]) -> list[str]:
    specs = [
        ("1. Boot / partitions / AVB / OTA", ["AB-SUPER-GEOMETRY","AVB-SIGNING-CHAIN","BOOT-CONTROL-SLOTS","BOOT-IMAGES","DTB-DTBO","OTA-AB-UPDATE","PARTITION-OWNERSHIP","RECOVERY-ORANGEFOX"], "A/B geometry, AVB topology and slot safety are statically closed.", "Custom-image boot, OTA/snapshot and recovery acceptance remain.", "OEM signing/rollback state and live update safety cannot be inferred from static files alone."),
        ("2. Kernel infrastructure", ["GKI-KMI-BASELINE","INIT-INSMOD","MTK-MODULE-LOADER","OEM-KERNEL-MODULES","SYSTEM-DLKM","VENDOR-DLKM","VENDOR-ALL-MODULES-READY"], "Loader ordering and GKI/KMI baseline are known.", "Image parity and unresolved child modules remain umbrella work.", "Tracking scopes must not be mistaken for one source component."),
        ("3. Power / charging / battery", ["BATTERY-PACK","COOLING-HARDWARE","MT6375-CHARGER","PD-DBG-INFO","PD-PPS-UFCS","RT5133-POWER-IC","SC8510-BIDIRECTIONAL-CHARGE-PUMP","SC8571-CHARGE-PUMP","SH366003-FUEL-GAUGE","THERMAL-POWER-HAL","USB-CHARGER-INTEGRATION"], "Charge pumps, fuel gauge and core providers are mapped/mostly source-closed.", "MT6375 parity, policy/config and live negotiation/thermal behavior remain.", "Pack identity, cooling stack and high-power safety need physical/runtime evidence."),
        ("4. USB / Type-C", ["EXTCON-MTK-USB","EXTERNAL-USB","MTU3-SSUSB","TCPC-CLASS","TCPC-MT6375","USB-PHY","USB-TYPEC","USB3-FEASIBILITY"], "USB2 controller/PHY/extcon/TCPC topology is closed; SuperSpeed absence is proven.", "Runtime role/gadget/charging acceptance remains.", "USB3 finding should live under USB-TYPEC."),
        ("5. Display / touch / LEDs", ["AW2013-RGB-LED","BACKLIGHT-DISPLAY-GLUE","CO5300-REAR-DISPLAY","FT3680-TOUCH","HAPTICS","HYNITRON-REAR-TOUCH","MEDIATEK-DRM","MTK-DISP-NOTIFY","MTK-PWM","VTDR6115-DISPLAY"], "Main/rear display, DRM, rear touch, LEDs and haptics have named static closure.", "FT3680 parity and full runtime brightness/touch acceptance remain.", "Ilitek/Chipone enabled nodes are driverless reference-board baggage."),
        ("6. Camera", ["AW36515-FLASH","AW36518-FLASH","AW36518-V2-FLASH","CAMERA-EEPROMS","CAMERA-HAL-ISP","CAMERA-IMX989","CAMERA-OV64B","CAMERA-S5KJN1","CAMERA-S5KJN1MAIN2","CAMERA-VCMS","CUSTOM-LDO","DW9781C-OIS","WL2868-CAMERA-LDO"], "Sensor/VCM/OIS/EEPROM and power/flash kernel scopes are closed or strongly bounded.", "ISP kernel parity should be split and finished.", "HAL/3A/tuning/CCU/calibration remain proprietary."),
        ("7. Thermal camera", ["AC020-UVC","FM78100-COMPANION","INTERNAL-THERMAL-USB","THERMAL-RADIOMETRY","THERMOVUE-T2","YFT-TINY2C-USB"], "USB/UVC/internal power/companion kernel path is mapped and closed.", "Command protocol and replacement viewer remain.", "Radiometry algorithms and per-unit calibration are proprietary/device-internal."),
        ("8. Audio", ["AUDIO-DSP","AUDIO-DSP-KERNEL","AW883XX-SPEAKER-AMP","MICROPHONES","MT6369-AUDIO-CODEC","MT6878-AFE"], "Codec, AFE, DSP kernel transport and speaker-driver kernel scope are closed.", "Audio HAL routing and microphone runtime integration remain.", "DSP firmware/algorithms and calibration remain binary."),
        ("9. Connectivity", ["BLUETOOTH","CONNFEM","CONNINFRA-KERNEL","FM-KERNEL","FM-RADIO-HEADSET","MT6637-BT-KERNEL","MT6637-WIFI","MT6637-WIFI-KERNEL"], "Conninfra and Wi-Fi/BT/FM Linux sides are closed.", "Live RF/features and HAL integration remain.", "Controller firmware and radio calibration are proprietary."),
        ("10. Modem / telephony / IMS", ["CCCI-KERNEL","CCMNI-KERNEL","DPMAIF-KERNEL","IMS","MODEM-FIRMWARE","MODEM-KERNEL-TRANSPORT","RADIO-HAL-RIL"], "The reconstructable Linux modem transport is closed.", "Carrier/runtime RIL and IMS validation remain.", "MD1 firmware, vendor RIL/IMS and RF calibration are signed/proprietary."),
        ("11. Sensors / SCP / TinySys", ["ICM4N607-IMU","MMC5603-MAGNETOMETER","MTK-MBOX","MTK-RPMSG-MBOX","MTK-TINYSYS-IPI","SENSOR-HUB","SENSOR-HUB-KERNEL","SPL07-BAROMETER","STK3A5X-ALS-PS"], "Mailbox/IPI and sensorhub Linux transport are closed.", "Android sensor behavior/calibration validation remains.", "Physical sensor register drivers/fusion live in signed SCP firmware; no fake Linux-driver tasks."),
        ("12. Storage", ["MICROSD","MICROSD-KERNEL","UFS-RPMB-KERNEL","UFS-STORAGE"], "UFS, RPMB and microSD static contracts/kernel stacks are closed.", "Runtime media/gear/OTA interactions remain integration work.", "Device firmware and secure keys are not reconstructable."),
        ("13. NFC", ["NFC-SECURE-ELEMENT","ST21NFC"], "ST21NFC kernel/controller identity is closed.", "NCI/eSE runtime acceptance remains.", "Secure applets/access-control and controller firmware are proprietary."),
        ("14. Fingerprint / biometrics", ["FINGERPRINT-PLATFORM-SHIM","MADEV-FINGERPRINT","MICROARRAY-FP-TEE"], "Platform and normal-world kernel/TEE-client scopes are closed.", "HAL integration and enroll/auth validation remain.", "Sensor protocol, templates and TA are proprietary; five alternative rc services are dead baggage."),
        ("15. Security / TEE / RPMB", ["FFA-V10","GZ-IPC-MOD","GZ-MAIN-MOD","GZ-TRANSPORT","GZ-TRUSTY-MOD","GZ-TZ-SYSTEM","KEYSTORE-VOLD-KEYMINT","TKCORE-DRV","TMEM-FFA","TRUSTKERNEL-ABI-ISLAND","TRUSTKERNEL-TEE"], "Normal-world FF-A/GZ/TKCORE/TMEM/RPMB transport is represented and mostly closed.", "FBE/credential runtime and taxonomy consolidation remain.", "Secure-world payload/TA/private ABI source is blocked."),
        ("16. GNSS", ["GNSS","GNSS-KERNEL-TRANSPORT"], "Kernel transport and fitted connsys identity are closed.", "L1/L5/runtime validation remains.", "Firmware and mnld/libmnl engine are proprietary."),
        ("17. IR / rugged-device extras", ["IR-BLASTER","LN2403-CAMPLIGHT","PROGRAMMABLE-KEYS","REAR-RUGGED-FEATURES","YFT-DEVINFO","YFT-TPD-GESTURE"], "IR, keys, camp lights and gesture paths are represented; most kernel scopes are closed.", "YFT-DEVINFO residual and end-to-end rugged integration remain.", "Umbrella should remain a checklist, not duplicate child reconstruction."),
        ("18. Android HAL / framework integration", ["ANDROID-INIT","VENDOR-BLOB-HAL-INVENTORY","VENDOR-PROPERTIES","VENDOR-SEPOLICY","VINTF-HAL-MANIFEST"], "All stock/current integration artifacts are inventoried and owned.", "Generated VINTF/properties/policy/init acceptance remains.", "448 significant proprietary libraries require retention or independently demonstrated replacements."),
        ("19. NVRAM / calibration", ["FIRMWARE-INVENTORY","NVRAM-CALIBRATION"], "Partitions, consumers, hashes and firmware classes are mapped.", "Ownership labels and safe backup/restore validation remain.", "Per-unit values and vendor algorithms are private/device-internal."),
        ("20. Other board-specific glue", ["DRAM-MEMORY","ESIM-EUICC-ABSENCE","RF-ANTENNAS","SPI-MT65XX","WIRELESS-CHARGING-ABSENCE"], "SPI glue and negative eSIM/wireless findings are represented.", "DRAM package/training and RF antenna topology remain.", "These require signed boot firmware, schematics, teardown or RF measurement."),
    ]
    known = {r["component"] for r in c}
    out = []
    for title, names, closed, remains, boundary in specs:
        names = [n for n in names if n in known]
        out += [f"### {title}", "", f"- **Closed:** {closed}", f"- **Remains:** {remains}", f"- **Boundary:** {boundary}", "- **Components:** " + ", ".join(f"`{n}`" for n in names), ""]
    return out


def build_index(m: dict) -> None:
    c = m["components"]
    out = ["# GQ5012BF1 Reverse-Engineering Index", "",
           "## Purpose", "",
           "Authoritative human-readable ownership/status map for every canonical GQ5012BF1 reverse-engineering component needed by a LieppOS custom ROM and custom-kernel port.", "",
           "- **Phone:** Ulefone Armor 29 Pro Thermal",
           "- **Board/product:** GQ5012BF1",
           "- **Platform:** MediaTek MT6878T / Dimensity 7400 family",
           f"- **Audit date:** {DATE}",
           "- **Authoritative workspace:** `/home/armol/androido_dalykai/LieppOS custom ROM/`",
           "- **Machine database:** [`coverage-audit/components.tsv`](coverage-audit/components.tsv)", "",
           "## Status definitions", "",
           "- **DONE:** the explicitly named static/source/parity scope is closed. It does **not** imply open proprietary firmware/HAL/TA code or complete runtime validation.",
           "- **PARTIAL:** represented and useful, with an explicit actionable, proprietary, physical or umbrella boundary.",
           "- **BLOCKED:** the required evidence/source/access is unavailable; the blocker is named.",
           "- **TODO:** accepted component with no meaningful work yet. Current count is zero.", "",
           "## Methodology and evidence precedence", "",
           "The audit joins every shipped kernel module, effective merged DT compatible, physical hardware row, HAL/interface, init service, firmware/calibration payload, secure-world surface, partition family, Android integration file and significant native library back to the canonical workspace folders. Coverage classes are A dedicated, B broader owner, C generic/no dedicated RE, D dead/reference, E unmapped.", "",
           "Evidence precedence: (1) current verified stock/runtime captures, (2) newest authoritative research, (3) exact binary parity, (4) active device/vendor tree, (5) older provenance, (6) donor/reference assumptions.", "",
           "> **DONE is scope-specific.** Read the Kernel/Userspace/Firmware/Hardware columns and boundary; never infer whole-device source parity from the folder status.", "",
           "RE completeness is separate from pack hygiene. The latest manifest result is recorded in [`coverage-audit/notes/MANIFEST-HYGIENE.md`](coverage-audit/notes/MANIFEST-HYGIENE.md).", "",
           "## Current totals", "", "| Status | Count |", "|---|---:|"]
    for st in ("DONE", "PARTIAL", "BLOCKED", "TODO"):
        out.append(f"| {st} | {m['status'].get(st, 0)} |")
    out += [f"| **TOTAL** | **{len(c)}** |", "", "## PARTIAL classification", "", "| Classification | Count |", "|---|---:|"]
    for cls in "ABCDEF":
        out.append(f"| {cls} — {PARTIAL_MEANING[cls]} | {m['partial'].get(cls, 0)} |")
    out += ["", "## Master component table", "",
            "| Component | Status | Subsystem | Scope | Coverage class | Kernel | Userspace/HAL | Firmware | Hardware | Remaining work / boundary | Research |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in c:
        target = os.path.relpath(r["research_path"], "reverse-engineering")
        boundary = r["blocker"] or r["notes"]
        out.append("| " + " | ".join([
            esc(r["component"]), esc(r["status"]), esc(r["subsystem"]), esc(short(r["scope"], 150)),
            esc(r["partial_class"]), esc(r["kernel_state"]), esc(r["userspace_state"]),
            esc(r["firmware_state"]), esc(r["hardware_state"]), esc(short(boundary, 210)),
            f"[report]({target})",
        ]) + " |")
    out += ["", "## Subsystem summaries", ""] + subsystem_sections(c)
    out += ["## Missing components discovered", "",
            "One: **MALI-GPU-KERNEL**. See [`coverage-audit/MISSING-COVERAGE.md`](coverage-audit/MISSING-COVERAGE.md).", "",
            "## Duplicate / merge candidates", "",
            "Four migration records: consolidate four GZ children into GZ-TRANSPORT; AW36518-V2 into AW36518; USB3-FEASIBILITY into USB-TYPEC; VENDOR-ALL-MODULES-READY into INIT-INSMOD.", "",
            "## Split candidates", "",
            "One: split actionable **CAMERA-ISP-KERNEL** from proprietary `CAMERA-HAL-ISP`.", "",
            "## Stale / obsolete component candidates", "",
            "`ESIM-EUICC-ABSENCE` and `WIRELESS-CHARGING-ABSENCE` should become preserved negative findings rather than canonical components. `USB3-FEASIBILITY` is a resolved-negative merge candidate.", "",
            "## Components whose status may be wrong", "",
            "No evidence supports an automatic directory status move. RT5133's DONE static scope remains justified, but its canonical name should reflect the corrected camera-LDO role. OEM/VENDOR module umbrella prose must refresh 471→457 without changing PARTIAL.", "",
            "## Intentionally persistent PARTIAL scopes", "",
            "`FIRMWARE-INVENTORY`, `OEM-KERNEL-MODULES`, `REAR-RUGGED-FEATURES`, `SYSTEM-DLKM`, `VENDOR-BLOB-HAL-INVENTORY`, and `VENDOR-DLKM` are class F tracking/integration umbrellas. They should not become DONE merely because children close.", "",
            "## Generic shipped artifacts not requiring dedicated RE", "",
            f"{m['km_cov']['C']} kernel modules, {m['active_dt_cov']['C']} active DT-compatible rows, 188 HAL/service rows and 90 significant-name system libraries are generic/upstream/platform infrastructure. They remain enumerated as C rather than inflating the component count.", "",
            "## Dead/reference-board artifacts", "",
            f"- {m['km_cov']['D']} modules are dead/debug/reference baggage.",
            "- Enabled Ilitek/Chipone TDDI nodes have no shipped driver; fitted touch is FT3680 + Hynitron.",
            "- Twenty-two non-trigger init declarations point to absent executables, including five alternative fingerprint services and six legacy modem loggers.",
            "- The face example, virtual camera and DOOGEE-named EIS payload are explicit reference/example findings.", "",
            "## Proposed taxonomy result", "",
            "If every reviewed ADD/MERGE/SPLIT/REMOVE is accepted, the canonical total becomes **126**. No migration was executed by this audit.", "",
            "See [`coverage-audit/PROPOSED-CHANGES.md`](coverage-audit/PROPOSED-CHANGES.md) and [`coverage-audit/SUMMARY.md`](coverage-audit/SUMMARY.md)."]
    save(RE / "index.md", "\n".join(out))


def build_manifest_note(m: dict) -> None:
    a = m["manifest"]
    drift = ", ".join(f"`{k}` ({v.get('hash', 0)} hash/{v.get('size', 0)} size)" for k, v in a.get("components_with_drift", {}).items())
    unreg = ", ".join(f"`{k}` ({v})" for k, v in a.get("components_with_unregistered_files", {}).items())
    dup = ", ".join(f"`{x}`" for x in a.get("duplicate_paths", [])) or "None"
    stc = ", ".join(f"{k}={v}" for k, v in sorted(a.get("status_tree_components", {}).items()))
    out = f"""# Pack / manifest hygiene

Audit run: {DATE}

This is deliberately separate from reverse-engineering completeness.

The existing `reverse-engineering/scripts/manifest-audit.py` was run against the canonical workspace and `COPY-MANIFEST.tsv`. It exited non-zero because bookkeeping drift remains; no unrelated workspace file or manifest row was fixed.

| Measure | Result |
|---|---:|
| Manifest rows | {a.get('rows_total', 0)} |
| Resolved rows | {a.get('rows_resolved', 0)} |
| Missing files | {a.get('rows_missing_file', 0)} |
| Malformed rows | {a.get('rows_wrong_field_count', 0)} |
| Hash mismatches | {a.get('rows_hash_mismatch', 0)} |
| Size mismatches | {a.get('rows_size_mismatch', 0)} |
| Status-tree files | {a.get('status_tree_files_total', 0)} |
| Unregistered files | {a.get('unregistered_files_total', 0)} |
| Duplicate paths | {len(a.get('duplicate_paths', []))} |

Status-tree component counts from the independent run: {stc}.

## Drift owners

{drift or 'None'}.

## Unregistered-file owners

{unreg or 'None'}.

## Duplicate path

{dup}.

Full machine report: [`../audit-evidence/manifest-audit-2026-10-07.json`](../audit-evidence/manifest-audit-2026-10-07.json).
"""
    save(CA / "notes/MANIFEST-HYGIENE.md", out)


def build_readme(m: dict) -> None:
    out = f"""# GQ5012BF1 reverse-engineering coverage audit

Audit date: {DATE}

This directory is the reproducible coverage database behind [`../index.md`](../index.md).

## Verdict

**NEAR-COMPLETE:** one confirmed ownership gap (`MALI-GPU-KERNEL`), no unresolved possible gap meeting the component threshold.

## Reports

- [SUMMARY.md](SUMMARY.md) — measured verdict and explicit answers
- [PARTIAL-TRIAGE.md](PARTIAL-TRIAGE.md) — all 45 PARTIAL components, A–F
- [MISSING-COVERAGE.md](MISSING-COVERAGE.md) — confirmed/possible/not-missing/generic
- [PORT-READINESS.md](PORT-READINESS.md) — seven target readiness views
- [PROPOSED-CHANGES.md](PROPOSED-CHANGES.md) — reviewable taxonomy migration plan
- [notes/MANIFEST-HYGIENE.md](notes/MANIFEST-HYGIENE.md) — separate pack/manifest drift result

## Machine-readable tables

- `components.tsv` — {len(m['components'])} canonical components
- `artifact-map.tsv` — {len(m['art'])} normalized artifacts across axes 1–10
- `kernel-modules.tsv` — {len(m['km'])} modules
- `device-tree.tsv` — {len(m['dt'])} compatibles / {sum(int(r['nodes']) for r in m['dt'])} nodes
- `hardware.tsv` — 44 physical/absence/reference rows
- `hals-services.tsv` — {len(m['hs'])} VINTF/legacy-HAL rows
- `vendor-services.tsv` — {len(m['vs'])} init service/trigger-exec rows
- `firmware.tsv` — {len(m['fw'])} metadata-only payload rows
- `secure-world.tsv` — {len(m['sw'])} security boundaries
- `boot-storage.tsv` — 61 partition families
- `android-integration.tsv` — 654 stock/current integration files
- `userspace-libraries.tsv` — 538 significant library basenames

## Coverage classes

A dedicated component; B broader component; C generic/no dedicated RE; D dead/reference; E unmapped.

## Rebuild order

```sh
python3 scripts/harvest-pack-identity.py
python3 scripts/harvest-pack-module-claims.py
python3 scripts/harvest-pack-dt-claims.py
python3 scripts/harvest-pack-artifact-claims.py
python3 scripts/harvest-stock-artifacts.py
python3 scripts/harvest-integration.py
python3 scripts/build-kernel-modules.py
python3 scripts/build-devicetree.py
python3 scripts/build-hardware.py
python3 scripts/build-services.py
python3 scripts/build-integration.py
python3 scripts/build-components.py
python3 scripts/build-reports.py
python3 scripts/check-audit.py
```

`check-audit.py` is the fail-closed quality gate: it re-derives every universe total, coverage tally, orphan-class count, component-set equality with the canonical workspace folders, per-component research path existence and every relative link in the generated Markdown, and exits non-zero on any drift.

Harvesters read private/local stock and workspace trees; committed evidence contains metadata/textual claims only. No proprietary firmware/library payload is copied here.
"""
    save(CA / "README.md", out)


def main() -> int:
    m = metrics()
    build_partial(m)
    build_missing(m)
    build_changes()
    build_readiness()
    build_summary(m)
    build_index(m)
    build_manifest_note(m)
    build_readme(m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
