#!/usr/bin/env python3
"""module-inventory.py KO [KO...] > module-inventory.tsv

Per-module identity/ABI inventory for stock kernel modules (llvm-readelf based).
Columns: module path sha256 size vermagic depends srcversion build_id
         imports exports export_crcs functions kcfi_functions data_objects
         relocations sections section_sizes source_path_strings
KCFI functions = defined FUNC symbols preceded by a 4-byte type-id word that is
the target of no relocation (the clang -fsanitize=kcfi prologue constant).
"""
import hashlib, os, re, subprocess, sys

RE = os.environ.get('LLVM_READELF', 'llvm-readelf')


def run(*a):
    return subprocess.run([RE, *a], capture_output=True, text=True).stdout


def main():
    cols = ['module', 'path', 'sha256', 'size', 'vermagic', 'depends', 'srcversion', 'build_id',
            'imports', 'exports', 'export_crcs', 'functions', 'kcfi_functions', 'data_objects',
            'relocations', 'sections', 'section_sizes', 'source_path_strings']
    print('\t'.join(cols))
    for p in sys.argv[1:]:
        raw = open(p, 'rb').read()
        mi = {}
        for l in run('-p', '.modinfo', p).splitlines():
            m = re.match(r'\s*\[\s*[0-9a-f]+\]\s+(\w+)=(.*)$', l)
            if m:
                mi.setdefault(m.group(1), m.group(2))
        secs = {}
        for l in run('-SW', p).splitlines():
            m = re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)', l)
            if m:
                secs[int(m.group(1))] = (m.group(2), int(m.group(4), 16), int(m.group(5), 16))
        syms = []
        for l in run('-sW', p).splitlines():
            f = l.split()
            if len(f) >= 8 and f[0].rstrip(':').isdigit():
                syms.append(f)
        funcs = [s for s in syms if s[3] == 'FUNC' and s[6].isdigit()]
        objs = [s for s in syms if s[3] == 'OBJECT' and s[6].isdigit()]
        exports = [s[7] for s in syms if s[7].startswith('__ksymtab_') and s[3] != 'SECTION'
                   and s[7] not in ('__ksymtab_strings', '__ksymtab_gpl')]
        crcs = [s for s in syms if s[7].startswith('__crc_')]
        nimp = sum(1 for _ in range(0, next((v[2] for v in secs.values() if v[0] == '__versions'), 0), 64))
        relocs = run('-rW', p)
        nrel = sum(1 for l in relocs.splitlines() if re.match(r'^[0-9a-f]{16}\s', l))
        # KCFI: 4 bytes before each function entry inside its section, non-zero word
        kcfi = 0
        for s in funcs:
            name, off, size = secs[int(s[6])]
            v = int(s[1], 16)
            if v >= 4 and raw[off + v - 4:off + v] != b'\0\0\0\0':
                kcfi += 1
        bid = re.search(r'Build ID:\s*([0-9a-f]+)', run('-n', p))
        srcs = sorted(set(re.findall(rb'[\w./-]+\.[ch]\b', raw)))
        srcs = [x.decode() for x in srcs if b'/' in x]
        keysec = ['.text', '.rodata', '.data', '.bss', '.rodata.str1.1', '.init.text', '.exit.text', '__versions', '.modinfo']
        ss = ','.join(f'{n}={sz}' for n, o, sz in secs.values() if n in keysec)
        row = [os.path.basename(p)[:-3], p, hashlib.sha256(raw).hexdigest(), str(len(raw)),
               mi.get('vermagic', ''), mi.get('depends', ''), mi.get('srcversion', ''),
               bid.group(1) if bid else '', str(nimp), str(len(exports)), str(len(crcs)),
               str(len(funcs)), str(kcfi), str(len(objs)), str(nrel), str(len(secs)), ss,
               ';'.join(srcs) or '(none)']
        print('\t'.join(row))


if __name__ == '__main__':
    main()
