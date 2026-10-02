#!/usr/bin/env python3
"""Extract every `static (kal_)u16 name[] = { ... };` register table from donor
C source files into <out>/settings/<name>.tsv (addr/value pairs), so legacy
donor drivers can be cross-matched with crossmatch_tables.py without building.

Usage: c_tables_to_tsv.py <out_dir> <file.c|file.h>...
Handles `#if 0` blocks crudely (skipped) and C/C++ comments.
"""
from __future__ import annotations

import os
import re
import sys

ARR = re.compile(r"(?:static\s+)?(?:const\s+)?(?:kal_uint16|u16|unsigned short|uint16_t)\s+(\w+)\s*\[\s*\]\s*=\s*\{(.*?)\};",
                 re.S)


def strip(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    t = re.sub(r"//[^\n]*", "", t)
    out, skip = [], 0
    for ln in t.splitlines():
        s = ln.strip()
        if re.match(r"#\s*if\s+0\b", s):
            skip += 1
            continue
        if skip and re.match(r"#\s*if", s):
            skip += 1
            continue
        if skip and re.match(r"#\s*endif", s):
            skip -= 1
            continue
        if not skip:
            out.append(ln)
    return "\n".join(out)


def main():
    out = sys.argv[1]
    os.makedirs(os.path.join(out, "settings"), exist_ok=True)
    n = 0
    for f in sys.argv[2:]:
        t = strip(open(f, errors="replace").read())
        for m in ARR.finditer(t):
            vals = [int(x, 0) for x in re.findall(r"0[xX][0-9a-fA-F]+|\b\d+\b", m.group(2))]
            if len(vals) < 4 or len(vals) % 2:
                continue
            with open(os.path.join(out, "settings", m.group(1) + ".tsv"), "w") as fo:
                fo.write("addr\tvalue\n")
                for i in range(0, len(vals), 2):
                    fo.write(f"0x{vals[i]:04x}\t0x{vals[i + 1]:04x}\n")
            n += 1
    print(f"{n} tables extracted")


if __name__ == "__main__":
    main()
