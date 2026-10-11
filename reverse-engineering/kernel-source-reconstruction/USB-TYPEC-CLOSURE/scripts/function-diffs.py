#!/usr/bin/env python3
"""Precise body/layout and relocation evidence; never modifies source or operands."""
from pathlib import Path
import csv,sys,json,hashlib,subprocess,difflib,re,collections
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent/'ulefone-gq5012bf1-research';N=R.parent/'android_kernel_modules_usb_typec_ulefone_gq5012bf1-usb-typec-closure';sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp,normalized
O=Path(sys.argv[1]);tag=sys.argv[2];D=P/'evidence'/tag;D.mkdir(parents=True,exist_ok=True);m='tcpc_class';r=next(r for r in csv.DictReader((P/'evidence/baseline/ALL-458-MODULES.tsv').open(),delimiter='\t') if r['filename']==m+'.ko');a=kpp.KO(ROOT/r['stock_paths'].split(';')[0]);b=kpp.KO(O/(m+'.stripped'));af=kpp.functions(a);bf=kpp.functions(b);syms=lambda k:{s['n']:s for s in k.syms if s['info']&15==2 and 0<s['shndx']<len(k.secs)};aa=syms(a);bb=syms(b);unmatched=[n for n in af if n not in bf or af[n][0]!=bf[n][0] or af[n][2]!=bf[n][2]];base=P/'evidence/tcpc-baseline/function-comparison.json';names=[x['name'] for x in json.loads(base.read_text())['unmatched']] if tag!='tcpc-baseline' and base.exists() else unmatched;objdump=Path('/home/armol/kernel-work/usb-typec-closure-01/prebuilts/clang/host/linux-x86/clang-r487747c/bin/llvm-objdump');j=[]
def relocs(k,s):
 out=[]
 for sec in k.secs:
  if sec['type']!=4 or sec['info']!=s['shndx']:continue
  for off,info,add in k.rela_entries(sec):
   if s['val']<=off<s['val']+s['size']:out.append({'function_offset':off-s['val'],'type':info&0xffffffff,'symbol':k.sym_name(info>>32) or ('SECTION:'+k.secs[k.syms[info>>32]['shndx']]['n'] if 0<k.syms[info>>32]['shndx']<len(k.secs) else '<unnamed>'),'addend':add})
 return out
# A symbol-only disassembly can stop at embedded $d/$x mapping symbols.
# Disassemble complete sections once and extract the entire declared STT_FUNC
# range, including embedded jump-table data and all later code islands.
cache={}
for label,k,ys,path in [('stock',a,aa,ROOT/r['stock_paths'].split(';')[0]),('source',b,bb,O/(m+'.stripped'))]:
 for sec in {k.secs[ys[n]['shndx']]['n'] for n in names if n in ys}:
  p=subprocess.run([str(objdump),'--disassemble','--reloc','--no-show-raw-insn','--section='+sec,str(path)],capture_output=True,text=True)
  assert p.returncode==0,p.stderr
  cache[label,sec]=p.stdout.splitlines()
for n in names:
 s,t=aa[n],bb.get(n);dis=[]
 for label,k,y in [('stock',a,s),('source',b,t)]:
  if not y:dis.append('MISSING');continue
  f=D/(n+'.'+label+'.asm');lines=[];raw=[]
  for line in cache[label,k.secs[y['shndx']]['n']]:
   z=re.match(r'\s*([0-9a-f]+):\s*(.*)',line)
   if z and y['val']<=int(z[1],16)<y['val']+y['size']:raw.append(line)
  f.write_text(f"{label} {n} section={k.secs[y['shndx']]['n']} address={y['val']:#x} size={y['size']}\n"+'\n'.join(raw)+'\n')
  for line in raw:
   z=re.match(r'\s*([0-9a-f]+):\s*(.*)',line)
   if z:
    off=int(z[1],16)-y['val'];text=z[2]
    # LLVM -r emits unrelated section relocations even for one symbol; never
    # include them in a function-level comparison.
    if 0<=off<y['size']:lines.append(f'{off:+#06x}: {text}')
  dis.append('\n'.join(lines)+'\n')
 diff=''.join(difflib.unified_diff(dis[0].splitlines(True),dis[1].splitlines(True),fromfile=n+'.stock-relative',tofile=n+'.source-relative'));(D/(n+'.diff')).write_text(diff)
 sr=relocs(a,s);br=relocs(b,t) if t else [];j.append({'name':n,'body_exact':n not in unmatched,'stock':{'section':a.secs[s['shndx']]['n'],'offset':s['val'],'size':s['size'],'sha256':hashlib.sha256(af[n][2]).hexdigest()},'source':{'section':b.secs[t['shndx']]['n'],'offset':t['val'],'size':t['size'],'sha256':hashlib.sha256(bf[n][2]).hexdigest()} if t else None,'stock_relocations':sr,'source_relocations':br,'relative_relocations_exact':sr==br,'instruction_and_control_flow_comparison':str(D.relative_to(P)/(n+'.diff')),'full_disassembly':[n+'.stock.asm',n+'.source.asm']})
an,_,_=normalized(a);bn,_,_=normalized(b);result={'module_id':r['module_id'],'stock_functions':len(af),'source_functions':len(bf),'exact_named_bodies':len(af)-len(unmatched),'whole_stock_acceptance':an==bn,'unmatched':[x for x in j if not x['body_exact']],'original_eight_functions':j};(D/'function-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(tag,len(af)-len(unmatched),'/',len(af),'wholeELF',an==bn,[(r['name'],r['stock']['size'],r['source']['size'] if r['source'] else None) for r in j])
