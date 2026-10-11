#!/usr/bin/env python3
"""Four sequential private builds: committed fresh clones, no development reuse."""
from pathlib import Path
import subprocess,os,json,csv,hashlib,shutil,collections
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
os.environ.update(GIT_NO_LAZY_FETCH='1',GIT_ALLOW_PROTOCOL='file',GIT_TERMINAL_PROMPT='0',PYTHONDONTWRITEBYTECODE='1',JOBS='4',LIEPPOS_IOMMU_MIRROR='/home/armol/kernel-work/interconnect-pin-mirror',LIEPPOS_NKM_MIRROR='/home/armol/kernel-work/public-mtk/nkm.git')
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent;W=Path('/home/armol/kernel-work/next-dg-batch-01');E=P/'evidence/independent-proof';E.mkdir(parents=True,exist_ok=True)
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log,**kwargs):
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('w') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,**kwargs)
 assert p.returncode==0,'Failed genuine command preserved at '+str(log)
def outputs(ws):
 return {str(f.relative_to(ws)):SHA(f) for base in [ws/'src',ws/'kout'] for f in base.rglob('*.o')}
def symvers(ws):
 result={}
 for f in (ws/'src').rglob('Module.symvers'):
  ls=[]
  for l in f.read_text().splitlines():
   a=l.split('\t');assert len(a)==5;a[2]=a[2].replace(str(ws),'/PRIVATE_WS');ls.append(a)
  result[str(f.relative_to(ws))]=sorted(ls)
 return result
# Rename only this assignment's owned development dirs. Never another agent's artifacts.
Q=W/'quarantined-development';Q.mkdir(exist_ok=True)
for family in ['diagnostics','met']:
 dev=W/'dev'/family
 if dev.exists():assert not (Q/family).exists();dev.rename(Q/family)
 assert not dev.exists(),'Original development path must be unavailable'
stock=W/'proof/stock';stock.mkdir(parents=True,exist_ok=True)
for r in csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'):
 f=stock/r['filename']
 if not f.exists():f.symlink_to(R/r['stock_paths'].split(';')[0])
summary={}
for family,repository in [('diagnostics','android_kernel_modules_platform_diagnostics_ulefone_gq5012bf1'),('met','android_kernel_modules_met_instrumentation_ulefone_gq5012bf1')]:
 source=ROOT/repository;commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip();assert not subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
 bundle=E/(repository+'.bundle');run(['git','-C',str(source),'bundle','create',str(bundle),'HEAD'],E/(family+'-bundle-create.log'));run(['git','-C',str(source),'bundle','verify',str(bundle)],E/(family+'-bundle-verify.log'))
 builds=[]
 for tag in ['B1','B2']:
  base=W/'proof'/family/tag;base.mkdir(parents=True,exist_ok=True);clone=base/'source';ws=base/'ws';D=E/family/tag;D.mkdir(parents=True,exist_ok=True)
  assert not clone.exists(),'A fresh clone is required, not a prior failed bootstrap reuse'
  run(['git','clone','--no-hardlinks',str(source),str(clone)],D/'source-clone.log');assert subprocess.check_output(['git','-C',str(clone),'rev-parse','HEAD'],text=True).strip()==commit;assert not (clone/'.git/objects/info/alternates').exists()
  run(['bash',str(clone/'scripts/bootstrap.sh'),str(ws)],D/'bootstrap.log')
  run(['bash',str(clone/'scripts/bulk-build.sh'),str(ws),tag],D/'build.log')
  run(['python3',str(clone/'scripts/verify.py'),str(ws/'out'/tag),str(stock),str(D/'acceptance')],D/'whole-stock-acceptance.log')
  run(['python3',str(clone/'scripts/mutation-test.py'),str(ws/'out'/tag),str(stock)],D/'actual-elf-mutations.log')
  objects=outputs(ws);(D/'ALL-ACTUAL-OBJECT-SHA256.json').write_text(json.dumps(objects,indent=2,sort_keys=True)+'\n')
  source_trees={f.name:f.read_text().strip() for f in (ws/'out'/tag).glob('*SOURCE-TREE')};configs=SHA(ws/'kout/.config');syms=symvers(ws)
  (D/'NATURAL-SYMVERS.json').write_text(json.dumps(syms,indent=2,sort_keys=True)+'\n')
  actual_files={f.name:SHA(f) for f in (ws/'out'/tag).iterdir() if f.suffix in ['.ko','.stripped']}
  for f in (ws/'out'/tag).iterdir():
   if f.is_file() and f.suffix not in ['.ko','.stripped']:shutil.copyfile(f,D/f.name)
  shutil.copytree(ws/'out'/tag/'provider',D/'provider',dirs_exist_ok=True)
  # Every compiled provider .o byte must match its witness SHA after the actual build.
  j=json.loads((D/'provider/provider-witnesses.json').read_text())
  for name,entries in j.items():
   for e in entries:assert not e['errors'] and SHA(ws/'src/kdm'/e['object'])==e['object_sha256']
  builds.append(dict(tag=tag,ws=str(ws),clone=str(clone),objects=objects,source_trees=source_trees,config_sha256=configs,symvers=syms,files=actual_files,provider_slots=len(j)))
  summary[family]=dict(commit=commit,completed_tags=[b['tag'] for b in builds],bundle_sha256=SHA(bundle),builds=builds)
  (E/'PROGRESS.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print('PASS',family,tag,'whole-stock/mutations',len(actual_files)//2,'targets',len(objects),'actual objects',flush=True)
 a,b=builds
 assert a['files']==b['files'],'Raw/stripped B1/B2 modules differ'
 assert a['objects']==b['objects'],'Intermediate or preparation objects differ'
 assert a['source_trees']==b['source_trees'] and a['config_sha256']==b['config_sha256'],'Actual source/config differs'
 assert a['symvers']==b['symvers'],'Natural source symvers differs beyond explicit producer workspace spelling'
 recovered=W/'proof'/family/'bundle-recovery';assert not recovered.exists();run(['git','clone',str(bundle),str(recovered)],E/family/'bundle-recovery.log');assert subprocess.check_output(['git','-C',str(recovered),'rev-parse','HEAD'],text=True).strip()==commit;run(['git','-C',str(recovered),'fsck','--full','--no-dangling'],E/family/'bundle-fsck.log');assert not (recovered/'.git/objects/info/alternates').exists()
 summary[family]['result']='FULL_B1_B2_WHOLE_STOCK_ALL_OBJECTS_SYMVERS_MUTATIONS_BUNDLE_PASS'
 (E/'PROGRESS.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
 print('COMPLETE',family,'B1/B2 exact all outputs/source/config/natural symvers/intermediates+prep; bundle recovered',flush=True)
(E/'RESULT.json').write_text(json.dumps(dict(result='PASS',families=summary,scope=22,raw_stripped_pairs=44),indent=2,sort_keys=True)+'\n');print('PASS all22 independent source modules',flush=True)
