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

Output: coverage-audit/kernel-modules.tsv
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
    """component -> (status, subsystem) from the canonical workspace index."""
    txt = open(os.path.join(WS, "REVERSE-ENGINEERING-STATUS.md"), encoding="utf8").read()
    out = {}
    for m in re.finditer(r"^\| \[`([^`]+)`\]\(<[^>]+>\) \| ([^|]+) \| (\w+) \|", txt, re.M):
        out[m.group(1)] = (m.group(3).strip(), m.group(2).strip())
    return out


def main() -> None:
    meta = json.load(open(META))
    order, deps, alias = meta["load"], meta["dep"], meta["alias"]

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
            "in_modules_load": "yes" if fn in order else "no",
            "load_order": str(order.get(fn, "")),
            "load_phase": field(bootmap.get(stem, ""), "resolved_phase", "phase"),
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
