#!/usr/bin/env python3
"""depgraph.py STOCKDIR OUT.tsv : provider->consumer graph for the TinySys messaging exports.

For every export of mtk-mbox / mtk_rpmsg_mbox / mtk_tinysys_ipi (and the per-processor
ipidev/mbox accessors) find every stock module that imports it, and record
  provider, symbol, provider export CRC (__kcrctab), consumer, consumer __versions CRC,
  CRC match, call-site count (CALL26/JUMP26 relocs), address-taken count (other relocs),
  containing functions, provider KCFI type id (word at func-4) and consumer
  __kcfi_typeid_<sym> if the consumer takes the address.
"""
import os, struct, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from elfmini import Elf
D = sys.argv[1]
PROV = ['mtk-mbox', 'mtk_rpmsg_mbox', 'mtk_tinysys_ipi', 'scp', 'vcp', 'vcp_status', 'mcupm', 'gpueb', 'adsp']
def exports(e):
    names = []
    for s in e.symbols:
        if s.name.startswith('__ksymtab_') and s.shndx:
            names.append(s.name[len('__ksymtab_'):])
    crc = {}
    kc = [x for x in e.sections if x.name in ('__kcrctab', '__kcrctab_gpl')]
    for s in e.symbols:
        if s.name.startswith('__crc_'):
            sec = e.sections[s.shndx]
            crc[s.name[6:]] = struct.unpack_from('<I', e.blob, sec.off + s.value)[0]
    return names, crc
def versions(e):
    v = {}
    s = e.secbyname.get('__versions')
    if not s: return v
    for i in range(s.size // 64):
        c, = struct.unpack_from('<Q', e.blob, s.off + 64 * i)
        n = e.blob[s.off + 64 * i + 8: s.off + 64 * i + 64].split(b'\0')[0].decode()
        v[n] = c & 0xffffffff
    return v
def kcfi_of(e, name):
    for s in e.symbols:
        if s.name == name and s.type == 2 and s.shndx:
            sec = e.sections[s.shndx]
            if s.value >= 4:
                return struct.unpack_from('<I', e.blob, sec.off + s.value - 4)[0]
    return None
mods = {f[:-3]: os.path.join(D, f) for f in os.listdir(D) if f.endswith('.ko')}
E = {}
def elf(m):
    if m not in E: E[m] = Elf(mods[m])
    return E[m]
provided = {}
for p in PROV:
    e = elf(p); names, crc = exports(e)
    for n in names:
        if p in ('mtk-mbox', 'mtk_rpmsg_mbox', 'mtk_tinysys_ipi') or 'ipidev' in n or 'PIN_ID' in n or 'mbox_pin' in n:
            provided[n] = (p, crc.get(n), kcfi_of(e, n))
rows = []
for m in sorted(mods):
    try: e = elf(m)
    except Exception: continue
    v = versions(e)
    und = {s.idx: s.name for s in e.symbols if s.shndx == 0 and s.name in provided}
    if not und: continue
    calls = collections.Counter(); addr = collections.Counter(); funcs = collections.defaultdict(set)
    for sec, lst in e.relocs.items():
        for r in lst:
            if r.sym.idx in und:
                n = und[r.sym.idx]
                if r.rtype in (282, 283): calls[n] += 1
                else: addr[n] += 1
                c = e.containing(sec, r.off)
                funcs[n].add(c.name if c else e.sections[sec].name)
    tid = {s.name[len('__kcfi_typeid_'):]: s.value & 0xffffffff for s in e.symbols if s.name.startswith('__kcfi_typeid_')}
    for idx, n in sorted(und.items(), key=lambda t: t[1]):
        p, pc, pk = provided[n]
        cc = v.get(n)
        rows.append([p, n, '0x%08x' % pc if pc is not None else '-', m, '0x%08x' % cc if cc is not None else '-',
                     'yes' if cc == pc else 'NO', str(calls[n]), str(addr[n]),
                     '0x%08x' % pk if pk is not None else '-', '0x%08x' % tid[n] if n in tid else '-',
                     ','.join(sorted(funcs[n]))])
hdr = ['provider', 'symbol', 'export_crc', 'consumer', 'import_crc', 'crc_match', 'call_sites', 'addr_refs', 'provider_kcfi', 'consumer_kcfi_typeid', 'functions']
with open(sys.argv[2], 'w') as f:
    f.write('\t'.join(hdr) + '\n')
    for r in sorted(rows): f.write('\t'.join(r) + '\n')
print(len(rows), 'edges;', sum(r[5] == 'NO' for r in rows), 'CRC mismatches;',
      sum(1 for r in rows if r[9] != '-' and r[9] != r[8]), 'KCFI mismatches;',
      sum(1 for r in rows if r[9] != '-'), 'KCFI-checkable')
