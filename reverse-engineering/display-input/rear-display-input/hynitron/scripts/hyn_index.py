#!/usr/bin/env python3
"""Static index of a hynitron.ko: functions, string refs, calls, data refs.

usage: hyn_index.py MODULE.ko  -> python dict via index(path)
Offline, read-only. Uses llvm-readelf/llvm-objdump from PATH.
"""
import re, subprocess, sys, json, hashlib

def run(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout

def sections(ko):
    out = {}
    for l in run('llvm-readelf', '-SW', ko).splitlines():
        m = re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)', l)
        if m:
            out[m.group(2)] = dict(idx=int(m.group(1)), off=int(m.group(3), 16), size=int(m.group(4), 16))
    return out

def symbols(ko):
    syms = []
    for l in run('llvm-readelf', '-sW', ko).splitlines():
        p = l.split()
        if len(p) >= 8 and p[3] in ('FUNC', 'OBJECT') and p[6].isdigit():
            syms.append(dict(name=p[7], value=int(p[1], 16), size=int(p[2]), type=p[3], bind=p[4], shndx=int(p[6])))
    return syms

def data_mapping_symbols(ko):
    """Return (section index, value) sites explicitly marked as AArch64 data."""
    out = set()
    for l in run('llvm-readelf', '-sW', ko).splitlines():
        p = l.split()
        if len(p) >= 8 and p[6].isdigit() and p[7].startswith('$d'):
            out.add((int(p[6]), int(p[1], 16)))
    return out


def relocs(ko):
    cur = None; out = {}
    for l in run('llvm-readelf', '-rW', ko).splitlines():
        m = re.match(r"Relocation section '\.rela(\S+)'", l)
        if m: cur = m.group(1); out[cur] = []; continue
        p = l.split()
        if cur and len(p) >= 5 and re.fullmatch(r'[0-9a-f]{16}', p[0]):
            add = 0
            if len(p) >= 7 and p[-2] in '+-': add = int(p[-1], 16) * (1 if p[-2] == '+' else -1)
            out[cur].append(dict(off=int(p[0], 16), type=p[2], sym=p[4], add=add))
    return out

def strings(ko, secs):
    raw = open(ko, 'rb').read(); s = secs['.rodata.str1.1']; b = raw[s['off']:s['off'] + s['size']]
    res = {}; i = 0
    while i < len(b):
        j = b.index(b'\0', i); res[i] = b[i:j].decode('latin1'); i = j + 1
    return res

def index(ko):
    secs = sections(ko); syms = symbols(ko); rel = relocs(ko); strs = strings(ko, secs)
    dmaps = data_mapping_symbols(ko)
    byidx = {v['idx']: k for k, v in secs.items()}
    funcs = [s for s in syms if s['type'] == 'FUNC']
    for f in funcs:
        f['section'] = byidx.get(f['shndx'], '?'); f.update(strings=[], calls=[], data=[], callers=[])
    def owner(sec, off):
        for f in funcs:
            if f['section'] == sec and f['value'] <= off < f['value'] + f['size']: return f
    strref = {}
    for sec in ('.text', '.init.text', '.exit.text'):
        for r in rel.get(sec, []):
            f = owner(sec, r['off'])
            if not f: continue
            if r['sym'] == '.rodata.str1.1':
                if r['type'].endswith('LO12_NC') or r['type'] == 'R_AARCH64_ABS64':
                    f['strings'].append(r['add']); strref.setdefault(r['add'], []).append(f['name'])
            elif r['type'] in ('R_AARCH64_CALL26', 'R_AARCH64_JUMP26'):
                f['calls'].append(r['sym'])
            elif r['type'].endswith('LO12_NC') or r['type'].startswith('R_AARCH64_LDST'):
                f['data'].append(f"{r['sym']}+{r['add']:#x}")
    names = {f['name'] for f in funcs}
    for f in funcs:
        for c in f['calls']:
            for g in funcs:
                if g['name'] == c and f['name'] not in g['callers']: g['callers'].append(f['name'])
    raw = open(ko, 'rb').read()
    for f in funcs:
        s = secs[f['section']]; body = raw[s['off'] + f['value']:s['off'] + f['value'] + f['size']]
        f['sha256'] = hashlib.sha256(body).hexdigest()
        has_kcfi = f['value'] >= 4 and (f['shndx'], f['value'] - 4) in dmaps
        kc = raw[s['off'] + f['value'] - 4:s['off'] + f['value']] if has_kcfi else b''
        f['kcfi'] = kc[::-1].hex() if has_kcfi else 'N/A'
    return dict(sections=secs, symbols=syms, funcs=funcs, strings=strs, strref=strref, relocs=rel)

if __name__ == '__main__':
    ix = index(sys.argv[1])
    for f in sorted(ix['funcs'], key=lambda f: (f['section'], f['value'])):
        print(f"{f['section']}\t{f['value']:#x}\t{f['size']}\t{f['name']}\t{len(f['strings'])} str\t{len(f['calls'])} calls")
