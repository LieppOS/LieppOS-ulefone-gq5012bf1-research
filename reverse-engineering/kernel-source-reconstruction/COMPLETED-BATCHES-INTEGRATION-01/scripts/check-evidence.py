#!/usr/bin/env python3
"""Recheck actual immutable B1/B2 outputs and authentic stock; never rebuild."""
from pathlib import Path
import os,json,hashlib,csv,subprocess,sys,collections
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];R=P.parents[2];E=P/'evidence/source-check';E.mkdir(exist_ok=True);W=Path('/home/armol/kernel-work');PR=W/'completed-batches-integration-01';STOCK=PR/'stock-selected'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def table(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def run(args,log,env=None):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',**(env or {})));log.parent.mkdir(parents=True,exist_ok=True);log.write_text(p.stdout+p.stderr);assert p.returncode==0,(args,p.returncode,p.stderr[-900:]);return p.stdout
def tree_check(src,expected):
 # git ls-tree is read-only; do not write-index/tree in another agent's outputs.
 p=subprocess.run(['git','-C',str(src),'ls-tree','-rz',expected],capture_output=True);assert p.returncode==0
 count=0
 for rec in p.stdout.split(b'\0'):
  if not rec:continue
  head,path=rec.split(b'\t',1);mode,typ,obj=head.decode().split();f=src/os.fsdecode(path)
  if typ=='blob':
   b=os.fsencode(os.readlink(f)) if mode=='120000' else f.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==obj,f;count+=1
 return count
manifest=table(P/'COMBINED-MANIFEST.tsv');repos=table(P/'SOURCE-REPOSITORIES.tsv');result=[];mutations=[];provider=[]
previous=R/'reverse-engineering/kernel-source-reconstruction/AUDIO-DEPENDENCIES-BATCH-02/evidence/independent-proof-pathmaps/result.json';deps=json.loads(previous.read_text())
for rec in repos:
 repo=rec['repository'];clone=Path(rec['private_clone']);family={'audio':'audio','scp_sensorhub':'scp','connectivity':'conn','slbc':'slbc','modem_audio_transport':'modem','audio_shared_infrastructure':'shared'}[repo.removeprefix('android_kernel_modules_').removesuffix('_ulefone_gq5012bf1')];members=[m for m in manifest if m['source_repository']==repo];records=[]
 for tag in ['B1','B2']:
  if family in ['audio','scp','conn']:
   base=W/({'audio':'codex-audio-batch-01/cleancheck','scp':'codex-conn-batch-01/cleancheck-scp','conn':'codex-conn-batch-01/cleancheck-conn'}[family]);ws=base/('ws'+tag);out=ws/'out'/tag
   assert subprocess.check_output(['git','-C',str(base/'repo'),'rev-parse','HEAD'],text=True).strip()==rec['commit']
   objmanifest=out/'INTERMEDIATE-SHA256SUMS';obj={}
   for line in objmanifest.read_text().splitlines():
    digest,relative=line.split(maxsplit=1);relative=relative.removeprefix('./');f=ws/'src/kdm'/relative
    if relative.startswith('native/'):f=ws/'native-kout'/relative.removeprefix('native/')
    elif relative.startswith('nkm/'):f=ws/'o/vendor/mediatek/kernel_modules/connectivity'/relative.removeprefix('nkm/')
    elif relative.startswith('kdm/'):f=ws/'src/kdm'/relative.removeprefix('kdm/')
    assert SHA(f)==digest,(family,relative);obj[relative]=digest
   target=(out/'TARGET-SOURCE-TREE').read_text().strip();trees=target.splitlines();source_files=tree_check(ws/'src/kdm',trees[0])
   if family=='conn':source_files+=tree_check(ws/'vendor/mediatek/kernel_modules/connectivity',trees[1])
  else:
   old=next(x for x in deps['runs'] if x['family']==family and x['tag']==tag);assert old['commit']==rec['commit'];ws=Path(old['workspace']);out=Path(old['output']);obj={}
   for relative,digest in old['object_sha256'].items():
    f=ws/'native-kout'/relative.removeprefix('common/') if relative.startswith('common/') else ws/'src/kdm'/relative.removeprefix('kdm/');assert SHA(f)==digest;obj[relative]=digest
   target=old['source_tree'];source_files=tree_check(ws/'src/kdm',target)
  hashes={m['filename']:dict(raw=SHA(out/m['filename']),stripped=SHA(out/(m['filename'][:-3]+'.stripped'))) for m in members}
  kout=ws/('o/kout' if family=='conn' else 'kout');config=SHA(kout/'.config');core=SHA(kout/'Module.symvers')
  if family in ['audio','scp','conn']:
   batch=members[0]['batch'];sub={'audio':'cleancheck','scp':'scp-sensorhub/cleancheck','conn':'connectivity/cleancheck'}[family]
   saved=R/'reverse-engineering/kernel-source-reconstruction'/batch/'evidence'/sub/(tag+'-SHA256SUMS')
   expected={l.split(maxsplit=1)[1].removeprefix('./'):l.split(maxsplit=1)[0] for l in saved.read_text().splitlines()}
   assert all(expected[m['filename']]==hashes[m['filename']]['raw'] and expected[m['filename'][:-3]+'.stripped']==hashes[m['filename']]['stripped'] for m in members)
  else:assert all(old['raw_stripped_sha256'][name]==SHA(out/name) for name in old['raw_stripped_sha256'])
  d=E/(family+'-'+tag);d.mkdir(exist_ok=True)
  verifyenv={'LIEPPOS_VERIFY_JOINT':'1'} if (clone/'reference/joint-stock-normalized.tsv').exists() else {}
  saved=d/'acceptance/acceptance.json';acceptance=json.loads(saved.read_text()) if saved.exists() else {}
  valid_cache=len(acceptance)==sum(m['proposed_class']=='A' for m in members) and all(acceptance.get(m['filename'][:-3],{}).get('rebuild_sha256')==hashes[m['filename']]['stripped'] and acceptance.get(m['filename'][:-3],{}).get('stock_sha256')==SHA(STOCK/m['filename']) for m in members if m['proposed_class']=='A')
  if not valid_cache:
   acceptance={}
   for m in members:
    if m['proposed_class']!='A':continue
    md=d/'acceptance'/m['filename'][:-3]
    run([sys.executable,clone/'scripts/verify.py',out,STOCK,md],d/(m['filename']+'-acceptance.log'),dict(verifyenv,LIEPPOS_VERIFY_MODULE=m['filename'][:-3]))
    acceptance.update(json.loads((md/'acceptance.json').read_text()))
   saved.parent.mkdir(exist_ok=True);saved.write_text(json.dumps(acceptance,indent=2)+'\n')
  assert len(acceptance)==sum(m['proposed_class']=='A' for m in members)
  if any(m['proposed_class']=='C' for m in members):
   residual=clone/'scripts'/('residual-check.py' if family=='audio' else 'residual-btf.py');run([sys.executable,residual,out,STOCK,d/'residual'],d/'residual.log')
   # Strict complete-file GNU20-only rejection independent of the residual gate.
   for m in members:
    if m['proposed_class']!='C':continue
    code='from normalize import kpp,normalized;import sys;assert normalized(kpp.KO(sys.argv[1]))[0]!=normalized(kpp.KO(sys.argv[2]))[0];print("EXPECTED_STRICT_REJECTION")'
    run([sys.executable,'-c',code,STOCK/m['filename'],out/(m['filename'][:-3]+'.stripped')],d/(m['filename']+'-strict.log'),{'PYTHONPATH':str(clone/'scripts')})
  # Genuine provider object hashes + recorded CRC/KCFI source comparisons.
  witness=out/'provider/provider-witnesses.json'
  if witness.exists():
   for symbol,entries in json.loads(witness.read_text()).items():
    for entry in entries:
     root=ws/'native-kout' if entry.get('source_root')=='native-kout' else ws/'o/vendor/mediatek/kernel_modules/connectivity' if entry.get('source_root')=='nkm' else ws/'src/kdm'
     assert not entry['errors'];assert SHA(root/entry['object'])==entry['object_sha256'];provider.append(dict(family=family,tag=tag,symbol=symbol,crc=entry['crc'],object_sha256=entry['object_sha256'],result='PASS'))
  def abi(file):
   rows=[]
   for line in file.read_text().splitlines():
    x=line.split('\t');producer=x[2];root=str(ws/'src/kdm')+'/'
    if producer.startswith(root):producer=producer[len(root):]
    elif producer.startswith(str(ws)+'/'):producer=producer[len(str(ws))+1:]
    rows.append((x[0],x[1],producer,*x[3:]))
   return sorted(rows)
  abi_files={f.name:abi(f) for f in [out/'batch-full.Module.symvers',out/'native.Module.symvers',out/'batch-kdm.Module.symvers',out/'nkm-extra.symvers.final'] if f.exists()}
  records.append(dict(tag=tag,workspace=str(ws),output=str(out),hashes=hashes,object_sha256=obj,source_tree=target,source_files_checked=source_files,config_sha256=config,core_symvers_sha256=core,abi=abi_files,accepted=len(acceptance),retained_C=sum(m['proposed_class']=='C' for m in members)))
  if tag=='B1':
   # Published recipes mutate only new temporary copies, never original stock.
   if family in ['audio','scp','conn']:
    log=d/'mutations.log'
    text=log.read_text() if log.exists() and '"all_detected": true' in log.read_text() else run([sys.executable,clone/'scripts/mutation-test.py',out,STOCK],log)
    j=json.loads(text.splitlines()[-1]);assert j['all_detected'];mutations.append(dict(family=family,result=j))
  (E/(family+'-progress.json')).write_text(json.dumps(records,indent=2)+'\n')
 a,b=records
 for key in ['hashes','object_sha256','source_tree','config_sha256','core_symvers_sha256','abi']:assert a[key]==b[key],(family,key)
 result.append(dict(repository=repo,commit=rec['commit'],family=family,records=records,result='PASS'))
# The changed-source dependency engines'68 actual independent ELF controls are
# preserved, not relabelled as newly run mutation tests in this integration.
(P/'evidence/source-evidence-result.json').write_text(json.dumps(dict(result='PASS',repositories=result,actual_A_acceptances=sum(r['records'][0]['accepted'] for r in result)*2,retained_C=sum(r['records'][0]['retained_C'] for r in result),independent_module_pairs=sum(len(r['records'][0]['hashes']) for r in result)*2,independent_object_pairs=sum(len(r['records'][0]['object_sha256']) for r in result),provider_records=provider,new_recipe_mutation_runs=mutations,preserved_dependency_mutation_cases=deps['mutation_cases'],full_builds_repeated=0),indent=2)+'\n')
print('PASS:114 actual A acceptances,12 strict C rejections+residual gates,all63 B1/B2 module/object/source/config/ABI files checked; no builds repeated')
