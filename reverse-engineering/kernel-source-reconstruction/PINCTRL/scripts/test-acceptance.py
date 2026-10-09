#!/usr/bin/env python3
"""Offline negative tests on disposable copies, never actual build/stock operands.
Usage: test-acceptance.py <maintained-repo> <accepted-build-dir>
A build-ID byte edit is allowed; behavior, ABI, strings and table edits must be rejected.
"""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
N,B=map(Path,sys.argv[1:]);sys.path.insert(0,str(N/'scripts'))
from normalize import kpp,normalized
results=[]
with tempfile.TemporaryDirectory(prefix='pinctrl-acceptance-tests-') as tmp:
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
    name='pinctrl-mt6878.stripped';k=kpp.KO(D/name);_,off,_=normalized(k)
    run('GNU_descriptor_only',name,off,True)
    for section,label in [('.init.text','instruction'),('.rodata','pin_tables'),('__versions','import_crc'),('.modinfo','module_metadata'),('.rela.rodata','raw_relocation')]:
        s=k.sec(section);assert s and s['size'],section
        run(label,name,s['off'],False)
    name='pinctrl-mtk-v2.stripped';k=kpp.KO(D/name)
    for section,label in [('__kcrctab_gpl','export_crc'),('.strtab','symbol_name')]:
        s=k.sec(section);assert s and s['size'];run(label,name,s['off']+min(1,s['size']-1),False)
print(json.dumps({'tests':len(results),'all_pass':all(r['pass'] for r in results),'results':results},indent=2))
