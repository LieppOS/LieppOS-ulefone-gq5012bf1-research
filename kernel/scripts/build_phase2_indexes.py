#!/usr/bin/env python3
import argparse
import csv
import hashlib
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

PARTITION_EXPECTED = {
    "vendor_boot_platform": 196,
    "vendor_dlkm": 215,
    "system_dlkm": 60,
}
EXPECTED_PLACEMENTS = 471
EXPECTED_UNIQUE_SHA = 458
EXPECTED_UNIQUE_FILENAMES = 457

MAKE_OBJ_RE = re.compile(r"^\s*obj-\$\((CONFIG_[A-Za-z0-9_]+)\)\s*\+=\s*([^#]+)")
COMPOSITE_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)-(?:objs|y|\$\([^)]*\))\s*\+=\s*([^#]+)")
ALIAS_RE = re.compile(r'MODULE_ALIAS\s*\(\s*"([^"]+)"\s*\)')
EXPORT_RE = re.compile(r"EXPORT_SYMBOL(?:_GPL)?\s*\(\s*([A-Za-z0-9_]+)\s*\)")
COMPAT_RE = re.compile(r'\.compatible\s*=\s*"([^"]+)"')
SOFTDEP_RE = re.compile(r'MODULE_SOFTDEP\s*\(\s*"([^"]+)"\s*\)')
BZL_KO_RE = re.compile(r'["\']([^"\']+\.ko)["\']')

MANUAL_CLASS = {
    # Ulefone/YFT-specific modules established from stock evidence.
    "focaltech_touch_spi_ft3680": ("NEEDS_ULEFONE_PORT", "Ulefone FT3680 driver; Nothing has related FT3519 family source but no direct FT3680 module/API match"),
    "hynitron": ("ULEFONE_ONLY", "Ulefone secondary-touch driver; no convincing Nothing source match found"),
    "spi_tiny_co5300_lcd": ("ULEFONE_ONLY", "Ulefone secondary-display driver; no convincing Nothing source match found"),
    "yft_devinfo": ("ULEFONE_ONLY", "YFT/Ulefone board-device registration infrastructure"),
    "yft_tpd_gesture": ("ULEFONE_ONLY", "YFT/Ulefone gesture-wake ABI provider"),
    "yft_gpio_keys": ("ULEFONE_ONLY", "YFT/Ulefone GPIO keys implementation"),
    "yft_tiny2c_usb": ("ULEFONE_ONLY", "YFT/Ulefone USB/charger glue"),
    "microarray_fp_tee": ("ULEFONE_ONLY", "Microarray fingerprint module; Nothing tree uses a different fingerprint family"),
    "sc8571_charger": ("ULEFONE_ONLY", "SC8571 charger module; no convincing Nothing source match found"),

    # UNKNOWN-resolution audit: direct MT6878 source donor.
    "connfem": ("DIRECT_SOURCE_MATCH", "Nothing MT6878 publishes the connfem external-module source and MT6878 connfem DTS integration; stock module/API evidence matches"),
    "conninfra": ("DIRECT_SOURCE_MATCH", "Nothing MT6878 publishes the conninfra external-module source; stock module name and exported conninfra API are present"),
    "gps_pwr": ("DIRECT_SOURCE_MATCH", "Nothing MT6878 publishes connectivity/gps/gps_pwr source and builds it as an external module"),
    "gps_scp": ("DIRECT_SOURCE_MATCH", "Nothing MT6878 publishes connectivity/gps/gps_scp source with exact module/build references"),
    "gps_drv_dl_v051": ("DIRECT_SOURCE_MATCH", "Nothing MT6878 publishes the GPS data_link external-module source and an exact gps_drv_dl_v051 build target"),
    "wmt_chrdev_wifi_connac2": ("DIRECT_SOURCE_MATCH", "Nothing MT6878 publishes the WLAN adaptor external-module source; exact module/API evidence identifies wmt_chrdev_wifi_connac2"),
    "wlan_drv_gen4m_6878": ("DIRECT_SOURCE_MATCH", "Nothing MT6878 contains the exact wlan_drv_gen4m_6878 build target and gen4m WLAN source tree"),

    # Same platform/family source exists, but exact source/build equivalence is not yet proven.
    "bt_drv_6878": ("LIKELY_PLATFORM_MATCH", "Nothing MT6878 builds the MediaTek BT linux_v2 stack and contains matching btmtk API, but the exact bt_drv_6878 output target was not proven"),
    "leds_rgb_aw2013": ("LIKELY_PLATFORM_MATCH", "Nothing common kernel contains an AW2013 driver for the same chip family; Ulefone uses a custom awinic,rgb,aw2013 compatible and needs integration comparison"),

    # Public/vendor source exists outside the Nothing donor, so port rather than reverse engineer.
    "aw883xx_driver": ("NEEDS_ULEFONE_PORT", "Awinic publishes GPL-2.0 AW883xx Smart PA driver source; port and compare against the Ulefone module instead of reconstructing from binary"),
    "aw36515": ("NEEDS_ULEFONE_PORT", "Awinic publishes AW36515 Android driver/porting resources; Nothing only provided matching hardware/DTS evidence"),
    "aw36518": ("NEEDS_ULEFONE_PORT", "Awinic publishes AW36518 Android driver/porting resources; no exact Nothing source implementation was found"),
    "aw36518_v2": ("NEEDS_ULEFONE_PORT", "Awinic publishes AW36518/AW3651X Android driver resources; Ulefone's V2 module requires integration/ABI comparison"),

    # No usable source donor found in the Nothing tree or current external-source audit.
    "panel_ky_vtdr6115_dphy_cmd": ("ULEFONE_ONLY", "VTDR6115 panel hardware is identified, but no usable Nothing/public kernel panel source was found in the current audit"),
    "leds_ln2403": ("ULEFONE_ONLY", "LN2403 hardware/datasheet is identifiable, but no usable kernel driver source was found in the current audit"),
    "sh366003_fg": ("ULEFONE_ONLY", "SH366003 fuel-gauge module has no exact Nothing/public kernel source hit in the current audit"),
    "sc851x_charger": ("ULEFONE_ONLY", "SC851x charger module has no exact Nothing/public kernel source hit in the current audit"),
    "custom_ldo": ("ULEFONE_ONLY", "Ulefone custom LDO module has no usable donor source hit"),
    "custom_ldo_wl2868": ("ULEFONE_ONLY", "WL2864/WL2868 custom LDO integration has no usable Nothing/public kernel source hit in the current audit"),
    "tkcore": ("ULEFONE_ONLY", "TrustKernel TKCore is a distinct TEE stack; matching GlobalPlatform TEEC API names in Nothing TEEI do not prove source equivalence"),
    "tkcore_drv": ("ULEFONE_ONLY", "TrustKernel TKCore TZ driver has no exact Nothing source hit"),
    "fingerprint": ("ULEFONE_ONLY", "Stock yft_finger bridge is Ulefone/YFT-specific; generic 'fingerprint' text hits in Nothing are unrelated and Nothing uses a different fingerprint family"),
}


def run(cmd, check=True):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str, cmd))}\n{p.stderr.strip()}")
    return p.stdout


def tool(name, fallback=None):
    p = shutil.which(name) or (shutil.which(fallback) if fallback else None)
    if not p:
        raise RuntimeError(f"required tool missing: {name}")
    return p


def sha256_file(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def modinfo_field(modinfo, ko, field):
    txt = run([modinfo, "-F", field, str(ko)], check=False)
    return ";".join(x.strip() for x in txt.splitlines() if x.strip())


def parse_modversions_text(text):
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].startswith("0x"):
            rows.append((parts[0], parts[1]))
    return rows


def parse_ksymtab_strings(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r"^\s*\[[^]]+\]\s+(\S.*\S|\S)\s*$", line)
        if m:
            rows.append(m.group(1))
    return rows


def module_imports(modprobe, ko):
    return parse_modversions_text(run([modprobe, "--dump-modversions", str(ko)], check=False))


def module_exports(readelf, ko):
    return sorted(set(parse_ksymtab_strings(run([readelf, "-p", "__ksymtab_strings", str(ko)], check=False))))


def parse_module_metadata(root):
    normal = set()
    recovery = set()
    deps = {}
    for filename, target in (("modules.load", normal), ("modules.load.recovery", recovery)):
        p = root / filename
        if p.is_file():
            for line in p.read_text(errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    target.add(Path(line).name)
    dep = root / "modules.dep"
    if dep.is_file():
        for line in dep.read_text(errors="ignore").splitlines():
            if ":" not in line:
                continue
            lhs, rhs = line.split(":", 1)
            deps[Path(lhs.strip()).name] = [Path(x).name for x in rhs.split() if x.strip()]
    return normal, recovery, deps


def stock_roots(research):
    stock = research / "workspace/gq5012bf1/stock"
    return {
        "vendor_boot_platform": stock / "vendor-ramdisks/platform-extracted/lib/modules",
        "vendor_dlkm": stock / "partitions/vendor_dlkm/lib/modules",
        "system_dlkm": stock / "partitions/system_dlkm/lib/modules",
    }


def discover_stock(research, strict=True):
    roots = stock_roots(research)
    rows = []
    metadata = {}
    counts = {}
    for location, root in roots.items():
        if not root.is_dir():
            raise RuntimeError(f"missing module root: {root}")
        normal, recovery, deps = parse_module_metadata(root)
        metadata[location] = (normal, recovery, deps)
        modules = sorted(root.glob("*.ko"))
        counts[location] = len(modules)
        for ko in modules:
            rows.append({"location": location, "root": root, "path": ko, "filename": ko.name, "sha256": sha256_file(ko)})
    if strict:
        for k, v in PARTITION_EXPECTED.items():
            if counts.get(k) != v:
                raise RuntimeError(f"{k}: expected {v}, found {counts.get(k)}")
        if len(rows) != EXPECTED_PLACEMENTS:
            raise RuntimeError(f"placements: expected {EXPECTED_PLACEMENTS}, found {len(rows)}")
        if len({r['sha256'] for r in rows}) != EXPECTED_UNIQUE_SHA:
            raise RuntimeError("unique SHA256 count changed; investigate before continuing")
        if len({r['filename'] for r in rows}) != EXPECTED_UNIQUE_FILENAMES:
            raise RuntimeError("unique filename count changed; investigate before continuing")
    return rows, metadata, counts


def read_text_files(files):
    text = ""
    for p in files:
        try:
            text += "\n" + p.read_text(errors="ignore")
        except OSError:
            pass
    return text


def source_facts(files):
    text = read_text_files(files)
    return {
        "aliases": sorted(set(ALIAS_RE.findall(text))),
        "compatibles": sorted(set(COMPAT_RE.findall(text))),
        "softdeps": sorted(set(SOFTDEP_RE.findall(text))),
        "exports": sorted(set(EXPORT_RE.findall(text))),
    }


def module_source_files(directory, stem, make_text):
    """Return (files, scope).

    TARGET_FILES means facts came only from files directly attributable to the
    module target (target stem and/or composite object members).
    DIRECTORY_FALLBACK means no target-specific source files were resolved, so
    facts were collected from the whole directory and are not strong enough to
    prove a direct source match.
    """
    names = {stem}
    for line in make_text.splitlines():
        m = COMPOSITE_RE.match(line)
        if m and m.group(1) == stem:
            for tok in m.group(2).split():
                if tok.endswith(".o"):
                    names.add(Path(tok[:-2]).name)
    files = []
    for name in names:
        for suffix in (".c", ".h"):
            p = directory / f"{name}{suffix}"
            if p.is_file():
                files.append(p)
    if files:
        return sorted(set(files)), "TARGET_FILES"

    files = [
        p for p in directory.iterdir()
        if p.is_file() and p.suffix in {".c", ".h", ".dts", ".dtsi"}
    ]
    return sorted(files), "DIRECTORY_FALLBACK"


def subsystem_from_dir(relative_dir):
    parts = Path(relative_dir).parts
    if "drivers" in parts:
        i = parts.index("drivers")
        return "/".join(parts[i:i+3])
    if "net" in parts:
        i = parts.index("net")
        return "/".join(parts[i:i+2])
    return "/".join(parts[:3])


def index_nothing(nothing):
    records = {}
    roots = [("kernel", nothing / "kernel"), ("device_modules", nothing / "device_modules"), ("kernel_modules", nothing / "kernel_modules")]
    for root_name, root in roots:
        if not root.is_dir():
            raise RuntimeError(f"Nothing source root missing: {root}")
        makefiles = list(root.rglob("Makefile")) + list(root.rglob("Kbuild"))
        for mf in makefiles:
            directory = mf.parent
            rel = directory.relative_to(root).as_posix()
            try:
                text = mf.read_text(errors="ignore")
            except OSError:
                continue
            targets = defaultdict(set)
            for line in text.splitlines():
                m = MAKE_OBJ_RE.match(line)
                cfg = ""
                body = ""
                if m:
                    cfg, body = m.group(1), m.group(2)
                if not body:
                    continue
                for tok in body.split():
                    if not tok.endswith(".o"):
                        continue
                    stem = tok[:-2]
                    if "/" in stem or stem.endswith("-objs") or stem.endswith("-y"):
                        continue
                    if cfg:
                        targets[stem].add(cfg)
                    else:
                        targets.setdefault(stem, set())
            for stem, configs in targets.items():
                files, source_scope = module_source_files(directory, stem, text)
                facts = source_facts(files)
                key = (root_name, rel, stem)
                records[key] = {
                    "source_root": root_name,
                    "source_dir": rel,
                    "module_name": stem,
                    "kconfig_symbols": sorted(configs),
                    "makefile_target": f"{stem}.o",
                    "compatibles": facts["compatibles"],
                    "aliases": facts["aliases"],
                    "softdeps": facts["softdeps"],
                    "exports": facts["exports"],
                    "subsystem": subsystem_from_dir(rel),
                    "evidence": str(mf.relative_to(nothing)),
                    "source_scope": source_scope,
                    "source_files": [str(p.relative_to(root)) for p in files],
                }
        # Kleaf/Bazel explicit .ko output lists catch targets not obvious in Makefiles.
        for bzl in list(root.rglob("*.bzl")) + list(root.rglob("BUILD.bazel")):
            try:
                txt = bzl.read_text(errors="ignore")
            except OSError:
                continue
            for ko_path in BZL_KO_RE.findall(txt):
                p = Path(ko_path)
                stem = p.stem
                rel = p.parent.as_posix()
                key = (root_name, rel, stem)
                if key not in records:
                    directory = root / p.parent
                    files = []
                    source_scope = "DIRECTORY_FALLBACK"
                    if directory.is_dir():
                        files, source_scope = module_source_files(directory, stem, "")
                    facts = source_facts(files)
                    records[key] = {
                        "source_root": root_name,
                        "source_dir": rel,
                        "module_name": stem,
                        "kconfig_symbols": [],
                        "makefile_target": p.name,
                        "compatibles": facts["compatibles"],
                        "aliases": facts["aliases"],
                        "softdeps": facts["softdeps"],
                        "exports": facts["exports"],
                        "subsystem": subsystem_from_dir(rel),
                        "evidence": str(bzl.relative_to(nothing)),
                        "source_scope": source_scope,
                        "source_files": [str(q.relative_to(root)) for q in files],
                    }
    return sorted(records.values(), key=lambda r: (r["module_name"], r["source_root"], r["source_dir"]))


def normalize_module_name(name):
    return name.removesuffix(".ko").replace("-", "_")


def compatible_from_alias(alias):
    marker = "of:N*T*C"
    if marker not in alias:
        return None
    x = alias.split(marker, 1)[1]
    if x.endswith("C*"):
        x = x[:-2]
    return x.rstrip("*")


def classify(stock, imports, exports, nothing_by_norm):
    """Conservative source classifier.

    Exact module-name correspondence is necessary but not sufficient for a
    DIRECT_SOURCE_MATCH. Direct requires target-scoped hardware identity
    evidence (matching MODULE_ALIAS or OF compatible). Export overlap is useful
    corroboration, but cannot by itself prove source equivalence because common
    platform APIs are often shared across related implementations.
    """
    norm = normalize_module_name(stock["module_name"] or stock["filename"])
    if norm in MANUAL_CLASS:
        return MANUAL_CLASS[norm]

    candidates = nothing_by_norm.get(norm, [])
    if not candidates:
        return "UNKNOWN", "No exact Nothing module-name match in generated source index"

    stock_aliases = set(filter(None, stock["aliases"].split(";")))
    stock_compats = {
        c for c in (compatible_from_alias(a) for a in stock_aliases) if c
    }
    stock_exports = set(exports)

    direct_reasons = []
    weak_reasons = []

    for c in candidates:
        alias_overlap = stock_aliases & set(c["aliases"])
        compat_overlap = stock_compats & set(c["compatibles"])
        export_overlap = stock_exports & set(c["exports"])
        target_scoped = c.get("source_scope") == "TARGET_FILES"
        label = f"{c['source_root']}:{c['source_dir']}"

        if target_scoped and (alias_overlap or compat_overlap):
            parts = []
            if alias_overlap:
                parts.append("alias=" + ",".join(sorted(alias_overlap)[:4]))
            if compat_overlap:
                parts.append("compatible=" + ",".join(sorted(compat_overlap)[:4]))
            if export_overlap:
                parts.append("exports=" + ",".join(sorted(export_overlap)[:6]))
            direct_reasons.append(
                f"{label} target-scoped ({'; '.join(parts)})"
            )
            continue

        parts = []
        if alias_overlap:
            parts.append("alias=" + ",".join(sorted(alias_overlap)[:4]))
        if compat_overlap:
            parts.append("compatible=" + ",".join(sorted(compat_overlap)[:4]))
        if export_overlap:
            parts.append("exports=" + ",".join(sorted(export_overlap)[:6]))
        if parts:
            scope = c.get("source_scope", "UNKNOWN_SCOPE")
            weak_reasons.append(
                f"{label} {scope} ({'; '.join(parts)})"
            )

    paths = ";".join(
        f"{c['source_root']}:{c['source_dir']}" for c in candidates[:6]
    )

    if direct_reasons:
        return (
            "DIRECT_SOURCE_MATCH",
            "exact module name plus target-scoped hardware corroboration: "
            + " | ".join(direct_reasons[:4]),
        )

    if weak_reasons:
        return (
            "LIKELY_PLATFORM_MATCH",
            "exact module-name target found; corroboration is non-decisive "
            "(export-only and/or directory-scoped): "
            + " | ".join(weak_reasons[:4]),
        )

    return (
        "LIKELY_PLATFORM_MATCH",
        "exact module-name target found in Nothing source index; "
        f"needs target-scoped symbol/DT/KMI confirmation; {paths}",
    )


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def build(args):
    research = args.research.resolve()
    nothing = args.nothing.resolve()
    outdir = research / "kernel"
    modinfo = tool("modinfo")
    modprobe = tool("modprobe")
    readelf = tool("readelf", "llvm-readelf")

    placements, metadata, counts = discover_stock(research, strict=not args.no_strict)
    groups = defaultdict(list)
    for r in placements:
        groups[r["sha256"]].append(r)

    print(f"placements={len(placements)} unique_sha={len(groups)}")
    print("Indexing Nothing source targets...", file=sys.stderr)
    nothing_rows = index_nothing(nothing)
    nothing_by_norm = defaultdict(list)
    for r in nothing_rows:
        nothing_by_norm[normalize_module_name(r["module_name"])].append(r)

    nothing_fields = ["module_name","source_root","source_dir","kconfig_symbols","makefile_target","compatibles","aliases","softdeps","exports","subsystem","evidence","source_scope","source_files"]
    write_csv(
        outdir / "nothing-module-index.csv",
        nothing_fields,
        [{
            **r,
            "kconfig_symbols": ";".join(r["kconfig_symbols"]),
            "compatibles": ";".join(r["compatibles"]),
            "aliases": ";".join(r["aliases"]),
            "softdeps": ";".join(r["softdeps"]),
            "exports": ";".join(r["exports"]),
            "source_files": ";".join(r.get("source_files", [])),
        } for r in nothing_rows],
    )

    master = []
    import_rows = []
    export_rows = []
    binary_exports = {}
    binary_imports = {}

    for idx, (sha, group) in enumerate(sorted(groups.items()), 1):
        rep = group[0]
        ko = rep["path"]
        mi = module_imports(modprobe, ko)
        ex = module_exports(readelf, ko)
        binary_imports[sha] = mi
        binary_exports[sha] = ex
        module_name = modinfo_field(modinfo, ko, "name") or ko.stem
        aliases = modinfo_field(modinfo, ko, "alias")
        locs = sorted({r["location"] for r in group})
        paths = []
        normal_locs = []
        recovery_locs = []
        depnames = set()
        for r in group:
            rel = r["path"].relative_to(r["root"]).as_posix()
            paths.append(f"{r['location']}:{rel}")
            normal, recovery, deps = metadata[r["location"]]
            if r["filename"] in normal:
                normal_locs.append(r["location"])
            if r["filename"] in recovery:
                recovery_locs.append(r["location"])
            depnames.update(deps.get(r["filename"], []))
        stock = {
            "sha256": sha,
            "filename": rep["filename"],
            "module_name": module_name,
            "locations": ";".join(locs),
            "paths": ";".join(sorted(paths)),
            "placement_count": len(group),
            "size_bytes": ko.stat().st_size,
            "vermagic": modinfo_field(modinfo, ko, "vermagic"),
            "srcversion": modinfo_field(modinfo, ko, "srcversion"),
            "depends_modinfo": modinfo_field(modinfo, ko, "depends"),
            "modules_dep_dependencies": ";".join(sorted(depnames)),
            "aliases": aliases,
            "softdeps": modinfo_field(modinfo, ko, "softdep"),
            "license": modinfo_field(modinfo, ko, "license"),
            "description": modinfo_field(modinfo, ko, "description"),
            "import_modversion_count": len(mi),
            "export_count": len(ex),
            "normal_load_locations": ";".join(sorted(set(normal_locs))),
            "recovery_load_locations": ";".join(sorted(set(recovery_locs))),
        }
        cls, evidence = classify(stock, mi, ex, nothing_by_norm)
        stock["classification"] = cls
        stock["classification_evidence"] = evidence
        master.append(stock)
        for crc, sym in mi:
            import_rows.append({"sha256":sha,"module_name":module_name,"filename":rep["filename"],"locations":";".join(locs),"crc":crc,"symbol":sym})
        for sym in ex:
            export_rows.append({"sha256":sha,"module_name":module_name,"filename":rep["filename"],"locations":";".join(locs),"symbol":sym})
        if idx == 1 or idx % 50 == 0 or idx == len(groups):
            print(f"[{idx}/{len(groups)}] {module_name}", file=sys.stderr)

    master_fields = ["sha256","filename","module_name","locations","paths","placement_count","size_bytes","vermagic","srcversion","depends_modinfo","modules_dep_dependencies","aliases","softdeps","license","description","import_modversion_count","export_count","normal_load_locations","recovery_load_locations","classification","classification_evidence"]
    write_csv(outdir / "stock-module-master.csv", master_fields, master)
    # TSVs are grep/join friendly.
    for dest, fields, rows in [
        (outdir / "stock-module-imports.tsv", ["sha256","module_name","filename","locations","crc","symbol"], import_rows),
        (outdir / "stock-module-exports.tsv", ["sha256","module_name","filename","locations","symbol"], export_rows),
    ]:
        with dest.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
            w.writeheader(); w.writerows(rows)

    providers = defaultdict(list)
    for r in export_rows:
        providers[r["symbol"]].append((r["sha256"], r["module_name"], r["locations"]))
    nothing_exporters = defaultdict(set)
    for r in nothing_rows:
        for sym in r["exports"]:
            nothing_exporters[sym].add(f"{r['module_name']}@{r['source_root']}:{r['source_dir']}")
    kmi_rows = []
    for r in import_rows:
        ps = providers.get(r["symbol"], [])
        nps = sorted(nothing_exporters.get(r["symbol"], set()))
        if ps:
            provider_state = "STOCK_MODULE_PROVIDER"
        elif nps:
            provider_state = "NO_STOCK_MODULE_PROVIDER__NOTHING_SOURCE_EXPORT_EXISTS"
        else:
            provider_state = "NO_STOCK_MODULE_PROVIDER"
        kmi_rows.append({
            **r,
            "stock_provider_sha256": ";".join(x[0] for x in ps),
            "stock_provider_modules": ";".join(x[1] for x in ps),
            "stock_provider_locations": ";".join(x[2] for x in ps),
            "nothing_source_exporters": ";".join(nps),
            "provider_state": provider_state,
        })
    kmi_fields = ["sha256","module_name","filename","locations","crc","symbol","stock_provider_sha256","stock_provider_modules","stock_provider_locations","nothing_source_exporters","provider_state"]
    write_csv(outdir / "kmi-symbol-map.csv", kmi_fields, kmi_rows)

    module_map_fields = ["sha256","filename","module_name","locations","classification","classification_evidence"]
    write_csv(outdir / "module-map.csv", module_map_fields, [{k:r[k] for k in module_map_fields} for r in master])

    counts_cls = defaultdict(int)
    for r in master:
        counts_cls[r["classification"]] += 1

    summary = outdir / "phase2-index-summary.md"
    with summary.open("w", encoding="utf-8") as f:
        f.write("# Phase 2 generated index summary\n\n")
        f.write(f"- module placements: {len(placements)}\n")
        f.write(f"- distinct SHA256 module binaries: {len(master)}\n")
        f.write(f"- unique module filenames: {len({r['filename'] for r in placements})}\n")
        f.write(f"- Nothing source module targets indexed: {len(nothing_rows)}\n")
        f.write(f"- versioned import records: {len(import_rows)}\n")
        f.write(f"- exported symbol records: {len(export_rows)}\n\n")
        f.write("## Initial conservative classification\n\n")
        for k in ("DIRECT_SOURCE_MATCH","LIKELY_PLATFORM_MATCH","NEEDS_ULEFONE_PORT","ULEFONE_ONLY","ALTERNATE_BOM","UNKNOWN"):
            f.write(f"- {k}: {counts_cls[k]}\n")
        f.write("\nClassification is a first-pass source-index result. UNKNOWN is intentional where exact evidence is insufficient.\n")

    print(f"Nothing indexed module targets: {len(nothing_rows)}")
    print(f"master binaries: {len(master)} imports: {len(import_rows)} exports: {len(export_rows)}")
    for k in ("DIRECT_SOURCE_MATCH","LIKELY_PLATFORM_MATCH","NEEDS_ULEFONE_PORT","ULEFONE_ONLY","ALTERNATE_BOM","UNKNOWN"):
        print(f"{k}: {counts_cls[k]}")


def self_test():
    assert parse_modversions_text("0x1 foo\n0x2\tbar\n") == [("0x1","foo"),("0x2","bar")]
    x = "String dump of section '__ksymtab_strings':\n  [     0]  alpha\n  [     6]  beta\n"
    assert parse_ksymtab_strings(x) == ["alpha","beta"]
    assert normalize_module_name("mt6375-charger.ko") == "mt6375_charger"
    assert compatible_from_alias("of:N*T*Cmediatek,fooC*") == "mediatek,foo"
    assert MANUAL_CLASS["connfem"][0] == "DIRECT_SOURCE_MATCH"
    assert MANUAL_CLASS["gps_scp"][0] == "DIRECT_SOURCE_MATCH"
    assert MANUAL_CLASS["bt_drv_6878"][0] == "LIKELY_PLATFORM_MATCH"
    assert MANUAL_CLASS["aw883xx_driver"][0] == "NEEDS_ULEFONE_PORT"
    assert MANUAL_CLASS["tkcore"][0] == "ULEFONE_ONLY"

    stock = {
        "module_name": "foo",
        "filename": "foo.ko",
        "aliases": "of:N*T*Cvendor,fooC*",
    }
    export_only = {
        "source_root": "device_modules",
        "source_dir": "drivers/foo",
        "aliases": [],
        "compatibles": [],
        "exports": ["shared_api"],
        "source_scope": "TARGET_FILES",
    }
    cls, _ = classify(stock, [], ["shared_api"], {"foo": [export_only]})
    assert cls == "LIKELY_PLATFORM_MATCH"

    directory_compat = {
        "source_root": "device_modules",
        "source_dir": "drivers/foo",
        "aliases": [],
        "compatibles": ["vendor,foo"],
        "exports": [],
        "source_scope": "DIRECTORY_FALLBACK",
    }
    cls, _ = classify(stock, [], [], {"foo": [directory_compat]})
    assert cls == "LIKELY_PLATFORM_MATCH"

    target_compat = {
        "source_root": "device_modules",
        "source_dir": "drivers/foo",
        "aliases": [],
        "compatibles": ["vendor,foo"],
        "exports": [],
        "source_scope": "TARGET_FILES",
    }
    cls, _ = classify(stock, [], [], {"foo": [target_compat]})
    assert cls == "DIRECT_SOURCE_MATCH"

    print("self-test: PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", type=Path, default=Path(os.environ.get("RESEARCH", ".")))
    ap.add_argument("--nothing", type=Path, default=Path(os.environ.get("NOTHING", ".")))
    ap.add_argument("--no-strict", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    build(args)

if __name__ == "__main__":
    main()
