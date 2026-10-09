#!/usr/bin/env python3
"""Generate source-table and board-DT ledgers without touching a device.
Usage: map-contract.py <assembled-kdm> <merged.dtb> <live-devicetree.tar> <output-dir>
Source tables are from the fully stock-accepted source; DT assertions are configuration,
not proof of PCB wiring or of runtime state selection. No external Python packages.
"""
import csv,hashlib,json,re,struct,sys,tarfile
from pathlib import Path
T,D,L,O=map(Path,sys.argv[1:]);O.mkdir(parents=True,exist_ok=True)
S=T/'drivers/pinctrl/mediatek'
def cells(b):
    assert len(b)%4==0
    return list(struct.unpack('>'+str(len(b)//4)+'I',b))
def strings(b):return b.rstrip(b'\0').decode(errors='replace').split('\0') if b else []
def decode(b):
    if not b:return True
    if b.endswith(b'\0') and all(c==0 or 32<=c<127 for c in b):return strings(b)
    return [hex(x) for x in cells(b)] if len(b)%4==0 else b.hex()
def fdt(path):
    b=path.read_bytes();h=struct.unpack_from('>10I',b);assert h[0]==0xd00dfeed
    i=h[2];st=b[h[3]:h[3]+h[8]];stack=[];out={}
    while True:
        tag,=struct.unpack_from('>I',b,i);i+=4
        if tag==1:
            e=b.index(0,i);name=b[i:e].decode();i=(e+4)&~3;stack.append(name)
            p='/'+'/'.join(stack[1:]);out[p]={}
        elif tag==2:stack.pop()
        elif tag==3:
            n,k=struct.unpack_from('>II',b,i);i+=8;name=st[k:st.index(0,k)].decode()
            out['/'+'/'.join(stack[1:])][name]=b[i:i+n];i=(i+n+3)&~3
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
            rel=n[len(prefix):];p,_,key=rel.rpartition('/');out.setdefault(p or '/',{})[key]=tf.extractfile(m).read()
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
# Parse every physical descriptor and supported mux (not a generic datasheet list).
h=(S/'pinctrl-mtk-mt6878.h').read_text();pins={};mux=[]
for m in re.finditer(r'MTK_PIN_NODRV\(\s*(\d+),\s*"([^"]+)",\s*MTK_EINT_FUNCTION\(([^,]+),\s*([^\)]+)\)(.*?)\n\s*\),?',h,re.S):
    pin=int(m[1]);em,en=m[3].strip(),m[4].strip();fs=re.findall(r'MTK_FUNCTION\((\d+),\s*"([^"]+)"\)',m[5]);pins[pin]=(em,en,dict((int(a),b) for a,b in fs))
    mux.extend([pin,m[2],em,en,int(a),b,'DRIVER IMPLEMENTATION'] for a,b in fs)
assert set(pins)==set(range(196)),len(pins)
for pin,en in re.findall(r'MTK_PIN_EINT\((\d+),\s*(\d+)\)',h):
    pins[int(pin)]=('EINT_NO_GPIO',en,{})
    mux.append([int(pin),'virtual','EINT_NO_GPIO',en,'','interrupt-only','DRIVER IMPLEMENTATION'])
assert len(pins)==216
c=(S/'pinctrl-mt6878.c').read_text();fields=[];bases=[0x10005000,0x11d10000,0x11d30000,0x11d40000,0x11d50000,0x11d60000,0x11e20000,0x11e30000,0x11eb0000,0x11ec0000]
for arr,body in re.findall(r'static const struct mtk_pin_field_calc (mt6878_pin_\w+_range)\[\] = \{(.*?)\};',c,re.S):
    for kind,arg in re.findall(r'\b(PINS?_FIELD_BASE)\(([^)]+)\)',body):
        a,z,base,addr,stride,bit,width=[int(x.strip(),0) for x in arg.split(',')];fixed=kind=='PINS_FIELD_BASE'
        for pin in range(a,z+1):
            bits=bit if fixed else bit+(pin-a)*width;off=addr+stride*(bits//32);bp=bits%32
            fields.append([pin,arr,base,hex(bases[base]),hex(off),bp,width,hex((1<<width)-1),hex(bases[base]+off),int(fixed),stride if bp+width>32 else 0])
assert fields
pull=re.search(r'mt6878_pull_type\[\] = \{(.*?)\};',c,re.S)[1];pull=re.sub(r'/\*.*?\*/','',pull,flags=re.S);pv=[int(x.strip(),0) for x in pull.split(',') if x.strip()];assert len(pv)==196
# SR is deliberately aliased to DIR by this SoC descriptor, not a separate slew register.
fields.extend([r[0],'mt6878_pin_sr_range_ALIAS_DIR',*r[2:]] for r in list(fields) if r[1]=='mt6878_pin_dir_range')
tab('PIN-FUNCTIONS.tsv',['pin','name','eint_mode','eint_number','mux','function','evidence_class'],mux)
tab('REGISTER-FIELDS.tsv',['pin','array','base_index','base_phys','offset','bit','width','mask','register_phys','shared_fixed_field','cross_register_stride'],fields)
tab('PULL-TYPES.tsv',['pin','type_mask'],[[i,v] for i,v in enumerate(pv)])
pm=(S/'pinctrl-mt6363.c').read_text();pmfields=[]
for arr,body in re.findall(r'static const struct mtk_pin_field_calc (mt6363_pin_\w+_range)\[\] = \{(.*?)\};',pm,re.S):
    for arg in re.findall(r'PIN_SIMPLE_FIELD_BASE\(([^)]+)\)',body):
        pin,addr,bit,width=[int(x.strip(),0) for x in arg.split(',')]
        pmfields.append([pin,arr,hex(addr),bit,width,'SPMI parent regmap, not SoC MMIO'])
tab('MT6363-REGISTER-FIELDS.tsv',['pin','array','regmap_offset','bit','width','access'],pmfields)
summary={};all_states=[];consumers=[];gpios=[];irqrefs=[];eints=[];controller_records={}
for label,nodes in [('static',fdt(D)),('live',live(L))]:
    ph={cells(v['phandle'])[0]:p for p,v in nodes.items() if 'phandle' in v};controllers={p:v for p,v in nodes.items() if any(x in strings(v.get('compatible',b'')) for x in ['mediatek,mt6878-pinctrl','mediatek,mt6363-pinctrl'])}
    controller_records[label]={p:{k:decode(v) for k,v in n.items()} for p,n in controllers.items()}
    pio=next(p for p,v in controllers.items() if 'mediatek,mt6878-pinctrl' in strings(v['compatible']))
    ei=ph[cells(nodes[pio]['mediatek,eint'])[0]];ed=nodes[ei]
    controller_records[label][ei]={k:decode(v) for k,v in ed.items()}
    seq=cells(ed['mediatek,pins']);assert len(seq)%4==0
    names=strings(ed.get('reg-name',b''));reg=cells(ed['reg'])
    for i in range(0,len(seq),4):
        n,inst,idx,deb=seq[i:i+4];assert n<cells(ed['mediatek,total-pin-number'])[0]
        base=(reg[inst*4]<<32)|reg[inst*4+1];eints.append([label,ei,n,inst,names[inst],idx,deb,hex(base)])
    statecount=0
    for p,v in nodes.items():
        # States consist of subnodes with pinmux; retain every declared state including unreferenced.
        if p.startswith(pio+'/') and 'pinmux' in v:
            state=p.rpartition('/')[0];config={k:decode(b) for k,b in v.items() if k not in ['pinmux','phandle','linux,phandle','name']}
            for word in cells(v['pinmux']):
                pin,mode=word>>8,word&0xf;fun=pins.get(pin,('','',{}))[2].get(mode,'INVALID_OR_UNKNOWN')
                all_states.append([label,state,p,hex(word),pin,mode,fun,json.dumps(config,sort_keys=True),status(nodes,p),'ENABLED DT CONFIGURATION' if status(nodes,p)=='okay' else 'POSSIBLE BUT UNVERIFIED']);statecount+=1
        ns=strings(v.get('pinctrl-names',b''))
        for key,b in v.items():
            if re.fullmatch(r'pinctrl-\d+',key):
                num=int(key.split('-')[1]);name=ns[num] if num<len(ns) else '(unnamed)'
                for handle in cells(b):
                    target=ph.get(handle,'UNKNOWN')
                    if target==pio or target.startswith(pio+'/') or target in controllers:consumers.append([label,p,key,name,hex(handle),target,status(nodes,p)])
            # GPIO specifier parsing follows provider #gpio-cells, not blind phandle scanning.
            if key=='gpios' or key.endswith('-gpios') or key.endswith('-gpio') or key in ['uvc_switch_gpio','uvc_vbus_gpio','otg_gpio_select','tiny2c_usb_vdd_1v8','tiny2c_usb_vdd_3v3','tiny2c_usb_vddio_3v3']:
                if len(b)%4:continue
                cc=cells(b);j=0
                while j<len(cc):
                    handle=cc[j];provider=ph.get(handle);j+=1
                    if not provider or '#gpio-cells' not in nodes[provider]:break
                    num=cells(nodes[provider]['#gpio-cells'])[0];args=cc[j:j+num];j+=num
                    if len(args)!=num:break
                    if provider in controllers:gpios.append([label,p,key,provider,args[0],hex(args[1]) if len(args)>1 else '',status(nodes,p),'GPIO controller-relative offset; not Linux global GPIO number'])
        # Follow of_irq_find_parent: stop at the first ancestor/provider declaring
        # #interrupt-cells. A PMIC's child IRQ domain must not be attributed to SoC EINT.
        parent=p;seen=set()
        while parent not in seen:
            seen.add(parent);ip=nodes.get(parent,{}).get('interrupt-parent')
            parent=ph.get(cells(ip)[0],'UNKNOWN') if ip else (parent.rpartition('/')[0] or '/')
            if '#interrupt-cells' in nodes.get(parent,{}):break
            if parent in ['UNKNOWN','/']:break
        if parent in controllers and 'interrupts' in v:
            irqrefs.append([label,p,parent,json.dumps(cells(v['interrupts'])),status(nodes,p)])
    summary[label]={'nodes':len(nodes),'pinmux_entries':statecount,'controllers':list(controllers),'eint_node':ei,'eint_total':cells(ed['mediatek,total-pin-number'])[0],'eint_instances':cells(ed['mediatek,instance-num'])[0],'configured_eint_rows':len(seq)//4}
tab('DT-PIN-STATES.tsv',['operand','state_node','config_node','pinmux_word','pin','mode','function','electrical_config','effective_status','evidence_class'],all_states)
tab('DT-CONSUMERS.tsv',['operand','consumer','property','state_name','phandle','state_node','effective_status'],consumers)
tab('DT-GPIO-REFERENCES.tsv',['operand','consumer','property','controller','offset','flags','effective_status','number_namespace'],gpios)
tab('DT-EINT-CONSUMERS.tsv',['operand','consumer','controller','interrupt_cells','effective_status'],irqrefs)
tab('EINT-MATRIX.tsv',['operand','controller','eint','instance','instance_name','instance_local_index','debounce_supported','instance_base'],eints)
(O/'CONTROLLERS.json').write_text(json.dumps(controller_records,indent=2,sort_keys=True)+'\n')
summary['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D,L,S/'pinctrl-mt6878.c',S/'pinctrl-mtk-mt6878.h']}
summary.update(physical_pins=196,virtual_descriptors=20,alternate_function_rows=len(mux),register_field_rows=len(fields),gpio_references=len(gpios),state_references=len(consumers),eint_consumers=len(irqrefs))
(O/'mapping-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2))
