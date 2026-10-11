#!/usr/bin/env python3
"""Complete five-ELF diagnostic ledgers. Only structural GNU20 normalization.
Usage: compare-five.py RECIPE STOCK_RESEARCH BUILD_OUT REPORT_DIR
No mismatch is waived: partial code/data evidence is never A/B acceptance.
"""
from pathlib import Path
import csv,sys,json,hashlib,struct,collections,subprocess,os
P=Path(__file__).resolve().parents[1]
N,ROOT,O,D=map(Path,sys.argv[1:5]);D.mkdir(parents=True,exist_ok=True)
sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'))
from normalize import kpp,normalized
manifest={r['filename'].removesuffix('.ko'):r for r in csv.DictReader((P/'evidence/baseline/ALL-458-MODULES.tsv').open(),delimiter='\t')}
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(name,head,rows,folder):
 with (folder/name).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(head);w.writerows(rows)
def body(k,s):
 sec=k.secs[s['shndx']]
 return b'' if sec['type']==8 else k.b[sec['off']+s['val']:sec['off']+s['val']+s['size']]
def typed(k,typ):
 out=collections.defaultdict(list)
 for s in k.syms:
  if s['info']&15==typ and 0<s['shndx']<len(k.secs):out[k.secs[s['shndx']]['n'],s['n']].append(s)
 return out
def exports(k):
 out={}
 for s in k.syms:
  if not s['n'].startswith('__crc_') or not 0<s['shndx']<len(k.secs):continue
  sec=k.secs[s['shndx']]
  if 'kcrctab' not in sec['n']:continue
  out[s['n'][6:]]=['EXPORT_SYMBOL_GPL' if '_gpl' in sec['n'] else 'EXPORT_SYMBOL',struct.unpack_from('<I',k.b,sec['off']+s['val'])[0]]
 assert len(out)*4==sum(s['size'] for s in k.secs if 'kcrctab' in s['n'])
 return out
summary=[]
for m in ['charger_class','mtk_chg_type_det','rt_pd_manager','tcpc_mt6375','tcpc_class']:
 r=manifest[m];E=D/m;E.mkdir(exist_ok=True)
 stock=ROOT/r['stock_paths'].split(';')[0];a=kpp.KO(stock);b=kpp.KO(O/(m+'.stripped'))
 assert sha(a.b)==r['stock_sha256'],'stock identity drift'
 an,ad,al=normalized(a);bn,bd,bl=normalized(b)
 j={'module':m,'module_id':r['module_id'],'original_class':'C','final_class':'C','stock_sha256':sha(a.b),'source_sha256':sha(b.b),'source_normalized_sha256':sha(bn),'stock_size':len(a.b),'source_size':len(b.b),'whole_permitted_stock_parity':an==bn and (ad,al)==(bd,bl),'normalization':'Only the parsed 20-byte GNU build-ID descriptor','axes':{}}
 for typ,axis in [(2,'functions'),(1,'data')]:
  aa,bb=typed(a,typ),typed(b,typ);rows=[]
  for key in sorted(set(aa)|set(bb)):
   for ordinal in range(max(len(aa[key]),len(bb[key]))):
    s=aa[key][ordinal] if ordinal<len(aa[key]) else None;t=bb[key][ordinal] if ordinal<len(bb[key]) else None
    x=body(a,s) if s else None;y=body(b,t) if t else None
    exact=s is not None and t is not None and s['size']==t['size'] and x==y
    pos=exact and s['val']==t['val']
    rows.append([key[1],key[0],ordinal,s['val'] if s else '',s['size'] if s else '',t['val'] if t else '',t['size'] if t else '',sha(x) if x is not None else '',sha(y) if y is not None else '',exact,pos])
  save(axis+'.tsv',['name','section','ordinal','stock_offset','stock_size','source_offset','source_size','stock_sha256','source_sha256','body_exact','body_and_position_exact'],rows,E)
  j['axes'][axis]={'stock_count':sum(map(len,aa.values())),'source_count':sum(map(len,bb.values())),'body_exact':sum(v[-2] for v in rows),'body_and_position_exact':sum(v[-1] for v in rows),'unmatched':[v[0] for v in rows if not v[-2]]}
 sections=[];rels=[]
 for name in sorted(set(a.sec_by_name)|set(b.sec_by_name)):
  s=a.sec(name);t=b.sec(name);x=a.data(name) if s else None;y=b.data(name) if t else None
  layout=s is not None and t is not None and all(s[k]==t[k] for k in ['type','flags','off','size','link','info','align','entsz'])
  sections.append([name,s['size'] if s else '',t['size'] if t else '',sha(x) if x is not None else '',sha(y) if y is not None else '',layout,x==y])
  if (s and s['type']==4) or (t and t['type']==4):
   xs=list(a.rela_entries(s)) if s else [];ys=list(b.rela_entries(t)) if t else []
   def semantic(k,e):
    if not e:return None
    sym=k.syms[e[1]>>32];target=sym['n']
    if not target and 0<sym['shndx']<len(k.secs):target='SECTION:'+k.secs[sym['shndx']]['n']
    return [e[0],e[1]&0xffffffff,target,e[2]]
   for i in range(max(len(xs),len(ys))):
    xx=xs[i] if i<len(xs) else None;yy=ys[i] if i<len(ys) else None
    rels.append([name,i,json.dumps(xx),json.dumps(yy),json.dumps(semantic(a,xx)),json.dumps(semantic(b,yy)),xx==yy,semantic(a,xx)==semantic(b,yy)])
 save('sections.tsv',['section','stock_size','source_size','stock_sha256','source_sha256','layout_exact','content_exact'],sections,E)
 save('relocations.tsv',['section','index','stock_raw','source_raw','stock_semantic','source_semantic','raw_exact','semantic_exact'],rels,E)
 j['different_sections']=[v[0] for v in sections if not v[-1]];j['section_layout_exact']=all(v[-2] for v in sections)
 j['raw_relocations_exact']=all(v[-2] for v in rels);j['semantic_relocations_exact']=all(v[-1] for v in rels);j['relocation_records']=len(rels)
 va,vb=kpp.versions(a)[0],kpp.versions(b)[0];ea,eb=exports(a),exports(b)
 ka={s['n']:s['val'] for s in a.syms if s['n'].startswith('__kcfi_typeid_')};kb={s['n']:s['val'] for s in b.syms if s['n'].startswith('__kcfi_typeid_')}
 abi={'stock_imports':va,'source_imports':vb,'stock_exports':ea,'source_exports':eb,'stock_kcfi':ka,'source_kcfi':kb}
 (E/'abi.json').write_text(json.dumps(abi,indent=2)+'\n');j['import_crc_exact']=va==vb;j['export_crc_and_license_exact']=ea==eb;j['kcfi_abs_exact']=ka==kb
 (E/'symbols.json').write_text(json.dumps({'stock':a.syms,'source':b.syms},indent=2)+'\n')
 for label,k in [('stock',a),('source',b)]:
  (E/(label+'.modinfo.bin')).write_bytes(k.data('.modinfo'))
  (E/(label+'.modinfo.txt')).write_text('\n'.join(v.decode(errors='replace') for v in k.data('.modinfo').split(b'\0') if v)+'\n')
 j['modinfo_exact']=a.data('.modinfo')==b.data('.modinfo')
 j['btf']={n:{'stock_present':a.sec(n) is not None,'source_present':b.sec(n) is not None,'bytes_exact':a.data(n)==b.data(n)} for n in ['.BTF','.BTF.ext']}
 diff=[i for i,(x,y) in enumerate(zip(a.b,b.b)) if x!=y];ranges=[]
 for i in diff:
  if ranges and ranges[-1][1]==i:ranges[-1][1]+=1
  else:ranges.append([i,i+1])
 j['raw_differing_bytes']=len(diff);j['raw_difference_ranges']=ranges;j['length_delta']=len(b.b)-len(a.b)
 j['source_counter_symbols']=[s['n'] for s in b.syms if s['n'].startswith('__UNIQUE_ID_')]
 j['stock_counter_symbols']=[s['n'] for s in a.syms if s['n'].startswith('__UNIQUE_ID_')]
 # Exercise the unchanged strict verifier. An expected rejection is NOT acceptance.
 env=dict(os.environ,LIEPPOS_VERIFY_MODULE=m,LIEPPOS_VERIFY_JOINT='1',PYTHONDONTWRITEBYTECODE='1')
 p=subprocess.run(['python3',str(N/'scripts/verify.py'),str(O)],capture_output=True,text=True,env=env)
 (E/'strict-stock-acceptance.log').write_text(p.stdout+p.stderr);j['strict_stock_verifier_exit']=p.returncode
 assert not j['whole_permitted_stock_parity'] and p.returncode!=0,'New parity requires full independent certification review'
 (E/'result.json').write_text(json.dumps(j,indent=2)+'\n');summary.append(j)
 print(m,'functions',j['axes']['functions'],'data',j['axes']['data'],'strict acceptance',p.returncode)
(D/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
