#!/usr/bin/env python3
"""Extract USB-relevant nodes from a stock Android DT table image.

Read-only input; writes a small, reviewable text report rather than a full DTS.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import struct
import subprocess
import tempfile

DT_TABLE_MAGIC = 0xD7B7AB1E
FDT_MAGIC = 0xD00DFEED

SELECTED_PATHS = {
    "/yft_tiny2c_usb",
    "/soc/i2c@11280000/mt6375@34/chg/otg",
    "/soc/i2c@11280000/mt6375@34/tcpc",
    "/soc/i2c@11e03000/fm78100@0x3c",
    "/soc/usb-offload",
    "/soc/usb0@11201000",
    "/soc/usb-phy0@11f40000",
    "/soc/typec-mux-switch",
    "/extcon-usb",
    "/usb-phy",
}

NODE_RE = re.compile(r"^\s*([A-Za-z0-9,._+@#-]+|/)\s*\{\s*$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def first_fdt(image: bytes) -> tuple[bytes, str]:
    if len(image) < 8:
        raise ValueError("input too short")
    magic = struct.unpack_from(">I", image, 0)[0]
    if magic == FDT_MAGIC:
        total = struct.unpack_from(">I", image, 4)[0]
        return image[:total], "raw-fdt(offset=0)"
    if magic != DT_TABLE_MAGIC or len(image) < 64:
        raise ValueError(f"unsupported input magic 0x{magic:08x}")

    (_magic, total_size, header_size, entry_size, entry_count,
     entries_offset, page_size, version) = struct.unpack_from(">8I", image, 0)
    if entry_count < 1 or entry_size < 8:
        raise ValueError("Android DT table contains no usable entries")
    dt_size, dt_offset = struct.unpack_from(">2I", image, entries_offset)
    payload = image[dt_offset:dt_offset + dt_size]
    if len(payload) != dt_size or struct.unpack_from(">I", payload, 0)[0] != FDT_MAGIC:
        raise ValueError("first Android DT table entry is not a complete FDT")
    provenance = (
        f"android-dt-table(total_size={total_size},header_size={header_size},"
        f"entry_size={entry_size},entry_count={entry_count},entries_offset={entries_offset},"
        f"page_size={page_size},version={version},first_dt_offset={dt_offset},"
        f"first_dt_size={dt_size})"
    )
    return payload, provenance


def node_blocks(dts: str) -> dict[str, list[str]]:
    lines = dts.splitlines()
    stack: list[tuple[str, int]] = []
    blocks: dict[str, list[str]] = {}
    for index, line in enumerate(lines):
        match = NODE_RE.match(line)
        if match:
            name = match.group(1)
            stack.append((name, index))
            continue
        if line.strip().startswith("};") and stack:
            name, start = stack.pop()
            names = [entry[0] for entry in stack] + [name]
            path_parts = [part for part in names if part != "/"]
            path = "/" + "/".join(path_parts)
            blocks[path] = lines[start:index + 1]
    return blocks


def usb_node_inventory(dts: str) -> list[tuple[str, str, str, str]]:
    """Return path, compatible, status and maximum-speed for relevant nodes."""
    stack: list[str] = []
    properties: dict[str, dict[str, str]] = {}
    for line in dts.splitlines():
        match = NODE_RE.match(line)
        if match:
            name = match.group(1)
            stack.append(name)
            parts = [part for part in stack if part != "/"]
            properties.setdefault("/" + "/".join(parts), {})
            continue
        if line.strip().startswith("};"):
            if stack:
                stack.pop()
            continue
        if not stack or "=" not in line:
            continue
        key, value = line.strip().split("=", 1)
        parts = [part for part in stack if part != "/"]
        properties["/" + "/".join(parts)][key.strip()] = value.strip().rstrip(";")

    keywords = re.compile(
        r"usb|xhci|mtu3|xsphy|typec|tcpc|extcon|tiny2c|fm78100|mt6375|"
        r"sc8571|sc851|ufcs|pd-manager",
        re.IGNORECASE,
    )
    result = []
    for path, props in properties.items():
        compatible = props.get("compatible", "")
        if not keywords.search(path + " " + compatible):
            continue
        result.append((
            path,
            compatible,
            props.get("status", '"okay/implicit"'),
            props.get("maximum-speed", ""),
        ))
    return sorted(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--overlay", type=pathlib.Path,
                        help="optional raw FDT/Android DT-table overlay to apply")
    args = parser.parse_args()

    image = args.input.read_bytes()
    fdt, container = first_fdt(image)
    base_fdt = fdt
    overlay_image = args.overlay.read_bytes() if args.overlay else None
    overlay_fdt = first_fdt(overlay_image)[0] if overlay_image is not None else None
    with tempfile.TemporaryDirectory(prefix="armol-usb-dt-") as temp_dir:
        dtb = pathlib.Path(temp_dir) / "stock.dtb"
        dts = pathlib.Path(temp_dir) / "stock.dts"
        dtb.write_bytes(fdt)
        if overlay_fdt is not None:
            overlay = pathlib.Path(temp_dir) / "stock.dtbo"
            merged = pathlib.Path(temp_dir) / "stock-merged.dtb"
            overlay.write_bytes(overlay_fdt)
            subprocess.run(
                ["fdtoverlay", "-i", str(dtb), "-o", str(merged), str(overlay)],
                check=True,
            )
            dtb = merged
            fdt = dtb.read_bytes()
        subprocess.run(
            ["dtc", "-q", "-I", "dtb", "-O", "dts", "-o", str(dts), str(dtb)],
            check=True,
        )
        text = dts.read_text(errors="replace")

    blocks = node_blocks(text)
    inventory = usb_node_inventory(text)
    missing = sorted(SELECTED_PATHS - blocks.keys())
    output = [
        "GQ5012BF1 stock USB DT extraction",
        f"source={args.input}",
        f"source_sha256={sha256(image)}",
        f"container={container}",
        f"base_fdt_sha256={sha256(base_fdt)}",
        f"effective_fdt_sha256={sha256(fdt)}",
        *( [f"overlay_source={args.overlay}",
             f"overlay_source_sha256={sha256(overlay_image)}",
             f"overlay_fdt_sha256={sha256(overlay_fdt)}"]
           if overlay_image is not None and overlay_fdt is not None else [] ),
        f"dtc_node_count={len(blocks)}",
        "",
        "===== USB-RELEVANT NODE INVENTORY =====",
        "path\tcompatible\tstatus\tmaximum-speed",
    ]
    output.extend("\t".join(row) for row in inventory)
    output.append("")
    for path in sorted(SELECTED_PATHS):
        output.append(f"===== {path} =====")
        output.extend(blocks.get(path, ["<MISSING>"]))
        output.append("")
    if missing:
        output.append("missing_selected_paths=" + ",".join(missing))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
