#!/usr/bin/env python3
"""Stock-vs-rebuilt parity analyser for ffa_v10.ko.

Writes kernel/phase4-ffa-v10-function-parity.tsv and
kernel/phase4-ffa-v10-object-parity.tsv, and prints the summary counters the
authoritative report quotes.
"""
from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path


def load(path: Path):
    blob = path.read_bytes()
    e_shoff, = struct.unpack_from("<Q", blob, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", blob, 0x3A)

    def raw(i):
        return struct.unpack_from("<IIQQQQIIQQ", blob, e_shoff + i * shentsize)

    stroff = raw(shstrndx)[4]
    secs = {}
    for i in range(shnum):
        nm, ty, fl, ad, off, sz = raw(i)[:6]
        end = blob.index(b"\0", stroff + nm)
        secs[i] = (blob[stroff + nm:end].decode(), off, sz, ty)

    out = subprocess.run(["readelf", "-sW", str(path)], capture_output=True,
                         text=True, check=True).stdout
    funcs, objs = {}, {}
    for line in out.splitlines():
        f = line.split()
        if len(f) < 8 or f[6] in ("UND", "ABS"):
            continue
        try:
            value, size, idx = int(f[1], 16), int(f[2]), int(f[6])
        except ValueError:
            continue
        sec, soff, ssz, ty = secs[idx]
        name = f[7].split(".")[0]
        body = blob[soff:soff + size] if ty == 8 else blob[soff + value:
                                                           soff + value + size]
        kc = ""
        if f[3] == "FUNC" and value >= 4:
            kc = "0x%08x" % struct.unpack_from("<I", blob, soff + value - 4)[0]
        rec = {"sec": sec, "size": size, "bytes": body, "kcfi": kc,
               "bind": f[4], "off": value}
        (funcs if f[3] == "FUNC" else objs if f[3] == "OBJECT" else {})[name] = rec

    sec_sizes = {v[0]: v[2] for v in secs.values()}
    return funcs, objs, sec_sizes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stock")
    ap.add_argument("rebuilt")
    ap.add_argument("--prefix", default="kernel/phase4-ffa-v10")
    args = ap.parse_args()

    sf, so, ss = load(Path(args.stock))
    bf, bo, bs = load(Path(args.rebuilt))

    common = sorted(set(sf) & set(bf))
    missing = sorted(set(sf) - set(bf))
    extra = sorted(set(bf) - set(sf))

    size_id = [n for n in common if sf[n]["size"] == bf[n]["size"]]
    byte_id = [n for n in common if sf[n]["bytes"] == bf[n]["bytes"]]
    kcfi_id = [n for n in common if sf[n]["kcfi"] == bf[n]["kcfi"]]

    with open(args.prefix + "-function-parity.tsv", "w") as fh:
        fh.write("name\tsection\tstock_size\trebuild_size\tstock_kcfi\t"
                 "rebuild_kcfi\tkcfi_match\tsize_match\tbyte_match\tresidual\n")
        for n in sorted(set(sf) | set(bf)):
            s, b = sf.get(n), bf.get(n)
            if not s:
                fh.write("%s\t%s\t\t%d\t\t%s\t\t\t\tEXTRA\n"
                         % (n, b["sec"], b["size"], b["kcfi"]))
                continue
            if not b:
                fh.write("%s\t%s\t%d\t\t%s\t\t\t\t\tMISSING\n"
                         % (n, s["sec"], s["size"], s["kcfi"]))
                continue
            residual = ("none" if s["bytes"] == b["bytes"] else
                        "size-equal, bytes differ"
                        if s["size"] == b["size"] else
                        "size delta %+d" % (b["size"] - s["size"]))
            fh.write("%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t%s\t%s\n"
                     % (n, s["sec"], s["size"], b["size"], s["kcfi"],
                        b["kcfi"], s["kcfi"] == b["kcfi"],
                        s["size"] == b["size"], s["bytes"] == b["bytes"],
                        residual))

    with open(args.prefix + "-object-parity.tsv", "w") as fh:
        fh.write("name\tsection\tstock_size\trebuild_size\tclass\n")
        for n in sorted(set(so) | set(bo)):
            s, b = so.get(n), bo.get(n)
            if not s:
                cls = "EXTRA"
            elif not b:
                cls = "MISSING"
            elif s["bytes"] == b["bytes"]:
                cls = "BYTE_IDENTICAL"
            elif s["size"] == b["size"]:
                cls = "RELOCATION_EQUIVALENT"
            else:
                cls = "UNRESOLVED"
            fh.write("%s\t%s\t%s\t%s\t%s\n"
                     % (n, (s or b)["sec"], s["size"] if s else "",
                        b["size"] if b else "", cls))

    print("stock functions      : %d" % len(sf))
    print("rebuilt functions    : %d" % len(bf))
    print("shared               : %d" % len(common))
    print("missing              : %d %s" % (len(missing), missing))
    print("extra                : %d %s" % (len(extra), extra))
    print("size-identical       : %d / %d" % (len(size_id), len(common)))
    print("byte-identical       : %d / %d" % (len(byte_id), len(common)))
    print("kCFI identical       : %d / %d" % (len(kcfi_id), len(common)))
    bad = [n for n in common if sf[n]["kcfi"] != bf[n]["kcfi"]]
    if bad:
        print("kCFI mismatches      : %s" % bad)
    print("stock objects        : %d, rebuilt %d" % (len(so), len(bo)))
    obad = sorted(set(so) ^ set(bo))
    if obad:
        print("object name deltas   : %s" % obad)
    for k in sorted(set(ss) & set(bs)):
        if k.startswith((".text", ".init.text", ".exit.text", ".rodata",
                         ".data", ".bss", "__ksymtab", "__kcrctab",
                         "__versions")) and ss[k] != bs[k]:
            print("section size delta   : %-22s stock %6d rebuilt %6d"
                  % (k, ss[k], bs[k]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
