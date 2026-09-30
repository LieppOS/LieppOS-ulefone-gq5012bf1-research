#!/usr/bin/env python3
"""Compare the per-section object layout of two kernel modules.

Kernel-module data sections (`.data`, `.bss`, `.rodata*`, `.rodata.cst*`) hold
one `OBJECT` symbol per file-scope variable, laid out in the order the compiler
emitted them, which for a single translation unit is driven by the declaration
order and alignment of the globals in the original C source.  Two builds whose
layout differs therefore differ in the *source-level declaration order* (or in a
struct's field padding), not only in code generation.

This tool lists every section symbol of both modules sorted by section offset,
and reports

  * side-by-side address/size order for every data section, and
  * the reference offsets that the *disassembly* of one or more functions
    actually materialises, resolved back to the owning object name.

Usage:
  ko-layout-diff.py STOCK.ko REBUILT.ko [--section .data] [--fn NAME ...]
"""

import argparse
import re
import subprocess
import sys


def section_symbols(path):
    """{section: [(offset, size, name)]} for every non-section OBJECT symbol."""
    out = subprocess.run(["readelf", "-sW", path], capture_output=True,
                         text=True, check=True).stdout
    res = {}
    for line in out.splitlines():
        m = re.match(
            r"\s*\d+:\s+([0-9a-f]+)\s+([0-9a-f]+)\s+(\S+)\s+(\S+)\s+(\S+)\s+"
            r"(\S+)\s+(\S*)", line)
        if not m:
            continue
        val, size, otype, bind, vis, sect, name = m.groups()
        if otype != "OBJECT" or sect in ("UND", ""):
            continue
        res.setdefault(sect, []).append((int(val, 16), int(size, 16), name))
    for sect in res:
        res[sect].sort()
    return res


def disasm(path):
    return subprocess.run(["llvm-objdump", "-d", "--no-show-raw-insn", path],
                          capture_output=True, text=True,
                          check=True).stdout


ADRPS = re.compile(r"\s(adrp|add)\s+x\d+,\s+([^\s#,]+)(?:\s*#\s*(-?0x[0-9a-f]+|-?\d+))?")


def resolved_data_refs(path, syms, functions=None):
    """[(fn, section, offset, owner)] for every adrp/add pair touching data."""
    text = disasm(path)
    cur = None
    pending = {}
    res = []
    for line in text.splitlines():
        fm = re.match(r"^(?:[0-9a-f]+ )?<([A-Za-z0-9_.$]+)>:", line)
        if fm:
            cur = fm.group(1)
            continue
        if functions and cur not in functions:
            continue
        am = ADRPS.search(line)
        if not am:
            continue
        kind, base, imm = am.groups()
        if kind == "adrp":
            pending[(cur, am.start(2))] = (base, imm)
            continue
        reg = re.search(r"\badd\s+(x\d+),\s*(x\d+),\s*:lo12:([^\s#,]+)", line)
        if reg and cur:
            sym = reg.group(3)
            for sect, entries in syms.items():
                for off, size, name in entries:
                    if name == sym:
                        res.append((cur, sect, off, size, name))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stock")
    ap.add_argument("rebuilt")
    ap.add_argument("--section", action="append", default=None)
    ap.add_argument("--fn", action="append", default=None)
    args = ap.parse_args()

    ss, rs = section_symbols(args.stock), section_symbols(args.rebuilt)
    sections = args.section or sorted({*ss, *rs})
    for sect in sections:
        a, b = ss.get(sect, []), rs.get(sect, [])
        if not a and not b:
            continue
        print(f"== {sect}  stock={len(a)}/{sum(s for _, s, _ in a)}B  "
              f"rebuilt={len(b)}/{sum(s for _, s, _ in b)}B")
        byname_a = {n: (o, s) for o, s, n in a}
        byname_b = {n: (o, s) for o, s, n in b}
        order_a = [n for _, _, n in a]
        order_b = [n for _, _, n in b]
        for n in order_a:
            o1, s1 = byname_a[n]
            o2, s2 = byname_b.get(n, (None, None))
            flag = "" if (o1 == o2 and s1 == s2) else "  <-- differs"
            print(f"   {n:<48} stock {o1:#07x}/{s1:<5} "
                  f"rebuild {'-' if o2 is None else hex(o2)}/"
                  f"{'-' if o2 is None else s2}{flag}")
        only_b = [n for n in order_b if n not in byname_a]
        if only_b:
            print(f"   rebuilt-only: {only_b}")
        if order_a == order_b:
            print("   ORDER IDENTICAL")

    if args.fn:
        print("\n== resolved data references")
        for path, tag in ((args.stock, "stock"), (args.rebuilt, "rebuilt")):
            for fn, sect, off, size, name in resolved_data_refs(
                    path, section_symbols(path), set(args.fn)):
                print(f"   {tag:<8}{fn:<28}{sect:<16}{off:#07x} ({name})")


if __name__ == "__main__":
    sys.exit(main())
