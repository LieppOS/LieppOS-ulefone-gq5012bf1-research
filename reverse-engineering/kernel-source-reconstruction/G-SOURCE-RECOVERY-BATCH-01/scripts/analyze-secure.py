#!/usr/bin/env python3
from pathlib import Path
import sys,os,subprocess,json,csv,hashlib,collections,argparse
ap=argparse.ArgumentParser();ap.add_argument('--tag',default='D3');args=ap.parse_args();os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];R=P.parents[2];S=R.parent/'android_kernel_modules_secure_transport_ulefone_gq5012bf1';W=Path('/home/armol/kernel-work/g-source-recovery-batch-01');O=W/'dev/secure_transport/out'/args.tag;E=P/'evidence/development'/('secure-'+args.tag);E.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(S/'scripts'));from normalize import kpp,normalized
sha=lambda b:hashlib.sha256(b).hexdigest();summary={};functionrows=[];datarows=[];sections=[]
for r in csv.DictReader((S/'reference/BATCH-MANIFEST.tsv').open(),delimiter='\t'):
 m=r['filename'].removesuffix('.ko');env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',LIEPPOS_VERIFY_MODULE=m);p=subprocess.run(['python3',str(S/'scripts/verify.py'),str(O),str(W/'stock-flat'),str(E/m/'acceptance')],capture_output=True,text=True,env=env);(E/(m+'-whole-stock.log')).write_text(p.stdout+p.stderr);A=kpp.KO(W/'stock-flat'/r['filename']);B=kpp.KO(O/(m+'.stripped'));na,d,n=normalized(A);nb,bd,bn=normalized(B)
 def syms(ko,t):
  out={}
  for y in ko.syms:
   if y['info']&15!=t or not 0<y['shndx']<len(ko.secs):continue
   s=ko.secs[y['shndx']];out[(s['n'],y['val'],y['n'],y['size'])]=b'' if s['type']==8 else ko.b[s['off']+y['val']:s['off']+y['val']+y['size']]
  return out
 counts={}
 for typ,axis,ledger in [(2,'functions',functionrows),(1,'data',datarows)]:
  aa,bb=syms(A,typ),syms(B,typ);exact=sum(aa[k]==bb.get(k) for k in aa);counts[axis]=dict(stock=len(aa),rebuilt=len(bb),exact=exact,unmatched=len(set(aa)^set(bb)))
  for k in sorted(set(aa)|set(bb)):ledger.append(dict(module=m,name=k[2],section=k[0],offset=hex(k[1]),size=k[3],stock_sha256=sha(aa[k]) if k in aa else 'MISSING',rebuilt_sha256=sha(bb[k]) if k in bb else 'MISSING',result='EXACT' if k in aa and aa[k]==bb.get(k) else 'DIFFERENT'))
 av,_=kpp.versions(A);bv,_=kpp.versions(B);abi_diff={s:dict(stock=hex(av[s]),rebuilt=hex(bv[s]) if s in bv else 'MISSING') for s in av if av[s]!=bv.get(s)}
 for sec in A.secs[1:]:
  s=B.sec(sec['n']);sections.append(dict(module=m,section=sec['n'],stock_size=sec['size'],rebuilt_size=s['size'] if s else 'MISSING',stock_sha256=sha(A.data(sec['n'])),rebuilt_sha256=sha(B.data(sec['n'])) if s else 'MISSING',result='EXACT' if s and A.data(sec['n'])==B.data(sec['n']) else 'GNU20_ONLY' if sec['n']=='.note.gnu.build-id' and s else 'DIFFERENT'))
 summary[m]=dict(stock_gate='PASS' if p.returncode==0 else 'REJECT',stock_bytes=len(A.b),rebuilt_bytes=len(B.b),functions=counts['functions'],data=counts['data'],import_crc_residual=abi_diff,whole_normalized_equal=na==nb,build_id_only_if_pass=p.returncode==0)
 print(m,summary[m]['stock_gate'],counts,'CRCresidual',len(abi_diff))
for name,rows in [('functions',functionrows),('data',datarows),('sections',sections)]:
 with (E/(name+'-mismatch-ledger.tsv')).open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
(E/'TARGET-RESULTS.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
