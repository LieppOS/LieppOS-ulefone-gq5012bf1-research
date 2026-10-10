#!/usr/bin/env python3
"""14 disposable full-file acceptance mutations; never alter stock operands.
Usage: test-acceptance.py <recipe> <accepted-build-directory>
"""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
N,B=map(Path,sys.argv[1:]);sys.path.insert(0,str(N/'scripts'));from normalize import kpp,normalized
results=[]
with tempfile.TemporaryDirectory(prefix='iommu-verifier-mutations-') as tmp:
 D=Path(tmp);name='mtk_iommu.stripped';shutil.copy2(B/name,D/name);orig=(D/name).read_bytes();k=kpp.KO(D/name)
 def run(label,off=None,accept=False,append=False):
  b=bytearray(orig)
  if off is not None:b[off]^=1
  if append:b.extend(b'not-an-accepted-signature')
  (D/name).write_bytes(b);p=subprocess.run([sys.executable,str(N/'scripts/verify.py'),str(D)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);ok=(p.returncode==0)==accept;results.append({'case':label,'expected_accept':accept,'accepted':p.returncode==0,'pass':ok});assert ok,(label,p.stdout,p.stderr)
 run('pristine',accept=True);run('GNU_descriptor_only',normalized(k)[1],True)
 for sec,label in [('.text','instruction'),('.rodata','platform_domains_operations'),('__versions','import_crc'),('.modinfo','module_metadata'),('.rela.rodata','raw_relocation'),('.strtab','symbol_name'),('.init.text','registration_code'),('.shstrtab','section_names')]:
  s=k.sec(sec);assert s and s['size'],sec;run(label,s['off'])
 idx=next(i for i,y in enumerate(k.syms) if y['n'].startswith('__kcfi_typeid_'));run('absolute_kcfi',k.sec('.symtab')['off']+idx*24+8)
 sec=next(s for s in k.secs if 'kcrctab' in s['n'] and s['size']);run('export_crc',sec['off'])
 idx=next(i for i,y in enumerate(k.syms) if y['info']&15==2 and y['size']);run('function_symbol_size',k.sec('.symtab')['off']+idx*24+16);run('unexpected_signature_or_trailing_bytes',append=True)
assert len(results)==14
print(json.dumps({'tests':len(results),'all_pass':all(r['pass'] for r in results),'results':results},indent=2))
