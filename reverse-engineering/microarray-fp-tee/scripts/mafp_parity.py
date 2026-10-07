#!/usr/bin/env python3
"""microarray_fp_tee.ko parity: stock vs rebuild.

usage: mafp_parity.py <stock.ko> <rebuild.ko> [--diff FUNC] [--tsv out]
Per function: size, raw bytes, relocation (offset,type,target) list, KCFI word.
Data objects: size, bytes (NOBITS zero-filled), relocations.
Module: __versions (order+CRC), .modinfo minus vermagic/srcversion, strings, imports, exports.
"""
import os
import struct
import subprocess
import sys

sys.path.insert(0, os.environ.get("ELFMINI", os.path.dirname(os.path.abspath(__file__))))
from elfmini import Elf  # noqa: E402

OBJDUMP = os.environ.get("OBJDUMP", "llvm-objdump")


def body(e, s):
    return bytes(s.size) if e.sections[s.shndx].type == 8 else e.bytes_of(s)


def rels(e, s):
    out = []
    for r in e.relocs_in(s):
        t, o = e.target(r)
        out.append((r.off - s.value, r.rtype, t.name or e.sections[t.shndx].name, o))
    return out


def kcfi(e, s):
    sec = e.sections[s.shndx]
    return struct.unpack_from("<I", e.blob, sec.off + s.value - 4)[0] if s.value >= 4 else None


def defined(e, t):
    return {(s.name): s for s in e.symbols if s.type == t and s.size and 0 < s.shndx < 0xFF00}


def versions(e):
    v = e.secbyname["__versions"]
    out = []
    for i in range(v.size // 64):
        crc, = struct.unpack_from("<Q", e.blob, v.off + 64 * i)
        out.append((e.blob[v.off + 64 * i + 8:v.off + 64 * i + 64].split(b"\0")[0].decode(), crc))
    return out


def modinfo(e):
    m = e.secbyname[".modinfo"]
    return [x.decode() for x in e.blob[m.off:m.off + m.size].split(b"\0") if x]


def main():
    A, B = Elf(sys.argv[1]), Elf(sys.argv[2])
    rows = []
    FA, FB = defined(A, 2), defined(B, 2)
    nf = 0
    for k, a in sorted(FA.items(), key=lambda kv: (kv[1].shndx, kv[1].value)):
        b = FB.get(k)
        if b is None:
            rows.append(("FUNC", k, a.size, "-", "MISSING"))
            continue
        bb, rr, kk = body(A, a) == body(B, b), rels(A, a) == rels(B, b), kcfi(A, a) == kcfi(B, b)
        ok = a.size == b.size and bb and rr and kk
        nf += ok
        rows.append(("FUNC", k, a.size, b.size, "IDENTICAL" if ok else
                     f"DIFF(bytes={'=' if bb else '!'} relocs={'=' if rr else '!'} kcfi={'=' if kk else '!'})"))
    OA, OB = defined(A, 1), defined(B, 1)
    no = 0
    for k, a in sorted(OA.items()):
        b = OB.get(k)
        ok = b is not None and a.size == b.size and body(A, a) == body(B, b) and \
            [x[:2] + x[2:] for x in rels(A, a)] == [x[:2] + x[2:] for x in rels(B, b)]
        no += ok
        rows.append(("OBJECT", k, a.size, b.size if b else "-", "IDENTICAL" if ok else "DIFF"))
    va, vb = versions(A), versions(B)
    ma = [m for m in modinfo(A) if not m.startswith(("vermagic=", "srcversion="))]
    mb = [m for m in modinfo(B) if not m.startswith(("vermagic=", "srcversion="))]
    print(f"functions identical: {nf}/{len(FA)} (rebuild defines {len(FB)})")
    print(f"data objects identical: {no}/{len(OA)} (rebuild defines {len(OB)})")
    print(f"__versions: {'IDENTICAL' if va == vb else 'DIFF'} ({len(va)}/{len(vb)} entries)")
    print(f".modinfo (excl. vermagic/srcversion): {'IDENTICAL' if ma == mb else 'DIFF'}")
    for n in (".rodata.str1.1", ".rodata.str1.8", ".rodata"):
        sa, sb = A.secbyname.get(n), B.secbyname.get(n)
        if sa or sb:
            same = sa and sb and A.blob[sa.off:sa.off + sa.size] == B.blob[sb.off:sb.off + sb.size]
            print(f"section {n}: {'IDENTICAL' if same else 'DIFF'} ({sa.size if sa else '-'}/{sb.size if sb else '-'})")
    # whole-file comparison
    fa, fb = open(sys.argv[1], "rb").read(), open(sys.argv[2], "rb").read()
    bysec = {}
    if len(fa) == len(fb):
        for i in range(len(fa)):
            if fa[i] != fb[i]:
                n = next((x.name for x in A.sections if x.type != 8 and x.off <= i < x.off + x.size), "<ELF/section headers>")
                bysec[n] = bysec.get(n, 0) + 1
    print(f"file size: stock {len(fa)} / rebuild {len(fb)}; differing bytes: "
          f"{sum(bysec.values()) if len(fa) == len(fb) else 'n/a (size differs)'} {bysec}")
    print(f"section headers: {'IDENTICAL' if [(x.name, x.type, x.size, x.off) for x in A.sections] == [(x.name, x.type, x.size, x.off) for x in B.sections] else 'DIFF'} ({len(A.sections)}/{len(B.sections)})")
    ka = [(s.name, s.type, s.bind, s.size) for s in A.symbols]
    kb = [(s.name, s.type, s.bind, s.size) for s in B.symbols]
    print(f"symbol table (ordered name/type/bind/size): {'IDENTICAL' if ka == kb else 'DIFF'} ({len(ka)}/{len(kb)})")
    for r in rows:
        print("  {:6s} {:28s} {:>5} {:>5}  {}".format(*r))
    if "--tsv" in sys.argv:
        with open(sys.argv[sys.argv.index("--tsv") + 1], "w") as f:
            f.write("kind\tsymbol\tstock_size\trebuild_size\tverdict\n")
            for r in rows:
                f.write("\t".join(map(str, r)) + "\n")
    if "--diff" in sys.argv:
        fn = sys.argv[sys.argv.index("--diff") + 1]
        for e, s, tag in ((A, FA[fn], "stock"), (B, FB[fn], "rebuild")):
            sec = e.sections[s.shndx].name
            out = subprocess.run([OBJDUMP, "-dr", "--no-show-raw-insn", f"--section={sec}",
                                  f"--disassemble-symbols={fn}", e.path], capture_output=True, text=True).stdout
            open(f"/tmp/mafp-{fn}-{tag}.s", "w").write(out)
        print(f"wrote /tmp/mafp-{fn}-stock.s /tmp/mafp-{fn}-rebuild.s")
    sys.exit(0 if nf == len(FA) and no == len(OA) and va == vb and ma == mb else 1)


if __name__ == "__main__":
    main()
