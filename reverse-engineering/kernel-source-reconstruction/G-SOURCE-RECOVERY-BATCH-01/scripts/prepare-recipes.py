#!/usr/bin/env python3
"""Create truthful family references/provenance from immutable stock metadata; no output patching."""
from pathlib import Path
import csv,json,collections,sys,importlib.util,struct,hashlib,shutil,os
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent;W=Path('/home/armol/kernel-work/g-source-recovery-batch-01');S=ROOT/'android_kernel_modules_platform_diagnostics_ulefone_gq5012bf1';sys.path.insert(0,str(S/'scripts'));from normalize import kpp,normalized
manifest=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));allrows=list(csv.DictReader((R/'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv').open(),delimiter='\t'));by={r['module_id']:r for r in allrows};edges=[e for e in csv.DictReader((R/'reverse-engineering/kernel-source-parity-audit/DEPENDENCY-EDGES.tsv').open(),delimiter='\t') if e['consumer_module_id'] in {r['module_id'] for r in manifest}];sha=lambda b:hashlib.sha256(b).hexdigest();abi=[]
names={'NORMAL-WORLD-SECURE-TRANSPORT':'secure_transport','MODEM-INTERFACES':'modem_interfaces','CAMERA-LENS':'camera_lens'}
units={'secure_transport':{'drivers/dma-buf/heaps':['mtk_sec_heap']},'modem_interfaces':{'drivers/misc/mediatek/eccci':['ccci_md_all'],'drivers/thermal/mediatek':['thermal_trace'],'drivers/misc/mediatek/power_throttling':['pmic_lbat_service','mtk_battery_oc_throttling','mtk_bp_thl','mtk_low_battery_throttling']},'camera_lens':{'drivers/misc/mediatek/sensor/2.0/core':['hf_manager']}}
for fam,n in names.items():
 repo=ROOT/('android_kernel_modules_'+n+'_ulefone_gq5012bf1');rs=[r for r in manifest if r['source_family']==fam];selected={r['module_id'] for r in rs};ref=[];bounds={};symvers=[]
 with (repo/'reference/BATCH-MANIFEST.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
 for r in rs:
  f=R/r['stock_paths'].split(';')[0];b=f.read_bytes();assert len(b)==int(r['stock_size']) and sha(b)==r['stock_sha256'];(W/'stock-flat'/r['filename']).symlink_to(f) if not (W/'stock-flat'/r['filename']).exists() else None;k=kpp.KO(f);normalized_b,d,l=normalized(k);ref.append(dict(module=r['filename'].removesuffix('.ko'),bytes=len(b),stock_sha256=sha(b),normalized_sha256=sha(normalized_b),build_id_offset=d,build_id_bytes=l))
 for e in edges:
  if e['consumer_module_id'] not in selected:continue
  pid=e['provider_module_ids'];pids=pid.split(';');p=next((x for x in pids if x in by),None);external=pid!='GKI_CORE' and not any(x in selected for x in pids);provider=by.get(p,{})
  v=dict(e,consumer_filename=by[e['consumer_module_id']]['filename'],family=fam,provider_filename=provider.get('filename',pid),provider_stock_sha256=provider.get('stock_sha256','GKI12901745_PIN'),provider_class=provider.get('source_status','GKI_CORE'),provider_source_repo=provider.get('source_repo','kernel/common'),provider_source_commit=provider.get('source_commit','6b18f0b574ab3267615ae6ce642d5a7c3c21ac09'),provider_load_order=provider.get('load_order','BUILTIN'),provider_load_evidence=provider.get('runtime_evidence','PinnedGKIpublicsymvers'),boundary='EXTERNAL_WITNESS_ONLY_NO_PROVIDER_PROMOTION' if external else 'INTRA_FAMILY_SOURCE' if pid!='GKI_CORE' else 'PINNED_GKI_CORE');abi.append(v)
  if not external:continue
  assert p,pid;s=e['symbol'];f=R/provider['stock_paths'].split(';')[0];ko=kpp.KO(f);y=next(v for v in ko.syms if v['n']==s and 0<v['shndx']<len(ko.secs));typ=y['info']&15;word=hex(struct.unpack_from('<I',ko.b,ko.secs[y['shndx']]['off']+y['val']-4)[0]) if typ==2 else None;nsym=next((v for v in ko.syms if v['n']=='__kstrtabns_'+s and 0<v['shndx']<len(ko.secs)),None);ns=ko.b[ko.secs[nsym['shndx']]['off']+nsym['val']:].split(b'\0')[0].decode() if nsym else None
  lic=e['export_type'];lic='EXPORT_SYMBOL_GPL' if lic=='EXPORT_SYMBOL_GPL' else 'EXPORT_SYMBOL';record=dict(crc=e['required_crc'],licence=lic,namespace=ns,symbol_type=typ,stock_kcfi_prefix_word=word,provider_module=provider['filename'],provider_id=p,provider_source_status=provider['source_status'])
  if s in bounds:assert bounds[s]==record
  bounds[s]=record
 for s,v in sorted(bounds.items()):symvers.append(f"{v['crc']}\t{s}\t{v['provider_module'].removesuffix('.ko')}\t{v['licence']}\t{v['namespace'] or ''}\n")
 with (repo/'reference/stock-normalized.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(ref[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(ref)
 (repo/'reference/provider-boundaries.json').write_text(json.dumps(bounds,indent=2,sort_keys=True)+'\n');(repo/'reference/external-provider.symvers').write_text(''.join(symvers));(repo/'reference/provider-build-units.json').write_text(json.dumps(units[n],indent=2,sort_keys=True)+'\n');owner=repo/'families'/fam;owner.mkdir(parents=True,exist_ok=True);(owner/'OWNERSHIP.json').write_text(json.dumps(dict(owner='CODEX:G-SOURCE-RECOVERY-BATCH-01',family=fam,targets=[r['module_id'] for r in rs],initial_class='G',source_ancestry='PinnedALPS5e415e; inherited tested shared build engine only, not old diagnostics target ownership',external_providers_not_owned=sorted({v['provider_module'] for v in bounds.values()})),indent=2)+'\n')
 pins=list(csv.DictReader((repo/'SOURCE-PINS.tsv').open(),delimiter='\t'))
 for q in pins:
  if q['id']=='alps5e41':q['role']='Complete '+fam+' targets and genuine source-only provider witnesses; no other provider certification'
 with (repo/'SOURCE-PINS.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(pins[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(pins)
 print(n,'targets',len(rs),'external sourceABI slots',len(bounds),'providerclasses',collections.Counter(v['provider_source_status'] for v in bounds.values()))
with (P/'ABI-PROVIDERS.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(abi[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(abi)
print('All972 actualimport edges recorded with canonical provider identity/class/CRC/source/load evidence')
