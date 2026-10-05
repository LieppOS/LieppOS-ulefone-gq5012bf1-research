#!/usr/bin/env python3
"""Rigorous function parity of stock imgsensor.ko vs a reconstruction build.

Every .text function is keyed by (translation unit, name, occurrence) so the
per-sensor static duplicates (open, init_ctx, get_imgsensor_id, ...) are
compared against the function of the *same* sensor TU.

A function is EXACT only when all of the following hold:
  * raw bytes identical (relocations unapplied, as stored in ET_REL),
  * KCFI type id (4 bytes before the entry) identical,
  * the ordered relocation list is identical after symbolic normalisation
    (offset-in-function, type, resolved target: symbol name + offset,
    string literal contents for merged-string sections, import name).

Usage:
  imgsensor_parity.py <stock.ko> <rebuilt.ko> <build_dir> [--tsv out.tsv]
                      [--diff NAME[@TU]]...

TU attribution
  rebuilt: exact, by consuming each object's function list (in the order of
           <build_dir>/imgsensor.mod) through the module's address order;
  stock:   framework functions inherit the TU of their name in the rebuilt
           objects (stock-only names inherit the previous function's TU);
           the sensor region (after the virt-sensor TU) is split at every
           get_imgsensor_id / leading init_ctx and named from the first
           <sensor>_ prefixed function in the segment.
"""
from __future__ import annotations

import argparse
import collections
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from elfmini import Elf  # noqa: E402

SENSOR_PREFIXES = ["imx989cts", "imx989", "s5kgm2sp", "s5kgn1sp", "ov32b40", "s5kjn1main2",
                   "s5kjn1cts", "s5kjn1", "ov64b"]


def text_funcs(elf):
    text = elf.secbyname[".text"].idx
    fs = [s for s in elf.symbols if s.type == 2 and s.shndx == text]
    fs.sort(key=lambda s: s.value)
    return fs


def obj_funcs(path):
    out = subprocess.run(["llvm-nm", "--defined-only", "-n", path], capture_output=True, text=True).stdout
    return [l.split()[-1] for l in out.splitlines() if len(l.split()) == 3 and l.split()[1] in "tT"]


def sensor_of(name):
    for p in SENSOR_PREFIXES:
        if name.startswith(p + "_"):
            return p
    return None


def tu_name(objpath, bdir):
    rel = os.path.relpath(objpath, bdir)
    if rel.startswith("common/"):
        return rel.split("/")[1].replace("_mipi_raw", "")
    return rel[:-2] + ".c"


def attribute_rebuilt(elf, bdir):
    fs = text_funcs(elf)
    objs = [o for o in open(os.path.join(bdir, "imgsensor.mod")).read().split() if o.endswith(".o")]
    seq = []
    for o in objs:
        for n in obj_funcs(o):
            seq.append((tu_name(o, bdir), n))
    res = []
    i = 0
    for s in fs:
        # objects contain .init/.exit functions too; skip names not in .text
        while i < len(seq) and seq[i][1] != s.name:
            i += 1
        if i == len(seq):
            raise SystemExit(f"cannot attribute rebuilt function {s.name}")
        res.append((seq[i][0], s))
        i += 1
    return res


def attribute_stock(elf, owner_by_name):
    fs = text_funcs(elf)
    res = []
    cur = None
    in_sensors = False
    seg = []

    def flush():
        if not seg:
            return
        tu = next((sensor_of(s.name) for s in seg if sensor_of(s.name)), "?sensor")
        for s in seg:
            res.append((tu, s))
        seg.clear()

    for k, s in enumerate(fs):
        if not in_sensors:
            if s.name in ("get_imgsensor_id", "init_ctx") and (cur or "").startswith("virt-sensor"):
                in_sensors = True
            else:
                cur = owner_by_name.get(s.name, cur)
                res.append((cur, s))
                continue
        prev = fs[k - 1].name if k else ""
        if s.name == "get_imgsensor_id" or (s.name == "init_ctx" and prev != "get_imgsensor_id"):
            flush()
        seg.append(s)
    flush()
    return res


class Normaliser:
    def __init__(self, elf):
        self.e = elf
        self.text = elf.secbyname[".text"].idx

    def target(self, r):
        e = self.e
        s = r.sym
        if s.shndx == 0:
            return f"U:{s.name}{'+%d' % r.addend if r.addend else ''}"
        sec = e.sections[s.shndx]
        if s.type in (1, 2):
            return f"{s.name}+{r.addend}"
        addr = s.value + r.addend
        if sec.flags & 0x20:  # SHF_STRINGS
            return "S:" + repr(e.cstring_at(s.shndx, addr))
        c = e.containing(s.shndx, addr)
        if c is not None:
            return f"{c.name}+{addr - c.value}"
        return f"{sec.name}?"

    def sig(self, f):
        lst = self.e.relocs.get(self.text, [])
        out = []
        for r in lst:
            if f.value <= r.off < f.value + f.size:
                out.append((r.off - f.value, r.tname, self.target(r)))
        return out


def fbytes(elf, f):
    sec = elf.sections[f.shndx]
    return elf.blob[sec.off + f.value: sec.off + f.value + f.size]


def kcfi(elf, f):
    sec = elf.sections[f.shndx]
    return struct.unpack_from("<I", elf.blob, sec.off + f.value - 4)[0] if f.value >= 4 else None


def addr_taken(elf):
    """Names of .text functions referenced by any relocation that is not a direct call."""
    text = elf.secbyname[".text"].idx
    out = set()
    for sec, lst in elf.relocs.items():
        if "eh_frame" in elf.sections[sec].name or not (elf.sections[sec].flags & 2):
            continue
        for r in lst:
            if r.tname in ("CALL26", "JUMP26"):
                continue
            t, off = elf.target(r)
            if t is not None and t.type == 2 and t.shndx == text and off == 0:
                out.add(t.value)
    return out


def layout_norm(elf, f):
    """Function words with non-relocated B/BL displacements replaced by the
    resolved target (symbol name + offset): equal iff code is identical
    modulo placement of the translation unit's other functions."""
    text = elf.secbyname[".text"]
    relocated = {r.off for r in elf.relocs.get(text.idx, []) if f.value <= r.off < f.value + f.size}
    out = []
    for off in range(f.value, f.value + f.size, 4):
        w = struct.unpack_from("<I", elf.blob, text.off + off)[0]
        if (w >> 26) in (0x25, 0x05) and off not in relocated:
            imm = w & 0x3FFFFFF
            if imm & 0x2000000:
                imm -= 1 << 26
            tgt = off + imm * 4
            if f.value <= tgt < f.value + f.size:
                out.append(("b", w >> 26, tgt - f.value))
            else:
                c = elf.containing(text.idx, tgt)
                out.append(("b", w >> 26, (c.name, tgt - c.value) if c else tgt))
        else:
            out.append(w)
    return out


def keyed(pairs):
    cnt = collections.Counter()
    out = {}
    for tu, s in pairs:
        k = (tu, s.name)
        out[(tu, s.name, cnt[k])] = s
        cnt[k] += 1
    return out


# ---------------------------------------------------------------- data objects
DATA_SECS = (".data", ".rodata", ".bss", ".data.once", ".rodata.cst16", ".ref.data", "__param")


def data_objs(elf):
    out = {}
    for s in elf.symbols:
        if s.type == 1 and 0 < s.shndx < 0xFF00:
            sec = elf.sections[s.shndx].name
            if sec in DATA_SECS:
                out.setdefault(sec, []).append(s)
    for k in out:
        out[k].sort(key=lambda s: (s.value, s.name))
    return out


def obj_objects(path):
    e = Elf(path)
    res = {}
    for s in e.symbols:
        if s.type == 1 and 0 < s.shndx < 0xFF00:
            sec = e.sections[s.shndx].name
            res.setdefault(sec, []).append((s.value, s.name))
    return {k: [n for _, n in sorted(v)] for k, v in res.items()}


def attribute_rebuilt_data(elf, bdir):
    objs = [o for o in open(os.path.join(bdir, "imgsensor.mod")).read().split() if o.endswith(".o")]
    per = [(tu_name(o, bdir), obj_objects(o)) for o in objs]
    res = []
    for sec, lst in data_objs(elf).items():
        seq = [(tu, n) for tu, d in per for n in d.get(sec, [])]
        i = 0
        for s in lst:
            j = i
            while j < len(seq) and seq[j][1] != s.name:
                j += 1
            if j == len(seq):
                res.append(("?", sec, s))
                continue
            res.append((seq[j][0], sec, s))
            i = j + 1
    return res


def attribute_stock_data(elf, owner, owner_seq=None):
    """owner_seq[(sec, name)] lists the rebuilt TUs (link order) defining a
    same-named static; the k-th stock occurrence is given to the k-th owner,
    so duplicated statics (e.g. hdr_exp_idx_map, Four_Cell_Array) are not all
    attributed to the first TU that defines them."""
    owner_seq = owner_seq or {}
    res = []
    for sec, lst in data_objs(elf).items():
        cur = None
        seen = collections.Counter()
        sensor_mode = False
        seg = []

        def flush():
            if seg:
                tu = None
                for s in seg:
                    for p in SENSOR_PREFIXES:
                        if s.name.startswith(p + "_"):
                            tu = p
                            break
                    if tu:
                        break
                for s in seg:
                    res.append((tu or "?sensor", sec, s))
                seg.clear()

        for s in lst:
            sp = next((p for p in SENSOR_PREFIXES if s.name.startswith(p + "_")), None)
            starts = (sec == ".data" and s.name == "pw_seq") or (sec == ".rodata" and s.name.endswith("_mipi_raw_entry"))
            if starts:
                sensor_mode = True
                flush()
            if sensor_mode and s.name in owner and owner[s.name].endswith(".c") and not sp:
                sensor_mode = False
                flush()
            if sensor_mode:
                seg.append(s)
            else:
                seq = owner_seq.get((sec, s.name))
                if seq and len(seq) > 1:
                    tu = seq[min(seen[s.name], len(seq) - 1)]
                    seen[s.name] += 1
                    res.append((tu, sec, s))
                    continue
                cur = owner.get(s.name, cur)
                res.append((cur, sec, s))
        flush()
    return res


def data_main(a, se, re_):
    rb = attribute_rebuilt_data(re_, a.bdir)
    owner = {}
    owner_seq = collections.defaultdict(list)
    for tu, sec, s in rb:
        owner.setdefault(s.name, tu)
        owner_seq[(sec, s.name)].append(tu)
    st = attribute_stock_data(se, owner, owner_seq)
    ns, nr = Normaliser(se), Normaliser(re_)

    def key(lst):
        cnt = collections.Counter()
        out = {}
        for tu, sec, s in lst:
            k = (tu, sec, s.name)
            out[(tu, sec, s.name, cnt[k])] = s
            cnt[k] += 1
        return out

    S, R = key(st), key(rb)

    def rsig(e, n, s):
        return [(r.off - s.value, r.tname, n.target(r)) for r in e.relocs_in(s)]

    rows = []
    for k in sorted(set(S) | set(R), key=lambda k: (k[1], S[k].value if k in S else 1 << 40, k)):
        s, r = S.get(k), R.get(k)
        if s and r:
            be = se.bytes_of(s) == re_.bytes_of(r)
            rl = rsig(se, ns, s) == rsig(re_, nr, r)
            cls = "EXACT" if (be and rl and s.size == r.size) else "DIFF"
            note = ",".join(x for x, ok in (("bytes", be), ("relocs", rl), ("size", s.size == r.size)) if not ok)
        else:
            cls, note = ("MISSING", "missing-in-rebuild") if s else ("EXTRA", "rebuild-only")
        rows.append((k[0], k[1], k[2], k[3], s.size if s else "-", r.size if r else "-", cls, note))
    if a.tsv:
        with open(a.tsv, "w") as f:
            f.write("tu\tsection\tobject\tocc\tstock_size\trebuilt_size\tcls\tnote\n")
            for row in rows:
                f.write("\t".join(map(str, row)) + "\n")
    per = collections.defaultdict(collections.Counter)
    for row in rows:
        per[row[0]][row[6]] += 1
    tot = collections.Counter(r[6] for r in rows)
    print("data objects:", dict(tot))
    for tu in sorted(per, key=str):
        print(f"  {str(tu):28s} " + " ".join(f"{k}={v}" for k, v in sorted(per[tu].items())))
    if not a.quiet:
        for row in rows:
            if row[6] != "EXACT":
                print("  - " + "  ".join(map(str, row)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stock")
    ap.add_argument("rebuilt")
    ap.add_argument("bdir")
    ap.add_argument("--tsv")
    ap.add_argument("--classes", help="optional TSV name<TAB>tu<TAB>class<TAB>note overriding non-exact class")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--data", action="store_true", help="compare data objects instead of functions")
    a = ap.parse_args()
    se, re_ = Elf(a.stock), Elf(a.rebuilt)
    if a.data:
        return data_main(a, se, re_)
    rb = attribute_rebuilt(re_, a.bdir)
    owner = {}
    for tu, s in rb:
        owner.setdefault(s.name, tu)
    st = attribute_stock(se, owner)
    S, R = keyed(st), keyed(rb)
    ns, nr = Normaliser(se), Normaliser(re_)
    at_s, at_r = addr_taken(se), addr_taken(re_)
    manual = {}
    if a.classes and os.path.exists(a.classes):
        for line in open(a.classes):
            if line.startswith("#") or not line.strip():
                continue
            p = line.rstrip("\n").split("\t")
            manual[(p[1], p[0])] = (p[2], p[3] if len(p) > 3 else "")
    rows = []
    for k in sorted(set(S) | set(R), key=lambda k: (S[k].value if k in S else 1 << 40, k)):
        s, r = S.get(k), R.get(k)
        tu, name, occ = k
        if s and r:
            be = fbytes(se, s) == fbytes(re_, r)
            ke = kcfi(se, s) == kcfi(re_, r)
            ss, rs = ns.sig(s), nr.sig(r)
            rl = ss == rs
            cls = "EXACT" if (be and ke and rl) else None
            why = []
            if cls is None and rl:
                ln = layout_norm(se, s) == layout_norm(re_, r)
                k_ok = ke or (s.value not in at_s and r.value not in at_r)
                if ln and k_ok:
                    cls = "EXACT-CODE"
                    why.append("identical modulo intra-TU branch displacement"
                               + ("" if ke else " and preceding-function KCFI word (not address-taken)"))
            if not be:
                why.append("bytes")
            if not ke:
                why.append("kcfi")
            if not rl:
                why.append(f"relocs({len(ss)}/{len(rs)})")
            note = ",".join(why)
        elif s:
            cls, note = None, "missing-in-rebuild"
        else:
            cls, note = None, "rebuild-only"
        if cls is None:
            m = manual.get((tu, name))
            cls, mnote = (m if m else ("UNRESOLVED", ""))
            if mnote:
                note = (note + "; " if note else "") + mnote
        rows.append(dict(tu=tu, function=name, occ=occ,
                         stock_size=s.size if s else "-", rebuilt_size=r.size if r else "-",
                         size_eq=bool(s and r and s.size == r.size),
                         byte_eq=bool(s and r and fbytes(se, s) == fbytes(re_, r)),
                         kcfi_eq=bool(s and r and kcfi(se, s) == kcfi(re_, r)),
                         reloc_eq=bool(s and r and ns.sig(s) == nr.sig(r)),
                         cls=cls, note=note))
    if a.tsv:
        with open(a.tsv, "w") as f:
            cols = ["tu", "function", "occ", "stock_size", "rebuilt_size", "size_eq", "byte_eq", "kcfi_eq",
                    "reloc_eq", "cls", "note"]
            f.write("\t".join(cols) + "\n")
            for r in rows:
                f.write("\t".join(str(r[c]) for c in cols) + "\n")
    stock_rows = [r for r in rows if r["stock_size"] != "-"]
    c = collections.Counter(r["cls"] for r in stock_rows)
    fw = [r for r in stock_rows if r["tu"].endswith(".c")]
    sn = [r for r in stock_rows if not r["tu"].endswith(".c")]
    print(f"stock functions {len(stock_rows)}  rebuilt-only {sum(1 for r in rows if r['stock_size'] == '-')}")
    print("classes:", dict(c))
    ex = lambda L: sum(r['cls'] == 'EXACT' for r in L)
    ec = lambda L: sum(r['cls'] in ('EXACT', 'EXACT-CODE') for r in L)
    print(f"framework: {ex(fw)}/{len(fw)} EXACT, {ec(fw)}/{len(fw)} EXACT+EXACT-CODE;"
          f" sensor TUs: {ex(sn)}/{len(sn)} EXACT, {ec(sn)}/{len(sn)} EXACT+EXACT-CODE")
    per = collections.defaultdict(collections.Counter)
    for r in stock_rows:
        per[r["tu"]][r["cls"]] += 1
    for tu in sorted(per):
        print(f"  {tu:28s} " + " ".join(f"{k}={v}" for k, v in sorted(per[tu].items())))
    if not a.quiet:
        for r in rows:
            if r["cls"] not in ("EXACT",):
                print(f"  - {r['tu']:24s} {r['function']:40s} {r['stock_size']:>5} {r['rebuilt_size']:>5} "
                      f"{r['cls']:18s} {r['note']}")


if __name__ == "__main__":
    main()
