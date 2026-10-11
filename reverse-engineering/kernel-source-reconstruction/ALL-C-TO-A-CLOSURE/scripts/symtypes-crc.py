#!/usr/bin/env python3
"""Recompute genksyms (scripts/genksyms/genksyms.c, 6.1) modversion CRCs from a .symtypes file.

usage: symtypes-crc.py FILE.symtypes [--types OTHER.symtypes ...] [SYMBOL ...]

--types: definitions from these files override FILE's own type definitions (used to test
whether an export's CRC changes when it sees another translation unit's type expansions).
Algorithm (expand_and_crc_sym): tokens are CRC32-accumulated with a trailing space; a
reference s#/u#/e#/t#/E# is expanded to its definition the first time it is met while
expanding one exported symbol and to "struct NAME"-style text on later visits.
"""
import sys

def crc32_table():
    t = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ 0xedb88320 if c & 1 else c >> 1
        t.append(c)
    return t
T = crc32_table()

def load(path):
    d = {}
    for line in open(path):
        p = line.split()
        if p:
            d[p[0]] = p[1:]
    return d

KW = {'s': 'struct', 'u': 'union', 'e': 'enum', 't': None, 'E': None}

def crc_of(name, defs):
    crc = 0xffffffff
    def acc(s):
        nonlocal crc
        for ch in s.encode():
            crc = T[(crc ^ ch) & 0xff] ^ (crc >> 8)
    visited = set()
    def expand(tokens):
        for tok in tokens:
            if len(tok) > 2 and tok[1] == '#' and tok[0] in KW:
                kind, nm = tok[0], tok[2:]
                if tok in visited or tok not in defs:
                    if kind == 't' or kind == 'E':
                        acc(nm); acc(' ')
                    else:
                        acc(KW[kind]); acc(' '); acc(nm); acc(' ')
                        if tok not in defs:   # never defined: genksyms emits "{ UNKNOWN }"
                            for x in ('{', 'UNKNOWN', '}'):
                                acc(x); acc(' ')
                    continue
                visited.add(tok)
                expand(defs[tok])
            else:
                acc(tok); acc(' ')
    expand(defs[name])
    return crc ^ 0xffffffff

if __name__ == '__main__':
    args = sys.argv[1:]
    base = load(args.pop(0)); over = {}
    while args and args[0] == '--types':
        args.pop(0); o = load(args.pop(0)); over.update({k: v for k, v in o.items() if '#' in k})
    defs = dict(base); defs.update(over)
    syms = args or [k for k in base if '#' not in k]
    for s in syms:
        print(f'0x{crc_of(s, defs):08x}\t{s}')
