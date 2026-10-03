#!/usr/bin/env python3
from pathlib import Path
import re,csv
ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'mt6369/source'
h=(S/'mt6369.h').read_text(errors='ignore').replace('\\\n',' ')
mac={m.group(1):m.group(2).strip() for m in re.finditer(r'^#define\s+(\w+)\s+([^\n/]+)',h,re.M)}
def val(k,seen=()):
    if k in seen:return None
    s=mac.get(k,'').strip().strip('()')
    try:return int(s,0)
    except ValueError:pass
    toks=re.findall(r'\b[A-Za-z_]\w*\b',s)
    if len(toks)==1:return val(toks[0],seen+(k,))
    return None
rows=[]
for src in ('mt6369.c','mt6369-accdet.c'):
    t=(S/src).read_text(errors='ignore')
    ids=set(re.findall(r'\b(?:MT6369_[A-Z0-9_]+|[A-Z][A-Z0-9_]+_ADDR)\b',t))
    for k in ids:
        v=val(k)
        if v is not None and v>=0x100: rows.append((v,k,src,t.count(k)))
with (ROOT/'mt6369/registers.tsv').open('w') as f:
    f.write('address\tmacro\tsource\treferences\n')
    for v,k,s,c in sorted(set(rows)):f.write(f'0x{v:04x}\t{k}\t{s}\t{c}\n')
