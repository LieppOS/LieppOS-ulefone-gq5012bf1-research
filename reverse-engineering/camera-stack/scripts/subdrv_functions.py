#!/usr/bin/env python3
"""Per-sub-driver function inventory for stock imgsensor.ko vs a donor object.

Static functions of one sensor translation unit are contiguous in .text; the
stock TU is delimited from the <prefix>_set_test_pattern symbol up to the next
TU's first symbol (given explicitly).  For each function: size, KCFI type id
(4 bytes before entry), call targets (CALL26 relocations, resolved), and the
same for the donor object where a same-named function exists.

Usage: subdrv_functions.py <stock.ko> <stock_lo_hex> <stock_hi_hex> <donor.o>
"""
from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfmini import Elf  # noqa: E402


def funcs(elf, lo=None, hi=None):
    text = elf.secbyname[".text"].idx
    out = {}
    for s in elf.symbols:
        if s.type == 2 and s.shndx == text and (lo is None or lo <= s.value < hi):
            body = elf.blob[elf.sections[text].off + s.value: elf.sections[text].off + s.value + s.size]
            kid = struct.unpack_from("<I", elf.blob, elf.sections[text].off + s.value - 4)[0] if s.value >= 4 else 0
            calls = []
            for r in elf.relocs.get(text, []):
                if s.value <= r.off < s.value + s.size and r.tname in ("CALL26", "JUMP26"):
                    t, _ = elf.target(r)
                    calls.append(t.name)
            out.setdefault(s.name, []).append({"addr": s.value, "size": s.size, "kcfi": kid, "calls": calls})
    return out


def main():
    ko, lo, hi, donor = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16), sys.argv[4]
    st = funcs(Elf(ko), lo, hi)
    dn = funcs(Elf(donor))
    print("function\tstock_size\tdonor_size\tsize_equal\tstock_calls_only\tdonor_calls_only")
    for name in sorted(set(st) | set(dn)):
        s = st.get(name, [None])[0]
        d = dn.get(name, [None])[0]
        if s and d:
            sc, dc = set(s["calls"]), set(d["calls"])
            print(f"{name}\t{s['size']}\t{d['size']}\t{'yes' if s['size'] == d['size'] else 'no'}\t"
                  f"{','.join(sorted(sc - dc))}\t{','.join(sorted(dc - sc))}")
        elif s:
            print(f"{name}\t{s['size']}\t-\tSTOCK_ONLY\t{','.join(sorted(set(s['calls'])))}\t")
        else:
            print(f"{name}\t-\t{d['size']}\tDONOR_ONLY\t\t{','.join(sorted(set(d['calls'])))}")


if __name__ == "__main__":
    main()
