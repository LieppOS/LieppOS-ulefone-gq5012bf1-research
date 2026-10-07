import re,sys
txt=open(sys.argv[1]).read()
for fn in sys.argv[2:]:
    m=re.search(r'\n[0-9a-f]+ <'+re.escape(fn)+r'>:\n(.*?)(?=\n[0-9a-f]{16} <[^$]|\nDisassembly of|\Z)',txt,re.S)
    out=[f'== {fn}']
    for l in m.group(1).split('\n'):
        l=l.strip()
        if not l or re.match(r'^[0-9a-f]{16} <\$',l): continue
        if 'R_AARCH64' in l:
            r=l.split('R_AARCH64_')[1]
            r=re.sub(r'ADR_PREL_PG_HI21\s*','PG ',r); r=re.sub(r'ADD_ABS_LO12_NC\s*','LO ',r); r=re.sub(r'LDST(\d+)_ABS_LO12_NC\s*',r'LS\1 ',r); r=re.sub(r'CALL26\s*','',r)
            out[-1]=re.sub(r'\s+0x[0-9a-f]+ <[^>]*>','',out[-1])+'   ; '+r
        else: out.append(re.sub(r'\s+',' ',l,count=1))
    print('\n'.join(out))
