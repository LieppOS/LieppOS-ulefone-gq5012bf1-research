import subprocess,sys,re
from concurrent.futures import ThreadPoolExecutor
K='/home/armol/kernel-work/gki-12901745-workspace/lieppos/nfc/kout'
pre=open(sys.argv[1]).read(); old=sys.argv[2]; want=sys.argv[3]; cands=open(sys.argv[4]).read().split()
pat=re.compile(r'\b'+re.escape(old)+r'\b')
def f(c):
    g=subprocess.run([K+'/scripts/genksyms/genksyms','-r','/dev/null'],input=pat.sub(c,pre),capture_output=True,text=True).stdout
    return c, want in g
with ThreadPoolExecutor(16) as ex:
    for c,ok in ex.map(f,cands):
        if ok: print('MATCH',c); sys.stdout.flush()
print('done')
