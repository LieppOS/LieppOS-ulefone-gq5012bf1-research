#!/usr/bin/env python3
"""Minimal read-only ELF64 (AArch64 relocatable .ko) reader: sections, symbols, RELA.

No third-party dependencies.  Used by the camera EEPROM decoders.
"""
import struct


class Ko:
    def __init__(self, path):
        self.path = path
        self.b = b = open(path, 'rb').read()
        assert b[:4] == b'\x7fELF' and b[4] == 2 and b[5] == 1
        (self.shoff,) = struct.unpack_from('<Q', b, 0x28)
        shentsize, shnum, shstrndx = struct.unpack_from('<HHH', b, 0x3a)
        self.sh = []
        for i in range(shnum):
            name, typ, flags, addr, off, size, link, info, align, entsize = struct.unpack_from(
                '<IIQQQQIIQQ', b, self.shoff + i * shentsize)
            self.sh.append(dict(name=name, type=typ, flags=flags, off=off, size=size,
                                link=link, info=info, entsize=entsize, idx=i))
        stro = self.sh[shstrndx]['off']
        for s in self.sh:
            s['name'] = self._str(stro, s['name'])
        self.secs = {s['name']: s for s in self.sh}
        self._syms()
        self._relas()

    def _str(self, base, off):
        e = self.b.index(b'\0', base + off)
        return self.b[base + off:e].decode('latin1')

    def data(self, sec):
        s = self.secs[sec] if isinstance(sec, str) else self.sh[sec]
        if s['type'] == 8:  # NOBITS
            return bytes(s['size'])
        return self.b[s['off']:s['off'] + s['size']]

    def _syms(self):
        st = self.secs['.symtab']
        strtab = self.sh[st['link']]['off']
        self.syms = []
        for i in range(st['size'] // 24):
            name, info, other, shndx, value, size = struct.unpack_from('<IBBHQQ', self.b, st['off'] + i * 24)
            self.syms.append(dict(i=i, name=self._str(strtab, name), type=info & 15, bind=info >> 4,
                                  shndx=shndx, value=value, size=size,
                                  sec=self.sh[shndx]['name'] if 0 < shndx < len(self.sh) else None))

    def _relas(self):
        """relocs[target_section_name] = sorted list of (offset, type, sym, addend)"""
        self.relocs = {}
        for s in self.sh:
            if s['type'] != 4:
                continue
            tgt = self.sh[s['info']]['name']
            out = []
            for i in range(s['size'] // 24):
                off, info, add = struct.unpack_from('<QQq', self.b, s['off'] + i * 24)
                out.append((off, info & 0xffffffff, self.syms[info >> 32], add))
            self.relocs[tgt] = sorted(out, key=lambda r: r[0])

    def reloc_at(self, sec, off):
        for r in self.relocs.get(sec, []):
            if r[0] == off:
                return r
        return None

    def cstr(self, sec, off):
        d = self.data(sec)
        e = d.index(b'\0', off)
        return d[off:e].decode('latin1')

    def describe_ptr(self, sec, off):
        """Resolve a 64-bit pointer field stored at sec+off via its relocation."""
        r = self.reloc_at(sec, off)
        if r is None:
            v = struct.unpack_from('<Q', self.data(sec), off)[0]
            return None if v == 0 else hex(v)
        _, typ, sym, add = r
        if sym['type'] == 3:  # SECTION symbol
            if sym['sec'] and sym['sec'].startswith('.rodata.str'):
                return 'str:' + self.cstr(sym['sec'], add)
            target = [s for s in self.syms if s['sec'] == sym['sec'] and s['type'] in (1, 2)
                      and s['value'] <= add < s['value'] + max(s['size'], 1)]
            if target:
                t = target[0]
                return t['name'] + ('' if add == t['value'] else '+%d' % (add - t['value'])) + '@' + sym['sec'] + ':0x%x' % t['value']
            return '%s+0x%x' % (sym['sec'], add)
        return sym['name'] + ('' if add == 0 else '+%d' % add)
