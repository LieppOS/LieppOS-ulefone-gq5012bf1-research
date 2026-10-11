#!/usr/bin/env python3
"""Mutate real accepted module bytes against the unchanged strict ELF verifier."""
from pathlib import Path
import sys,os,json,tempfile,subprocess,struct
P=Path(__file__).resolve().parents[1];N,O,stock=map(Path,sys.argv[1:4]);sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp,normalized
m='mtk_charger_algorithm_class';K=kpp.KO(O/(m+'.stripped'));_,bid,_=normalized(K);env=dict(os.environ,LIEPPOS_VERIFY_JOINT='1',LIEPPOS_VERIFY_MODULE=m,PYTHONDONTWRITEBYTECODE='1');E=P/'evidence/mutation-tests';E.mkdir(exist_ok=True);cases=[]
def run(name,data,expect):
 with tempfile.TemporaryDirectory() as td:
  d=Path(td);(d/(m+'.stripped')).write_bytes(data)
  p=subprocess.run(['python3',str(N/'scripts/verify.py'),str(d),str(stock)],env=env,capture_output=True,text=True)
  good=(p.returncode==0)==expect;cases.append({'case':name,'expected_accept':expect,'pass':good,'exit':p.returncode})
  (E/(str(len(cases)).zfill(2)+'.log')).write_text(p.stdout+p.stderr);assert good,(name,p.stdout,p.stderr)
run('unmodified independently accepted module',K.b,True)
b=bytearray(K.b);b[bid]^=1;run('only structural GNU20 descriptor changes',b,True)
offsets={'ELF magic':0,'function instruction':K.sec('.text')['off'],'data initializer':next(s['off'] for s in K.secs if s['n'] in ['.rodata','.data'] and s['size']),'raw relocation':next(s['off'] for s in K.secs if s['type']==4),'symbol table':K.sec('.symtab')['off']+24,'import CRC':K.sec('__versions')['off'],'export CRC':next(s['off'] for s in K.secs if 'kcrctab' in s['n'] and s['size']),'module metadata':K.sec('.modinfo')['off'],'string table':K.sec('.strtab')['off']+1,'GNU owner':K.sec('.note.gnu.build-id')['off']+12,'GNU descriptor size':K.sec('.note.gnu.build-id')['off']+4,'section flags/layout':struct.unpack_from('<Q',K.b,40)[0]+64+8}
for name,off in offsets.items():
 b=bytearray(K.b);b[off]^=1;run(name,b,False)
run('truncated ELF',K.b[:-1],False);run('unexpected appended payload',K.b+b'NOT_ACCEPTED',False)
off=K.b.find(b'srcversion=',K.sec('.modinfo')['off']);assert off>=0;b=bytearray(K.b);b[off+len(b'srcversion=')]^=1;run('srcversion not silently waived',b,False)
v=next(s for s in K.syms if s['info']&15==2 and 0<s['shndx']<len(K.secs) and s['val']>=4);b=bytearray(K.b);b[K.secs[v['shndx']]['off']+v['val']-4]^=1;run('KCFI prefix',b,False)
for name in ['charger_class','mtk_chg_type_det','rt_pd_manager','tcpc_mt6375','tcpc_class']:
 p=subprocess.run(['python3',str(N/'scripts/verify.py'),str(O),str(stock)],env=dict(env,LIEPPOS_VERIFY_MODULE=name),capture_output=True,text=True)
 cases.append({'case':'unmodified incomplete '+name,'expected_accept':False,'pass':p.returncode!=0,'exit':p.returncode});assert p.returncode!=0
 (E/(str(len(cases)).zfill(2)+'.log')).write_text(p.stdout+p.stderr)
(E/'result.json').write_text(json.dumps({'all_pass':True,'count':len(cases),'cases':cases,'verifier':str(N/'scripts/verify.py'),'scope':'Real accepted ELF mutation plus five unchanged C rejections. No false positive build-ID-only exemption for metadata or source fingerprints.'},indent=2)+'\n');print('Real ELF mutation/rejection tests',len(cases),'PASS')
