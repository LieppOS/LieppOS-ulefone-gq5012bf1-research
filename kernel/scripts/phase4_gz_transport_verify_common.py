#!/usr/bin/env python3
"""Shared fail-closed checks for the GQ5012BF1 GenieZone transport closure."""
from __future__ import annotations

import csv
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GKI = Path(os.environ.get("GKI_WORKSPACE", "/home/armol/kernel-work/gki-12901745-workspace"))
SRCROOT = GKI / "kernel_device_modules-6.1/drivers/misc/mediatek/geniezone"
REVISION = "957dac185efe46cbf6336b0fff9516d84c8cd78f"

sys.path.insert(0, str(ROOT / "kernel/scripts"))
from phase4_module_parity import export_crcs, funcs, modversions, strings_of, undef  # noqa: E402

SPECS = {
    "gz_trusty_mod": {
        "hyphen": "gz-trusty-mod",
        "sha256": "83e7e3d89b192ea6258db2cb6e5071492caf3badc289e03575661a03341bb5eb",
        "size": 53848,
        "build_id": "c06e791cf6e3de51ce75e986230da4461e0778ec",
        "load_index": 145,
        "depends": "",
        "license": "GPL",
        "description": "",
        "functions": 33,
        "imports": 59,
        "modversions": 60,
        "exports": 14,
        "relocations": 553,
        "string_rows": 63,
        "consumers": 34,
        "sources": ["trusty.c", "smcnr-table.c"],
        "objects": ["gz_trusty_mod-y += trusty.o", "gz_trusty_mod-y += smcnr-table.o"],
        "markers": ["android,trusty-smc-v1", "android,nebula-smc-v1", "trusty_enqueue_nop", "trusty_std_call32"],
    },
    "gz_ipc_mod": {
        "hyphen": "gz-ipc-mod",
        "sha256": "87d8a2a1eb8cb55bbf3bd372fc76e59fecfa8d8479bd931f714252cac60b6a19",
        "size": 78648,
        "build_id": "a430fe26d6e355bf7264af682787afc9a5bda3df",
        "load_index": 146,
        "depends": "gz_trusty_mod",
        "license": "GPL v2",
        "description": "Trusty IPC driver",
        "functions": 43,
        "imports": 81,
        "modversions": 82,
        "exports": 15,
        "relocations": 1003,
        "string_rows": 88,
        "consumers": 6,
        "sources": ["trusty-ipc.c"],
        "objects": ["gz_ipc_mod-y += trusty-ipc.o"],
        "markers": ["TIPC_IOC_CONNECT", "tipc_k_connect", "tipc_k_read", "tipc_compat_ioctl_entry"],
    },
}


class Checks:
    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix
        self.total = 0
        self.passed = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.total += 1
        if condition:
            self.passed += 1
        else:
            self.failures.append(f"{self.prefix}{label}")

    def merge(self, other: "Checks") -> None:
        self.total += other.total
        self.passed += other.passed
        self.failures.extend(other.failures)

    def finish(self) -> int:
        print(f"{self.passed}/{self.total} CHECKS PASSED")
        if self.failures:
            for failure in self.failures:
                print(f"FAIL: {failure}")
            return 1
        return 0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def modinfo(path: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for line in run("modinfo", str(path)).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result.setdefault(key.strip(), []).append(value.strip())
    return result


def build_id(path: Path) -> str:
    match = re.search(r"Build ID: (\S+)", run("readelf", "-nW", str(path)))
    return match.group(1) if match else ""


def semantic_relocations(path: Path) -> list[str]:
    return [
        line.strip()
        for line in run("readelf", "-rW", str(path)).splitlines()
        if re.match(r"^\s*[0-9a-f]+\s+", line)
    ]


def section_names(path: Path) -> list[str]:
    names = []
    for line in run("readelf", "-SW", str(path)).splitlines():
        match = re.match(r"\s*\[\s*\d+\]\s+(\S*)", line)
        if match:
            names.append(match.group(1))
    return names


def section_size(path: Path, name: str) -> int | None:
    for line in run("readelf", "-SW", str(path)).splitlines():
        match = re.match(
            r"\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+\S+\s+\S+\s+([0-9a-fA-F]+)", line
        )
        if match and match.group(1) == name:
            return int(match.group(2), 16)
    return None


def filtered_metadata(info: dict[str, list[str]]) -> dict[str, list[str]]:
    keys = ("name", "depends", "license", "description", "author", "alias", "parm", "import_ns")
    return {key: info.get(key, []) for key in keys}


def verify_source_hashes(c: Checks) -> None:
    table = rows(ROOT / "kernel/phase4-gz-transport-source-hashes.tsv")
    c.check(len(table) == 16, "source hash inventory has 16 files")
    for row in table:
        path = GKI / "kernel_device_modules-6.1" / row["path"]
        c.check(path.is_file(), f"source exists: {row['path']}")
        if path.is_file():
            c.check(path.stat().st_size == int(row["size"]), f"source size: {row['path']}")
            c.check(sha256(path) == row["sha256"], f"source hash: {row['path']}")
        c.check(row["revision"] == REVISION, f"source revision: {row['path']}")


def verify_build_log(c: Checks, name: str) -> None:
    path = ROOT / "workspace/phase4-gz-transport/build/logs" / name
    c.check(path.is_file(), f"build log exists: {name}")
    if not path.is_file():
        return
    text = path.read_text(errors="replace")
    c.check("Build completed successfully" in text, "BUILD_RC=0")
    c.check(not re.search(r"(^|[^a-z])warning:", text, re.I | re.M), "compiler warnings=0")
    c.check(not re.search(r"modpost.*warning|WARNING: modpost", text, re.I), "modpost warnings=0")
    c.check(not re.search(r"undefined!|undefined symbol|unresolved symbol", text, re.I), "unresolved symbols=0")


def verify_no_forbidden_build_mechanism(c: Checks) -> None:
    package = SRCROOT / "gz-trusty"
    paths = [package / "Makefile", package / "BUILD.bazel"]
    text = "\n".join(path.read_text(errors="replace") for path in paths if path.is_file())
    forbidden = {
        "KBUILD_MODPOST_WARN assignment": r"^\s*(?:export\s+)?KBUILD_MODPOST_WARN\s*[:?+]?=",
        "stock provider witness": r"stock-provider\.(?:symvers|json)",
        "KBUILD_EXTRA_SYMBOLS": r"\bKBUILD_EXTRA_SYMBOLS\b",
        "copied __versions": r"\b__versions\b",
        "manual kcrctab": r"\bkcrctab\b",
        "ELF objcopy patch": r"\bobjcopy\b",
    }
    for label, pattern in forbidden.items():
        c.check(not re.search(pattern, text), f"forbidden mechanism absent: {label}")
    c.check(not any(package.glob("*stock*provider*")), "no stock-provider file in final package")


def verify_module(name: str) -> Checks:
    spec = SPECS[name]
    hyphen = spec["hyphen"]
    c = Checks(prefix=f"{name}: ")
    frozen = ROOT / f"workspace/phase4-gz-transport/oracle/{name}.stock.ko"
    canonical = ROOT / f"workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/{name}.ko"
    rebuilt = ROOT / f"workspace/phase4-gz-transport/build/{name}.rebuilt.ko"

    for label, path in (("frozen oracle", frozen), ("canonical stock", canonical), ("rebuilt module", rebuilt)):
        c.check(path.is_file(), f"{label} exists")
    if not (frozen.is_file() and canonical.is_file() and rebuilt.is_file()):
        return c

    c.check(sha256(frozen) == spec["sha256"], "stock SHA256")
    c.check(frozen.stat().st_size == spec["size"], "stock size")
    c.check(sha256(canonical) == spec["sha256"], "canonical stock matches frozen oracle")
    c.check(build_id(frozen) == spec["build_id"], "stock Build ID")

    stock_copies = list((ROOT / "workspace/gq5012bf1/stock").rglob(f"{name}.ko"))
    dashed_copies = list((ROOT / "workspace/gq5012bf1/stock").rglob(f"{hyphen}.ko"))
    c.check(len(stock_copies) == 1, "exactly one committed stock copy")
    c.check(len(dashed_copies) == 0, "no dashed-name duplicate")

    load = (ROOT / "workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/modules.load").read_text().splitlines()
    c.check(load.count(f"{name}.ko") == 1, "one normal modules.load entry")
    c.check(load.index(f"{name}.ko") + 1 == spec["load_index"], "normal load index")
    other_loads = [
        p for p in (ROOT / "workspace/gq5012bf1/stock").rglob("modules.load")
        if "vendor_dlkm" not in str(p)
    ]
    c.check(all(f"{name}.ko" not in p.read_text(errors="ignore") for p in other_loads), "absent from recovery/system load lists")

    si, ri = modinfo(frozen), modinfo(rebuilt)
    c.check(si.get("name", [""])[0] == name, "stock module name")
    c.check(si.get("depends", [""])[0] == spec["depends"], "stock depends")
    c.check(si.get("license", [""])[0] == spec["license"], "stock license")
    c.check(si.get("description", [""])[0] == spec["description"], "stock description")
    c.check(si.get("srcversion", []) == [], "stock srcversion absent")
    c.check(si.get("parm", []) == [], "stock parameters absent")
    c.check(si.get("import_ns", []) == [], "stock import namespace absent")
    c.check(filtered_metadata(si) == filtered_metadata(ri), "module metadata parity excluding vermagic")
    c.check("g945dff7bc1bf" in si.get("vermagic", [""])[0], "stock vermagic fingerprint")
    c.check("maybe-dirty" in ri.get("vermagic", [""])[0], "rebuilt provenance vermagic")
    c.check(rebuilt.stat().st_size == spec["size"] - 8, "whole-ELF residual is exactly 8 bytes")

    sf, rf = funcs(str(frozen)), funcs(str(rebuilt))
    c.check(len(sf) == spec["functions"], "stock function count")
    c.check(len(rf) == spec["functions"], "rebuilt function count")
    c.check(set(sf) == set(rf), "function set exact")
    for symbol in sorted(sf):
        c.check(sf[symbol]["size"] == rf[symbol]["size"], f"function size exact: {symbol}")
        c.check(sf[symbol]["body"] == rf[symbol]["body"], f"function bytes exact: {symbol}")
        c.check(sf[symbol]["kcfi"] == rf[symbol]["kcfi"], f"function KCFI exact: {symbol}")

    su, ru = undef(str(frozen)), undef(str(rebuilt))
    sm, rm = modversions(str(frozen)), modversions(str(rebuilt))
    se, rexp = export_crcs(str(frozen)), export_crcs(str(rebuilt))
    c.check(len(su) == spec["imports"] and su == ru, "import set/count exact")
    c.check(len(sm) == spec["modversions"] and sm == rm, "MODVERSION set/count exact")
    c.check(len(se) == spec["exports"] and set(se) == set(rexp), "export set/count exact")
    for symbol in sorted(se):
        c.check(se[symbol] == rexp[symbol], f"natural export CRC exact: {symbol}")

    sr, rr = semantic_relocations(frozen), semantic_relocations(rebuilt)
    c.check(len(sr) == spec["relocations"], "stock relocation count")
    c.check(sr == rr, "semantic relocation records exact")
    c.check(section_names(frozen) == section_names(rebuilt), "ELF section-name/order parity")
    c.check(strings_of(str(frozen)) == strings_of(str(rebuilt)), "string set exact")
    string_table = ROOT / f"kernel/phase4-{hyphen}-strings.tsv"
    c.check(len(rows(string_table)) == spec["string_rows"], "stock string inventory row count")
    c.check(section_size(frozen, ".llvm_addrsig") == section_size(rebuilt, ".llvm_addrsig") + 8, "LLVM addrsig residual is 8 bytes")

    object_table = rows(ROOT / f"kernel/phase4-{hyphen}-object-parity.tsv")
    c.check(bool(object_table), "object parity table nonempty")
    c.check(all(row["status"] in {"EXACT", "EXACT_NOBITS", "MODINFO_LAYOUT"} for row in object_table), "all objects exact or provenance-only")
    c.check(not any(row["status"] in {"MISSING", "LAYOUT_DIFF", "CONTENT_DIFF"} for row in object_table), "no functional object mismatch")

    acceptance = [
        row for row in rows(ROOT / "kernel/phase4-gz-transport-consumer-acceptance.tsv")
        if row["provider"] == name
    ]
    c.check(len(acceptance) == spec["consumers"], "all stock consumer edges inventoried")
    c.check(all(row["status"] == "NATURAL_OK" for row in acceptance), "all stock consumers accept natural CRCs")
    c.check(all(row["consumer_required_crc"] == row["source_built_crc"] for row in acceptance), "consumer CRC equality")

    source = (SRCROOT / "gz-trusty/trusty.c").read_text(errors="replace") + (SRCROOT / "gz-trusty/trusty-ipc.c").read_text(errors="replace")
    for marker in spec["markers"]:
        c.check(marker in source, f"source marker: {marker}")
    makefile = (SRCROOT / "gz-trusty/Makefile").read_text(errors="replace")
    for marker in spec["objects"]:
        c.check(marker in makefile, f"exact object list: {marker}")
    build = (SRCROOT / "gz-trusty/BUILD.bazel").read_text(errors="replace")
    c.check(REVISION in build, "pinned revision recorded in build target")
    c.check('kernel_build = "//common:kernel_aarch64"' in build, "exact GKI target")

    verify_source_hashes(c)
    verify_no_forbidden_build_mechanism(c)
    verify_build_log(c, "gz-transport-final-build.log")
    return c
