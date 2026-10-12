#!/usr/bin/env python3
"""ActualB1/B2freshfamilyclones, privatecohorts, regenerateconfig, all-objectproof."""
from pathlib import Path
import subprocess,os,json,csv,hashlib,shutil,argparse
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
ap=argparse.ArgumentParser();ap.add_argument('family',choices=['board_io','camera_aux','biometric_transport']);args=ap.parse_args();family=args.family
os.environ.update(GIT_NO_LAZY_FETCH='1',GIT_ALLOW_PROTOCOL='file',GIT_TERMINAL_PROMPT='0',PYTHONDONTWRITEBYTECODE='1',JOBS='4',LIEPPOS_IOMMU_MIRROR='/home/armol/kernel-work/g-source-recovery-batch-01/pin-mirror',LIEPPOS_NKM_MIRROR='/home/armol/kernel-work/public-mtk/nkm.git')
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent;W=Path('/home/armol/kernel-work/g-source-recovery-batch-02');E=P/'evidence/independent-proof'/family;E.mkdir(parents=True,exist_ok=True);SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('w') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==0,'Actual failure preserved '+str(log)
def symvers(ws):
 out={}
 for f in (ws/'src').rglob('Module.symvers'):
  rows=[]
  for l in f.read_text().splitlines():a=l.split('\t');assert len(a)==5;a[2]=a[2].replace(str(ws),'/PRIVATE_WS');rows.append(a)
  out[str(f.relative_to(ws))]=sorted(rows)
 return out
source=ROOT/('android_kernel_modules_'+family+'_ulefone_gq5012bf1');commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip();assert not subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
assert not (W/'dev/cohort').exists(),'Make originaldevelopmentcohort unavailable beforeproof'
bundle=E/(source.name+'.bundle');run(['git','-C',str(source),'bundle','create',str(bundle),'HEAD'],E/'bundle-create.log');run(['git','-C',str(source),'bundle','verify',str(bundle)],E/'bundle-verify.log');builds=[];count=len(list(csv.DictReader((source/'reference/BATCH-MANIFEST.tsv').open(),delimiter='\t')))
for tag in ['B1','B2']:
 base=W/'proof'/tag;base.mkdir(parents=True,exist_ok=True);clone=base/(family+'-source');ws=base/'ws';D=E/tag;D.mkdir(parents=True,exist_ok=True);assert not clone.exists(),'No priorclone/outputreuse'
 assert os.statvfs(W).f_bavail*os.statvfs(W).f_frsize>20*2**30,'Lowdisk20GiBfloor: preservecheckpoint'
 run(['git','clone','--no-hardlinks',str(source),str(clone)],D/'clone.log');assert subprocess.check_output(['git','-C',str(clone),'rev-parse','HEAD'],text=True).strip()==commit;assert not (clone/'.git/objects/info/alternates').exists()
 if (ws/'src').exists():
  q=ws/'preserved-source';q.mkdir(exist_ok=True);prior=json.loads((ws/'COHORT-LAST-FAMILY.json').read_text())['family'];dest=q/prior;assert not dest.exists();(ws/'src').rename(dest)
 run(['bash',str(clone/'scripts/bootstrap.sh'),str(ws)],D/'bootstrap.log');run(['bash',str(clone/'scripts/make-kout.sh'),str(ws)],D/'fresh-config-prepare.log');mixed=(clone/'reference/acceptance-plan.json').exists();build='build-reproducible.sh' if mixed else 'bulk-build.sh';verify='verify-planned.py' if mixed else 'verify.py';run(['bash',str(clone/'scripts'/build),str(ws),family+'-'+tag],D/'build.log');out=ws/'out'/(family+'-'+tag)
 run(['python3',str(clone/'scripts'/verify),str(out),str(W/'stock-flat'),str(D/'acceptance')],D/'whole-stock.log')
 if mixed:run(['python3',str(clone/'scripts/mutation-accepted.py'),family,str(out),str(W/'stock-flat')],D/'actual-elf-mutations.log')
 else:run(['python3',str(clone/'scripts/mutation-test.py'),str(out),str(W/'stock-flat')],D/'actual-elf-mutations.log')
 objects={str(f.relative_to(ws)):SHA(f) for b in [ws/'src',ws/'kout'] for f in b.rglob('*.o')};files={f.name:SHA(f) for f in out.iterdir() if f.suffix in ['.ko','.stripped']};assert len(files)==2*count;trees={f.name:f.read_text().strip() for f in out.glob('*SOURCE-TREE')};syms=symvers(ws);j=json.loads((out/'provider/provider-witnesses.json').read_text())
 expected_errors=dict(json.loads((clone/'reference/acceptance-plan.json').read_text())['provider_errors']) if mixed else {}
 for s,entries in j.items():
  for e in entries:assert e['errors']==expected_errors.get(s,[]) and SHA(ws/'src/kdm'/e['object'])==e['object_sha256'],(s,e['errors'])
 (D/'ALL-ACTUAL-OBJECT-SHA256.json').write_text(json.dumps(objects,indent=2,sort_keys=True)+'\n');(D/'NATURAL-SYMVERS.json').write_text(json.dumps(syms,indent=2,sort_keys=True)+'\n')
 for f in out.iterdir():
  if f.is_file() and f.suffix not in ['.ko','.stripped']:shutil.copyfile(f,D/f.name)
 shutil.copytree(out/'provider',D/'provider',dirs_exist_ok=True);builds.append(dict(tag=tag,source_commit=commit,ws=str(ws),objects=objects,files=files,source_trees=trees,config_sha256=SHA(ws/'kout/.config'),symvers=syms,provider_slots=len(j)));(E/'PROGRESS.json').write_text(json.dumps(dict(family=family,commit=commit,builds=builds),indent=2,sort_keys=True)+'\n');(ws/'COHORT-LAST-FAMILY.json').write_text(json.dumps(dict(family=family))+'\n');print('PASS',family,tag,count,'modules',len(objects),'allactualobjects',flush=True)
a,b=builds
for axis in ['objects','files','source_trees','config_sha256','symvers']:assert a[axis]==b[axis],axis+' B1/B2 discrepancy (no droppedobjects)'
recovered=W/'proof'/(family+'-bundle-recovery');assert not recovered.exists();run(['git','clone',str(bundle),str(recovered)],E/'bundle-recovery.log');assert subprocess.check_output(['git','-C',str(recovered),'rev-parse','HEAD'],text=True).strip()==commit;run(['git','-C',str(recovered),'fsck','--full','--no-dangling'],E/'bundle-fsck.log');assert not (recovered/'.git/objects/info/alternates').exists();(E/'RESULT.json').write_text(json.dumps(dict(result='PASS',family=family,scope=count,commit=commit,bundle_sha256=SHA(bundle),builds=builds),indent=2,sort_keys=True)+'\n');print('COMPLETE',family,'actualB1/B2 whole-stock/mutations/allobjects/source/config/natural symvers/bundle',flush=True)
