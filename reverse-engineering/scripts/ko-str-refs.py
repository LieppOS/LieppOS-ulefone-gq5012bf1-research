#!/usr/bin/env python3
"""ko-str-refs.py — trace every string literal of a kernel module to its referrer.

Why not disassembly: a .ko is produced by `ld -r`, so EVERY sh_addr is 0 and
ADRP page arithmetic cannot cross a section boundary.  The reference graph has
to come from the RELA stream instead, which survives the relocatable link.

For each side (A = shipped stock, B = reconstruction) this builds, per
literal-bearing section, the map

    literal byte offset -> [referencing symbol+off, ...]

by walking every `.rela<code>` section:

  * a reloc whose TARGET symbol is a STT_FUNC/STT_OBJECT symbol inside a code
    section is an outbound call/data reference; the r_offset is mapped back to
    the function containing it -> that is the referrer;
  * a reloc whose TARGET is a section symbol (or an unnamed local symbol) whose
    section is a literal section gives the exact literal byte offset in
    r_addend;
  * ADR_PREL_PG_HI21 alone is page-granular ("page"); the LO12 accessors
    (ADD_ABS_LO12_NC, LDST{8,16,32,64,128}_ABS_LO12_NC), PREL32/64 and
    ABS32/64 identify the exact byte ("exact").

Literals are compared by CONTENT (offsets legitimately differ between builds),
and reported as shared / A-only / B-only, each with its traced referrers, so a
residual string can be classified (log format of a shared function vs. string
of stock-only code) instead of guessed at.

An A-only/B-only path literal whose basename also appears on the other side is
counted separately (`*-build-path`) and excluded from the verdict: that is the
same `__FILE__` under a different build-tree prefix, which an out-of-tree Kleaf
build can never reproduce, so it is build provenance and not source residue.

usage: ko-str-refs.py [--sections .rodata.str,.rodata.str1.1,.rodata]
                      [--json OUT.json] [--shared] A.ko B.ko
"""
import argparse
import json
import struct
import sys

SHT_RELA, SHT_NOBITS = 4, 8
ALLOC, EXEC_FLAG = 0x2, 0x4
STT_FUNC, STT_OBJECT, STT_SECTION, STT_FILE = 1, 2, 3, 4

# AArch64 relocation types identifying the exact referenced byte:
#   257/258 ABS64/32, 259/260/261 PREL64/32/16 -- pointers / table entries
#   (261 PREL16 is what __bug_table uses for its __FILE__ pointer)
#   277 ADD_ABS_LO12_NC, 278/284/285/286/299 LDST*_ABS_LO12_NC
#   300-303, 335-337 LDST*_UNS (unscaled accessors, byte tables)
EXACT_TYPES = {257, 258, 259, 260, 261, 277, 278, 284, 285, 286, 299,
               300, 301, 302, 303, 335, 336, 337}
PAGE_TYPES = {274, 275, 276}        # ADR_PREL_LO21, ADR_PREL_PG_HI21{,_NC}


class KO:
    def __init__(self, path):
        self.path = path
        b = open(path, "rb").read()
        self.b = b
        assert b[:4] == b"\x7fELF" and b[4] == 2, f"{path}: need ELF64"
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x3a)
        shoff = struct.unpack_from("<Q", b, 0x28)[0]
        self.secs = []
        for i in range(shnum):
            o = shoff + i * shentsize
            nm, stype, flags, addr, off, size, link, info, _al, _e = \
                struct.unpack_from("<IIQQQQIIQQ", b, o)
            self.secs.append(dict(idx=i, name="", type=stype, flags=flags, addr=addr,
                                  off=off, size=size, link=link, info=info))
        shstr = self.secs[shstrndx]["off"]
        for i, s in enumerate(self.secs):
            s["name"] = self._cs(b[shstr:],
                                 struct.unpack_from("<I", b, shoff + i * shentsize)[0])
        self.byname = {s["name"]: s for s in self.secs}
        self.symbols = []
        sym = self.byname.get(".symtab") or self.byname.get(".dynsym")
        if sym:
            strb = self.secs[sym["link"]]["off"]
            for o in range(sym["off"], sym["off"] + sym["size"], 24):
                st_name, st_info, _o, st_shndx = struct.unpack_from("<IBBH", b, o)
                v, sz = struct.unpack_from("<QQ", b, o + 8)
                self.symbols.append(dict(name=self._cs(b[strb:], st_name),
                                         bind=st_info >> 4, type=st_info & 0xf,
                                         shndx=st_shndx, value=v, size=sz))

    @staticmethod
    def _cs(blob, off):
        end = blob.find(b"\0", off)
        return blob[off:end].decode("utf-8", "replace") if end > 0 else ""

    def data(self, name):
        s = self.byname.get(name)
        return self.b[s["off"]:s["off"] + s["size"]] if s else b""

    def owner(self, sec_name, off):
        """Innermost named symbol of section sec_name containing byte offset off."""
        best = None
        for s in self.symbols:
            if not s["name"] or s["shndx"] >= len(self.secs) or \
                    self.secs[s["shndx"]]["name"] != sec_name:
                continue
            if s["value"] <= off and off < s["value"] + max(s["size"], 4):
                span = max(s["size"], 4)
                if best is None or span < best[0]:
                    best = (span, s["name"], off - s["value"])
        if best:
            return f"{best[1]}+{best[2]:#x}"
        return f"<{sec_name}>+{off:#x}"

    def refs_by_offset(self, lit_secs):
        """{literal section: {byte offset: {kind: [referrer, ...]}}}"""
        out = {n: {} for n in lit_secs}
        # a .relaX section applies to X (sh_info), which may be code (.text,
        # .init.text, .exit.text) or a data table (_ddebug, __tracepoints, .data,
        # __param, ...).  Both kinds can reference a literal.
        applies = {}
        for s in self.secs:
            if s["type"] == SHT_RELA and s["info"] < len(self.secs):
                applies[s["idx"]] = self.secs[s["info"]]["name"]
        for s in self.secs:
            if s["type"] != SHT_RELA or s["idx"] not in applies or not s["size"]:
                continue
            cname = applies[s["idx"]]
            for o in range(s["off"], s["off"] + s["size"], 24):
                r_off, r_info, r_add = struct.unpack_from("<QQq", self.b, o)
                r_type, r_sym = r_info & 0xFFFFFFFF, r_info >> 32   # ELF64 r_info
                kind = "exact" if r_type in EXACT_TYPES else \
                    ("page" if r_type in PAGE_TYPES else None)
                if kind is None or r_sym >= len(self.symbols):
                    continue
                sym = self.symbols[r_sym]
                if sym["shndx"] >= len(self.secs):
                    continue
                tsec = self.secs[sym["shndx"]]["name"]
                if tsec not in out:
                    continue
                base = sym["value"] + r_add if sym["type"] != STT_SECTION else r_add
                ref = f"{cname}:{r_off:#x} {self.owner(cname, r_off)} ({sym['name'] or tsec})"
                slot = out[tsec].setdefault(base, {"exact": [], "page": []})
                slot[kind].append(ref)
        return out

    def literals(self, sections):
        """{section: {offset: text}} -- every NUL-terminated literal."""
        out = {}
        for name in sections:
            blob, pos, m = self.data(name), 0, {}
            for chunk in blob.split(b"\0"):
                if chunk:
                    m[pos] = chunk.decode("utf-8", "replace")
                pos += len(chunk) + 1
            out[name] = m
        return out


def is_path_basename_pair(entry, opposites):
    """True when `entry` is a path literal whose basename also appears as a path
    literal on the other side -- i.e. the same `__FILE__` under a different
    build-tree prefix, which is build plumbing and not source residue."""
    a = entry["string"]
    if "/" not in a:
        return False
    base = a.rsplit("/", 1)[-1]
    return any("/" in o["string"] and o["string"].rsplit("/", 1)[-1] == base
               for o in opposites)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--sections", default=".rodata.str,.rodata.str1.1,.rodata")
    ap.add_argument("--json")
    ap.add_argument("--shared", action="store_true", help="print shared literals too")
    ap.add_argument("--max-refs", type=int, default=3)
    args = ap.parse_args()

    A, B = KO(args.a), KO(args.b)
    secs = [s for s in args.sections.split(",") if s]
    print(f"A = {A.path}")
    print(f"B = {B.path}")
    for tag, ko in (("A", A), ("B", B)):
        live = [s["name"] for s in ko.secs
                if s["size"] and (s["name"].startswith(".rodata") or ".str" in s["name"])]
        print(f"  {tag} literal sections: " +
              ", ".join(f"{n}={ko.byname[n]['size']}B" for n in live))
    print()

    lit = {t: ko.literals(secs) for t, ko in (("A", A), ("B", B))}
    refs = {t: ko.refs_by_offset(secs) for t, ko in (("A", A), ("B", B))}
    out, tot, unref = {}, {"A-only": 0, "B-only": 0, "shared": 0,
                           "A-only-build-path": 0, "B-only-build-path": 0}, {}
    for sec in secs:
        ma, mb = lit["A"][sec], lit["B"][sec]
        ca = {}
        for o, t in ma.items():
            ca.setdefault(t, []).append(o)
        cb = {}
        for o, t in mb.items():
            cb.setdefault(t, []).append(o)
        print(f"### {sec}: A={len(ma)} literals/{len(A.data(sec))}B   "
              f"B={len(mb)} literals/{len(B.data(sec))}B   "
              f"traced-ref-offsets: A={len(refs['A'][sec])} B={len(refs['B'][sec])}")
        out[sec] = {}
        # Shared literals are always *counted*; --shared only controls whether
        # they are also listed one by one.
        for label, tag in (("A-only", "A"), ("B-only", "B"), ("shared", "A")):
            texts = (sorted(set(ca) & set(cb)) if label == "shared" else
                     sorted(set(ca) - set(cb)) if label == "A-only" else
                     sorted(set(cb) - set(ca)))
            verbose = args.shared or label != "shared"
            tot[label] += len(texts)
            print(f"  {label}: {len(texts)}")
            out[sec][label] = []
            for t in texts:
                hits, kinds = [], set()
                for off in (ca if tag == "A" else cb)[t]:
                    r = refs[tag][sec].get(off)
                    if r:
                        kinds |= {k for k in r if r[k]}
                        hits += [x for k in ("exact", "page") for x in r[k]]
                entry = dict(sec=sec, offsets=(ca if tag == "A" else cb)[t], bytes=len(t),
                             string=t, refs=sorted(set(hits)), kinds=sorted(kinds))
                if not hits:
                    unref[label] = unref.get(label, 0) + 1
                out[sec][label].append(entry)
                if not verbose:
                    continue
                print(f"    [+{entry['offsets'][0]:#x}] {entry['bytes']}B "
                      f"{'/'.join(sorted(kinds)) or 'UNREFERENCED':14s} {t!r}")
                for h in entry["refs"][:args.max_refs]:
                    print(f"         {h}")
        print()
    # An out-of-tree rebuild cannot reproduce the *build-tree prefix* of the
    # translation unit, so the __FILE__ that __bug_table points at differs as a
    # matter of build plumbing, not of source.  Pair such literals by basename
    # and keep them out of the residue count.
    pa = sorted({t for sec in secs for e in out[sec]["A-only"]
                 for t in [e["string"]] if is_path_basename_pair(e, out[sec]["B-only"])})
    pb = sorted({t for sec in secs for e in out[sec]["B-only"]
                 for t in [e["string"]] if is_path_basename_pair(e, out[sec]["A-only"])})
    tot["A-only-build-path"] = len(pa)
    tot["B-only-build-path"] = len(pb)
    for sec in secs:
        for label, pool in (("A-only", pa), ("B-only", pb)):
            for e in out[sec][label]:
                e["build_path"] = e["string"] in pool
                if e["build_path"]:
                    print(f"  note: {sec}+{e['offsets'][0]:#x} {label} is an "
                          f"out-of-tree build path (basename shared with the "
                          f"other side): {e['string']!r}")
    residue = (tot["A-only"] - tot["A-only-build-path"]) + \
              (tot["B-only"] - tot["B-only-build-path"])
    print("totals: " + "  ".join(f"{k}={v}" for k, v in tot.items()))
    if residue:
        print(f"verdict: literal residue present ({residue} non-build-path)")
    elif tot["A-only"] or tot["B-only"]:
        print("verdict: only out-of-tree build paths differ -- benign")
    else:
        print("verdict: no literal residue")
    if unref:
        print("note (literal present, no traced referrer): " +
              "  ".join(f"{k}={v}" for k, v in unref.items()))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(dict(a=A.path, b=B.path, totals=tot, unreferenced=unref,
                           sections=out), fh, indent=1)
        print("wrote", args.json)
    return 1 if residue else 0


if __name__ == "__main__":
    sys.exit(main())
