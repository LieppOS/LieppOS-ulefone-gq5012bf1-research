#!/usr/bin/env python3
"""Offline compiled platform/domain proof and typed static/live IOMMU clients.
Usage: map-topology.py <accepted-ws> <merged.dtb> <saved-live.tar> <output>
No scalar-as-phandle guessing; runtime mappings/groups/IRQ state are never inferred.
"""
import sys,json,csv,hashlib,re,struct,subprocess,shlex,collections,fnmatch
sys.dont_write_bytecode=True
from pathlib import Path
from dtlib import *
W,D,L,O=map(Path,sys.argv[1:]);O.mkdir(parents=True,exist_ok=True);P=Path(__file__).resolve().parents[1];R=P.parents[2];N=R.parent/'android_kernel_modules_iommu_ulefone_gq5012bf1';sys.path.insert(0,str(N/'scripts'));from normalize import kpp
T=W/'src/kdm';cmd=(T/'drivers/iommu/.mtk_iommu.o.cmd').read_text().splitlines()[0].split(':=',1)[1];args=shlex.split(cmd);args[0]=str(W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin/clang');ca=[];i=0
while i<len(args):
 if args[i]=='-o':i+=2;continue
 if args[i]=='-c' or args[i].startswith('-Wp,-MMD,'):i+=1;continue
 ca.append(args[i]);i+=1
q=subprocess.run(ca+['-E','-P'],cwd=W/'kout',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert q.returncode==0,q.stderr;s=q.stdout
q=subprocess.run(ca+['-fsyntax-only','-Xclang','-fdump-record-layouts-complete'],cwd=W/'kout',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert q.returncode==0,q.stderr
layouts={}
for name in ['mtk_iommu_plat_data','mtk_iommu_iova_region','iommu_ops','iommu_domain_ops']:
 m=re.search(r'0 \| struct '+name+r'\n(.*?\[sizeof=(\d+), align=(\d+)\])',q.stdout,re.S);assert m,name
 (O/(name+'-layout.txt')).write_text(m[0]+'\n');fields={}
 for line in m[1].splitlines():
  z=re.match(r'\s*(\d+) \|   (\S.*)',line)
  if z:fields[re.sub(r'\[.*','',z[2].split()[-1]).lstrip('*')]=int(z[1])
 layouts[name]=(int(m[2]),fields)
# Evaluate only bounded compiler-expanded integer initializers with declared enums.
enums={}
for name in ['mtk_iommu_plat','mtk_iommu_type','mm_iommu','apu_iommu','iommu_tab_id','iova_type']:
 b=block(s,s.index('enum '+name+' {'));n=0
 for e in split_top(b):
  k,sep,v=e.partition('=');k=k.strip()
  if sep:n=int(v.strip(),0)
  enums[k]=n;n+=1
def num(v):
 if v.strip() in enums:return enums[v.strip()]
 return number(' '.join(v.split()))
def fields(name):
 b=block(s,s.index(name+' ='));return {z[1]:z[2] for f in split_top(b) if (z:=re.match(r'\.(\w+)\s*=\s*(.*)',f,re.S))}
def symbol(k,name):return next(y for y in k.syms if y['n']==name and 0<y['shndx']<len(k.secs))
def data(k,y):return k.data(k.secs[y['shndx']]['n'])[y['val']:y['val']+y['size']]
def relocation(k,y,delta):
 for se in k.secs:
  if se['type']==4 and se['info']==y['shndx']:
   for off,info,add in k.rela_entries(se):
    if off==y['val']+delta:assert info&0xffffffff==257;z=k.syms[info>>32];return z['shndx'],z['val']+add
 raise AssertionError((y['n'],delta))
k=kpp.KO(R/'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/mtk_iommu.ko');regionrows=[];regions={};plats={};prows=[]
for name in ['mt6878_multi_dom_mm','mt6878_multi_dom_apu']:
 b=block(s,s.index(name+'[]'));ss=[{z[1]:num(z[2]) for f in split_top(e.strip()[1:-1]) if (z:=re.match(r'\.(\w+)\s*=\s*(.*)',f,re.S))} for e in split_top(b) if e.startswith('{')];y=symbol(k,name);bb=data(k,y);size,offs=layouts['mtk_iommu_iova_region'];assert len(bb)==len(ss)*size;rr=[]
 for i,d in enumerate(ss):
  v={'iova_base':struct.unpack_from('<Q',bb,i*size+offs['iova_base'])[0],'size':struct.unpack_from('<Q',bb,i*size+offs['size'])[0],'type':struct.unpack_from('<I',bb,i*size+offs['type'])[0]};assert d==v,(d,v);rr.append(v);regionrows.append([name,i,hex(v['iova_base']),hex(v['size']),hex(v['iova_base']+v['size']-1),['NORMAL','PROTECTED','SECURE'][v['type']],'STOCK_BINARY_IMPLEMENTATION','ALL_SOURCE_FIELDS_IDENTICAL'])
 regions[name]=rr
for name,region,compat in [('mt6878_data_disp','mt6878_multi_dom_mm','mediatek,mt6878-disp-iommu'),('mt6878_data_apu0','mt6878_multi_dom_apu','mediatek,mt6878-apu-iommu0')]:
 f=fields(name);y=symbol(k,name);bb=data(k,y);size,offs=layouts['mtk_iommu_plat_data'];assert y['size']==size;v={}
 for field in ['m4u_plat','flags','inv_sel_reg','iommu_id','iommu_type','tab_id','normal_dom','mau_count']:
  v[field]=struct.unpack_from('<I',bb,offs[field])[0];assert v[field]==num(f[field]),(field,v[field],f[field])
 for implicit in ['tbw_reg_val','reg_val']:
  assert struct.unpack_from('<I',bb,offs[implicit])[0]==0 and implicit not in f
 assert bb[offs['larbid_remap']:offs['mau_count']]==bytes(offs['mau_count']-offs['larbid_remap'])
 hw=symbol(k,f['hw_list'].strip().lstrip('&'));assert relocation(k,y,offs['hw_list'])==(hw['shndx'],hw['val'])
 rr=symbol(k,region);assert relocation(k,y,offs['iova_region'])==(rr['shndx'],rr['val']);v['iova_region_nr']=struct.unpack_from('<I',bb,offs['iova_region_nr'])[0];assert v['iova_region_nr']==len(regions[region]);v['region']=region;plats[compat]=v
 prows.append([name,compat,*[hex(v[x]) for x in ['m4u_plat','flags','inv_sel_reg','iommu_id','iommu_type','tab_id','normal_dom','mau_count']],region,len(regions[region]),'STOCK_BINARY_IMPLEMENTATION','COMPILER_LAYOUT_AND_ALL_FIELDS_IDENTICAL'])
tab(O/'PLATFORM-CONTRACTS.tsv',['object','compatible','platform_enum','flags','invalidate_select_register','iommu_id','iommu_type','table_id','normal_domain','mau_count','region_table','region_count','evidence_level','source_check'],prows);tab(O/'IOVA-REGIONS.tsv',['object','domain_id','base','size','inclusive_end','type','evidence_level','source_check'],regionrows)
# Stock DT and saved read-only live tree, same contracts independently parsed.
raws={'static':fdt(D),'live':live(L)};selected={};providersrows=[];ports=[];refs=[];properties=[];driver_matches=[];stockids=json.load((R/'reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json').open());aliases=[]
for ident,v in stockids.items():
 for a in v['modinfo'].get('alias',[]):
  if a.startswith('of:') and 'C' in a:aliases.append((ident,a.split('C',1)[1].removesuffix('C*')))
def driver(v):
 c=strings(v.get('compatible',b''));return ';'.join(sorted({ident for ident,a in aliases if any(fnmatch.fnmatchcase(x,a) for x in c)})) or 'UNKNOWN_NO_STOCK_OF_ALIAS_MATCH'
def dec(v,key):return json.dumps(decode(v[key])) if key in v else 'ABSENT'
for operand,dt in raws.items():
 ph={cells(v['phandle'])[0]:p for p,v in dt.items() if 'phandle' in v};providers={p:next(c for c in strings(v.get('compatible',b'')) if c in plats) for p,v in dt.items() if any(c in plats for c in strings(v.get('compatible',b'')))};assert len(providers)==2;selected[operand]=set(providers)
 def typed(p,prop,cellkey=None):
  v=dt[p]
  if prop not in v:return []
  cc=cells(v[prop]);i=0;result=[]
  while i<len(cc):
   handle=cc[i];i+=1
   if handle==0 and prop=='mediatek,smi-supply':
    refs.append([operand,p,prop,'NULL_PHANDLE','ABSENT','[]','UNKNOWN','EXPLICIT_ZERO_NOT_A_SUPPLIER']);continue
   assert handle in ph,(p,prop,handle);q=ph[handle];n=cells(dt[q][cellkey])[0] if cellkey else 0;args=cc[i:i+n];i+=n;assert len(args)==n;result.append((q,args));refs.append([operand,p,prop,q,dec(dt[q],'compatible'),json.dumps([hex(x) for x in args]),status(dt,q),'TYPED_PROPERTY']);selected[operand].add(q)
  return result
 for p,compat in providers.items():
  v=dt[p];pd=plats[compat];assert cells(v['#iommu-cells'])==[1];assert cells(v['table_id'])==[pd['tab_id']];providersrows.append([operand,p,compat,status(dt,p),dec(v,'reg'),dec(v,'interrupts'),dec(v,'interrupt-parent'),dec(v,'power-domains'),pd['tab_id'],pd['region'],pd['iova_region_nr'],'mtk_iommu.ko','RECORDED_LOADED; NODE_BINDING_UNKNOWN','ENABLED_IN_STOCK_DT'])
  for prop,cellkey in [('power-domains','#power-domain-cells'),('clocks','#clock-cells'),('resets','#reset-cells'),('mediatek,larbs',None),('mediatek,iommu-banks',None),('mediatek,iommu_banks',None),('mediatek,apu-power',None)]:typed(p,prop,cellkey)
 for p,v in dt.items():
  if 'iommus' not in v:continue
  specs=typed(p,'iommus','#iommu-cells');selected[operand].add(p)
  typed(p,'power-domains','#power-domain-cells')
  for idx,(q,args) in enumerate(specs):
   assert q in providers and len(args)==1;arg=args[0];tabid=(arg>>20)&3;dom=(arg>>16)&15;larb=(arg>>5)&63;port=arg&31;pd=plats[providers[q]];assert tabid==pd['tab_id'] and dom<pd['iova_region_nr'];rgn=regions[pd['region']][dom]
   ports.append([operand,p,';'.join(strings(v.get('compatible',b''))),status(dt,p),idx,q,hex(arg),tabid,dom,larb,port,pd['region'],hex(rgn['iova_base']),hex(rgn['size']),['NORMAL','PROTECTED','SECURE'][rgn['type']],dec(v,'reg'),dec(v,'interrupts'),dec(v,'power-domains'),driver(v),'NODE_BINDING_UNKNOWN; ACTIVE_DMA_UNKNOWN','ENABLED_IN_STOCK_DT' if status(dt,p)=='okay' else 'DISABLED_IN_STOCK_DT'])
 # recursively follow only explicit SMI supplier edges, not register/IRQ integers
 todo=list(selected[operand]);seen=set()
 while todo:
  p=todo.pop()
  if p in seen:continue
  seen.add(p)
  for q,_ in typed(p,'mediatek,smi-supply'):todo.append(q)
 for p in sorted(selected[operand]):
  for prop,b in dt[p].items():properties.append([operand,p,status(dt,p),prop,json.dumps(decode(b))])
  driver_matches.append([operand,p,driver(dt[p]),'STOCK_MODULE_ALIAS_CANDIDATE_NOT_BINDING'])
tab(O/'DT-IOMMU-CONTROLLERS.tsv',['operand','node','compatible','status','register_cells','interrupt_cells','interrupt_parent','power_domain_cells','table_id','region_table','domain_count','driver','runtime_evidence','evidence_level'],providersrows)
tab(O/'DT-IOMMU-PORTS.tsv',['operand','client','compatible','status','specifier_index','controller','full_port_id','table','domain','larb','port','region_table','aperture_base','aperture_size','region_type','client_reg','client_interrupts','client_power_domains','stock_driver_alias_candidates','runtime_evidence','evidence_level'],ports)
tab(O/'DT-RESOURCE-REFERENCES.tsv',['operand','consumer','property','supplier','compatible','arguments','status','evidence_level'],refs);tab(O/'DT-PROPERTIES.tsv',['operand','node','status','property','value'],properties);tab(O/'DRIVER-ALIAS-CANDIDATES.tsv',['operand','node','stock_module_id_candidates','evidence'],driver_matches)
assert selected['static']==selected['live'];comparisons=[];fchecks=[]
for p in sorted(selected['static']):
 # Linux adds the descriptive `name` property while unflattening; it is not a
 # hardware contract property and absent from this static FDT. Do not discard any
 # differing register, specifier, status or other shared property.
 a={k:v for k,v in raws['static'][p].items() if k!='name'};b_live={k:v for k,v in raws['live'][p].items() if k!='name'}
 assert all(b_live.get(prop)==b for prop,b in a.items()),p
 for prop,b in b_live.items():
  if prop not in a:comparisons.append([p,prop,hashlib.sha256(b).hexdigest(),'LIVE_ONLY_PROPERTY_NOT_A_STATIC_ROUTE_PROOF'])
 for prop,b in a.items():
  comparisons.append([p,prop,hashlib.sha256(b).hexdigest(),'BYTE_IDENTICAL'])
  out=subprocess.check_output(['fdtget','-t','bx',str(D),p,prop],text=True).split();assert bytes(int(x,16) for x in out)==b,(p,prop);fchecks.append([p,prop,'BYTE_IDENTICAL'])
tab(O/'STATIC-LIVE-COMPARISON.tsv',['node','property','sha256','result'],comparisons);tab(O/'FDTGET-CROSSCHECKS.tsv',['node','property','result'],fchecks)
# Reuse accepted interconnect evidence; do not rebuild or modify completed components.
I=R/'reverse-engineering/kernel-source-reconstruction/INTERCONNECT-EMI/evidence/hardware';old=list(csv.DictReader((I/'DT-IOMMU-PORTS.tsv').open(),delimiter='\t'));new=[x for x in ports if x[0]=='static'];assert len(new)==len([r for r in old if r['operand']=='static'])==133
for row in new:assert any(r['consumer']==row[1] and r['iommu_provider']==row[5] and int(r['full_iommu_arg'],16)==int(row[6],16) for r in old if r['operand']=='static')
join=[]
for r in old:
 if r['operand']!='static':continue
 m=next(x for x in new if x[1]==r['consumer'] and x[5]==r['iommu_provider'] and x[6]==r['full_iommu_arg']);join.append([r['consumer'],r['full_iommu_arg'],r['iommu_provider'],m[8],r['mmqos_node_id'],r['mmqos_node'],r['larb_dt'],'TRANSLATION_AND_VOTE_IDS_DECODED_SEPARATELY','NO_ACTIVE_DMA_OR_VOTE_PROOF'])
tab(O/'SMI-MMQOS-JOIN.tsv',['client','iommu_arg','controller','domain','mmqos_node_id','mmqos_node','smi_larb','contract','runtime_limit'],join)
result={'controllers':2,'static_specifiers':len(new),'static_clients':len({r[1] for r in new}),'domain_usage':dict(collections.Counter(f'{r[7]}:{r[8]}' for r in new)),'static_live_nodes':len(selected['static']),'static_live_properties':len(comparisons),'shared_property_differences':0,'live_only_nonname_properties':sum(r[3]!='BYTE_IDENTICAL' for r in comparisons),'independent_fdtget_checks':len(fchecks),'source_platforms_all_fields_match':True,'source_regions_all_fields_match':True,'compiled_mt6878_region_entries':len(regionrows),'interconnect_reuse_all133_specifiers_match':True,'runtime_translations_or_groups_measured':0,'compiler_cpp_sha256':hashlib.sha256(s.encode()).hexdigest(),'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D,L]}}
(O/'contract-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
