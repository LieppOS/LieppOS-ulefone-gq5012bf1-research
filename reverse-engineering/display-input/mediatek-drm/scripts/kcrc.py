import subprocess,re,sys,struct
def crcs(k):
    raw=open(k,'rb').read()
    sh=subprocess.run(['llvm-readelf','-SW',k],capture_output=True,text=True).stdout
    secs={}
    for m in re.finditer(r'\[\s*(\d+)\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)',sh): secs[m.group(1)]=(m.group(2),int(m.group(3),16))
    out={}
    for l in subprocess.run(['llvm-readelf','-sW',k],capture_output=True,text=True).stdout.splitlines():
        p=l.split()
        if len(p)>=8 and p[7].startswith('__crc_'):
            n,off=secs[p[6]]; v=int(p[1],16)
            out[p[7][6:]]=struct.unpack('<I',raw[off+v:off+v+4])[0]
    return out
a=crcs(sys.argv[1]); b=crcs(sys.argv[2])
for k in sorted(set(a)|set(b)):
    if a.get(k)!=b.get(k): print(k, hex(a.get(k,0)), hex(b.get(k,0)))
print(len(a),len(b))
