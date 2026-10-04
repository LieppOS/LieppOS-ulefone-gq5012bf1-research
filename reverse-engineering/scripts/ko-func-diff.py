#!/usr/bin/env python3
"""Per-function disassembly diff between two .ko files.

Unlike `llvm-objdump -d -r --disassemble-symbols=F`, which prints the whole
section's relocation table, this slices `.rela.text` to the function's own
address range and annotates each instruction with the relocation that applies
to it. Output is address-free and label-normalised so two independently linked
modules can be diffed directly.

usage: ko-func-diff.py A.ko B.ko FUNC [FUNC...]
       ko-func-diff.py --summary A.ko B.ko      (classify every shared function)
"""
import subprocess, sys, re, difflib

def readelf(p, *args):
    return subprocess.run(['llvm-readelf', *args, p], capture_output=True, text=True).stdout

def sections(p):
    idx = {}
    for l in readelf(p, '-S').splitlines():
        m = re.match(r'\s*\[\s*(\d+)\]\s+(\S+)', l)
        if m:
            idx[int(m.group(1))] = m.group(2)
    return idx

def funcs(p):
    idx = sections(p)
    out = {}
    for l in readelf(p, '--syms').splitlines():
        f = l.split()
        if len(f) > 7 and f[3] == 'FUNC' and f[6].isdigit():
            out[f[7]] = (int(f[1], 16), int(f[2]), idx.get(int(f[6]), '?'))
    return out

def relas(p, sec='.text'):
    cur, out = None, {}
    for l in readelf(p, '-r').splitlines():
        m = re.match(r"Relocation section '(\S+)'", l)
        if m:
            cur = m.group(1)
            continue
        if cur != '.rela' + sec:
            continue
        m = re.match(r'([0-9a-f]{16})\s+\S+\s+(\S+)\s+[0-9a-f]{16}\s+(\S+)'
                     r'(?:\s*\+\s*([0-9a-f]+))?', l)
        if m:
            off = int(m.group(1), 16)
            out.setdefault(off, []).append((m.group(2), m.group(3),
                                            int(m.group(4), 16) if m.group(4) else 0))
    return out

_secdata = {}
_symmap = {}

def secdata(p, name):
    key = (p, name)
    if key not in _secdata:
        hx = readelf(p, '-x', name)
        b = bytearray()
        for l in hx.splitlines():
            m = re.match(r'\s*0x[0-9a-f]+\s+((?:[0-9a-f]{2,8}\s+){1,4})', l)
            if m:
                for t in m.group(1).split():
                    b += bytes.fromhex(t)
        _secdata[key] = bytes(b)
    return _secdata[key]

def symmap(p):
    """section -> sorted [(value, size, name)] for OBJECT symbols."""
    if p not in _symmap:
        idx = sections(p)
        out = {}
        for l in readelf(p, '--syms').splitlines():
            f = l.split()
            if len(f) > 7 and f[3] == 'OBJECT' and f[6].isdigit():
                out.setdefault(idx.get(int(f[6]), '?'), []).append(
                    (int(f[1], 16), int(f[2]), f[7]))
        for v in out.values():
            v.sort()
        _symmap[p] = out
    return _symmap[p]

def resolve(p, sym, add):
    """Turn a (section, addend) relocation operand into a stable name.

    Strings become their literal content, so two modules whose string tables
    are ordered differently still compare equal. Other section-relative
    targets become 'object+delta'."""
    if sym.startswith('.rodata.str'):
        d = secdata(p, sym)
        end = d.find(b'\0', add)
        return 'str:' + d[add:end].decode('utf-8', 'replace')
    if sym in ('.text', '.init.text', '.exit.text'):
        return f'{sym}+0x{add:x}'
    for v, s, n in symmap(p).get(sym, []):
        if v <= add < v + max(s, 1):
            return f'{n}+0x{add - v:x}' if add != v else n
    return f'{sym}+0x{add:x}' if add else sym

def body(p, fn, fmap, rmap):
    if fn not in fmap:
        return None
    va, size, sec = fmap[fn]
    txt = subprocess.run(['llvm-objdump', '-d', '--disassemble-symbols=' + fn, p],
                         capture_output=True, text=True).stdout
    lines = []
    for l in txt.splitlines():
        m = re.match(r'\s*([0-9a-f]+):\s*([0-9a-f]{8})\s*\t(.*)', l)
        if not m:
            continue
        off = int(m.group(1), 16)
        ins = re.sub(r'0x[0-9a-f]+ <[^>]*>', 'LBL', m.group(3).strip())
        ins = re.sub(r'\s+', ' ', ins)
        ann = ''
        for ty, sym, add in rmap.get(off, []):
            ann += f'   [{ty} {resolve(p, sym, add)}]'
        lines.append(ins + ann)
    return lines

def classify(a, b):
    """Return (category, note) for two instruction+reloc line lists."""
    if a == b:
        return 'IDENTICAL', ''
    ca = sorted(re.findall(r'R_AARCH64_CALL26 ([^\]]+)\]', '\n'.join(a)))
    cb = sorted(re.findall(r'R_AARCH64_CALL26 ([^\]]+)\]', '\n'.join(b)))
    ra = sorted(re.findall(r'\[R_\S+ ([^\]]+)\]', '\n'.join(a)))
    rb = sorted(re.findall(r'\[R_\S+ ([^\]]+)\]', '\n'.join(b)))
    ia = sorted(l.split('   [')[0].split(' ')[0] for l in a)
    ib = sorted(l.split('   [')[0].split(' ')[0] for l in b)
    if ca != cb:
        only_a = [x for x in ca if x not in cb]
        only_b = [x for x in cb if x not in ca]
        return 'CALLS_DIFFER', f'A-only={sorted(set(only_a))} B-only={sorted(set(only_b))}'
    if ra != rb:
        return 'RELOCS_DIFFER', f'{len(ra)} vs {len(rb)} relocation operands'
    if ia != ib:
        return 'OPCODES_DIFFER', f'{len(a)} vs {len(b)} instructions'
    return 'ORDER_ONLY', 'identical instruction and relocation multisets'

def main():
    if sys.argv[1] == '--summary':
        A, B = sys.argv[2], sys.argv[3]
        fa, fb = funcs(A), funcs(B)
        ra, rb = relas(A), relas(B)
        print('function\tA_size\tB_size\tcategory\tnote')
        for n in sorted(set(fa) & set(fb)):
            la, lb = body(A, n, fa, ra), body(B, n, fb, rb)
            cat, note = classify(la, lb)
            print(f'{n}\t{fa[n][1]}\t{fb[n][1]}\t{cat}\t{note}')
        return
    A, B = sys.argv[1], sys.argv[2]
    fa, fb = funcs(A), funcs(B)
    ra, rb = relas(A), relas(B)
    for n in sys.argv[3:]:
        la, lb = body(A, n, fa, ra), body(B, n, fb, rb)
        if la is None or lb is None:
            print(f'### {n}: missing in ' + ('A' if la is None else 'B'))
            continue
        cat, note = classify(la, lb)
        print(f'### {n}  A={fa[n][1]} B={fb[n][1]}  {cat} {note}')
        for l in difflib.unified_diff(la, lb, 'A', 'B', lineterm='', n=2):
            print(l)

main()
