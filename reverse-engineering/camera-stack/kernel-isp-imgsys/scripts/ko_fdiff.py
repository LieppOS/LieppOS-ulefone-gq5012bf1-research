#!/usr/bin/env python3
"""Symbolic disassembly diff of one function (or hexdump diff of one data
object) between a stock and a rebuilt module.

usage: ko_fdiff.py <stock.ko> <rebuilt.ko> <name> [occ] [--stock-only|--rebuilt-only] [--section .text]
"""
import difflib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from elfmini import Elf  # noqa: E402
import ko_parity as KP  # noqa: E402


def find(e, name, occ, sec=None):
    c = [s for s in e.symbols if s.name == name and 0 < s.shndx < 0xFF00 and s.type in (1, 2)
         and (sec is None or e.sections[s.shndx].name == sec)]
    c.sort(key=lambda s: (e.sections[s.shndx].name, s.value))
    return c[occ] if len(c) > occ else None


def flist(path, e, f):
    sec = e.sections[f.shndx].name
    out = subprocess.run(["llvm-objdump", "-d", "--no-show-raw-insn", f"--start-address={f.value}",
                          f"--stop-address={f.value + f.size}", "-j", sec, path],
                         capture_output=True, text=True).stdout
    n = KP.Norm(e)
    rel = {}
    for off, t, tgt in n.sig(f):
        rel.setdefault(off, []).append(f"{t} {tgt}")
    lines = []
    for l in out.splitlines():
        m = re.match(r"\s*([0-9a-f]+):\s+(.*)", l)
        if not m:
            continue
        a = int(m.group(1), 16) - f.value
        ins = re.sub(r"\s+", " ", m.group(2)).strip()
        ins = re.sub(r"0x([0-9a-f]+) <[^>]*>", lambda mm: f"<+{int(mm.group(1), 16) - f.value:#x}>", ins)
        ins = re.sub(r"\s*//.*$", "", ins)
        r = rel.get(a)
        if r:
            ins = re.sub(r"<\+0x[0-9a-f]+>", "<>", ins) if any(x.startswith(("CALL26", "JUMP26")) for x in r) else ins
            ins = re.sub(r"#0x[0-9a-f]+", "#rel", ins) if "ADD_ABS_LO12_NC" in " ".join(r) or "LDST" in " ".join(r) else ins
            ins = re.sub(r"adrp (\w+), .*", r"adrp \1", ins)
        lines.append(f"{a:5x}: {ins}" + (f"    ; {' | '.join(r)}" if r else ""))
    return lines


def dlist(e, s):
    b = KP.sbytes(e, s) or b""
    n = KP.Norm(e)
    rel = {off: f"{t} {tgt}" for off, t, tgt in n.sig(s)}
    out = []
    for i in range(0, max(len(b), s.size), 8):
        chunk = b[i:i + 8].hex() if b else "nobits"
        rr = [rel[j] for j in range(i, i + 8) if j in rel]
        out.append(f"{i:5x}: {chunk}" + (f"  ; {' | '.join(rr)}" if rr else ""))
    return out


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    stock, reb, name = args[:3]
    occ = int(args[3]) if len(args) > 3 else 0
    sec = sys.argv[sys.argv.index("--section") + 1] if "--section" in sys.argv else None
    a, b = Elf(stock), Elf(reb)
    sa, sb = find(a, name, occ, sec), find(b, name, occ, sec)
    L = lambda p, e, s: (flist(p, e, s) if s.type == 2 else dlist(e, s)) if s else ["<absent>"]  # noqa
    la, lb = L(stock, a, sa), L(reb, b, sb)
    if "--stock-only" in sys.argv:
        print("\n".join(la))
        return
    if "--rebuilt-only" in sys.argv:
        print("\n".join(lb))
        return
    norm = lambda ls: [re.sub(r"^\s*[0-9a-f]+: ", "", x) for x in ls]  # noqa
    for l in difflib.unified_diff(norm(la), norm(lb), "stock", "rebuilt", n=2, lineterm=""):
        print(l)


if __name__ == "__main__":
    main()
