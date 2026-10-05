#!/usr/bin/env python3
"""ipi_callsites.py KO... : static call-site census of TinySys IPI / mbox / rpmsg APIs.

For every bl/b to an imported mtk_ipi_*/mtk_mbox_*/mtk_rpmsg_* symbol, report the
containing function and the best-effort constant values of x0..x5 at the call,
from a linear intra-function register tracker (mov/movz/movk/orr-imm/add-imm,
adrp+add/ldr symbol references via relocations, reg-to-reg mov). Values that are
not statically constant are printed as '?'.  Read-only, offline.
"""
import re, subprocess, sys, os
OBJ = 'llvm-objdump'
API = re.compile(r'^(mtk_ipi_\w+|ipi_monitor_dump|mtk_mbox_\w+|mtk_rpmsg_create_\w+|get_\w+_ipidev|vcp_get_ipidev|gpueb_get_\w+_PIN_ID_by_name|get_adsp_mbox_pin_\w+)$')
def run(ko):
    out = subprocess.run([OBJ, '-d', '-r', '--no-show-raw-insn', ko], capture_output=True, text=True).stdout
    func = None; regs = {}; rows = []; snap = {}; prev_dst = None; pend_pin = None; pend_store = False
    lines = out.split('\n')
    for i, l in enumerate(lines):
        m = re.match(r'^[0-9a-f]+ <(.+)>:$', l)
        if m: func = m.group(1); regs = {}; continue
        m = re.match(r'^\s+([0-9a-f]+):\s+(R_AARCH64_\w+)\s+(\S+)$', l)
        if m:
            typ, sym = m.group(2), m.group(3)
            # attach reloc to previous instruction's destination register
            if pend_store and typ.startswith('R_AARCH64_LDST32'):
                rows.append((func, 'PINVAR', [re.sub(r'\+0x0$', '', sym), pend_pin, '', '', '', '']))
                pend_store = False; pend_pin = None
            if prev_dst is not None and typ != 'R_AARCH64_CALL26' and typ != 'R_AARCH64_JUMP26':
                regs[prev_dst] = '&' + re.sub(r'\+0x0$', '', sym)
            if typ in ('R_AARCH64_CALL26', 'R_AARCH64_JUMP26'):
                tgt = re.sub(r'\+0x0$', '', sym)
                if API.match(tgt):
                    rows.append((func, tgt, [snap.get('x%d' % k, '?') for k in range(6)]))
                if 'PIN_ID_by_name' in tgt:
                    pend_pin = snap.get('x0')
                if API.match(tgt) and ('get_' in tgt):
                    regs['x0'] = 'ret:' + tgt
            continue
        m = re.match(r'^\s+([0-9a-f]+):\s+(\w+(?:\.\w+)?)\s*(.*)$', l)
        if not m: prev_dst = None; continue
        op, args = m.group(2), m.group(3)
        if pend_pin is not None and op == 'str' and args.startswith('w0,'):
            pend_store = True
        a = [x.strip() for x in re.split(r',(?![^\[]*\])', args)] if args else []
        def R(x):
            x = x.strip()
            if re.match(r'^[wx]\d+$', x): return 'x' + x[1:]
            return None
        dst = R(a[0]) if a else None
        prev_dst = dst
        if op in ('mov', 'movz') and len(a) >= 2:
            if a[1].startswith('#'):
                v = int(a[1][1:], 0)
                if len(a) > 2 and 'lsl' in a[2]: v <<= int(a[2].split('#')[1], 0)
                regs[dst] = v
            elif R(a[1]): regs[dst] = regs.get(R(a[1]), '?')
            else: regs.pop(dst, None)
        elif op == 'movk' and dst in regs and isinstance(regs[dst], int):
            v = int(a[1][1:], 0); sh = int(a[2].split('#')[1], 0) if len(a) > 2 else 0
            regs[dst] = (regs[dst] & ~(0xffff << sh)) | (v << sh)
        elif op == 'orr' and len(a) == 3 and a[1] in ('wzr', 'xzr') and a[2].startswith('#'):
            regs[dst] = int(a[2][1:], 0)
        elif op == 'add' and len(a) == 3 and dst and R(a[1]) and isinstance(regs.get(R(a[1])), str) and regs[R(a[1])].startswith('&'):
            if dst not in regs or not str(regs.get(dst, '')).startswith('&'):
                regs[dst] = regs[R(a[1])] + ('' if a[2] in ('#0x0', '#0') else '+' + a[2])
        elif op in ('bl', 'blr', 'b', 'br', 'ret') or op.startswith('b.') or op in ('cbz', 'cbnz', 'tbz', 'tbnz'):
            snap = dict(regs)
            if op in ('bl', 'blr', 'b', 'br'):
                for k in range(0, 19): regs.pop('x%d' % k, None)
            prev_dst = None
        elif op.startswith('ldr') and dst and R(a[1]) is None and '[' in args:
            mm = re.match(r'\[(x\d+)(?:, #(-?0x[0-9a-f]+|\d+))?\]', a[1])
            base = regs.get(mm.group(1)) if mm else None
            if isinstance(base, str) and base.startswith('&'):
                regs[dst] = '*' + base[1:] + ('' if not mm.group(2) else '+' + mm.group(2))
            else:
                regs.pop(dst, None)
        elif dst:
            regs.pop(dst, None)
    return rows
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from elfmini import Elf
def resolve(e, v):
    if isinstance(v, str) and v.startswith('&.rodata.str'):
        m = re.match(r'&(\S+?)(?:\+0x([0-9a-f]+))?$', v)
        sec = e.secbyname.get(m.group(1))
        if sec:
            o = sec.off + int(m.group(2) or '0', 16)
            return '"' + e.blob[o:e.blob.index(b'\0', o)].decode(errors='replace') + '"'
    return v
for ko in sys.argv[1:]:
    e = Elf(ko)
    for f, t, r in run(ko):
        print('\t'.join([os.path.basename(ko)[:-3], f, t] + [str(resolve(e, x)) for x in r]))
