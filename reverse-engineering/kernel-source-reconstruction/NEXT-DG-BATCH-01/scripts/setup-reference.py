#!/usr/bin/env python3
"""Expected stock hashes/type boundaries only; never produces compiled metadata bytes."""
from pathlib import Path
import csv,collections,json,sys,struct,hashlib,os,subprocess,importlib.util
sys.dont_write_bytecode=True;os.environ.update(GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent
manifest=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));audit=list(csv.DictReader((R/'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').open(),delimiter='\t'));by={r['module_id']:r for r in audit};edges=list(csv.DictReader((R/'reverse-engineering/kernel-source-parity-audit/DEPENDENCY-EDGES.tsv').open(),delimiter='\t'))
repos={'MTK-SYSTEM-DIAGNOSTICS':ROOT/'android_kernel_modules_platform_diagnostics_ulefone_gq5012bf1','MET-INSTRUMENTATION':ROOT/'android_kernel_modules_met_instrumentation_ulefone_gq5012bf1'}
sp=importlib.util.spec_from_file_location('norm',repos['MTK-SYSTEM-DIAGNOSTICS']/'scripts/normalize.py');norm=importlib.util.module_from_spec(sp);sp.loader.exec_module(norm);kpp=norm.kpp
SHA=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,rows):
 with p.open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
abi=[]
for family,repo in repos.items():
 rows=[dict(r,build_domain='KDM' if family=='MTK-SYSTEM-DIAGNOSTICS' else 'NKM') for r in manifest if r['source_family']==family]
 if family=='MET-INSTRUMENTATION':
  for r in rows:
   n=r['filename'].removesuffix('.ko');r['candidate_directory']='met_drv_v3' if n=='met' else 'met_drv_v3/met_api/'+n
 dump(repo/'reference/BATCH-MANIFEST.tsv',rows)
 normalized=[];required={};units=collections.defaultdict(set);external=[];ids={r['module_id'] for r in rows}
 for r in rows:
  stock=R/r['stock_paths'].split(';')[0];ko=kpp.KO(stock);b,off,n=norm.normalized(ko);normalized.append(dict(module=r['filename'].removesuffix('.ko'),bytes=len(ko.b),stock_sha256=SHA(ko.b),normalized_sha256=SHA(b),gnu20_range=hex(off)+'+20'))
 for edge in edges:
  if edge['consumer_module_id'] not in ids:continue
  providers=edge['provider_module_ids']
  if providers=='GKI_CORE':
   abi.append(dict(consumer=edge['consumer_module_id'],symbol=edge['symbol'],required_crc=edge['required_crc'],provider='GKI_CORE',partition='CORE_KERNEL',source_status='PINNED_COMMON6b18f0_AND_PUBLIC_GKI12901745',export_type=edge['export_type'],namespace='CORE_SYMVERS',witness='pinned public GKI core symvers+common sources; not separately source-certifying whole vmlinux',claimed_provider_certification='NONE'));continue
  choices=[x for x in providers.split(';') if x in by];assert len(choices)==1,(edge,choices)
  provider=by[choices[0]];name=edge['symbol'];ko=kpp.KO(R/provider['stock_paths'].split(';')[0]);symbol=next(y for y in ko.syms if y['n']==name and 0<y['shndx']<len(ko.secs));typ=symbol['info']&15;word=None
  if typ==2:assert symbol['val']>=4;word=hex(struct.unpack_from('<I',ko.b,ko.secs[symbol['shndx']]['off']+symbol['val']-4)[0])
  ns=next(y for y in ko.syms if y['n']=='__kstrtabns_'+name);namespace=ko.b[ko.secs[ns['shndx']]['off']+ns['val']:].split(b'\0')[0].decode()
  crc=next(y for y in ko.syms if y['n']=='__crc_'+name);sec=ko.secs[crc['shndx']];val=struct.unpack_from('<I',ko.b,sec['off']+crc['val'])[0];assert val==int(edge['required_crc'],16)
  licence='EXPORT_SYMBOL_GPL' if '_gpl' in sec['n'] else 'EXPORT_SYMBOL';assert licence==edge['export_type']
  abi.append(dict(consumer=edge['consumer_module_id'],symbol=name,required_crc=edge['required_crc'],provider=provider['module_id'],partition=provider['partitions'],source_status=provider['source_status'],export_type=licence,namespace=namespace,witness='OWNED_TARGET_NATURAL_SYMVERS' if provider['module_id'] in ids else 'SOURCE_BUILT_EXPORT_OBJECT_REQUIRED',claimed_provider_certification='NONE'))
  if provider['module_id'] in ids:continue
  entry=dict(crc=f'0x{val:08x}',licence=licence,namespace=namespace,provider_module=provider['filename'].removesuffix('.ko'),provider_identity=provider['module_id'],symbol_type=typ,stock_kcfi_prefix_word=word)
  if name in required:assert required[name]==entry
  required[name]=entry
  path=provider['candidate_path']
  if '/device_modules/' in path:d=path.split('/device_modules/')[1]
  elif '/kernel_modules/' in path:d=path.split('/kernel_modules/')[1]
  else:raise RuntimeError('Provider source route must be recovered explicitly: '+str(provider))
  units[d].add(provider['filename'].removesuffix('.ko'))
 for name,e in sorted(required.items()):external.append(f"{e['crc']}\t{name}\t{e['provider_module']}\t{e['licence']}\t{e['namespace']}\n")
 dump(repo/'reference/stock-normalized.tsv',normalized);(repo/'reference/external-provider.symvers').write_text(''.join(external));(repo/'reference/provider-boundaries.json').write_text(json.dumps(required,indent=2,sort_keys=True)+'\n');(repo/'reference/provider-build-units.json').write_text(json.dumps({d:sorted(ms) for d,ms in units.items()},indent=2,sort_keys=True)+'\n')
 (repo/'families'/family).mkdir(exist_ok=True);(repo/'families'/family/'OWNERSHIP.json').write_text(json.dumps(dict(family=family,targets=[r['module_id'] for r in rows],claim='codex/next-dg-source-batch',manifest_sha256=SHA((P/'BATCH-MANIFEST.tsv').read_bytes()),provider_only={d:sorted(ms) for d,ms in units.items()}),indent=2)+'\n')
 print(family,'targets',len(rows),'external export slots',len(required),'units',dict(units))
dump(P/'ABI-PROVIDERS.tsv',abi)
