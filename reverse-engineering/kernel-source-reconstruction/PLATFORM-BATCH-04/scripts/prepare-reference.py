#!/usr/bin/env python3
"""Read-only stock hashing/ABI references; no stock compiled operands enter builds."""
import csv,sys,json,hashlib,struct,collections,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];N=R.parent/'android_kernel_modules_charging_battery_ulefone_gq5012bf1'
sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp,normalized
rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));ids={r['module_id'] for r in rows};meta=json.loads((R/'reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json').read_text());edges=list(csv.DictReader((P/'DEPENDENCIES.tsv').open(),delimiter='\t'))
refs=[];external={};boundary={}
for r in rows:
 m=r['filename'].removesuffix('.ko');s=R/r['stock_paths'].split(';')[0];ko=kpp.KO(s);nb,off,size=normalized(ko);assert hashlib.sha256(ko.b).hexdigest()==r['stock_sha256']
 refs.append({'module':m,'bytes':len(ko.b),'stock_sha256':r['stock_sha256'],'normalized_sha256':hashlib.sha256(nb).hexdigest(),'build_id_offset':hex(off),'build_id_size':size})
for e in edges:
 provider=e['provider_module_ids'];s=e['symbol']
 if provider=='GKI_CORE':continue
 assert ';' not in provider,'Ambiguous provider must be investigated separately'
 p=meta[provider];pk=kpp.KO(R/p['stock_paths'][0]);v=next(y for y in pk.syms if y['n']==s and 0<y['shndx']<len(pk.secs));sec=pk.secs[v['shndx']];typ=v['info']&15
 licence=e['export_type'];ns=''
 nssec=pk.sec('__ksymtab_strings');nsym=next((y for y in pk.syms if y['n']=='__kstrtabns_'+s),None)
 if nsym:ns=pk.b[pk.secs[nsym['shndx']]['off']+nsym['val']:].split(b'\0')[0].decode()
 cfi=None
 if typ==2:
  assert v['val']>=4;cfi=hex(struct.unpack_from('<I',pk.b,sec['off']+v['val']-4)[0])
 boundary[s]={'provider_id':provider,'provider_module':p['filename'].removesuffix('.ko'),'crc':e['required_crc'],'licence':licence,'namespace':ns,'symbol_type':typ,'stock_kcfi_prefix_word':cfi}
 if provider not in ids:external[s]=f"{e['required_crc']}\t{s}\t{p['filename'].removesuffix('.ko')}\t{licence}\t{ns}\n"
with (N/'reference/stock-normalized.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(refs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(refs)
(N/'reference/external-provider.symvers').write_text(''.join(external[s] for s in sorted(external)))
(N/'reference/provider-boundaries.json').write_text(json.dumps(boundary,indent=2,sort_keys=True)+'\n')
print('Stock golden hashes',len(refs),'external source slots',len(external),'all shared non-core boundaries',len(boundary))
