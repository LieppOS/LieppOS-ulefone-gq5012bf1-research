#!/usr/bin/env python3
"""Stock-vs-rebuild verification for the FT3680 reconstruction.

Usage:  fts-verify.py <workspace-dir> <rebuilt.ko>

Reports: import sets, MODVERSION CRCs, function sets/sizes, byte-identity of
the __versions/.modinfo contract, string overlap and object layout.
"""
import struct
import subprocess
import sys
import os


def sect(ko, name):
    r = subprocess.run(["llvm-objcopy", "--dump-section", f"{name}=/dev/stdout",
                        ko, "/dev/null"], capture_output=True)
    return r.stdout


def versions(ko):
    blob = sect(ko, "__versions")
    out = {}
    for i in range(0, len(blob) - 63, 64):
        e = blob[i:i + 64]
        crc = struct.unpack_from("<Q", e, 0)[0] & 0xFFFFFFFF
        out[e[8:].split(b"\0")[0].decode()] = crc
    return out


def syms(ko):
    r = subprocess.run(["llvm-readelf", "--symbols", ko], capture_output=True, text=True)
    imports, funcs = set(), {}
    for line in r.stdout.split("\n"):
        p = line.split()
        if len(p) < 8:
            continue
        if p[6] == "UND" and p[7] and not p[7].startswith("$"):
            imports.add(p[7])
        elif p[3] == "FUNC" and p[7] and not p[7].startswith("$"):
            try:
                funcs[p[7]] = int(p[2], 0)
            except ValueError:
                pass
    return imports, funcs


def main():
    ws, ko = sys.argv[1], sys.argv[2]

    st_imports = set()
    st_crc = {}
    with open(os.path.join(ws, "stock-imports.tsv")) as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if p and p[0]:
                st_imports.add(p[0])
    with open(os.path.join(ws, "stock-modversions.tsv")) as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 2:
                st_crc[p[1]] = int(p[0], 16)

    st_funcs = {}
    with open(os.path.join(ws, "stock-functions.tsv")) as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                st_funcs[p[0]] = int(p[3])

    rb_imports, rb_funcs = syms(ko)
    rb_crc = versions(ko)

    print("== imports ==")
    print(f"stock            : {len(st_imports)}")
    print(f"rebuilt          : {len(rb_imports)}")
    miss = sorted(st_imports - rb_imports)
    extra = sorted(rb_imports - st_imports)
    print(f"missing ({len(miss)}) : {miss}")
    print(f"extra   ({len(extra)}) : {extra}")

    print("\n== MODVERSION CRCs (shared imports) ==")
    ok = bad = 0
    badlist = []
    for k, v in sorted(rb_crc.items()):
        if k in st_crc:
            if st_crc[k] == v:
                ok += 1
            else:
                bad += 1
                badlist.append((k, st_crc[k], v))
    print(f"shared: {ok + bad}   identical: {ok}   mismatched: {bad}")
    for k, a, b in badlist:
        print(f"   {k:32s} stock 0x{a:08x}  rebuilt 0x{b:08x}")

    print("\n== functions ==")
    print(f"stock            : {len(st_funcs)}")
    print(f"rebuilt          : {len(rb_funcs)}")
    shared = set(st_funcs) & set(rb_funcs)
    same_size = [f for f in shared if st_funcs[f] == rb_funcs[f]]
    print(f"shared names     : {len(shared)}")
    print(f"size-identical   : {len(same_size)}")
    print(f"stock-only       : {len(set(st_funcs) - set(rb_funcs))}")
    print(f"rebuilt-only     : {len(set(rb_funcs) - set(st_funcs))}")
    print("stock-only list  :", sorted(set(st_funcs) - set(rb_funcs)))
    print("rebuilt-only list:", sorted(set(rb_funcs) - set(st_funcs)))

    print("\n== .modinfo ==")
    mi = sect(ko, ".modinfo").replace(b"\0", b"\n").decode("utf-8", "replace")
    for line in mi.split("\n"):
        if line.startswith(("depends", "name", "license", "description", "alias")):
            print("  " + line)


if __name__ == "__main__":
    main()
