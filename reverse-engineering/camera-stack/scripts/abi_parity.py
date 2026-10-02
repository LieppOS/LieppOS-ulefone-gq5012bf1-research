#!/usr/bin/env python3
"""Whole-module ABI / section parity of stock vs rebuilt imgsensor.ko.

Unlike section_parity.py (raw bytes), this normalises everything that only
depends on symbol-table *ordering*:
  * PROGBITS sections: byte compare; for .text/.data the differing 4-byte
    words are attributed to the containing function/object;
  * RELA sections: compared as sorted (offset, type, target) where target is
    the symbol name (or section-name+absolute-addend for section symbols);
  * .symtab: compared as a multiset of (name, type, bind, section, value, size);
  * .modinfo: compared as key=value multiset;
  * __versions (modversions CRCs) and __ksymtab/__kcrctab: byte compare;
  * KCFI: the 4-byte type-hash word preceding every FUNC symbol.
Sections present only on one side are listed (debug sections are reported
separately since the parity build keeps DWARF for tooling).

usage: abi_parity.py <stock.ko> <rebuilt.ko> [--tsv out.tsv]
"""
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfmini import Elf  # noqa: E402


def rel_key(e, r):
    s = r.sym
    if s.type == 3:  # section symbol
        return (r.off, r.rtype, f"{e.sections[s.shndx].name}+{s.value + r.addend:#x}")
    return (r.off, r.rtype, f"{s.name}+{r.addend:#x}")


def symset(e):
    c = collections.Counter()
    for s in e.symbols[1:]:
        if s.type in (3, 4):
            continue
        sec = e.sections[s.shndx].name if 0 < s.shndx < 0xFF00 else str(s.shndx)
        c[(s.name, s.type, s.bind, sec, s.value, s.size)] += 1
    return c


def modinfo(e):
    s = e.secbyname.get(".modinfo")
    if not s:
        return collections.Counter()
    return collections.Counter(x.decode() for x in e.blob[s.off:s.off + s.size].split(b"\0") if x)


def kcfi(e):
    t = e.secbyname[".text"]
    out = {}
    for s in e.symbols:
        if s.type == 2 and s.shndx == t.idx and s.value >= 4:
            out[(s.name, s.value)] = struct.unpack_from("<I", e.blob, t.off + s.value - 4)[0]
    return out


def main():
    a, b = Elf(sys.argv[1]), Elf(sys.argv[2])
    rows = []
    dbg = lambda n: n.startswith((".debug", ".rela.debug"))  # noqa: E731
    for sa in a.sections:
        n = sa.name
        if not n or sa.type in (2, 3) or n == ".note.gnu.build-id":
            continue
        sb = b.secbyname.get(n)
        if sb is None:
            rows.append((n, "ONLY_IN_STOCK", ""))
            continue
        if sa.type == 4:  # RELA
            ra = sorted(rel_key(a, r) for r in a.relocs.get(sa.info, []) if True)
            rb = sorted(rel_key(b, r) for r in b.relocs.get(sb.info, []))
            # relocs dict is keyed by target section; multiple RELA sections for
            # one target do not occur in these modules
            if ra == rb:
                rows.append((n, "IDENTICAL(normalised)", f"{len(ra)} relocs"))
            else:
                sa_, sb_ = set(ra), set(rb)
                da = sorted(sa_ - sb_)[:5]
                db = sorted(sb_ - sa_)[:5]
                rows.append((n, "DIFF", f"{len(sa_ - sb_)} stock-only, {len(sb_ - sa_)} rebuilt-only; "
                             f"e.g. stock {da[:2]} rebuilt {db[:2]}"))
            continue
        ba = a.blob[sa.off:sa.off + sa.size] if sa.type != 8 else None
        bb = b.blob[sb.off:sb.off + sb.size] if sb.type != 8 else None
        if sa.type == 8 or sb.type == 8:
            ok = sa.size == sb.size and sa.type == sb.type
            rows.append((n, "IDENTICAL" if ok else "DIFF", f"NOBITS {sa.size}/{sb.size}"))
            continue
        if ba == bb:
            rows.append((n, "IDENTICAL", f"{sa.size} bytes"))
            continue
        note = f"size {sa.size}/{sb.size}"
        if sa.size == sb.size:
            words = [i for i in range(0, sa.size - 3, 4) if ba[i:i + 4] != bb[i:i + 4]]
            owners = collections.Counter()
            for w in words:
                c = a.containing(sa.idx, w)
                owners[c.name if c else f"@{w:#x}"] += 1
            note += f"; {len(words)} differing words in " + ", ".join(f"{k}({v})" for k, v in owners.most_common(8))
        rows.append((n, "DIFF", note))
    for sb in b.sections:
        if sb.name and sb.name not in a.secbyname:
            rows.append((sb.name, "ONLY_IN_REBUILT" + ("(debug)" if dbg(sb.name) else ""), ""))

    # symbol table
    A, B = symset(a), symset(b)
    rows.append((".symtab", "IDENTICAL(set)" if A == B else "DIFF",
                 f"{sum(A.values())}/{sum(B.values())} symbols; stock-only {sorted(A - B)[:3]} rebuilt-only {sorted(B - A)[:3]}"
                 if A != B else f"{sum(A.values())} symbols"))
    MA, MB = modinfo(a), modinfo(b)
    rows.append((".modinfo(kv)", "IDENTICAL(set)" if MA == MB else "DIFF",
                 "" if MA == MB else f"stock-only {sorted(MA - MB)} rebuilt-only {sorted(MB - MA)}"))
    KA, KB = kcfi(a), kcfi(b)
    kd = [k for k in KA if k in KB and KA[k] != KB[k]]
    rows.append(("KCFI type words", "IDENTICAL" if not kd and KA.keys() == KB.keys() else "DIFF",
                 f"{len(KA)} funcs; {len(kd)} differ {kd[:5]}"))

    w = max(len(r[0]) for r in rows)
    for r in rows:
        print(f"{r[0]:{w}s}  {r[1]:28s} {r[2]}")
    cnt = collections.Counter(r[1].split("(")[0] for r in rows)
    print("#", dict(cnt))
    if "--tsv" in sys.argv:
        with open(sys.argv[sys.argv.index("--tsv") + 1], "w") as f:
            f.write("section\tstatus\tnote\n")
            for r in rows:
                f.write("\t".join(r) + "\n")


if __name__ == "__main__":
    main()
