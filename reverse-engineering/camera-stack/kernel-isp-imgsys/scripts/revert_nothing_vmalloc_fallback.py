#!/usr/bin/env python3
"""Remove the NothingOSS-only "kcalloc memory faill" vmalloc fallback blocks.

Nothing added, after many devm_k*alloc() calls, a block

    if (!X) {
        dev_info(dev, "kcalloc memory faill %d", __LINE__);   // or printk(...)
        X = vmalloc(...);
    }

The GQ5012BF1 stock modules contain no "kcalloc memory faill" string at all
(checked over every stock vendor_dlkm / vendor_boot module), and per-function
parity proves the blocks absent (e.g. mtk-ipesys-me probe becomes byte-exact
once removed).  This script deletes exactly that block shape and reports
any occurrence it cannot handle.

usage: revert_nothing_vmalloc_fallback.py <file.c>...
"""
import re
import sys

BLOCK = re.compile(
    r"\n([ \t]*)if \(!\s*([^)]+?)\s*\)\s*\{[ \t]*\n"
    r"[ \t]*(?:dev_info\([^;]*?|printk\()\"kcalloc memory faill %d\", __LINE__\);[ \t]*\n"
    r"[ \t]*\2\s*=\s*vmalloc\([^;]*\);[ \t]*\n"
    r"[ \t]*\}[ \t]*\n")


def main():
    total = 0
    for p in sys.argv[1:]:
        s = open(p).read()
        n_before = s.count("kcalloc memory faill")
        s2, n = BLOCK.subn("\n", s)
        left = s2.count("kcalloc memory faill")
        if n:
            open(p, "w").write(s2)
        total += n
        print(f"{p}: removed {n}/{n_before}" + (f"  LEFT {left}" if left else ""))
    print("total", total)


if __name__ == "__main__":
    main()
