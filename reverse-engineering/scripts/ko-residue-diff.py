#!/usr/bin/env python3
"""ko-residue-diff.py — stock-source residue axis for two kernel module ELFs.

`ko-pair-parity.py` proves structural/semantic equality (sections, function
bodies, imports, exports, .modinfo, semantic RELA, string tables).  It does NOT
answer the question that separates "structurally equivalent" from "derived from
the same source": whether one side contains evidence that can only come from
compiling ADDITIONAL stock source.  Literal-level evidence is ko-str-refs.py +
ko-literal-census.py; this tool covers the SYMBOL/relocation axis.

Everything is derived from `.symtab` and the RELA stream -- never from a raw
string-table dump.  (A .ko carries TWO SHT_STRTAB sections named `.strtab`, one
per symtab, so "strings present in .strtab" is ambiguous; and `EXPORT_SYMBOL`
leaves no `__kcrctab_<name>` symbol in an lld-linked module, so an export set
built from symbol names alone comes out empty.  Both mistakes produced phantom
residue in earlier revisions of this script, so both are avoided structurally.)

Axes, for A (usually shipped stock) and B (usually the reconstruction), each
reported as shared / A-only / B-only:

  defined FUNC names    every STT_FUNC symbol with a name (the compiled
                        surface: static helpers included, so a stock-only
                        translation unit would show up here).
  export names          the FUNC targets of `.rela__ksymtab*` in tab order --
                        the same derivation ko-pair-parity.py uses.
  external references   names targeted by a relocation whose symbol is
                        SHN_UNDEF, i.e. calls/data references that leave this
                        module.  A rebuild from reconstructed source cannot
                        invent one of these either, so A-only entries would be
                        stock source residue.  Reported family-filtered
                        (--prefix, default mtk_|cmdq_|mbox) AND unfiltered,
                        because an extra stock source file could call a
                        non-family helper too.
  init/exit surface     FUNC symbols living in .init.text/.exit.text plus the
                        `__NNN_*_init()` stubs kbuild materialises in vmlinux
                        objects.  A different set means a different set of
                        module_init()/module_exit() registrations.

Exit status 0 when no residue appears on any axis, 1 otherwise, so the check can
gate a PARTIAL -> DONE move.

usage: ko-residue-diff.py [--prefix mtk_,cmdq_,mbox] [--json OUT.json] A.ko B.ko
"""
import argparse
import json
import re
import struct
import sys

SHT_RELA = 4
STT_FUNC = 2
SHN_UNDEF = 0

INITCALL = re.compile(r"^__\d+_(?:early_|late_)?"
                      r"(?:arch|core|postcore|fs|security|pure|subsys|device)_(?:init|exit)(?:_\d+)?$")
MODULE_FAMILY_PREFIXES_DEFAULT = ("mtk_", "cmdq_", "mbox")


class KO:
    """Minimal ELF64-REL reader; every axis is derived from symtab + RELA."""

    def __init__(self, path):
        self.path = path
        self.b = b = open(path, "rb").read()
        assert b[:4] == b"\x7fELF" and b[4] == 2, f"{path}: need ELF64"
        assert struct.unpack_from("<H", b, 0x10)[0] == 1, f"{path}: need REL"
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x3a)
        shoff = struct.unpack_from("<Q", b, 0x28)[0]
        self.secs = []
        for i in range(shnum):
            o = shoff + i * shentsize
            nm, stype, _fl, _a, off, size, link, info, _al, _e = \
                struct.unpack_from("<IIQQQQIIQQ", b, o)
            self.secs.append(dict(idx=i, name="", type=stype, off=off, size=size,
                                  link=link, info=info))
        sh_base = self.secs[shstrndx]["off"]
        for i, s in enumerate(self.secs):
            s["n"] = self._cstr(b[sh_base:],
                                struct.unpack_from("<I", b, shoff + i * shentsize)[0])
        symtab = [s for s in self.secs if s["type"] == 2]      # SHT_SYMTAB
        self.symbols = []
        for s in symtab:
            base = self.secs[s["link"]]["off"]
            for o in range(s["off"], s["off"] + s["size"], 24):
                st_name, st_info, _o, st_shndx = struct.unpack_from("<IBBH", b, o)
                v, sz = struct.unpack_from("<QQ", b, o + 8)
                self.symbols.append(dict(name=self._cstr(b[base:], st_name),
                                         bind=st_info >> 4, type=st_info & 0xf,
                                         shndx=st_shndx, value=v, size=sz,
                                         sec=self.secs[st_shndx]["n"]
                                         if st_shndx < len(self.secs) else ""))
        self.funcs = {s["name"] for s in self.symbols
                      if s["type"] == STT_FUNC and s["name"]}

    @staticmethod
    def _cstr(blob, off):
        end = blob.find(b"\0", off)
        return blob[off:end].decode("ascii", "replace") if end > 0 else ""

    def sec(self, name):
        for s in self.secs:
            if s["n"] == name:
                return s
        return None

    def has(self, name):
        return any(s["n"] == name for s in self.secs)

    def relocs(self):
        """Yield (applies-to section, r_offset, type, sym index, addend, sym dict)."""
        applies = {s["idx"]: self.secs[s["info"]]["n"] for s in self.secs
                   if s["type"] == SHT_RELA and s["info"] < len(self.secs)}
        for s in self.secs:
            if s["type"] != SHT_RELA or s["idx"] not in applies:
                continue
            for o in range(s["off"], s["off"] + s["size"], 24):
                r_off, r_info, r_add = struct.unpack_from("<QQq", self.b, o)
                idx = r_info >> 32
                sym = self.symbols[idx] if idx < len(self.symbols) else None
                yield applies[s["idx"]], r_off, r_info & 0xFFFFFFFF, idx, r_add, sym

    def exports(self):
        """Export names = FUNC targets of `.rela__ksymtab*`, in tab order."""
        out = set()
        for applies, _o, _t, _i, _a, sym in self.relocs():
            if "ksymtab" in applies and sym is not None and sym["name"]:
                out.add(sym["name"])
        if out:
            return out
        for s in self.symbols:                      # fallback: symbol naming
            n = s["name"]
            for pre in ("__ksymtab_gpl_", "__ksymtab_gpl", "__ksymtab_", "__ksymtab"):
                if n.startswith(pre) and len(n) > len(pre):
                    out.add(n[len(pre):])
                    break
        return out

    def external_refs(self):
        """Names this module references but does not define (SHN_UNDEF symbols)."""
        return {sym["name"] for _a, _o, _t, _i, _ad, sym in self.relocs()
                if sym is not None and sym["shndx"] == SHN_UNDEF and sym["name"]}

    def init_exit(self):
        """Init/exit registration surface actually present in the object."""
        out = set()
        for s in self.symbols:
            if s["type"] == STT_FUNC and s["name"] and \
                    s["sec"] in (".init.text", ".exit.text", ".text"):
                if INITCALL.match(s["name"]) or s["sec"] in (".init.text", ".exit.text"):
                    out.add(f"{s['name']}@{s['sec']}")
        for s in self.symbols:
            if INITCALL.match(s["name"]):
                out.add(s["name"])
        return out


def diff_sets(a, b):
    return dict(shared=sorted(a & b), a_only=sorted(a - b), b_only=sorted(b - a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--prefix", default=",".join(MODULE_FAMILY_PREFIXES_DEFAULT))
    ap.add_argument("--json")
    args = ap.parse_args()
    prefixes = tuple(p for p in args.prefix.split(",") if p)

    A, B = KO(args.a), KO(args.b)
    print(f"A = {A.path}")
    print(f"B = {B.path}")
    print(f"prefixes={prefixes}")
    res = {}

    axes = [
        ("defined FUNC symbols", diff_sets(A.funcs, B.funcs)),
        ("export names", diff_sets(A.exports(), B.exports())),
        ("external refs (all families)",
         diff_sets(A.external_refs(), B.external_refs())),
        ("external refs (family-prefixed)",
         diff_sets({w for w in A.external_refs() if w.startswith(prefixes)},
               {w for w in B.external_refs() if w.startswith(prefixes)})),
        ("init/exit surface", diff_sets(A.init_exit(), B.init_exit())),
    ]
    residue = 0
    for label, d in axes:
        residue += len(d["a_only"]) + len(d["b_only"])
        print(f"\n{label}: shared={len(d['shared'])} "
              f"A-only={len(d['a_only'])} B-only={len(d['b_only'])}"
              f"{' -> NO RESIDUE' if not (d['a_only'] or d['b_only']) else ''}")
        for lbl in ("a_only", "b_only"):
            for n in d[lbl]:
                print(f"    {lbl.upper()}: {n}")
        res[label] = d

    print("\nsections: " + "  ".join(
        f"{t}={len([s for s in k.secs if s['size']])}" for t, k in (("A", A), ("B", B))) +
        f"  .llvm_addrsig: A={A.has('.llvm_addrsig')} B={B.has('.llvm_addrsig')}")
    print("\nverdict:", "no stock-source residue on any residue axis" if not residue
          else f"{residue} residue entries")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(dict(a=A.path, b=B.path, prefixes=list(prefixes), axes=res,
                           residue=residue), fh, indent=1)
        print("wrote", args.json)
    return 1 if residue else 0


if __name__ == "__main__":
    sys.exit(main())
