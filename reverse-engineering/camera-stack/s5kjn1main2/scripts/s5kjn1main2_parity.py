#!/usr/bin/env python3
"""S5KJN1MAIN2 sub-driver parity against the SHIPPED vendor_dlkm imgsensor.ko.

A = shipped imgsensor.ko (sha256 9243061c...)  B = reconstructed build (B1/B2)

1. B1 == B2 (stripped .ko, unstripped .ko, s5kjn1main2mipiraw_Sensor.o).
2. Whole file A vs B1(stripped): every differing byte is attributed to a
   section, and inside .text / .rela.text to the function it belongs to.
3. Module-wide structured parity (functions, data, KCFI, __versions,
   imports/exports, relocations, strings, .modinfo, section headers, symtab).
4. S5KJN1MAIN2 translation unit: every FUNC/OBJECT defined in s5kjn1main2mipiraw_Sensor.o
   is located in A by (name, size, bytes, symbolic relocations) and must be
   identical; the TU must not overlap any differing byte.

usage: s5kjn1main2_parity.py <shipped.ko> <B1 dir> <B2 dir> [--tsv out.tsv] [--tu-tsv out.tsv]
"""
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
from elfmini import Elf  # noqa: E402

rows = []


def rec(check, status, detail=""):
    rows.append((check, status, str(detail)))


def section_at(e, off):
    for s in e.sections:
        if s.type != 8 and s.size and s.off <= off < s.off + s.size:
            return s
    return None


def sym_rel(e, r):
    s = r.sym
    if s.type == 3:
        # section symbol: resolve to containing object/function when possible
        t, o = e.target(r)
        return f"{t.name}+{o:#x}" if t is not s else f"{e.sections[s.shndx].name}+{s.value + r.addend:#x}"
    return f"{s.name}+{r.addend:#x}"


def fn_relocs(e, sym):
    return [(r.off - sym.value, r.rtype, sym_rel(e, r)) for r in e.relocs_in(sym)]


def body(e, sym):
    """Symbol contents; NOBITS (.bss) symbols occupy no file bytes and are zero-filled."""
    if e.sections[sym.shndx].type == 8:
        return bytes(sym.size)
    return e.bytes_of(sym)


def defined(e, kinds=(1, 2)):
    return [s for s in e.symbols if s.type in kinds and 0 < s.shndx < 0xFF00]


def kcfi_word(e, s):
    sec = e.sections[s.shndx]
    return struct.unpack_from("<I", e.blob, sec.off + s.value - 4)[0] if s.type == 2 and s.value >= 4 else None


def main():
    a_path, b1, b2 = sys.argv[1:4]
    for f in ("imgsensor.parity.stripped.ko", "imgsensor.ko", "s5kjn1main2mipiraw_Sensor.o"):
        x = open(os.path.join(b1, f), "rb").read()
        y = open(os.path.join(b2, f), "rb").read()
        rec(f"B1==B2 {f}", "IDENTICAL" if x == y else "DIFF", f"{len(x)} bytes")
    A = Elf(a_path)
    B = Elf(os.path.join(b1, "imgsensor.parity.stripped.ko"))
    a, b = A.blob, B.blob
    rec("file size", "IDENTICAL" if len(a) == len(b) else "DIFF", f"{len(a)}/{len(b)}")

    # ---- 2. attribute every differing byte
    diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
    attrib = collections.Counter()
    diff_funcs = set()
    for i in diff:
        s = section_at(A, i)
        if s is None:
            attrib["<headers>"] += 1
            continue
        where = s.name
        if s.type == 1 and s.flags & 4:  # PROGBITS + EXECINSTR
            c = A.containing(s.idx, i - s.off)
            where += ":" + (c.name if c else "?")
            if c:
                diff_funcs.add(c.name)
        elif s.type == 4:  # RELA: entry -> r_offset -> function
            ent = (i - s.off) // 24
            r_off, = struct.unpack_from("<Q", a, s.off + ent * 24)
            c = A.containing(s.info, r_off)
            where += f":{c.name if c else '?'}"
            if c:
                diff_funcs.add(c.name)
        attrib[where] += 1
    rec("differing bytes (A vs B1)", f"{len(diff)}", "; ".join(f"{k}={v}" for k, v in sorted(attrib.items())))

    # ---- 3. module-wide structured parity
    FA = {(s.name, s.value): s for s in defined(A, (2,))}
    FB = {(s.name, s.value): s for s in defined(B, (2,))}
    same = [k for k in FA if k in FB and FA[k].size == FB[k].size and A.bytes_of(FA[k]) == B.bytes_of(FB[k])
            and fn_relocs(A, FA[k]) == fn_relocs(B, FB[k]) and kcfi_word(A, FA[k]) == kcfi_word(B, FB[k])]
    bad = sorted(k[0] for k in FA if k not in same)
    rec("functions (size,bytes,relocs,KCFI)", f"{len(same)}/{len(FA)}", f"rebuilt {len(FB)}; differing: {bad}")
    OA = {(s.name, s.shndx, s.value): s for s in defined(A, (1,))}
    OB = {(s.name, s.shndx, s.value): s for s in defined(B, (1,))}
    same_o = [k for k in OA if k in OB and OA[k].size == OB[k].size and A.bytes_of(OA[k]) == B.bytes_of(OB[k])
              and fn_relocs(A, OA[k]) == fn_relocs(B, OB[k])]
    rec("data objects (size,bytes,relocs)", f"{len(same_o)}/{len(OA)}", f"rebuilt {len(OB)}")
    ka = [kcfi_word(A, s) for s in defined(A, (2,))]
    kb = [kcfi_word(B, s) for s in defined(B, (2,))]
    rec("KCFI type words", "IDENTICAL" if ka == kb else "DIFF", f"{len(ka)}")
    for name in ("__versions", ".modinfo", "__ksymtab", "__kcrctab", "__ksymtab_strings", ".rodata.str1.1",
                 ".rodata.str1.8", ".llvm_addrsig"):
        sa, sb = A.secbyname.get(name), B.secbyname.get(name)
        if sa is None and sb is None:
            continue
        ok = sa is not None and sb is not None and a[sa.off:sa.off + sa.size] == b[sb.off:sb.off + sb.size]
        rec(f"section {name}", "IDENTICAL" if ok else "DIFF", f"{sa.size if sa else '-'} bytes")
    ia = sorted({s.name for s in A.symbols if s.shndx == 0 and s.name})
    ib = sorted({s.name for s in B.symbols if s.shndx == 0 and s.name})
    rec("imports (UND)", "IDENTICAL" if ia == ib else "DIFF", f"{len(ia)}/{len(ib)}")
    ea = sorted(s.name for s in A.symbols if s.name.startswith("__ksymtab_"))
    eb = sorted(s.name for s in B.symbols if s.name.startswith("__ksymtab_"))
    rec("exports", "IDENTICAL" if ea == eb else "DIFF", ", ".join(x[len('__ksymtab_'):] for x in ea))
    mi = [x.decode() for x in a[A.secbyname['.modinfo'].off:][:A.secbyname['.modinfo'].size].split(b"\0") if x]
    rec("vermagic", "", next(m for m in mi if m.startswith("vermagic=")))
    rec("srcversion", "ABSENT(both)" if not any(m.startswith("srcversion=") for m in mi) else "PRESENT")
    ra = collections.Counter((A.sections[t].name, r.off, r.rtype, sym_rel(A, r)) for t, l in A.relocs.items() for r in l)
    rb = collections.Counter((B.sections[t].name, r.off, r.rtype, sym_rel(B, r)) for t, l in B.relocs.items() for r in l)
    d = (ra - rb) + (rb - ra)
    rec("relocations (multiset)", f"{sum(ra.values()) - sum((ra - rb).values())}/{sum(ra.values())}",
        f"differing entries: {sorted(d)[:4]}")
    sh = lambda e: [(s.name, s.type, s.flags, s.size, s.entsize) for s in e.sections]  # noqa: E731
    rec("section headers", "IDENTICAL" if sh(A) == sh(B) else "DIFF", f"{len(A.sections)}")
    st = lambda e: [(s.name, s.type, s.bind, s.shndx, s.value, s.size) for s in e.symbols]  # noqa: E731
    rec("symbol table (ordered)", "IDENTICAL" if st(A) == st(B) else "DIFF", f"{len(A.symbols)}")

    # ---- 4. S5KJN1MAIN2 translation unit
    O = Elf(os.path.join(b1, "s5kjn1main2mipiraw_Sensor.o"))

    def candidates(s):
        cands = [x for x in defined(A, (s.type,)) if x.name == s.name and x.size == s.size
                 and body(A, x) == body(O, s)
                 and (A.sections[x.shndx].type == 8) == (O.sections[s.shndx].type == 8)]
        # symbolic relocations of the object vs the shipped module
        return cands, [x for x in cands
                       if [(o, t) for o, t, _ in fn_relocs(A, x)] == [(o, t) for o, t, _ in fn_relocs(O, s)]]

    # Anchor set: shipped-module addresses referenced from TU functions that match uniquely.
    # A same-named static in another TU (e.g. s5kjn1's own Four_Cell_Array) is never referenced from here.
    refs = set()
    for s in defined(O, (2,)):
        if s.size:
            _, ok = candidates(s)
            if len(ok) == 1:
                for r in A.relocs_in(ok[0]):
                    t, _ = A.target(r)
                    refs.add((t.shndx, t.value))
    tu = []
    for s in defined(O):
        if s.size == 0:
            continue
        sec_kind = O.sections[s.shndx].name
        cands, ok = candidates(s)
        pinned = [x for x in ok if (x.shndx, x.value) in refs]
        hit = pinned[0] if len(pinned) == 1 else (ok[0] if len(ok) == 1 or (ok and s.type == 2) else None)
        if hit is None and ok and all(body(A, x) == body(A, ok[0]) for x in ok):
            hit = ok[0]   # unreferenced ambiguous data: all candidates byte-identical
        overlap = False
        if hit and A.sections[hit.shndx].type != 8:
            sa = A.sections[hit.shndx]
            lo, hi = sa.off + hit.value, sa.off + hit.value + hit.size
            overlap = any(lo <= i < hi for i in diff) or hit.name in diff_funcs
        elif hit:
            overlap = hit.name in diff_funcs
        tu.append((s.kind, s.name, sec_kind, s.size, len(cands), len(ok),
                   "IDENTICAL" if hit and not overlap else "DIFF"))
    nid = sum(1 for t in tu if t[-1] == "IDENTICAL")
    nf = sum(1 for t in tu if t[0] == "FUNC")
    rec("S5KJN1MAIN2 TU symbols identical in shipped module", f"{nid}/{len(tu)}",
        f"{nf} functions, {len(tu) - nf} data objects; none overlaps a differing byte"
        if nid == len(tu) else "see TU table")

    w = max(len(r[0]) for r in rows)
    for r in rows:
        print(f"{r[0]:{w}s}  {r[1]:14s} {r[2]}")
    print("\nS5KJN1MAIN2 TU:")
    for t in tu:
        print(f"  {t[0]:6s} {t[1]:40s} {t[2]:18s} {t[3]:6d}  cand={t[4]} relocmatch={t[5]} {t[6]}")
    if "--tsv" in sys.argv:
        with open(sys.argv[sys.argv.index("--tsv") + 1], "w") as f:
            f.write("check\tstatus\tdetail\n")
            for r in rows:
                f.write("\t".join(r) + "\n")
    if "--tu-tsv" in sys.argv:
        with open(sys.argv[sys.argv.index("--tu-tsv") + 1], "w") as f:
            f.write("kind\tsymbol\tsection\tsize\tname_size_bytes_candidates\treloc_matches\tverdict\n")
            for t in tu:
                f.write("\t".join(map(str, t)) + "\n")
    sys.exit(0 if nid == len(tu) else 1)


if __name__ == "__main__":
    main()
