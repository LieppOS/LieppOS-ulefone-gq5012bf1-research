#!/usr/bin/env python3
"""Independent committed-source B1/B2: hides only this task's own originals.
No stock/shared mirror/source/audit/device writes. Retains failed proof and restores
all owned paths even if compilation/parity fails. Known C outputs must still reject.
"""
from pathlib import Path
import csv,hashlib,json,os,shutil,subprocess,sys,tempfile,struct,importlib.util
# Four-core hard affinity and lower scheduling priority propagate to every
# child (git/tar/clang/make/pahole), not just the make job count.
CPU_CORES=sorted(os.sched_getaffinity(0))[-4:]
os.sched_setaffinity(0,CPU_CORES);os.nice(10)
P=Path(__file__).resolve().parents[1];ROOT=P.parents[3]
W=Path('/home/armol/kernel-work/codex-audio-dependencies-batch-02');D=W/'independent-proof-pathmaps'
assert not D.exists(), 'use a new proof root rather than replay old objects'
D.mkdir();E=P/'evidence/independent-proof-pathmaps';E.mkdir(exist_ok=True)
PREVIOUS=P/'evidence/independent-proof-low-cpu'
# Preserve valid, unchanged committed-engine B1/B2 proof; never recompile it
# gratuitously. Rehash every actual original output/config/object/ABI below.
RESUME=[r for r in json.loads((PREVIOUS/'progress.json').read_text()) if r['family']!='shared']
assert len(RESUME)==4
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR='/tmp',JOBS='4',LIEPPOS_IOMMU_MIRROR='/home/armol/kernel-work/interconnect-pin-mirror',LIEPPOS_NATIVE_MIRROR=str(W/'native-mirror'))
STOCK=W/'stock-selected';SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
families=[('slbc','android_kernel_modules_slbc_ulefone_gq5012bf1'),('modem','android_kernel_modules_modem_audio_transport_ulefone_gq5012bf1'),('shared','android_kernel_modules_audio_shared_infrastructure_ulefone_gq5012bf1')]
commits={};runs=[];moved=[]
def command(args,log):
 p=subprocess.run(args,env=ENV,capture_output=True,text=True)
 log.parent.mkdir(parents=True,exist_ok=True);log.write_text(p.stdout+p.stderr)
 assert p.returncode==0,(args,p.returncode,(p.stdout+p.stderr)[-1000:])
 return p

def abi(path,src):
 if not path.exists():return None
 rows=[]
 for line in path.read_text().splitlines():
  crc,symbol,producer,license,*namespace=line.split('\t')
  if producer.startswith(str(src)+'/'):producer=producer[len(str(src))+1:]
  rows.append([crc,symbol,producer,license,namespace])
 return rows

def modules(recipe):return list(csv.DictReader((recipe/'reference/BATCH-MANIFEST.tsv').open(),delimiter='\t'))

def mutated_verifier(recipe,out,report):
 spec=importlib.util.spec_from_file_location('norm',recipe/'scripts/normalize.py');norm=importlib.util.module_from_spec(spec);spec.loader.exec_module(norm)
 records=[];rs=modules(recipe);accepted=next(r['filename'][:-3] for r in rs if r['filename'] not in ['drm_display_helper.ko','drm_dma_helper.ko'])
 for m in [accepted]+([r['filename'][:-3] for r in rs if r['filename'] in ['drm_display_helper.ko','drm_dma_helper.ko']]):
  # A stock-original positive verifies the strict checker before mutations,
  # even for C helpers. Current source C outputs are checked separately below.
  payload=(STOCK/(m+'.ko')).read_bytes();ko=norm.kpp.KO(STOCK/(m+'.ko'))
  def at(name,offset=0):
   s=ko.sec(name);return s['off']+offset if s and s['type']!=8 and s['size']>offset else None
  cases={'original_positive':None,'text':at('.text',4),'data':at('.data'),'rodata':at('.rodata') or at('.rodata.str1.1'),
         'import_crc':at('__versions'),'modinfo':at('.modinfo'),'relocation':at('.rela.text',16),'symbol_table':at('.symtab',24),
         'export_crc':next((at(s['n']) for s in ko.secs if 'kcrctab' in s['n']),None),'btf':at('.BTF',28),
         'gnu20':norm.normalized(ko)[1],'elf_layout':0x28,'signature_append':-1}
  function=next((s for s in ko.syms if s['info']&15==2 and 0<s['shndx']<len(ko.secs) and s['val']>=4),None)
  cases['kcfi_prefix']=ko.secs[function['shndx']]['off']+function['val']-4 if function else None
  for axis,off in cases.items():
   if off is None and axis!='original_positive':continue
   with tempfile.TemporaryDirectory(prefix='audio-deps-mutation-',dir=W) as td:
    b=bytearray(payload)
    if off==-1:b+=b'UNAUTHORIZED_SIGNATURE_TRAILER'
    elif off is not None:b[off]^=1
    Path(td,m+'.stripped').write_bytes(b)
    env=dict(ENV,LIEPPOS_VERIFY_MODULE=m)
    p=subprocess.run(['python3',str(recipe/'scripts/verify.py'),td,str(STOCK)],env=env,capture_output=True,text=True)
    positive=axis in ['original_positive','gnu20'];ok=(p.returncode==0)==positive
    row=dict(module=m,axis=axis,offset=off,exit=p.returncode,expected='PASS' if positive else 'REJECT',ok=ok)
    records.append(row);assert ok,row
  if m in ['drm_display_helper','drm_dma_helper']:
   p=subprocess.run(['python3',str(recipe/'scripts/verify.py'),str(out),str(STOCK)],env=dict(ENV,LIEPPOS_VERIFY_MODULE=m),capture_output=True,text=True)
   assert p.returncode!=0;records.append(dict(module=m,axis='unchanged_source_C_rejection',exit=p.returncode,expected='REJECT',ok=True))
 report.write_text(json.dumps(records,indent=2)+'\n');return records

try:
 for family,name in families:
  repo=ROOT/name;assert not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True)
  commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();commits[name]=commit
  bundle=D/(family+'.bundle');command(['git','-C',str(repo),'bundle','create',str(bundle),'HEAD'],E/(family+'-bundle-create.log'))
  command(['git','-C',str(repo),'bundle','verify',str(bundle)],E/(family+'-bundle-verify.log'))
  shutil.copy2(bundle,P/'evidence/bundles'/('fresh-'+family+'-'+commit+'.bundle'))
  for tag in ['B1','B2']:
   recipe=D/(family+'-'+tag)/'recipe';command(['git','clone','--no-hardlinks',str(bundle),str(recipe)],E/(family+'-'+tag+'-clone.log'))
   command(['git','-C',str(recipe),'fsck','--full'],E/(family+'-'+tag+'-fsck.log'))
   assert subprocess.check_output(['git','-C',str(recipe),'rev-parse','HEAD'],text=True).strip()==commit
   assert not (recipe/'.git/objects/info/alternates').exists()
 # Recheck all actual bytes behind unchanged SLBC/modem independent records.
 for r in RESUME:
  name=dict(families)[r['family']];assert r['commit']==commits[name]
  ws=Path(r['workspace']);out=Path(r['output'])
  assert {f:SHA(out/f) for f in r['raw_stripped_sha256']}==r['raw_stripped_sha256']
  for rel,digest in r['object_sha256'].items():
   f=ws/'native-kout'/rel[len('common/'):] if rel.startswith('common/') else ws/'src/kdm'/rel.removeprefix('kdm/')
   assert SHA(f)==digest
  assert SHA(ws/'kout/.config')==r['config_sha256'];assert SHA(ws/'kout/Module.symvers')==r['core_symvers_sha256']
  assert subprocess.check_output(['git','-C',str(ws/'src/kdm'),'write-tree'],text=True).strip()==r['source_tree']
  assert abi(out/'batch-full.Module.symvers',ws/'src/kdm')==r['abi'];assert abi(out/'native.Module.symvers',ws/'src/kdm')==r['native_abi']
  shutil.copytree(PREVIOUS/(r['family']+'-'+r['tag']),E/(r['family']+'-'+r['tag']))
  runs.append(r)
 # Make ALL own development recipes and objects unavailable for continuing builds.
 for family,name in families:
  for path in [ROOT/name,W/(family+'-dev')]:
   hidden=path.with_name(path.name+'.unavailable-during-independent-proof');assert path.exists() and not hidden.exists()
   path.rename(hidden);moved.append((path,hidden))
 for family,name in families:
  if family!='shared':continue
  for tag in ['B1','B2']:
   base=D/(family+'-'+tag);recipe=base/'recipe';ws=base/'ws';dest=E/(family+'-'+tag);dest.mkdir(exist_ok=True)
   print('BUILDING',family,tag,flush=True)
   command(['bash',str(recipe/'scripts/bootstrap.sh'),str(ws)],dest/'bootstrap.log')
   command(['bash',str(recipe/'scripts/bulk-build.sh'),str(ws),tag],dest/'build.log')
   out=ws/'out'/tag;counts={'accepted':0,'expected_rejected':0}
   for r in modules(recipe):
    m=r['filename'][:-3];p=subprocess.run(['python3',str(recipe/'scripts/verify.py'),str(out),str(STOCK),str(dest/'acceptance'/m)],env=dict(ENV,LIEPPOS_VERIFY_MODULE=m),capture_output=True,text=True)
    (dest/(m+'-acceptance.log')).write_text(p.stdout+p.stderr)
    expected_C=m in ['drm_display_helper','drm_dma_helper'];assert (p.returncode!=0)==expected_C,(m,p.stderr)
    counts['expected_rejected' if expected_C else 'accepted']+=1
   if family=='shared':command(['python3',str(recipe/'scripts/residual-btf.py'),str(out),str(STOCK),str(dest/'C-residuals')],dest/'C-residual-gate.log')
   actual={}
   for r in modules(recipe):
    for suffix in ['.ko','.stripped']:
     f=out/(r['filename'][:-3]+suffix);actual[f.name]=SHA(f)
   objects={}
   for line in (out/'INTERMEDIATE-SHA256SUMS').read_text().splitlines():
    digest,rel=line.split(maxsplit=1)
    f=(ws/'native-kout'/rel[len('common/'):]) if rel.startswith('common/') else (ws/'src/kdm'/rel.removeprefix('kdm/'))
    assert SHA(f)==digest,rel;objects[rel]=digest
   for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','TARGET-SOURCE-TREE','batch-full.Module.symvers','native.Module.symvers','CONFIG-SHA256SUMS']:
    if (out/f).exists():shutil.copy2(out/f,dest/f)
   if (out/'provider').exists():shutil.copytree(out/'provider',dest/'provider',dirs_exist_ok=True);assert not json.loads((out/'provider/provider-errors.json').read_text())
   mutation_count=0
   if tag=='B1':mutation_count=len(mutated_verifier(recipe,out,dest/'mutation-tests.json'))
   record=dict(family=family,tag=tag,commit=commits[name],workspace=str(ws),output=str(out),raw_stripped_sha256=actual,
               object_sha256=objects,config_sha256=SHA(ws/'kout/.config'),core_symvers_sha256=SHA(ws/'kout/Module.symvers'),
               source_tree=(out/'TARGET-SOURCE-TREE').read_text().strip(),abi=abi(out/'batch-full.Module.symvers',ws/'src/kdm'),
               native_abi=abi(out/'native.Module.symvers',ws/'src/kdm'),mutation_count=mutation_count,**counts)
   runs.append(record);(E/'progress.json').write_text(json.dumps(runs,indent=2)+'\n');print('PASS',family,tag,counts,'objects',len(objects),flush=True)
 for family,_ in families:
  a,b=[r for r in runs if r['family']==family]
  for key in ['raw_stripped_sha256','object_sha256','config_sha256','core_symvers_sha256','source_tree','abi','native_abi']:
   assert a[key]==b[key],(family,key)
 result=dict(result='PASS_20_STRICT_ACCEPTANCES_TWO_EXPECTED_C_REJECTIONS',source_commits=commits,runs=runs,
             all_raw_stripped_objects_source_config_abi_independent=True,development_inputs_unavailable_for_all_six_builds=True,
             mutation_cases=sum(r['mutation_count'] for r in runs),source_builds=6,newly_certifiable_A=20,retained_C=2,no_stock_normalization_except_GNU20=True,
             build_jobs=4,cpu_affinity=CPU_CORES,nice_priority=10,
             unchanged_independent_records_rehashed=4,new_source_builds_this_attempt=2)
 (E/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(result['result'],'mutations',result['mutation_cases'],flush=True)
except Exception as error:
 (E/'failure.json').write_text(json.dumps({'error':repr(error),'runs_completed':len(runs)},indent=2)+'\n');raise
finally:
 for path,hidden in reversed(moved):
  if hidden.exists():hidden.rename(path)
 print('OWNED_ORIGINALS_RESTORED',flush=True)
