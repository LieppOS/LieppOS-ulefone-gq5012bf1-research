#!/usr/bin/env python3
"""Generate relocation-aware static inventory for stock yft_tiny2c_usb.ko."""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import struct
import subprocess
from pathlib import Path


def run(*args: str) -> str:
    p = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, check=True)
    return p.stdout


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def parse_sections(text: str) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    # llvm-readelf -SW: [ 9] .text PROGBITS addr off size ...
    rx = re.compile(r"\[\s*(\d+)\]\s+(\S+)\s+\S+\s+([0-9a-fA-F]+)\s+"
                    r"([0-9a-fA-F]+)\s+([0-9a-fA-F]+)")
    for line in text.splitlines():
        m = rx.search(line)
        if m:
            idx, name, addr, off, size = m.groups()
            out[idx] = {"name": name, "addr": int(addr, 16),
                        "off": int(off, 16), "size": int(size, 16)}
    return out


def parse_symbols(text: str) -> list[dict[str, object]]:
    out = []
    rx = re.compile(r"\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+)\s+(\w+)\s+"
                    r"(\w+)\s+(\w+)\s+(\S+)\s+(.+)$")
    for line in text.splitlines():
        m = rx.match(line)
        if not m:
            continue
        value, size, typ, bind, vis, ndx, name = m.groups()
        out.append({"value": int(value, 16), "size": int(size), "type": typ,
                    "bind": bind, "vis": vis, "ndx": ndx,
                    "name": name.strip()})
    return out


def extract_section(ko: Path, name: str, temp: Path) -> bytes:
    temp.unlink(missing_ok=True)
    subprocess.run(["llvm-objcopy", "--dump-section", f"{name}={temp}", str(ko)],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return temp.read_bytes()


def function_blocks(disasm: str) -> dict[tuple[str, int], dict[str, object]]:
    blocks: dict[tuple[str, int], dict[str, object]] = {}
    section = ""
    current: dict[str, object] | None = None
    for line in disasm.splitlines():
        sm = re.match(r"Disassembly of section (\S+):", line)
        if sm:
            section = sm.group(1)
            current = None
            continue
        fm = re.match(r"^([0-9a-fA-F]+) <([^>]+)>:", line)
        if fm:
            current = {"section": section, "offset": int(fm.group(1), 16),
                       "name": fm.group(2), "external": [], "internal": []}
            blocks[(section, int(fm.group(1), 16))] = current
            continue
        if current is None:
            continue
        rm = re.search(r"R_AARCH64_CALL26\s+(\S+)", line)
        if rm:
            target = rm.group(1).split("+")[0]
            dest = current["internal"] if not target.startswith(("_", "gpio", "i2c", "kmalloc", "msleep", "of_", "platform_", "device_", "scnprintf", "sscanf")) and target.startswith("tiny2c_") else current["external"]
            dest.append(target)
    return blocks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ko", required=True, type=Path)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--oracle-dir", required=True, type=Path)
    ns = ap.parse_args()
    ko = ns.ko.resolve()
    repo = ns.repo.resolve()
    oracle = ns.oracle_dir.resolve()
    oracle.mkdir(parents=True, exist_ok=True)
    kernel = repo / "kernel"

    outputs = {
        "modinfo.txt": run("modinfo", str(ko)),
        "notes.txt": run("llvm-readelf", "-n", str(ko)),
        "sections.txt": run("llvm-readelf", "-SW", str(ko)),
        "symbols.txt": run("llvm-readelf", "-Ws", str(ko)),
        "relocations.txt": run("llvm-readelf", "-rW", str(ko)),
        "disasm-text.txt": run("llvm-objdump", "-dr", "--section=.text", str(ko)),
        "disasm-init-text.txt": run("llvm-objdump", "-dr", "--section=.init.text", str(ko)),
        "disasm-exit-text.txt": run("llvm-objdump", "-dr", "--section=.exit.text", str(ko)),
        "strings-all.txt": run("strings", "-a", "-t", "x", str(ko)),
    }
    for name, text in outputs.items():
        (oracle / name).write_text(text)
    sha = hashlib.sha256(ko.read_bytes()).hexdigest()
    (oracle / "SHA256SUMS").write_text(f"{sha}  {ko.name}\n")

    sections = parse_sections(outputs["sections.txt"])
    syms = parse_symbols(outputs["symbols.txt"])
    disasm_all = "\n".join((outputs["disasm-text.txt"],
                             outputs["disasm-init-text.txt"],
                             outputs["disasm-exit-text.txt"]))
    blocks = function_blocks(disasm_all)
    sec_bytes: dict[str, bytes] = {}
    for sec in sections.values():
        if sec["size"] and sec["name"] in {".text", ".init.text", ".exit.text"}:
            sec_bytes[sec["name"]] = extract_section(ko, sec["name"], Path("/tmp") / ("yft" + sec["name"].replace(".", "-") + ".bin"))

    funcs = []
    for s in syms:
        if s["type"] != "FUNC" or s["ndx"] == "UND":
            continue
        sec = sections.get(str(s["ndx"]), {"name": f"#{s['ndx']}"})["name"]
        off = int(s["value"])
        raw = sec_bytes.get(sec, b"")
        kcfi = "UNKNOWN"
        if off >= 4 and len(raw) >= off:
            kcfi = f"0x{struct.unpack_from('<I', raw, off - 4)[0]:08x}"
        block = blocks.get((sec, off), {})
        funcs.append([s["name"], sec, f"0x{off:x}", s["size"], s["bind"], kcfi,
                      ",".join(dict.fromkeys(block.get("external", []))) or "-",
                      ",".join(dict.fromkeys(block.get("internal", []))) or "-"])
    funcs.sort(key=lambda r: (r[1], int(r[2], 16)))
    write_tsv(kernel / "phase4-yft-tiny2c-usb-functions.tsv",
              ["name", "section", "offset", "size", "binding", "kcfi_typeid",
               "external_calls", "internal_calls"], funcs)

    objects = []
    for s in syms:
        if s["type"] != "OBJECT" or s["ndx"] == "UND":
            continue
        sec = sections.get(str(s["ndx"]), {"name": f"#{s['ndx']}"})["name"]
        objects.append([s["name"], sec, f"0x{int(s['value']):x}", s["size"],
                        s["bind"], s["vis"]])
    objects.sort(key=lambda r: (r[1], int(r[2], 16), r[0]))
    write_tsv(kernel / "phase4-yft-tiny2c-usb-objects.tsv",
              ["name", "section", "offset", "size", "binding", "visibility"], objects)

    version_raw = extract_section(ko, "__versions", Path("/tmp/yft-versions.bin"))
    versions: dict[str, int] = {}
    version_rows = []
    for off in range(0, len(version_raw), 64):
        crc = struct.unpack_from("<Q", version_raw, off)[0]
        name = version_raw[off + 8: off + 64].split(b"\0")[0].decode()
        versions[name] = crc
        provider = "mt6375-charger" if name == "yft_usb_flag" else ("GKI/module loader" if name == "module_layout" else "GKI")
        version_rows.append([f"0x{crc:08x}", name, provider, f"0x{off:x}"])
    write_tsv(kernel / "phase4-yft-tiny2c-usb-modversions.tsv",
              ["crc", "symbol", "provider", "offset"], version_rows)

    # Map relocation target occurrences to section/offset/function.
    reloc_rows = []
    reloc_section = ""
    rel_rx = re.compile(r"^([0-9a-fA-F]+)\s+\S+\s+(R_AARCH64_\S+)\s+"
                        r"[0-9a-fA-F]+\s+(.+)$")
    ref_sites: dict[str, list[str]] = {}
    func_ranges = []
    for r in funcs:
        func_ranges.append((r[1], int(r[2], 16), int(r[2], 16) + int(r[3]), r[0]))
    for line in outputs["relocations.txt"].splitlines():
        msec = re.match(r"Relocation section '(\.rela[^']+)'", line)
        if msec:
            reloc_section = msec.group(1)
            continue
        m = rel_rx.match(line.strip())
        if not m:
            continue
        off_s, typ, target_expr = m.groups()
        off = int(off_s, 16)
        target = target_expr.split(" + ")[0].split()[0]
        source_sec = reloc_section.removeprefix(".rela")
        owner = next((n for sec, lo, hi, n in func_ranges if sec == source_sec and lo <= off < hi), "")
        reloc_rows.append([reloc_section, f"0x{off:x}", typ, target_expr, owner or "-"])
        ref_sites.setdefault(target, []).append(f"{source_sec}+0x{off:x}" + (f" ({owner})" if owner else ""))
    write_tsv(kernel / "phase4-yft-tiny2c-usb-relocations.tsv",
              ["relocation_section", "offset", "type", "target_addend", "owning_function"], reloc_rows)

    undef = [s for s in syms if s["ndx"] == "UND" and s["name"]]
    import_rows = []
    for s in undef:
        name = str(s["name"])
        cls = "INTERMODULE_OBJECT" if name == "yft_usb_flag" else "KERNEL_IMPORT"
        import_rows.append([name, cls, f"0x{versions[name]:08x}", len(ref_sites.get(name, [])), ";".join(ref_sites.get(name, []))])
    # module_layout is versioned loader ABI but not represented as an undefined ELF symbol.
    import_rows.append(["module_layout", "KERNEL_LOADER_ABI", f"0x{versions['module_layout']:08x}", 0, "__versions only"])
    write_tsv(kernel / "phase4-yft-tiny2c-usb-imports.tsv",
              ["symbol", "class", "crc", "relocation_count", "reference_sites"], import_rows)

    # Every NUL-delimited string in all ELF string-bearing sections; preserve one-byte strings.
    string_rows = []
    for idx, sec in sections.items():
        name = str(sec["name"])
        if not ("str" in name or name in {".modinfo", ".comment", ".rodata.str1.1"}):
            continue
        try:
            raw = extract_section(ko, name, Path("/tmp") / ("yft-string-" + re.sub(r"[^A-Za-z0-9]", "_", name) + ".bin"))
        except subprocess.CalledProcessError:
            continue
        start = 0
        for i, byte in enumerate(raw + b"\0"):
            if byte != 0:
                continue
            blob = raw[start:i]
            if blob and all((32 <= c < 127) or c in (9, 10, 13) for c in blob):
                string_rows.append([name, f"0x{start:x}", len(blob), blob.decode("ascii").replace("\n", "\\n").replace("\t", "\\t")])
            start = i + 1
    write_tsv(kernel / "phase4-yft-tiny2c-usb-strings.tsv",
              ["section", "offset", "length", "string"], string_rows)

    print(f"stock_sha256={sha}")
    print(f"functions={len(funcs)} objects={len(objects)} undefined={len(undef)} versions={len(version_rows)} relocations={len(reloc_rows)} strings={len(string_rows)}")
    print(f"oracle_dir={oracle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
