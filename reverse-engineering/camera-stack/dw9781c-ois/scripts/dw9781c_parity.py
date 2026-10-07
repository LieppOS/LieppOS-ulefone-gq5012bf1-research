#!/usr/bin/env python3
"""Whole-file parity of stock vendor_dlkm dw9781c.ko vs the B1/B2 rebuild.

Checks, in order:
  1. B1 == B2 byte-for-byte (deterministic build);
  2. stock vs B1(stripped): file size, every differing byte attributed to a
     section -> the ONLY allowed residual is the 20-byte GNU build-id
     descriptor in .note.gnu.build-id;
  3. structured parity (independent of 2): functions (name/size/bytes),
     data objects, KCFI type words, imports (UND symbols), exports,
     __versions (modversion CRC + name), relocations per section (offset,
     type, symbol, addend), strings (.rodata.str1.1), .modinfo key/values
     (incl. vermagic, srcversion if present), section headers.

usage: dw9781c_parity.py <stock.ko> <B1 dir> <B2 dir> [--tsv out.tsv]
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


def section_of(e, off):
    for s in e.sections:
        if s.type != 8 and s.size and s.off <= off < s.off + s.size:
            return s.name
    return "<elf/section headers>"


def funcs(e):
    return {s.name: (s.size, e.bytes_of(s)) for s in e.symbols if s.type == 2 and s.shndx and s.shndx < 0xFF00}


def objs(e):
    return {(s.name, e.sections[s.shndx].name): (s.size, e.bytes_of(s)) for s in e.symbols
            if s.type == 1 and 0 < s.shndx < 0xFF00}


def kcfi(e):
    out = {}
    for s in e.symbols:
        if s.type == 2 and 0 < s.shndx < 0xFF00 and s.value >= 4:
            sec = e.sections[s.shndx]
            out[s.name] = struct.unpack_from("<I", e.blob, sec.off + s.value - 4)[0]
    return out


def imports(e):
    return sorted({s.name for s in e.symbols if s.shndx == 0 and s.name})


def exports(e):
    return sorted(s.name[len("__ksymtab_"):] for s in e.symbols if s.name.startswith("__ksymtab_"))


def versions(e):
    s = e.secbyname.get("__versions")
    out = []
    if s:
        for i in range(0, s.size, 64):
            crc, = struct.unpack_from("<Q", e.blob, s.off + i)
            name = e.blob[s.off + i + 8:s.off + i + 64].split(b"\0")[0].decode()
            out.append((name, crc & 0xFFFFFFFF))
    return out


def relocs(e):
    out = collections.Counter()
    for tgt, lst in e.relocs.items():
        tn = e.sections[tgt].name
        for r in lst:
            s = r.sym
            sym = f"{e.sections[s.shndx].name}+{s.value + r.addend:#x}" if s.type == 3 else f"{s.name}+{r.addend:#x}"
            out[(tn, r.off, r.rtype, sym)] += 1
    return out


def strings(e):
    s = e.secbyname.get(".rodata.str1.1")
    return [x for x in e.blob[s.off:s.off + s.size].split(b"\0") if x] if s else []


def modinfo(e):
    s = e.secbyname[".modinfo"]
    return [x.decode() for x in e.blob[s.off:s.off + s.size].split(b"\0") if x]


def shdrs(e):
    return [(s.name, s.type, s.flags, s.size, s.entsize) for s in e.sections]


def main():
    stock = sys.argv[1]
    b1d, b2d = sys.argv[2], sys.argv[3]
    # 1. determinism
    for f in ("dw9781c.o", "dw9781c.ko", "dw9781c.stripped.ko"):
        x = open(os.path.join(b1d, f), "rb").read()
        y = open(os.path.join(b2d, f), "rb").read()
        rec(f"B1==B2 {f}", "IDENTICAL" if x == y else "DIFF", f"{len(x)} bytes")
    rb = os.path.join(b1d, "dw9781c.stripped.ko")
    A, B = Elf(stock), Elf(rb)
    a, b = A.blob, B.blob
    # 2. whole-file
    rec("file size", "IDENTICAL" if len(a) == len(b) else "DIFF", f"{len(a)}/{len(b)}")
    diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
    where = collections.Counter(section_of(A, i) for i in diff)
    bid = A.secbyname[".note.gnu.build-id"]
    desc = range(bid.off + 16, bid.off + 16 + 20)
    only_bid = all(i in desc for i in diff)
    rec("differing bytes", "BUILD-ID ONLY" if only_bid else "DIFF", f"{len(diff)} bytes in {dict(where)}")
    masked_a = bytearray(a); masked_b = bytearray(b)
    for i in desc:
        masked_a[i] = masked_b[i] = 0
    rec("whole file with build-id masked", "IDENTICAL" if masked_a == masked_b else "DIFF")
    # 3. structured
    FA, FB = funcs(A), funcs(B)
    same = [n for n in FA if n in FB and FA[n] == FB[n]]
    rec("functions (name,size,bytes)", "IDENTICAL" if len(same) == len(FA) == len(FB) else "DIFF",
        f"{len(same)}/{len(FA)} stock, {len(FB)} rebuilt")
    OA, OB = objs(A), objs(B)
    same = [n for n in OA if n in OB and OA[n] == OB[n]]
    rec("data objects (name,section,size,bytes)", "IDENTICAL" if len(same) == len(OA) == len(OB) else "DIFF",
        f"{len(same)}/{len(OA)} stock, {len(OB)} rebuilt")
    KA, KB = kcfi(A), kcfi(B)
    rec("KCFI type words", "IDENTICAL" if KA == KB else "DIFF", f"{sum(KA[k] == KB.get(k) for k in KA)}/{len(KA)}")
    IA, IB = imports(A), imports(B)
    rec("imports (UND)", "IDENTICAL" if IA == IB else "DIFF", f"{len(IA)}/{len(IB)}")
    EA, EB = exports(A), exports(B)
    rec("exports (__ksymtab)", "IDENTICAL" if EA == EB else "DIFF", f"{len(EA)}/{len(EB)}")
    VA, VB = versions(A), versions(B)
    rec("__versions (name,CRC)", "IDENTICAL" if VA == VB else "DIFF", f"{len(VA)}/{len(VB)}")
    RA, RB = relocs(A), relocs(B)
    rec("relocations (sec,off,type,sym+addend)", "IDENTICAL" if RA == RB else "DIFF",
        f"{sum(RA.values())}/{sum(RB.values())}")
    SA, SB = strings(A), strings(B)
    rec("strings (.rodata.str1.1)", "IDENTICAL" if SA == SB else "DIFF", f"{len(SA)}/{len(SB)}")
    MA, MB = modinfo(A), modinfo(B)
    rec(".modinfo", "IDENTICAL" if MA == MB else "DIFF", "; ".join(MA))
    has_src = any(m.startswith("srcversion=") for m in MA)
    rec("srcversion", "PRESENT" if has_src else "ABSENT(both)" if not any(m.startswith("srcversion=") for m in MB) else "DIFF")
    rec("section headers (name,type,flags,size,entsize)", "IDENTICAL" if shdrs(A) == shdrs(B) else "DIFF",
        f"{len(A.sections)}/{len(B.sections)}")
    symA = [(s.name, s.type, s.bind, s.shndx, s.value, s.size) for s in A.symbols]
    symB = [(s.name, s.type, s.bind, s.shndx, s.value, s.size) for s in B.symbols]
    rec("symbol table (ordered)", "IDENTICAL" if symA == symB else "DIFF", f"{len(symA)}/{len(symB)}")

    w = max(len(r[0]) for r in rows)
    for r in rows:
        print(f"{r[0]:{w}s}  {r[1]:16s} {r[2]}")
    if "--tsv" in sys.argv:
        with open(sys.argv[sys.argv.index("--tsv") + 1], "w") as f:
            f.write("check\tstatus\tdetail\n")
            for r in rows:
                f.write("\t".join(r) + "\n")
    bad = [r for r in rows if r[1] == "DIFF"]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
