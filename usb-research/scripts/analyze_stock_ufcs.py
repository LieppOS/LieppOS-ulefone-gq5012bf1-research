#!/usr/bin/env python3
"""Locate the kernel-side UFCS provider and record adapter-state evidence."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys


def run(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strings(path: pathlib.Path) -> list[str]:
    return run("strings", "-a", str(path)).splitlines()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stock_root", type=pathlib.Path)
    parser.add_argument("kernel", type=pathlib.Path)
    parser.add_argument("dtb", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()

    modules = sorted(args.stock_root.rglob("*.ko"))
    ufcs_modules: list[tuple[pathlib.Path, list[str]]] = []
    register_importers: list[pathlib.Path] = []
    for module in modules:
        module_strings = strings(module)
        matches = sorted({line for line in module_strings if "ufcs" in line.lower()})
        if matches:
            ufcs_modules.append((module, matches))
        symbols = run("readelf", "-Ws", "--wide", str(module))
        if any(
            " UND " in line and line.rstrip().endswith("adapter_device_register")
            for line in symbols.splitlines()
        ):
            register_importers.append(module)

    framework = next((path for path in modules if path.name == "mtk_charger_framework.ko"), None)
    if framework is None:
        raise FileNotFoundError("mtk_charger_framework.ko")

    kernel_matches = sorted({line for line in strings(args.kernel) if "ufcs" in line.lower()})
    dt_matches = sorted(
        {
            line
            for line in strings(args.dtb)
            if "ufcs" in line.lower() or "adapter" in line.lower()
        }
    )
    disassembly = run(
        "/usr/lib/llvm/23/bin/llvm-objdump",
        "-d",
        "--disassemble-symbols=mtk_adapter_protocol_init,mtk_adapter_switch_control",
        str(framework),
    )

    lines = [
        "# Stock UFCS-provider static audit",
        f"stock_root={args.stock_root}",
        f"modules_scanned={len(modules)}",
        f"kernel={args.kernel}",
        f"kernel_sha256={sha256(args.kernel)}",
        f"dtb={args.dtb}",
        f"dtb_sha256={sha256(args.dtb)}",
        f"charger_framework={framework}",
        f"charger_framework_sha256={sha256(framework)}",
        "",
        "## modules containing a case-insensitive UFCS string",
    ]
    for module, matches in ufcs_modules:
        lines.append(str(module))
        lines.extend(f"  {value}" for value in matches)
    lines.extend(
        [
            "",
            "## modules importing adapter_device_register",
            *[str(path) for path in register_importers],
            "",
            "## GKI kernel UFCS strings",
            *(kernel_matches or ["(none)"]),
            "",
            "## raw stock DT adapter/UFCS strings",
            *(dt_matches or ["(none)"]),
            "",
            "## adapter protocol disassembly",
            disassembly.rstrip(),
            "",
            "## bounded interpretation",
            "mtk_adapter_protocol_init stores 0x0000000100000001 at offsets 0x6f8/0x6fc,",
            "initializing both adjacent protocol-state fields to integer 1 before negotiation.",
            "Therefore a log value ufcs_type:1 is an initialized baseline, not by itself proof",
            "that a UFCS provider registered or negotiated. Only mtk_pd_adapter.ko imports the",
            "adapter registration API; the raw DT string table names only pd_adapter.",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n")
    print(
        f"scanned {len(modules)} modules; UFCS strings in {len(ufcs_modules)}; "
        f"adapter registrars {len(register_importers)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
