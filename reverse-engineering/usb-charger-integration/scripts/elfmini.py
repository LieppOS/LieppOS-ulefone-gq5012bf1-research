#!/usr/bin/env python3
"""Minimal, dependency-free ELF64 (little-endian, AArch64 relocatable) reader.

Only what the camera-stack oracle scripts need: sections, symbols, RELA
relocations and "which symbol contains address X" lookups.  Read-only.
"""
from __future__ import annotations

import bisect
import struct
from dataclasses import dataclass, field

R_AARCH64 = {
    257: "ABS64", 258: "ABS32", 261: "PREL32", 260: "PREL64",
    275: "ADR_PREL_PG_HI21", 277: "ADD_ABS_LO12_NC", 278: "LDST8_ABS_LO12_NC",
    284: "LDST16_ABS_LO12_NC", 285: "LDST32_ABS_LO12_NC", 286: "LDST64_ABS_LO12_NC",
    299: "LDST128_ABS_LO12_NC", 282: "JUMP26", 283: "CALL26", 280: "CONDBR19",
    279: "TSTBR14", 274: "ADR_PREL_LO21", 311: "ADR_GOT_PAGE", 312: "LD64_GOT_LO12_NC",
}


@dataclass
class Section:
    idx: int
    name: str
    type: int
    flags: int
    off: int
    size: int
    link: int
    info: int
    entsize: int


@dataclass
class Symbol:
    idx: int
    name: str
    value: int
    size: int
    type: int      # 0 notype 1 object 2 func 3 section 4 file
    bind: int      # 0 local 1 global 2 weak
    shndx: int

    @property
    def kind(self):
        return {0: "NOTYPE", 1: "OBJECT", 2: "FUNC", 3: "SECTION", 4: "FILE"}.get(self.type, str(self.type))


@dataclass
class Reloc:
    sec: int          # section being relocated
    off: int
    rtype: int
    sym: Symbol
    addend: int

    @property
    def tname(self):
        return R_AARCH64.get(self.rtype, str(self.rtype))


class Elf:
    def __init__(self, path: str):
        self.path = path
        self.blob = open(path, "rb").read()
        b = self.blob
        assert b[:4] == b"\x7fELF" and b[4] == 2 and b[5] == 1, "ELF64 LE only"
        e_shoff, = struct.unpack_from("<Q", b, 0x28)
        shent, shnum, shstr = struct.unpack_from("<HHH", b, 0x3A)
        raw = [struct.unpack_from("<IIQQQQIIQQ", b, e_shoff + i * shent) for i in range(shnum)]
        stro = raw[shstr][4]
        self.sections: list[Section] = []
        for i, (nm, ty, fl, ad, off, sz, lk, inf, al, es) in enumerate(raw):
            end = b.index(b"\0", stro + nm)
            self.sections.append(Section(i, b[stro + nm:end].decode(), ty, fl, off, sz, lk, inf, es))
        self.secbyname = {s.name: s for s in self.sections}
        self._load_symbols()
        self._load_relocs()
        self._index()

    def _load_symbols(self):
        st = next(s for s in self.sections if s.type == 2)
        strs = self.sections[st.link]
        self.symbols: list[Symbol] = []
        for i in range(st.size // 24):
            nm, info, oth, shndx, val, sz = struct.unpack_from("<IBBHQQ", self.blob, st.off + i * 24)
            end = self.blob.index(b"\0", strs.off + nm)
            name = self.blob[strs.off + nm:end].decode(errors="replace")
            self.symbols.append(Symbol(i, name, val, sz, info & 0xF, info >> 4, shndx))
        for s in self.symbols:
            if s.type == 3 and not s.name:
                s.name = self.sections[s.shndx].name

    def _load_relocs(self):
        self.relocs: dict[int, list[Reloc]] = {}
        for s in self.sections:
            if s.type != 4:  # SHT_RELA
                continue
            lst = self.relocs.setdefault(s.info, [])
            for i in range(s.size // 24):
                off, info, add = struct.unpack_from("<QQq", self.blob, s.off + i * 24)
                lst.append(Reloc(s.info, off, info & 0xFFFFFFFF, self.symbols[info >> 32], add))
            lst.sort(key=lambda r: r.off)

    def _index(self):
        self._by_sec: dict[int, list[tuple[int, int, Symbol]]] = {}
        for s in self.symbols:
            if s.type in (1, 2) and 0 < s.shndx < 0xFF00:
                self._by_sec.setdefault(s.shndx, []).append((s.value, s.value + max(s.size, 1), s))
        for k in self._by_sec:
            self._by_sec[k].sort(key=lambda t: (t[0], -t[1]))
        self._starts = {k: [t[0] for t in v] for k, v in self._by_sec.items()}

    # ------------------------------------------------------------------
    def containing(self, shndx: int, addr: int):
        lst = self._by_sec.get(shndx)
        if not lst:
            return None
        i = bisect.bisect_right(self._starts[shndx], addr) - 1
        while i >= 0:
            a, e, s = lst[i]
            if a <= addr < e:
                return s
            if a < addr - 0x100000:
                break
            i -= 1
        return None

    def target(self, r: Reloc):
        """Resolve a relocation to (symbol, offset-in-symbol)."""
        s = r.sym
        if s.type in (1, 2) and s.shndx not in (0,):
            return s, r.addend
        if s.shndx == 0:
            return s, r.addend   # undefined import
        addr = s.value + r.addend
        c = self.containing(s.shndx, addr)
        if c is None:
            return s, addr
        return c, addr - c.value

    def relocs_in(self, sym: Symbol):
        lst = self.relocs.get(sym.shndx, [])
        lo, hi = sym.value, sym.value + sym.size
        i = bisect.bisect_left([r.off for r in lst], lo)
        out = []
        while i < len(lst) and lst[i].off < hi:
            out.append(lst[i])
            i += 1
        return out

    def ptr_at(self, sym: Symbol, field_off: int):
        """Pointer field value inside a data object = relocation target there."""
        for r in self.relocs_in(sym):
            if r.off == sym.value + field_off:
                return self.target(r)
        return None

    def bytes_of(self, sym: Symbol, start: int = 0, length: int | None = None) -> bytes:
        sec = self.sections[sym.shndx]
        if sec.type == 8:  # NOBITS
            return b"\0" * (length if length is not None else sym.size)
        n = sym.size - start if length is None else length
        return self.blob[sec.off + sym.value + start: sec.off + sym.value + start + n]

    def sym(self, name: str, kind: int | None = None):
        c = [s for s in self.symbols if s.name == name and (kind is None or s.type == kind) and s.shndx]
        return c

    def cstring(self, sym: Symbol, off: int):
        sec = self.sections[sym.shndx]
        p = sec.off + sym.value + off
        e = self.blob.index(b"\0", p)
        return self.blob[p:e].decode(errors="replace")

    def cstring_at(self, shndx: int, addr: int):
        sec = self.sections[shndx]
        p = sec.off + addr
        e = self.blob.index(b"\0", p)
        return self.blob[p:e].decode(errors="replace")
