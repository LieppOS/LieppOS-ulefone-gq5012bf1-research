#!/usr/bin/env python3
"""Minimal flat-device-tree walker (no external deps).

Parses an FDT/.dtb into a node list with full property values, so the coverage
axes can answer bus/address/status questions exactly instead of heuristically
re-parsing dtc text.

Node record: {"path", "name", "parent", "props": {name: [values]}}
Property values are decoded as: int lists for cell arrays, str for short
byte strings, else hex-dumped string prefixed with "bytes:".
"""
from __future__ import annotations

import struct

FDT_BEGIN_NODE = 1
FDT_END_NODE = 2
FDT_PROP = 3
FDT_END = 9


def _cstr(b: bytes, off: int) -> tuple[str, int]:
    end = b.index(b"\x00", off)
    return b[off:end].decode("utf-8", "replace"), end + 1


def _cells(data: bytes) -> list[int]:
    return list(struct.unpack(f">{len(data) // 4}I", data))


def _decode(name: str, data: bytes):
    if name == "compatible":
        out = data.rstrip(b"\x00").split(b"\x00")
        return [s.decode("utf-8", "replace") for s in out if s]
    if name in ("status", "model", "name", "label", "fsmode", "customval"):
        return [data.rstrip(b"\x00").decode("utf-8", "replace")]
    if len(data) and len(data) % 4 == 0 and len(data) <= 64:
        return [hex(v) for v in _cells(data)]
    if not data:
        return ["<empty>"]
    return [f"bytes:{data.hex()}"]


def walk(path: str) -> list[dict]:
    blob = open(path, "rb").read()
    magic, totalsize, off_dt_struct, off_dt_strings = struct.unpack(">4I", blob[:16])
    if magic != 0xD00DFEED:
        raise ValueError(f"not an FDT (magic {hex(magic)})")
    strings = blob[off_dt_strings : off_dt_strings + totalsize]
    p = off_dt_struct
    end = len(blob)
    stack: list[str] = []
    nodes: list[dict] = []
    cur: dict | None = None
    while p < end:
        (tag,) = struct.unpack(">I", blob[p : p + 4])
        p += 4
        if tag == FDT_END:
            break
        if tag == FDT_BEGIN_NODE:
            name, p = _cstr(blob, p)
            p += (-p) % 4
            cur = {
                "path": "/" + "/".join([s for s in stack + [name] if s]),
                "name": name,
                "parent": "/" + "/".join([s for s in stack if s]),
                "props": {},
            }
            nodes.append(cur)
            stack.append(name)
            continue
        if tag == FDT_END_NODE:
            if stack:
                stack.pop()
            cur = None
            continue
        if tag == FDT_PROP:
            plen, nmoff = struct.unpack(">2I", blob[p : p + 8])
            p += 8
            s = strings.index(b"\x00", nmoff)
            nm = strings[nmoff:s].decode("utf-8", "replace")
            data = blob[p : p + plen]
            p += plen + (-plen) % 4
            if cur is not None:
                cur["props"].setdefault(nm, []).extend(_decode(nm, data))
            continue
        if tag == 4:  # FDT_NOP
            continue
        raise ValueError(f"unknown FDT tag {tag} at {p - 4}")
    return nodes


def unit_addr(name: str) -> str:
    return name.split("@", 1)[1] if "@" in name else ""


if __name__ == "__main__":
    import sys

    for n in walk(sys.argv[1])[:10]:
        print(n["path"], sorted(n["props"]))
