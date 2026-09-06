#!/usr/bin/env python3
"""Compact annotated disassembly: collapses adrp/add pairs into one line and
strips duplicate relocation echoes.  Usage: fts-compact.py <ws> <func...>"""
import re
import subprocess
import sys

ws = sys.argv[1]
out = subprocess.run(
    [sys.executable, __file__.rsplit("/", 1)[0] + "/fts-annotate.py", ws] + sys.argv[2:],
    capture_output=True, text=True).stdout

out = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', lambda m: m.group(0).replace("\n", "\\n"), out, flags=re.S)
lines = out.split("\n")
res = []
i = 0
pend = None
while i < len(lines):
    ln = lines[i]
    m = re.match(r"\s*([0-9a-f]+): (.*)", ln)
    if not m:
        res.append(ln)
        i += 1
        continue
    addr, ins = m.group(1), m.group(2).strip()
    rel = None
    if i + 1 < len(lines) and lines[i + 1].lstrip().startswith("R:"):
        rel = lines[i + 1].strip()[2:].strip()
        i += 1
    i += 1
    ins = re.sub(r"\s+", " ", ins)
    # collapse "bl 0x... -> name" noise
    ins = re.sub(r"bl\s+0x[0-9a-f]+ <[^>]*>\s*->\s*\S+", "bl", ins)
    ins = re.sub(r"(b|b\.\w+|cbz|cbnz|tbz|tbnz)\s+(0x[0-9a-f]+) <[^>]*>\s*->\s*\S+",
                 r"\1 \2", ins)
    if ins.startswith("adrp"):
        pend = (addr, ins, rel)
        continue
    if pend and (ins.startswith("add ") or ins.startswith("ldr") or
                 ins.startswith("str") or ins.startswith("ldrb") or
                 ins.startswith("ldrh") or ins.startswith("strb")):
        prel = rel or pend[2]
        base = ins.split()[0]
        if base == "add":
            res.append("  %s: LEA %s   ; %s" % (addr, ins.split(",")[0].split()[1], prel or "?"))
        else:
            res.append("  %s: %s   ; %s" % (addr, ins, prel or "?"))
        pend = None
        continue
    if pend:
        res.append("  %s: %s   ; %s" % (pend[0], pend[1], pend[2] or "?"))
        pend = None
    res.append("  %s: %s%s" % (addr, ins, ("   ; " + rel) if rel else ""))
print("\n".join(res))
