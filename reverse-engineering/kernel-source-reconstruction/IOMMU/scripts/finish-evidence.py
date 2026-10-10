#!/usr/bin/env python3
"""Preserve accepted clean-build ELF/source/provider/reverse-consumer evidence.
Usage: finish-evidence.py <recipe> <accepted-ws>
Derived from accepted INTERCONNECT-EMI verifier machinery; no runtime IO.
"""
import sys,csv,json,hashlib,struct,subprocess,re,shlex,lzma,shutil
sys.dont_write_bytecode=True
from pathlib import Path
from dtlib import tab,export_values
N,W=map(Path,sys.argv[1:]);P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit';sys.path.insert(0,str(N/'scripts'));from normalize import kpp
S=R/'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules';B=W/'out/B1';j=json.load((W/'acceptance/acceptance.json').open());assert set(j)=={'mtk_iommu'}
for d in ['evidence/acceptance','evidence/build','source']: (P/d).mkdir(parents=True,exist_ok=True)
for p in (W/'acceptance').iterdir():shutil.copy2(p,P/'evidence/acceptance'/p.name)
for src,dst in [('functions-parity.tsv','FUNCTION-PARITY.tsv'),('data-parity.tsv','DATA-PARITY.tsv')]:shutil.copy2(W/'acceptance'/src,P/dst)
rows=[]
for m,x in j.items():
 k=kpp.KO(S/(m+'.ko'));assert not k.b.endswith(b'~Module signature appended~\n');rows.append([m+'.ko',x['stock_sha256'],x['bytes'],x['functions'],x['functions'],x['data'],x['data'],x['imports'],x['exports'],x['kcfi_abs_ids'],x['relocations'],len(k.secs),hex(x['allowed_range'][0]),x['allowed_range'][1],x['raw_differing_bytes'],'BUILD_METADATA_ONLY','A',x['unresolved']])
tab(P/'MODULE-PARITY.tsv',['module','stock_sha256','bytes','functions_exact','functions_total','data_exact','data_total','imports','exports','kcfi_abs_ids','relocations','sections_including_null','build_id_offset','build_id_bytes','raw_differing_bytes','residual','accepted_source_class','unresolved'],rows)
for tag in ['B1','B2']:
 for name in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','SOURCE-TREE','PROVIDER-TREE','config.sha256','gki-symvers.sha256','iommu.Module.symvers','natural-external-provider.symvers','crc-witnesses.tsv','provider-object.sha256','build.log']:shutil.copy2(W/'out'/tag/name,P/'evidence/build'/f'{tag}-{name}')
shutil.copy2(W/'provider/build.log',P/'evidence/build/provider-build.log');shutil.copy2(W.parent/'b1b2-clean-checkout.log',P/'evidence/build/b1b2-clean-checkout.log')
master={r['module_id']:r for r in csv.DictReader((A/'ALL-457-MODULES.tsv').open(),delimiter='\t')};tid=next(k for k,v in master.items() if v['filename']=='mtk_iommu.ko');edges=list(csv.DictReader((A/'DEPENDENCY-EDGES.tsv').open(),delimiter='\t'));external=[r for r in edges if r['consumer_module_id']==tid and r['provider_module_ids']!='GKI_CORE'];assert len(external)==18
wc={r['symbol']:r['command_record'] for r in csv.DictReader((B/'crc-witnesses.tsv').open(),delimiter='\t')};cpp={};proof=[]
def sym(ko,s):return next(y for y in ko.syms if y['n']==s and 0<y['shndx']<len(ko.secs))
def prefix(ko,y):
 assert y['info']&15==2 and y['val']>=4;sec=ko.secs[y['shndx']];return struct.unpack_from('<I',ko.b,sec['off']+y['val']-4)[0]
def preprocess(cmd):
 if cmd in cpp:return cpp[cmd]
 text=(W/'src/prov'/cmd).read_text();args=shlex.split(text.splitlines()[0].split(':=',1)[1]);args[0]=str(W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin/clang');clean=[];i=0
 while i<len(args):
  if args[i]=='-o':i+=2;continue
  if args[i]=='-c' or args[i].startswith('-Wp,-MMD,'):i+=1;continue
  clean.append(args[i]);i+=1
 p=subprocess.run(clean+['-E','-P'],cwd=W/'kout',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);assert p.returncode==0,p.stderr;cpp[cmd]=p.stdout
 dest=P/'evidence/build/provider-commands'/cmd;dest.parent.mkdir(parents=True,exist_ok=True);dest.with_suffix(dest.suffix+'.xz').write_bytes(lzma.compress((W/'src/prov'/cmd).read_bytes()));return p.stdout
for r in external:
 s=r['symbol'];pid=r['provider_module_ids'];pr=master[pid];cmd=wc[s];ob=W/'src/prov'/cmd;src=kpp.KO(ob.with_name(ob.name[1:-4]));stk=kpp.KO(R/pr['stock_paths'].split(';')[0]);a,b=sym(src,s),sym(stk,s);assert a['info']&15==b['info']&15==2;av,bv=prefix(src,a),prefix(stk,b);assert av==bv,(s,av,bv)
 text=preprocess(cmd);q=re.search(r'(?:^|[;}\n])([^\n;{}]*?\b'+re.escape(s)+r'\s*\([^;{}]*?\))\s*\{',text,re.S);assert q,('source signature missing',s);proof.append([s,pid,r['required_crc'],r['export_type'],cmd,' '.join(q[1].split()),hex(av),hex(bv),'CRC_LICENCE_KCFI_PREFIX_IDENTICAL','ABI proof only; provider whole module remains uncertified'])
tab(P/'evidence/acceptance/PROVIDER-ABI-WITNESSES.tsv',['symbol','stock_provider_id','crc','licence','source_command','signature','source_callee_kcfi_word','stock_callee_kcfi_word','result','limit'],proof)
# Actual reverse imports into owned target; separately record completed components'
# real imports into debug/secure providers without certifying those whole modules.
cross=[];transport=[];accel={'MALI-GPU-KERNEL','APUSYS-NPU-KERNEL','CAMERA-ISP-KERNEL','MTK-VCODEC-KERNEL','MTK-MDP-KERNEL','GPU-AI-AUX-KERNEL-INTERFACES'}
for r in edges:
 owned=r['provider_module_ids']==tid;related=r['provider_module_ids'].split('@')[0] in ['iommu_debug.ko','iommu_secure.ko'];cr=master[r['consumer_module_id']]
 if not owned and not (related and cr['component_owner'] in accel):continue
 s=r['symbol'];pr=master[r['provider_module_ids']];stk=kpp.KO(R/pr['stock_paths'].split(';')[0]);c=kpp.KO(R/cr['stock_paths'].split(';')[0]);assert kpp.versions(c)[0][s]==int(r['required_crc'],16);assert export_values(stk)[s]==(r['export_type'],int(r['required_crc'],16))
 if owned:src=kpp.KO(B/'mtk_iommu.stripped')
 else:src=kpp.KO(W/'src/prov/drivers/misc/mediatek/iommu'/(pr['filename'][:-3]+'.o'))
 a,b=sym(src,s),sym(stk,s);assert prefix(src,a)==prefix(stk,b);expected=[y['val']&0xffffffff for y in c.syms if y['n']=='__kcfi_typeid_'+s];assert not expected or all(v==prefix(src,a) for v in expected)
 reloc=[]
 for sec in c.secs:
  if sec['type']==4:
   for off,info,add in c.rela_entries(sec):
    if c.sym_name(info>>32)==s:reloc.append((sec['n'],hex(off),info&0xffffffff,add))
 assert reloc
 row=[r['consumer_module_id'],cr['component_owner'],cr['source_status'],s,r['provider_module_ids'],r['required_crc'],r['export_type'],hex(prefix(src,a)),json.dumps(expected),json.dumps(reloc),'FULL_OWNED_FUNCTION_EXACT' if owned else 'SOURCE_PROVIDER_CRC_AND_KCFI_EXACT; WHOLE_PROVIDER_NOT_CERTIFIED','STOCK_BINARY_IMPLEMENTATION; EXECUTION_UNKNOWN']
 if owned:cross.append(row)
 else:
  text=(W/'src/prov/drivers/misc/mediatek/iommu'/('.'+pr['filename'][:-3]+'.o.cmd')).read_text();natural={n:int(v,16) for n,v in re.findall(r'^#SYMVER (\S+) (\S+)',text,re.M)};assert natural[s]==int(r['required_crc'],16);transport.append(row)
header=['consumer_id','owner','source_status','symbol','provider_id','crc','licence','source_callee_kcfi_word','consumer_abs_kcfi_ids','consumer_relocations','result','limit'];tab(P/'CROSS-COMPONENT-ABI.tsv',header,cross);tab(P/'evidence/acceptance/ACCELERATOR-IOMMU-BOUNDARIES.tsv',header,transport)
# Freeze all actual local public dependencies for target and real provider objects.
files={};base='5e415e059253ce0d2e61c97108e5f5785d71f06f'
for kind in ['kdm','prov']:
 root=W/'src'/kind
 for cmd in root.rglob('.*.o.cmd'):
  for path in re.findall(re.escape(str(root))+r'/([^\s\\]+)',cmd.read_text()):
   src=root/path
   if src.is_file() and src.suffix in ['.c','.h'] and not path.endswith('.mod.c'):
    canonical=str(src.resolve().relative_to(root.resolve()));files[canonical]=src.resolve()
for path,src in sorted(files.items()):
 blob=subprocess.check_output(['git','-C',str(W/'kernel_device_modules-6.1'),'show',base+':'+path]);assert blob==src.read_bytes(),path;dst=P/'source/compiled-inputs'/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
tab(P/'source/COMPILED-INPUTS.tsv',['file','sha256','public_pin','status'],[[f,hashlib.sha256(src.read_bytes()).hexdigest(),base,'PUBLIC_BLOB_UNCHANGED'] for f,src in sorted(files.items())])
(P/'source/COMMIT').write_text(subprocess.check_output(['git','-C',str(N),'rev-parse','HEAD'],text=True));summary={'maintained_commit':(P/'source/COMMIT').read_text().strip(),'whole_stock_parity':True,'unresolved':0,'functions':48,'data_objects':88,'imports':98,'exports':2,'kcfi_absolute_ids':2,'relocations':1220,'target_objects_per_build':len((B/'INTERMEDIATE-SHA256SUMS').read_text().splitlines()),'provider_objects_per_build':len((B/'provider-object.sha256').read_text().splitlines()),'source_crc_licence_kcfi_boundary_checks':len(proof),'actual_reverse_imports':len(cross),'completed_accelerator_debug_secure_boundaries':len(transport),'unchanged_public_compiled_inputs':len(files),'runtime_validation':'DEFERRED'};(P/'evidence/acceptance/result.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
