#!/usr/bin/env python3
from pathlib import Path
import csv
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
E = Path(__file__).resolve().parent
K = ROOT / "kernel"
KO = E / "stock-custom-ldo.ko"
LLVM_OBJCOPY = "/usr/lib/llvm/23/bin/llvm-objcopy"

sections_text = (E / "stock-readelf-sections.txt").read_text()
symbols_text = (E / "stock-readelf-symbols.txt").read_text()
relocs_text = (E / "stock-readelf-relocations.txt").read_text()

sections = {}
for line in sections_text.splitlines():
    m = re.match(r"\s*\[\s*(\d+)\]\s+(\S*)\s+(\S+)\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)", line)
    if m:
        idx, name, typ, off, size = m.groups()
        sections[idx] = {"name": name or "<null>", "type": typ,
                         "file_offset": int(off, 16), "size": int(size, 16)}

symbols = []
for line in symbols_text.splitlines():
    m = re.match(r"\s*(\d+):\s+([0-9a-fA-F]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)$", line)
    if not m:
        continue
    num, value, size, typ, bind, vis, ndx, name = m.groups()
    symbols.append({"num": int(num), "value": int(value, 16), "size": int(size),
                    "type": typ, "bind": bind, "vis": vis, "ndx": ndx,
                    "section": sections.get(ndx, {}).get("name", ndx), "name": name.strip()})

# Dump the exact section bytes used by the inventories.
for sec, fn in [(".text", "stock-text.bin"), (".init.text", "stock-init-text.bin"),
                (".exit.text", "stock-exit-text.bin"), (".rodata.str1.1", "stock-rodata-str1-1.bin"),
                (".rodata", "stock-rodata.bin"), (".data", "stock-data.bin"),
                (".bss", "stock-bss.bin"), ("__versions", "stock-versions.bin"),
                ("__kcrctab", "stock-kcrctab.bin")]:
    out = E / fn
    try:
        subprocess.run([LLVM_OBJCOPY, f"--dump-section", f"{sec}={out}", str(KO)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        # NOBITS sections such as .bss cannot be dumped; preserve an empty marker.
        out.write_bytes(b"")

section_bytes = {}
for sec, fn in [(".text", "stock-text.bin"), (".init.text", "stock-init-text.bin"),
                (".exit.text", "stock-exit-text.bin")]:
    section_bytes[sec] = (E / fn).read_bytes()

mapping = {(s["section"], s["value"], s["name"].split(".")[0])
           for s in symbols if s["name"].startswith(("$d.", "$x."))}

def kcfi_id(s):
    data = section_bytes.get(s["section"])
    if data is None or s["value"] < 4 or s["value"] > len(data):
        return ""
    has_d = any(sec == s["section"] and value == s["value"] - 4 and kind == "$d"
                for sec, value, kind in mapping)
    has_x = any(sec == s["section"] and value == s["value"] and kind == "$x"
                for sec, value, kind in mapping)
    if not (has_d and has_x):
        return ""
    return f"0x{struct.unpack_from('<I', data, s['value'] - 4)[0]:08x}"

funcs = sorted((s for s in symbols if s["type"] == "FUNC" and s["ndx"] != "UND"),
               key=lambda s: (s["section"], s["value"], s["name"]))
export_names = {"custom_ldo_en", "custom_ldo_vout"}
with (K / "phase4-custom-ldo-functions.tsv").open("w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["symbol", "section", "offset_hex", "size", "binding", "visibility", "kcfi_id", "exported"])
    for s in funcs:
        w.writerow([s["name"], s["section"], f"0x{s['value']:x}", s["size"], s["bind"], s["vis"],
                    kcfi_id(s), "yes" if s["name"] in export_names else "no"])

# Include every named, defined data-like symbol, including NOTYPE ksymtab/CRC symbols.
objects = [s for s in symbols if s["ndx"] != "UND" and s["name"] and s["type"] != "FUNC"
           and not s["name"].startswith(("$d.", "$x.")) and s["type"] not in {"FILE", "SECTION"}]
objects.sort(key=lambda s: (s["section"], s["value"], s["name"]))
with (K / "phase4-custom-ldo-objects.tsv").open("w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["symbol", "elf_type", "section", "offset_hex", "size", "binding", "visibility"])
    for s in objects:
        w.writerow([s["name"], s["type"], s["section"], f"0x{s['value']:x}", s["size"], s["bind"], s["vis"]])

# MODVERSIONS imports.
version_bytes = (E / "stock-versions.bin").read_bytes()
versions = []
for off in range(0, len(version_bytes), 64):
    chunk = version_bytes[off:off + 64]
    if len(chunk) != 64:
        raise RuntimeError("partial modversion_info entry")
    crc = struct.unpack_from("<Q", chunk, 0)[0]
    name = chunk[8:].split(b"\0", 1)[0].decode()
    versions.append((name, crc))
version_map = dict(versions)

# Relocations.
relocs = []
relsec = None
for line in relocs_text.splitlines():
    m = re.match(r"Relocation section '([^']+)'", line)
    if m:
        relsec = m.group(1)
        continue
    m = re.match(r"([0-9a-fA-F]{16})\s+([0-9a-fA-F]{16})\s+(R_AARCH64_\S+)\s+([0-9a-fA-F]{16})\s+(\S+)\s+\+\s+(\S+)", line)
    if m:
        off, info, typ, symval, symname, addend = m.groups()
        relocs.append({"relocation_section": relsec, "offset": int(off, 16), "info": info,
                       "type": typ, "symbol_value": int(symval, 16), "symbol": symname,
                       "addend": addend})

funcs_by_sec = {}
for s in funcs:
    funcs_by_sec.setdefault(s["section"], []).append(s)

def owner_for(relsec, off):
    if not relsec or not relsec.startswith(".rela"):
        return ""
    target = relsec[5:]
    if target == "_jump_table":
        target = "__jump_table"
    candidates = funcs_by_sec.get(target, [])
    for s in candidates:
        if s["value"] <= off < s["value"] + s["size"]:
            return s["name"]
    # Data object owner, when uniquely enclosing the relocation.
    candidates = [s for s in objects if s["section"] == target and s["size"] and
                  s["value"] <= off < s["value"] + s["size"]]
    return candidates[0]["name"] if len(candidates) == 1 else ""

with (K / "phase4-custom-ldo-relocations.tsv").open("w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["relocation_section", "offset_hex", "owner", "type", "symbol_value_hex", "symbol", "addend"])
    for r in relocs:
        w.writerow([r["relocation_section"], f"0x{r['offset']:x}", owner_for(r["relocation_section"], r["offset"]),
                    r["type"], f"0x{r['symbol_value']:x}", r["symbol"], r["addend"]])

undefined = sorted((s for s in symbols if s["ndx"] == "UND" and s["name"]), key=lambda s: s["name"])
# module_layout is represented only by its __versions entry, not an ELF UND symbol.
imports = undefined + [{"name": "module_layout", "type": "MODVERSION", "bind": "GLOBAL"}]
imports.sort(key=lambda s: s["name"])
reloc_count = {}
reloc_types = {}
for r in relocs:
    reloc_count[r["symbol"]] = reloc_count.get(r["symbol"], 0) + 1
    reloc_types.setdefault(r["symbol"], set()).add(r["type"])
with (K / "phase4-custom-ldo-imports.tsv").open("w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["symbol", "stock_crc", "elf_type", "binding", "relocation_count", "relocation_types", "provider_class"])
    for s in imports:
        crc = version_map.get(s["name"])
        provider = "custom_ldo_wl2868" if s["name"] in {"will_ldo_en", "will_ldo_vout"} else "kernel/GKI"
        w.writerow([s["name"], f"0x{crc:08x}" if crc is not None else "", s["type"], s["bind"],
                    reloc_count.get(s["name"], 0), ",".join(sorted(reloc_types.get(s["name"], set()))),
                    provider])

with (K / "phase4-custom-ldo-modversions.tsv").open("w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["symbol", "crc", "role"])
    for name, crc in versions:
        w.writerow([name, f"0x{crc:08x}", "module-layout" if name == "module_layout" else "import"])

kcrcs = struct.unpack("<II", (E / "stock-kcrctab.bin").read_bytes())
export_crc = {}
for s in symbols:
    if s["name"].startswith("__crc_") and s["section"] == "__kcrctab":
        export_crc[s["name"][6:]] = kcrcs[s["value"] // 4]
with (K / "phase4-custom-ldo-exports.tsv").open("w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["symbol", "section", "offset_hex", "size", "binding", "kcfi_id", "stock_crc", "namespace", "consumer"])
    for s in funcs:
        if s["name"] in export_names:
            w.writerow([s["name"], s["section"], f"0x{s['value']:x}", s["size"], s["bind"], kcfi_id(s),
                        f"0x{export_crc[s['name']]:08x}", "", "imgsensor"])

# Inventory every printable string reported by GNU strings, mapped back to its
# containing ELF section. This includes module metadata, symbol names, compiler
# provenance, and section names; the module has no functional/logging strings.
strings = []
for line in (E / "stock-strings-offsets.txt").read_text().splitlines():
    m = re.match(r"\s*([0-9a-fA-F]+)\s+(.*)$", line)
    if not m:
        continue
    off = int(m.group(1), 16)
    sec = next((v["name"] for v in sections.values()
                if v["file_offset"] <= off < v["file_offset"] + v["size"]), "<none>")
    strings.append((off, sec, m.group(2)))
with (K / "phase4-custom-ldo-strings.tsv").open("w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["file_offset_hex", "section", "string"])
    for off, sec, text in strings:
        w.writerow([f"0x{off:x}", sec, text])

print(f"functions={len(funcs)} objects={len(objects)} imports={len(imports)} exports={len(export_names)} modversions={len(versions)} relocations={len(relocs)} strings={len(strings)}")
for s in funcs:
    print(f"FUNC {s['name']} {s['section']} 0x{s['value']:x} size={s['size']} kcfi={kcfi_id(s)}")
for name in sorted(export_names):
    print(f"EXPORT {name} crc=0x{export_crc[name]:08x}")
