#!/usr/bin/env python3
"""Mutate disposable build copies. Stock/build operands are never changed.
Usage: test-acceptance.py <maintained-repo> <accepted-build-dir>
"""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
N,B=map(Path,sys.argv[1:]);sys.path.insert(0,str(N/'scripts'))
from normalize import kpp,normalized
results=[]
with tempfile.TemporaryDirectory(prefix='regulators-acceptance-tests-') as tmp:
    D=Path(tmp)
    for p in B.glob('*.stripped'):shutil.copy2(p,D/p.name)
    def run(label,file=None,offset=None,expected=True):
        original=(D/file).read_bytes() if file else None
        if file:
            b=bytearray(original);b[offset]^=1;(D/file).write_bytes(b)
        p=subprocess.run([sys.executable,str(N/'scripts/verify.py'),str(D)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        ok=(p.returncode==0)==expected
        results.append({'case':label,'expected_accept':expected,'accepted':p.returncode==0,'pass':ok})
        if file:(D/file).write_bytes(original)
        assert ok,(label,p.stdout,p.stderr)
    run('pristine')
    name='mt6315-regulator.stripped';k=kpp.KO(D/name);_,off,_=normalized(k)
    run('GNU_descriptor_only',name,off,True)
    for section,label in [('.text','instruction'),('.rodata','voltage_and_descriptor_tables'),('__versions','import_crc'),('.modinfo','module_metadata'),('.rela.rodata','raw_relocation'),('.strtab','symbol_name')]:
        s=k.sec(section);assert s and s['size'],section
        run(label,name,s['off']+min(1,s['size']-1),False)
    idx=next(i for i,y in enumerate(k.syms) if y['n'].startswith('__kcfi_typeid_'))
    run('kcfi_type_id',name,k.sec('.symtab')['off']+idx*24+8,False)
print(json.dumps({'tests':len(results),'all_pass':all(r['pass'] for r in results),'results':results},indent=2))
