#!/usr/bin/env python3
"""Tiny DWARF type database built from `llvm-dwarfdump --debug-info` text.

Only what is needed to turn stock data bytes back into C initializers:
base/enum/typedef/const/volatile/pointer/array/struct/union/subroutine types,
struct members (byte offset, bit-field size/offset) and global/static
variables (name -> type).  Read-only.
"""
from __future__ import annotations

import re
import subprocess

DIE_RE = re.compile(r"^(0x[0-9a-f]+):(\s+)(DW_TAG_\w+|NULL)")
ATTR_RE = re.compile(r"^\s+(DW_AT_\w+)\s+\((.*)\)\s*$")


class Die:
    __slots__ = ("off", "tag", "attrs", "children", "parent")

    def __init__(self, off, tag, parent):
        self.off, self.tag, self.attrs, self.children, self.parent = off, tag, {}, [], parent

    def name(self):
        v = self.attrs.get("DW_AT_name")
        return v.strip('"') if v else None

    def tref(self):
        v = self.attrs.get("DW_AT_type")
        if not v:
            return None
        return int(v.split()[0], 16)

    def ival(self, a, default=None):
        v = self.attrs.get(a)
        if v is None:
            return default
        v = v.split()[0]
        return int(v, 0)


class TypeDB:
    def __init__(self, obj):
        out = subprocess.run(["llvm-dwarfdump", "--debug-info", obj], capture_output=True, text=True).stdout
        self.dies: dict[int, Die] = {}
        self.vars: dict[str, Die] = {}
        stack: list[tuple[int, Die]] = []
        cur = None
        for line in out.splitlines():
            m = DIE_RE.match(line)
            if m:
                off, ind, tag = int(m.group(1), 16), len(m.group(2)), m.group(3)
                while stack and stack[-1][0] >= ind:
                    stack.pop()
                if tag == "NULL":
                    cur = None
                    continue
                parent = stack[-1][1] if stack else None
                cur = Die(off, tag, parent)
                self.dies[off] = cur
                if parent:
                    parent.children.append(cur)
                stack.append((ind, cur))
                continue
            m = ATTR_RE.match(line)
            if m and cur is not None:
                cur.attrs[m.group(1)] = m.group(2)
        for d in self.dies.values():
            if d.tag == "DW_TAG_variable" and d.name():
                self.vars.setdefault(d.name(), d)
        self.struct_by_name = {}
        for d in self.dies.values():
            if d.tag in ("DW_TAG_structure_type", "DW_TAG_union_type") and d.name() and \
                    "DW_AT_declaration" not in d.attrs:
                self.struct_by_name.setdefault(d.name(), d)

    # ------------------------------------------------------------------
    def strip(self, off):
        """Follow typedef/const/volatile to the underlying type DIE."""
        d = self.dies[off]
        while d.tag in ("DW_TAG_typedef", "DW_TAG_const_type", "DW_TAG_volatile_type"):
            t = d.tref()
            if t is None:
                return d
            d = self.dies[t]
        if d.tag in ("DW_TAG_structure_type", "DW_TAG_union_type") and "DW_AT_declaration" in d.attrs:
            d = self.struct_by_name.get(d.name(), d)
        return d

    def size(self, off):
        d = self.strip(off)
        if d.tag == "DW_TAG_pointer_type":
            return 8
        if d.tag == "DW_TAG_array_type":
            n = 1
            for c in d.children:
                if c.tag == "DW_TAG_subrange_type":
                    cnt = c.ival("DW_AT_count")
                    if cnt is None:
                        ub = c.ival("DW_AT_upper_bound")
                        cnt = (ub + 1) if ub is not None else 0
                    n *= cnt
            return n * self.size(d.tref())
        return d.ival("DW_AT_byte_size", 0)

    def cname(self, off):
        """C spelling of a type (used for declarations)."""
        d = self.dies[off]
        if d.tag == "DW_TAG_typedef" or d.tag == "DW_TAG_base_type":
            return d.name()
        if d.tag == "DW_TAG_const_type":
            return "const " + self.cname(d.tref())
        if d.tag == "DW_TAG_structure_type":
            return "struct " + d.name()
        if d.tag == "DW_TAG_union_type":
            return "union " + d.name()
        if d.tag == "DW_TAG_enumeration_type":
            return "enum " + d.name() if d.name() else "int"
        if d.tag == "DW_TAG_pointer_type":
            t = d.tref()
            return (self.cname(t) if t else "void") + " *"
        raise ValueError(d.tag)

    def members(self, sd):
        out = []
        for c in sd.children:
            if c.tag != "DW_TAG_member":
                continue
            bs = c.ival("DW_AT_bit_size")
            if bs is not None:
                bo = c.ival("DW_AT_data_bit_offset")
                out.append((c.name(), bo // 8, c.tref(), bs, bo))
            else:
                out.append((c.name(), c.ival("DW_AT_data_member_location", 0), c.tref(), None, None))
        return out

    def enumerators(self, ed):
        return {c.ival("DW_AT_const_value"): c.name() for c in ed.children if c.tag == "DW_TAG_enumerator"}
