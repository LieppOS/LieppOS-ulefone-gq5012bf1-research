#!/usr/bin/env python3
"""Offline source descriptors + complete stock supply graph, with effective DT status.
Usage: map-power.py <clean-build-ws> <merged.dtb> <live-devicetree.tar> <output-dir>
Voltage support is driver capability. Constraints are DT settings, never measured voltages.
No third-party packages; compiler preprocessing uses the accepted target compile command.
"""
import csv,hashlib,json,re,struct,sys,tarfile,shlex,subprocess
from pathlib import Path
W,D,L,O=map(Path,sys.argv[1:]);O.mkdir(parents=True,exist_ok=True);T=W/'src/kdm'
def cells(b):
    assert len(b)%4==0
    return list(struct.unpack('>'+str(len(b)//4)+'I',b))
def strings(b):return b.rstrip(b'\0').decode(errors='replace').split('\0') if b else []
def decode(b):
    if not b:return True
    if b[0]!=0 and b.endswith(b'\0') and all(c==0 or 32<=c<127 for c in b):return strings(b)
    return [hex(x) for x in cells(b)] if len(b)%4==0 else b.hex()
def fdt(path):
    b=path.read_bytes();h=struct.unpack_from('>10I',b);assert h[0]==0xd00dfeed
    i=h[2];st=b[h[3]:h[3]+h[8]];stack=[];out={}
    while True:
        tag,=struct.unpack_from('>I',b,i);i+=4
        if tag==1:
            e=b.index(0,i);name=b[i:e].decode();i=(e+4)&~3;stack.append(name);out['/'+'/'.join(stack[1:])]={}
        elif tag==2:stack.pop()
        elif tag==3:
            n,k=struct.unpack_from('>II',b,i);i+=8;name=st[k:st.index(0,k)].decode();out['/'+'/'.join(stack[1:])][name]=b[i:i+n];i=(i+n+3)&~3
        elif tag==4:continue
        elif tag==9:break
        else:raise ValueError(tag)
    return out
def live(path):
    out={};prefix='sys/firmware/devicetree/base'
    with tarfile.open(path) as tf:
        for m in tf:
            n=m.name.lstrip('./')
            if not n.startswith(prefix) or not m.isfile():continue
            p,_,key=n[len(prefix):].rpartition('/');out.setdefault(p or '/',{})[key]=tf.extractfile(m).read()
    return out
def status(nodes,p):
    while True:
        v=strings(nodes.get(p,{}).get('status',b'okay'))
        if v and v[0] not in ['okay','ok']:return v[0]+'@'+p
        if p=='/':return 'okay'
        p=p.rpartition('/')[0] or '/'
def tab(name,head,rows):
    with (O/name).open('w') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(head);w.writerows(rows)
def split_top(s):
    parts=[];depth=0;quote=False;start=0
    for i,c in enumerate(s):
        if c=='"' and (i==0 or s[i-1]!='\\'):quote=not quote
        if quote:continue
        if c in '({[':depth+=1
        elif c in ')}]':depth-=1
        elif c==',' and depth==0:parts.append(s[start:i].strip());start=i+1
    if s[start:].strip():parts.append(s[start:].strip())
    return parts
def block(s,start):
    i=s.index('{',start);depth=0
    for j in range(i,len(s)):
        if s[j]=='{':depth+=1
        elif s[j]=='}':
            depth-=1
            if depth==0:return s[i+1:j]
    raise ValueError('unclosed block')
def number(s):
    s=re.sub(r'(?<=[0-9a-fA-F])[uUlL]+\b','',s.strip())
    if re.fullmatch(r'[0-9a-fA-FxX()+*/<>|&~ \t\n-]+',s):return int(eval(s,{'__builtins__':{}},{}))
    return s
# Resolve all descriptor register constants by the accepted compiler/preprocessor, not datasheets.
expanded={};descriptors={};ranges={};tables={};ops={}
for mod in ['mt6315-regulator','mt6363-regulator']:
    line=(T/f'drivers/regulator/.{mod}.o.cmd').read_text().splitlines()[0].split(':=',1)[1]
    args=shlex.split(line);args[0]=str(W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin/clang');clean=[];i=0
    while i<len(args):
        if args[i]=='-o':i+=2;continue
        if args[i]=='-c':i+=1;continue
        if args[i].startswith('-Wp,-MMD,'):i+=1;continue
        clean.append(args[i]);i+=1
    p=subprocess.run(clean+['-E','-P'],cwd=W/'kout',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);assert p.returncode==0,p.stderr
    s=p.stdout;expanded[mod]=hashlib.sha256(s.encode()).hexdigest()
    arr=mod.split('-')[0]+'_regulators';start=s.index('static struct '+mod.split('-')[0]+'_regulator_info '+arr+'[]');body=block(s,start);dd={}
    for entry in split_top(body):
        if '.desc' not in entry:continue
        desc=block(entry,entry.index('.desc'));d={}
        for field in split_top(desc):
            m=re.match(r'\.(\w+)\s*=\s*(.*)',field,re.S)
            if m:d[m[1]]=number(m[2])
        name=d['name'].strip('"');extra=entry[entry.index('.desc'):];end=extra.index(desc)+len(desc)+1
        for field in split_top(extra[end:].lstrip('}, ')):
            m=re.match(r'\.(\w+)\s*=\s*(.*)',field,re.S)
            if m:d['info_'+m[1]]=number(m[2])
        dd[name]=d
    descriptors[mod]=dd
    for name,body in re.findall(r'static const struct linear_range (mt_volt_range\d+)\[\] = \{(.*?)\};',s,re.S):
        vals=[]
        for entry in split_top(body):
            entry=entry.strip('{} ');values={m[1]:number(m[2]) for f in split_top(entry) if (m:=re.match(r'\.(\w+)\s*=\s*(.*)',f,re.S))};vals.append(values)
        ranges[mod+':'+name]=vals
    for name,body in re.findall(r'static const unsigned int (ldo_volt_table\d+)\[\] = \{(.*?)\};',s,re.S):tables[mod+':'+name]=[number(v) for v in split_top(body)]
    for name,body in re.findall(r'static const struct regulator_ops (\w+) = \{(.*?)\};',s,re.S):ops[mod+':'+name]={m[1]:m[2].strip() for f in split_top(body) if (m:=re.match(r'\.(\w+)\s*=\s*(.*)',f,re.S))}
assert len(descriptors['mt6315-regulator'])==4 and len(descriptors['mt6363-regulator'])==39,{k:len(v) for k,v in descriptors.items()}
for mod,ds in descriptors.items():
    for name,d in ds.items():
        d['name']=name
        if 'volt_table' in d:d['n_voltages']=len(tables[mod+':'+d['volt_table']])
        if 'linear_ranges' in d:d['n_linear_ranges']=len(ranges[mod+':'+d['linear_ranges']])
rt=(T/'drivers/regulator/rt6160-regulator.c').read_text();dv=(T/'drivers/regulator/mtk-dvfsrc-regulator.c').read_text()
rtconst={k:number(v) for k,v in re.findall(r'^#define (RT6160_\w+)\s+([^\n]+)',rt,re.M)}
rtvalues=[int(v.strip()) for v in re.search(r'const int ramp_tables\[\] = \{([^}]+)',rt)[1].split(',')]
dvvalues=[int(v.strip()) for v in re.search(r'mt6878_voltages\[\] = \{([^}]+)',dv)[1].split(',') if v.strip()]
assert [rtconst[x] for x in ['RT6160_VOUT_MINUV','RT6160_VOUT_MAXUV','RT6160_VOUT_STPUV']]==[2025000,5200000,25000]
assert dvvalues==[575000,600000,650000,725000]
source={'descriptors':descriptors,'linear_ranges':ranges,'voltage_tables_uV':tables,'operations':ops,'preprocessed_sha256':expanded,'rt6160_source_constants':rtconst,'rt6160_ramp_table_uV_per_us':rtvalues,'mt6878_dvfsrc_voltage_table_uV':dvvalues}
(O/'SOURCE-DESCRIPTORS.json').write_text(json.dumps(source,indent=2,sort_keys=True)+'\n')
source_rows=[]
for mod,ds in descriptors.items():
    for name,d in ds.items():source_rows.append([mod,name,d.get('n_voltages',''),d.get('ops',''),d.get('enable_reg',''),d.get('enable_mask',''),d.get('vsel_reg',''),d.get('vsel_mask',''),d.get('linear_ranges',d.get('volt_table','')),json.dumps({k:v for k,v in d.items() if k.startswith('info_')},sort_keys=True),'STOCK_BINARY_IMPLEMENTATION'])
tab('SOURCE-RAILS.tsv',['module','descriptor','n_voltages','operations','enable_reg','enable_mask','vsel_reg','vsel_mask','voltage_definition','other_control_fields','evidence_class'],source_rows)
raws={'static':fdt(D),'live':live(L)};providers={};nodesets={};allrails=[];allsupplies=[];checks=[];phrefs=[]
def family(p,v):
    cc=strings(v.get('compatible',b''))
    if any(re.fullmatch(r'mediatek,mt6315_\d+-regulator',c) for c in cc):return 'mt6315-regulator'
    if any(c in ['mediatek,mt6363','mediatek,mt6363-pmic'] for c in cc):return 'mt6363-regulator'
    if 'mediatek,mt6878-dvfsrc' in cc:return 'mtk-dvfsrc-regulator'
    if 'richtek,rt6160' in cc:return 'rt6160-regulator'
    return ''
for operand,nodes in raws.items():
    ph={cells(v['phandle'])[0]:p for p,v in nodes.items() if 'phandle' in v};pv={p:family(p,v) for p,v in nodes.items() if family(p,v)};providers[operand]=pv
    nodesets[operand]={p:{k:decode(v) for k,v in n.items()} for p,n in nodes.items() if any(p==q or p.startswith(q+'/') for q in pv)}
    for p,v in nodes.items():
        if 'regulator-name' in v:
            name=strings(v['regulator-name'])[0];anc=next((q for q in sorted(pv,key=len,reverse=True) if p==q or p.startswith(q+'/')),None);mod=pv.get(anc,'OUT_OF_SCOPE_PROVIDER');handle=cells(v['phandle'])[0] if 'phandle' in v else None
            mi=cells(v['regulator-min-microvolt'])[0] if 'regulator-min-microvolt' in v else '';ma=cells(v['regulator-max-microvolt'])[0] if 'regulator-max-microvolt' in v else ''
            allrails.append([operand,p,hex(handle) if handle is not None else '',name,mod,anc or '',status(nodes,p),mi,ma,'regulator-always-on' in v,'regulator-boot-on' in v,json.dumps({k:decode(b) for k,b in v.items() if k not in ['name','phandle','linux,phandle']},sort_keys=True),'ENABLED_IN_STOCK_DT' if status(nodes,p)=='okay' else 'SOURCE_REFERENCE_ONLY'])
            if mod in ['mt6315-regulator','mt6363-regulator']:
                match=strings(v.get('regulator-compatible',p.rsplit('/',1)[1].encode()+b'\0'))[0];ds=descriptors[mod];by_match={re.search(r'"([^"]+)"',d['of_match'])[1]:d for d in ds.values()};d=by_match.get(match);valid='DESCRIPTOR_MATCH' if d else 'NO_DESCRIPTOR_MATCH'
                supported=[]
                if d and 'volt_table' in d:supported=tables[mod+':'+d['volt_table']]
                if d and 'linear_ranges' in d:
                    for rng in ranges[mod+':'+d['linear_ranges']]:supported.extend(rng['min']+i*rng['step'] for i in range(rng['max_sel']-rng['min_sel']+1))
                if d and supported and mi!='' and ma!='':valid+=';HAS_SELECTORS_IN_DT_INTERVAL' if any(mi<=x<=ma for x in supported) else ';NO_SUPPORTED_VOLTAGE_IN_DT_INTERVAL'
                checks.append([operand,p,mod,match,d.get('name','') if d else '',mi,ma,min(supported) if supported else '',max(supported) if supported else '',valid])
            elif mod in ['rt6160-regulator','mtk-dvfsrc-regulator']:
                supported=list(range(2025000,5200001,25000)) if mod=='rt6160-regulator' else [575000,600000,650000,725000]
                valid='DESCRIPTOR_MATCH;HAS_SELECTORS_IN_DT_INTERVAL' if mi!='' and ma!='' and any(mi<=x<=ma for x in supported) else 'CONSTRAINT_UNKNOWN_OR_MISMATCH'
                checks.append([operand,p,mod,'richtek,rt6160' if mod=='rt6160-regulator' else 'mediatek,mt6878-dvfsrc','rt6160-buckboost' if mod=='rt6160-regulator' else 'dvfsrc-vcore',mi,ma,min(supported),max(supported),valid])
        for key,b in v.items():
            if key.endswith('-supply'):
                cc=cells(b) if len(b)==4 else [];target=ph.get(cc[0],'UNKNOWN') if cc else 'NON_PHANDLE_VALUE:'+json.dumps(decode(b));targetv=nodes.get(target,{});anc=next((q for q in sorted(pv,key=len,reverse=True) if target==q or target.startswith(q+'/')),None)
                kind='REGULATOR_PHANDLE' if 'regulator-name' in targetv else ('NON_REGULATOR_PHANDLE' if target in nodes else 'NON_SINGLE_REGULATOR_PHANDLE')
                allsupplies.append([operand,p,key,hex(cc[0]) if cc else '',target,';'.join(strings(targetv.get('regulator-name',b''))),pv.get(anc,'OUT_OF_SCOPE_PROVIDER'),status(nodes,p),status(nodes,target) if target in nodes else 'UNKNOWN','ENABLED_IN_STOCK_DT' if status(nodes,p)=='okay' else 'SOURCE_REFERENCE_ONLY',kind])
            # Nonstandard supply links are separate from standard *-supply properties.
            if len(b)==4 and cells(b)[0] in ph and key not in ['phandle','linux,phandle'] and not key.endswith('-supply'):
                target=ph[cells(b)[0]]
                if 'regulator-name' in nodes[target]:phrefs.append([operand,p,key,hex(cells(b)[0]),target,';'.join(strings(nodes[target]['regulator-name'])),status(nodes,p),'NUMERIC_COLLISION_NOT_EVIDENCE_OF_REFERENCE'])
tab('DT-RAILS.tsv',['operand','node','phandle','regulator_name','module','controller','effective_status','min_uV','max_uV','always_on','boot_on','all_properties','evidence_class'],allrails)
tab('DT-SUPPLIES.tsv',['operand','consumer','property','phandle','provider_node','regulator_name','module','consumer_effective_status','provider_effective_status','evidence_class','reference_kind'],allsupplies)
tab('DT-OTHER-RAIL-REFERENCES.tsv',['operand','consumer','property','phandle','provider_node','regulator_name','effective_status','interpretation'],phrefs)
tab('DT-SOURCE-CHECKS.tsv',['operand','node','module','of_match','descriptor','dt_min_uV','dt_max_uV','driver_min_uV','driver_max_uV','result'],checks)
(O/'CONTROLLERS.json').write_text(json.dumps(nodesets,indent=2,sort_keys=True)+'\n')
parents={operand:{p:{k:decode(v) for k,v in nodes[p].items()} for p in {q.rpartition('/')[0] or '/' for q in providers[operand]}|{'/aliases'} if p in nodes} for operand,nodes in raws.items()}
(O/'PARENT-RESOURCES.json').write_text(json.dumps(parents,indent=2,sort_keys=True)+'\n')
comparison=[]
for p in sorted(set(nodesets['static'])|set(nodesets['live'])):
    a=raws['static'].get(p,{});b=raws['live'].get(p,{})
    for key in sorted(set(a)|set(b)):
        if key in ['name','phandle','linux,phandle']:continue
        comparison.append([p,key,'IDENTICAL' if a.get(key)==b.get(key) else 'DIFFERENT',json.dumps(decode(a[key])) if key in a else 'ABSENT',json.dumps(decode(b[key])) if key in b else 'ABSENT'])
tab('STATIC-LIVE-COMPARISON.tsv',['node','property','result','static','live'],comparison)
resource_refs=[]
for operand,nodes in raws.items():
    ph={cells(v['phandle'])[0]:p for p,v in nodes.items() if 'phandle' in v}
    contexts=set(providers[operand])|{q.rpartition('/')[0] or '/' for q in providers[operand]}|{r[1] for r in allsupplies if r[0]==operand and r[6]!='OUT_OF_SCOPE_PROVIDER'}
    for p in sorted(contexts):
        for prop,ncells in [('clocks','#clock-cells'),('power-domains','#power-domain-cells'),('interconnects','#interconnect-cells')]:
            if prop not in nodes.get(p,{}):continue
            cc=cells(nodes[p][prop]);i=0
            while i<len(cc):
                handle=cc[i];i+=1;provider=ph.get(handle,'UNKNOWN');v=nodes.get(provider,{})
                if ncells not in v:
                    resource_refs.append([operand,p,prop,hex(handle),provider,'UNKNOWN','UNKNOWN',status(nodes,p)]);break
                num=cells(v[ncells])[0];args=cc[i:i+num];i+=num;assert len(args)==num
                resource_refs.append([operand,p,prop,hex(handle),provider,';'.join(strings(v.get('compatible',b''))),json.dumps([hex(x) for x in args]),status(nodes,p)])
tab('DT-CLOCK-POWER-REFERENCES.tsv',['operand','consumer','property','phandle','provider','provider_compatible','specifier_args','consumer_effective_status'],resource_refs)
summary={'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D,L]},'providers':providers,'source_descriptors':{k:len(v) for k,v in descriptors.items()},'dt_nodes':{k:len(v) for k,v in raws.items()},'supply_suffix_properties':{k:sum(r[0]==k for r in allsupplies) for k in raws},'regulator_supply_edges':{k:sum(r[0]==k and r[-1]=='REGULATOR_PHANDLE' for r in allsupplies) for k in raws},'regulator_nodes':{k:sum(r[0]==k for r in allrails) for k in raws},'source_check_results':{r[-1]:sum(x[-1]==r[-1] for x in checks) for r in checks},'static_live_properties':len(comparison),'static_live_differences':[r for r in comparison if r[2]!='IDENTICAL']}
(O/'mapping-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2))
