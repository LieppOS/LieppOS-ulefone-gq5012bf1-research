#!/usr/bin/env python3
"""Derive saved board evidence without inferring runtime from generic source."""
from pathlib import Path
import sys,csv,json,hashlib,fnmatch,re
P=Path(__file__).resolve().parents[1];R=P.parents[2];sys.dont_write_bytecode=True;sys.path.insert(0,str(P.parent/'INTERCONNECT-EMI/scripts'));from dtlib import live,status,strings,cells,decode,tab
cap=R/'workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar';N=live(cap);ph={cells(v['phandle'])[0]:p for p,v in N.items() if 'phandle' in v};meta=json.loads((R/'reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json').read_text());rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));E=P/'evidence/hardware';E.mkdir(parents=True,exist_ok=True);matched=[];props=[];typed=[];aliases=[];configured=[];configured_props=[]
for r in rows:
 aa=meta[r['module_id']]['modinfo'].get('alias',[]);patterns=[s.split('C',1)[1].removesuffix('C*') for s in aa if s.startswith('of:') and 'C' in s]
 for a in aa:aliases.append([r['module_id'],a,'STOCK_BINARY_IMPLEMENTATION'])
 for p,v in N.items():
  comps=strings(v.get('compatible',b''))
  if not any(fnmatch.fnmatchcase(c,pat) for c in comps for pat in patterns):continue
  st=status(N,p);matched.append([r['module_id'],p,';'.join(comps),st,'ENABLED_IN_STOCK_DT' if st=='okay' else 'STOCK_DT_DISABLED_CONFIGURATION'])
  for k,b in v.items():
   if k not in ['name','phandle']:props.append([r['filename'],p,k,json.dumps(decode(b),separators=(',',':')),hashlib.sha256(b).hexdigest()])
  for prop,ncells in [('clocks','#clock-cells'),('power-domains','#power-domain-cells'),('mboxes','#mbox-cells'),('iommus','#iommu-cells'),('dmas','#dma-cells')]:
   if prop not in v:continue
   cs=cells(v[prop]);i=slot=0
   while i<len(cs):
    h=cs[i];i+=1;q=ph.get(h)
    if not q:typed.append([r['filename'],p,prop,slot,hex(h),'NULL_OR_UNRESOLVED','UNKNOWN',json.dumps(cs[i:])]);break
    assert ncells in N[q],(p,prop,q);n=cells(N[q][ncells])[0];assert i+n<=len(cs);typed.append([r['filename'],p,prop,slot,hex(h),q,status(N,q),json.dumps(cs[i:i+n])]);i+=n;slot+=1
  if 'interrupts' in v:
   par=p
   while par and 'interrupt-parent' not in N.get(par,{}):
    if par=='/':par='';break
    par=par.rpartition('/')[0] or '/'
   h=cells(N[par]['interrupt-parent'])[0] if par else None;q=ph.get(h)
   if q and '#interrupt-cells' in N[q]:
    n=cells(N[q]['#interrupt-cells'])[0];cs=cells(v['interrupts']);assert n>0 and len(cs)%n==0
    for i in range(0,len(cs),n):typed.append([r['filename'],p,'interrupts',i//n,hex(h),q,status(N,q),json.dumps(cs[i:i+n])])
# Independently configured nodes, including those whose static match table lacks module aliases.
for p,v in N.items():
 comps=strings(v.get('compatible',b''));tag=p+' '+','.join(comps)
 if not comps or not re.search(r'emi|dramc|smpu|pmif|spmi|sspm|mcupm|mailbox|mbox|tinysys|bp-thl|battery.*thrott|lbat|lvsys',tag,re.I):continue
 for k,b in v.items():
  if k not in ['name','phandle']:configured_props.append([p,k,json.dumps(decode(b),separators=(',',':')),hashlib.sha256(b).hexdigest()])
 configured.append([p,';'.join(comps),status(N,p),json.dumps({k:decode(b) for k,b in v.items() if k in ['reg','interrupts','clocks','clock-names','power-domains','mboxes','memory-region','mediatek,mbox-count','mediatek,send-table','mediatek,recv-table']},separators=(',',':')),'SAVED_CONFIGURATION_NOT_DRIVER_BINDING_OR_FIRMWARE_STARTUP'])
tab(E/'DT-ALIAS-MATCHES.tsv',['module_id','node','compatible','effective_status','evidence_level'],matched);tab(E/'DT-PROPERTIES.tsv',['module','node','property','decoded','sha256'],props);tab(E/'TYPED-RESOURCES.tsv',['module','client','property','index','provider_phandle','provider_node','provider_status','arguments'],typed);tab(E/'STOCK-ALIASES.tsv',['module_id','alias','evidence_level'],aliases);tab(E/'CONFIGURED-PLATFORM-NODES.tsv',['node','compatible','effective_status','configured_resources','evidence_level'],configured)
tab(E/'CONFIGURED-NODE-PROPERTIES.tsv',['node','property','decoded','sha256'],configured_props)
ids={r['module_id'] for r in rows};load=list(csv.DictReader((R/'reverse-engineering/kernel-source-parity-audit/LOAD-LIST-EVIDENCE.tsv').open(),delimiter='\t'));load=[x for x in load if ids&set(x['matching_module_ids'].split(';'))]
if load:tab(E/'LOAD-LIST-EVIDENCE.tsv',list(load[0]),[[x[k] for k in load[0]] for x in load])
original=json.loads((P/'evidence/baseline/selected-original-rows.json').read_text());bound=[{'module_id':x['module_id'],'bound_probe_status':x['bound_probe_status'],'runtime_evidence':x['runtime_evidence'],'evidence_level':'PROVEN_RUNTIME' if x['bound_probe_status']=='RECORDED_DRIVER_MODULE_SYMLINK' else 'UNKNOWN','limit':'saved binding evidence only, no transaction/firmware startup inferred'} for x in original]
(E/'SAVED-RUNTIME-BOUNDARIES.json').write_text(json.dumps(bound,indent=2)+'\n');res={'saved_capture':str(cap.relative_to(R)),'saved_capture_sha256':hashlib.sha256(cap.read_bytes()).hexdigest(),'selected':27,'alias_matches':len(matched),'typed_resources':len(typed),'configured_nodes':len(configured),'load_occurrences':len(load),'live_access':False,'firmware_communication_tested':False};(E/'result.json').write_text(json.dumps(res,indent=2)+'\n');print(res)
for x in configured:
 if any(s in x[1] for s in ['pmif','spmi','sspm','mcupm','emi','dramc']):print(*x[:4])
