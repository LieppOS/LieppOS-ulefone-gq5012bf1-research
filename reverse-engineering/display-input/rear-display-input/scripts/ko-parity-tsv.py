#!/usr/bin/env python3
"""Explicit-operand parity between two Linux kernel modules (.ko).

    ko-parity-tsv.py A.ko B.ko OUTDIR

A is the reference (shipped stock), B the candidate (rebuild).  Writes:

  function-parity.tsv    per function: sizes, raw-byte equality, KCFI type id,
                         relocation-normalised instruction equality
  data-parity.tsv        per data object: section, size, byte equality
  abi-parity.tsv         imports (+modversion CRC), exports, .modinfo keys,
                         vermagic, depends ordering
  relocation-parity.tsv  per function: relocation count and normalised
                         (offset, type, target, addend) sequence equality

Normalisation: relocation targets in string sections are compared by string
content; targets in data/bss/rodata by containing object name + offset; this
removes pure layout differences.  Intra-section direct branches (resolved by
the assembler without a relocation) are reported separately as
'layout-only' when the only differing bytes are BL/B immediates.

Only standard tools are required: python3 and llvm-readelf/llvm-objdump
(LLVM_BIN or PATH).
"""
import os
import re
import subprocess
import sys
import hashlib

LLVM = os.environ.get('LLVM_BIN', '')


def tool(name):
    return os.path.join(LLVM, name) if LLVM else name


def run(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout


class Ko:
    def __init__(self, path):
        self.path = path
        self.raw = open(path, 'rb').read()
        self.secs = {}      # name -> (index, offset, size, type)
        self.byidx = {}
        for l in run(tool('llvm-readelf'), '-SW', path).splitlines():
            m = re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+[0-9a-f]+\s+'
                         r'([0-9a-f]+)\s+([0-9a-f]+)', l)
            if m:
                i, n, t = int(m.group(1)), m.group(2), m.group(3)
                self.secs[n] = (i, int(m.group(4), 16), int(m.group(5), 16), t)
                self.byidx[i] = n
        self.syms = []      # (name, type, bind, secname, value, size)
        for l in run(tool('llvm-readelf'), '-sW', path).splitlines():
            p = l.split()
            if len(p) >= 8 and p[0].rstrip(':').isdigit():
                ndx = p[6]
                sec = self.byidx.get(int(ndx)) if ndx.isdigit() else ndx
                self.syms.append((p[7], p[3], p[4], sec, int(p[1], 16), int(p[2])))
        self.funcs = {s[0]: s for s in self.syms if s[1] == 'FUNC' and s[3]}
        self.objs = {s[0]: s for s in self.syms
                     if s[1] == 'OBJECT' and s[3] and s[3] != 'UND'}
        self.relocs = self._relocs()

    def secdata(self, name):
        i, off, size, t = self.secs[name]
        return b'' if t == 'NOBITS' else self.raw[off:off + size]

    def resolve(self, sec, off):
        if sec is None:
            return '?'
        if sec.startswith('.rodata.str') or sec == '.modinfo':
            d = self.secdata(sec)
            e = d.find(b'\0', off)
            return 'S:' + d[off:e].decode('latin1')
        best = None
        for s in self.syms:
            if s[3] == sec and s[1] in ('OBJECT', 'FUNC') and s[4] <= off < s[4] + max(s[5], 1):
                best = s
                break
        if best:
            return f'{best[0]}+{off - best[4]:#x}'
        return f'{sec}+{off:#x}'

    def _relocs(self):
        out = {}
        cur = None
        for l in run(tool('llvm-readelf'), '-rW', self.path).splitlines():
            m = re.match(r"Relocation section '\.rela(\S+)'", l)
            if m:
                cur = m.group(1)
                out[cur] = []
                continue
            p = l.split()
            if cur and len(p) >= 5 and re.match(r'^[0-9a-f]{16}$', p[0]):
                off = int(p[0], 16)
                rtype = p[2]
                name = p[4]
                add = 0
                m2 = re.search(r'([+-])\s*([0-9a-f]+)$', l)
                if m2:
                    add = int(m2.group(2), 16) * (-1 if m2.group(1) == '-' else 1)
                if name in self.secs:      # section symbol
                    tgt = self.resolve(name, add)
                    add = 0
                else:
                    tgt = name
                out[cur].append((off, rtype, tgt, add))
        return out

    def func_bytes(self, name):
        n, t, b, sec, v, sz = self.funcs[name]
        return self.secdata(sec)[v:v + sz]

    def kcfi(self, name):
        n, t, b, sec, v, sz = self.funcs[name]
        if v < 4:
            return ''
        w = self.secdata(sec)[v - 4:v]
        # a KCFI type id is only present if a mapping symbol / data word precedes
        return w[::-1].hex()

    def func_relocs(self, name):
        n, t, b, sec, v, sz = self.funcs[name]
        return [(o - v, ty, tg, a) for (o, ty, tg, a) in self.relocs.get(sec, [])
                if v <= o < v + sz]

    def modinfo(self):
        d = self.secdata('.modinfo') if '.modinfo' in self.secs else b''
        return [x.decode('latin1') for x in d.split(b'\0') if x]

    def versions(self):
        d = self.secdata('__versions') if '__versions' in self.secs else b''
        out = []
        for i in range(0, len(d), 64):
            crc = int.from_bytes(d[i:i + 4], 'little')
            nm = d[i + 8:i + 64].split(b'\0')[0].decode()
            out.append((nm, crc))
        return out

    def exports(self):
        return sorted(s[0][len('__ksymtab_'):] for s in self.syms
                      if s[0].startswith('__ksymtab_') and not s[0].startswith('__ksymtab_strings'))


def branch_only_diff(a, b):
    """True if two equal-length AArch64 byte strings differ only in B/BL imm26."""
    if len(a) != len(b):
        return False
    for i in range(0, len(a), 4):
        wa = int.from_bytes(a[i:i + 4], 'little')
        wb = int.from_bytes(b[i:i + 4], 'little')
        if wa == wb:
            continue
        if (wa & 0x7c000000) == 0x14000000 and (wa & 0xfc000000) == (wb & 0xfc000000):
            continue
        if (wa & 0x9f000000) == 0x90000000 and (wa & 0x9f00001f) == (wb & 0x9f00001f):
            continue   # ADRP page delta (layout)
        return False
    return True


def main():
    a, b, outdir = Ko(sys.argv[1]), Ko(sys.argv[2]), sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    summ = []

    # ---- functions -------------------------------------------------------
    names = sorted(set(a.funcs) | set(b.funcs))
    rows = []
    c = dict(present=0, size=0, raw=0, layout=0, kcfi=0, reloc=0)
    for n in names:
        if n not in a.funcs or n not in b.funcs:
            rows.append([n, a.funcs.get(n, ('',) * 6)[5], b.funcs.get(n, ('',) * 6)[5],
                         'ONE-SIDED', '', '', '', ''])
            continue
        c['present'] += 1
        ba, bb = a.func_bytes(n), b.func_bytes(n)
        size_eq = len(ba) == len(bb)
        raw_eq = ba == bb
        lay = (not raw_eq) and branch_only_diff(ba, bb)
        ka, kb = a.kcfi(n), b.kcfi(n)
        ra, rb = a.func_relocs(n), b.func_relocs(n)
        rel_eq = ra == rb
        status = ('BYTE-IDENTICAL' if raw_eq else
                  'LAYOUT-ONLY' if lay and rel_eq else
                  'SIZE-EQUAL' if size_eq else 'SIZE-DIFF')
        c['size'] += size_eq
        c['raw'] += raw_eq
        c['layout'] += (raw_eq or (lay and rel_eq))
        c['kcfi'] += ka == kb
        c['reloc'] += rel_eq
        rows.append([n, len(ba), len(bb), status, 'yes' if ka == kb else f'{ka}/{kb}',
                     len(ra), len(rb), 'yes' if rel_eq else 'no'])
    with open(f'{outdir}/function-parity.tsv', 'w') as f:
        f.write('function\tA_size\tB_size\tstatus\tkcfi_equal\tA_relocs\tB_relocs\trelocs_equal\n')
        for r in rows:
            f.write('\t'.join(map(str, r)) + '\n')
    summ.append(f"functions: A={len(a.funcs)} B={len(b.funcs)} shared={c['present']} "
                f"size-equal={c['size']} byte-identical={c['raw']} "
                f"byte-identical-or-layout-only={c['layout']} kcfi-equal={c['kcfi']} "
                f"relocs-equal={c['reloc']}")

    # ---- data objects ----------------------------------------------------
    uid = re.compile(r'^(__UNIQUE_ID_\D+?)\d+$')
    def keyed(objs):
        out, seen = {}, {}
        for n in sorted(objs, key=lambda x: (objs[x][3], objs[x][4])):
            m = uid.match(n)
            k = m.group(1) if m else n
            seen[k] = seen.get(k, 0) + 1
            out[k if seen[k] == 1 else f'{k}#{seen[k]}'] = n
        return out
    ka = keyed(a.objs)
    kb = keyed(b.objs)
    drows = []
    dc = dict(shared=0, secsize=0, bytes=0)
    for k in sorted(set(ka) | set(kb)):
        if k not in ka or k not in kb:
            drows.append([k, ka.get(k, ''), kb.get(k, ''), '', '', '', 'ONE-SIDED'])
            continue
        oa, ob = a.objs[ka[k]], b.objs[kb[k]]
        dc['shared'] += 1
        ss = (oa[3], oa[5]) == (ob[3], ob[5])
        dc['secsize'] += ss
        da = a.secdata(oa[3])[oa[4]:oa[4] + oa[5]] if a.secs[oa[3]][3] != 'NOBITS' else b'\0' * oa[5]
        db = b.secdata(ob[3])[ob[4]:ob[4] + ob[5]] if b.secs[ob[3]][3] != 'NOBITS' else b'\0' * ob[5]
        be = da == db
        dc['bytes'] += be
        drows.append([k, f'{oa[3]}:{oa[5]}', f'{ob[3]}:{ob[5]}', 'yes' if ss else 'no',
                      'yes' if be else 'no', hashlib.sha256(da).hexdigest()[:16],
                      'EXACT' if ss and be else 'DIFF'])
    with open(f'{outdir}/data-parity.tsv', 'w') as f:
        f.write('object\tA_section:size\tB_section:size\tsection_size_equal\tbytes_equal\tA_sha256_16\tstatus\n')
        for r in drows:
            f.write('\t'.join(map(str, r)) + '\n')
    summ.append(f"data objects: A={len(a.objs)} B={len(b.objs)} shared(by name, __UNIQUE_ID "
                f"counter-normalised)={dc['shared']} section+size-equal={dc['secsize']} "
                f"bytes-equal={dc['bytes']}")

    # ---- ABI -------------------------------------------------------------
    va, vb = dict(a.versions()), dict(b.versions())
    arows = []
    for n in sorted(set(va) | set(vb)):
        arows.append(['import', n, f'{va[n]:#010x}' if n in va else '', f'{vb[n]:#010x}' if n in vb else '',
                      'yes' if va.get(n) == vb.get(n) else 'no'])
    ea, eb = a.exports(), b.exports()
    for n in sorted(set(ea) | set(eb)):
        arows.append(['export', n, 'yes' if n in ea else '', 'yes' if n in eb else '',
                      'yes' if (n in ea) == (n in eb) else 'no'])
    ma, mb = a.modinfo(), b.modinfo()
    for i in range(max(len(ma), len(mb))):
        x = ma[i] if i < len(ma) else ''
        y = mb[i] if i < len(mb) else ''
        arows.append(['modinfo', x.split('=')[0] or y.split('=')[0], x, y, 'yes' if x == y else 'no'])
    with open(f'{outdir}/abi-parity.tsv', 'w') as f:
        f.write('kind\tname\tA\tB\tequal\n')
        for r in arows:
            f.write('\t'.join(map(str, r)) + '\n')
    imp_eq = sum(1 for n in va if vb.get(n) == va[n])
    summ.append(f"imports: A={len(va)} B={len(vb)} name+CRC-equal={imp_eq}; "
                f"__versions order equal={a.versions() == b.versions()}")
    summ.append(f"exports: A={len(ea)} B={len(eb)} equal={ea == eb}")
    mi_eq = [x == y for x, y in zip(ma, mb)]
    summ.append(f"modinfo: A={len(ma)} B={len(mb)} positional-equal={sum(mi_eq)} "
                f"differing={[ma[i].split('=')[0] for i, e in enumerate(mi_eq) if not e]}")

    # ---- relocations -----------------------------------------------------
    with open(f'{outdir}/relocation-parity.tsv', 'w') as f:
        f.write('function\tindex\tA_off\tA_type\tA_target\tB_off\tB_type\tB_target\tequal\n')
        for n in names:
            if n not in a.funcs or n not in b.funcs:
                continue
            ra, rb = a.func_relocs(n), b.func_relocs(n)
            for i in range(max(len(ra), len(rb))):
                x = ra[i] if i < len(ra) else ('', '', '', '')
                y = rb[i] if i < len(rb) else ('', '', '', '')
                f.write('\t'.join(map(str, [n, i, hex(x[0]) if x[0] != '' else '', x[1], f'{x[2]}{x[3]:+#x}' if x[1] else '',
                                            hex(y[0]) if y[0] != '' else '', y[1], f'{y[2]}{y[3]:+#x}' if y[1] else '',
                                            'yes' if x == y else 'no'])) + '\n')
    nodbg = lambda r: {k: v for k, v in r.items() if not k.startswith('.debug')}
    ra_, rb_ = nodbg(a.relocs), nodbg(b.relocs)
    tot_a = sum(len(v) for v in ra_.values())
    tot_b = sum(len(v) for v in rb_.values())
    per = ', '.join(f'{k}={len(ra_.get(k, []))}/{len(rb_.get(k, []))}' for k in sorted(set(ra_) | set(rb_)))
    summ.append(f"relocation entries excluding DWARF: A={tot_a} B={tot_b} [{per}]")
    sa = {k: v[2] for k, v in a.secs.items()}
    sb = {k: v[2] for k, v in b.secs.items()}
    keysec = ['.text', '.rodata', '.data', '.bss', '.rodata.str1.1', '.init.text',
              '.exit.text', '__versions', '.modinfo']
    summ.append('section sizes A/B: ' + ', '.join(f'{k}={sa.get(k)}/{sb.get(k)}' for k in keysec))
    open(f'{outdir}/SUMMARY.txt', 'w').write(
        f"A = {sys.argv[1]}\nB = {sys.argv[2]}\n\n" + '\n'.join(summ) + '\n')
    print('\n'.join(summ))


if __name__ == '__main__':
    main()
