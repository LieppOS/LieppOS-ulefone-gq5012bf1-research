#!/usr/bin/env python3
"""
st21-relr.py — decode Android/LLVM `.relr.dyn` (packed relative relocations).

Why: `nfc_nci.st21nfc.st.so` is linked with `-fuse-ld=lld --pack-dyn-relocs=relr`
(aarch64 relocation packing). `readelf -r` prints nothing for those, so pointer
fields in `.got`/`.data.rel.ro` read as zero and every "which string does this
global point at" question dead-ends unless RELR is decoded by hand. RELR entries
carry no addend or symbol: a set bit just means "the 8 bytes at this vaddr get
load_base added", i.e. the *stored* value is the static target. This tool expands
the runs so those slots become resolvable statically.

Usage:
  st21-relr.py <blob>                 # list every RELR target address
  st21-relr.py <blob> <vaddr>         # is <vaddr> a RELR slot? (and its stored value)
"""
import struct
import subprocess
import sys


def sections(path):
    data = open(path, "rb").read()
    e_shoff, = struct.unpack_from("<Q", data, 0x28)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", data, 0x3a)
    shstr_off = None
    off = e_shoff + e_shstrndx * e_shentsize
    _t, _f, _a, so, _sz = struct.unpack_from("<IIQQQ", data, off)[0:5]
    shstr_off = so
    out = {}
    for i in range(e_shnum):
        o = e_shoff + i * e_shentsize
        sh_name, sh_type, _fl, sh_addr, sh_offset, sh_size = struct.unpack_from("<IIQQQQ", data, o)
        name = data[shstr_off + sh_name: data.index(b"\x00", shstr_off + sh_name)].decode()
        out[name] = (sh_addr, sh_offset, sh_size, sh_type)
    return data, out


def main(argv):
    blob = argv[1]
    want = int(argv[2], 16) if len(argv) > 2 else None
    data, secs = sections(blob)
    if ".relr.dyn" not in secs:
        sys.exit("no .relr.dyn (plain RELA build?)")
    addr, off, size, _t = secs[".relr.dyn"]
    ents = [struct.unpack_from("<Q", data, off + 8 * i)[0] for i in range(size // 8)]
    SHIFT = 3  # 64-bit words -> 8 bytes, log2
    targets, base = [], None
    for e in ents:
        if e & 1:
            base = e & ~1
            targets.append(base)
        else:
            assert base is not None, "RELR bitmap before any run address"
            for bit in range(SHIFT + 1, 64):
                if (e >> bit) & 1:
                    targets.append(base + (1 << SHIFT) * bit)
    print(f"### .relr.dyn @0x{addr:x} size=0x{size:x}: {len(ents)} entries -> {len(targets)} relocated slots")
    if want is None:
        lo = min(targets) if targets else 0
        print("  first 24 targets: " + ", ".join(hex(t) for t in targets[:24]))
        print(f"  range: 0x{lo:x}..0x{max(targets):x}")
    else:
        print(f"  0x{want:x} RELR slot: {want in targets}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
