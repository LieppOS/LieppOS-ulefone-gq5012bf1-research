#!/usr/bin/env python3
"""Annotated function disassembly for the FT3680 reconstruction.

Merges llvm-objdump output with:
  * symbol names for .text targets (from <functions.tsv>)
  * string literal contents for .rodata.str* relocation addends
  * object names for .data/.bss relocation addends (from <objects.tsv>)

Usage:
  fts-annotate.py <workspace-dir> <name> [name...]

Expects in <workspace-dir>:
  stock-functions.tsv, stock-objects.tsv, stock-disassembly-text.txt,
  and the raw .ko path in stock-module-paths.txt (for string extraction).
"""
import bisect
import os
import re
import subprocess
import sys

ADDR = re.compile(r"^\s*([0-9a-f]+):\s+([0-9a-f]{8})\s+(.*)$")
REL = re.compile(r"^\s*([0-9a-f]+):\s+(R_AARCH64_\S+)\s+(\S+)")


def load_tsv(path):
    rows = []
    with open(path) as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                rows.append((p[0], p[1], int(p[2], 16), int(p[3])))
    return rows


def section_bytes(ko, name):
    out = subprocess.run(
        ["llvm-objcopy", "--dump-section", f"{name}=/dev/stdout", ko, "/dev/null"],
        capture_output=True)
    return out.stdout


def main():
    ws = sys.argv[1]
    names = sys.argv[2:]
    funcs = load_tsv(os.path.join(ws, "stock-functions.tsv"))
    objs = load_tsv(os.path.join(ws, "stock-objects.tsv"))
    ko = open(os.path.join(ws, "stock-module-paths.txt")).read().strip().split("\n")[0]

    text = [(o, n, s) for n, sec, o, s in funcs if sec == ".text"]
    text.sort()
    tstarts = [t[0] for t in text]

    strs = {}
    for sec in (".rodata.str1.1", ".rodata.str"):
        blob = section_bytes(ko, sec)
        if not blob:
            continue
        i = 0
        for chunk in blob.split(b"\0"):
            strs[(sec, i)] = chunk.decode("utf-8", "replace")
            i += len(chunk) + 1

    objmap = {}
    for n, sec, o, s in objs:
        objmap.setdefault(sec, []).append((o, n, s))
    for v in objmap.values():
        v.sort()

    def sym_text(a):
        i = bisect.bisect_right(tstarts, a) - 1
        if i < 0:
            return None
        o, n, s = text[i]
        return n if a == o else (f"{n}+0x{a - o:x}" if a < o + s else None)

    def annotate_target(t):
        m = re.match(r"^([^+]+)(?:\+0x([0-9a-f]+))?$", t)
        if not m:
            return ""
        sec, add = m.group(1), int(m.group(2) or "0", 16)
        if sec.startswith(".rodata.str"):
            s = strs.get((sec, add))
            return f'  "{s}"' if s is not None else ""
        if sec == ".text":
            n = sym_text(add)
            return f"  <{n}>" if n else ""
        lst = objmap.get(sec)
        if lst:
            i = bisect.bisect_right([x[0] for x in lst], add) - 1
            if i >= 0:
                o, n, s = lst[i]
                if add < o + max(s, 1):
                    return f"  <{n}+0x{add - o:x}>" if add != o else f"  <{n}>"
        return ""

    ranges = []
    for n in names:
        hit = [(o, s) for nm, sec, o, s in funcs if nm == n and sec == ".text"]
        if not hit:
            sys.exit(f"unknown .text function: {n}")
        ranges.append((n, hit[0][0], hit[0][0] + hit[0][1]))

    keep = False
    with open(os.path.join(ws, "stock-disassembly-text.txt")) as fh:
        for line in fh:
            m = ADDR.match(line)
            if m:
                a = int(m.group(1), 16)
                keep = any(lo <= a < hi for _, lo, hi in ranges)
                if keep:
                    for n, lo, hi in ranges:
                        if a == lo:
                            print(f"\n=== {n} (0x{lo:x} .. 0x{hi:x}) ===")
                    txt = m.group(3).rstrip()
                    bt = re.search(r"0x([0-9a-f]+)\s+<", txt)
                    extra = ""
                    tm = re.search(r"\b(?:b|bl|b\.\w+|cbz|cbnz|tbz|tbnz)\s+.*?0x([0-9a-f]+)",
                                   txt)
                    if tm:
                        s = sym_text(int(tm.group(1), 16))
                        if s:
                            extra = f"   -> {s}"
                    print(f"  {a:6x}: {txt}{extra}")
                continue
            m = REL.match(line)
            if m and keep:
                print(f"          R: {m.group(3)}{annotate_target(m.group(3))}")


if __name__ == "__main__":
    main()
