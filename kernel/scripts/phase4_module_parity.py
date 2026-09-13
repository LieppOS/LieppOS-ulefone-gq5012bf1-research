#!/usr/bin/env python3
"""Generic stock-vs-rebuilt module parity comparator (function/KCFI/ABI level).

Usage: phase4_module_parity.py <stock.ko> <rebuilt.ko> [--tsv out-prefix]
Prints a compact parity report; never mutates either input.
"""
from __future__ import annotations
import subprocess, struct, sys, csv, os


def sections(blob):
    e_shoff, = struct.unpack_from("<Q", blob, 0x28)
    shent, shnum, shstr = struct.unpack_from("<HHH", blob, 0x3A)
    raw = lambda i: struct.unpack_from("<IIQQQQIIQQ", blob, e_shoff + i * shent)
    stro = raw(shstr)[4]
    out = {}
    for i in range(shnum):
        nm, ty, fl, ad, off, sz, lk, inf, al, es = raw(i)
        end = blob.index(b"\0", stro + nm)
        out[i] = (blob[stro + nm:end].decode(), off, sz, ty)
    return out


def kcfi_ids(path, blob, sc):
    """Map function name -> kcfi type id (u32 stored 4 bytes before entry)."""
    ids = {}
    for name, (secn, off, size, binding, val) in funcs_raw(path, blob, sc).items():
        sname, soff, ssz, sty = sc[secn]
        if sty == 8 or val < 4:      # NOBITS
            continue
        p = soff + val - 4
        if p + 4 <= len(blob):
            w, = struct.unpack_from("<I", blob, p)
            ids[name] = "0x%08x" % ((~w) & 0xFFFFFFFF) if False else "0x%08x" % w
    return ids


def funcs_raw(path, blob, sc):
    out = subprocess.run(["readelf", "-sW", path], capture_output=True, text=True).stdout
    res = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) < 8 or not f[0].endswith(":"):
            continue
        if f[3] != "FUNC" or f[6] in ("UND", "ABS"):
            continue
        res[f[7]] = (int(f[6]), None, int(f[2]), f[4], int(f[1], 16))
    return res


def funcs(path):
    blob = open(path, "rb").read()
    sc = sections(blob)
    res = {}
    for name, (secn, _, size, binding, val) in funcs_raw(path, blob, sc).items():
        sname, soff, ssz, sty = sc[secn]
        body = blob[soff + val: soff + val + size] if sty != 8 else b""
        kid = None
        if sty != 8 and val >= 4:
            w, = struct.unpack_from("<I", blob, soff + val - 4)
            kid = "0x%08x" % w
        res[name] = dict(section=sname, size=size, bind=binding, body=body, kcfi=kid)
    return res


def syms(path, pref):
    out = subprocess.run(["readelf", "-sW", path], capture_output=True, text=True).stdout
    r = set()
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[0].endswith(":") and f[7].startswith(pref):
            r.add(f[7][len(pref):])
    return r


def undef(path):
    out = subprocess.run(["readelf", "-sW", path], capture_output=True, text=True).stdout
    r = set()
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[0].endswith(":") and f[6] == "UND" and f[7] != "":
            r.add(f[7])
    return r


def export_crcs(path):
    blob = open(path, "rb").read()
    sc = sections(blob)
    out = subprocess.run(["readelf", "-sW", path], capture_output=True, text=True).stdout
    crc = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) < 8 or not f[0].endswith(":"):
            continue
        if f[7].startswith("__crc_") and f[6] not in ("UND", "ABS"):
            sname, soff, ssz, sty = sc[int(f[6])]
            v, = struct.unpack_from("<I", blob, soff + int(f[1], 16))
            crc[f[7][6:]] = "0x%08x" % v
    return crc


def modversions(path):
    blob = open(path, "rb").read()
    sc = sections(blob)
    for i, (n, off, sz, ty) in sc.items():
        if n == "__versions":
            out = {}
            for p in range(off, off + sz, 64):
                crc, = struct.unpack_from("<Q", blob, p)
                nm = blob[p + 8:p + 64].split(b"\0")[0].decode()
                if nm:
                    out[nm] = "0x%08x" % (crc & 0xFFFFFFFF)
            return out
    return {}


def strings_of(path):
    blob = open(path, "rb").read()
    sc = sections(blob)
    out = []
    for i, (n, off, sz, ty) in sc.items():
        if n.startswith(".rodata.str") or n == ".rodata.str1.1":
            for s in blob[off:off + sz].split(b"\0"):
                if s:
                    out.append(s.decode("utf-8", "replace"))
    return sorted(out)


def main():
    stock, reb = sys.argv[1], sys.argv[2]
    A, B = funcs(stock), funcs(reb)
    sa, sb = set(A), set(B)
    shared = sa & sb
    same_size = [n for n in shared if A[n]["size"] == B[n]["size"]]
    same_byte = [n for n in shared if A[n]["body"] == B[n]["body"]]
    same_kcfi = [n for n in shared if A[n]["kcfi"] == B[n]["kcfi"]]
    print(f"stock functions        : {len(sa)}")
    print(f"rebuilt functions      : {len(sb)}")
    print(f"shared                 : {len(shared)}")
    print(f"missing (stock only)   : {len(sa-sb)} {sorted(sa-sb) if sa-sb else ''}")
    print(f"extra   (rebuilt only) : {len(sb-sa)} {sorted(sb-sa) if sb-sa else ''}")
    print(f"size-identical         : {len(same_size)}/{len(shared)}")
    print(f"BYTE-IDENTICAL         : {len(same_byte)}/{len(shared)}")
    print(f"KCFI identical         : {len(same_kcfi)}/{len(shared)}")
    diff = sorted(n for n in shared if A[n]["body"] != B[n]["body"])
    if diff:
        print("  byte-differing:")
        for n in diff[:40]:
            print(f"    {n:42s} stock={A[n]['size']:<6} reb={B[n]['size']:<6} "
                  f"kcfi {A[n]['kcfi']}/{B[n]['kcfi']}")
    ua, ub = undef(stock), undef(reb)
    print(f"imports                : stock {len(ua)} rebuilt {len(ub)} "
          f"{'IDENTICAL' if ua==ub else 'DIFF'}")
    if ua != ub:
        print(f"   stock-only  : {sorted(ua-ub)}")
        print(f"   rebuilt-only: {sorted(ub-ua)}")
    ma, mb = modversions(stock), modversions(reb)
    print(f"MODVERSIONs            : stock {len(ma)} rebuilt {len(mb)} "
          f"{'IDENTICAL' if ma==mb else 'DIFF'}")
    for k in sorted(set(ma) | set(mb)):
        if ma.get(k) != mb.get(k):
            print(f"   {k:38s} stock={ma.get(k)} rebuilt={mb.get(k)}")
    ea, eb = export_crcs(stock), export_crcs(reb)
    nat = [k for k in ea if ea[k] == eb.get(k)]
    print(f"exports                : stock {len(ea)} rebuilt {len(eb)}")
    print(f"NATURAL export CRCs    : {len(nat)}/{len(ea)}")
    for k in sorted(ea):
        if ea[k] != eb.get(k):
            print(f"   {k:38s} stock={ea[k]} rebuilt={eb.get(k)}")
    ta, tb = strings_of(stock), strings_of(reb)
    print(f"strings                : stock {len(ta)} rebuilt {len(tb)} "
          f"{'IDENTICAL' if ta==tb else 'DIFF'}")
    if ta != tb:
        onlyA = [s for s in ta if s not in set(tb)]
        onlyB = [s for s in tb if s not in set(ta)]
        for s in onlyA[:12]:
            print(f"   stock-only  : {s!r}")
        for s in onlyB[:12]:
            print(f"   rebuilt-only: {s!r}")


if __name__ == "__main__":
    main()
