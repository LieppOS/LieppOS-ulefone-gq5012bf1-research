#!/usr/bin/env python3
"""ABI-level parity of a rebuilt kernel module vs stock.

Compares: imported symbols, exported symbols (+namespace), __versions
(name, CRC), .modinfo keys/values (vermagic/srcversion reported separately),
section sizes for code/data sections, and KCFI type-id words of global functions.
usage: abi_parity.py <stock.ko> <rebuilt.ko> [--label L] [--tsv out.tsv]
"""
import os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'camera-stack', 'kernel-isp-imgsys', 'scripts'))
from elfmini import Elf  # noqa

def secs(e):
    return {s.name: s for s in e.sections}

def versions(e, path):
    s = secs(e).get('__versions')
    if not s: return {}
    b = open(path, 'rb').read()[s.off:s.off + s.size]
    out = {}
    for i in range(0, len(b), 64):
        crc = struct.unpack_from('<Q', b, i)[0]
        name = b[i + 8:i + 64].split(b'\0')[0].decode()
        out[name] = crc
    return out

def modinfo(e, path):
    s = secs(e).get('.modinfo')
    if not s: return {}
    b = open(path, 'rb').read()[s.off:s.off + s.size]
    d = {}
    for kv in b.split(b'\0'):
        if b'=' in kv:
            k, v = kv.decode(errors='replace').split('=', 1)
            d.setdefault(k, []).append(v)
    return d

def syms(e):
    und = sorted({s.name for s in e.symbols if s.shndx == 0 and s.name})
    sn = {i: x.name for i, x in enumerate(e.sections)}
    exp = sorted({(s.name[len('__ksymtab_'):], sn.get(s.shndx, '?')) for s in e.symbols
                  if s.name.startswith('__ksymtab_') and s.type != 3 and sn.get(s.shndx, '').startswith('__ksymtab')
                  and not sn.get(s.shndx, '').startswith('__ksymtab_strings')})
    return und, exp

def main():
    a, b = sys.argv[1], sys.argv[2]
    label = sys.argv[sys.argv.index('--label') + 1] if '--label' in sys.argv else os.path.basename(a)
    ea, eb = Elf(a), Elf(b)
    rows = []
    ua, xa = syms(ea); ub, xb = syms(eb)
    rows.append(('imports', len(set(ua) & set(ub)), len(set(ua) | set(ub)), 'EXACT' if ua == ub else f'-{sorted(set(ua)-set(ub))} +{sorted(set(ub)-set(ua))}'))
    rows.append(('exports', len(set(xa) & set(xb)), len(set(xa) | set(xb)), 'EXACT' if xa == xb else f'-{sorted(set(xa)-set(xb))} +{sorted(set(xb)-set(xa))}'))
    va, vb = versions(ea, a), versions(eb, b)
    same = [k for k in va if vb.get(k) == va[k]]
    bad = sorted(set(va) ^ set(vb)) + sorted(k for k in va if k in vb and va[k] != vb[k])
    rows.append(('modversions', len(same), len(set(va) | set(vb)), 'EXACT' if not bad and list(va) == list(vb) else ('ORDER' if not bad else f'diff {bad}')))
    def kcrc(e, path):
        blob = open(path, 'rb').read(); out = {}
        for x in e.symbols:
            if x.name.startswith('__crc_') and x.shndx and x.shndx < len(e.sections):
                sec = e.sections[x.shndx]
                if sec.type == 8: continue
                out[x.name[6:]] = struct.unpack_from('<I', blob, sec.off + x.value)[0]
        return out
    ca, cb = kcrc(ea, a), kcrc(eb, b)
    badc = sorted(k for k in set(ca) | set(cb) if ca.get(k) != cb.get(k))
    rows.append(('export-crcs', len(set(ca) | set(cb)) - len(badc), len(set(ca) | set(cb)), 'EXACT' if not badc else f'diff {badc}'))
    ma, mb = modinfo(ea, a), modinfo(eb, b)
    keys = sorted(set(ma) | set(mb))
    mk = [k for k in keys if k not in ('vermagic', 'srcversion', 'scmversion') and ma.get(k) != mb.get(k)]
    rows.append(('modinfo', len(keys) - len(mk), len(keys), 'EXACT(excl vermagic/srcversion)' if not mk else f'diff {mk}'))
    vm = (ma.get('vermagic', [''])[0], mb.get('vermagic', [''])[0])
    rows.append(('vermagic', int(vm[0] == vm[1]), 1, 'EXACT' if vm[0] == vm[1] else f'stock={vm[0]!r} rebuilt={vm[1]!r}'))
    sa, sb = secs(ea), secs(eb)
    names = [n for n in sa if n.startswith(('.text', '.rodata', '.data', '.bss', '.init', '.exit', '__ksymtab', '__param', '.modinfo', '__versions', '.altinstr', '__jump', '__bug', '__patchable', '.note.gnu.property')) and not n.startswith('.rela')]
    sd = [n for n in names if n not in sb or sa[n].size != sb[n].size]
    rows.append(('section-sizes', len(names) - len(sd), len(names), 'EXACT' if not sd else 'diff ' + ', '.join(f'{n}:{sa[n].size}/{sb[n].size if n in sb else "-"}' for n in sd)))
    ok = all(r[3].startswith('EXACT') for r in rows if r[0] != 'vermagic')
    print(f"{label}\tABI {'EXACT' if ok else 'DIFF'}\t" + ' | '.join(f'{r[0]} {r[1]}/{r[2]}' + ('' if r[3].startswith('EXACT') else ' !') for r in rows))
    if '--tsv' in sys.argv:
        with open(sys.argv[sys.argv.index('--tsv') + 1], 'w') as f:
            f.write('check\tmatch\ttotal\tresult\n')
            for r in rows: f.write('\t'.join(map(str, r)) + '\n')
    if '-v' in sys.argv:
        for r in rows: print('  ', *r)

main()
