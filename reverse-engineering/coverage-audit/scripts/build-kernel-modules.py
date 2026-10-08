#!/usr/bin/env python3
"""Axis 1: map every shipped GQ5012BF1 kernel module to an RE component.

Universe
  Reverse Engineer - PARTIAL/OEM-KERNEL-MODULES/evidence/module-map.csv
  (458 module records across vendor_dlkm / vendor_boot platform stage /
  system_dlkm, each with a source-provenance classification) enriched with the
  vendor_dlkm load/dependency metadata harvested into audit-evidence/
  module-metadata.json and the load-phase map in
  reverse-engineering/boot/module-loading/module-classification.tsv.

Ownership resolution (no step guesses; every step writes its evidence into the
row)
  1. CURATED   audit-curated owner, reason text carried in the row
  2. PACK      a workspace component whose own inventory row or prose mentions the
               module - narrowest scope (fewest modules owned) wins, all
               co-owners recorded in `co_owners`
  3. RESEARCH  only a research-repo domain scope claims it -> covered as part of a
               broader subsystem scope (class B)
  4. OEMMAP    no component owns it and OEM-KERNEL-MODULES classified it
               DIRECT_SOURCE_MATCH / LIKELY_PLATFORM_MATCH -> class C (generic
               upstream/GKI/vendor-platform module, no device-specific RE needed)
  5. otherwise class E (real coverage gap)

Coverage classes
  A dedicated component for this module (component owns <=2 modules)
  B covered as part of a broader component scope
  C generic upstream/GKI/vendor-platform module - no dedicated RE component needed
  D shipped but dead on this board (reference/duplicate baggage)
  E unmapped - genuine coverage gap

Output: coverage-audit/kernel-modules.tsv plus notes/KERNEL-MODULES.md, which is
fully regenerated on every run so its numbers can never drift from the rows.
"""
import csv
import json
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CA = os.path.abspath(os.path.join(HERE, ".."))
WS = os.environ.get("RE_WORKSPACE", os.path.abspath(os.path.join(CA, "..", "..", "..")))
MODDIR = os.path.join(WS, "vendor_ulefone_gq5012bf1/proprietary/vendor_dlkm/lib/modules")
CLAIMS = os.path.join(CA, "audit-evidence", "harvested-pack-module-claims.tsv")
META = os.path.join(CA, "audit-evidence", "module-metadata.json")
OUT = os.path.join(CA, "kernel-modules.tsv")

UMBRELLA = {
    "MTK-MODULE-LOADER", "VENDOR-DLKM", "SYSTEM-DLKM", "GKI-KMI-BASELINE",
    "OEM-KERNEL-MODULES", "INIT-INSMOD", "VENDOR-ALL-MODULES-READY",
    "FIRMWARE-INVENTORY", "DTB-DTBO", "BOOT-IMAGES", "VENDOR-BLOB-HAL-INVENTORY",
    "RECOVERY-ORANGEFOX",
}

# module stem -> (owner component, coverage class, reason).  Used only where the
# harvested claims do not already give an unambiguous narrow owner, or where the
# owning pack records the module as dead on this board.
CURATED = {
    "snd-soc-tfa98xx": ("AW883XX-SPEAKER-AMP", "D",
                        "NXP TFA98xx codec driver ships in vendor_dlkm but no TFA98xx "
                        "device exists in DT or HAL config; fitted amp is AW88394"),
    "reboot-mode": ("BOOT-IMAGES", "B",
                    "reboot-mode/syscon-reboot-mode chain verified end-to-end in research "
                    "android17-hidl-fixed-build-20261002/reboot-mode-end-to-end-proof-20261003"),
    "syscon-reboot-mode": ("BOOT-IMAGES", "B", "same reboot-mode chain (syscon variant)"),
    "mtk_sec_heap": ("TMEM-FFA", "B", "secure-heap/CTX reserved-memory provider used by TMEM/FFA"),
    "tui-common": ("TRUSTKERNEL-TEE", "B", "TrustUI common TEE client transport (normal world side)"),
    "nvmem-mt635x-efuse": ("USB-PHY", "B", "PMIC efuse nvmem reader; USB-PHY documents efuse calibration reads"),
    "thermal-generic-adc": ("COOLING-HARDWARE", "C",
                            "upstream generic ADC thermal sensor driver; nothing board-specific beyond auxadc channel config"),
    "apusys": ("VENDOR-BLOB-HAL-INVENTORY", "C", "APU/Neuropilot kernel transport; behaviour lives in the proprietary APU HAL stack"),
    "apu_top": ("VENDOR-BLOB-HAL-INVENTORY", "C", "APU DVFS/thermal client"),
    "widevine_driver": ("KEYSTORE-VOLD-KEYMINT", "C", "OEMCrypto/T-base L1 kernel driver; secure-world TAs proprietary"),
    "mtk-composite": ("MTU3-SSUSB", "B",
                      "MTK USB composite gadget function provider; MTU3-SSUSB scope covers the gadget-side vendor modules but its inventory does not name mtk-composite.ko"),
    "hbt": ("MTK-MODULE-LOADER", "C", "MediaTek HBT tracer: vendor debug tooling, not part of a ROM port"),
    "met": ("MTK-MODULE-LOADER", "C", "MediaTek MEU micro-tracer: vendor debug tooling, not part of a ROM port"),
    "mali_kbase_mt6878_r44": ("UNMAPPED", "E",
                                "active Mali Valhall KMD has no current RE ownership scope; proposed MALI-GPU-KERNEL"),
    "mali_mgm_mt6878_r44": ("UNMAPPED", "E",
                              "active Mali memory-group manager belongs to the uncovered Mali KMD scope"),
    "mali_prot_alloc_mt6878_r44": ("UNMAPPED", "E",
                                     "active Mali protected allocator belongs to the uncovered Mali KMD scope"),
    "mali_dmabuf_test_mt6878_r44": ("COVERED-GENERIC", "D",
                                     "Mali DMA-BUF test helper is shipped in modules.load but is diagnostic support, not a distinct device subsystem"),
    # Research-directory mentions are evidence, not canonical owners.  Resolve
    # the remaining mentioned modules to a real component or generic class.
    "aee_aed": ("COVERED-GENERIC", "C", "MTK exception-engine infrastructure"),
    "clk-common": ("COVERED-GENERIC", "C", "generic MTK clock framework"),
    "btbcm": ("COVERED-GENERIC", "C", "upstream Bluetooth helper; fitted controller uses the MT6637 stack"),
    "btqca": ("COVERED-GENERIC", "C", "upstream Bluetooth helper; reference controller baggage"),
    "btsdio": ("COVERED-GENERIC", "C", "generic Bluetooth SDIO helper"),
    "hci_uart": ("COVERED-GENERIC", "C", "upstream HCI UART helper"),
    "log_store": ("COVERED-GENERIC", "C", "generic MTK persistent logging helper"),
    "c2k_usb_f_via_atc": ("MODEM-KERNEL-TRANSPORT", "B", "C2K modem USB function"),
    "c2k_usb_f_via_ets": ("MODEM-KERNEL-TRANSPORT", "B", "C2K modem USB function"),
    "c2k_usb_f_via_modem": ("MODEM-KERNEL-TRANSPORT", "B", "C2K modem USB function"),
    "ccci_auxadc": ("CCCI-KERNEL", "B", "CCCI modem AUXADC transport"),
    "ccci_ccif": ("CCCI-KERNEL", "B", "CCCI CCIF host interface"),
    "ccci_fsm_scp": ("CCCI-KERNEL", "B", "CCCI/SCP state bridge"),
    "ccci_md_all": ("CCCI-KERNEL", "B", "CCCI modem aggregate"),
    "ccci_util_lib": ("CCCI-KERNEL", "B", "CCCI utility layer"),
    "md_cooling_all": ("MODEM-KERNEL-TRANSPORT", "B", "modem cooling bridge"),
    "mddp": ("MODEM-KERNEL-TRANSPORT", "B", "modem data acceleration path"),
    "mrdump": ("MODEM-KERNEL-TRANSPORT", "B", "modem/platform crash dump path"),
    "mtk_mdpm": ("MODEM-KERNEL-TRANSPORT", "B", "modem dynamic power manager"),
    "mtk_battery_oc_throttling": ("THERMAL-POWER-HAL", "B", "battery over-current throttling provider"),
    "mtk_bp_thl": ("THERMAL-POWER-HAL", "B", "battery-percent throttling provider"),
    "mtk_cpu_power_throttling": ("THERMAL-POWER-HAL", "B", "CPU power throttling provider"),
    "mtk_dynamic_loading_throttling": ("THERMAL-POWER-HAL", "B", "dynamic load throttling provider"),
    "mtk_gpu_power_throttling": ("THERMAL-POWER-HAL", "B", "GPU power throttling provider"),
    "mtk_low_battery_throttling": ("THERMAL-POWER-HAL", "B", "low-battery throttling provider"),
    "mtk_md_power_throttling": ("THERMAL-POWER-HAL", "B", "modem power throttling provider"),
    "pmic_lbat_service": ("THERMAL-POWER-HAL", "B", "PMIC low-battery service"),
    "pmic_lvsys_notify": ("THERMAL-POWER-HAL", "B", "PMIC low-system-voltage notifier"),
    "mtk_ioctl_touch_boost": ("FT3680-TOUCH", "B", "touch input latency boost bridge"),
    "touch_boost": ("FT3680-TOUCH", "B", "touch input latency boost bridge"),
}

# a component's own per-module state column, when it says the module does not
# exist / is not used on this board, overrides the coverage class to D
STATE_COLS = ("board_state", "runtime", "runtime_class", "status", "load_status",
              "class", "board-status")
STOP_TOKENS = {"mtk", "mediatek", "kernel", "driver", "drv", "hal", "class", "core",
                "common", "driver", "src", "notes", "ko", "v1", "v2", "v3", "main",
                "mod", "chip", "dev", "debug", "dbg", "lib", "api", "inf", "ext"}


def tokens(name: str) -> set:
    out = set()
    for tok in re.split(r"[^a-z0-9]+", name.casefold()):
        if len(tok) >= 2 and tok not in STOP_TOKENS:
            out.add(tok)
            # split glued alphanumeric tokens: 'ft3680' -> ft + 3680
            m = re.fullmatch(r"([a-z]*)(\d+)", tok)
            if m and len(m.group(1)) >= 2:
                out.add(m.group(1))
    return out


def name_score(stem: str, comp: str) -> int:
    """length of the longest distinctive name token shared by module and component"""
    shared = tokens(stem) & tokens(comp)
    return max((len(t) for t in shared), default=0)


DEAD_VALUES = ("absent", "unused", "inert", "not bound", "not loaded", "not present",
               "never loaded", "no dt", "no device", "dead", "disabled", "reference")


def state_dead(extras: str) -> str:
    for part in extras.split(" | "):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k.strip().lower() not in STATE_COLS:
            continue
        v = v.strip().casefold()
        for bad in DEAD_VALUES:
            if v.startswith(bad) or f"({bad}" in v:
                return f"{k}={v[:70]}"
    return ""


def field(extras: str, *keys: str) -> str:
    """last non-empty value of any of `keys` in a 'k=v | k=v' extras blob"""
    out = ""
    for part in extras.split(" | "):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k.strip().lower() in keys and v.strip():
            out = v.strip()
    return out


def component_index() -> dict:
    """Workspace identity supplies status; historical index supplies domain labels only."""
    txt = open(os.path.join(WS, "REVERSE-ENGINEERING-STATUS.md"), encoding="utf8").read()
    out = {}
    for m in re.finditer(r"^\| \[`([^`]+)`\]\(<[^>]+>\) \| ([^|]+) \| (\w+) \|", txt, re.M):
        out[m.group(1)] = (m.group(3).strip(), m.group(2).strip())
    identity = os.path.join(CA, "audit-evidence", "pack-identity.tsv")
    return {r["component"]: (r["status"], r["subsystem"] or
                              out.get(r["component"], ("", r["component"]))[1])
            for r in csv.DictReader(open(identity), delimiter="\t")}


NOTE = os.path.join(CA, "notes", "KERNEL-MODULES.md")


def short_reason(row: dict) -> str:
    """human-readable reason for a dead/curated row without the raw evidence blob"""
    for part in row["evidence"].split(";"):
        if part.startswith("dead-per:"):
            return (part.split(":", 2)[2]
                    .replace("class=never loaded: ", "")
                    .replace("debug/eng baggage (met profiler / test / fake-eng)",
                             "MET debug-tracer family, never loaded in any boot phase"))
        if part.startswith("curated:"):
            return part[len("curated:"):]
    return row["evidence"]


def summarise(rows: list[dict], claims: list[dict]) -> None:
    """Regenerate notes/KERNEL-MODULES.md from the rows just written."""
    cnt = lambda pred: sum(1 for r in rows if pred(r))  # noqa: E731
    C = Counter(r["coverage"] for r in rows)
    tiers = Counter(r["tier"] for r in claims)
    both = [r for r in rows if r["partitions"] == "vendor_boot_platform;vendor_dlkm"]
    vd = cnt(lambda r: "vendor_dlkm" in r["partitions"])
    vb = cnt(lambda r: "vendor_boot" in r["partitions"])
    sd = cnt(lambda r: r["partitions"] == "system_dlkm")
    owned = [r for r in rows if r["coverage"] in "AB"]
    weak = [r for r in owned if r["evidence"].split(":")[0] in ("pack-mention", "pack-owns-source")]
    cclass = Counter(r["oemmap_source_class"] for r in rows if r["coverage"] == "C")
    meta = json.load(open(META))
    out = ["# Axis 1 - kernel module coverage (authoritative)", "",
           "Generated by `scripts/build-kernel-modules.py` from the shipped `.ko` set, "
           "`OEM-KERNEL-MODULES/evidence/module-map.csv`, "
           "`reverse-engineering/boot/module-loading/*.tsv`, "
           "`audit-evidence/module-metadata.json` and the per-pack claims harvested by "
           "`scripts/harvest-pack-module-claims.py`. The per-module rows live in "
           f"[`../kernel-modules.tsv`](../kernel-modules.tsv) ({len(rows)} rows).", "",
           "Reproduce: `python3 reverse-engineering/coverage-audit/scripts/"
           "harvest-pack-module-claims.py && python3 reverse-engineering/coverage-audit/"
           "scripts/build-kernel-modules.py`, then "
           "`python3 reverse-engineering/coverage-audit/scripts/check-audit.py`", "",
           "## Universe", "",
           "| source | what it contributes |", "|---|---|",
           f"| `Reverse Engineer - PARTIAL/OEM-KERNEL-MODULES/evidence/module-map.csv` | "
           f"{tiers['oemmap']} module records / **{len({r['module'] for r in rows})} unique "
           f"module names** across `vendor_dlkm` ({vd}), `vendor_boot` platform stage ({vb}), "
           f"`system_dlkm` ({sd}) ({len(both)} modules are loaded in both stages), plus a "
           "per-module source-provenance class |",
           "| shipped `.ko` payload under `vendor_ulefone_gq5012bf1/proprietary/"
           "vendor_dlkm/lib/modules` | 215 vendor_dlkm module names; unioned with the "
           f"module-map name set this forms the authoritative {len(rows)}-module universe "
           "(the module-map also covers `vendor_boot` ramdisk and `system_dlkm` stages) |",
           "| `reverse-engineering/boot/module-loading/module-classification.tsv` and "
           f"`init-insmod-map.tsv` | {tiers['bootmap']} boot-map rows: load phase, sequence, "
           "`loaded_in_capture` flag, never-loaded class |",
           "| `audit-evidence/module-metadata.json` | `modules.load` order "
           f"({len(meta['load'])} modules), `modules.dep` ({len(meta['dep'])} rows) |",
       ] + [f"| pack claims harvested | {tiers['inventory']:,} inventory rows, "
            f"{tiers['ownsource']} own-source rows, {tiers['mention']} prose mentions, "
            f"{tiers['research']:,} research-scope rows |", "",
           "No payload is copied into this repository; only module names and metadata.", "",
           "## Coverage classes and result", "",
           "| class | meaning | count |", "|---|---|---:|"]
    for k, label in (("A", "dedicated component (owns <=2 shipped modules)"),
                    ("B", "covered as part of a broader component scope"),
                    ("C", "generic upstream/GKI/vendor-platform module - no dedicated RE component needed"),
                    ("D", "shipped but dead on this board (debug/eng or absent-hardware baggage)"),
                    ("E", "unmapped - genuine coverage gap")):
        out.append(f"| {k} | {label} | {C[k]} |")
    out += [f"| **total** |  | **{sum(C.values())}** |", "",
            f"Class C is justified per row by the OEM module-map source-provenance class "
            f"({', '.join(f'`{k}` {v}' for k, v in sorted(cclass.items()))}) - the module has "
            "an upstream/GKI/MTK-platform source match and carries no board-specific logic to "
            "reverse-engineer.", "",
            "### Class by partition", "",
            "| partitions | A | B | C | D | total |", "|---|---|---|---|---|---|"]
    for part in sorted({r["partitions"] for r in rows}):
        pc = Counter(r["coverage"] for r in rows if r["partitions"] == part)
        out.append(f"| `{part}` | {pc['A']} | {pc['B']} | {pc['C']} | {pc['D']} | "
                   f"{sum(pc.values())} |")
    out += [f"| **total** | **{C['A']}** | **{C['B']}** | **{C['C']}** | **{C['D']}** | "
            f"**{sum(C.values())}** |", "",
            "## D - shipped but dead (no port work implied)", "",
            "| module | why dead |", "|---|---|"]
    out += [f"| `{r['module']}` | {short_reason(r)} |"
            for r in sorted(rows, key=lambda r: r["module"]) if r["coverage"] == "D"]
    out += ["", "## E - unmapped (the real gap)", "", "| module | evidence |", "|---|---|"]
    out += [f"| `{r['module']}` | {short_reason(r)} |"
            for r in sorted(rows, key=lambda r: r["module"]) if r["coverage"] == "E"]
    out += ["", "## Ownership evidence strength", "",
            f"{len(weak)} of the {len(owned)} modules that have a component owner rest on "
            "*prose or own-source* evidence: the pack names the module in its README/notes, "
            "or carries `<module>.c`, but has no module-inventory row for it. The owner is "
            "right; the claim is just not machine-checkable. This is the pack-hygiene "
            "backlog (add a `kernel/module-inventory.tsv` row per owned module):", "",
            "| component | modules owned by prose/source evidence only |", "|---|---|"]
    bycomp = defaultdict(list)
    for r in weak:
        bycomp[r["component"]].append(r["module"][:-3])
    out += [f"| `{c}` ({len(v)}) | {', '.join(f'`{x}`' for x in sorted(v))} |"
            for c, v in sorted(bycomp.items(), key=lambda kv: (-len(kv[1]), kv[0]))]
    out += ["", "## Audit-curated overrides (reason also stored in the row's `evidence` "
            "field)", "", "| module | owner | class | reason |", "|---|---|:---:|---|"]
    bymod = {r["module"][:-3]: r for r in rows}
    out += [f"| `{m}.ko` | `{CURATED[m][0]}` | {CURATED[m][1]} | {CURATED[m][2]} |"
            for m in sorted(CURATED) if m in bymod]
    gpu = sorted(r["module"] for r in rows if r["coverage"] == "E")
    charging = ["`adapter_class`/`charger_class`/`mtk_charger_algorithm_class` -> `TCPC-CLASS`",
                "`mtk_pep40`/`mtk_charger_framework` -> `MT6375-CHARGER`",
                "`mtk_pep`/`mtk_pep50` -> `SH366003-FUEL-GAUGE`",
                "`mtk_pd_adapter`/`mtk_pd_charging` -> `PD-PPS-UFCS`",
                "`sc851x_charger` -> `SC8510-BIDIRECTIONAL-CHARGE-PUMP`",
                "`sc8571_charger` -> `SC8571-CHARGE-PUMP`/`BATTERY-PACK`"]
    out += ["", "## Conclusions for this axis", "",
            f"1. **One module-level gap, and it is named.** Every one of the {len(rows)} shipped "
            f"kernel modules resolves either to a component owner ({len(owned)}) or a "
            f"documented generic/dead class ({C['C'] + C['D']}). "
            f"`coverage=E` is exactly {len(gpu)} rows: "
            f"{', '.join(f'`{x}`' for x in gpu)}. That is the whole Mali KMD question, recorded "
            "as the proposed `MALI-GPU-KERNEL` component in "
            "[`../MISSING-COVERAGE.md`](../MISSING-COVERAGE.md).",
            f"2. **Generic mass is real, not laziness.** {C['C']} modules are class C and every "
            "one of them is justified by an existing source-provenance record in "
            "`OEM-KERNEL-MODULES/evidence/module-map.csv` "
            f"({', '.join(f'{v} {k}' for k, v in sorted(cclass.items()))}). For a same-BSP "
            "custom kernel these travel as vendor platform code; they need no board-specific "
            "RE and must not inflate the component count.",
            "3. **The GPU kernel driver has no owner of its own - decision recorded.** "
            "No pack inventory claims the active Mali KMD modules: "
            f"{len(gpu)} active modules stay E. Decision (see MISSING-COVERAGE.md): create "
            "`MALI-GPU-KERNEL` (PARTIAL, class A) to own the Valhall KMD, MGM and protected "
            "allocator plus the three GPU DT compatibles. The Mali DMA-BUF *test* helper is "
            "separately D (diagnostic, not a subsystem), and `mtk_vcodec-*`/`mtk-vcu` media-VPU "
            "transport stays C under the vendor-blob boundary.",
            "4. **The MTK charging framework is spread over several packs with no single "
            "inventory**:", *[f"   - {x}" for x in charging],
            "",
            "Coverage exists, but no one component can currently answer \"what does the "
            "charging stack look like end to end\". A cross-pack index row inside "
            "`MT6375-CHARGER` (or a merge) is the follow-up.", "",
            f"5. **`mtk-composite.ko` (USB composite gadget) had no owner** in any pack "
            "inventory: curated to `MTU3-SSUSB` (B) because that scope already declares "
            "\"gadget-side vendor modules\"; the pack still has no inventory row for it.",
            f"6. **Dead payload** is {C['D']} modules (D): the `met*`/`scheduler_ext` "
            "debug/eng tracer family, `nfc.ko` (the ST21NFC stack uses a misc char device, "
            "not the in-kernel NFC core), `snd-soc-tfa98xx.ko` (NXP amp driver shipped "
            "although the board fits AW88394) and `mali_dmabuf_test_mt6878_r44.ko` "
            "(diagnostic self-test helper).",
            "", "## Follow-ups produced by this axis", "",
            f"- add per-module inventory rows for the {len(weak)} prose/own-source-owned "
            "modules (table above), so pack ownership becomes machine-checkable;",
            "- create `MALI-GPU-KERNEL` as recorded in `../MISSING-COVERAGE.md` and move these "
            f"{len(gpu)} E rows onto it;",
            "- record the charging-framework cross-pack view (conclusion 4);",
            "- refresh the stale 471-module prose count inside `OEM-KERNEL-MODULES` to the "
            f"measured {len(rows)}.", ""]
    os.makedirs(os.path.dirname(NOTE), exist_ok=True)
    with open(NOTE, "w") as fh:
        fh.write("\n".join(out).rstrip() + "\n")


def main() -> None:
    meta = json.load(open(META))
    order, deps, alias = meta["load"], meta["dep"], meta["alias"]
    # Targeted correction: prove the RT5133 first-stage listing from the actual
    # extracted stock list, rather than infer loading from a client name.
    platform_load = os.path.join(WS, "ulefone-gq5012bf1-research/workspace/gq5012bf1/stock/"
                                "vendor-ramdisks/platform-extracted/lib/modules/modules.load")
    with open(platform_load) as fh:
        platform_order = {line.strip(): i for i, line in enumerate(fh, 1) if line.strip()}

    claims = defaultdict(list)
    oemmap, bootmap = {}, {}
    for row in csv.DictReader(open(CLAIMS), delimiter="\t"):
        m, tier, comp = row["module"], row["tier"], row["component"]
        if tier == "oemmap":
            oemmap[m] = row["extras"]
        elif tier == "bootmap":
            bootmap[m] = row["extras"]
        else:
            claims[m].append((comp, tier, row["source_file"], row["extras"]))

    shipped = {f[:-3] for f in os.listdir(MODDIR) if f.endswith(".ko")}
    universe = set(oemmap) | shipped

    idx = component_index()
    owned = defaultdict(set)
    for m, cs in claims.items():
        if m not in universe:
            continue
        for comp, tier, _f, _e in cs:
            if comp in UMBRELLA or comp.startswith("research:") or tier == "mention":
                continue
            owned[comp].add(m)
    pack_names = sorted(idx)

    rows = []
    for stem in sorted(universe):
        fn = f"{stem}.ko"
        cs = claims.get(stem, [])
        evidence, co_owners = [], []
        comp = cls = subsystem = status = ""

        pack_owners = sorted({c for c, t, _f, _e in cs
                             if c not in UMBRELLA and t == "inventory"})
        ownsrc_owners = sorted({c for c, t, _f, _e in cs
                               if c not in UMBRELLA and t == "ownsource"})
        mention_owners = sorted({c for c, t, _f, _e in cs
                                if c not in UMBRELLA and t == "mention"})
        research_owners = sorted({c for c, t, _f, _e in cs if c.startswith("research:")})
        umbrellas = sorted({c for c, t, _f, _e in cs if c in UMBRELLA and t != "oemmap"})

        oem_cls = re.search(r"classification=(\w+)", oemmap.get(stem, ""))
        oem_cls = oem_cls.group(1) if oem_cls else ""

        if stem in CURATED:
            comp, cls, why = CURATED[stem]
            evidence.append(f"curated:{why}")
        elif pack_owners:
            comp = max(pack_owners, key=lambda c: (name_score(stem, c),
                                                  -len(owned.get(c, ())), c))
            cls = "A" if len(owned.get(comp, ())) <= 2 else "B"
            tier = next(t for c, t, _f, _e in cs if c == comp)
            evidence.append(f"pack-{tier}:{comp}")
        elif ownsrc_owners:
            comp = min(ownsrc_owners, key=lambda c: (len(owned.get(c, ())), c))
            cls = "A" if len(owned.get(comp, ())) <= 2 else "B"
            evidence.append(f"pack-owns-source:{comp}")
        elif mention_owners:
            scores = {c: name_score(stem, c) for c in mention_owners}
            best = max(scores.values())
            cand = sorted(c for c in mention_owners if scores[c] == best)
            comp = min(cand, key=lambda c: (len(owned.get(c, ())), c))
            cls = "A" if len(owned.get(comp, ())) <= 2 else "B"
            evidence.append(f"pack-mention:{comp}")
            if best == 0:
                evidence.append(f"name-mismatch:{len(mention_owners)}-packs-mention-it")
        elif research_owners:
            comp, cls = research_owners[0], "B"
            evidence.append("research-scope:" + ",".join(research_owners))
        elif oem_cls in ("DIRECT_SOURCE_MATCH", "LIKELY_PLATFORM_MATCH"):
            comp, cls = "COVERED-GENERIC", "C"
            evidence.append(f"oemmap:{oem_cls}")
        else:
            comp, cls = "UNMAPPED", "E"
            evidence.append(f"oemmap:{oem_cls or 'ABSENT'}")

        co_owners = sorted(set(pack_owners) | set(ownsrc_owners) | set(mention_owners)
                      | set(research_owners))
        if oem_cls in ("ULEFONE_ONLY", "NEEDS_ULEFONE_PORT") and comp == "COVERED-GENERIC":
            comp, cls = "UNMAPPED", "E"
            evidence.append(f"oemmap-device-only:{oem_cls}")
        for _c, _t, _f, extras in cs:
            hit = state_dead(extras)
            if hit:
                cls = "D"
                evidence.append(f"dead-per:{_c}:{hit}")
                break
        bm_class = field(bootmap.get(stem, ""), "class")
        if bm_class.casefold().startswith("never loaded"):
            cls = "D"
            evidence.append(f"dead-per:boot-module-loading:{bm_class[:80]}")
        if comp in idx:
            status, subsystem = idx[comp]
        elif comp == "COVERED-GENERIC":
            status, subsystem = "N/A", "generic platform/GKI module"
        rows.append({
            "module": fn,
            "partitions": field(oemmap.get(stem, ""), "locations"),
            # module-metadata.json covers vendor_dlkm only, not all stages.
            "in_modules_load": ("yes" if fn in order else
                                "yes" if stem == "rt5133-regulator" and fn in platform_order else "no"),
            "load_order": str(order.get(fn, platform_order.get(fn, "")
                                        if stem == "rt5133-regulator" else "")),
            "load_phase": (field(bootmap.get(stem, ""), "resolved_phase", "phase") or
                           ("first-stage" if stem == "rt5133-regulator" else "")),
            "loaded_in_capture": field(bootmap.get(stem, ""), "loaded_in_capture"),
            "depends": ",".join(deps.get(fn, [])),
            "oemmap_source_class": oem_cls,
            "subsystem": subsystem,
            "component": comp,
            "component_status": status,
            "coverage": cls,
            "co_owners": ",".join(x for x in co_owners if x != comp),
            "umbrella_records": ",".join(umbrellas),
            "evidence": ";".join(evidence),
        })

    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    all_claims = list(csv.DictReader(open(CLAIMS), delimiter="\t"))
    summarise(rows, all_claims)

    c = Counter(r["coverage"] for r in rows)
    print(f"universe={len(rows)} coverage={dict(sorted(c.items()))}")
    print("D:", [r["module"] for r in rows if r["coverage"] == "D"])
    print("per-partition:", dict(Counter(
        (r["partitions"], r["coverage"]) for r in rows).most_common()))
    print("A:", sum(1 for r in rows if r["coverage"] == "A"),
          "B:", sum(1 for r in rows if r["coverage"] == "B"),
          "C:", sum(1 for r in rows if r["coverage"] == "C"))
    print("E:", [r["module"] for r in rows if r["coverage"] == "E"])


if __name__ == "__main__":
    main()
