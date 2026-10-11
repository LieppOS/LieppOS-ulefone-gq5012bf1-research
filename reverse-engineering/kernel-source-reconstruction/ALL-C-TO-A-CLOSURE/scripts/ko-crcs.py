#!/usr/bin/env python3
"""Print export CRCs (__crc_*) of a module. Works on a PRIVATE COPY: reads ELF bytes only (no tool writes).

usage: ko-crcs.py MODULE.ko   -> "0xCRC<TAB>symbol" lines
"""
import struct, sys

b = open(sys.argv[1], 'rb').read()
shoff, = struct.unpack_from('<Q', b, 0x28); shentsize, shnum, shstrndx = struct.unpack_from('<HHH', b, 0x3a)
secs = [struct.unpack_from('<IIQQQQIIQQ', b, shoff + i * shentsize) for i in range(shnum)]
names = secs[shstrndx]
nm = lambda off, base: b[base + off:b.index(b'\0', base + off)].decode()
shname = [nm(s[0], names[4]) for s in secs]
sym = next(s for s in secs if s[1] == 2); strs = secs[sym[6]]
for i in range(sym[5] // 24):
    st_name, info, other, shndx, value, size = struct.unpack_from('<IBBHQQ', b, sym[4] + i * 24)
    n = nm(st_name, strs[4])
    if n.startswith('__crc_') and 0 < shndx < len(secs):
        sec = secs[shndx]
        crc, = struct.unpack_from('<I', b, sec[4] + value)
        print(f'0x{crc:08x}\t{n[6:]}')
