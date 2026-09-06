#!/usr/bin/env python3
"""Slice one or more functions out of the FT3680 stock/rebuilt disassembly.

Usage:
  fts-slice-func.py <functions.tsv> <disassembly.txt> <name> [name...]

Addresses in the disassembly are section-relative (llvm-objdump -d of a .ko),
and functions.tsv rows are  name<TAB>section<TAB>0xoffset<TAB>size<TAB>bind.
Relocation continuation lines (no leading address) stay attached to the
preceding instruction.
"""
import re
import sys

ADDR = re.compile(r"^\s*([0-9a-f]+):\s")


def load(tsv):
    out = {}
    with open(tsv) as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            out[p[0]] = (p[1], int(p[2], 16), int(p[3]))
    return out


def main():
    tsv, dis, *names = sys.argv[1:]
    funcs = load(tsv)
    ranges = []
    for n in names:
        if n not in funcs:
            sys.exit(f"unknown function: {n}")
        sec, off, size = funcs[n]
        ranges.append((n, sec, off, off + size))

    keep = False
    with open(dis) as fh:
        for line in fh:
            m = ADDR.match(line)
            if m:
                a = int(m.group(1), 16)
                keep = any(lo <= a < hi for _, _, lo, hi in ranges)
            if keep:
                sys.stdout.write(line)


if __name__ == "__main__":
    main()
