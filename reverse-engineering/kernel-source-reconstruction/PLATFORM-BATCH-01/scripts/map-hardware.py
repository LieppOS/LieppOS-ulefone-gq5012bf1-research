#!/usr/bin/env python3
"""Saved live DT configuration + actual stock alias capability, never current phone I/O."""
import sys,csv,hashlib,json,fnmatch
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];sys.dont_write_bytecode=True
sys.path.insert(0,str(R/'reverse-engineering/kernel-source-reconstruction/INTERCONNECT-EMI/scripts'))
from dtlib import live,status,strings,cells,decode,tab
cap=R/'workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar';nodes=live(cap);ph={cells(v['phandle'])[0]:p for p,v in nodes.items() if 'phandle' in v};meta=json.loads((R/'reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json').read_text());rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));O=P/'evidence/hardware';O.mkdir(parents=True,exist_ok=True)
matched=[];props=[];resources=[];family_nodes={};aliases=[]
for r in rows:
 a=meta[r['module_id']]['modinfo'].get('alias',[]);of=[s.split('C',1)[1].removesuffix('C*') for s in a if s.startswith('of:') and 'C' in s]
 for alias in a:aliases.append([r['module_id'],alias,'BINARY_CAPABILITY_ONLY'])
 for p,v in nodes.items():
  comp=strings(v.get('compatible',b''))
  if not any(fnmatch.fnmatchcase(c,pattern) for c in comp for pattern in of):continue
  matched.append([r['module_id'],p,';'.join(comp),status(nodes,p),'SAVED_DT_CONFIG_ALIAS_MATCH_NOT_PROBE_PROOF']);family_nodes[p]=v
  for k,b in v.items():
   if k not in ['name','phandle']:props.append([r['filename'],p,k,json.dumps(decode(b),separators=(',',':')),hashlib.sha256(b).hexdigest()])
  for prop,ncells in [('clocks','#clock-cells'),('power-domains','#power-domain-cells'),('mboxes','#mbox-cells'),('iommus','#iommu-cells'),('dmas','#dma-cells')]:
   if prop not in v:continue
   cs=cells(v[prop]);i=0;slot=0
   while i<len(cs):
    h=cs[i];i+=1;q=ph.get(h)
    if not q:resources.append([r['filename'],p,prop,slot,hex(h),'NULL_OR_UNRESOLVED','UNKNOWN',json.dumps(cs[i:])]);break
    assert ncells in nodes[q],(p,prop,q,ncells);n=cells(nodes[q][ncells])[0];assert i+n<=len(cs)
    resources.append([r['filename'],p,prop,slot,hex(h),q,status(nodes,q),json.dumps(cs[i:i+n])]);i+=n;slot+=1
  # interrupt-parent may be inherited; no bare integer is assumed to be a phandle.
  if 'interrupts' in v:
   parent=p
   while parent not in [''] and 'interrupt-parent' not in nodes.get(parent,{}):
    if parent=='/':parent='';break
    parent=parent.rpartition('/')[0] or '/'
   h=cells(nodes[parent]['interrupt-parent'])[0] if parent else None;q=ph.get(h)
   if q and '#interrupt-cells' in nodes[q]:
    n=cells(nodes[q]['#interrupt-cells'])[0];cs=cells(v['interrupts']);assert n>0 and len(cs)%n==0
    for i in range(0,len(cs),n):resources.append([r['filename'],p,'interrupts',i//n,hex(h),q,status(nodes,q),json.dumps(cs[i:i+n])])
tab(O/'DT-ALIAS-MATCHES.tsv',['module_id','node','compatible','effective_status','evidence_level'],matched)
tab(O/'DT-PROPERTIES.tsv',['module','node','property','decoded','sha256'],props)
tab(O/'TYPED-RESOURCES.tsv',['module','client','property','index','provider_phandle','provider_node','provider_status','arguments'],resources)
tab(O/'STOCK-ALIASES.tsv',['module_id','alias','evidence_level'],aliases)
(O/'result.json').write_text(json.dumps({'saved_capture':str(cap.relative_to(R)),'saved_capture_sha256':hashlib.sha256(cap.read_bytes()).hexdigest(),'selected_modules':35,'alias_matches':len(matched),'unique_nodes':len(family_nodes),'properties':len(props),'typed_resources':len(resources),'runtime_binding_or_DMA_success_claimed':False,'live_access_performed':False,'existing_iommu_contract':'../IOMMU/evidence/hardware/contract-validation.json'},indent=2)+'\n')
print('Offline hardware:',len(matched),'alias matches',len(family_nodes),'unique nodes',len(resources),'typed resource entries')
for p in sorted(family_nodes):
 if any(s in p for s in ['gce','scpsys','smi','dvfsrc','uart']):print(p,status(nodes,p),{k:decode(b) for k,b in family_nodes[p].items() if k in ['compatible','reg','interrupts','mbox-names','clock-names','power-domain-names']})
