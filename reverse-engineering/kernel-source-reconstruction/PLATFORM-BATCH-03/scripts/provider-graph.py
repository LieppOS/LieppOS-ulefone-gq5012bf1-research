#!/usr/bin/env python3
"""All1434 imports and every owned export:real source ABI and explicit runtime uncertainty."""
from pathlib import Path
import csv,json,sys,struct
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=Path('/home/armol/kernel-work/platform-batch-03-cleancheck');N=C/'recipes/android_kernel_modules_secure_diagnostics_ulefone_gq5012bf1';sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp
E=P/'evidence';rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));meta=json.loads((R/'reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json').read_text());wit=json.loads((C/'ws/out/F0-B1/provider/provider-witnesses.json').read_text());edges=list(csv.DictReader((P/'DEPENDENCIES.tsv').open(),delimiter='\t'));out=[]
def namespace(k,s):
 v=next((v for v in k.syms if v['n']=='__kstrtabns_'+s and 0<v['shndx']<len(k.secs)),None)
 assert v,('missing namespace string symbol',s)
 return k.b[k.secs[v['shndx']]['off']+v['val']:].split(b'\0')[0].decode()
for e in edges:
 s=e['symbol'];pid=e['provider_module_ids'];v=wit.get(s,[]);core=pid=='GKI_CORE';assert core or (v and all(not x['errors'] for x in v))
 out.append({'axis':'IMPORT','consumer_id':e['consumer_module_id'],'symbol':s,'evidence_supported_provider':pid,'required_crc':e['required_crc'],'source_crc':e['required_crc'] if core else v[0]['crc'],'export_licence':e['export_type'],'source_namespace':'OFFICIAL_GKI_SYMVERS' if core else v[0]['namespace'],'stock_kcfi_prefix_word':'UNKNOWN_CORE_PROVIDER_WORD' if core else v[0]['stock_kcfi_prefix_word'],'source_kcfi_prefix_word':'UNKNOWN_CORE_PROVIDER_WORD' if core else v[0]['source_kcfi_prefix_word'],'source_revision':'6b18f0b574ab3267615ae6ce642d5a7c3c21ac09' if core else v[0]['source_revision'],'source_definition':'OFFICIAL_GKI12901745_SHA_VERIFIED_SYMVERS_NOT_FRESH_KERNEL_BUILD' if core else ';'.join(x['object'] for x in v),'runtime_provider':'UNKNOWN;stock CRC resolution does not prove actual runtime provider','load_order_reference':'evidence/hardware/LOAD-LIST-EVIDENCE.tsv','status':'CORE_ABI_VERIFIED_STOCK_CONSUMER_ELF_EXACT' if core else 'SOURCE_CRC_LICENCE_NAMESPACE_PREFIX_EXACT_PROVIDER_WHOLE_MODULE_NOT_INFERRED'})
for r in rows:
 m=r['filename'].removesuffix('.ko');a=kpp.KO(R/r['stock_paths'].split(';')[0]);b=kpp.KO(C/'ws/out/F0-B1'/r['filename'].replace('.ko','.stripped'))
 for y in a.syms:
  if not y['n'].startswith('__crc_') or not 0<y['shndx']<len(a.secs):continue
  sec=a.secs[y['shndx']]
  if 'kcrctab' not in sec['n']:continue
  s=y['n'][6:];crc=struct.unpack_from('<I',a.b,sec['off']+y['val'])[0];z=next(z for z in b.syms if z['n']==y['n']);newcrc=struct.unpack_from('<I',b.b,b.secs[z['shndx']]['off']+z['val'])[0];assert crc==newcrc;fn=next(z for z in a.syms if z['n']==s and 0<z['shndx']<len(a.secs));bn=next(z for z in b.syms if z['n']==s and 0<z['shndx']<len(b.secs));word=newword='EXPORTED_DATA_NOT_FUNCTION'
  if fn['info']&15==2:
   word=hex(struct.unpack_from('<I',a.b,a.secs[fn['shndx']]['off']+fn['val']-4)[0]);newword=hex(struct.unpack_from('<I',b.b,b.secs[bn['shndx']]['off']+bn['val']-4)[0]);assert word==newword
  ns=namespace(a,s);assert ns==namespace(b,s)
  out.append({'axis':'EXPORT','consumer_id':'DEPENDENCY_CONSUMERS_IN_CANONICAL_GRAPH','symbol':s,'evidence_supported_provider':r['module_id'],'required_crc':f'0x{crc:08x}','source_crc':f'0x{newcrc:08x}','export_licence':'EXPORT_SYMBOL_GPL' if '_gpl' in sec['n'] else 'EXPORT_SYMBOL','source_namespace':ns,'stock_kcfi_prefix_word':word,'source_kcfi_prefix_word':newword,'source_revision':r['public_source_commit']+' plus full preserved patches at owned source commit','source_definition':r['candidate_directory']+'/'+m+'.o (composites in pinned Kbuild)','runtime_provider':'SOURCE_CERTIFIED_NOT_RUNTIME_COMMUNICATION_PROOF','load_order_reference':'evidence/hardware/LOAD-LIST-EVIDENCE.tsv','status':'FULL_OWNED_STOCK_ELF_EXPORT_EXACT'})
with (E/'PROVIDER-GRAPH.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(out)
print('Graph imports',len(edges),'owned exports',len(out)-len(edges),'noncore source boundaries',len(wit))
