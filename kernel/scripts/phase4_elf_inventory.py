#!/usr/bin/env python3
"""Generic stock-module ELF inventory dumper (phase 4).

Emits the standard seven TSVs used by every phase-4 reconstruction:
functions, objects, imports, modversions, exports, relocations, strings.

Usage:
  phase4_elf_inventory.py <module.ko> <out-prefix> [--symvers <vmlinux.symvers>]
"""
from __future__ import annotations

import argparse
import re
import struct
import subprocess
import sys
from pathlib import Path


def sections(blob: bytes):
    e_shoff, = struct.unpack_from("<Q", blob, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", blob, 0x3A)

    def raw(i):
        return struct.unpack_from("<IIQQQQIIQQ", blob, e_shoff + i * shentsize)

    stroff = raw(shstrndx)[4]
    out = {}
    for i in range(shnum):
        nm, ty, fl, ad, off, sz, lk, inf, al, es = raw(i)
        end = blob.index(b"\0", stroff + nm)
        out[i] = (blob[stroff + nm:end].decode(), ty, fl, off, sz, es)
    return out


def symbols(path: Path):
    out = subprocess.run(["readelf", "-sW", str(path)], capture_output=True,
                         text=True, check=True).stdout
    res = []
    for line in out.splitlines():
        f = line.split()
        if len(f) < 8 or not f[0].endswith(":"):
            continue
        try:
            value, size = int(f[1], 16), int(f[2])
        except ValueError:
            continue
        res.append({"value": value, "size": size, "type": f[3], "bind": f[4],
                    "ndx": f[6], "name": f[7]})
    return res


def kcfi(blob, secs, sym):
    """kCFI type id = word immediately before the function entry."""
    try:
        idx = int(sym["ndx"])
    except ValueError:
        return ""
    if sym["value"] < 4 or idx not in secs:
        return ""
    off = secs[idx][3] + sym["value"] - 4
    if off + 4 > len(blob):
        return ""
    v, = struct.unpack_from("<I", blob, off)
    return "0x%08x" % v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("prefix")
    args = ap.parse_args()
    ko = Path(args.module)
    blob = ko.read_bytes()
    secs = sections(blob)
    byname = {v[0]: (k, v) for k, v in secs.items()}
    syms = symbols(ko)
    pre = args.prefix

    # ---- functions -------------------------------------------------------
    with open(pre + "-functions.tsv", "w") as fh:
        fh.write("name\tsection\toffset\tsize\tbind\tkcfi_type_id\n")
        n = 0
        for s in sorted((s for s in syms if s["type"] == "FUNC"
                         and s["ndx"] not in ("UND", "ABS")),
                        key=lambda s: (s["ndx"], s["value"])):
            sec = secs[int(s["ndx"])][0]
            fh.write("%s\t%s\t0x%x\t%d\t%s\t%s\n"
                     % (s["name"], sec, s["value"], s["size"], s["bind"],
                        kcfi(blob, secs, s)))
            n += 1
    print("functions: %d" % n)

    # ---- objects ---------------------------------------------------------
    with open(pre + "-objects.tsv", "w") as fh:
        fh.write("name\tsection\toffset\tsize\tbind\n")
        n = 0
        for s in sorted((s for s in syms if s["type"] == "OBJECT"
                         and s["ndx"] not in ("UND", "ABS")),
                        key=lambda s: (s["ndx"], s["value"])):
            fh.write("%s\t%s\t0x%x\t%d\t%s\n"
                     % (s["name"], secs[int(s["ndx"])][0], s["value"],
                        s["size"], s["bind"]))
            n += 1
    print("objects: %d" % n)

    # ---- modversions -----------------------------------------------------
    mv = {}
    if "__versions" in byname:
        _, (_, _, _, off, size, _) = byname["__versions"]
        for i in range(off, off + size, 64):
            rec = blob[i:i + 64]
            if len(rec) < 64:
                break
            crc, = struct.unpack_from("<I", rec, 0)
            mv[rec[8:].split(b"\0")[0].decode()] = crc
    with open(pre + "-modversions.tsv", "w") as fh:
        fh.write("symbol\tcrc\n")
        for k in sorted(mv):
            fh.write("%s\t0x%08x\n" % (k, mv[k]))
    print("modversions: %d" % len(mv))

    # ---- imports ---------------------------------------------------------
    und = sorted({s["name"].split("@")[0] for s in syms
                  if s["ndx"] == "UND" and s["name"]})
    with open(pre + "-imports.tsv", "w") as fh:
        fh.write("symbol\tmodversion_crc\n")
        for u in und:
            fh.write("%s\t%s\n" % (u, "0x%08x" % mv[u] if u in mv else ""))
    print("imports (UND): %d" % len(und))

    # ---- exports ---------------------------------------------------------
    exports = []
    for tabname, cls in (("__ksymtab", "EXPORT_SYMBOL"),
                         ("__ksymtab_gpl", "EXPORT_SYMBOL_GPL")):
        if tabname not in byname:
            continue
        idx, (_, _, _, off, size, _) = byname[tabname]
        crctab = "__kcrctab" + ("_gpl" if cls.endswith("GPL") else "")
        crcoff = byname[crctab][1][3] if crctab in byname else None
        names = sorted((s for s in syms
                        if s["name"].startswith("__ksymtab_")
                        and s["name"] not in ("__ksymtab", "__ksymtab_gpl")
                        and s["type"] != "SECTION"
                        and s["ndx"] != "UND"), key=lambda s: s["value"])
        for s in names:
            if int(s["ndx"]) != idx:
                continue
            name = s["name"][len("__ksymtab_"):]
            crc = ""
            if crcoff is not None:
                # __crc_<name> symbol carries the offset inside the crctab
                for c in syms:
                    if c["name"] == "__crc_" + name:
                        v, = struct.unpack_from("<I", blob, crcoff + c["value"])
                        crc = "0x%08x" % v
                        break
            exports.append((name, cls, crc))
    with open(pre + "-exports.tsv", "w") as fh:
        fh.write("symbol\texport_class\tcrc\n")
        for name, cls, crc in sorted(exports):
            fh.write("%s\t%s\t%s\n" % (name, cls, crc))
    print("exports: %d" % len(exports))

    # ---- relocations -----------------------------------------------------
    out = subprocess.run(["readelf", "-rW", str(ko)], capture_output=True,
                         text=True, check=True).stdout
    cur = None
    rels = []
    for line in out.splitlines():
        m = re.match(r"Relocation section '(\S+)'", line)
        if m:
            cur = m.group(1)
            continue
        f = line.split()
        if cur and len(f) >= 5 and re.fullmatch(r"[0-9a-f]{16}", f[0]):
            rels.append((cur, f[0], f[2], f[4],
                         f[6] if len(f) > 6 else ""))
    with open(pre + "-relocations.tsv", "w") as fh:
        fh.write("section\toffset\ttype\tsymbol\taddend\n")
        for r in rels:
            fh.write("\t".join(r) + "\n")
    print("relocations: %d" % len(rels))

    # ---- strings ---------------------------------------------------------
    strs = []
    for nm, (_, ty, _, off, size, _) in ((v[0], v) for v in secs.values()):
        if not nm.startswith(".rodata.str") and nm != ".modinfo":
            continue
        for item in blob[off:off + size].split(b"\0"):
            if len(item) >= 2:
                try:
                    strs.append((nm, item.decode()))
                except UnicodeDecodeError:
                    pass
    with open(pre + "-strings.tsv", "w") as fh:
        fh.write("section\tstring\n")
        for sec, s in strs:
            fh.write("%s\t%s\n" % (sec, s.replace("\t", "\\t")
                                   .replace("\n", "\\n")))
    print("strings: %d" % len(strs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
