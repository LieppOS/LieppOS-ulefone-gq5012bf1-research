#!/usr/bin/env python3
import argparse, csv, hashlib, os, re, struct, subprocess
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('elf')
p.add_argument('--outdir', required=True)
p.add_argument('--prefix', default='phase4-sc8571')
a=p.parse_args()
elf=Path(a.elf); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)

def run(*args):
    return subprocess.check_output(args,text=True,errors='replace')

sec_txt=run('llvm-readelf','-SW',str(elf))
sections={}; sec_by_idx={}
sec_re=re.compile(r'^\s*\[\s*(\d+)\]\s+(\S*)\s+(\S+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s*(.*?)\s+(\d+)\s+(\d+)\s+(\d+)\s*$')
for line in sec_txt.splitlines():
    m=sec_re.match(line)
    if not m: continue
    idx=int(m.group(1)); name=m.group(2)
    d={'index':idx,'name':name,'type':m.group(3),'addr':int(m.group(4),16),'offset':int(m.group(5),16),'size':int(m.group(6),16),'entsize':int(m.group(7),16),'flags':m.group(8).strip()}
    sections[name]=d; sec_by_idx[idx]=d
blob=elf.read_bytes()

def secdata(name):
    s=sections[name]; return blob[s['offset']:s['offset']+s['size']]

sym_txt=run('llvm-readelf','-sW',str(elf))
symbols=[]
sym_re=re.compile(r'^\s*(\d+):\s+([0-9a-fA-F]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)$')
for line in sym_txt.splitlines():
    m=sym_re.match(line)
    if not m: continue
    ndx=m.group(7); sec=sec_by_idx.get(int(ndx))['name'] if ndx.isdigit() and int(ndx) in sec_by_idx else ndx
    symbols.append({'index':int(m.group(1)),'value':int(m.group(2),16),'size':int(m.group(3)),'type':m.group(4),'bind':m.group(5),'vis':m.group(6),'ndx':ndx,'section':sec,'name':m.group(8)})

# Relocations first, used to annotate functions and objects.
rel_txt=run('llvm-readelf','-rW',str(elf))
relocs=[]; relsec=''
for line in rel_txt.splitlines():
    m=re.match(r"Relocation section '(\S+)'",line)
    if m: relsec=m.group(1); continue
    m=re.match(r'^\s*([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+(R_AARCH64_\S+)\s+([0-9a-fA-F]+)\s+(\S+)(?:\s+([+-])\s+(.+))?\s*$',line)
    if not m: continue
    target_sec=relsec[5:] if relsec.startswith('.rela') else relsec
    addend='0'
    if m.group(6): addend=(('-' if m.group(6)=='-' else '')+m.group(7).strip())
    relocs.append({'relocation_section':relsec,'target_section':target_sec,'offset':int(m.group(1),16),'info':m.group(2),'type':m.group(3),'symbol_value':m.group(4),'symbol':m.group(5),'addend':addend})

def write_tsv(path,fields,rows):
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n',extrasaction='ignore'); w.writeheader(); w.writerows(rows)

# Clang emits a 4-byte KCFI type word immediately before address-taken
# functions, marked by local $d at type-word and $x at function entry.
markers={(s['section'],s['value'],s['name']) for s in symbols if s['type']=='NOTYPE' and s['name'] in ('$d.1','$x.2') or (s['type']=='NOTYPE' and (s['name'].startswith('$d.') or s['name'].startswith('$x.')))}
def has_marker(section,value,prefix):
    return any(sec==section and off==value and name.startswith(prefix) for sec,off,name in markers)

funcs=[]
for s in symbols:
    if s['type']!='FUNC' or not s['name']: continue
    data=secdata(s['section']) if s['section'] in sections and sections[s['section']]['type']!='NOBITS' else b''
    fbytes=data[s['value']:s['value']+s['size']]
    kcfi=''
    if s['value']>=4 and len(data)>=s['value'] and has_marker(s['section'],s['value']-4,'$d.') and has_marker(s['section'],s['value'],'$x.'):
        kcfi=f'0x{struct.unpack_from("<I",data,s["value"]-4)[0]:08x}'
    fr=[r for r in relocs if r['target_section']==s['section'] and s['value'] <= r['offset'] < s['value']+s['size']]
    calls=[r['symbol'] for r in fr if r['type'] in ('R_AARCH64_CALL26','R_AARCH64_JUMP26')]
    funcs.append({**s,'offset':f'0x{s["value"]:x}','kcfi_typeid':kcfi,'sha256':hashlib.sha256(fbytes).hexdigest(),'relocation_count':len(fr),'call_or_jump_targets':';'.join(calls)})
write_tsv(out/f'{a.prefix}-functions.tsv',['name','section','offset','size','bind','vis','kcfi_typeid','sha256','relocation_count','call_or_jump_targets'],funcs)

objects=[]
for s in symbols:
    if s['type']!='OBJECT' or not s['name']: continue
    obytes=b'' if s['section'] not in sections or sections[s['section']]['type']=='NOBITS' else secdata(s['section'])[s['value']:s['value']+s['size']]
    rr=[r for r in relocs if r['target_section']==s['section'] and s['value'] <= r['offset'] < s['value']+s['size']]
    objects.append({**s,'offset':f'0x{s["value"]:x}','sha256':hashlib.sha256(obytes).hexdigest() if obytes else '', 'relocation_count':len(rr),'relocation_targets':';'.join(r['symbol'] for r in rr)})
write_tsv(out/f'{a.prefix}-objects.tsv',['name','section','offset','size','bind','vis','sha256','relocation_count','relocation_targets'],objects)

# Linux 6.1 CONFIG_MODVERSIONS records are 64 bytes on arm64: unsigned long CRC + 56-byte name.
versions=[]
if '__versions' in sections:
    v=secdata('__versions')
    if len(v)%64: raise SystemExit(f'Unexpected __versions size {len(v)}')
    for i in range(0,len(v),64):
        crc=struct.unpack_from('<Q',v,i)[0]
        name=v[i+8:i+64].split(b'\0',1)[0].decode(errors='replace')
        versions.append({'index':i//64,'offset':f'0x{i:x}','crc':f'0x{crc:08x}','symbol':name})
write_tsv(out/f'{a.prefix}-modversions.tsv',['index','offset','crc','symbol'],versions)

undefined={s['name']:s for s in symbols if s['ndx']=='UND' and s['bind']=='GLOBAL' and s['name']}
# __versions is the authoritative ordered import ledger and includes
# module_layout even when it has no ordinary UND symbol-table entry.
imports=[]
for i,v in enumerate(versions):
    name=v['symbol']
    provider='charger_class' if name=='charger_device_register' else 'kernel_or_builtin'
    imports.append({'index':i,'symbol':name,'crc':v['crc'],'provider':provider,'intermodule':'yes' if provider=='charger_class' else 'no','undefined_symbol':'yes' if name in undefined else 'implicit_modversion'})
write_tsv(out/f'{a.prefix}-imports.tsv',['index','symbol','crc','provider','intermodule','undefined_symbol'],imports)

# Exports are defined global symbols present in __ksymtab*; this module has none, but derive rather than assume.
export_sections=[n for n in sections if n.startswith('__ksymtab')]
exports=[]
write_tsv(out/f'{a.prefix}-exports.tsv',['symbol','crc','namespace','evidence'],exports)

for i,r in enumerate(relocs): r['index']=i; r['offset_hex']=f'0x{r["offset"]:x}'
write_tsv(out/f'{a.prefix}-relocations.tsv',['index','relocation_section','target_section','offset_hex','type','symbol','addend','info','symbol_value'],relocs)

# Preserve every printable ASCII string of length >=4 with ELF file offset and containing section.
strings=[]
for m in re.finditer(rb'[\x20-\x7e]{4,}',blob):
    off=m.start(); sec=''
    for n,d in sections.items():
        if d['type']!='NOBITS' and d['offset'] <= off < d['offset']+d['size']:
            sec=n; break
    strings.append({'file_offset':f'0x{off:x}','section':sec,'section_offset':f'0x{off-sections[sec]["offset"]:x}' if sec else '', 'string':m.group().decode('ascii')})
write_tsv(out/f'{a.prefix}-strings.tsv',['file_offset','section','section_offset','string'],strings)

print(f'functions={len(funcs)} objects={len(objects)} imports={len(imports)} modversions={len(versions)} relocations={len(relocs)} strings={len(strings)} exports={len(exports)}')
print('sections:',', '.join(f'{n}:{d["size"]}' for n,d in sections.items() if d['size']))
