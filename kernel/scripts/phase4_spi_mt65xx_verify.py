#!/usr/bin/env python3
"""Fail-closed static verifier for the GQ5012BF1 spi-mt65xx closure."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KERNEL = ROOT / "kernel"
WORK = ROOT / "workspace/phase4-spi-mt65xx"
STOCK_ROOT = ROOT / "workspace/gq5012bf1/stock"
CANONICAL = STOCK_ROOT / "vendor-ramdisks/platform-extracted/lib/modules/spi-mt65xx.ko"
STOCK = WORK / "oracle/spi-mt65xx.stock.ko"
REBUILT = WORK / "build/spi-mt65xx.ko"
SYMVERS = WORK / "build/Module.symvers"
DONOR = Path("/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878/device_modules")
DONOR_REV = "957dac185efe46cbf6336b0fff9516d84c8cd78f"
STOCK_SHA = "5463e06c205623e4b1b713416836e3b5235dc246c7d536595f6613ba3492d712"
STOCK_SIZE = 58144
SOURCE_SHA = "339e05e55161aa35696fa84fc6a0426e0d72b4a45e471f589e94e5cfe2e45669"
HEADER_SHA = "8971388cc7e30c6eaaae662c8eb7aaef67ecf89d7ebd76810f7bbbbba156ea16"
EXPORTS = {
    "mtk_spi_set_autosuspend_delay": ("0xd3e99558", "EXPORT_SYMBOL"),
    "mt_spi_disable_master_clk": ("0xccc1e350", "EXPORT_SYMBOL"),
    "mt_spi_enable_master_clk": ("0x1cc49782", "EXPORT_SYMBOL"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path):
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def row_map(path: Path, key="symbol"):
    return {r[key]: r for r in rows(path)}


def sections(path: Path):
    blob = path.read_bytes()
    shoff, = struct.unpack_from("<Q", blob, 0x28)
    entsize, count, stridx = struct.unpack_from("<HHH", blob, 0x3A)

    def raw(i):
        return struct.unpack_from("<IIQQQQIIQQ", blob, shoff + i * entsize)

    stroff = raw(stridx)[4]
    out = {}
    for i in range(count):
        x = raw(i)
        start = stroff + x[0]
        name = blob[start:blob.index(b"\0", start)].decode()
        out[name] = (x[1], x[4], x[5])
    return blob, out


def versions(path: Path):
    blob, sec = sections(path)
    if "__versions" not in sec:
        return {}
    _, off, size = sec["__versions"]
    out = {}
    for pos in range(off, off + size, 64):
        crc, = struct.unpack_from("<Q", blob, pos)
        name = blob[pos + 8:pos + 64].split(b"\0")[0].decode()
        if name:
            out[name] = f"0x{crc & 0xffffffff:08x}"
    return out


def modinfo(path: Path):
    blob, sec = sections(path)
    _, off, size = sec[".modinfo"]
    out = {}
    for item in blob[off:off + size].split(b"\0"):
        if b"=" in item:
            k, v = item.decode().split("=", 1)
            out.setdefault(k, []).append(v)
    return out


def symvers(path: Path):
    out = {}
    for line in path.read_text().splitlines():
        f = line.split()
        if len(f) >= 4:
            out[f[1]] = (f[0].lower(), f[3])
    return out


def comparable_tsv(a: Path, b: Path, fields, kind="", phase=""):
    def normalise(r):
        r = dict(r)
        # A shorter rebuilt vermagic shifts only .modinfo object offsets.
        if kind == "objects" and r.get("section") == ".modinfo":
            r["offset"] = "BUILD_PROVENANCE"
            if r.get("name", "").startswith("__UNIQUE_ID_vermagic"):
                r["size"] = "BUILD_PROVENANCE"
        # RED used the unchanged include spelling, so four BUG table records
        # address different offsets in the sole __FILE__ string. Final is exact.
        if (kind == "relocations" and phase == "red" and
                r.get("section") == ".rela__bug_table" and
                r.get("symbol") == ".rodata.str"):
            r["addend"] = "SOURCE_PATH_PROVENANCE"
        return tuple(r[f] for f in fields)

    aa_rows, bb_rows = rows(a), rows(b)
    if kind == "strings":
        def functional(rs):
            return [r for r in rs if not (
                r.get("string", "").startswith("vermagic=") or
                r.get("string", "").endswith("/spi-mt65xx.c"))]
        aa_rows, bb_rows = functional(aa_rows), functional(bb_rows)
    aa = sorted(normalise(r) for r in aa_rows)
    bb = sorted(normalise(r) for r in bb_rows)
    return aa == bb


def uncomment(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//.*", "", text)
    return "\n".join(line for line in text.splitlines()
                     if not re.match(r"^\s*#", line))


def result_name(path: Path):
    return path.name


def main() -> int:
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), str(detail)))

    required = [
        CANONICAL, STOCK, REBUILT, SYMVERS,
        WORK / "raw/final-build.log",
        WORK / "acceptance/microarray_fp_tee.ko",
        WORK / "acceptance/build.log",
        WORK / "acceptance/verify.json",
        KERNEL / "phase4-spi-mt65xx-function-parity.tsv",
        KERNEL / "phase4-spi-mt65xx-object-parity.tsv",
    ]
    for p in required:
        check("required:" + result_name(p), p.is_file(), p)
    if not all(p.is_file() for p in required):
        return finish(checks)

    check("stock canonical sha256", sha(CANONICAL) == STOCK_SHA, sha(CANONICAL))
    check("stock oracle sha256", sha(STOCK) == STOCK_SHA, sha(STOCK))
    check("stock canonical size", CANONICAL.stat().st_size == STOCK_SIZE, CANONICAL.stat().st_size)
    check("stock oracle size", STOCK.stat().st_size == STOCK_SIZE, STOCK.stat().st_size)
    copies = sorted(p for p in STOCK_ROOT.rglob("spi-mt65xx.ko") if p.is_file())
    check("one committed stock payload", len(copies) == 1, len(copies))
    check("all stock copies identical", all(sha(p) == STOCK_SHA for p in copies), copies)

    donor_c = DONOR / "drivers/spi/spi-mt65xx.c"
    donor_h = DONOR / "include/linux/platform_data/spi-mt65xx.h"
    rev = subprocess.run(["git", "-C", str(DONOR), "rev-parse", "HEAD"],
                         capture_output=True, text=True)
    check("donor revision", rev.returncode == 0 and rev.stdout.strip() == DONOR_REV,
          rev.stdout.strip())
    check("donor source hash", donor_c.is_file() and sha(donor_c) == SOURCE_SHA,
          sha(donor_c) if donor_c.is_file() else "missing")
    check("donor header hash", donor_h.is_file() and sha(donor_h) == HEADER_SHA,
          sha(donor_h) if donor_h.is_file() else "missing")
    final_c = WORK / "source/spi-mt65xx.c"
    final_h = WORK / "source/spi-mt65xx-platform-data.h"
    check("final vendor header exact", sha(final_h) == HEADER_SHA, sha(final_h))
    expected = donor_c.read_text().replace(
        "#include <linux/platform_data/spi-mt65xx.h>",
        '#include "spi-mt65xx-platform-data.h" /* external-build include-path plumbing */')
    check("source delta is include redirect only", final_c.read_text() == expected)

    stock_files = {
        "functions": KERNEL / "phase4-spi-mt65xx-functions.tsv",
        "imports": KERNEL / "phase4-spi-mt65xx-imports.tsv",
        "modversions": KERNEL / "phase4-spi-mt65xx-modversions.tsv",
        "exports": KERNEL / "phase4-spi-mt65xx-exports.tsv",
        "objects": KERNEL / "phase4-spi-mt65xx-objects.tsv",
        "relocations": KERNEL / "phase4-spi-mt65xx-relocations.tsv",
        "strings": KERNEL / "phase4-spi-mt65xx-strings.tsv",
    }
    compare_fields = {
        "functions": ["name", "section", "offset", "size", "bind", "kcfi_type_id"],
        "imports": ["symbol", "modversion_crc"],
        "modversions": ["symbol", "crc"],
        "exports": ["symbol", "export_class", "crc"],
        "objects": ["name", "section", "offset", "size", "bind"],
        "relocations": ["section", "offset", "type", "symbol", "addend"],
        "strings": ["section", "string"],
    }
    expected_counts = {"functions": 31, "imports": 65, "modversions": 66,
                       "exports": 3, "objects": 60, "relocations": 545,
                       "strings": 120}
    for kind, stock_file in stock_files.items():
        check(f"stock {kind} count", len(rows(stock_file)) == expected_counts[kind],
              len(rows(stock_file)))
        for phase in ("red", "final"):
            candidate = WORK / f"build/{phase}-{kind}.tsv"
            check(f"{phase} {kind} parity",
                  comparable_tsv(stock_file, candidate, compare_fields[kind],
                                 kind, phase))

    fp = rows(KERNEL / "phase4-spi-mt65xx-function-parity.tsv")
    check("function parity count", len(fp) == 31, len(fp))
    check("31/31 function bytes exact", all(r["byte_identity"] == "YES" for r in fp))
    check("31/31 function KCFI exact",
          all(r["stock_kcfi"] == r["rebuilt_kcfi"] for r in fp))
    op = rows(KERNEL / "phase4-spi-mt65xx-object-parity.tsv")
    check("object parity has no unresolved",
          all(r["classification"] != "UNRESOLVED" for r in op))
    check("object residuals provenance-only",
          all(r["classification"] in {"BYTE_IDENTICAL", "BUILD_PROVENANCE_ONLY"} for r in op))

    natural = symvers(SYMVERS)
    check("natural export count", len(natural) == 3, len(natural))
    for name, want in EXPORTS.items():
        check("natural export:" + name, natural.get(name) == want, natural.get(name))
    provider_make = (WORK / "source/Makefile").read_text()
    provider_build = (WORK / "source/BUILD.bazel").read_text()
    provider_c = final_c.read_text()
    active_provider_text = uncomment(provider_make + "\n" + provider_build +
                                     "\n" + provider_c)
    forbidden = re.compile(r"KBUILD_MODPOST_WARN|KBUILD_EXTRA_SYMBOLS|__crc_|__kcrctab|objcopy|llvm-objcopy|patchelf", re.I)
    check("no provider witness symvers", "symvers" not in active_provider_text.lower())
    check("no CRC injection or ELF patching", not forbidden.search(active_provider_text))

    # Independently recover every stock consumer edge from every committed .ko.
    export_names = set(EXPORTS)
    consumers = {}
    scanned = 0
    for p in STOCK_ROOT.rglob("*.ko"):
        if not p.is_file():
            continue
        scanned += 1
        try:
            vv = versions(p)
        except Exception:
            continue
        hits = {s: vv[s] for s in export_names & set(vv)}
        if hits:
            consumers[p.name] = hits
    expected_consumers = {"microarray_fp_tee.ko": {
        "mt_spi_enable_master_clk": "0x1cc49782",
        "mt_spi_disable_master_clk": "0xccc1e350",
    }}
    check("stock module population scanned", scanned == 471, scanned)
    check("complete stock consumer set", consumers == expected_consumers, consumers)

    acceptance = json.loads((WORK / "acceptance/verify.json").read_text())
    check("MicroArray verifier pass", acceptance.get("result", "").startswith("PASS"),
          acceptance.get("result"))
    check("MicroArray verifier no failures", acceptance.get("failures") == [],
          acceptance.get("failures"))
    ac = acceptance.get("checks", {})
    check("MicroArray 66 MODVERSION edges", ac.get("modversion_total") == 66,
          ac.get("modversion_total"))
    check("MicroArray 65 natural ABI edges", ac.get("modversion_natural") == 65,
          ac.get("modversion_natural"))
    check("MicroArray two natural SPI edges", ac.get("modversion_natural_provider") == 2,
          ac.get("modversion_natural_provider"))
    check("MicroArray one tkcore witness", ac.get("modversion_stock_provider_witness") == 1,
          ac.get("modversion_stock_provider_witness"))
    check("MicroArray function set exact", ac.get("functions", {}).get("ok") is True)
    check("MicroArray depends exact", ac.get("depends", {}).get("ok") is True)
    for name in ("mt_spi_enable_master_clk", "mt_spi_disable_master_clk"):
        edge = acceptance.get("edges", {}).get(name, {})
        check("MicroArray natural edge:" + name,
              edge.get("class") == "NATURAL_PROVIDER" and
              edge.get("crc") == EXPORTS[name][0], edge)

    sm, rm = modinfo(STOCK), modinfo(REBUILT)
    for key in ("name", "description", "author", "license", "depends", "alias"):
        check("module metadata:" + key, sm.get(key) == rm.get(key),
              f"stock={sm.get(key)} rebuilt={rm.get(key)}")
    sv = sm.get("vermagic", [""])[0]
    rv = rm.get("vermagic", [""])[0]
    base = "6.1.115-android14-11"
    check("vermagic base and flags",
          sv.startswith(base) and rv.startswith(base) and
          sv.split(" ", 1)[1] == rv.split(" ", 1)[1], f"{sv} / {rv}")

    log = (WORK / "raw/final-build.log").read_text(errors="replace")
    check("exact-GKI build target", "//lieppos/spi-mt65xx:spi_mt65xx" in log)
    check("BUILD_RC zero", "Build completed successfully" in log)
    check("compiler warnings zero", not re.search(r"(^|[^A-Za-z])warning:", log, re.M | re.I))
    check("modpost warnings zero", not re.search(r"modpost.*warning|WARNING: modpost", log, re.I))
    check("unresolved symbols zero", not re.search(
        r"undefined!|undefined symbol|undefined reference|unresolved symbol", log, re.I))
    check("no KBUILD_MODPOST_WARN", "KBUILD_MODPOST_WARN" not in active_provider_text)

    acceptance_log = (WORK / "acceptance/build.log").read_text(errors="replace")
    check("MicroArray build successful", "Build completed successfully" in acceptance_log)
    check("MicroArray compiler warnings zero",
          not re.search(r"(^|[^A-Za-z])warning:", acceptance_log, re.M | re.I))
    check("MicroArray modpost warnings zero",
          not re.search(r"modpost.*warning|WARNING: modpost", acceptance_log, re.I))
    check("MicroArray unresolved symbols zero", not re.search(
        r"undefined!|undefined symbol|undefined reference|unresolved symbol", acceptance_log, re.I))

    return finish(checks)


def finish(checks) -> int:
    passed = sum(ok for _, ok, _ in checks)
    for name, ok, detail in checks:
        print(("PASS" if ok else "FAIL") + "\t" + name +
              (("\t" + detail) if detail else ""))
    print(f"{passed}/{len(checks)} CHECKS PASSED")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
