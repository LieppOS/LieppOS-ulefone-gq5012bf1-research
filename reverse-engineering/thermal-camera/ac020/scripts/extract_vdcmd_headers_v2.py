#!/usr/bin/env python3
"""Extract AC020 vdcmd frame-header constants from an llvm-objdump -d listing of libircmd020.so.

For every exported adv_/basic_/sys_/spi_/test_/dfu_ function, track constant byte/half/word
stores to the stack (sp- or x29-relative) and, at each call to a *_cmd_* transport entry
(standard/short/long read/write), report the bytes stored inside the header buffer passed
in x1. Works for both the -O0-style (sp-relative 'strh') and the byte-store ('sturb')
code generation found in the shipped builds.
Output: function, transport_call, header bytes '+off:0xVV' (byte granularity)."""
import re, sys
dis = open(sys.argv[1]).read().split('\n\n')
W = {'strb': 1, 'sturb': 1, 'strh': 2, 'sturh': 2, 'str': 4, 'stur': 4}
for blk in dis:
    m = re.search(r'^[0-9a-f]+ <([^>]+)>:', blk, re.M)
    if not m: continue
    fn = m.group(1)
    if not re.match(r'(adv|basic|sys|spi|dfu|test)_', fn): continue
    regs = {}; mem = {}; x1 = None
    for line in blk.splitlines()[1:]:
        p = line.split('\t')
        if len(p) < 3: continue
        op = p[1].strip(); a = p[2].strip()
        mm = re.match(r'([wx])(\d+), #(-?0x[0-9a-f]+|-?\d+)', a)
        if op == 'mov' and mm: regs[mm.group(2)] = int(mm.group(3), 0) & 0xffffffff; continue
        mm = re.match(r'w(\d+), wzr, #(0x[0-9a-f]+)', a)
        if op == 'orr' and mm: regs[mm.group(1)] = int(mm.group(2), 16); continue
        mm = re.match(r'w(\d+), wzr$', a)
        if op == 'mov' and mm: regs[mm.group(1)] = 0; continue
        mm = re.match(r'w(\d+), #(0x[0-9a-f]+), lsl #(\d+)', a)
        if op == 'movk' and mm and mm.group(1) in regs:
            regs[mm.group(1)] |= int(mm.group(2), 16) << int(mm.group(3)); continue
        if op in W:
            mm = re.match(r'(w\d+|wzr|x\d+|xzr), \[(sp|x29)(?:, #(-?0x[0-9a-f]+|-?\d+))?\]$', a)
            if mm:
                r = mm.group(1); base = mm.group(2); off = int(mm.group(3), 0) if mm.group(3) else 0
                key = (base, off)
                if r in ('wzr', 'xzr'): v = 0
                else: v = regs.get(r[1:])
                width = 8 if r.startswith('x') else W[op]
                for i in range(width):
                    mem[(base, off + i)] = None if v is None else (v >> (8 * i)) & 0xff
            continue
        mm = re.match(r'x1, (sp|x29), #(0x[0-9a-f]+|\d+)$', a)
        if op in ('add', 'sub') and mm:
            o = int(mm.group(2), 0); x1 = (mm.group(1), o if op == 'add' else -o); continue
        if op == 'mov' and re.match(r'x1, sp$', a): x1 = ('sp', 0); continue
        md = re.match(r'([wx])(\d+),', a)
        if md and op not in W and not op.startswith(('cmp','tst','cb','tb','b.','st')):
            regs.pop(md.group(2), None)
        mb = re.match(r'0x[0-9a-f]+ <([a-z_0-9]+)@plt>', a)
        if op == 'bl' and mb:
            t = mb.group(1)
            if re.match(r'(standard|short|long)_cmd_(read|write)', t) and x1:
                b, o = x1
                hb = {k[1] - o: v for k, v in mem.items() if k[0] == b and 0 <= k[1] - o < 24 and v is not None}
                print('\t'.join([fn, t, ' '.join(f'+{k}:{v:#04x}' for k, v in sorted(hb.items()) if v or k < 3)]))
            for r in [str(i) for i in range(19)]: regs.pop(r, None)
