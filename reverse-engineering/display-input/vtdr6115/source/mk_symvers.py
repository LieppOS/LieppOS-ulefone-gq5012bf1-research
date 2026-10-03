#!/usr/bin/env python3
"""Emit a Module.symvers line per exported symbol of a stock .ko,
using the CRC stored in that module's own __kcrctab* sections."""
import subprocess,re,struct,sys
def crcmap(p):
    syms=subprocess.run(['llvm-readelf','--syms',p],capture_output=True,text=True).stdout
    S=subprocess.run(['llvm-readelf','-S',p],capture_output=True,text=True).stdout
    names={}
    for l in S.splitlines():
        m=re.match(r'\s*\[\s*(\d+)\]\s+(\S+)',l)
        if m: names[int(m.group(1))]=m.group(2)
    crcs={}; gpl=set()
    for l in syms.splitlines():
        f=l.split()
        if len(f)>7 and f[7].startswith('__crc_'):
            crcs[f[7][6:]]=(int(f[1],16),int(f[6]))
        if len(f)>7 and f[7].startswith('__ksymtab_'):
            pass
    data={}
    out={}
    for name,(val,ndx) in crcs.items():
        sname=names[ndx]
        if sname not in data:
            hx=subprocess.run(['llvm-readelf','-x',sname,p],capture_output=True,text=True).stdout
            b=bytearray()
            for l in hx.splitlines():
                m=re.match(r'\s*0x[0-9a-f]+\s+((?:[0-9a-f]{2,8}\s+){1,4})',l)
                if m:
                    for t in m.group(1).split(): b+=bytes.fromhex(t)
            data[sname]=bytes(b)
        out[name]=struct.unpack_from('<I',data[sname],val)[0]
    # licence: __ksymtab_gpl section presence per symbol
    lic={}
    for l in syms.splitlines():
        f=l.split()
        if len(f)>7 and f[7].startswith('__ksymtab_') and not f[7].startswith('__ksymtab_strings'):
            n=f[7][len('__ksymtab_'):]
            sname=names.get(int(f[6]),'')
            lic[n]='EXPORT_SYMBOL_GPL' if 'gpl' in sname else 'EXPORT_SYMBOL'
    return out,lic
for p in sys.argv[1:]:
    mod=p.split('/')[-1][:-3]
    crcs,lic=crcmap(p)
    for n in sorted(crcs):
        print(f"0x{crcs[n]:08x}\t{n}\t{mod}\t{lic.get(n,'EXPORT_SYMBOL_GPL')}\t")
