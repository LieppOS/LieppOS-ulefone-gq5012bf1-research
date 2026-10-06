import re,sys,collections
dis=open('ircmd.dis').read().split('\n\n')
rows=[]
for blk in dis:
    m=re.search(r'^[0-9a-f]+ <([^>]+)>:',blk,re.M)
    if not m: continue
    fn=m.group(1)
    if not re.match(r'(adv|basic|sys|spi|dfu|test)_',fn): continue
    regs={}; stores={}; calls=[]; base=0
    for line in blk.splitlines()[1:]:
        p=line.split('\t')
        if len(p)<3: continue
        op=p[1].strip(); args=p[2].strip() if len(p)>2 else ''
        mm=re.match(r'(w\d+|x\d+), #(-?0x[0-9a-f]+|-?\d+)',args)
        if op=='mov' and mm: regs[mm.group(1)[1:]]=int(mm.group(2),0); continue
        if op=='movk':
            mk=re.match(r'w(\d+), #(0x[0-9a-f]+), lsl #(\d+)',args)
            if mk and mk.group(1) in regs: regs[mk.group(1)]|=int(mk.group(2),16)<<int(mk.group(3))
            continue
        if op=='orr':
            mo=re.match(r'w(\d+), wzr, #(0x[0-9a-f]+)',args)
            if mo: regs[mo.group(1)]=int(mo.group(2),16); continue
        ms=re.match(r'(strh|strb|str) (w\d+|wzr), \[sp(?:, #(0x[0-9a-f]+|\d+))?\]$',args) if op in('strh','strb','str') else None
        if op in('strh','strb','str'):
            ms=re.match(r'(w\d+|wzr), \[sp(?:, #(0x[0-9a-f]+|\d+))?\]$',args)
            if ms:
                off=int(ms.group(2),0) if ms.group(2) else 0
                r=ms.group(1); v=0 if r=='wzr' else regs.get(r[1:])
                if v is not None: stores[off]=(op,v)
            continue
        mx=re.match(r'x1, sp(?:, #(0x[0-9a-f]+|\d+))?$',args)
        if op in('add','mov') and mx: base=int(mx.group(1),0) if mx.group(1) else 0
        mb=re.match(r'0x[0-9a-f]+ <([a-z_0-9]+)@plt>',args)
        if op=='bl' and mb and re.search(r'cmd_(read|write)|long_time|short_cmd',mb.group(1)):
            calls.append((mb.group(1),{k-base:v for k,v in stores.items() if 0<=k-base<=6},regs.get('2')))
            stores={}
    for c,s,w2 in calls:
        f=' '.join(f'+{k}:{v:#x}' for k,v in sorted((k,v[1]) for k,v in s.items()))
        rows.append((fn,c,f,'' if w2 is None else hex(w2)))
for r in rows: print('\t'.join(r))
