#!/usr/bin/env python3
"""Read actual modpost .mod/.cmd inputs; preserve ordered raw source provenance."""
from pathlib import Path
import subprocess,json,hashlib,re,sys,csv
P=Path(__file__).resolve().parents[1];W=Path(sys.argv[1]);D=P/'evidence/metadata/final-inputs';D.mkdir(parents=True,exist_ok=True);T=W/'src/kdm'
result=[]
for m in ['charger_class','mtk_chg_type_det','rt_pd_manager','tcpc_mt6375','tcpc_class']:
 files=list(T.rglob(m+'.mod'));assert len(files)==1
 path=files[0].with_suffix('');p=subprocess.run([str(W/'sumversion-probe'),'--module',str(path)],cwd=W/'kout',capture_output=True,text=True);assert p.returncode==0,p.stderr
 reads=[line.split('\t',1)[1] for line in p.stderr.splitlines() if line.startswith('READ\t')]
 gen=path.with_suffix('.mod.c').read_text();match=re.search(r'MODULE_INFO\(srcversion, "([A-F0-9]+)"\)',gen);assert match and match[1]==p.stdout.strip()
 E=D/m;E.mkdir(exist_ok=True);(E/'read-trace.txt').write_text(p.stderr);(E/'module.mod').write_bytes(files[0].read_bytes());(E/'generated.mod.c').write_text(gen)
 hashed=[];cmds=[]
 for index,s in enumerate(reads):
  f=Path(s)
  if f.suffix not in ['.c','.h'] and f.suffix!='.cmd':continue
  row={'read_index':index,'path':s,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
  if f.suffix=='.cmd':
   (E/f.name).write_bytes(f.read_bytes());cmds.append(row)
  else:hashed.append(row)
 # Capture all source/include prerequisites, also those excluded by sumversion.
 dependencies=[]
 for row in cmds:
  s=Path(row['path']).read_text();dep=s[s.find('\ndeps_'):];dep=dep[:dep.find('\n\n')] if '\n\n' in dep else dep
  for x in re.findall(r'(/[^\s\\]+\.[ch])',dep):
   f=Path(x)
   if f.is_file():dependencies.append({'path':x,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 j={'module':m,'regenerated':p.stdout.strip(),'generated_mod_c_srcversion':match[1],'actual_reads':reads,'hashed_files':hashed,'object_command_files':cmds,'absolute_include_dependencies':dependencies,'kbuild_objects':files[0].read_text().splitlines(),'limit':'The ordered stream is measured, including repeated same-directory headers. OEM raw input tokens remain unavailable; this trace does not manufacture them.'}
 (E/'provenance.json').write_text(json.dumps(j,indent=2)+'\n');result.append(j)
 print(m,match[1],'source/header reads',len(hashed),'objects',len(cmds))
(D/'all-five-traces.json').write_text(json.dumps(result,indent=2)+'\n')
