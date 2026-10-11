#!/usr/bin/env python3
"""Exercise strict DRM acceptance on rebuilt temporary copies, never stock ELFs.
Usage: drm-mutation-test.py RECIPE BUILD_DIR STOCK_DIR REPORT_JSON
"""
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

recipe, build, stock, report = [Path(x).resolve() for x in sys.argv[1:]]
sys.dont_write_bytecode = True
sys.path.insert(0, str(recipe/'scripts'))
from normalize import kpp, normalized
results=[]
controls=[]
for module in ['drm_display_helper','drm_dma_helper']:
    source=build/(module+'.stripped');k=kpp.KO(source)
    _,bid,n=normalized(k);assert n==20
    def at(name,relative=0):
        sec=k.sec(name);assert sec and sec['size']>relative,(module,name)
        return sec['off']+relative
    ro=next(s for s in k.secs if s['n'].startswith('.rodata') and s['size'])
    data=next((s for s in k.secs if s['n']=='.data' and s['size']),ro)
    crc=next(s for s in k.secs if 'kcrctab' in s['n'] and s['size'])
    btf=k.sec('.BTF');assert btf
    hl,toff,tlen,soff,slen=struct.unpack_from('<IIIII',k.b,btf['off']+4)
    start=btf['off']+hl+toff;end=start+tlen;pos=start;named=None;typed=None
    while pos<end:
        name,info,value=struct.unpack_from('<III',k.b,pos);kind=(info>>24)&31;vlen=info&65535
        if named is None and name: named=pos
        if typed is None and value and kind in [2,8,9,10,11,12,13,14,18]:typed=pos+8
        extra={1:4,2:0,3:12,4:12*vlen,5:12*vlen,6:8*vlen,7:0,8:0,9:0,10:0,11:0,12:0,13:8*vlen,14:4,15:12*vlen,16:0,17:4,18:0,19:12*vlen}[kind]
        pos+=12+extra
    assert pos==end and named is not None and typed is not None and slen>1
    symtab=k.sec('.symtab')
    kcfi=next(i for i,s in enumerate(k.syms) if s['n'].startswith('__kcfi_typeid_'))
    # ELF section-header size field supplies a real layout mutation even for zeroed BSS.
    shoff=struct.unpack_from('<Q',k.b,40)[0];shentsize=struct.unpack_from('<H',k.b,58)[0]
    bss=next((i for i,s in enumerate(k.secs) if s['type']==8),1)
    cases={
        'executable':at('.text',16),'rodata':ro['off'],'initialized_data':data['off'],
        'import_crc':at('__versions'),'export_crc':crc['off'],
        'export_name':at('__ksymtab_strings'),'modinfo':at('.modinfo'),
        'raw_relocation_addend':at('.rela.text',16),'symbol_value':symtab['off']+24+8,
        'kcfi_absolute_id':symtab['off']+kcfi*24+8,
        'section_bss_layout':shoff+bss*shentsize+32,
        'btf_header':btf['off'],'btf_name_reference':named,'btf_type_reference':typed,
        'btf_string':btf['off']+hl+soff+1,'gnu20_positive':bid,
        'signature_trailer':None,
    }
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','LIEPPOS_VERIFY_MODULE':module}
    with tempfile.TemporaryDirectory(prefix='drm-elf-mutation-') as tmp:
        dest=Path(tmp)/source.name;shutil.copyfile(source,dest)
        cmd=[sys.executable,str(recipe/'scripts/verify.py'),tmp,str(stock)]
        control=subprocess.run(cmd,env=env,capture_output=True,text=True)
        assert control.returncode==0,control.stderr;controls.append(dict(module=module,exit=0))
        for axis,offset in cases.items():
            data=bytearray(source.read_bytes())
            if offset is None:data+=bytes(32)+struct.pack('>BBBBB3sI',0,0,2,0,0,bytes(3),32)+b'~Module signature appended~\n'
            else:data[offset]^=1
            dest.write_bytes(data)
            test=subprocess.run(cmd,env=env,capture_output=True,text=True)
            expected=axis=='gnu20_positive';ok=(test.returncode==0)==expected
            results.append(dict(module=module,axis=axis,offset=offset,expected='PASS' if expected else 'REJECT',exit=test.returncode,result='OK' if ok else 'FAIL'))
            assert ok,(module,axis,test.stdout,test.stderr)
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps(dict(controls=controls,cases=results,all_detected=all(x['result']=='OK' for x in results),scope='Actual rebuilt ELF copies only; sole allowed structural GNU20 positive'),indent=2)+'\n')
print(f'PASS {len(results)}/{len(results)} DRM ELF mutation controls; GNU20 positives only')
