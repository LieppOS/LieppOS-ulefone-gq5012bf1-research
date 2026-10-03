#!/usr/bin/env python3
"""ko-pair-parity.py — full static parity between two kernel module ELFs.

Canonical GQ5012BF1 verification tool. Callers must state the proof operands
(e.g. A = shipped stock .ko, B = unchanged-donor exact-GKI rebuild).

Axes: sections, per-section bytes, per-function bytes, data objects,
import MODVERSION CRCs (__versions), export names/licences/CRCs
(__ksymtab*/__kcrctab*), .modinfo, relocations.
"""
import struct, sys, hashlib, collections

SHN_ABS = 0xfff1

class KO:
    def __init__(self, path):
        self.path = path
        self.b = open(path, 'rb').read()
        e = self.b
        assert e[:4] == b'\x7fELF' and e[4] == 2, "need ELF64"
        shentsize, shnum, shstrndx = struct.unpack_from('<HHH', e, 0x3a)
        shoff, = struct.unpack_from('<Q', e, 0x28)
        raw = []
        for i in range(shnum):
            o = shoff + i * shentsize
            name, typ, flags, addr, off, size, link, info, align, entsz = \
                struct.unpack_from('<IIQQQQIIQQ', e, o)
            raw.append(dict(name=name, type=typ, off=off, size=size, link=link,
                           info=info, align=align, entsz=entsz))
        so = raw[shstrndx]['off']
        for s in raw:
            s['n'] = self.cstr(so + s['name'])
        self.secs = raw
        self.symtab = next((s for s in raw if s['type'] == 2), None)
        self.syms = []
        if self.symtab:
            st = self.secs[self.symtab['link']]
            strb = e[st['off']:st['off'] + st['size']]
            for i in range(self.symtab['size'] // 24):
                o = self.symtab['off'] + i * 24
                nm, info_, other, shndx, val, size = struct.unpack_from('<IBBHQQ', e, o)
                self.syms.append(dict(n=self.cstr(strb, nm), info=info_, other=other,
                                      shndx=shndx, val=val, size=size))

    def cstr(self, b_or_off, off=None):
        if off is None:
            b, o = self.b, b_or_off
        else:
            b, o = b_or_off, off
        z = b.find(b'\0', o)
        return b[o:z].decode(errors='replace')

    def sec(self, n):
        for s in self.secs:
            if s['n'] == n:
                return s
        return None

    def data(self, n):
        s = self.sec(n)
        if not s or s['type'] == 8:
            return b''
        return self.b[s['off']:s['off'] + s['size']]

def versions(ko):
    s = ko.sec('__versions')
    out = {}
    if not s:
        return out, None
    raw = ko.b[s['off']:s['off'] + s['size']]
    for esz in (64, 40, 72, 32):
        if s['size'] % esz:
            continue
        ok, d = True, {}
        for i in range(s['size'] // esz):
            crc, = struct.unpack_from('<Q', raw, i * esz)
            nm = raw[i * esz + 8:(i + 1) * esz].split(b'\0')[0].decode(errors='replace')
            if not nm or any(ord(c) > 126 or c.isspace() for c in nm):
                ok = False; break
            d[nm] = crc & 0xffffffff
        if ok:
            return d, esz
    return out, None

def ksymtab(ko):
    """export name -> licence bucket"""
    out = {}
    for secname, lic in (('__ksymtab', 'EXPORT_SYMBOL'), ('__ksymtab_gpl', 'EXPORT_SYMBOL_GPL')):
        s, rs = ko.sec(secname), ko.sec('.rela' + secname)
        if not s:
            continue
        for i in range(s['size'] // 8):
            if rs and i * 24 < rs['size']:
                _, r_info, _ = struct.unpack_from('<QQq', ko.b, rs['off'] + i * 24)
                idx = r_info >> 32
                name = ko.syms[idx]['n'] if idx < len(ko.syms) else '?'
            else:
                p, = struct.unpack_from('<Q', ko.b, s['off'] + i * 8)
                name = ko.cstr(p)
            out[name] = lic
    return out

def kcrctab(ko):
    """export name -> CRC via __kcrctab* parallel to __ksymtab*"""
    out = {}
    for cs, ks in (('__kcrctab', '__ksymtab'), ('__kcrctab_gpl', '__ksymtab_gpl')):
        c, k = ko.sec(cs), ko.sec(ks)
        if not c or not k or c['size'] != k['size']:
            continue
        n = c['size'] // 8
        for i in range(n):
            off = k['off'] + i * 24
            # resolve names through the rela of __ksymtab when present
            crc, = struct.unpack_from('<Q', ko.b, c['off'] + i * 8)
            out.setdefault(('gpl' if 'gpl' in cs else 'gpl?' , i), crc & 0xffffffff)
    return out

def kcrctab_named(ko):
    """symbol->crc mapping aligned via .rela__ksymtab* ordering."""
    out = {}
    for cs, ks in (('__kcrctab', '__ksymtab'), ('__kcrctab_gpl', '__ksymtab_gpl')):
        c, k = ko.sec(cs), ko.sec(ks)
        rs = ko.sec('.rela' + ks)
        if not c or not k or c['size'] != k['size']:
            continue
        for i in range(k['size'] // 8):
            crc, = struct.unpack_from('<Q', ko.b, c['off'] + i * 8)
            if rs:
                _, r_info, _ = struct.unpack_from('<QQq', ko.b, rs['off'] + i * 24)
                idx = r_info >> 32
                name = ko.syms[idx]['n'] if idx < len(ko.syms) else '?'
            else:
                p, = struct.unpack_from('<Q', ko.b, k['off'] + i * 8)
                name = ko.cstr(p)
            out[name] = crc & 0xffffffff
    return out

def main(a_path, b_path):
    A, B = KO(a_path), KO(b_path)
    print(f"A = {a_path}")
    print(f"B = {b_path}")
    print(f"A sha256 {hashlib.sha256(A.b).hexdigest()}")
    print(f"B sha256 {hashlib.sha256(B.b).hexdigest()}")

    an = {s['n']: s for s in A.secs if s['n']}
    bn = {s['n']: s for s in B.secs if s['n']}
    one = sorted(set(an) ^ set(bn))
    print(f"\nSECTIONS: A={len(an)} B={len(bn)} one-sided={len(one)}")
    for n in one:
        s = an.get(n) or bn.get(n)
        print(f"  one-sided {'A' if n in an else 'B'} {n} size={s['size']}")
    dsz = sorted(n for n in set(an) & set(bn) if an[n]['size'] != bn[n]['size'])
    print(f"  size-differing shared: {dsz}")
    SKIP = {'.note.gnu.build-id', '.note.gnu.property', '.comment', '.modinfo',
            '.llvm_addrsig', '__versions', '.symtab', '.strtab', '.shstrtab',
            '.debug_frame', '__mcount_loc', '.rela__versions'}
    exact = tot = 0; bad = []
    for n in sorted(set(an) & set(bn)):
        if n in SKIP or an[n]['type'] == 8 or bn[n]['type'] == 8:
            continue
        tot += 1
        if A.data(n) == B.data(n):
            exact += 1
        else:
            bad.append((n, an[n]['size'], bn[n]['size']))
    print(f"  content sections byte-exact {exact}/{tot}: {bad if bad else 'no diffs'}")

    def bucket(ko, s):
        out = {}
        for sym in ko.syms:
            if sym['shndx'] in (0, SHN_ABS) or (sym['size'] == 0 and sym['info'] & 0xf != 2):
                continue
            sec = ko.secs[sym['shndx']]
            if not sec['n'].startswith(('.text', '.init.text', '.exit.text')):
                continue
            d = ko.b[sec['off'] + sym['val']: sec['off'] + sym['val'] + sym['size']]
            out[sym['n']] = (sym['size'], hashlib.sha256(d).hexdigest()[:16])
        return out
    fa, fb = bucket(A, 't'), bucket(B, 't')
    shared = sorted(set(fa) & set(fb))
    sb = sum(1 for k in shared if fa[k] == fb[k])
    ss = sum(1 for k in shared if fa[k][0] == fb[k][0])
    print(f"\nFUNCTIONS: A={len(fa)} B={len(fb)} shared={len(shared)} size-identical={ss} byte-identical={sb}")
    for k in shared:
        if fa[k] != fb[k]:
            print(f"  FUNC-DIFF {k}: A size={fa[k][0]} B size={fb[k][0]} bytes-differ={fa[k][1]!=fb[k][1]}")
    for k in sorted(set(fa) ^ set(fb)):
        print(f"  FUNC-ONE-SIDED {k} only in {'A' if k in fa else 'B'}")

    def objs(ko):
        out = {}
        for sym in ko.syms:
            if sym['shndx'] in (0, SHN_ABS) or sym['size'] == 0:
                continue
            sec = ko.secs[sym['shndx']]
            if sec['n'].startswith(('.text', '.init.text', '.exit.text')):
                continue
            if sym['n'] in ('__this_module',):
                continue
            h = '-' if sec['type'] == 8 else hashlib.sha256(
                ko.b[sec['off'] + sym['val']: sec['off'] + sym['val'] + sym['size']]).hexdigest()[:16]
            out[sym['n']] = (sec['n'], sym['size'], h)
        return out
    oa, ob = objs(A), objs(B)
    osh = sorted(set(oa) & set(ob))
    msm = [k for k in osh if oa[k][:2] != ob[k][:2]]
    bym = [k for k in osh if oa[k] != ob[k]]
    print(f"\nDATA OBJECTS: A={len(oa)} B={len(ob)} shared={len(osh)} (sec,size)-diff={len(msm)} byte-diff={len(bym)}")
    for k in bym[:20]:
        tag = 'SIZE' if oa[k][:2] != ob[k][:2] else 'bytes'
        print(f"  OBJ-{tag} {k}: A={oa[k]} B={ob[k]}")
    for k in sorted(set(oa) ^ set(ob)):
        print(f"  OBJ-ONE-SIDED {k} only in {'A' if k in oa else 'B'}")

    va, sza = versions(A); vb, szb = versions(B)
    ish = sorted(set(va) & set(vb))
    bc = [(k, hex(va[k]), hex(vb[k])) for k in ish if va[k] != vb[k]]
    print(f"\nIMPORTS (__versions entry={sza}/{szb}): A={len(va)} B={len(vb)} shared={len(ish)} "
          f"name-diff={sorted(set(va) ^ set(vb))} CRC-mismatch={bc}")

    ea, eb = ksymtab(A), ksymtab(B)
    ca, cb = kcrctab_named(A), kcrctab_named(B)
    esh = sorted(set(ea) & set(eb))
    lic = [(k, ea[k], eb[k]) for k in esh if ea[k] != eb[k]]
    bcx = [(k, hex(ca[k]), hex(cb[k])) for k in esh if k in ca and k in cb and ca[k] != cb[k]]
    print(f"\nEXPORTS: A={len(ea)} B={len(eb)} shared={len(esh)} name-diff={sorted(set(ea) ^ set(eb))} licence-diff={lic}")
    print(f"  export CRC comparable={sum(1 for k in esh if k in ca and k in cb)} CRC-mismatch={bcx}")

    def mi(ko):
        return {kv.decode().split('=', 1)[0]: kv.decode().split('=', 1)[1]
                for kv in ko.data('.modinfo').split(b'\0') if b'=' in kv}
    ma, mb = mi(A), mi(B)
    print("\n.MODINFO:")
    for k in sorted(set(ma) | set(mb)):
        if ma.get(k) != mb.get(k):
            print(f"  {k}: A={ma.get(k)!r} B={mb.get(k)!r}")

    def relas(ko):
        out = {}
        for s in ko.secs:
            if s['type'] != 4:
                continue
            c = collections.Counter()
            for i in range(s['size'] // 24):
                _, r_info, _ = struct.unpack_from('<QQq', ko.b, s['off'] + i * 24)
                idx = r_info >> 32
                c[ko.syms[idx]['n'] if idx < len(ko.syms) else '?'] += 1
            out[s['n']] = (s['size'] // 24, c, ko.data(s['n']))
        return out
    ra, rb = relas(A), relas(B)
    print("\nRELA:")
    for n in sorted(ra):
        ta, tb = ra[n], rb.get(n)
        if tb is None or ta[0] != tb[0]:
            print(f"  {n}: A={ta[0]} B={'MISSING' if tb is None else tb[0]}")
        elif ta[2] != tb[2]:
            d = {k: (ta[1][k], tb[1][k]) for k in set(ta[1]) | set(tb[1]) if ta[1][k] != tb[1][k]}
            print(f"  {n}: {ta[0]} entries, byte-differs, target-count diff={d}")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
