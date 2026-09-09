#!/usr/bin/env python3
"""Generate the SH366003 stock-oracle ELF inventories without modifying the ELF."""

from __future__ import annotations

import hashlib
import os
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KO = Path(__file__).resolve().with_name("sh366003_fg.stock.ko")
KERNEL = ROOT / "kernel"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            f.write("\t".join(str(x).replace("\t", "\\t").replace("\n", "\\n") for x in row) + "\n")


def elf_sections(blob: bytes) -> tuple[list[dict], dict[str, dict]]:
    if blob[:4] != b"\x7fELF" or blob[4] != 2 or blob[5] != 1:
        raise ValueError("expected ELF64 little-endian input")
    e_shoff = struct.unpack_from("<Q", blob, 0x28)[0]
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", blob, 0x3A)
    raw = [struct.unpack_from("<IIQQQQIIQQ", blob, e_shoff + i * e_shentsize) for i in range(e_shnum)]
    shstr = raw[e_shstrndx]
    names = blob[shstr[4] : shstr[4] + shstr[5]]

    def cstr(data: bytes, off: int) -> str:
        return data[off : data.find(b"\0", off)].decode("utf-8", "replace")

    sections = []
    for i, sh in enumerate(raw):
        sec = {
            "index": i,
            "name": cstr(names, sh[0]) if sh[0] < len(names) else "",
            "type": sh[1],
            "flags": sh[2],
            "address": sh[3],
            "offset": sh[4],
            "size": sh[5],
            "link": sh[6],
            "info": sh[7],
            "align": sh[8],
            "entsize": sh[9],
        }
        sec["data"] = b"" if sh[1] == 8 else blob[sh[4] : sh[4] + sh[5]]
        sections.append(sec)
    return sections, {s["name"]: s for s in sections}


blob = KO.read_bytes()
sections, sec_by_name = elf_sections(blob)
sec_names = {s["index"]: s["name"] for s in sections}

sym_text = run("llvm-readelf", "-s", "-W", str(KO))
symbols: list[dict] = []
for line in sym_text.splitlines():
    m = re.match(r"\s*(\d+):\s+([0-9a-fA-F]+)\s+(\d+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\S+)\s*(.*)", line)
    if not m:
        continue
    num, value, size, typ, bind, vis, ndx, name = m.groups()
    symbols.append(
        {
            "num": int(num),
            "value": int(value, 16),
            "size": int(size),
            "type": typ,
            "bind": bind,
            "vis": vis,
            "ndx": ndx,
            "name": name,
        }
    )

functions = []
for s in symbols:
    if s["type"] != "FUNC":
        continue
    idx = int(s["ndx"])
    sec = sections[idx]
    code = sec["data"][s["value"] : s["value"] + s["size"]]
    kcfi = "UNKNOWN"
    if s["value"] >= 4 and len(sec["data"]) >= s["value"]:
        kcfi = f"0x{struct.unpack_from('<I', sec['data'], s['value'] - 4)[0]:08x}"
    functions.append(
        [
            s["name"],
            sec["name"],
            f"0x{s['value']:x}",
            s["size"],
            s["bind"],
            s["vis"],
            kcfi,
            hashlib.sha256(code).hexdigest(),
        ]
    )
functions.sort(key=lambda r: (sections[[x["name"] for x in sections].index(r[1])]["index"], int(r[2], 16), r[0]))
tsv(
    KERNEL / "phase4-sh366003-functions.tsv",
    ["function", "section", "offset", "size", "binding", "visibility", "kcfi_typeid_word", "sha256"],
    functions,
)

objects = []
for s in symbols:
    if s["type"] != "OBJECT":
        continue
    idx = int(s["ndx"])
    sec = sections[idx]
    raw = sec["data"][s["value"] : s["value"] + s["size"]] if sec["type"] != 8 else b""
    objects.append(
        [
            s["name"],
            sec["name"],
            f"0x{s['value']:x}",
            s["size"],
            s["bind"],
            s["vis"],
            "NOBITS" if sec["type"] == 8 else hashlib.sha256(raw).hexdigest(),
        ]
    )
objects.sort(key=lambda r: (int(next(s["index"] for s in sections if s["name"] == r[1])), int(r[2], 16), r[0]))
tsv(
    KERNEL / "phase4-sh366003-objects.tsv",
    ["object", "section", "offset", "size", "binding", "visibility", "content_sha256_or_nobits"],
    objects,
)

versions = []
version_by_name: dict[str, str] = {}
vsec = sec_by_name["__versions"]["data"]
if len(vsec) % 64:
    raise ValueError("unexpected __versions entry size")
for off in range(0, len(vsec), 64):
    crc = struct.unpack_from("<Q", vsec, off)[0]
    name = vsec[off + 8 : off + 64].split(b"\0", 1)[0].decode("ascii")
    value = f"0x{crc:016x}"
    versions.append([off // 64, name, value])
    version_by_name[name] = value
tsv(KERNEL / "phase4-sh366003-modversions.tsv", ["index", "symbol", "crc"], versions)

intermodule = {"fuelgauge_fw_version", "yft_fuelgauge_device_add", "yft_set_fuelgauge_device_used"}
imports = []
for s in symbols:
    if s["ndx"] == "UND" and s["name"]:
        imports.append(
            [s["name"], "intermodule:yft_devinfo" if s["name"] in intermodule else "kernel", version_by_name.get(s["name"], "MISSING")]
        )
# module_layout is a modversion dependency but has no ordinary undefined relocation symbol.
if "module_layout" in version_by_name:
    imports.append(["module_layout", "kernel:implicit", version_by_name["module_layout"]])
imports.sort(key=lambda r: r[0])
tsv(KERNEL / "phase4-sh366003-imports.tsv", ["symbol", "provider_class", "stock_modversion_crc"], imports)

tsv(KERNEL / "phase4-sh366003-exports.tsv", ["symbol", "namespace", "crc", "notes"], [])

rel_text = run("llvm-readelf", "-r", "-W", str(KO))
rel_rows: list[list[object]] = []
current = ""
for line in rel_text.splitlines():
    m = re.match(r"Relocation section '([^']+)'", line)
    if m:
        current = m.group(1)
        continue
    m = re.match(r"([0-9a-fA-F]{16})\s+([0-9a-fA-F]{16})\s+(R_AARCH64_\S+)\s+([0-9a-fA-F]{16})\s+(.+)", line.strip())
    if not m:
        continue
    offset, info, typ, symvalue, expression = m.groups()
    rel_rows.append([current, f"0x{offset}", info, typ, f"0x{symvalue}", expression])
tsv(
    KERNEL / "phase4-sh366003-relocations.tsv",
    ["relocation_section", "offset", "info", "type", "symbol_value", "symbol_expression"],
    rel_rows,
)

string_rows = []
for line in run("strings", "-a", "-t", "x", str(KO)).splitlines():
    m = re.match(r"\s*([0-9a-fA-F]+)\s(.*)", line)
    if m:
        string_rows.append([f"0x{m.group(1)}", m.group(2)])
tsv(KERNEL / "phase4-sh366003-strings.tsv", ["file_offset", "string"], string_rows)

# Preserve relocation-aware raw evidence next to the frozen oracle.
(KO.parent / "sh366003_fg.stock.disasm.txt").write_text(
    run("llvm-objdump", "-dr", "--section=.text", "--section=.init.text", "--section=.exit.text", str(KO)),
    encoding="utf-8",
)
(KO.parent / "sh366003_fg.stock.sections.txt").write_text(run("llvm-readelf", "-S", "-W", str(KO)), encoding="utf-8")
(KO.parent / "sh366003_fg.stock.symbols.txt").write_text(sym_text, encoding="utf-8")
(KO.parent / "sh366003_fg.stock.relocations.txt").write_text(rel_text, encoding="utf-8")
(KO.parent / "sh366003_fg.stock.strings.txt").write_text(run("strings", "-a", "-t", "x", str(KO)), encoding="utf-8")

print(f"oracle_sha256={hashlib.sha256(blob).hexdigest()}")
print(f"functions={len(functions)} objects={len(objects)} imports={len(imports)} versions={len(versions)} relocations={len(rel_rows)} strings={len(string_rows)}")
print("generated:")
for p in sorted(KERNEL.glob("phase4-sh366003-*.tsv")):
    print(p.relative_to(ROOT))
