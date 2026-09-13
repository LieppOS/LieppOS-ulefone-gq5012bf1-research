#!/usr/bin/env python3
"""Fail-closed verifier for both providers and witness-free gz_tz_system acceptance."""
from __future__ import annotations

import re
from pathlib import Path

from phase4_gz_transport_verify_common import (
    Checks,
    GKI,
    ROOT,
    export_crcs,
    filtered_metadata,
    funcs,
    modinfo,
    modversions,
    rows,
    semantic_relocations,
    strings_of,
    undef,
    verify_build_log,
    verify_module,
)


def main() -> int:
    checks = Checks(prefix="stack: ")
    checks.merge(verify_module("gz_trusty_mod"))
    checks.merge(verify_module("gz_ipc_mod"))

    stock = ROOT / "workspace/phase4-gz-tz-system/oracle/gz_tz_system.stock.ko"
    accepted = ROOT / "workspace/phase4-gz-transport/build/gz_tz_system.acceptance.ko"
    checks.check(stock.is_file(), "frozen gz_tz_system oracle exists")
    checks.check(accepted.is_file(), "acceptance module exists")
    if stock.is_file() and accepted.is_file():
        sf, af = funcs(str(stock)), funcs(str(accepted))
        checks.check(len(sf) == 61 and len(af) == 61, "gz_tz_system function counts 61/61")
        checks.check(set(sf) == set(af), "gz_tz_system function set exact")
        for symbol in sorted(sf):
            checks.check(sf[symbol]["size"] == af[symbol]["size"], f"gz_tz_system size exact: {symbol}")
            checks.check(sf[symbol]["body"] == af[symbol]["body"], f"gz_tz_system bytes exact: {symbol}")
            checks.check(sf[symbol]["kcfi"] == af[symbol]["kcfi"], f"gz_tz_system KCFI exact: {symbol}")
        checks.check(len(undef(str(stock))) == 50 and undef(str(stock)) == undef(str(accepted)), "gz_tz_system imports 50/50 exact")
        checks.check(len(modversions(str(stock))) == 51 and modversions(str(stock)) == modversions(str(accepted)), "gz_tz_system MODVERSIONs 51/51 exact")
        checks.check(len(export_crcs(str(stock))) == 27 and export_crcs(str(stock)) == export_crcs(str(accepted)), "gz_tz_system exports 27/27 natural")
        checks.check(len(semantic_relocations(stock)) == 1082, "gz_tz_system stock relocations 1082")
        checks.check(semantic_relocations(stock) == semantic_relocations(accepted), "gz_tz_system relocations 1082/1082 exact")
        checks.check(strings_of(str(stock)) == strings_of(str(accepted)), "gz_tz_system string set exact")
        checks.check(len(rows(ROOT / "kernel/phase4-gz-tz-system-strings.tsv")) == 106, "gz_tz_system string inventory 106")
        checks.check(filtered_metadata(modinfo(stock)) == filtered_metadata(modinfo(accepted)), "gz_tz_system metadata parity excluding vermagic")

    acceptance_rows = rows(ROOT / "kernel/phase4-gz-transport-gz-tz-system-acceptance.tsv")
    checks.check(len(acceptance_rows) == 7, "seven gz_tz_system provider edges")
    checks.check(sum(r["provider"] == "gz_ipc_mod" for r in acceptance_rows) == 5, "five IPC edges")
    checks.check(sum(r["provider"] == "gz_trusty_mod" for r in acceptance_rows) == 2, "two Trusty edges")
    checks.check(all(r["status"] == "NATURAL_OK" for r in acceptance_rows), "all seven edges NATURAL_OK")
    checks.check(all(r["consumer_required_crc"] == r["source_built_crc"] for r in acceptance_rows), "all seven edge CRCs exact")

    provider_files = {
        "gz_trusty_mod": ROOT / "workspace/phase4-gz-transport/build/gz_trusty_mod.rebuilt.ko",
        "gz_ipc_mod": ROOT / "workspace/phase4-gz-transport/build/gz_ipc_mod.rebuilt.ko",
    }
    accepted_versions = modversions(str(accepted)) if accepted.is_file() else {}
    for row in acceptance_rows:
        provider = provider_files[row["provider"]]
        natural = export_crcs(str(provider)).get(row["symbol"]) if provider.is_file() else None
        checks.check(natural == row["source_built_crc"], f"provider emits natural edge: {row['symbol']}")
        checks.check(accepted_versions.get(row["symbol"]) == natural, f"acceptance consumes natural edge: {row['symbol']}")

    package = GKI / "lieppos/gz-tz-system-accept"
    checks.check(package.is_dir(), "acceptance source package exists")
    checks.check(not list(package.rglob("stock-provider*")) if package.is_dir() else False, "all stock-provider witness files deleted")
    make = (package / "Makefile").read_text(errors="replace") if (package / "Makefile").is_file() else ""
    build = (package / "BUILD.bazel").read_text(errors="replace") if (package / "BUILD.bazel").is_file() else ""
    checks.check("stock-provider.symvers" not in make + build, "stock witness symvers not referenced")
    checks.check("stock-provider.provenance.json" not in make + build, "stock witness provenance not referenced")
    checks.check("kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty/Module.symvers" in make, "real transport Module.symvers selected")
    checks.check("//kernel_device_modules-6.1/drivers/misc/mediatek/geniezone/gz-trusty:gz_transport" in build, "real transport Kleaf dependency")
    checks.check(not re.search(r"^\s*(?:export\s+)?KBUILD_MODPOST_WARN\s*[:?+]?=", make + "\n" + build, re.M), "no KBUILD_MODPOST_WARN assignment")

    consumers = rows(ROOT / "kernel/phase4-gz-transport-consumer-acceptance.tsv")
    checks.check(len(consumers) == 40, "all-consumer edge count 40")
    checks.check(all(r["status"] == "NATURAL_OK" for r in consumers), "40/40 consumer edges NATURAL_OK")
    checks.check(all(r["consumer_required_crc"] == r["source_built_crc"] for r in consumers), "zero broken consumer CRCs")

    report = (ROOT / "kernel/phase4-gz-transport-gz-tz-system-acceptance.md").read_text(errors="replace")
    checks.check("43 GKI_NATURAL + 5 GZ_IPC_NATURAL       + 2 GZ_TRUSTY_NATURAL" in report, "provider provenance transition recorded")
    verify_build_log(checks, "gz-tz-system-acceptance-build.log")
    return checks.finish()


if __name__ == "__main__":
    raise SystemExit(main())
