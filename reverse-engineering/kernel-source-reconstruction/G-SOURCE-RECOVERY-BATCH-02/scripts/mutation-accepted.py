#!/usr/bin/env python3
"""Mutate actual A candidates usingUNCHANGEDstrictverifier; C baseline remainsREJECT."""
from pathlib import Path
import csv,os,subprocess,sys,tempfile,json,struct
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2].parent;family=sys.argv[1];out,stock=map(Path,sys.argv[2:4]);R=P if (P/'SOURCE-PINS.tsv').exists() else ROOT/('android_kernel_modules_'+family+'_ulefone_gq5012bf1');sys.path.insert(0,str(R/'scripts'));from normalize import kpp,normalized
plan=json.loads((R/'reference/acceptance-plan.json').read_text());cases=[]
for row in csv.DictReader((R/'reference/stock-normalized.tsv').open(),delimiter='\t'):
 m=row['module'];original=out/(m+'.stripped');k=kpp.KO(original);accepted=m in plan['A']
 def at(n,rel=0):s=k.sec(n);return s['off']+rel if s and s['type']!=8 and s['size']>rel else None
 _,bid,n=normalized(k);function=next(y for y in k.syms if y['info']&15==2 and y['size'] and 0<y['shndx']<len(k.secs));fs=k.secs[function['shndx']];targets={'unmodified':None,'function':fs['off']+function['val'],'data':at('.data'),'rodata':at('.rodata') or at('.rodata.str1.1'),'import_crc':at('__versions'),'modinfo':at('.modinfo'),'raw_relocation':next((s['off']+16 for s in k.secs if s['type']==4 and s['size']>=24),None),'export_crc':next((s['off'] for s in k.secs if 'kcrctab' in s['n'] and s['size']),None),'symbol_table':k.symtab['off']+24+8,'section_header':struct.unpack_from('<Q',k.b,0x28)[0]+64+8,'signature_trailer':len(k.b),'GNU20_descriptor':bid,'GNU_note_header':at('.note.gnu.build-id')}
 if function['val']>=4:targets['KCFI_function_prefix']=fs['off']+function['val']-4
 for axis,offset in targets.items():
  if offset is None and axis!='unmodified':continue
  # C alreadyfailing is not a passingcorruptioncontrol: onlyretainactualbaseline rejection.
  if not accepted and axis!='unmodified':continue
  with tempfile.TemporaryDirectory(prefix='gsource02-actual-elf-mutation-') as d:
   temp=Path(d);b=bytearray(original.read_bytes())
   if axis=='signature_trailer':b+=b'~Module signature appended~\n'
   elif offset is not None:b[offset]^=1
   (temp/original.name).write_bytes(b);p=subprocess.run([sys.executable,str(R/'scripts/verify.py'),str(temp),str(stock)],capture_output=True,text=True,env=dict(os.environ,LIEPPOS_VERIFY_MODULE=m,PYTHONDONTWRITEBYTECODE='1'));expected=accepted and axis in ['unmodified','GNU20_descriptor'];ok=(p.returncode==0)==expected;cases.append(dict(module=m,class_plan='A' if accepted else 'C',axis=axis,offset=offset,expected='PASS' if expected else 'REJECT',verify_exit=p.returncode,result='PASS' if ok else 'FAIL'))
assert all(c['result']=='PASS' for c in cases),'UNCHANGEDstrictacceptancecontrolunexpected'
print(json.dumps(dict(result='PASS',A_controls=sum(c['class_plan']=='A' for c in cases),C_baseline_rejections=sum(c['class_plan']=='C' for c in cases),cases=cases),indent=2))
