#!/usr/bin/env python3
"""Function / data-object parity of one stock module vs one rebuilt module.

Functions (every SHF_EXECINSTR section) and data objects (.data/.rodata/.bss/...)
are keyed (section, name, occurrence-in-address-order).  Relocations are
compared symbolically (imported name, defined symbol+offset, string literal
content), so differing symbol-table order or string-pool layout is not a
difference.

Classes
  EXACT       size, bytes, relocations and KCFI type word identical
  EXACT-CODE  identical except B/BL displacements to other functions of the
              same module (layout shift caused by some other function)
  DIFF        anything else (note says what)
  MISSING     only in stock          EXTRA  only in rebuilt

usage: ko_parity.py <stock.ko> <rebuilt.ko> [--tsv f.tsv] [--data-tsv d.tsv] [--label name]
"""
import collections
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "../../scripts")))
from elfmini import Elf  # noqa: E402
import imgsensor_parity as P  # noqa: E402

DATA_SECS = (".data", ".rodata", ".bss", ".data.once", ".rodata.cst16", ".rodata.cst8", ".rodata.cst4",
             ".ref.data", "__param", ".init.data", ".exit.data", ".data..read_mostly", ".data..ro_after_init")


class Norm:
    def __init__(self, e):
        self.e = e

    def target(self, r):
        e = self.e
        s = r.sym
        if s.shndx == 0:
            return f"U:{s.name}{'+%d' % r.addend if r.addend else ''}"
        if s.shndx >= 0xFF00:
            return f"ABS:{s.name}"
        sec = e.sections[s.shndx]
        if s.type in (1, 2) and s.name:
            return f"{keyname(s.name)}+{r.addend}"
        addr = s.value + r.addend
        if sec.flags & 0x20:
            return "S:" + repr(e.cstring_at(s.shndx, addr))
        c = e.containing(s.shndx, addr)
        if c is not None:
            return f"{keyname(c.name)}+{addr - c.value}"
        return f"{sec.name}+?"

    def sig(self, sym):
        out = []
        for r in self.e.relocs.get(sym.shndx, []):
            if sym.value <= r.off < sym.value + max(sym.size, 1):
                out.append((r.off - sym.value, r.tname, self.target(r)))
        return out


LOCAL_SUFFIX = re.compile(r"\.\d+$")


def keyname(n):
    """clang numbers function-local statics (foo.__func___rs.84); the number
    depends on how many such statics preceded it in the TU, so it is not
    identity: compare by name without suffix + occurrence in address order."""
    return LOCAL_SUFFIX.sub("", n) if "." in n else n


def keyed(e, pred):
    cnt = collections.Counter()
    out = {}
    syms = [s for s in e.symbols if pred(s)]
    syms.sort(key=lambda s: (e.sections[s.shndx].name, s.value, s.name))
    for s in syms:
        k = (e.sections[s.shndx].name, keyname(s.name))
        out[(k[0], k[1], cnt[k])] = s
        cnt[k] += 1
    return out


def sbytes(e, s):
    sec = e.sections[s.shndx]
    if sec.type == 8:
        return None
    return e.blob[sec.off + s.value: sec.off + s.value + s.size]


def kcfi_word(e, s):
    sec = e.sections[s.shndx]
    if s.value < 4 or sec.type == 8:
        return None
    return struct.unpack_from("<I", e.blob, sec.off + s.value - 4)[0]


def layout_norm(e, f):
    sec = e.sections[f.shndx]
    relocated = {r.off for r in e.relocs.get(f.shndx, []) if f.value <= r.off < f.value + f.size}
    out = []
    for off in range(f.value, f.value + f.size - 3, 4):
        w = struct.unpack_from("<I", e.blob, sec.off + off)[0]
        if (w >> 26) in (0x25, 0x05) and off not in relocated:
            imm = w & 0x3FFFFFF
            if imm & 0x2000000:
                imm -= 1 << 26
            tgt = off + imm * 4
            if f.value <= tgt < f.value + f.size:
                out.append(("b", w >> 26, tgt - f.value))
            else:
                c = e.containing(f.shndx, tgt)
                out.append(("b", w >> 26, (c.name, tgt - c.value) if c else "?"))
        else:
            out.append(w)
    return out


def compare(a, b, sa, sb, na, nb, func):
    notes = []
    if sa.size != sb.size:
        notes.append(f"size {sa.size}/{sb.size}")
    ba, bb = sbytes(a, sa), sbytes(b, sb)
    be = ba == bb
    re_ = na.sig(sa) == nb.sig(sb)
    ke = True
    if func:
        ke = kcfi_word(a, sa) == kcfi_word(b, sb)
    if be and re_ and ke and sa.size == sb.size:
        return "EXACT", ""
    if func and sa.size == sb.size and re_ and layout_norm(a, sa) == layout_norm(b, sb):
        return ("EXACT-CODE", "branch displacement only" + ("" if ke else "; preceding KCFI word"))
    if not be:
        notes.append("bytes")
    if not re_:
        ra, rb = na.sig(sa), nb.sig(sb)
        notes.append(f"relocs({len(ra)}/{len(rb)})")
    if func and not ke:
        notes.append("kcfi")
    return "DIFF", ",".join(notes)


def run(stock, reb, tsv=None, dtsv=None, label=None):
    a, b = Elf(stock), Elf(reb)
    na, nb = Norm(a), Norm(b)
    isf = lambda e: (lambda s: s.type == 2 and 0 < s.shndx < 0xFF00 and e.sections[s.shndx].flags & 4)  # noqa
    isd = lambda e: (lambda s: s.type == 1 and 0 < s.shndx < 0xFF00 and e.sections[s.shndx].name in DATA_SECS)  # noqa
    res = {}
    for kind, pred in (("func", isf), ("data", isd)):
        A, B = keyed(a, pred(a)), keyed(b, pred(b))
        rows = []
        for k in sorted(set(A) | set(B), key=lambda k: (k[0], A[k].value if k in A else 1 << 40, k[1], k[2])):
            sa, sb = A.get(k), B.get(k)
            if sa and sb:
                cls, note = compare(a, b, sa, sb, na, nb, kind == "func")
            else:
                cls, note = ("MISSING", "") if sa else ("EXTRA", "")
            rows.append((k[0], k[1], k[2], sa.size if sa else "-", sb.size if sb else "-", cls, note))
        res[kind] = rows
        out = tsv if kind == "func" else dtsv
        if out:
            with open(out, "w") as f:
                f.write("section\tname\tocc\tstock_size\trebuilt_size\tclass\tnote\n")
                for r in rows:
                    f.write("\t".join(map(str, r)) + "\n")
    return res


def summary(res):
    out = {}
    for kind, rows in res.items():
        c = collections.Counter(r[5] for r in rows)
        stock_n = sum(1 for r in rows if r[5] != "EXTRA")
        out[kind] = (stock_n, c)
    return out


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None  # noqa
    stock, reb = args[0], args[1]
    res = run(stock, reb, opt("--tsv"), opt("--data-tsv"))
    s = summary(res)
    lab = opt("--label") or os.path.basename(stock)
    f_n, fc = s["func"]
    d_n, dc = s["data"]
    print(f"{lab}\tfuncs {fc['EXACT']}/{f_n} exact (+{fc['EXACT-CODE']} exact-code, {fc['DIFF']} diff, "
          f"{fc['MISSING']} missing, {fc['EXTRA']} extra)\tdata {dc['EXACT']}/{d_n} exact "
          f"({dc['DIFF']} diff, {dc['MISSING']} missing, {dc['EXTRA']} extra)")


if __name__ == "__main__":
    main()
