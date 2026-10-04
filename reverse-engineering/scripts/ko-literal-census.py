#!/usr/bin/env python3
"""ko-literal-census.py — where does every relocation of a kernel module point?

Companion to ko-str-refs.py.  `ko-str-refs.py` answers "who references literal
X"; this answers the dual question, which is what actually closes a literal
residue claim: "does ANY relocation in this module point into the section that
holds the residual literal?".  A literal with no inbound relocation anywhere
(code AND tables) is emitted-but-dead compiler residue, not evidence of extra
source; a literal with inbound relocations has to be explained by real code.

Prints, per module: every `.rela*` section, how many of its entries target each
target section, and for the literal-bearing sections the exact inbound offsets.
With --literal SECTION the inbound offsets of that section are printed as a
referrer table (referrer symbol+offset -> entry).

usage: ko-literal-census.py [--literal .rodata.str]... A.ko [B.ko ...]
"""
import argparse
import struct
import sys

SHT_RELA, SHT_NOBITS, ALLOC, EXEC_FLAG = 4, 8, 0x2, 0x4

R_TYPES = {
    257: "ABS64", 258: "ABS32", 259: "PREL64", 260: "PREL32", 261: "PREL16",
    274: "ADR_PREL_LO21", 275: "ADR_PREL_PG_HI21", 276: "ADR_PREL_PG_HI21_NC",
    277: "ADD_ABS_LO12_NC", 278: "LDST8_ABS_LO12_NC", 283: "CALL26",
    284: "LDST16_ABS_LO12_NC", 285: "LDST32_ABS_LO12_NC",
    286: "LDST64_ABS_LO12_NC", 299: "LDST128_ABS_LO12_NC",
    300: "LDST8_PREL_LO21", 301: "LDST8_PREL_PG_HI21",
    335: "LDST8_UNSCALED?", 336: "LDST16_UNSCALED", 337: "LDST32_UNSCALED",
    338: "LDST64_UNSCALED",
}


class KO:
    def __init__(self, path):
        b = open(path, "rb").read()
        self.path, self.b = path, b
        shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x3a)
        shoff = struct.unpack_from("<Q", b, 0x28)[0]
        self.secs = []
        for i in range(shnum):
            o = shoff + i * shentsize
            nm, stype, flags, addr, off, size, link, info, _a, _e = \
                struct.unpack_from("<IIQQQQIIQQ", b, o)
            self.secs.append(dict(idx=i, name="", type=stype, flags=flags, addr=addr,
                                  off=off, size=size, link=link, info=info))
        shstr = self.secs[shstrndx]["off"]
        for i, s in enumerate(self.secs):
            s["name"] = self._cs(b[shstr:],
                                 struct.unpack_from("<I", b, shoff + i * shentsize)[0])
        self.byname = {s["name"]: s for s in self.secs}
        self.symbols = []
        sym = self.byname.get(".symtab")
        if sym:
            strb = self.secs[sym["link"]]["off"]
            for o in range(sym["off"], sym["off"] + sym["size"], 24):
                st_name, st_info, _o, shndx = struct.unpack_from("<IBBH", b, o)
                v, sz = struct.unpack_from("<QQ", b, o + 8)
                self.symbols.append(dict(name=self._cs(b[strb:], st_name), type=st_info & 0xf,
                                         bind=st_info >> 4, shndx=shndx, value=v, size=sz))

    @staticmethod
    def _cs(blob, off):
        e = blob.find(b"\0", off)
        return blob[off:e].decode("utf-8", "replace") if e > 0 else ""

    def data(self, n):
        s = self.byname.get(n)
        return self.b[s["off"]:s["off"] + s["size"]] if s else b""

    def owner(self, sec_name, off):
        best = None
        for s in self.symbols:
            if not s["name"] or s["shndx"] >= len(self.secs) or \
                    self.secs[s["shndx"]]["name"] != sec_name:
                continue
            if s["value"] <= off < s["value"] + max(s["size"], 4):
                span = max(s["size"], 4)
                if best is None or span < best[0]:
                    best = (span, s["name"], off - s["value"])
        return f"{best[1]}+{best[2]:#x}" if best else f"<{sec_name}>+{off:#x}"

    def census(self):
        """{rela section: {target section: [ (r_off, type name, sym, addend) ]}}"""
        out = {}
        for s in self.secs:
            if s["type"] != SHT_RELA or not s["size"] or s["info"] >= len(self.secs):
                continue
            applies = self.secs[s["info"]]["name"]
            per = {}
            for o in range(s["off"], s["off"] + s["size"], 24):
                r_off, r_info, r_add = struct.unpack_from("<QQq", self.b, o)
                r_type, r_sym = r_info & 0xFFFFFFFF, r_info >> 32
                sym = self.symbols[r_sym] if r_sym < len(self.symbols) else None
                if sym is None or sym["shndx"] >= len(self.secs):
                    continue
                tgt = self.secs[sym["shndx"]]["name"] or (
                    "UND" if sym["shndx"] == 0 else f"<{sym['shndx']}>")
                per.setdefault(tgt, []).append(
                    (r_off, R_TYPES.get(r_type, f"#{r_type}"), sym, r_add))
            out[s["name"]] = dict(applies=applies, targets=per)
        return out

    def inbound(self, literal_secs):
        """{literal section: {offset: [(referrer sec, r_off, referrer owner, type)]}}"""
        res = {n: {} for n in literal_secs}
        for rname, r in self.census().items():
            applies = r["applies"]
            for tgt, entries in r["targets"].items():
                if tgt not in res:
                    continue
                for r_off, tname, sym, add in entries:
                    off = add if sym["type"] == 3 else sym["value"] + add
                    res[tgt].setdefault(off, []).append(
                        (applies, r_off, self.owner(applies, r_off), tname, sym["name"]))
        return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kos", nargs="+")
    ap.add_argument("--literal", action="append", default=[])
    ap.add_argument("--max", type=int, default=6)
    args = ap.parse_args()
    for p in args.kos:
        ko = KO(p)
        print("=" * 78)
        print(p)
        cen = ko.census()
        tot = {}
        for rname, r in sorted(cen.items()):
            tg = {t: len(v) for t, v in sorted(r["targets"].items())}
            for t, n in tg.items():
                tot[t] = tot.get(t, 0) + n
            print(f"  {rname:45s} -> {r['applies']:28s} {tg}")
        print(f"  inbound totals by target section: {dict(sorted(tot.items()))}")
        for sec in args.literal:
            ib = ko.inbound([sec]).get(sec, {})
            blob = ko.data(sec)
            lits = {}
            pos = 0
            for chunk in blob.split(b"\0"):
                if chunk:
                    lits[pos] = chunk.decode("utf-8", "replace")
                pos += len(chunk) + 1
            covered = {o for o in ib if any(o >= k and o < k + len(v) + 1
                                           for k, v in lits.items())}
            print(f"\n  --- inbound relocations into {sec} "
                  f"({len(blob)}B, {len(lits)} literal(s), "
                  f"{len(covered)}/{len(lits)} literals with an inbound reloc)")
            for off, text in sorted(lits.items()):
                hits = [h for o, hs in ib.items()
                        for h in hs if o >= off and o < off + len(text) + 1]
                print(f"      {sec}+{off:#x} {text[:72]!r} inbound={len(hits)}")
                for h in hits[:args.max]:
                    print(f"          from {h[0]}:{h[1]:#x} {h[2]} via {h[3]}"
                          f"{'' if not h[4] else ' sym=' + h[4]}")
            other = sorted(o for o in ib if o not in
                           {k for k in lits} and
                           not any(k <= o < k + len(v) + 1 for k, v in lits.items()))
            if other:
                print(f"      inbound offsets not inside a literal: "
                      f"{[hex(o) for o in other[:8]]}{'...' if len(other) > 8 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
