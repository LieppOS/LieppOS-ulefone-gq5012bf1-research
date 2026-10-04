#!/usr/bin/env python3
"""ko-pair-parity.py — full static parity between two kernel module ELFs.

Canonical GQ5012BF1 verification tool.  Callers must state the proof operands
(e.g. A = shipped stock .ko, B = unchanged-donor exact-GKI rebuild).

Axes, kept deliberately separate so one is never mistaken for another:
  sections            one-sided / size / byte-exact content
  functions           per-function size + bytes (kallsyms-visible bodies)
  data objects        per-object section+size and bytes
  imports             __versions name + CRC
  exports             __ksymtab* name + licence bucket, __kcrctab* CRC
  .modinfo            key-by-key
  relocations         SEMANTIC: (r_offset, r_type, target symbol NAME, r_addend).
                      Symbol-table *indices* are never compared: an out-of-tree
                      rebuild orders local symbols differently from MTK's in-tree
                      build, so raw RELA bytes can differ while the semantics are
                      identical.  Raw byte-equality is reported separately.
  string tables       which literal strings actually differ, and which of those
                      are only out-of-tree build paths
  CRC stubs           __UNIQUE_ID_<name> materialised by kbuild and which of them
                      are actually referenced by a relocation

usage: ko-pair-parity.py A.ko B.ko
"""
import hashlib
import struct
import sys

SHN_ABS = 0xfff1
STT_FUNC, STT_OBJECT, STT_SECTION = 2, 1, 3

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
        self.sec_by_name = {s['n']: s for s in raw if s['n']}
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
        return self.sec_by_name.get(n)

    def secs_by_prefix(self, prefix):
        return [s for s in self.secs if s['n'].startswith(prefix)]

    def data(self, n):
        s = self.sec(n)
        if not s or s['type'] == 8:
            return b''
        return self.b[s['off']:s['off'] + s['size']]

    def rela_entries(self, s):
        for i in range(s['size'] // 24):
            yield struct.unpack_from('<QQq', self.b, s['off'] + i * 24)

    def sym_name(self, idx):
        return self.syms[idx]['n'] if idx < len(self.syms) else '?'


def functions(ko):
    out = {}
    for sym in ko.syms:
        if sym['shndx'] in (0, SHN_ABS) or (sym['size'] == 0 and sym['info'] & 0xf != STT_FUNC):
            continue
        sec = ko.secs[sym['shndx']]
        if not sec['n'].startswith(('.text', '.init.text', '.exit.text')):
            continue
        d = ko.b[sec['off'] + sym['val']: sec['off'] + sym['val'] + sym['size']]
        out[sym['n']] = (sym['size'], hashlib.sha256(d).hexdigest()[:16], d)
    return out


def objects(ko):
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


def _tab_base(rela_name, kind):
    """`.rela___ksymtab_gpl+<first>` -> `__ksymtab_gpl`.

    lld names a merged relocation section `.rela` + the merged data-section name,
    and that merged name itself has the leading underscores of every input folded
    into one run, so the underscore count is not stable.  Rebuild the canonical
    `__<kind>[_gpl]` name instead of trusting underscore counts.
    """
    head = rela_name[len('.rela'):].split('+')[0]
    return '__' + head.lstrip('_')


def exports(ko):
    """export symbol name -> (licence bucket, CRC or None).

    EXPORT_SYMBOL emits one `__ksymtab_<name>` (or `__ksymtab_gpl_<name>`) input
    section per export; lld merges them into one output section whose name is the
    merged input names joined by '+', so the *section name* cannot identify an
    export.  The relocations can: every export slot relocates to its own FUNC
    symbol, so export names are the FUNC targets of `.rela__ksymtab*` in tab
    order.  CRCs come from the parallel `__kcrctab*` tab, paired positionally
    (kbuild emits both in the same per-symbol order); the entry width is derived
    from tab size / export count, never guessed.
    """
    out = {}
    for rs in ko.secs:
        if '.rela' not in rs['n'] or 'ksymtab' not in rs['n'] or 'strings' in rs['n']:
            continue
        n = _tab_base(rs['n'], 'ksymtab')
        if ko.sec(n) is None:
            continue
        lic = 'EXPORT_SYMBOL_GPL' if '_gpl' in n else 'EXPORT_SYMBOL'
        is_func = {y['n'] for y in ko.syms if y['info'] & 0xf == STT_FUNC}
        names = [ko.sym_name(i >> 32) for _, i, _ in ko.rela_entries(rs)
                 if ko.sym_name(i >> 32) in is_func]
        cs = ko.sec(n.replace('__ksymtab', '__kcrctab'))
        esz = 0
        if cs is not None and names and cs['size'] % len(names) == 0:
            esz = cs['size'] // len(names)
            if esz not in (4, 8):
                esz = 0
        for i, nm in enumerate(names):
            crc = None
            if esz:
                crc = struct.unpack_from('<I' if esz == 4 else '<Q', ko.b,
                                         cs['off'] + i * esz)[0]
            out[nm] = (lic, crc)
    return out


def crc_stubs(ko):
    """(__UNIQUE_ID_<name> set, subset actually targeted by a non-kcrctab rela).

    kbuild materialises one __UNIQUE_ID_<sym> local per symbol whose CRC came from
    Module.symvers.  Those referenced by code are real CRC-checked imports; the
    rest are unreferenced residue of the vendor CRC list and cannot affect
    behaviour."""
    names = {s['n'][12:] for s in ko.syms if s['n'].startswith('__UNIQUE_ID_')}
    referenced = set()
    for s in ko.secs:
        if s['type'] != 4 or s['n'].startswith(('.rela___kcrctab', '.rela___crc_')):
            continue
        for _, r_info, _ in ko.rela_entries(s):
            n = ko.sym_name(r_info >> 32)
            if n.startswith('__UNIQUE_ID_'):
                referenced.add(n[12:])
    return names, referenced


def rela_semantics(ko, sname):
    s = ko.sec(sname)
    if s is None:
        return None
    return [(off, r_info & 0xffffffff, ko.sym_name(r_info >> 32), addend)
            for off, r_info, addend in ko.rela_entries(s)]


def split_build_paths(items):
    def is_path(x):
        return ('/' in x and (x.startswith('../') or x.startswith('/'))
                and ('drivers/' in x or 'lieppos' in x))
    return sorted(x for x in items if not is_path(x)), sorted(x for x in items if is_path(x))


def strtab(ko, name):
    s = ko.sec(name)
    if s is None or s['type'] == 8:
        return None
    return [x.decode('latin-1') for x in ko.data(name).split(b'\0')[:-1]]


def main(a_path, b_path):
    A, B = KO(a_path), KO(b_path)
    print(f"A = {a_path}")
    print(f"B = {b_path}")
    print(f"A sha256 {hashlib.sha256(A.b).hexdigest()}")
    print(f"B sha256 {hashlib.sha256(B.b).hexdigest()}")

    an, bn = A.sec_by_name, B.sec_by_name
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
    exact = tot = 0
    bad = []
    for n in sorted(set(an) & set(bn)):
        if n in SKIP or an[n]['type'] == 8 or bn[n]['type'] == 8:
            continue
        tot += 1
        if A.data(n) == B.data(n):
            exact += 1
        else:
            bad.append((n, an[n]['size'], bn[n]['size']))
    print(f"  content sections byte-exact {exact}/{tot}: {bad if bad else 'no diffs'}")

    fa, fb = functions(A), functions(B)
    shared = sorted(set(fa) & set(fb))
    ss = sum(1 for k in shared if fa[k][0] == fb[k][0])
    sb = sum(1 for k in shared if fa[k][1] == fb[k][1])
    print(f"\nFUNCTIONS: A={len(fa)} B={len(fb)} shared={len(shared)} "
          f"size-identical={ss} byte-identical={sb}")
    for k in shared:
        if fa[k][:2] != fb[k][:2]:
            print(f"  FUNC-DIFF {k}: A size={fa[k][0]} B size={fb[k][0]} "
                  f"bytes-differ={fa[k][1] != fb[k][1]}")
    for k in sorted(set(fa) ^ set(fb)):
        print(f"  FUNC-ONE-SIDED {k} only in {'A' if k in fa else 'B'}")

    oa, ob = objects(A), objects(B)
    osh = sorted(set(oa) & set(ob))
    bym = [k for k in osh if oa[k] != ob[k]]
    print(f"\nDATA OBJECTS: A={len(oa)} B={len(ob)} shared={len(osh)} "
          f"(sec,size)-diff={len([k for k in osh if oa[k][:2] != ob[k][:2]])} byte-diff={len(bym)}")
    for k in bym:
        tag = 'SIZE' if oa[k][:1] != ob[k][:1] else 'bytes'
        print(f"  OBJ-{tag} {k}: A={oa[k][:2]} B={ob[k][:2]} bytes-equal={oa[k][2] == ob[k][2]}")
    for k in sorted(set(oa) ^ set(ob)):
        print(f"  OBJ-ONE-SIDED {k} only in {'A' if k in oa else 'B'}")

    va, sza = versions(A)
    vb, szb = versions(B)
    ish = sorted(set(va) & set(vb))
    print(f"\nIMPORTS (__versions entry={sza}/{szb}): A={len(va)} B={len(vb)} "
          f"shared={len(ish)} name-diff={sorted(set(va) ^ set(vb))} "
          f"CRC-mismatch={[(k, hex(va[k]), hex(vb[k])) for k in ish if va[k] != vb[k]]}")

    ea, eb = exports(A), exports(B)
    esh = sorted(set(ea) & set(eb))
    print(f"\nEXPORTS: A={len(ea)} B={len(eb)} shared={len(esh)} "
          f"name-diff={sorted(set(ea) ^ set(eb))} "
          f"licence-diff={[(k, ea[k][0], eb[k][0]) for k in esh if ea[k][0] != eb[k][0]]}")
    crc_cmp = [k for k in esh if ea[k][1] is not None and eb[k][1] is not None]
    print(f"  export CRC comparable={len(crc_cmp)}/{len(esh)} "
          f"CRC-mismatch={[(k, hex(ea[k][1]), hex(eb[k][1])) for k in crc_cmp if ea[k][1] != eb[k][1]]}")
    print('  export names: ' + ', '.join(sorted(ea)))

    def mi(ko):
        return {kv.decode().split('=', 1)[0]: kv.decode().split('=', 1)[1]
                for kv in ko.data('.modinfo').split(b'\0') if b'=' in kv}
    ma, mb = mi(A), mi(B)
    print("\n.MODINFO:")
    for k in sorted(set(ma) | set(mb)):
        if ma.get(k) != mb.get(k):
            print(f"  {k}: A={ma.get(k)!r} B={mb.get(k)!r}")

    print("\nRELA (semantic: r_offset/r_type/target-symbol-name/addend):")
    for n in sorted(x for x in an if x.startswith('.rela')):
        ta, tb = rela_semantics(A, n), rela_semantics(B, n)
        if tb is None:
            print(f"  {n}: A={len(ta)} entries, B MISSING")
            continue
        raw = A.data(n) == B.data(n)
        if ta == tb:
            print(f"  {n}: {len(ta)} entries semantic-identical raw-byte-identical={raw}")
            continue
        if len(ta) != len(tb):
            print(f"  {n}: ENTRY COUNT {len(ta)} vs {len(tb)}")
            continue
        d = [(x, y) for x, y in zip(ta, tb) if x != y]
        print(f"  {n}: {len(ta)} entries, {len(d)} semantic deltas, raw-byte-identical={raw}")
        for x, y in d[:8]:
            print(f"      A off=0x{x[0]:x} type={x[1]} {x[2]!r} +{x[3]:#x}")
            print(f"      B off=0x{y[0]:x} type={y[1]} {y[2]!r} +{y[3]:#x}")

    print("\nCRC STUBS (__UNIQUE_ID_<name>):")
    for lbl, k in (('A', A), ('B', B)):
        names, refd = crc_stubs(k)
        print(f"  {lbl}: total={len(names)} referenced-by-non-kcrctab-rela={len(refd)} "
              f"unreferenced-residue={sorted(names - refd)}")

    print("\nSTRING TABLES:")
    for n in ('.rodata.str1.8', '.rodata.str1.1', '.rodata'):
        x, y = strtab(A, n), strtab(B, n)
        if x is None or y is None:
            continue
        if x == y:
            print(f"  {n}: identical ({len(x)} entries)")
            continue
        oa_, ob_ = [i for i in x if i not in y], [i for i in y if i not in x]
        ba, pa = split_build_paths(oa_)
        bb, pb = split_build_paths(ob_)
        print(f"  {n}: differs ({len(x)} vs {len(y)} entries)")
        print(f"    behaviour-relevant only-in-A ({len(ba)}): {ba}")
        print(f"    behaviour-relevant only-in-B ({len(bb)}): {bb}")
        print(f"    out-of-tree build-path strings: A={pa} B={pb}")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
