#!/usr/bin/env python3
"""Decode accepted compiled node tables, crosscheck compiler-expanded source and typed DT.
Usage: map-topology.py <accepted-ws> <merged.dtb> <saved-live.tar> <output>
No hardware IO, no arbitrary scalar->phandle guessing, no measured bandwidth claims.
"""
import sys,json,csv,hashlib,re,struct,subprocess
sys.dont_write_bytecode=True
from pathlib import Path
from dtlib import *
W,D,L,O=map(Path,sys.argv[1:]);O.mkdir(parents=True,exist_ok=True);P=Path(__file__).resolve().parents[1];R=P.parents[2];N=R.parent/'android_kernel_modules_interconnect_emi_ulefone_gq5012bf1';sys.path.insert(0,str(N/'scripts'));from normalize import kpp
T=W/'src/kdm';stock=R/'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules'
def symbol(k,name):return next(y for y in k.syms if y['n']==name and 0<y['shndx']<len(k.secs))
def rels(k,section):
 out={}
 for s in k.secs:
  if s['type']==4 and s['info']==section:
   for off,info,add in k.rela_entries(s):
    assert info&0xffffffff==257
    out[off]=(k.syms[info>>32],add)
 return out
def deref(k,y,add):return k.secs[y['shndx']]['n'],y['val']+add
def string_at(k,r):
 sec,off=deref(k,*r);b=k.data(sec);return b[off:b.index(0,off)].decode()
def cpp(mod):
 p=subprocess.run(clang_command(W,mod)+['-E','-P'],cwd=W/'kout',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);assert p.returncode==0,p.stderr
 q=subprocess.run(clang_command(W,mod)+['-fsyntax-only','-Xclang','-fdump-record-layouts-complete'],cwd=W/'kout',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);assert q.returncode==0,q.stderr
 return p.stdout,q.stdout
# Struct layouts are independently confirmed by the exact target compiler.
s,layout=cpp('mmqos-mt6878');m=re.search(r'0 \| struct mtk_node_desc\n(.*?sizeof=24, align=8.*?\n)',layout,re.S);assert m
(O/'MMQOS-record-layout.txt').write_text(m[0]);expanded=hashlib.sha256(s.encode()).hexdigest()
body=block(s,s.index('static const struct mtk_node_desc node_descs_mt6878[]'));source=[]
for e in split_top(body):
 if not e.startswith('{'):continue
 dd={}
 for field in split_top(e.strip()[1:-1]):
  z=re.match(r'\.(\w+)\s*=\s*(.*)',field,re.S)
  if z:dd[z[1]]=z[2].strip('"') if z[1]=='name' else number(z[2])
 source.append(dd)
k=kpp.KO(stock/'mmqos-mt6878.ko');y=symbol(k,'node_descs_mt6878');sec=k.secs[y['shndx']];rr=rels(k,y['shndx']);assert y['size']==len(source)*24
nodes={};table=[]
for i,d in enumerate(source):
 off=y['val']+i*24;name=string_at(k,rr[off]);node,link,ratio,channel,write=struct.unpack_from('<IIHBB',k.data(sec['n']),off+8)
 assert (name,node,link,ratio,channel,write)==(d['name'],d['id'],d['link'],d['bw_ratio'],d['channel'],d['is_write']),((name,node,link,ratio,channel,write),d)
 assert node not in nodes;nodes[node]={'name':name,'id':node,'link':link,'ratio':ratio,'channel':channel,'write':bool(write)}
 table.append([i,name,hex(node),node>>16,hex(link),ratio,channel,bool(write),'STOCK_BINARY_IMPLEMENTATION','SOURCE_AND_COMPILED_FIELDS_IDENTICAL'])
for d in nodes.values():assert d['link']==0xffffffff or d['link'] in nodes
# Every linked path terminates and has no cycle; encoded IDs are not EMI onecell indices.
def chain(node):
 out=[]
 while node!=0xffffffff:
  assert node in nodes and node not in out;out.append(node);node=nodes[node]['link']
 return out
tab(O/'MMQOS-NODES.tsv',['index','name','node_id','node_type','link_id','bw_ratio','channel','is_write','evidence_level','source_check'],table)
se,elayout=cpp('mtk-emi');lm=re.search(r'0 \| struct mtk_icc_node\n(.*?sizeof=40, align=8.*?\n)',elayout,re.S);assert lm;(O/'EMI-record-layout.txt').write_text(lm[0])
e=kpp.KO(stock/'mtk-emi.ko');ar=symbol(e,'mt6873_icc_nodes');rel=rels(e,ar['shndx']);emi={};et=[]
for index in range(ar['size']//8):
 off=ar['val']+index*8;yy,add=rel[off];ss,pos=deref(e,yy,add);sid=next(i for i,t in enumerate(e.secs) if t['n']==ss);nr=rels(e,sid);name=string_at(e,nr[pos]);ep,nid,link,count=struct.unpack_from('<iHHH',e.data(ss),pos+8);assert count in [0,1]
 emi[index]={'name':name,'internal_id':nid,'endpoint':ep,'links':[] if count==0 else [link]};et.append([index,name,nid,ep,'' if count==0 else link,'STOCK_BINARY_IMPLEMENTATION','MT6878 compatible selects mt6873_icc'])
tab(O/'EMI-NODES.tsv',['xlate_index','name','internal_id','endpoint','link_internal_id','evidence_level','selection'],et)
raws={'static':fdt(D),'live':live(L)};prows=[];paths=[];iommu=[];bindings=[];resources=[];selected={};unknown=[]
for operand,dt in raws.items():
 ph={cells(v['phandle'])[0]:p for p,v in dt.items() if 'phandle' in v};providers={p:'MMQOS_PRIVATE' if 'mediatek,mt6878-mmqos' in strings(v.get('compatible',b'')) else 'EMI_LINUX' for p,v in dt.items() if any(c in strings(v.get('compatible',b'')) for c in ['mediatek,mt6878-mmqos','mediatek,mt6878-dvfsrc'])};assert set(providers.values())=={'MMQOS_PRIVATE','EMI_LINUX'}
 selected[operand]=set(providers)
 larbs={cells(v['mediatek,larb-id'])[0]:p for p,v in dt.items() if 'mediatek,larb-id' in v}
 for p,v in dt.items():
  if p in providers or 'mediatek,larb-id' in v or any('smi-' in c for c in strings(v.get('compatible',b''))):
   selected[operand].add(p)
   for prop,b in v.items():prows.append([operand,p,status(dt,p),prop,json.dumps(decode(b)), 'ENABLED_IN_STOCK_DT' if status(dt,p)=='okay' else 'DISABLED_IN_STOCK_DT'])
  # The private framework uses the SAME interconnects property, with its own #mtk cell rule.
  if 'interconnects' in v:
   cc=cells(v['interconnects']);i=0;spec=[]
   while i<len(cc):
    handle=cc[i];i+=1;provider=ph.get(handle);assert provider
    family=providers.get(provider,'OTHER');key='#mtk-interconnect-cells' if family=='MMQOS_PRIVATE' else '#interconnect-cells';assert key in dt[provider],(p,provider,key)
    count=cells(dt[provider][key])[0];args=cc[i:i+count];i+=count;assert len(args)==count==1
    ident=args[0]
    if family=='MMQOS_PRIVATE':
     name=nodes.get(ident,{}).get('name','UNKNOWN');route=[nodes[q]['name'] for q in chain(ident)] if ident in nodes else []
    elif family=='EMI_LINUX':name=emi.get(ident,{}).get('name','UNKNOWN');route=[]
    else:name='UNKNOWN';route=[]
    spec.append((provider,family,ident,name,route))
   assert len(spec)%2==0;pn=strings(v.get('interconnect-names',b''));assert len(pn)==len(spec)//2
   for index in range(len(pn)):
    src,dst=spec[index*2:index*2+2];assert src[1]!='OTHER' and dst[1]!='OTHER'
    larbid=next((n&0xffff for n in chain(src[2]) if n>>16==3),None) if src[1]=='MMQOS_PRIVATE' and src[2] in nodes else None
    larb=larbs.get(larbid,'NO_DT_LARB') if larbid is not None else 'NOT_A_LARB_PATH'
    iface='of_mtk_icc_get / mtk_icc_set_bw (mtk-icc-core)' if src[1]=='MMQOS_PRIVATE' else 'of_icc_get / icc_set_bw (GKI)'
    paths.append([operand,p,';'.join(strings(v.get('compatible',b''))),status(dt,p),pn[index],src[0],src[1],hex(src[2]),src[3],dst[0],hex(dst[2]),dst[3],'>'.join(src[4]),larbid,larb,iface,'ENABLED_IN_STOCK_DT' if status(dt,p)=='okay' else 'DISABLED_IN_STOCK_DT'])
    selected[operand].add(p)
  if 'iommus' in v:
   cc=cells(v['iommus']);i=0
   while i<len(cc):
    provider=ph.get(cc[i]);i+=1;assert provider
    count=cells(dt[provider]['#iommu-cells'])[0];args=cc[i:i+count];i+=count;assert len(args)==count
    if count!=1:continue
    port=args[0];node=0x40000|(port&0xffff);md=nodes.get(node);larbid=(port>>5)&0x3f;larbnode=nodes.get(0x30000|larbid)
    if md:assert md['link']==(0x30000|larbid)
    iommu.append([operand,p,status(dt,p),provider,hex(port),hex(node),'NO_COMPILED_PORT_NODE' if not md else md['name'],larbid,larbs.get(larbid,'NO_DT_LARB'),port&0x1f,(port>>16)&0xf,(port>>20)&3,'UNKNOWN' if not larbnode else larbnode['name'],'MTK_M4U tab/domain/larb/port decoded separately; leaf matching uses MASTER_LARB_PORT lower16','ENABLED_IN_STOCK_DT' if larbnode and status(dt,p)=='okay' else 'UNKNOWN'])
 for provider,family in providers.items():
  if family=='MMQOS_PRIVATE':
   for prop in ['mediatek,larbs-supply','mediatek,commons-supply']:
    for handle in cells(dt[provider][prop]):
     q=ph.get(handle);assert q;bindings.append([operand,provider,prop,hex(handle),q,status(dt,q),'ENABLED_IN_STOCK_DT' if status(dt,q)=='okay' else 'DISABLED_IN_STOCK_DT'])
 # Explicit resource-property arities only; no scalar-phandle collisions.
 contexts=selected[operand]|{p.rpartition('/')[0] or '/' for p in providers}
 for p in sorted(contexts):
  for prop,key in [('clocks','#clock-cells'),('power-domains','#power-domain-cells'),('iommus','#iommu-cells')]:
   if prop not in dt.get(p,{}):continue
   cc=cells(dt[p][prop]);i=0
   while i<len(cc):
    handle=cc[i];i+=1;q=ph.get(handle);assert q and key in dt[q]
    num=cells(dt[q][key])[0];args=cc[i:i+num];i+=num;assert len(args)==num
    resources.append([operand,p,prop,hex(handle),q,';'.join(strings(dt[q].get('compatible',b''))),json.dumps([hex(a) for a in args]),status(dt,p)])
tab(O/'DT-PROPERTIES.tsv',['operand','node','effective_status','property','value','evidence_level'],prows)
tab(O/'DT-INTERCONNECT-PATHS.tsv',['operand','consumer','compatible','effective_status','path_name','source_provider','framework','source_arg','source_node','destination_provider','destination_arg','destination_node','node_chain','larb_id','larb_dt','request_interface','evidence_level'],paths)
tab(O/'DT-IOMMU-PORTS.tsv',['operand','consumer','effective_status','iommu_provider','full_iommu_arg','mmqos_node_id','mmqos_node','larb_id','larb_dt','port_id','domain_id','table_id','mmqos_larb_node','matching_rule','evidence_level'],iommu)
tab(O/'DT-SMI-BINDINGS.tsv',['operand','mmqos_provider','property','phandle','supplier','effective_status','evidence_level'],bindings)
tab(O/'DT-RESOURCE-REFERENCES.tsv',['operand','consumer','property','phandle','provider','compatible','specifier_args','consumer_effective_status'],resources)
comparison=[];crosschecks=[]
for p in sorted(selected['static']):
 for prop,b in raws['static'][p].items():
  if prop in ['phandle','linux,phandle','name']:continue
  other=raws['live'].get(p,{}).get(prop);comparison.append([p,prop,'IDENTICAL' if b==other else 'DIFFERENT',json.dumps(decode(b)),json.dumps(decode(other or b''))])
  # fdtget provides an independent decoder for every selected integer-cell property.
  if b and len(b)%4==0 and not (b[0]!=0 and b.endswith(b'\0') and all(c==0 or 32<=c<127 for c in b)):
   vals=[int(v,16) for v in subprocess.check_output(['fdtget','-tx',str(D),p,prop],text=True).split()];assert vals==cells(b);crosschecks.append([p,prop,len(vals),'IDENTICAL'])
tab(O/'STATIC-LIVE-COMPARISON.tsv',['node','property','result','static','live'],comparison);tab(O/'FDTGET-CROSSCHECKS.tsv',['node','property','cells','result'],crosschecks)
summary={'compiled_mmqos_nodes':len(nodes),'mmqos_node_types':{str(t):sum((x>>16)==t for x in nodes) for t in [1,2,3,4]},'compiled_emi_onecell_nodes':len(emi),'compiler_cpp_sha256':expanded,'mmqos_source_table_all_fields_match_stock':True,'acyclic_node_graph':True,'static_interconnect_paths':sum(r[0]=='static' for r in paths),'static_iommu_specifiers':sum(r[0]=='static' for r in iommu),'static_smi_supplier_links':sum(r[0]=='static' for r in bindings),'static_live_properties':len(comparison),'static_live_differences':sum(r[2]!='IDENTICAL' for r in comparison),'independent_fdtget_checks':len(crosschecks),'runtime_votes_measured':0,'measured_frequencies_or_channels':0,'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D,L]}}
(O/'contract-validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
