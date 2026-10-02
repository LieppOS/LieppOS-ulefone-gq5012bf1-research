#!/usr/bin/env python3
"""Convert an inline_writes.py TSV (stock register writes recovered from a
sensor init function) into C statements using the imgsensor subdrv macros.

Delays: __const_udelay(n*4295) == udelay(n).  mdelay(n) with constant
n <= MAX_UDELAY_MS (5) is a single udelay(n*1000); larger n is a loop of n
udelay(1000) that clang unrolls, so k consecutive 1000us calls with k > 5
become mdelay(k).

Usage: inline_to_c.py <tsv> [--skip N] [--count N]
"""
import sys


def main():
    path = sys.argv[1]
    rows = [l.rstrip("\n").split("\t") for l in open(path) if l.strip() and not l.startswith(("#", "addr"))]
    out = []
    i = 0
    while i < len(rows):
        addr, kind, reg, val, *_ = rows[i] + [""]
        if kind.startswith("delay"):
            us = int(val.rstrip("us"))
            if us == 1000:
                j = i
                while j < len(rows) and rows[j][1].startswith("delay") and rows[j][3] == "1000us":
                    j += 1
                k = j - i
                if k > 5:
                    out.append(f"\tmdelay({k});")
                else:
                    out += ["\tmdelay(1);"] * k
                i = j
                continue
            if us % 1000 == 0 and us // 1000 <= 5:
                out.append(f"\tmdelay({us // 1000});")
            else:
                out.append(f"\tudelay({us});")
        elif kind in ("u16", "u8"):
            out.append(f"\tsubdrv_i2c_wr_{kind}(ctx, {int(reg, 16):#06x}, {int(val, 16):#06x});")
        else:
            out.append(f"\t/* unhandled {kind} {reg} {val} */")
        i += 1
    print("\n".join(out))


if __name__ == "__main__":
    main()
