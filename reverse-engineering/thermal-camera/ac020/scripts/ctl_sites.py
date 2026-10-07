import re,sys
# usage: ctl_sites.py file.dis target_symbol
dis=open(sys.argv[1]).read().splitlines(); tgt=sys.argv[2]
func=None; buf=[]
out=[]
for l in dis:
    m=re.match(r'^([0-9a-f]+) <(.+)>:',l)
    if m: func=m.group(2); buf=[]; continue
    p=l.strip().split('\t')
    if len(p)<2: continue
    addr=p[0].rstrip(':'); op=p[1] if len(p)>1 else ''; args=p[2] if len(p)>2 else ''
    buf.append((addr,op,args))
    if op in('bl','b') and f'<{tgt}@plt>' in args:
        regs={}
        for a,o,ar in reversed(buf[:-1][-40:]):
            if o in('ret',) : break
            if o in('bl','b') and '@plt' in ar and tgt not in ar: break
            mm=re.match(r'w([1-7]), #(-?0x[0-9a-f]+|-?\d+)',ar)
            if o=='mov' and mm and mm.group(1) not in regs: regs[mm.group(1)]=hex(int(mm.group(2),0)&0xffff)
            mz=re.match(r'w([1-7]), wzr',ar)
            if o=='mov' and mz and mz.group(1) not in regs: regs[mz.group(1)]='0x0'
            mr=re.match(r'w([1-7]), (w\d+)',ar)
            if o=='mov' and mr and mr.group(1) not in regs: regs[mr.group(1)]='reg:'+mr.group(2)
            mo=re.match(r'w([1-7]), wzr, #(0x[0-9a-f]+)',ar)
            if o=='orr' and mo and mo.group(1) not in regs: regs[mo.group(1)]=mo.group(2)
            ml=re.match(r'w([1-7]), (w\d+), #(\d+)',ar)
            if o=='lsl' and ml and ml.group(1) not in regs: regs[ml.group(1)]=f'{ml.group(2)}<<{ml.group(3)}'
            ml=re.match(r'w([1-7]), \[(.*)\]',ar)
            if o.startswith('ldr') and ml and ml.group(1) not in regs: regs[ml.group(1)]='mem['+ml.group(2)+']'
        out.append((addr,func,op,regs))
for a,f,o,r in out:
    print(a,f,o,' '.join(f'w{k}={r.get(k,"?")}' for k in '12346'))
