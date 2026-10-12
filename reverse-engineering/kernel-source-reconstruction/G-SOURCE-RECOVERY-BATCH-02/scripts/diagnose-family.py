#!/usr/bin/env python3
"""Actualtypeddiagnostics for everyfrozenmodule; failedstockgates neverwaived."""
from pathlib import Path
import sys,csv,json,subprocess,os,hashlib,collections
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2].parent;family=sys.argv[1];tag=sys.argv[2];ws=Path(sys.argv[3]);S=ROOT/('android_kernel_modules_'+family+'_ulefone_gq5012bf1');sys.path.insert(0,str(S/'scripts'));from normalize import kpp,normalized
W=Path('/home/armol/kernel-work/g-source-recovery-batch-02');O=ws/'out'/tag;D=P/'evidence/development'/(family+'-'+tag);D.mkdir(parents=True,exist_ok=True);rows=[];sha=lambda b:hashlib.sha256(b).hexdigest()
def symbols(k,t):return {(k.secs[y['shndx']]['n'],y['val'],y['n'],y['size']):(b'' if k.secs[y['shndx']]['type']==8 else k.b[k.secs[y['shndx']]['off']+y['val']:k.secs[y['shndx']]['off']+y['val']+y['size']]) for y in k.syms if y['info']&15==t and 0<y['shndx']<len(k.secs)}
for r in csv.DictReader((S/'reference/BATCH-MANIFEST.tsv').open(),delimiter='\t'):
 m=r['filename'].removesuffix('.ko');f=O/(m+'.stripped');A=kpp.KO(W/'stock-flat'/r['filename']);v=dict(module_id=r['module_id'],module=m,stock_sha256=r['stock_sha256'],compiled=f.exists(),strict_stock='NOT_BUILT',functions_exact=0,data_exact=0,functions_total=len(symbols(A,2)),data_total=len(symbols(A,1)))
 if f.exists():
  B=kpp.KO(f);p=subprocess.run(['python3',str(S/'scripts/verify.py'),str(O),str(W/'stock-flat'),str(D/m)],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',LIEPPOS_VERIFY_MODULE=m));(D/(m+'-strict.log')).write_text(p.stdout+p.stderr);v.update(strict_stock='PASS' if p.returncode==0 else 'REJECT',strict_exit=p.returncode,stock_bytes=len(A.b),rebuilt_bytes=len(B.b),rebuilt_sha256=sha(B.b),functions_exact=sum(vv==symbols(B,2).get(k) for k,vv in symbols(A,2).items()),data_exact=sum(vv==symbols(B,1).get(k) for k,vv in symbols(A,1).items()),function_residuals=[list(k) for k,vv in symbols(A,2).items() if vv!=symbols(B,2).get(k)],data_residuals=[list(k) for k,vv in symbols(A,1).items() if vv!=symbols(B,1).get(k)])
  secs=[]
  for s in A.secs:
   if s['type']==8 or s['n']=='.note.gnu.build-id':continue
   t=B.sec(s['n']);a=A.data(s['n']);b=B.data(s['n']) if t else b''
   if a!=b:secs.append(dict(section=s['n'],stock_bytes=len(a),rebuilt_bytes=len(b),different_overlap_bytes=sum(x!=y for x,y in zip(a,b)),stock_sha256=sha(a),rebuilt_sha256=sha(b)))
  va,_=kpp.versions(A);vb,_=kpp.versions(B);v.update(nonGNU_section_residuals=secs,imports_equal=va==vb,import_residuals={s:dict(stock=hex(c),rebuilt=hex(vb[s]) if s in vb else 'MISSING') for s,c in va.items() if vb.get(s)!=c},kcfi_abs_equal=[(y['n'],y['val']) for y in A.syms if y['n'].startswith('__kcfi_typeid_')]==[(y['n'],y['val']) for y in B.syms if y['n'].startswith('__kcfi_typeid_')],modinfo_equal=A.data('.modinfo')==B.data('.modinfo'),stock_modinfo=[x.decode(errors='replace') for x in A.data('.modinfo').split(b'\0') if x],rebuilt_modinfo=[x.decode(errors='replace') for x in B.data('.modinfo').split(b'\0') if x])
 rows.append(v);print(m,v['compiled'],v['strict_stock'],'functions',v['functions_exact'],v['functions_total'],'data',v['data_exact'],v['data_total'],'residual_sections',[s['section'] for s in v.get('nonGNU_section_residuals',[])],flush=True)
for f in O.glob('*'):
 if f.is_file() and f.suffix not in ['.ko','.stripped']:shutil=None; (D/f.name).write_bytes(f.read_bytes())
if (O/'provider').exists():
 import shutil;shutil.copytree(O/'provider',D/'provider',dirs_exist_ok=True)
(D/'ACTUAL-RESULTS.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
