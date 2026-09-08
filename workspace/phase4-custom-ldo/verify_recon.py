#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re
import struct
import subprocess

E = Path(__file__).resolve().parent
STOCK = E / "stock-custom-ldo.ko"
RECON = E / "recon-custom_ldo.ko"
READELF = "/usr/lib/llvm/23/bin/llvm-readelf"
STRINGS = "strings"
MODINFO = "modinfo"


def output(*args):
    return subprocess.check_output(args, text=True, errors="replace")


def sections(path):
    result = {}
    for line in output(READELF, "-SW", str(path)).splitlines():
        m = re.match(r"\s*\[\s*(\d+)\]\s+(\S*)\s+(\S+)\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)", line)
        if m:
            idx, name, typ, off, size = m.groups()
            result[idx] = {"name": name or "<null>", "type": typ,
                           "offset": int(off, 16), "size": int(size, 16)}
    return result


def symbols(path, secs):
    result = []
    for line in output(READELF, "-sW", str(path)).splitlines():
        m = re.match(r"\s*(\d+):\s+([0-9a-fA-F]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)$", line)
        if m:
            num, value, size, typ, bind, vis, ndx, name = m.groups()
            result.append({"num": int(num), "value": int(value, 16), "size": int(size),
                           "type": typ, "bind": bind, "vis": vis, "ndx": ndx,
                           "section": secs.get(ndx, {}).get("name", ndx), "name": name.strip()})
    return result


def section_bytes(path, secs, name):
    rec = next((x for x in secs.values() if x["name"] == name), None)
    if rec is None or rec["type"] == "NOBITS":
        return None
    return path.read_bytes()[rec["offset"]:rec["offset"] + rec["size"]]


def inventory(path):
    secs = sections(path)
    syms = symbols(path, secs)
    funcs = {s["name"]: s for s in syms if s["type"] == "FUNC" and s["ndx"] != "UND"}
    for s in funcs.values():
        data = section_bytes(path, secs, s["section"])
        s["bytes"] = data[s["value"]:s["value"] + s["size"]]
        s["kcfi"] = struct.unpack_from("<I", data, s["value"] - 4)[0] if s["value"] >= 4 else None
    objects = [s for s in syms if s["ndx"] != "UND" and s["name"] and s["type"] != "FUNC"
               and not s["name"].startswith(("$d.", "$x.")) and s["type"] not in {"FILE", "SECTION"}]
    und = {s["name"] for s in syms if s["ndx"] == "UND" and s["name"]}
    vb = section_bytes(path, secs, "__versions") or b""
    versions = {}
    for off in range(0, len(vb), 64):
        chunk = vb[off:off + 64]
        versions[chunk[8:].split(b"\0", 1)[0].decode()] = struct.unpack_from("<Q", chunk)[0]
    kb = section_bytes(path, secs, "__kcrctab") or b""
    exports = {}
    for s in syms:
        if s["name"].startswith("__crc_") and s["section"] == "__kcrctab":
            exports[s["name"][6:]] = struct.unpack_from("<I", kb, s["value"])[0]
    relocs = []
    relsec = None
    for line in output(READELF, "-rW", str(path)).splitlines():
        m = re.match(r"Relocation section '([^']+)'", line)
        if m:
            relsec = m.group(1)
            continue
        m = re.match(r"([0-9a-fA-F]{16})\s+[0-9a-fA-F]{16}\s+(R_AARCH64_\S+)\s+[0-9a-fA-F]{16}\s+(\S+)\s+\+\s+(\S+)", line)
        if m:
            off, typ, sym, add = m.groups()
            relocs.append((relsec, int(off, 16), typ, sym, add))
    strings = []
    for line in output(STRINGS, "-a", "-t", "x", str(path)).splitlines():
        m = re.match(r"\s*[0-9a-fA-F]+\s+(.*)$", line)
        if m:
            strings.append(m.group(1))
    meta = {}
    for line in output(MODINFO, str(path)).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            if k != "filename":
                meta.setdefault(k.strip(), []).append(v.strip())
    return {"path": path, "bytes": path.read_bytes(), "sections": secs, "symbols": syms,
            "funcs": funcs, "objects": objects, "undefined": und, "versions": versions,
            "exports": exports, "relocs": relocs, "strings": strings, "meta": meta}


s = inventory(STOCK)
r = inventory(RECON)
shared = sorted(set(s["funcs"]) & set(r["funcs"]))
size_same = [n for n in shared if s["funcs"][n]["size"] == r["funcs"][n]["size"]]
byte_same = [n for n in shared if s["funcs"][n]["bytes"] == r["funcs"][n]["bytes"]]
kcfi_same = [n for n in shared if s["funcs"][n]["kcfi"] == r["funcs"][n]["kcfi"]]
stock_imports = set(s["versions"])
recon_imports = set(r["versions"])
stock_secs = {x["name"] for x in s["sections"].values()}
recon_secs = {x["name"] for x in r["sections"].values()}
selected = [".text", "__ksymtab", "__kcrctab", "__ksymtab_strings", ".modinfo", ".comment",
            "__versions", ".note.Linux", ".gnu.linkonce.this_module", ".data", ".rodata", ".bss"]
lines = []
add = lines.append
add(f"stock_sha256={hashlib.sha256(s['bytes']).hexdigest()}")
add(f"recon_sha256={hashlib.sha256(r['bytes']).hexdigest()}")
add(f"stock_size={len(s['bytes'])}")
add(f"recon_size={len(r['bytes'])}")
add(f"whole_module_byte_identical={s['bytes'] == r['bytes']}")
add(f"stock_functions={len(s['funcs'])}")
add(f"recon_functions={len(r['funcs'])}")
add(f"shared_functions={len(shared)} names={','.join(shared)}")
add(f"stock_only_functions={sorted(set(s['funcs']) - set(r['funcs']))}")
add(f"recon_only_functions={sorted(set(r['funcs']) - set(s['funcs']))}")
add(f"size_identical_functions={len(size_same)} names={','.join(size_same)}")
add(f"byte_identical_functions={len(byte_same)} names={','.join(byte_same)}")
add(f"kcfi_parity_functions={len(kcfi_same)} names={','.join(kcfi_same)}")
for n in shared:
    a, b = s["funcs"][n], r["funcs"][n]
    add(f"FUNCTION {n}: stock={a['section']}+0x{a['value']:x}/{a['size']} recon={b['section']}+0x{b['value']:x}/{b['size']} byte_equal={a['bytes']==b['bytes']} stock_kcfi=0x{a['kcfi']:08x} recon_kcfi=0x{b['kcfi']:08x}")
add(f"stock_objects={len(s['objects'])} recon_objects={len(r['objects'])}")
add(f"undefined_elf_parity={s['undefined'] == r['undefined']} stock={sorted(s['undefined'])} recon={sorted(r['undefined'])}")
add(f"import_name_parity={stock_imports == recon_imports} stock={sorted(stock_imports)} recon={sorted(recon_imports)}")
add(f"modversion_parity={s['versions'] == r['versions']}")
for n in sorted(stock_imports | recon_imports):
    add(f"MODVERSION {n}: stock={('0x%08x'%s['versions'][n]) if n in s['versions'] else 'ABSENT'} recon={('0x%08x'%r['versions'][n]) if n in r['versions'] else 'ABSENT'} match={s['versions'].get(n)==r['versions'].get(n)}")
add(f"export_parity={s['exports'] == r['exports']}")
for n in sorted(set(s["exports"]) | set(r["exports"])):
    add(f"EXPORT {n}: stock={('0x%08x'%s['exports'][n]) if n in s['exports'] else 'ABSENT'} recon={('0x%08x'%r['exports'][n]) if n in r['exports'] else 'ABSENT'} match={s['exports'].get(n)==r['exports'].get(n)}")
add(f"relocation_parity={s['relocs'] == r['relocs']} stock_count={len(s['relocs'])} recon_count={len(r['relocs'])}")
if s["relocs"] != r["relocs"]:
    add(f"stock_only_relocations={sorted(set(s['relocs'])-set(r['relocs']))}")
    add(f"recon_only_relocations={sorted(set(r['relocs'])-set(s['relocs']))}")
ss, rs = set(s["strings"]), set(r["strings"])
add(f"string_set_parity={ss == rs} stock_count={len(s['strings'])} recon_count={len(r['strings'])} shared_unique={len(ss&rs)}")
add(f"stock_only_strings={sorted(ss-rs)}")
add(f"recon_only_strings={sorted(rs-ss)}")
for name in selected:
    sb = section_bytes(STOCK, s["sections"], name)
    rb = section_bytes(RECON, r["sections"], name)
    add(f"SECTION {name}: stock={'ABSENT' if sb is None else len(sb)} recon={'ABSENT' if rb is None else len(rb)} byte_equal={sb == rb}")
add(f"section_name_parity={stock_secs == recon_secs}")
add(f"stock_only_sections={sorted(stock_secs-recon_secs)}")
add(f"recon_only_sections={sorted(recon_secs-stock_secs)}")
keys = sorted(set(s["meta"]) | set(r["meta"]))
for k in keys:
    add(f"MODINFO {k}: stock={s['meta'].get(k)} recon={r['meta'].get(k)} match={s['meta'].get(k)==r['meta'].get(k)}")
report = "\n".join(lines) + "\n"
(E / "verify-recon-vs-stock.txt").write_text(report)
print(report)
