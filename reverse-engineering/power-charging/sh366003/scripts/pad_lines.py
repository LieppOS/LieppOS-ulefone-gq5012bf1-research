import re,sys
src=open(sys.argv[1]).read().split('\n'); out=[]; ok=True
for l in src:
    m=re.search(r'\s*/\*@(\d+)\*/\s*$',l)
    if m:
        tgt=int(m.group(1)); l=l[:m.start()]
        cur=len(out)+1
        if cur>tgt: print('OVER',tgt,cur,l.strip()[:60]); ok=False
        else: out+=['']*(tgt-cur)
    out.append(l)
open(sys.argv[2],'w').write('\n'.join(out))
print('lines',len(out),'ok',ok)
