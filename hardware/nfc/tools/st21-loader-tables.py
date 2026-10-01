#!/usr/bin/env python3
"""
st21-loader-tables.py — decode the ST21NFC HAL driver's embedded loader/patch
descriptors so "which firmware/patch revisions does this build accept" is a
reproducible query.

Why: nfc_nci.st21nfc.st.so keeps the factory loader and every supported patch in
its own .rodata, described by a five-symbol tuple per generation:

    loader_<gen>_patch            the patch image itself (embedded, not a pointer:
                                  see st21-data-graph.py — 0 relocations in its
                                  window, and the first word is a firmware record
                                  header, not an address)
    loader_<gen>_patch_size_tab   per-chunk table companion (108 B == cmd_nb, also
                                  embedded and high-entropy; its name is a label,
                                  not a spec, so the words are printed, never summed)
    loader_<gen>_patch_cmd_nb     number of download commands
    loader_<gen>_patch_AuthKeyId  the AuthKeyId (authentication gate) it needs
    loader_<gen>_patch_version    the FW/patch revision it produces

`ft_cmd_HwReset`'s loader picks a tuple by the chip's reported revision/type and
rejects anything not in the table ("integrates unknown patch NFC FW -- rejected"),
so the tuples + their byte extents are exactly the policy an offline reimplementation
has to satisfy. Spans are derived from the section layout (the next symbol of
increasing address bounds the image), which is why the sizes are reported as
"up to <sym>" rather than as assertions.

Usage: st21-loader-tables.py [blob] [--tab-dump N]
"""
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.normpath(os.path.join(HERE, "..", "analysis", "st21-gemini-audit",
                                      "runtime-blobs", "nfc_nci.st21nfc.st.so"))
GEN = re.compile(r"^loader_(?P<gen>[A-Za-z0-9]+)_(?P<what>patch|patch_size_tab|patch_cmd_nb|patch_AuthKeyId|patch_version)$")
PTR_SECTION_RE = re.compile(r"\.(rodata|data|data\.rel\.ro|bss)$")


def elf(path):
    data = open(path, "rb").read()
    e_phoff, = struct.unpack_from("<Q", data, 0x20)
    esz, num = struct.unpack_from("<HH", data, 0x36)
    loads = []
    for i in range(num):
        o = e_phoff + i * esz
        p_type, _f, p_off, p_va, _p, p_fs, p_ms, _a = struct.unpack_from("<IIQQQQQQ", data, o)
        if p_type == 1:
            loads.append((p_va, p_off, p_fs, p_ms))
    return data, loads


def read(data, loads, va, size):
    for v, o, fs, ms in loads:
        if v <= va and va + size <= v + fs:
            return data[o + (va - v): o + (va - v) + size]
    return None


def u32(data, loads, va):
    b = read(data, loads, va, 4)
    return None if b is None else struct.unpack("<I", b)[0]


def rodata_end(path):
    """End vaddr of .rodata, so windows past it are reported as clamped."""
    data = open(path, "rb").read()
    e_shoff, = struct.unpack_from("<Q", data, 0x28)
    esz, num, shstrx = struct.unpack_from("<HHH", data, 0x3a)
    so = struct.unpack_from("<IIQQQQ", data, e_shoff + shstrx * esz)[4]  # sh_offset
    for i in range(num):
        o = e_shoff + i * esz
        nm, _t, _fl, va, _off, size = struct.unpack_from("<IIQQQQ", data, o)
        end = data.index(b"\x00", so + nm)
        if data[so + nm:end].decode("latin1") == ".rodata":
            return va + size
    return 1 << 63


def main(argv):
    blob = argv[1] if len(argv) > 1 and not argv[1].startswith("--") else DEFAULT
    out = subprocess.run(["nm", "-D", "--defined-only", blob], capture_output=True, text=True).stdout
    syms = []
    for line in out.splitlines():
        m = re.match(r"^([0-9a-f]{16}) (\S) (.*)$", line)
        if m:
            syms.append((int(m.group(1), 16), m.group(2), m.group(3)))
    syms.sort()
    addrs = [s[0] for s in syms]

    data, loads = elf(blob)
    ro_end = rodata_end(blob)
    print(f"### {os.path.basename(blob)}: loader/patch descriptors "
          f"({sum(1 for _, _, n in syms if GEN.match(n))} symbols)")
    gens = {}
    for a, t, n in syms:
        m = GEN.match(n)
        if m:
            gens.setdefault(m.group("gen"), {})[m.group("what")] = (a, t)
    for gen, d in sorted(gens.items()):
        print(f"\n  generation {gen}:")
        for what in ("patch_version", "patch_cmd_nb", "patch_AuthKeyId", "patch", "patch_size_tab"):
            if what not in d:
                continue
            a, t = d[what]
            note = ""
            if t in "RDA" and what in ("patch_cmd_nb", "patch_AuthKeyId", "patch_version"):
                v = u32(data, loads, a)
                note = f" = 0x{v:x} ({v})" if v is not None else " = <unmapped>"
            elif t == "B":
                note = "  (.bss: filled at runtime)"
            nxt = [x for x in addrs if x > a]
            span = f"window<=0x{nxt[0] - a:x}" if nxt and what in ("patch", "patch_size_tab") else ""
            print(f"    {what:<18} @0x{a:x} [{t}]{note} {span}".rstrip())
        # Windows are gaps to the next symbol in address order, clamped to the end
        # of .rodata: they bound an object from above and must not be read as its
        # declared length (which is why the raw words are printed, not summed).
        for what in ("patch", "patch_size_tab"):
            if what not in d:
                continue
            a, t = d[what]
            nxt = min((x for x in addrs if x > a), default=a)
            window = max(min(nxt, ro_end) - a, 0)
            raw = read(data, loads, a, window) or b""
            words = struct.unpack(f"<{len(raw) // 4}I", raw[:(len(raw) // 4) * 4])
            print(f"      {what} window 0x{a:x}..0x{a + window:x} = {window} B "
                  f"({len(words)} u32 words) first={[hex(v) for v in words[:4]]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
