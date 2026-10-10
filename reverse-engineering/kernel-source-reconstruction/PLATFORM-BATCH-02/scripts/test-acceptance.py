#!/usr/bin/env python3
"""Exercise the actual full ELF verifier, not a synthetic acceptance boolean."""
import sys,os,json,csv,tempfile,shutil,subprocess,struct
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=Path('/home/armol/kernel-work/platform-batch-02-cleancheck');N=C/'recipes/android_kernel_modules_memory_platform_ulefone_gq5012bf1';sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp,normalized
O=C/'ws/out/F0-B1';m='mtk-icc-core';K=kpp.KO(O/(m+'.stripped'));_,bid,n=normalized(K);env=dict(os.environ,LIEPPOS_VERIFY_MODULE=m,LIEPPOS_VERIFY_JOINT='1');stock=C/'comparison-F0-B1/stock-operands';results=[]
def run(name,b,expect):
 with tempfile.TemporaryDirectory() as td:
  d=Path(td);(d/(m+'.stripped')).write_bytes(b);p=subprocess.run(['python3',str(N/'scripts/verify.py'),str(d),str(stock)],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);passed=(p.returncode==0)==expect;results.append({'case':name,'expected_accept':expect,'pass':passed,'exit':p.returncode});assert passed,(name,p.stdout[-1000:])
run('unmodified accepted target',K.b,True)
b=bytearray(K.b);b[bid]^=1;run('parsed GNU descriptor only',b,True)
mutations={'ELF header':0,'function instruction':K.sec('.text')['off'],'data initializer':next(s['off'] for s in K.secs if s['n'] in ['.data','.rodata'] and s['size']),'relocation':next(s['off'] for s in K.secs if s['type']==4),'symbol table':K.sec('.symtab')['off']+24,'import CRC':K.sec('__versions')['off'],'module metadata':K.sec('.modinfo')['off'],'string table':K.sec('.strtab')['off']+1,'GNU owner':K.sec('.note.gnu.build-id')['off']+12,'GNU descriptor size':K.sec('.note.gnu.build-id')['off']+4,'section layout':struct.unpack_from('<Q',K.b,40)[0]+64+8}
mutations['export CRC']=next(s['off'] for s in K.secs if 'kcrctab' in s['n'] and s['size'])
for name,off in mutations.items():
 b=bytearray(K.b);b[off]^=1;run(name,b,False)
run('truncated ELF',K.b[:-1],False);run('unexpected appended signature',K.b+b'UNVERIFIED_SIGNATURE',False)
(P/'evidence/acceptance-mutation-tests.json').write_text(json.dumps({'all_pass':all(x['pass'] for x in results),'count':len(results),'cases':results},indent=2)+'\n');print('Actual acceptance mutation cases:',len(results),'all PASS')
