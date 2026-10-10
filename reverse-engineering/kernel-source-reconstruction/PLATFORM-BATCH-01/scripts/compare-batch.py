#!/usr/bin/env python3
"""Investigate all35; exact full-file acceptance is stricter than partial axis matches."""
import csv,sys,json,hashlib,struct,collections,os,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];N=R.parent/'android_kernel_modules_power_platform_ulefone_gq5012bf1'
sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp,normalized
O=Path(sys.argv[1]);D=Path(sys.argv[2]);D.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));out=[]
provider_errors=json.loads((O/'provider/provider-errors.json').read_text());bad={e[0] for e in provider_errors};edges=list(csv.DictReader((P/'DEPENDENCIES.tsv').open(),delimiter='\t'))
def syms(k,typ):
 d={}
 for v in k.syms:
  if v['info']&15==typ and 0<v['shndx']<len(k.secs):
   sec=k.secs[v['shndx']];key=(sec['n'],v['n'],v['val'],v['size']);b=b'' if sec['type']==8 else k.b[sec['off']+v['val']:sec['off']+v['val']+v['size']];d[key]=b
 return d
def exports(k):
 d={}
 for v in k.syms:
  if v['n'].startswith('__crc_') and 0<v['shndx']<len(k.secs):
   sec=k.secs[v['shndx']]
   if 'kcrctab' in sec['n']:d[v['n'][6:]]=(sec['n'],struct.unpack_from('<I',k.b,sec['off']+v['val'])[0])
 return d
for r in rows:
 m=r['filename'].removesuffix('.ko');a=kpp.KO(R/r['stock_paths'].split(';')[0]);f=O/(m+'.stripped');x={'module_id':r['module_id'],'module':m,'family':r['dependency_group'],'initial_class':'D','status':'NOT_BUILT','stock_functions':int(r['stock_functions']),'stock_data':int(r['stock_data_objects']),'residual':[]}
 if not f.exists():x['residual']=['No linked target: inspect objects.log/modules.log'];out.append(x);continue
 b=kpp.KO(f);an,ad,al=normalized(a);bn,bd,bl=normalized(b);x['status']='SOURCE_BUILD_UNVERIFIED';x['stock_size']=len(a.b);x['rebuild_size']=len(b.b)
 x['stock_sha256']=hashlib.sha256(a.b).hexdigest();x['normalized_sha256']=hashlib.sha256(bn).hexdigest()
 for typ,axis in [(2,'functions'),(1,'data')]:
  aa,bb=syms(a,typ),syms(b,typ);same=[k for k in aa if k in bb and aa[k]==bb[k]];x[axis+'_exact']=len(same);x[axis+'_rebuilt']=len(bb);x[axis+'_different']=[list(k) for k in aa if k not in same]
 va,_=kpp.versions(a);vb,_=kpp.versions(b);x['import_crc_mismatches']=[s for s in set(va)|set(vb) if va.get(s)!=vb.get(s)]
 ea,eb=exports(a),exports(b);x['export_crc_mismatches']=[s for s in set(ea)|set(eb) if ea.get(s)!=eb.get(s)]
 ka={v['n']:v['val'] for v in a.syms if v['n'].startswith('__kcfi_typeid_')};kb={v['n']:v['val'] for v in b.syms if v['n'].startswith('__kcfi_typeid_')};x['kcfi_abs_mismatches']=[s for s in set(ka)|set(kb) if ka.get(s)!=kb.get(s)];x['provider_boundary_failures']=sorted({e['symbol'] for e in edges if e['consumer_module_id']==r['module_id'] and e['symbol'] in bad})
 x['different_sections']=[s['n'] for s in a.secs[1:] if not b.sec(s['n']) or a.data(s['n'])!=b.data(s['n'])]
 # All raw differences are saved before any normalization; differing lengths remain explicit.
 diff=[i for i,(u,v) in enumerate(zip(a.b,b.b)) if u!=v];ranges=[]
 for i in diff:
  if ranges and i==ranges[-1][1]:ranges[-1][1]+=1
  else:ranges.append([i,i+1])
 x['raw_differing_bytes_in_overlap']=len(diff);x['raw_difference_ranges']=ranges;x['length_delta']=len(b.b)-len(a.b)
 if an==bn and (ad,al)==(bd,bl) and not x['provider_boundary_failures']:
  env=dict(os.environ,LIEPPOS_VERIFY_MODULE=m,LIEPPOS_VERIFY_JOINT='1');stock=D/'stock-operands';stock.mkdir(exist_ok=True);link=stock/(m+'.ko')
  if not link.exists():link.symlink_to((R/r['stock_paths'].split(';')[0]).resolve())
  p=subprocess.run(['python3',str(N/'scripts/verify.py'),str(O),str(stock),str(D/m)],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(D/(m+'-verification.txt')).write_text(p.stdout)
  if p.returncode==0:x['status']='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE'
  else:x['residual'].append(p.stdout[-1000:])
 else:
  if an!=bn:x['residual'].append('Whole normalized ELF differs: no A/B')
  if x['provider_boundary_failures']:x['residual'].append('Source provider CRC/licence/KCFI failures:'+','.join(x['provider_boundary_failures']))
 out.append(x)
(D/'comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print('all35 investigated',dict(collections.Counter(x['status'] for x in out)))
for x in out:print(x['module'],x['status'],'fn',x.get('functions_exact'),'/'+str(x['stock_functions']),'data',x.get('data_exact'),'/'+str(x['stock_data']),'CRC',x.get('import_crc_mismatches'),x.get('export_crc_mismatches'),'KCFI',x.get('kcfi_abs_mismatches'))
