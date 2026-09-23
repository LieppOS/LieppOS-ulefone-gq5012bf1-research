#!/usr/bin/env python3
"""Extract a reproducible inventory of stock USB/Type-C/charging modules.

The selection is intentionally broader than the core data path: it includes charger
algorithms, factory/legacy USB functions, offload/boost/logging, TCPC/PD and the
Ulefone thermal glue. It does not claim that every selected module owns USB data.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import subprocess
import sys

NAME_PATTERN = re.compile(
    r"(?:usb|xhci|mtu3|xsphy|typec|tcpc|tcpci|charger|charging|_chg|"
    r"mtk_pep|pd_|adapter_class|sc8571|sc851|sh366|rt6160|tiny2c|"
    r"mux_switch|extcon)",
    re.IGNORECASE,
)
EXTRA_NAMES = {
    "cdc-acm.ko",
    "cdc_ether.ko",
    "cdc_ncm.ko",
    "mtk_u_ether.ko",
}
EXCLUDE_NAMES = {"yft_tpd_gesture.ko"}
STRING_PATTERN = re.compile(
    r"(?:usb|xhci|mtu3|type.?c|tcpc|charger|bc1\.?2|vbus|vconn|otg|"
    r"power.?delivery|\bpd\b|pps|ufcs|adapter|sc8571|sc851|thermal|uvc)",
    re.IGNORECASE,
)


def run(*args: str) -> str:
    completed = subprocess.run(args, check=True, text=True, capture_output=True)
    return completed.stdout


def modinfo(path: pathlib.Path, field: str) -> str:
    result = subprocess.run(
        ["modinfo", "-F", field, str(path)], text=True, capture_output=True
    )
    if result.returncode:
        return ""
    return ";".join(line.strip() for line in result.stdout.splitlines() if line.strip())


def storage_class(relative: pathlib.Path) -> str:
    value = relative.as_posix()
    if "vendor-ramdisks/platform-extracted/" in value:
        return "vendor_ramdisk"
    if "/vendor_dlkm/" in f"/{value}":
        return "vendor_dlkm"
    if "/system_dlkm/" in f"/{value}":
        return "system_dlkm"
    return "other"


def symbols(path: pathlib.Path) -> tuple[list[str], list[str]]:
    text = run("readelf", "-Ws", "--wide", str(path))
    imports: set[str] = set()
    exports: set[str] = set()
    for line in text.splitlines():
        columns = line.split()
        if len(columns) < 8 or not columns[0].rstrip(":").isdigit():
            continue
        ndx, name = columns[6], columns[7].split("@", 1)[0]
        if ndx == "UND" and name:
            imports.add(name)
        if name.startswith("__ksymtab_") and name not in {
            "__ksymtab_gpl",
            "__ksymtab_strings",
        }:
            exports.add(name.removeprefix("__ksymtab_"))
    return sorted(imports), sorted(exports)


def relevant_strings(path: pathlib.Path) -> list[str]:
    text = run("strings", "-a", "-n", "4", str(path))
    keep_exact = {"UFCS", "ufcs_adapter", "pd_adapter", "PD_PPS"}
    result = set()
    for raw in text.splitlines():
        line = raw.strip().replace("\t", " ")
        if not line or not STRING_PATTERN.search(line) or line.startswith("__"):
            continue
        # Full symbols are already preserved in the symbol TSV. Keep human-readable
        # messages/properties/paths plus protocol names that are meaningful alone.
        if (
            line in keep_exact
            or any(character in line for character in (" ", "%", "/", "=", ",", ":"))
        ):
            result.add(line)
    return sorted(result)


def selected_modules(root: pathlib.Path) -> list[pathlib.Path]:
    result = []
    for path in root.rglob("*.ko"):
        if path.name in EXCLUDE_NAMES:
            continue
        if NAME_PATTERN.search(path.name) or path.name in EXTRA_NAMES:
            result.append(path)
    return sorted(result, key=lambda path: (path.name, path.as_posix()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stock_root", type=pathlib.Path)
    parser.add_argument("metadata_output", type=pathlib.Path)
    parser.add_argument("symbols_output", type=pathlib.Path)
    parser.add_argument("strings_output", type=pathlib.Path, nargs="?")
    args = parser.parse_args()

    root = args.stock_root.resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    modules = selected_modules(root)
    metadata_lines = [
        "module\tstock_location\tstorage\tsha256\tname\tvermagic\tdepends\taliases\timports\texports"
    ]
    symbol_lines = ["module\tkind\tsymbol"]
    string_lines = ["module\tstring"]

    for path in modules:
        relative = path.relative_to(root)
        imports, exports = symbols(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        fields = [
            path.name,
            relative.as_posix(),
            storage_class(relative),
            digest,
            modinfo(path, "name"),
            modinfo(path, "vermagic"),
            modinfo(path, "depends"),
            modinfo(path, "alias"),
            str(len(imports)),
            str(len(exports)),
        ]
        metadata_lines.append("\t".join(value.replace("\t", " ") for value in fields))
        symbol_lines.extend(f"{path.name}\tIMPORT\t{name}" for name in imports)
        symbol_lines.extend(f"{path.name}\tEXPORT\t{name}" for name in exports)
        if args.strings_output:
            string_lines.extend(
                f"{path.name}\t{value}" for value in relevant_strings(path)
            )

    args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
    args.symbols_output.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_output.write_text("\n".join(metadata_lines) + "\n")
    args.symbols_output.write_text("\n".join(symbol_lines) + "\n")
    if args.strings_output:
        args.strings_output.parent.mkdir(parents=True, exist_ok=True)
        args.strings_output.write_text("\n".join(string_lines) + "\n")
    suffix = f", {len(string_lines) - 1} filtered strings" if args.strings_output else ""
    print(
        f"wrote {len(modules)} modules, {len(metadata_lines) - 1} metadata rows, "
        f"{len(symbol_lines) - 1} symbol rows{suffix}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
