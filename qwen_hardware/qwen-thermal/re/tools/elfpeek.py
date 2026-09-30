#!/usr/bin/env python3
"""Static ELF helper: dereference relocated data symbols (RELATIVE relocations)
and dump data at vaddrs. Usage: elfpeek.py <lib.so> [nm-grep-regex]"""
import struct, subprocess, sys

class ELF:
    def __init__(self, path):
        self.d = open(path, 'rb').read()
        d = self.d
        assert d[:4] == b'\x7fELF' and d[4] == 2
        self.e_shoff = struct.unpack_from('<Q', d, 0x28)[0]
        self.e_shentsize = struct.unpack_from('<H', d, 0x3a)[0]
        self.e_shnum = struct.unpack_from('<H', d, 0x3c)[0]
        self.secs = []  # (name, type, addr, off, size, link)
        shstrndx = struct.unpack_from('<H', d, 0x3e)[0]
        for i in range(self.e_shnum):
            o = self.e_shoff + i * self.e_shentsize
            sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link = struct.unpack_from('<IIQQQQI', d, o)
            self.secs.append([sh_name, sh_type, sh_addr, sh_offset, sh_size, sh_link])
        ss = self.secs[shstrndx]
        def sname(n):
            b = ss[3] + n; e = d.index(b'\0', b); return d[b:e].decode()
        for s in self.secs: s.append(sname(s[0]))
        self.rela = {}
        for s in self.secs:
            if s[1] == 4:  # SHT_RELA
                for k in range(s[4] // 24):
                    r_off, r_info, r_add = struct.unpack_from('<QQQ', d, s[3] + k * 24)
                    self.rela[r_off] = r_add
    def v2o(self, v):
        for s in self.secs:
            if s[2] and s[1] != 8 and s[2] <= v < s[2] + s[4]:  # not SHT_NOBITS
                return s[3] + (v - s[2])
        return None
    def cstr(self, v):
        o = self.v2o(v)
        if o is None: return None
        e = self.d.index(b'\0', o); return self.d[o:e].decode('latin1')
    def deref(self, v):
        o = self.v2o(v)
        ptr = struct.unpack_from('<Q', self.d, o)[0] if o is not None else 0
        tgt = self.rela.get(v, ptr)
        return ptr, tgt

def dynsyms(path, rx):
    out = subprocess.run(['nm', '-D', '--defined-only', path], capture_output=True, text=True).stdout
    import re
    for line in out.splitlines():
        p = line.split()
        if len(p) == 3 and re.search(rx, p[2]):
            yield p[2], int(p[0], 16), p[1]

if __name__ == '__main__':
    path = sys.argv[1]
    rx = sys.argv[2] if len(sys.argv) > 2 else 'pck_name'
    e = ELF(path)
    for name, v, typ in sorted(dynsyms(path, rx)):
        ptr, tgt = e.deref(v)
        s = e.cstr(tgt) if tgt else None
        print(f"{name:48s} [{typ}] ptr={ptr:#x} addend={tgt:#x} -> {s!r}")
