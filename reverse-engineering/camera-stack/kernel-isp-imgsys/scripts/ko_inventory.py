#!/usr/bin/env python3
"""Static inventory of stock kernel modules (read-only).

usage: ko_inventory.py <out.tsv> <detail_dir> <module.ko>...

Per module: sha256, size, modinfo (name, vermagic, depends, srcversion?,
scmversion, license, import_ns, alias count), build-id, section sizes,
function / data-object counts, KCFI-typed functions, exports (+CRC),
imports (+CRC from __versions), embedded source paths (__FILE__ strings).
Detail lists go to <detail_dir>/<module>.{exports,imports,funcs,objects,paths,sections}.tsv
"""
import hashlib
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from elfmini import Elf  # noqa: E402


def modinfo(e):
    s = e.secbyname.get(".modinfo")
    out = {}
    if not s:
        return out
    for kv in e.blob[s.off:s.off + s.size].split(b"\0"):
        if b"=" in kv:
            k, v = kv.decode(errors="replace").split("=", 1)
            out.setdefault(k, []).append(v)
    return out


def versions(e):
    s = e.secbyname.get("__versions")
    res = []
    if not s:
        return res
    for i in range(0, s.size, 64):
        crc = struct.unpack_from("<Q", e.blob, s.off + i)[0]
        name = e.blob[s.off + i + 8:s.off + i + 64].split(b"\0")[0].decode()
        res.append((name, crc & 0xFFFFFFFF))
    return res


def exports(e):
    res = []
    for s in e.symbols:
        if s.name.startswith("__ksymtab_") and s.type in (0, 1) and s.shndx != 0:
            n = s.name[len("__ksymtab_"):]
            crc = None
            c = next((x for x in e.symbols if x.name == "__crc_" + n), None)
            if c is not None and c.shndx not in (0,) and c.shndx < 0xFF00:
                sec = e.sections[c.shndx]
                crc = struct.unpack_from("<I", e.blob, sec.off + c.value)[0]
            res.append((n, crc))
    # 6.1 modules: exports recorded in __ksymtab relocations; fall back to symbol scan
    if not res and "__ksymtab_strings" in e.secbyname:
        s = e.secbyname["__ksymtab_strings"]
        names = [x.decode() for x in e.blob[s.off:s.off + s.size].split(b"\0") if x]
        kc = e.secbyname.get("__kcrctab") or e.secbyname.get("__kcrctab_gpl")
        for i, n in enumerate(names):
            crc = None
            if kc and kc.size >= 4 * (i + 1):
                crc = struct.unpack_from("<I", e.blob, kc.off + 4 * i)[0]
            res.append((n, crc))
    return res


def build_id(e):
    s = e.secbyname.get(".note.gnu.build-id")
    if not s:
        return ""
    b = e.blob[s.off:s.off + s.size]
    nsz, dsz, _ = struct.unpack_from("<III", b, 0)
    o = 12 + ((nsz + 3) & ~3)
    return b[o:o + dsz].hex()


def kcfi_funcs(e):
    t = e.secbyname.get(".text")
    if not t:
        return 0
    n = 0
    for s in e.symbols:
        if s.type == 2 and s.shndx == t.idx and s.value >= 4:
            # KCFI preamble: the word before the function; for typed functions
            # the compiler emits a __cfi_<name> or __kcfi_typeid; count those
            pass
    n = sum(1 for s in e.symbols if s.name.startswith("__kcfi_typeid_"))
    return n


def paths(e):
    out = set()
    for sname in (".rodata.str1.1", ".rodata.str", ".rodata"):
        s = e.secbyname.get(sname)
        if not s or s.type == 8:
            continue
        for m in re.finditer(rb"[\x20-\x7e]{4,}", e.blob[s.off:s.off + s.size]):
            t = m.group(0).decode()
            if re.search(r"\.[ch]$", t) and "/" in t:
                out.add(t)
    return sorted(out)


def main():
    out, ddir = sys.argv[1], sys.argv[2]
    os.makedirs(ddir, exist_ok=True)
    cols = ["module", "sha256", "size", "name", "vermagic", "depends", "scmversion", "license", "import_ns",
            "aliases", "build_id", "funcs", "data_objs", "kcfi_typeids", "exports", "imports",
            "text", "data", "rodata", "bss", "src_paths_sample"]
    rows = []
    for p in sys.argv[3:]:
        e = Elf(p)
        mi = modinfo(e)
        fn = [s for s in e.symbols if s.type == 2 and 0 < s.shndx < 0xFF00]
        ob = [s for s in e.symbols if s.type == 1 and 0 < s.shndx < 0xFF00
              and not e.sections[s.shndx].name.startswith((".modinfo", "__ksymtab", "__kcrctab", "__param"))]
        ex = exports(e)
        im = versions(e)
        ps = paths(e)
        sz = lambda pre: sum(s.size for s in e.sections if s.name == pre or s.name.startswith(pre + "."))  # noqa
        base = os.path.basename(p)[:-3]
        rows.append([os.path.basename(p), hashlib.sha256(e.blob).hexdigest(), str(len(e.blob)),
                     ",".join(mi.get("name", [])), ",".join(mi.get("vermagic", [])),
                     ",".join(mi.get("depends", [])), ",".join(mi.get("scmversion", [])),
                     ",".join(mi.get("license", [])), ",".join(mi.get("import_ns", [])),
                     str(len(mi.get("alias", []))), build_id(e), str(len(fn)), str(len(ob)),
                     str(kcfi_funcs(e)), str(len(ex)), str(len(im)),
                     str(sz(".text")), str(sz(".data")), str(sz(".rodata")), str(sz(".bss")),
                     ";".join(ps[:3])])
        with open(f"{ddir}/{base}.exports.tsv", "w") as f:
            f.write("symbol\tcrc\n" + "".join(f"{n}\t{'' if c is None else '%#010x' % c}\n" for n, c in ex))
        with open(f"{ddir}/{base}.imports.tsv", "w") as f:
            f.write("symbol\tcrc\n" + "".join(f"{n}\t{c:#010x}\n" for n, c in im))
        with open(f"{ddir}/{base}.funcs.tsv", "w") as f:
            f.write("function\tsection\tsize\tbind\n" + "".join(
                f"{s.name}\t{e.sections[s.shndx].name}\t{s.size}\t{s.bind}\n" for s in sorted(fn, key=lambda s: (s.shndx, s.value))))
        with open(f"{ddir}/{base}.objects.tsv", "w") as f:
            f.write("object\tsection\tsize\tbind\n" + "".join(
                f"{s.name}\t{e.sections[s.shndx].name}\t{s.size}\t{s.bind}\n" for s in sorted(ob, key=lambda s: (s.shndx, s.value))))
        with open(f"{ddir}/{base}.paths.tsv", "w") as f:
            f.write("".join(x + "\n" for x in ps))
        with open(f"{ddir}/{base}.sections.tsv", "w") as f:
            f.write("section\ttype\tflags\tsize\n" + "".join(
                f"{s.name}\t{s.type}\t{s.flags:#x}\t{s.size}\n" for s in e.sections if s.name))
    with open(out, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")


if __name__ == "__main__":
    main()
