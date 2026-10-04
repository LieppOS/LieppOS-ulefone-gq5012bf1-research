#!/usr/bin/env python3
"""Symbolized per-function AArch64 disassembly of a kernel module (.ko).
Resolves section-relative relocations to object symbols / C strings.
usage: symdis.py module.ko [func ...]"""
import subprocess,sys,re
CL='/home/armol/kernel-work/gki-12901745-workspace/prebuilts/clang/host/linux-x86/clang-r487747c/bin/'
ko=sys.argv[1];want=set(sys.argv[2:])
raw=open(ko,'rb').read()
secs={};idx={}
for l in subprocess.run([CL+'llvm-readelf','-SW',ko],capture_output=True,text=True).stdout.splitlines():
    m=re.match(r'\s*\[\s*(\d+)\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)',l)
    if m: secs[m.group(2)]=(int(m.group(3),16),int(m.group(4),16)); idx[m.group(1)]=m.group(2)
syms={}
for l in subprocess.run([CL+'llvm-readelf','-sW',ko],capture_output=True,text=True).stdout.splitlines():
    p=l.split()
    if len(p)>=8 and p[3]=='OBJECT' and p[6].isdigit():
        syms.setdefault(idx[p[6]],[]).append((int(p[1],16),int(p[2]),p[7]))
def res(sec,off):
    if sec.startswith('.rodata.str'):
        o,_=secs[sec]; e=raw.index(b'\0',o+off); return repr(raw[o+off:e].decode('latin1'))
    for v,sz,n in syms.get(sec,[]):
        if v<=off<v+max(sz,1): return f'{n}+{off-v:#x}' if off!=v else n
    return f'{sec}+{off:#x}'
out=subprocess.run([CL+'llvm-objdump','-d','-r','--no-show-raw-insn',ko],capture_output=True,text=True).stdout
fn=None;base=0
for l in out.splitlines():
    m=re.match(r'^([0-9a-f]+) <(\S+)>:',l)
    if m:
        if not m.group(2).startswith('$'):
            fn=m.group(2); base=int(m.group(1),16)
            if not want or fn in want: print(f'######## {fn}')
        continue
    if want and fn not in want: continue
    m=re.search(r'(R_AARCH64_\S+)\s+(\S+?)(?:([+-])0x([0-9a-f]+))?$',l)
    if m and l.startswith('\t\t'):
        t,sym=m.group(1),m.group(2); off=int(m.group(4) or '0',16)*(-1 if m.group(3)=='-' else 1)
        if 'PG_HI21' in t: continue
        if sym.startswith('.'): sym=res(sym,off)
        elif off: sym+=f'{off:+#x}'
        print(f'           ; {sym}'); continue
    m=re.match(r'\s*([0-9a-f]+):\s+(.*)$',l)
    if m: print(f'{int(m.group(1),16)-base:5x}: {m.group(2).strip()}')
