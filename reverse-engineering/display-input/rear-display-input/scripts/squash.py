import sys,re
L=[l for l in sys.stdin.read().splitlines() if not re.search(r'\b(stp|ldp|paciasp|autiasp|adrp)\b',l) and not re.search(r'add\s+x\d+, x\d+, #0x0$',l)]
out=[];i=0
while i<len(L):
    if '#0x8958' in L[i] and i+3<len(L) and '__const_udelay' in L[i+3]:
        n=0
        while i+3<len(L) and '#0x8958' in L[i] and '__const_udelay' in L[i+3]: n+=1;i+=4
        out.append(f'      [udelay(1000) x{n}]');continue
    out.append(L[i]);i+=1
print('\n'.join(out))
