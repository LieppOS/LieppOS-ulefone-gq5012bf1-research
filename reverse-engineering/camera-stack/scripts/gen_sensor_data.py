#!/usr/bin/env python3
"""Regenerate C definitions for the data objects of one stock imgsensor.ko
sensor translation unit (static_ctx, mode_struct, frame descriptors,
register tables, pw_seq, ops, feature list, PD info, ...) from the stock
bytes + relocations, typed with DWARF from a reference build object.

Usage:
  gen_sensor_data.py <stock.ko> <tu-prefix> <ref.o> [<ref2.o> ...] > data.inc

Output: one C definition per object, topologically ordered (definitions
before use), each array emitted with its full stock element count so the
object size is identical.  Function pointers are emitted by name; the
functions themselves are hand-written in the sensor .c file.
"""
from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import imgsensor_parity as P  # noqa: E402
from dwarf_types import TypeDB  # noqa: E402
from elfmini import Elf  # noqa: E402

# variable name -> struct tag (element type) for objects that are not plain tables
STRUCT_OF = {
    "static_ctx": "subdrv_static_ctx",
    "mode_struct": "subdrv_mode_struct",
    "pw_seq": "subdrv_pw_seq_entry",
    "ops": "subdrv_ops",
    "feature_control_list": "subdrv_feature_control",
    "eeprom_info": "eeprom_info_struct",
    "imgsensor_pd_info": "SET_PD_BLOCK_INFO_T",
    "imgsensor_pd_info_fullsize": "SET_PD_BLOCK_INFO_T",
    "imgsensor_saturation_info_10bit": "mtk_sensor_saturation_info",
    "imgsensor_saturation_info_12bit": "mtk_sensor_saturation_info",
    "imgsensor_saturation_info_14bit": "mtk_sensor_saturation_info",
    "csi_param": "mtk_csi_param",
}
ENTRY_SUFFIX = "_mipi_raw_entry"


def ctype_of(name):
    if name.endswith(ENTRY_SUFFIX):
        return ("struct", "subdrv_entry")
    if name in STRUCT_OF:
        return ("struct", STRUCT_OF[name])
    if name.startswith("frame_desc"):
        return ("struct", "mtk_mbus_frame_desc_entry")
    if name.startswith("csi_param"):
        return ("struct", "mtk_csi_param")
    if name.endswith("_ana_gain_table") or "_dcg_ratio_table" in name:
        return ("base", "u32")
    if name in ("Is_Read_4Cell",):
        return ("base", "u8")
    if name in ("Four_Cell_Array",):
        return ("base", "u8")
    return ("base", "u16")   # *_setting, *_seamless_*, addr_data_pair_*, init tables


class Gen:
    def __init__(self, ko, prefix, refs):
        self.e = Elf(ko)
        self.n = P.Normaliser(self.e)
        self.dbs = [TypeDB(r) for r in refs]
        self.prefix = prefix
        self.objs = self._objects()
        self.byaddr = {(s.shndx, s.value): s for _, s in self.objs}
        self.kind = {}

    def _objects(self):
        # attribute stock data with an owner map from a reference build is not
        # available here; use the sensor-segment logic with an empty owner map
        # restricted to the requested prefix.
        rows = P.attribute_stock_data(self.e, {})
        return [(sec, s) for tu, sec, s in rows if tu == self.prefix]

    def struct(self, tag):
        for db in self.dbs:
            d = db.struct_by_name.get(tag)
            if d is not None:
                return db, d
        raise KeyError(tag)

    # ------------------------------------------------------------------
    def reloc_at(self, sym, off):
        for r in self.e.relocs_in(sym):
            if r.off == sym.value + off:
                return r
        return None

    def ptr_expr(self, sym, off):
        r = self.reloc_at(sym, off)
        if r is None:
            v = struct.unpack_from("<Q", self.e.bytes_of(sym), off)[0]
            return "NULL" if v == 0 else hex(v)
        tgt, toff = self.e.target(r)
        sec = self.e.sections[r.sym.shndx] if r.sym.shndx else None
        if sec is not None and sec.flags & 0x20:   # merged strings
            s = self.e.cstring_at(r.sym.shndx, r.sym.value + r.addend)
            return '"' + s.encode("unicode_escape").decode().replace('"', '\\"') + '"'
        if tgt.type == 2:
            return tgt.name
        k = self.kind.get(tgt.name)
        if toff == 0:
            if k and k[0] == "struct" and not k[2]:
                return "&" + tgt.name
            return tgt.name
        if k:
            el = k[3]
            if toff % el == 0:
                return f"&{tgt.name}[{toff // el}]"
        return f"(void *)((char *){tgt.name} + {toff})"

    def has_reloc(self, sym, lo, hi):
        return any(sym.value + lo <= r.off < sym.value + hi for r in self.e.relocs_in(sym))

    def value(self, db, toff, sym, off, bits=None, indent=1):
        d = db.strip(toff)
        b = self.e.bytes_of(sym)
        if bits is not None:
            bs, bo = bits
            w = int.from_bytes(b[bo // 8: bo // 8 + 8].ljust(8, b"\0"), "little")
            return str((w >> (bo % 8)) & ((1 << bs) - 1))
        if d.tag == "DW_TAG_pointer_type":
            return self.ptr_expr(sym, off)
        if d.tag in ("DW_TAG_base_type", "DW_TAG_enumeration_type"):
            sz = db.size(toff)
            v = int.from_bytes(b[off:off + sz], "little")
            enc = d.attrs.get("DW_AT_encoding", "")
            if "signed" in enc and "unsigned" not in enc and v >> (8 * sz - 1):
                v -= 1 << (8 * sz)
            if d.tag == "DW_TAG_enumeration_type":
                en = db.enumerators(d)
                if v in en:
                    return en[v]
            return hex(v) if sz == 2 and v > 9 else str(v)
        if d.tag == "DW_TAG_array_type":
            el = d.tref()
            esz = db.size(el)
            n = db.size(toff) // esz if esz else 0
            items = [self.value(db, el, sym, off + i * esz, indent=indent) for i in range(n)]
            while items and self.zero(db, el, sym, off + (len(items) - 1) * esz):
                items.pop()
            return "{" + ", ".join(items) + "}"
        if d.tag in ("DW_TAG_structure_type", "DW_TAG_union_type"):
            return self.struct_init(db, d, sym, off, indent + 1)
        raise ValueError(d.tag)

    def zero(self, db, toff, sym, off, size=None):
        size = size if size is not None else db.size(toff)
        return not any(self.e.bytes_of(sym)[off:off + size]) and not self.has_reloc(sym, off, off + size)

    def struct_init(self, db, sd, sym, off, indent=1):
        mem = db.members(sd)
        parts = []
        if sd.tag == "DW_TAG_union_type":
            size = db.size(sd.off)
            nz = [i for i in range(size) if self.e.bytes_of(sym)[off + i]]
            last = max(nz) + 1 if nz else 0
            for name, moff, mt, bs, bo in mem:
                if db.size(mt) >= last:
                    if not self.zero(db, mt, sym, off + moff):
                        parts.append(f".{name} = {self.value(db, mt, sym, off + moff, indent=indent)}")
                    break
            return "{" + ", ".join(parts) + "}"
        for name, moff, mt, bs, bo in mem:
            if bs is not None:
                v = self.value(db, mt, sym, off, bits=(bs, off * 8 + bo))
                if v != "0":
                    parts.append(f".{name} = {v}")
                continue
            if self.zero(db, mt, sym, off + moff):
                continue
            parts.append(f".{name} = {self.value(db, mt, sym, off + moff, indent=indent)}")
        pad = "\t" * indent
        if not parts:
            return "{0}"
        return "{\n" + "".join(f"{pad}{p},\n" for p in parts) + "\t" * (indent - 1) + "}"

    # ------------------------------------------------------------------
    def decl(self, s):
        kind, tname = ctype_of(s.name)
        const = self.e.sections[s.shndx].name == ".rodata"
        cst = "const " if const else ""
        glob = s.bind == 1
        storage = "" if glob else "static "
        if kind == "base":
            esz = {"u8": 1, "u16": 2, "u32": 4}[tname]
            self.kind[s.name] = ("base", tname, True, esz)
            n = s.size // esz
            b = self.e.bytes_of(s)
            vals = [int.from_bytes(b[i * esz:(i + 1) * esz], "little") for i in range(n)]
            if self.e.sections[s.shndx].type == 8:
                return f"{storage}{cst}{tname} {s.name}[{n}];"
            if tname == "u16" and n % 2 == 0:
                rows = [f"\t{vals[i]:#06x}, {vals[i + 1]:#06x}," for i in range(0, n, 2)]
            else:
                rows = ["\t" + ", ".join(str(v) for v in vals[i:i + 8]) + "," for i in range(0, n, 8)]
            return f"{storage}{cst}{tname} {s.name}[{n}] = {{\n" + "\n".join(rows) + "\n};"
        db, sd = self.struct(tname)
        esz = db.size(sd.off)
        is_arr = not (s.name in ("static_ctx", "ops") or s.name.endswith(ENTRY_SUFFIX)
                      or s.name.startswith("imgsensor_pd_info") or s.name.startswith("imgsensor_saturation"))
        self.kind[s.name] = ("struct", tname, is_arr, esz)
        if not is_arr:
            assert s.size == esz, (s.name, s.size, esz)
            return f"{storage}{cst}struct {tname} {s.name} = {self.struct_init(db, sd, s, 0)};"
        n = s.size // esz
        assert n * esz == s.size, (s.name, s.size, esz)
        items = [self.struct_init(db, sd, s, i * esz, indent=2) for i in range(n)]
        return f"{storage}{cst}struct {tname} {s.name}[{n}] = {{\n" + "".join(f"\t{it},\n" for it in items) + "};"

    def refs(self, s):
        out = []
        for r in self.e.relocs_in(s):
            t, _ = self.e.target(r)
            if t is not None and t.type == 1 and (t.shndx, t.value) in self.byaddr and t is not s:
                out.append(t)
        return out

    def emit(self):
        # pre-compute kinds so pointer expressions know array vs struct
        for _, s in self.objs:
            self.decl(s)
        done, order = set(), []

        def visit(s):
            if id(s) in done:
                return
            done.add(id(s))
            for t in self.refs(s):
                visit(t)
            order.append(s)

        for _, s in self.objs:
            visit(s)
        print(f"/* generated by gen_sensor_data.py from stock imgsensor.ko ({self.prefix}) */")
        for s in order:
            print(f"/* stock {self.e.sections[s.shndx].name}+{s.value:#x} size {s.size} */")
            print(self.decl(s))
            print()


def main():
    ko, prefix = sys.argv[1], sys.argv[2]
    Gen(ko, prefix, sys.argv[3:]).emit()


if __name__ == "__main__":
    main()
