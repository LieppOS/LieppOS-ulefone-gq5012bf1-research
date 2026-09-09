#!/usr/bin/env python3
"""Generate fail-closed ELF inventories for the GQ5012BF1 fingerprint provider.

The parser is intentionally dependency-free so it can run in the pinned GKI checkout.
It supports the ELF64 little-endian relocatable AArch64 modules used by this project.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path

SHT_NOBITS = 8
SHT_RELA = 4
SHN_UNDEF = 0
STT_NOTYPE = 0
STT_OBJECT = 1
STT_FUNC = 2
STT_SECTION = 3
STT_FILE = 4
TYPE_NAMES = {0: "NOTYPE", 1: "OBJECT", 2: "FUNC", 3: "SECTION", 4: "FILE", 5: "COMMON", 6: "TLS"}
BIND_NAMES = {0: "LOCAL", 1: "GLOBAL", 2: "WEAK"}


@dataclass
class Section:
    index: int
    name: str
    sh_type: int
    flags: int
    offset: int
    size: int
    link: int
    info: int
    entsize: int
    align: int
    data: bytes


@dataclass
class Symbol:
    index: int
    name: str
    value: int
    size: int
    bind: int
    st_type: int
    other: int
    shndx: int


class ELF64LE:
    def __init__(self, path: Path):
        self.path = path
        self.raw = path.read_bytes()
        if self.raw[:4] != b"\x7fELF" or self.raw[4] != 2 or self.raw[5] != 1:
            raise ValueError(f"{path}: expected ELF64 little-endian")
        eh = struct.unpack_from("<16sHHIQQQIHHHHHH", self.raw, 0)
        self.e_type, self.e_machine = eh[1], eh[2]
        self.e_shoff, self.e_shentsize, self.e_shnum, self.e_shstrndx = eh[6], eh[11], eh[12], eh[13]
        if self.e_machine != 183:
            raise ValueError(f"{path}: expected EM_AARCH64, got {self.e_machine}")
        raw_headers = []
        for i in range(self.e_shnum):
            off = self.e_shoff + i * self.e_shentsize
            raw_headers.append(struct.unpack_from("<IIQQQQIIQQ", self.raw, off))
        shstr_hdr = raw_headers[self.e_shstrndx]
        shstr = self.raw[shstr_hdr[4]:shstr_hdr[4] + shstr_hdr[5]]
        self.sections: list[Section] = []
        for i, h in enumerate(raw_headers):
            name = self.cstr(shstr, h[0])
            data = b"" if h[1] == SHT_NOBITS else self.raw[h[4]:h[4] + h[5]]
            self.sections.append(Section(i, name, h[1], h[2], h[4], h[5], h[6], h[7], h[9], h[8], data))
        self.by_name = {s.name: s for s in self.sections}
        self.symbols: list[Symbol] = []
        symtab = self.by_name.get(".symtab")
        if not symtab:
            raise ValueError(f"{path}: no .symtab")
        strtab = self.sections[symtab.link].data
        entsize = symtab.entsize or 24
        for i in range(symtab.size // entsize):
            name, info, other, shndx, value, size = struct.unpack_from("<IBBHQQ", symtab.data, i * entsize)
            self.symbols.append(Symbol(i, self.cstr(strtab, name), value, size, info >> 4, info & 0xF, other, shndx))
        self.sym_by_name = {s.name: s for s in self.symbols if s.name}

    @staticmethod
    def cstr(blob: bytes, off: int) -> str:
        if off >= len(blob):
            return ""
        end = blob.find(b"\0", off)
        if end < 0:
            end = len(blob)
        return blob[off:end].decode("utf-8", "replace")

    def symbol_bytes(self, sym: Symbol) -> bytes:
        if sym.shndx <= 0 or sym.shndx >= len(self.sections):
            return b""
        sec = self.sections[sym.shndx]
        if sec.sh_type == SHT_NOBITS:
            return b"\0" * sym.size
        return sec.data[sym.value:sym.value + sym.size]

    def kcfi(self, sym: Symbol) -> str:
        if sym.st_type != STT_FUNC or sym.shndx <= 0 or sym.value < 4:
            return ""
        sec = self.sections[sym.shndx]
        if sym.value > len(sec.data):
            return ""
        return f"0x{struct.unpack_from('<I', sec.data, sym.value - 4)[0]:08x}"


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def parse_modversions(elf: ELF64LE) -> list[tuple[str, int]]:
    sec = elf.by_name.get("__versions")
    if not sec:
        return []
    # Linux 6.1 struct modversion_info: unsigned long crc; char name[MODULE_NAME_LEN].
    # GKI modules here use 64-byte entries (8 + 56).
    if sec.size % 64:
        raise ValueError(f"{elf.path}: malformed __versions size {sec.size}")
    out = []
    for off in range(0, sec.size, 64):
        crc = struct.unpack_from("<Q", sec.data, off)[0] & 0xFFFFFFFF
        name = elf.cstr(sec.data, off + 8)
        out.append((name, crc))
    return out


def export_map(elf: ELF64LE) -> list[tuple[str, int]]:
    crcsec = elf.by_name.get("__kcrctab")
    if not crcsec:
        return []
    out = []
    for sym in elf.symbols:
        if sym.name.startswith("__crc_") and sym.shndx == crcsec.index:
            if sym.value + 4 > len(crcsec.data):
                raise ValueError(f"{elf.path}: export CRC outside __kcrctab: {sym.name}")
            out.append((sym.name[6:], struct.unpack_from("<I", crcsec.data, sym.value)[0]))
    return sorted(out, key=lambda x: elf.sym_by_name["__crc_" + x[0]].value)


def relocation_rows(elf: ELF64LE) -> list[list[object]]:
    rows: list[list[object]] = []
    for sec in elf.sections:
        if sec.sh_type != SHT_RELA:
            continue
        target = elf.sections[sec.info].name if sec.info < len(elf.sections) else str(sec.info)
        entsize = sec.entsize or 24
        for i in range(sec.size // entsize):
            off, info, addend = struct.unpack_from("<QQq", sec.data, i * entsize)
            sym_idx, rtype = info >> 32, info & 0xFFFFFFFF
            sym = elf.symbols[sym_idx] if sym_idx < len(elf.symbols) else None
            rows.append([target, f"0x{off:x}", rtype, sym.name if sym else "", f"0x{sym.value:x}" if sym else "", addend])
    return rows


def generate(module: Path, out_dir: Path, stem: str) -> dict[str, object]:
    elf = ELF64LE(module)
    funcs = []
    for s in elf.symbols:
        if s.st_type == STT_FUNC and s.shndx != SHN_UNDEF and s.name:
            body = elf.symbol_bytes(s)
            funcs.append([s.name, elf.sections[s.shndx].name, f"0x{s.value:x}", s.size,
                          BIND_NAMES.get(s.bind, str(s.bind)), elf.kcfi(s), hashlib.sha256(body).hexdigest()])
    funcs.sort(key=lambda r: (elf.sections[elf.sym_by_name[r[0]].shndx].index, int(r[2], 16), r[0]))
    write_tsv(out_dir / f"{stem}-functions.tsv",
              ["symbol", "section", "offset", "size", "binding", "kcfi_id", "sha256"], funcs)

    objects = []
    for s in elf.symbols:
        if not s.name or s.shndx == SHN_UNDEF or s.st_type in (STT_FUNC, STT_SECTION, STT_FILE):
            continue
        sec = elf.sections[s.shndx] if s.shndx < len(elf.sections) else None
        # Keep all named OBJECT symbols and named data/rodata/bss NOTYPE symbols.
        if s.st_type != STT_OBJECT and not (s.st_type == STT_NOTYPE and sec and
            (sec.name.startswith((".data", ".bss", ".rodata")) or sec.name.startswith("__mod_") or sec.name == "__mcount_loc")):
            continue
        body = elf.symbol_bytes(s)
        objects.append([s.name, sec.name if sec else str(s.shndx), f"0x{s.value:x}", s.size,
                        TYPE_NAMES.get(s.st_type, str(s.st_type)), BIND_NAMES.get(s.bind, str(s.bind)),
                        hashlib.sha256(body).hexdigest() if body else "N/A"])
    objects.sort(key=lambda r: (elf.sections[elf.sym_by_name[r[0]].shndx].index, int(r[2], 16), r[0]))
    write_tsv(out_dir / f"{stem}-objects.tsv",
              ["symbol", "section", "offset", "size", "type", "binding", "sha256"], objects)

    mods = parse_modversions(elf)
    modmap = dict(mods)
    undef = [s for s in elf.symbols if s.shndx == SHN_UNDEF and s.name and s.bind in (1, 2)]
    relocs = relocation_rows(elf)
    rel_use: dict[str, set[str]] = {}
    rel_count: dict[str, int] = {}
    for target, _, _, sym, _, _ in relocs:
        rel_count[sym] = rel_count.get(sym, 0) + 1
        rel_use.setdefault(sym, set()).add(str(target))
    imports = []
    seen = set()
    for s in sorted(undef, key=lambda x: x.name):
        seen.add(s.name)
        imports.append([s.name, f"0x{modmap[s.name]:08x}" if s.name in modmap else "", "undefined",
                        rel_count.get(s.name, 0), ",".join(sorted(rel_use.get(s.name, set())))])
    for name, crc in mods:
        if name not in seen:
            imports.append([name, f"0x{crc:08x}", "modversion-only", 0, "__versions"])
    write_tsv(out_dir / f"{stem}-imports.tsv",
              ["symbol", "crc", "elf_presence", "relocation_count", "relocation_sections"], imports)

    exports = []
    for name, crc in export_map(elf):
        s = elf.sym_by_name.get(name)
        exports.append([name, f"0x{crc:08x}", elf.sections[s.shndx].name if s else "", f"0x{s.value:x}" if s else "",
                        s.size if s else "", elf.kcfi(s) if s else "", "EXPORT_SYMBOL"])
    write_tsv(out_dir / f"{stem}-exports.tsv",
              ["symbol", "crc", "section", "offset", "size", "kcfi_id", "export_class"], exports)

    write_tsv(out_dir / f"{stem}-modversions.tsv", ["symbol", "crc"],
              [[name, f"0x{crc:08x}"] for name, crc in mods])
    write_tsv(out_dir / f"{stem}-relocations.tsv",
              ["target_section", "offset", "type_number", "symbol", "symbol_value", "addend"], relocs)

    strings = []
    pattern = re.compile(rb"[\x20-\x7e]{4,}")
    for sec in elf.sections:
        if not sec.data or sec.name in (".strtab", ".shstrtab", ".symtab") or sec.name.startswith(".debug"):
            continue
        for m in pattern.finditer(sec.data):
            strings.append([sec.name, f"0x{m.start():x}", m.group().decode("ascii")])
    write_tsv(out_dir / f"{stem}-strings.tsv", ["section", "offset", "string"], strings)

    return {
        "functions": len(funcs), "objects": len(objects), "imports": len(imports),
        "exports": len(exports), "modversions": len(mods), "relocations": len(relocs),
        "strings": len(strings), "sha256": hashlib.sha256(module.read_bytes()).hexdigest(),
        "size": module.stat().st_size,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("module", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--stem", default="phase4-fingerprint")
    args = ap.parse_args()
    stats = generate(args.module, args.out_dir, args.stem)
    for k, v in stats.items():
        print(f"{k}={v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
