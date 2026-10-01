#!/usr/bin/env python3
"""
st21-data-graph.py — what do the loader's data symbols actually contain?

Why: `audit/loader-tables.txt` shows that this generation of
`nfc_nci.st21nfc.st.so` exports the firmware patch tables (`loader_RA*_patch*`)
as *data* symbols rather than reading them out of a file, and `firmware-loader.md`
(Rev 1) inferred "the patch payload ships inside the HAL" from that alone. The
alternative reading has to be excluded: a table symbol in `.data.rel.ro`/`.got`
can equally well be a *pointer array* that the dynamic loader fills in at load
time, in which case the payload would still live in a file. The two cases are only
distinguishable by looking at the stored words *and* at whether .rela.dyn carries
relocations for those bytes. That is what this tool answers, per symbol.

For every dynamically-visible data symbol (optionally filtered) it prints, per
8-byte slot: the file byte pattern, and any R_AARCH64_ABS64/ABS32 addend plus
the literal that addend addresses. A symbol whose slots are relocations to
strings is an indirection table; a symbol whose slots are non-relocating high-
entropy words is an embedded payload.

Usage: st21-data-graph.py <blob> [symbol-regex]
"""
import re
import struct
import subprocess
import sys


def elf(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x7fELF' and struct.unpack_from('<H', d, 16)[0] == 3, 'not aarch64 ELF'
    phoff, = struct.unpack_from('<Q', d, 0x20)
    phentsize, phnum = struct.unpack_from('<HH', d, 0x36)
    loads = []
    for i in range(phnum):
        p = phoff + i * phentsize
        # Elf64_Phdr: type, flags, offset, vaddr, paddr, filesz, memsz, align
        typ, _fl, off, va, _pa, fsz, msz, _al = struct.unpack_from('<IIQQQQQQ', d, p)
        if typ == 1:                                                   # PT_LOAD
            loads.append((va, off, fsz, msz))
    shoff, = struct.unpack_from('<Q', d, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from('<HHH', d, 0x3a)
    base = shoff + shstrndx * shentsize
    strtab = struct.unpack_from('<Q', d, base + 0x18)[0]
    secs = {}
    for i in range(shnum):
        s = shoff + i * shentsize
        nm, typ = struct.unpack_from('<II', d, s)
        # Elf64_Shdr: name, type, flags, addr, offset, size, …
        addr, off, size = struct.unpack_from('<QQQ', d, s + 0x10)
        name = d[strtab + nm:d.index(b'\0', strtab + nm)].decode('utf-8', 'replace')
        secs[name] = (addr, off, size, typ)
    return d, loads, secs


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        return 2
    blob = argv[1]
    pat = re.compile(argv[2]) if len(argv) > 2 else re.compile(r'^(loader|DW|s_)')
    d, loads, secs = elf(blob)

    def window(va, n):
        for base, off, fsz, msz in loads:
            if base <= va < base + max(fsz, msz):
                p = off + (va - base)
                return d[p:p + n]
        return b''

    def cstr(va):
        w = window(va, 256)
        n = w.find(b'\0')
        w = w[:len(w) if n < 0 else n]
        return (w.decode('utf-8', 'backslashreplace')
                if w and all(32 <= b < 127 for b in w) and len(w) > 2 else None)

    rela = secs.get('.rela.dyn')
    relocs = {}
    if rela:
        addr, off, size, _ = rela
        for i in range(size // 24):
            rva, rtyp, radd = struct.unpack_from('<QQq', d, off + i * 24)
            if rtyp in (257, 258, 259, 1024, 1025, 1026):              # ABS64/ABS32/PAIR/GLOB_DAT
                relocs[rva] = radd

    out = subprocess.run(['nm', '-D', '--defined-only', '-S', '-v', blob],
                         capture_output=True, text=True).stdout
    syms = []
    for line in out.splitlines():
        m = re.match(r'^([0-9a-f]+) ([0-9a-f]+) (\S) (.*)$', line)
        if m and pat.search(m.group(4)):
            syms.append((int(m.group(1), 16), int(m.group(2), 16), m.group(3), m.group(4)))

    def section_of(va):
        for name, (a, _o, size, _t) in secs.items():
            if size and a <= va < a + size and not name.startswith('.debug'):
                return name
        return '?'

    print(f"### {blob}: data-symbol contents ({len(syms)} symbols matched)")
    for addr, size, typ, name in syms:
        if typ not in 'bdrBDR':
            continue
        if size and size < 8:                       # scalar: version / cmd_nb / AuthKeyId
            w = window(addr, size)
            print(f"\n  {name} @0x{addr:x} [{section_of(addr)}] type={typ} size={size}"
                  f" = 0x{int.from_bytes(w, 'little'):x} ({int.from_bytes(w, 'little')})"
                  f" — {sum(1 for i in range(len(w)) if addr + i in relocs)} relocated byte(s)")
            continue
        n = min(size or 8, 64)
        raw = window(addr, n)
        words = [struct.unpack('<Q', raw[i:i + 8])[0] for i in range(0, len(raw) - 7, 8)]
        rel = sum(1 for i in range(n // 8) if addr + 8 * i in relocs)
        if len(raw) < n:                             # .bss / beyond p_filesz
            verdict = ("zero-filled at load time -> runtime slot this loader writes into, "
                       "contents carry no information here")
        else:
            verdict = (f"{rel} of {len(words)} slots relocated -> indirection table" if rel else
                       "0 relocated -> embedded payload bytes, not a pointer array")
        if name.endswith('_size_tab') and not rel:
            verdict += "; the `_size_tab` name is a label, not a spec — do not sum it as sizes"
        print(f"\n  {name} @0x{addr:x} [{section_of(addr)}] type={typ} size={size}"
              f" — {len(words)} slot(s) shown of {(size or 8)//8}, {verdict}")
        for i, w in enumerate(words[:8]):
            r = relocs.get(addr + 8 * i)
            tgt = w if w else r
            tag = ''
            if r is not None:
                tag += f" rel->0x{r:x}"
            if tgt:
                s = cstr(tgt)
                tag += f" -> 0x{tgt:x}" + (f" {s!r}" if s else " (not a literal)")
            print(f"      +0x{8*i:02x} = 0x{w:016x}{tag}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
