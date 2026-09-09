#!/usr/bin/env python3
"""Fail-closed static verifier for the GQ5012BF1 fingerprint.ko reconstruction."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_STOCK_SHA256 = "f5d4dde1f09ac1d67877c66dddf2839de1f496bb2b6b74f50fbe3cd1693b60dc"
EXPECTED_COMPATIBLE = "mediatek,yft_finger"
EXPECTED_EXPORTS = {
    "yft_finger_get_irq_gpio": "0x1a8a2d17",
    "yft_finger_get_irqnum": "0x9cc3cc91",
    "yft_finger_get_reset_gpio": "0x6f79cc60",
    "yft_finger_power_deinit": "0xad1b117e",
    "yft_finger_probe_isok": "0x7476a412",
    "yft_finger_set_irq": "0x6d125ec3",
    "yft_finger_set_power": "0x1fc1d7b1",
    "yft_finger_set_reset": "0xcae83e02",
    "yft_finger_set_spi_mode": "0x0cf6e61a",
    "yft_waite_for_finger_dts_paser": "0x4202702c",
}
EXPECTED_CONSUMER_IMPORTS = {
    "yft_finger_set_irq": "0x6d125ec3",
    "yft_finger_set_reset": "0xcae83e02",
    "yft_finger_set_spi_mode": "0x0cf6e61a",
    "yft_waite_for_finger_dts_paser": "0x4202702c",
}
PINCTRL_STATES = [
    "finger_reset_en1",
    "finger_reset_en0",
    "finger_spi0_mi_as_spi0_mi",
    "finger_spi0_mi_as_gpio",
    "finger_spi0_mo_as_spi0_mo",
    "finger_spi0_mo_as_gpio",
    "finger_spi0_clk_as_spi0_clk",
    "finger_spi0_clk_as_gpio",
    "finger_spi0_cs_as_spi0_cs",
    "finger_spi0_cs_as_gpio",
    "finger_eint_pull_down",
    "finger_eint_pull_up",
    "finger_eint_pull_dis",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def keyed(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["symbol"]: row for row in rows}


def ascii_strings(data: bytes, minimum: int = 4) -> set[str]:
    return {
        match.group().decode("ascii")
        for match in re.finditer(rb"[\x20-\x7e]{%d,}" % minimum, data)
    }


def function_body(source: str, name: str) -> str:
    match = re.search(r"\b" + re.escape(name) + r"\s*\([^;]*?\)\s*\{", source, re.S)
    if not match:
        return ""
    start = match.start()
    pos = match.end() - 1
    depth = 0
    while pos < len(source):
        if source[pos] == "{":
            depth += 1
        elif source[pos] == "}":
            depth -= 1
            if depth == 0:
                return source[start : pos + 1]
        pos += 1
    return ""


def top_level_dts_node(dts: str, name: str) -> str:
    depth = 0
    lines = dts.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if re.fullmatch(re.escape(name) + r"\s*\{", stripped):
            if depth != 1:  # root node is depth 1; this proves /<name>.
                return ""
            node_depth = 0
            selected: list[str] = []
            for nested in lines[index:]:
                selected.append(nested)
                node_depth += nested.count("{") - nested.count("}")
                if node_depth == 0:
                    return "\n".join(selected)
            return ""
        depth += line.count("{") - line.count("}")
    return ""


def run_inventory(module: Path, output: Path, stem: str) -> None:
    script = ROOT / "kernel/scripts/phase4_fingerprint_inventory.py"
    result = subprocess.run(
        [sys.executable, str(script), str(module), str(output), "--stem", stem],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode:
        raise RuntimeError(f"inventory failed for {module}:\n{result.stdout}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stock", type=Path, default=ROOT / "workspace/phase4-fingerprint/oracle/fingerprint.stock.ko")
    parser.add_argument("--recon", type=Path, default=ROOT / "workspace/phase4-fingerprint/fingerprint.recon.ko")
    parser.add_argument("--consumer", type=Path, default=ROOT / "workspace/phase4-fingerprint/oracle/microarray_fp_tee.stock.ko")
    parser.add_argument("--dts", type=Path, default=ROOT / "workspace/phase4-fingerprint/oracle/vendor_boot.entry0.dtb.dts")
    parser.add_argument("--source", type=Path, default=ROOT / "kernel/phase4-fingerprint-recon/fingerprint.c")
    parser.add_argument("--build-log", type=Path, default=ROOT / "workspace/phase4-fingerprint/recon-build-final.log")
    parser.add_argument("--no-build-log", action="store_true")
    args = parser.parse_args()

    results: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        results.append((name, bool(condition), detail))

    required = [args.stock, args.recon, args.consumer, args.dts, args.source]
    if not args.no_build_log:
        required.append(args.build_log)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print("FAIL required evidence files missing: " + ", ".join(missing))
        return 1

    with tempfile.TemporaryDirectory(prefix="phase4-fingerprint-verify-") as temp:
        temp_path = Path(temp)
        try:
            for module, stem in ((args.stock, "stock"), (args.recon, "recon"), (args.consumer, "consumer")):
                run_inventory(module.resolve(), temp_path / stem, stem)
        except Exception as error:
            print(f"FAIL {error}")
            return 1

        def table(stem: str, kind: str) -> list[dict[str, str]]:
            return read_tsv(temp_path / stem / f"{stem}-{kind}.tsv")

        stock_functions = keyed(table("stock", "functions"))
        recon_functions = keyed(table("recon", "functions"))
        stock_imports = keyed(table("stock", "imports"))
        recon_imports = keyed(table("recon", "imports"))
        stock_modversions = keyed(table("stock", "modversions"))
        recon_modversions = keyed(table("recon", "modversions"))
        stock_exports = keyed(table("stock", "exports"))
        recon_exports = keyed(table("recon", "exports"))
        stock_objects = table("stock", "objects")
        recon_objects = table("recon", "objects")
        stock_relocations = table("stock", "relocations")
        recon_relocations = table("recon", "relocations")
        consumer_modversions = keyed(table("consumer", "modversions"))

        check("stock oracle SHA256", sha256(args.stock) == EXPECTED_STOCK_SHA256, sha256(args.stock))
        check("function set", stock_functions.keys() == recon_functions.keys(), f"{len(stock_functions)}/{len(recon_functions)}")
        check("function count", len(stock_functions) == len(recon_functions) == 16, f"{len(stock_functions)}/{len(recon_functions)}")
        byte_equal = sum(
            stock_functions[name]["sha256"] == recon_functions[name]["sha256"]
            for name in stock_functions.keys() & recon_functions.keys()
        )
        size_equal = sum(
            stock_functions[name]["size"] == recon_functions[name]["size"]
            for name in stock_functions.keys() & recon_functions.keys()
        )
        check("function bytes", byte_equal == 16, f"{byte_equal}/16")
        check("function sizes", size_equal == 16, f"{size_equal}/16")
        check(
            "function KCFI",
            all(stock_functions[name]["kcfi_id"] == recon_functions[name]["kcfi_id"] for name in stock_functions),
            "all 16",
        )
        check("kernel import set", stock_imports.keys() == recon_imports.keys() and len(stock_imports) == 18, f"{len(stock_imports)}/{len(recon_imports)}")
        check(
            "kernel import CRCs",
            all(stock_imports[name]["crc"] == recon_imports[name]["crc"] for name in stock_imports),
            "18/18",
        )
        check("MODVERSION set", stock_modversions.keys() == recon_modversions.keys() and len(stock_modversions) == 18, f"{len(stock_modversions)}/{len(recon_modversions)}")
        check(
            "MODVERSION CRCs",
            all(stock_modversions[name]["crc"] == recon_modversions[name]["crc"] for name in stock_modversions),
            "18/18",
        )
        actual_stock_exports = {name: row["crc"] for name, row in stock_exports.items()}
        actual_recon_exports = {name: row["crc"] for name, row in recon_exports.items()}
        check("stock export oracle", actual_stock_exports == EXPECTED_EXPORTS, f"{len(actual_stock_exports)}/10")
        check("reconstructed export set and CRCs", actual_recon_exports == EXPECTED_EXPORTS, f"{len(actual_recon_exports)}/10")
        check(
            "export KCFI",
            all(stock_exports[name]["kcfi_id"] == recon_exports[name]["kcfi_id"] for name in EXPECTED_EXPORTS),
            "10/10",
        )
        check("object count", len(stock_objects) == len(recon_objects) == 38, f"{len(stock_objects)}/{len(recon_objects)}")
        check("relocation count", len(stock_relocations) == len(recon_relocations) == 317, f"{len(stock_relocations)}/{len(recon_relocations)}")

        stock_data = args.stock.read_bytes()
        recon_data = args.recon.read_bytes()
        stock_strings = ascii_strings(stock_data)
        recon_strings = ascii_strings(recon_data)
        check("OF compatible string", EXPECTED_COMPATIBLE in stock_strings and EXPECTED_COMPATIBLE in recon_strings)
        check(
            "DT property strings",
            all(name in stock_strings and name in recon_strings for name in ("int-gpio", "reset-gpio")),
            "int-gpio, reset-gpio",
        )
        check(
            "pinctrl state strings",
            all(name in stock_strings and name in recon_strings for name in PINCTRL_STATES),
            f"{len(PINCTRL_STATES)}/{len(PINCTRL_STATES)}",
        )

        dts = args.dts.read_text(errors="replace")
        node = top_level_dts_node(dts, "yft_finger")
        check("merged DT path", bool(node), "/yft_finger")
        check("merged DT compatible/status", 'compatible = "mediatek,yft_finger";' in node and 'status = "okay";' in node)
        check(
            "merged DT GPIO/IRQ properties",
            all(re.search(r"\b" + re.escape(prop) + r"\s*=", node) for prop in ("int-gpio", "reset-gpio", "interrupt-parent", "interrupts", "debounce")),
        )
        check("merged DT pinctrl names", all(f'"{name}"' in node for name in PINCTRL_STATES), f"{len(PINCTRL_STATES)}/13")

        source = args.source.read_text(errors="strict")
        reset = function_body(source, "yft_finger_set_reset")
        irq = function_body(source, "yft_finger_set_irq")
        spi = function_body(source, "yft_finger_set_spi_mode")
        waiter = function_body(source, "yft_waite_for_finger_dts_paser")
        probe = function_body(source, "yft_finger_plat_probe")
        remove = function_body(source, "yft_finger_plat_remove")
        init = function_body(source, "yft_finger_init")
        exit_body = function_body(source, "yft_finger_exit")

        def ordered(text: str, tokens: list[str]) -> bool:
            positions = [text.find(token) for token in tokens]
            return all(pos >= 0 for pos in positions) and positions == sorted(positions)

        reset_mapping = reset[reset.find("if (value == 0)") :]
        irq_mapping = irq[irq.find("if (value == 0)") :]
        spi_gpio_mapping = spi[spi.find("if (mode == 0)") : spi.find("else if (mode == 1)")]
        spi_peripheral_mapping = spi[spi.find("else if (mode == 1)") :]
        check(
            "reset transitions",
            ordered(reset_mapping, ["value == 0", "yft_finger_reset_low", "value == 1", "yft_finger_reset_high"])
            and "return -1" in reset and "return 0" in reset,
            "0=low, 1=high, other=no-op success",
        )
        check(
            "IRQ semantics",
            ordered(irq_mapping, ["value == 0", "yft_finger_eint_pull_down", "value == 1", "yft_finger_eint_pull_up", "value == 2", "yft_finger_eint_pull_dis"])
            and "enable_irq" not in source and "disable_irq" not in source,
            "0=down, 1=up, 2=disable-pull",
        )
        check(
            "SPI GPIO mapping",
            ordered(spi_gpio_mapping, ["mode == 0", "clk_as_gpio", "cs_as_gpio", "mi_as_gpio", "mo_as_gpio"]),
            "mode 0: CLK,CS,MI,MO GPIO",
        )
        check(
            "SPI peripheral mapping",
            ordered(spi_peripheral_mapping, ["mode == 1", "clk_as_spi0_clk", "cs_as_spi0_cs", "mi_as_spi0_mi", "mo_as_spi0_mo"]),
            "mode 1: CLK,CS,MI,MO SPI0",
        )
        check(
            "DT-ready wait semantics",
            "wait_event_interruptible_timeout" in waiter and "finger_init_waiter" in waiter and "yft_finger_plat" in waiter and re.search(r"3\s*\*\s*HZ", waiter) is not None,
            "interruptible waitqueue, condition=platform pointer, timeout=3*HZ, return discarded",
        )
        check(
            "probe order and return",
            ordered(probe, ["yft_finger_plat = pdev", "yft_finger_get_gpio_info(pdev)", "return 0"]),
            "publish, parse (ignored result), success",
        )
        check("remove lifecycle", "yft_finger_plat = NULL" in remove and "return 0" in remove)
        check("init lifecycle", "platform_driver_register" in init and "return -ENODEV" in init)
        check("exit lifecycle", "platform_driver_unregister" in exit_body)
        check("no PM/shutdown callbacks", not re.search(r"\.(?:pm|shutdown|suspend|resume)\s*=", source))

        consumer_actual = {
            name: consumer_modversions.get(name, {}).get("crc", "MISSING")
            for name in EXPECTED_CONSUMER_IMPORTS
        }
        check("stock MicroArray dependency set", set(name for name in consumer_modversions if name.startswith("yft_")) == set(EXPECTED_CONSUMER_IMPORTS), f"{len(consumer_actual)}/4")
        check("stock MicroArray CRC oracle", consumer_actual == EXPECTED_CONSUMER_IMPORTS, "4/4")
        check(
            "stock MicroArray/reconstructed provider compatibility",
            all(actual_recon_exports.get(name) == crc for name, crc in EXPECTED_CONSUMER_IMPORTS.items()),
            "4/4 exact CRCs",
        )

        if not args.no_build_log:
            build_log = args.build_log.read_text(errors="replace")
            check("exact-GKI BUILD_RC", "Build completed successfully" in build_log and "Build did NOT complete successfully" not in build_log, "0")
            check("compiler warnings", re.search(r"warning:", build_log, re.I) is None, "0")
            check("modpost warnings", re.search(r"(?:WARNING:.*modpost|modpost.*warning)", build_log, re.I) is None, "0")
            check("unresolved symbols", re.search(r"(?:unresolved symbol|undefined symbol|undefined!)", build_log, re.I) is None, "0")

    passed = sum(ok for _, ok, _ in results)
    for name, ok, detail in results:
        suffix = f" ({detail})" if detail else ""
        print(f"{'PASS' if ok else 'FAIL'}: {name}{suffix}")
    print(f"{passed}/{len(results)} CHECKS PASSED")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
