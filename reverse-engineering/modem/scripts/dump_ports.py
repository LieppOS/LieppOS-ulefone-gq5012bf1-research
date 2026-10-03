#!/usr/bin/env python3
"""Decode the stock ccci_md_all.ko CCCI port table (md_ccci_ports) into TSV.

usage: dump_ports.py <stock ccci_md_all.ko> <rebuilt port_cfg.o (DWARF)> [table symbol]
Struct layout and enum values come from DWARF of our byte-identical rebuild;
the bytes and relocations come from the stock module.
"""
import re, subprocess, sys, struct, os
sys.path.insert(0, os.environ['RS'] + '/scripts')
from elfmini import Elf
ko, obj = sys.argv[1], sys.argv[2]
table = sys.argv[3] if len(sys.argv) > 3 else 'md_ccci_ports'
dw = subprocess.run(['llvm-dwarfdump', '--debug-info', obj], capture_output=True, text=True).stdout.splitlines()
enums = {}; cur = None; i = 0
while i < len(dw):
    l = dw[i]
    if 'DW_TAG_enumeration_type' in l:
        cur = None
        for j in range(i + 1, min(i + 6, len(dw))):
            m = re.search(r'DW_AT_name\s*\("(\w+)"\)', dw[j])
            if m: cur = m.group(1); enums.setdefault(cur, {}); break
    elif 'DW_TAG_enumerator' in l and cur:
        n = re.search(r'DW_AT_name\s*\("(\w+)"\)', dw[i + 1]).group(1)
        v = int(re.search(r'DW_AT_const_value\s*\((-?\w+)\)', dw[i + 2]).group(1), 0)
        enums[cur][v] = n
    elif re.search(r'^0x[0-9a-f]+:\s+DW_TAG_(structure|subprogram|variable|typedef|base_type)', l):
        cur = None
    i += 1
ch = enums['CCCI_CH']
hif = {}
for k, d in enums.items():
    for v, n in d.items():
        if n.endswith('_HIF_ID'): hif[v] = n
FLAGS = {0: 'ALLOW_DROP', 1: 'RX_FULLED', 2: 'USER_HEADER', 3: 'RX_EXCLUSIVE', 4: 'ADJUST_HEADER', 5: 'CH_TRAFFIC',
         6: 'DUMP_RAW_DATA', 7: 'WITH_CHAR_NODE', 8: 'TX_ACK_FULLED', 9: 'CLEAN', 10: 'NET_DUMP', 11: 'CLOSE_NO_DROP_PKT'}
e = Elf(ko)
s = [x for x in e.sym(table) if x.type == 1][0]
SZ = 0x118
print('idx\ttx_ch\ttx_ch_name\trx_ch\trx_ch_name\ttxq\trxq\ttxq_exp\trxq_exp\thif\tflags\tops\tminor\tname')
for k in range(s.size // SZ):
    b = e.bytes_of(s, k * SZ, SZ)
    tx, rx, tq, rq, tqe, rqe, hid, fl = struct.unpack_from('<IIBBBBBxH', b, 0)
    minor, = struct.unpack_from('<I', b, 24)
    ops = e.ptr_at(s, k * SZ + 16); nm = e.ptr_at(s, k * SZ + 32)
    opsn = ops[0].name if ops else '-'
    name = e.cstring_at(nm[0].shndx, nm[0].value + nm[1]) if nm and nm[0].shndx else '-'
    fls = '|'.join(v for b_, v in FLAGS.items() if fl & (1 << b_)) or '0'
    print(f"{k}\t{tx}\t{ch.get(tx,'?')}\t{rx}\t{ch.get(rx,'?')}\t{tq:#x}\t{rq:#x}\t{tqe:#x}\t{rqe:#x}\t{hif.get(hid,hid)}\t{fls}\t{opsn}\t{minor}\t{name}")
