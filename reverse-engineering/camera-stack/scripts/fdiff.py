#!/usr/bin/env python3
"""Disassemble one function (TU-qualified) from stock and rebuilt imgsensor.ko
with symbolic relocations and print a unified diff (or just the stock side).

Usage: fdiff.py <stock.ko> <rebuilt.ko|-> <build_dir|-> <tu> <name> [occ] [--stock-only] [--raw]
"""
from __future__ import annotations

import difflib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import imgsensor_parity as P  # noqa: E402
from elfmini import Elf  # noqa: E402


def listing(path, elf, f, norm):
    out = subprocess.run(["llvm-objdump", "-d", "--no-show-raw-insn", "--no-leading-addr",
                          f"--start-address={f.value}", f"--stop-address={f.value + f.size}",
                          "-j", ".text", path], capture_output=True, text=True).stdout
    out2 = subprocess.run(["llvm-objdump", "-d", "--no-show-raw-insn",
                           f"--start-address={f.value}", f"--stop-address={f.value + f.size}",
                           "-j", ".text", path], capture_output=True, text=True).stdout
    rel = {}
    for off, t, tgt in norm.sig(f):
        rel.setdefault(off, []).append(f"{t} {tgt}")
    lines = []
    for l in out2.splitlines():
        m = re.match(r"\s*([0-9a-f]+):\s+(.*)", l)
        if not m:
            continue
        a = int(m.group(1), 16) - f.value
        ins = re.sub(r"\s+", " ", m.group(2)).strip()
        # branch targets: make relative to function start
        ins = re.sub(r"0x([0-9a-f]+) <[^>]*>", lambda mm: f"<+{int(mm.group(1), 16) - f.value:#x}>", ins)
        ins = re.sub(r"\s*//.*$", "", ins)
        r = rel.get(a)
        lines.append(f"{a:5x}: {ins}" + (f"    ; {' | '.join(r)}" if r else ""))
    return lines


def find(elf, pairs, tu, name, occ):
    k = 0
    for t, s in pairs:
        if t == tu and s.name == name:
            if k == occ:
                return s
            k += 1
    raise SystemExit(f"{tu}:{name}#{occ} not found")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    stock, reb, bdir, tu, name = args[:5]
    occ = int(args[5]) if len(args) > 5 else 0
    se = Elf(stock)
    if reb != "-":
        re_ = Elf(reb)
        rb = P.attribute_rebuilt(re_, bdir)
        owner = {}
        for t, s in rb:
            owner.setdefault(s.name, t)
    else:
        owner = {}
        rb = None
    st = P.attribute_stock(se, owner) if owner else None
    if st is None:
        # stock-only mode: framework owner unknown, use sensor attribution only
        st = P.attribute_stock(se, {})
    sf = find(se, st, tu, name, occ)
    sl = listing(stock, se, sf, P.Normaliser(se))
    if "--stock-only" in sys.argv or reb == "-":
        print("\n".join(sl))
        return
    rf = find(re_, rb, tu, name, occ)
    rl = listing(reb, re_, rf, P.Normaliser(re_))
    if "--rebuilt-only" in sys.argv:
        print("\n".join(rl))
        return
    for l in difflib.unified_diff(sl, rl, "stock", "rebuilt", n=3, lineterm=""):
        print(l)


if __name__ == "__main__":
    main()
