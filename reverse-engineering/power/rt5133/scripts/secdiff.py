import subprocess,re,sys
def secs(k):
    raw=open(k,'rb').read(); d={}
    for l in subprocess.run(['llvm-readelf','-SW',k],capture_output=True,text=True).stdout.splitlines():
        m=re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)',l)
        if m: o,s=int(m.group(3),16),int(m.group(4),16); d[m.group(1)]=raw[o:o+s] if m.group(2)!='NOBITS' else s
    return d
a=secs(sys.argv[1]); b=secs(sys.argv[2])
print(f'sections {len(a)} vs {len(b)}; differing:',[n for n in sorted(set(a)|set(b)) if a.get(n)!=b.get(n)])
