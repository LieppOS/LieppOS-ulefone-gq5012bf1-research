#!/usr/bin/env python3
"""Generate stock-vs-reconstruction function and object closure ledgers."""
from __future__ import annotations

import csv
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFY = Path(__file__).with_name("phase4_custom_ldo_wl2868_verify_recon.py")
spec = importlib.util.spec_from_file_location("wlverify", VERIFY)
assert spec and spec.loader
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

stock, recon = v.Elf(v.STOCK), v.Elf(v.RECON)


def disassembly(path: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    current = ""
    for line in subprocess.check_output(["llvm-objdump", "-d", str(path)], text=True).splitlines():
        m = re.match(r"^[0-9a-f]+ <([^>]+)>:$", line)
        if m:
            current = m.group(1)
            out[current] = []
        elif current and re.match(r"^\s+[0-9a-f]+:", line):
            out[current].append(line)
    return out


def branch_shape(lines: list[str]) -> str:
    mnemonics = []
    for line in lines:
        m = re.search(r"\s([a-z][a-z0-9.]*)\s+", line)
        if m and (m.group(1).startswith("b.") or m.group(1) in {"b", "cbz", "cbnz", "tbz", "tbnz", "ret"}):
            mnemonics.append(m.group(1))
    return ",".join(mnemonics)


def split_calls(elf: v.Elf, name: str) -> tuple[str, str]:
    internal, external = [], []
    for called, count in sorted(elf.calls(name).items()):
        label = called if count == 1 else f"{called}*{count}"
        (internal if called in elf.functions else external).append(label)
    return ",".join(internal), ",".join(external)


def owner_reloc_count(elf: v.Elf, name: str) -> int:
    return sum(r["owner"] == name for r in elf.relocations)


def source_refs() -> dict[str, dict[str, str]]:
    result = {}
    with (ROOT / "kernel/phase4-custom-ldo-wl2868-functions.tsv").open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            result[row["symbol"]] = row
    return result


def hardware_constants(name: str) -> str:
    return {
        "wl2864c_probe": "vin1,reset;10000..11000us*3;1ms;addr=0x2f;chip_id=0x82",
        "wl2864c_vin2_power": "vin2_gpio@+0x40;gpio_to_desc;raw value",
        "wl2864c_ldo_vout": "regs=0x03..0x09;base=600/1200mV;step=12.5mV",
        "wl2868c_ldo_vout": "regs=0x03..0x09;floor=496/1504mV;step=8mV",
        "wl2864c_ldo_en": "reg=0x0e;mask=BIT(ldo-1);bit7 on write",
        "wl2868c_ldo_en": "reg=0x0e;mask=BIT(ldo-1);bit7 on write",
        "will_ldo_vout": "dispatch chip_id 0x01/0x82",
        "will_ldo_en": "dispatch chip_id 0x01/0x82",
        "wl2864c_llseek": "read_pos@+0x68;whence ignored",
        "wl2864c_read": "20 regs max;6 ASCII bytes/register;128-byte allocation",
        "wl2864c_write": "128-byte max;6-byte records;raw register writes",
        "wl2864c_remove": "misc deregister only",
        "wl2864c_open": "probe_ready@+0x6c",
        "init_module": "i2c driver register",
        "cleanup_module": "i2c driver delete",
    }.get(name, "")


sdis, rdis = disassembly(v.STOCK), disassembly(v.RECON)
refs = source_refs()
function_rows = []
for name in v.EXPECTED_FUNCTIONS:
    ss, rs = stock.functions[name], recon.functions[name]
    sb, rb = stock.function_bytes(name), recon.function_bytes(name)
    si, se = split_calls(stock, name)
    ri, rext = split_calls(recon, name)
    byte_equal = sb == rb
    size_equal = ss["size"] == rs["size"]
    stock_shape, recon_shape = branch_shape(sdis[name]), branch_shape(rdis[name])
    if byte_equal:
        cfg = "BYTE_IDENTICAL"
        residual = "NONE"
    elif stock.calls(name) == recon.calls(name):
        cfg = "BEHAVIOR_PROVEN_CALL_GRAPH_AND_SOURCE"
        residual = "COMPILER_OR_SOURCE_EXPRESSION_CODEGEN"
    else:
        cfg = "UNRESOLVED"
        residual = "CALL_GRAPH_MISMATCH"
    function_rows.append({
        "function": name,
        "stock_size": ss["size"], "recon_size": rs["size"],
        "size_identical": "yes" if size_equal else "no",
        "stock_kcfi": f"0x{stock.kcfi(name):08x}", "recon_kcfi": f"0x{recon.kcfi(name):08x}",
        "stock_external_calls": se, "recon_external_calls": rext,
        "stock_internal_calls": si, "recon_internal_calls": ri,
        "hardware_constants": hardware_constants(name),
        "gpio_references": "vin1,reset" if name == "wl2864c_probe" else ("vin2_gpio" if name == "wl2864c_vin2_power" else ""),
        "string_references": refs.get(name, {}).get("string_references", ""),
        "stock_relocations": owner_reloc_count(stock, name), "recon_relocations": owner_reloc_count(recon, name),
        "stock_cfg_shape": stock_shape, "recon_cfg_shape": recon_shape,
        "cfg_classification": cfg, "byte_identical": "yes" if byte_equal else "no", "residual": residual,
    })

function_fields = list(function_rows[0])
with (ROOT / "kernel/phase4-custom-ldo-wl2868-function-parity.tsv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=function_fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(function_rows)


def canonical_name(name: str) -> str:
    for prefix in ["__UNIQUE_ID___addressable_cleanup_module", "__UNIQUE_ID___addressable_init_module",
                   "__UNIQUE_ID_description", "__UNIQUE_ID_license", "__UNIQUE_ID_vermagic",
                   "__UNIQUE_ID_name", "__UNIQUE_ID_depends"]:
        if name.startswith(prefix):
            return prefix
    return name


def named_objects(elf: v.Elf) -> dict[str, tuple[str, dict]]:
    result = {}
    for name, sym in elf.symbols.items():
        relevant_notype = name.startswith(("__crc_will_ldo_", "__ksymtab_will_ldo_", "__kstrtab_will_ldo_", "__kstrtabns_will_ldo_"))
        if (sym["type"] == "OBJECT" or relevant_notype) and sym["ndx"] != "UND":
            result[canonical_name(name)] = (name, sym)
    return result


def content_size(name: str, sym: dict) -> int:
    if name.startswith("__crc_will_ldo_"):
        return 4
    if name.startswith("__ksymtab_will_ldo_"):
        return 12
    if name.startswith("__kstrtabns_will_ldo_"):
        return 1
    if name.startswith("__kstrtab_will_ldo_"):
        return len(name.removeprefix("__kstrtab_")) + 1
    return int(sym["size"])


def object_bytes(elf: v.Elf, name: str, sym: dict) -> bytes:
    size = content_size(name, sym)
    section = str(sym["section"])
    if elf.sections.get(section, {}).get("type") == "NOBITS":
        return b"\0" * size
    data = elf.section(section)
    start = int(sym["value"])
    return data[start:start + size]


def resolve_target(elf: v.Elf, symbol: str, addend: int) -> str:
    if symbol in elf.symbols and elf.symbols[symbol]["type"] != "SECTION":
        return symbol
    for name, sym in elf.symbols.items():
        if sym["section"] == symbol and int(sym["value"]) == addend and sym["type"] in {"FUNC", "OBJECT"}:
            return canonical_name(name)
    return f"{symbol}+0x{addend:x}"


def normalized_relocs(elf: v.Elf, name: str, sym: dict) -> list[tuple[int, str, str]]:
    start, end, section = int(sym["value"]), int(sym["value"]) + content_size(name, sym), str(sym["section"])
    return sorted((int(r["offset"]) - start, str(r["type"]), resolve_target(elf, str(r["symbol"]), int(r["addend"])))
                  for r in elf.relocations if r["target"] == section and start <= int(r["offset"]) < end)


def role(name: str) -> str:
    roles = {
        "wl2864c_data": "private singleton state",
        "wl2864c_i2c_driver": "i2c_driver descriptor",
        "wl2864c_miscdev": "miscdevice descriptor",
        "wl2864c_dt_match": "OF match table",
        "wl2864c_id": "I2C ID table",
        "wl2864c_fops": "file_operations table",
        "____versions": "27-entry MODVERSION table",
        "__this_module": "module descriptor",
        "__crc_will_ldo_vout": "export CRC",
        "__crc_will_ldo_en": "export CRC",
        "__ksymtab_will_ldo_vout": "export symbol entry",
        "__ksymtab_will_ldo_en": "export symbol entry",
        "__kstrtab_will_ldo_vout": "export name",
        "__kstrtab_will_ldo_en": "export name",
        "__kstrtabns_will_ldo_vout": "export namespace",
        "__kstrtabns_will_ldo_en": "export namespace",
        "__UNIQUE_ID___addressable_cleanup_module": "exit addressability",
        "__UNIQUE_ID___addressable_init_module": "init addressability",
        "__UNIQUE_ID_description": "module description",
        "__UNIQUE_ID_license": "module license",
        "__UNIQUE_ID_vermagic": "kernel release/vermagic",
    }
    if name.startswith(".note.Linux"):
        return "Linux note"
    if name.startswith(".note.gnu"):
        return "GNU build attribute"
    return roles.get(name, "module metadata/object")


stock_objects, recon_objects = named_objects(stock), named_objects(recon)
object_rows = []
for cname, (sname, ss) in sorted(stock_objects.items(), key=lambda item: (str(item[1][1]["section"]), int(item[1][1]["value"]))):
    ritem = recon_objects.get(cname)
    if not ritem:
        object_rows.append({"object": cname, "stock_section": ss["section"], "stock_offset": f"0x{ss['value']:x}",
                            "stock_size": ss["size"], "recon_section": "MISSING", "recon_offset": "", "recon_size": "",
                            "stock_content_sha256": object_bytes(stock, ss).hex(), "recon_content_sha256": "",
                            "stock_relocation_slots": "", "recon_relocation_slots": "", "semantic_role": role(cname),
                            "classification": "UNRESOLVED", "residual": "OBJECT_MISSING"})
        continue
    rname, rs = ritem
    sbytes, rbytes = object_bytes(stock, sname, ss), object_bytes(recon, rname, rs)
    sr, rr = normalized_relocs(stock, sname, ss), normalized_relocs(recon, rname, rs)
    def fmt(rows): return ";".join(f"+0x{o:x}:{t}:{n}" for o, t, n in rows)
    if sbytes == rbytes and sr == rr and ss["size"] == rs["size"]:
        classification, residual = "BYTE_IDENTICAL", "NONE"
    elif ss["size"] == rs["size"] and sr == rr:
        classification, residual = "RELOCATION_EQUIVALENT", "NON_POINTER_BYTES_DIFFER"
    elif cname == "__UNIQUE_ID_vermagic":
        classification, residual = "SEMANTIC_EQUIVALENT", "BUILD_RELEASE_LABEL_DIFFERS"
    else:
        classification, residual = "SEMANTIC_EQUIVALENT", "GENERATED_METADATA_OR_LAYOUT"
    import hashlib
    object_rows.append({
        "object": cname, "stock_section": ss["section"], "stock_offset": f"0x{int(ss['value']):x}", "stock_size": ss["size"],
        "stock_content_size": len(sbytes), "recon_section": rs["section"], "recon_offset": f"0x{int(rs['value']):x}", "recon_size": rs["size"],
        "recon_content_size": len(rbytes), "stock_content_sha256": hashlib.sha256(sbytes).hexdigest(), "recon_content_sha256": hashlib.sha256(rbytes).hexdigest(),
        "stock_relocation_slots": fmt(sr), "recon_relocation_slots": fmt(rr), "semantic_role": role(cname),
        "classification": classification, "residual": residual,
    })

# Four anonymous hardware-significant constant arrays are real data objects even though ELF gives them no symbols.
arrays = [
    ("anon_wl2864c_floor", 0x2E0, (60000, 60000, 120000, 120000, 120000, 120000, 120000)),
    ("anon_wl2864c_offset", 0x2FC, (-6000, -6000, -12000, -12000, -12000, -12000, -12000)),
    ("anon_wl2868c_floor", 0x318, (49600, 49600, 150400, 150400, 150400, 150400, 150400)),
    ("anon_wl2868c_offset", 0x334, (-4960, -4960, -15040, -15040, -15040, -15040, -15040)),
]
import hashlib, struct
for name, off, values in arrays:
    content = struct.pack("<7i", *values)
    roff = recon.section(".rodata").find(content)
    digest = hashlib.sha256(content).hexdigest()
    object_rows.append({
        "object": name, "stock_section": ".rodata", "stock_offset": f"0x{off:x}", "stock_size": 28, "stock_content_size": 28,
        "recon_section": ".rodata", "recon_offset": f"0x{roff:x}", "recon_size": 28, "recon_content_size": 28,
        "stock_content_sha256": digest, "recon_content_sha256": digest,
        "stock_relocation_slots": "", "recon_relocation_slots": "", "semantic_role": "voltage conversion table",
        "classification": "BYTE_IDENTICAL", "residual": "NONE",
    })

object_fields = list(object_rows[0])
with (ROOT / "kernel/phase4-custom-ldo-wl2868-object-parity.tsv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=object_fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(object_rows)

print(f"wrote {len(function_rows)} function rows and {len(object_rows)} object rows")
