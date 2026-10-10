#!/usr/bin/env python3
"""Preserve every incomplete axis; no srcversion/BTF/CRC/symbol normalization."""
from pathlib import Path
import csv,json,sys,hashlib,collections,os,struct
P=Path(__file__).resolve().parents[1];R=P.parents[2];N=Path(os.environ.get('LIEPPOS_BATCH_RECIPE',str(R.parent/'android_kernel_modules_charging_battery_ulefone_gq5012bf1')));sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp,normalized
O=Path(sys.argv[1]);D=Path(sys.argv[2]);comparison=json.loads((D/'comparison.json').read_text());manifest={r['module_id']:r for r in csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t')};summary=[]
def object_bytes(k,s):
 sec=k.secs[s['shndx']];return b'' if sec['type']==8 else k.b[sec['off']+s['val']:sec['off']+s['val']+s['size']]
for x in comparison:
 if x['status']=='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE':continue
 r=manifest[x['module_id']];m=x['module'];E=D/'incomplete'/m;E.mkdir(parents=True,exist_ok=True)
 if not (O/(m+'.stripped')).exists():continue
 a=kpp.KO(R/r['stock_paths'].split(';')[0]);b=kpp.KO(O/(m+'.stripped'));an,ad,al=normalized(a);bn,bd,bl=normalized(b);assert an!=bn or x['provider_boundary_failures'];axes={};different_names={}
 for typ,axis in [(2,'functions'),(1,'data')]:
  aa=[s for s in a.syms if s['info']&15==typ and 0<s['shndx']<len(a.secs)];bb=collections.defaultdict(list);ledger=[];seen=collections.Counter()
  for t in b.syms:
   if t['info']&15==typ and 0<t['shndx']<len(b.secs):bb[(b.secs[t['shndx']]['n'],t['n'])].append(t)
  for s in aa:
   sec=a.secs[s['shndx']]['n'];key=(sec,s['n']);ordinal=seen[key];seen[key]+=1;ts=bb.get(key,[]);t=ts[ordinal] if ordinal<len(ts) else None;ab=object_bytes(a,s);cb=object_bytes(b,t) if t else None;exact=t is not None and ab==cb and s['size']==t['size'];pos=t is not None and s['val']==t['val'];ledger.append([s['n'],sec,s['val'],s['size'],t['val'] if t else '',t['size'] if t else '',hashlib.sha256(ab).hexdigest(),hashlib.sha256(cb).hexdigest() if t else '',exact,pos,'EXACT' if exact and pos else 'BODY_EXACT_POSITION_DIFFERENT' if exact else 'UNMATCHED'])
   if not exact:
    sf=E/'unmatched-bytes';sf.mkdir(exist_ok=True);name=s['n'].replace('/','_');(sf/(axis+'-'+name+'.stock.bin')).write_bytes(ab)
    if t:(sf/(axis+'-'+name+'.source.bin')).write_bytes(cb)
  with (E/(axis+'-parity.tsv')).open('w') as f:
   w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['name','section','stock_offset','stock_size','source_offset','source_size','stock_sha256','source_sha256','body_exact','position_exact','result']);w.writerows(ledger)
  axes[axis]={'stock_count':len(aa),'source_count':sum(len(v) for v in bb.values()),'named_body_exact':sum(row[8] for row in ledger),'position_and_body_exact':sum(row[8] and row[9] for row in ledger)};different_names[axis]=[row[0] for row in ledger if not row[8]]
 sections=[];rel=[]
 for s in a.secs[1:]:
  t=b.sec(s['n']);ab=a.data(s['n']);cb=b.data(s['n']) if t else None;sections.append([s['n'],s['type'],s['off'],s['size'],t['off'] if t else '',t['size'] if t else '',hashlib.sha256(ab).hexdigest(),hashlib.sha256(cb).hexdigest() if t else '',t==s,ab==cb])
  if s['type']==4:
   aa=list(a.rela_entries(s));bb=list(b.rela_entries(t)) if t else [];n=max(len(aa),len(bb))
   for i in range(n):
    ar=aa[i] if i<len(aa) else None;br=bb[i] if i<len(bb) else None;semantic=lambda k,e:[e[0],e[1]&0xffffffff,k.sym_name(e[1]>>32),e[2]] if e else None;arsem=semantic(a,ar);brsem=semantic(b,br);rel.append([s['n'],i,json.dumps(ar),json.dumps(br),json.dumps(arsem),json.dumps(brsem),ar==br,arsem==brsem])
 for name,headers,rs in [('sections',['name','type','stock_offset','stock_size','source_offset','source_size','stock_sha256','source_sha256','layout_exact','content_exact'],sections),('relocations',['section','index','stock_raw','source_raw','stock_semantic','source_semantic','raw_exact','semantic_exact'],rel)]:
  with (E/(name+'-parity.tsv')).open('w') as f:w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(headers);w.writerows(rs)
 (E/'stock.modinfo.bin').write_bytes(a.data('.modinfo'));(E/'source.modinfo.bin').write_bytes(b.data('.modinfo'));(E/'symbol-tables.json').write_text(json.dumps({'stock':a.syms,'source':b.syms},indent=2)+'\n');(E/'CRC-KCFI.json').write_text(json.dumps({'imports_stock':kpp.versions(a)[0],'imports_source':kpp.versions(b)[0],'exports_stock':kpp.exports(a),'exports_source':kpp.exports(b),'stock_kcfi_abs':{s['n']:s['val'] for s in a.syms if s['n'].startswith('__kcfi_typeid_')},'source_kcfi_abs':{s['n']:s['val'] for s in b.syms if s['n'].startswith('__kcfi_typeid_')}},indent=2)+'\n')
 j={'module_id':x['module_id'],'module':m,'final_class':'C','initial_class':x['initial_class'],'stock_sha256':hashlib.sha256(a.b).hexdigest(),'source_sha256':hashlib.sha256(b.b).hexdigest(),'stock_size':len(a.b),'source_size':len(b.b),'axes':axes,'unmatched_names':different_names,'different_sections':x['different_sections'],'import_crc_mismatches':x['import_crc_mismatches'],'export_crc_mismatches':x['export_crc_mismatches'],'kcfi_mismatches':x['kcfi_abs_mismatches'],'provider_boundary_failures':x['provider_boundary_failures'],'relocation_records_stock':sum(s['size']//24 for s in a.secs if s['type']==4),'relocation_records_source':sum(s['size']//24 for s in b.secs if s['type']==4),'raw_and_semantic_relocations_exact':all(v[-1] and v[-2] for v in rel),'raw_difference_ranges':x['raw_difference_ranges'],'permitted_normalization':'GNU20 structural descriptor only; remaining differences not normalized','next_experiment':'Resolve actual2.0.31 OEM PD/timer/sysfs source differences and source-token provenance; inspect exact record-level ledgers, not code-count shortcuts' if m=='tcpc_class' else 'Recover authentic OEM token/counter lineage; srcversion is retained as mismatch, never manufactured or normalized'};(E/'incomplete-acceptance.json').write_text(json.dumps(j,indent=2)+'\n');summary.append(j)
(D/'incomplete-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for j in summary:print(j['module'],j['axes'],'unmatched',j['unmatched_names'],'sections',j['different_sections'],'relocations_exact',j['raw_and_semantic_relocations_exact'])
