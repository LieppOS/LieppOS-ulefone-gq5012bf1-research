#!/usr/bin/env python3
"""Preserve incomplete full acceptance; NEVER normalize mismatching BTF to certify."""
from pathlib import Path
import sys,csv,json,hashlib,struct,collections,os
P=Path(__file__).resolve().parents[1];R=P.parents[2];N=Path(os.environ.get('LIEPPOS_BATCH_RECIPE',str(R.parent/'android_kernel_modules_secure_diagnostics_ulefone_gq5012bf1')));sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp,normalized
O=Path(sys.argv[1]);E=Path(sys.argv[2]);E.mkdir(parents=True,exist_ok=True);r=next(x for x in csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t') if x['filename']=='thermal-generic-adc.ko');a=kpp.KO(R/r['stock_paths']);b=kpp.KO(O/'thermal-generic-adc.stripped');an,ad,al=normalized(a);bn,bd,bl=normalized(b);assert len(a.b)==len(b.b) and (ad,al)==(bd,bl)
sec=a.sec('.BTF');bs=b.sec('.BTF');assert sec==bs;diff=[i for i,(x,y) in enumerate(zip(a.b,b.b)) if x!=y];btfdiff=[i-sec['off'] for i in diff if sec['off']<=i<sec['off']+sec['size']];assert btfdiff
assert all(ad<=i<ad+al or sec['off']<=i<sec['off']+sec['size'] for i in diff),'Additional unexplained residue'
assert kpp.versions(a)==kpp.versions(b) and kpp.exports(a)==kpp.exports(b)
sections=[];functions=[];data=[];rel=[]
for s in a.secs[1:]:
 t=b.sec(s['n']);assert t==s;sections.append([s['n'],s['type'],s['size'],s['off'],hashlib.sha256(a.data(s['n'])).hexdigest(),hashlib.sha256(b.data(s['n'])).hexdigest(),'BUILD_ID_ONLY' if s['n']=='.note.gnu.build-id' else 'UNRESOLVED_BTF' if s['n']=='.BTF' else 'EXACT'])
 if s['type']==4:
  aa=list(a.rela_entries(s));bb=list(b.rela_entries(t));assert aa==bb
  for o,i,x in aa:
   assert a.sym_name(i>>32)==b.sym_name(i>>32);rel.append([s['n'],o,i&0xffffffff,a.sym_name(i>>32),x,'RAW_AND_SEMANTIC_EXACT'])
for typ,axis in [(2,functions),(1,data)]:
 aa=[y for y in a.syms if y['info']&15==typ and 0<y['shndx']<len(a.secs)];bb=[y for y in b.syms if y['info']&15==typ and 0<y['shndx']<len(b.secs)];assert aa==bb
 for y in aa:
  s=a.secs[y['shndx']];x=b'' if s['type']==8 else a.b[s['off']+y['val']:s['off']+y['val']+y['size']];z=b'' if s['type']==8 else b.b[s['off']+y['val']:s['off']+y['val']+y['size']];assert x==z;axis.append([y['n'],s['n'],y['val'],y['size'],hashlib.sha256(x).hexdigest(),'EXACT'])
for name,headers,rs in [('functions',['name','section','offset','size','sha256','result'],functions),('data',['name','section','offset','size','sha256','result'],data),('sections',['section','type','size','offset','stock_sha256','source_sha256','result'],sections),('relocations',['section','offset','type','target','addend','result'],rel)]:
 with (E/(name+'-parity.tsv')).open('w') as f:w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(headers);w.writerows(rs)
(E/'stock.BTF.bin').write_bytes(a.data('.BTF'));(E/'source.BTF.bin').write_bytes(b.data('.BTF'))
j={'module_id':r['module_id'],'module':'thermal-generic-adc','final_class':'C','source_revision':r['public_source_commit'],'stock_sha256':hashlib.sha256(a.b).hexdigest(),'source_stripped_sha256':hashlib.sha256(b.b).hexdigest(),'bytes':len(a.b),'functions':len(functions),'data':len(data),'relocations':len(rel),'imports':len(kpp.versions(a)[0]),'code_data_abi_raw_semantic_relocations_metadata_layout_exact':True,'unresolved':1,'blocker':'Public CI12901745 BTF base has different type/string reference numbering from stock OEM-base split BTF; complete metadata/source-base parity is unproved','raw_difference_offsets':diff,'btf_section_offset':sec['off'],'btf_section_bytes':sec['size'],'btf_differing_offsets':btfdiff,'btf_bytes_different':len(btfdiff),'GNU_descriptor_allowed_range':[ad,al],'normalizations_applied_for_acceptance':'GNU20 descriptor only; full normalized ELF still fails','next_experiment':'Locate authentic public/source-reproduced OEM g945dff7bc1bf BTF base or declaration/tool lineage; compare split BTF referenced type/string graphs and regenerate with pinned pahole. No stock BTF transplantation, no CRC/metadata patch and no firmware blame.'}
(E/'incomplete-acceptance.json').write_text(json.dumps(j,indent=2)+'\n');print('Native ADC full source C:',len(functions),'functions',len(data),'objects',len(rel),'relocations exact;',len(btfdiff),'BTF bytes unresolved')
