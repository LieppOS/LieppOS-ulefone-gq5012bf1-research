#!/usr/bin/env python3
"""Four fresh-clone/source-build proofs from bundles; keep strict C rejections.
Only this task's own source worktrees and development workspace are hidden.
No canonical checkout is moved, edited, reset or used as a recipe input.
"""
from pathlib import Path
import subprocess,os,json,csv,hashlib,signal,sys
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent
C=Path(os.environ.get('LIEPPOS_CLOSURE_PROOF_DIR','/home/armol/kernel-work/usb-typec-closure-proof'))
M=Path('/home/armol/kernel-work/usb-typec-closure-proof/mirror');E=P/'evidence/fresh-clones';E.mkdir(parents=True,exist_ok=True)
B=P/'evidence/bundles';B.mkdir(exist_ok=True)
names=['android_kernel_modules_usb_typec_ulefone_gq5012bf1','android_kernel_modules_charging_battery_ulefone_gq5012bf1']
owned=[ROOT/(n+'-usb-typec-closure') for n in names]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR='/tmp',TMP='/tmp',TEMP='/tmp',JOBS='12',LIEPPOS_IOMMU_MIRROR=str(M))
def run(cmd,log,**kwargs):
 with log.open('w') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,**kwargs)
 assert p.returncode==0,(cmd,p.returncode,str(log))
def state(phase,**kw):(E/'progress.json').write_text(json.dumps({'phase':phase,**kw},indent=2)+'\n')
def git(d,*args):return subprocess.check_output(['git','-C',str(d),*args],text=True).strip()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
commits=[]
for n,o in zip(names,owned):
 assert git(o,'status','--porcelain')==''
 commit=git(o,'rev-parse','HEAD');bundle=B/(n+'-'+commit[:12]+'.bundle')
 subprocess.run(['git','-C',str(o),'bundle','create',str(bundle),'codex/usb-typec-closure'],check=True,env=env)
 run(['git','-C',str(o),'bundle','verify',str(bundle)],E/(n+'-bundle-verify.log'))
 commits.append({'name':n,'commit':commit,'bundle':str(bundle.relative_to(P)),'bundle_sha256':sha(bundle)})
(E/'source-commits.json').write_text(json.dumps(commits,indent=2)+'\n')
held=[];reports=[]
signal.signal(signal.SIGTERM,lambda *_:sys.exit(143))
try:
 for p in owned+[Path('/home/armol/kernel-work/usb-typec-closure-01')]:
  q=p.with_name(p.name+'.held-by-closure-proof');assert not q.exists();p.rename(q);held.append((p,q))
 state('ORIGINAL_OWNED_RECIPES_AND_DEVELOPMENT_UNAVAILABLE',held=[str(p) for p,_ in held])
 for family,(n,source) in enumerate(zip(names,commits)):
  for build in ['B1','B2']:
   tag=f'F{family}-{build}';D=C/tag;D.mkdir(exist_ok=False);N=D/'recipe';W=D/'ws';logs=D/'logs';logs.mkdir()
   assert not any(p.exists() for p,_ in held)
   state('BUILDING',tag=tag,completed=[r['tag'] for r in reports],original_owned_paths_unavailable=True)
   run(['git','clone','-q','-b','codex/usb-typec-closure',str(P/source['bundle']),str(N)],logs/'clone.log')
   assert git(N,'rev-parse','HEAD')==source['commit'];assert not (N/'.git/objects/info/alternates').exists()
   run(['git','fsck','--full'],logs/'recovered-source-fsck.log')
   run(['bash',str(N/'scripts/bootstrap.sh'),str(W)],logs/'bootstrap.log')
   run(['bash',str(N/'scripts/bulk-build.sh'),str(W),build],logs/'build.log')
   O=W/'out'/build
   assert all((O/f).read_text().strip()=='0' for f in ['object-exit','module-exit'])
   assert len(list(O.glob('*.ko')))==len(list(O.glob('*.stripped')))==30
   assert json.loads((O/'provider/provider-errors.json').read_text())==[]
   stock=D/'stock-operands';stock.mkdir();rows=list(csv.DictReader((N/'reference/BATCH-MANIFEST.tsv').open(),delimiter='\t'))
   for r in rows:
    m=r['filename'].removesuffix('.ko');(stock/(m+'.ko')).symlink_to((ROOT/'ulefone-gq5012bf1-research'/r['stock_paths'].split(';')[0]).resolve())
   outcomes=[]
   for r in rows:
    m=r['filename'].removesuffix('.ko');bad=m in {'charger_class','mtk_chg_type_det','rt_pd_manager','tcpc_mt6375','tcpc_class'}
    e=dict(env,LIEPPOS_VERIFY_JOINT='1',LIEPPOS_VERIFY_MODULE=m)
    with (logs/(m+'-strict.log')).open('w') as f:p=subprocess.run(['python3',str(N/'scripts/verify.py'),str(O),str(stock),str(D/'accepted'/m)],env=e,stdout=f,stderr=subprocess.STDOUT)
    assert (p.returncode!=0)==bad,(tag,m,p.returncode)
    outcomes.append({'module':m,'expected_complete_stock_acceptance':not bad,'strict_verifier_exit':p.returncode})
   run(['python3',str(P/'scripts/compare-five.py'),str(N),str(ROOT/'ulefone-gq5012bf1-research'),str(O),str(D/'five-comparison')],logs/'five-comparison.log')
   report={'tag':tag,'source_commit':source['commit'],'source_recovered_from_bundle':True,'original_owned_paths_unavailable':True,'all_30_source_built':True,'accepted_preserved_modules':25,'closure_targets_still_rejected':5,'outcomes':outcomes,'intermediate_objects':len((O/'INTERMEDIATE-SHA256SUMS').read_text().splitlines()),'workspace':str(W),'output':str(O)}
   reports.append(report);(E/(tag+'.json')).write_text(json.dumps(report,indent=2)+'\n')
 # Check actual module/object bytes and precise CRC/producer records. The
 # diagnostic SHA manifest also hashes path-bearing Module.symvers text;
 # it is not itself a compiled ELF acceptance operand.
 run(['python3',str(P/'scripts/validate-cleancheck.py'),str(C)],E/'determinism-validation.log')
 print('PASS_FOUR_FRESH_SOURCE_BUILDS_WITH_FIVE_EXPECTED_STRICT_REJECTIONS',flush=True)
finally:
 for p,q in reversed(held):
  assert not p.exists(),p;q.rename(p)
 (E/'original-paths-restored.json').write_text(json.dumps({'restored':[str(p) for p,_ in held],'all_restored':all(p.exists() for p,_ in held)},indent=2)+'\n')
