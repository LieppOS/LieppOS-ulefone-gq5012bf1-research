#!/usr/bin/env python3
"""Section-by-section byte parity of two ELF relocatable modules (read-only).
Usage: section_parity.py <a.ko> <b.ko>"""
import hashlib, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfmini import Elf
a, b = Elf(sys.argv[1]), Elf(sys.argv[2])
names = [s.name for s in a.sections if s.name] 
same = diff = 0
for n in names:
    sa = a.secbyname.get(n); sb = b.secbyname.get(n)
    if sb is None:
        print(f"{n}\tONLY_IN_A"); diff += 1; continue
    ba = a.blob[sa.off:sa.off + sa.size] if sa.type != 8 else b"NOBITS%d" % sa.size
    bb = b.blob[sb.off:sb.off + sb.size] if sb.type != 8 else b"NOBITS%d" % sb.size
    if sa.type == 2 or sa.type == 3 or n in (".note.gnu.build-id",):   # symtab/strtab ordering, build-id
        tag = "SKIP(symtab/strtab/build-id)"
    else:
        tag = "IDENTICAL" if ba == bb else f"DIFF({sa.size} vs {sb.size})"
        same += tag == "IDENTICAL"; diff += tag != "IDENTICAL"
    print(f"{n}\t{tag}")
for s in b.sections:
    if s.name and s.name not in a.secbyname:
        print(f"{s.name}\tONLY_IN_B"); diff += 1
print(f"# {same} identical, {diff} different/missing")
