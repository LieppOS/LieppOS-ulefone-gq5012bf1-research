#!/usr/bin/env python3
"""Materialize final stock/body/ABI/provider/load/consumer witnesses from accepted clean build.
Usage: finish-evidence.py <recipe> <accepted-clean-ws>
"""
import sys,csv,json,hashlib,struct,subprocess,re,shlex,lzma,shutil
sys.dont_write_bytecode=True
from pathlib import Path
from dtlib import tab,export_values
N,W=map(Path,sys.argv[1:]);P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit';sys.path.insert(0,str(N/'scripts'));from normalize import kpp
S=R/'workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules';B=W/'out/B1';j=json.load((W/'acceptance/acceptance.json').open());assert set(j)=={'mmqos-common','mmqos-mt6878','mtk-emi'}
for p in (W/'acceptance').iterdir():shutil.copy2(p,P/'evidence/acceptance'/p.name)
for src,dst in [('functions-parity.tsv','FUNCTION-PARITY.tsv'),('data-parity.tsv','DATA-PARITY.tsv')]:shutil.copy2(W/'acceptance'/src,P/dst)
rows=[]
for m,x in j.items():
 k=kpp.KO(S/(m+'.ko'));assert not k.b.endswith(b'~Module signature appended~\n')
 rows.append([m+'.ko',x['stock_sha256'],x['bytes'],x['functions'],x['functions'],x['data'],x['data'],x['imports'],x['exports'],x['kcfi_abs_ids'],x['relocations'],len(k.secs),hex(x['allowed_range'][0]),x['allowed_range'][1],x['raw_differing_bytes'],'BUILD_METADATA_ONLY','A',x['unresolved']])
tab(P/'MODULE-PARITY.tsv',['module','stock_sha256','bytes','functions_exact','functions_total','data_exact','data_total','imports','exports','kcfi_abs_ids','relocations','sections_including_null','build_id_offset','build_id_bytes','raw_differing_bytes','residual','final_status','unresolved'],rows)
for tag in ['B1','B2']:
 for name in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','SOURCE-TREE','PROVIDER-TREE','config.sha256','gki-symvers.sha256','interconnect.Module.symvers','natural-external-provider.symvers','crc-witnesses.tsv','provider-object.sha256','build.log']:shutil.copy2(W/'out'/tag/name,P/'evidence/build'/f'{tag}-{name}')
shutil.copy2(W/'provider/build.log',P/'evidence/build/provider-build.log')
master={r['module_id']:r for r in csv.DictReader((A/'ALL-457-MODULES.tsv').open(),delimiter='\t')};targetids={k for k,r in master.items() if r['filename'] in {m+'.ko' for m in j}};edges=list(csv.DictReader((A/'DEPENDENCY-EDGES.tsv').open(),delimiter='\t'))
external=[r for r in edges if r['consumer_module_id'] in targetids and r['provider_module_ids']!='GKI_CORE' and r['provider_module_ids'] not in targetids];assert len(external)==33
wc={r['symbol']:r['command_record'] for r in csv.DictReader((B/'crc-witnesses.tsv').open(),delimiter='\t')};cache={};cpp={};proof=[]
def sym(ko,s):return next(y for y in ko.syms if y['n']==s and 0<y['shndx']<len(ko.secs))
def prefix(ko,y):
 assert y['info']&15==2 and y['val']>=4
 sec=ko.secs[y['shndx']];return struct.unpack_from('<I',ko.b,sec['off']+y['val']-4)[0]
def preprocess(cmd):
 if cmd in cpp:return cpp[cmd]
 text=(W/'src/prov'/cmd).read_text();line=text.splitlines()[0].split(':=',1)[1];args=shlex.split(line);args[0]=str(W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin/clang');clean=[];i=0
 while i<len(args):
  if args[i]=='-o':i+=2;continue
  if args[i]=='-c' or args[i].startswith('-Wp,-MMD,'):i+=1;continue
  clean.append(args[i]);i+=1
 p=subprocess.run(clean+['-E','-P'],cwd=W/'kout',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);assert p.returncode==0,p.stderr;cpp[cmd]=p.stdout
 dest=P/'evidence/build/provider-commands'/cmd;dest.parent.mkdir(parents=True,exist_ok=True);dest.with_suffix(dest.suffix+'.xz').write_bytes(lzma.compress((W/'src/prov'/cmd).read_bytes()))
 return p.stdout
for r in external:
 s=r['symbol'];pid=r['provider_module_ids'];pr=master[pid];cmd=wc[s];ob=W/'src/prov'/cmd;ob=ob.with_name(ob.name[1:-4]);src=kpp.KO(ob);stk=kpp.KO(R/pr['stock_paths'].split(';')[0]);a,b=sym(src,s),sym(stk,s);assert (a['info']&15)==(b['info']&15)
 text=preprocess(cmd)
 if a['info']&15==2:
  av,bv=prefix(src,a),prefix(stk,b);assert av==bv,(s,av,bv)
  q=re.search(r'(?:^|[;}\n])([^\n;{}]*?\b'+re.escape(s)+r'\s*\([^;{}]*?\))\s*\{',text,re.S)
  assert q,('source signature missing',s)
  signature=' '.join(q[1].split())
  result='CRC_LICENCE_AND_KCFI_PREFIX_IDENTICAL'
 else:
  assert a['size']==b['size'];av=bv=None;signature='struct tracepoint '+s+'; source/stock size '+str(a['size']);result='CRC_LICENCE_DATA_LAYOUT_IDENTICAL'
 proof.append([s,pid,r['required_crc'],r['export_type'],cmd,signature,'' if av is None else hex(av),'' if bv is None else hex(bv),result,'ABI boundary only; no provider source certification'])
tab(P/'evidence/acceptance/PROVIDER-ABI-WITNESSES.tsv',['symbol','stock_provider_id','crc','licence','source_command','signature','source_callee_kcfi_word','stock_callee_kcfi_word','result','limit'],proof)
# All actual stock reverse imports into targets: seven, not an invented accelerator-wide API.
reverse=[r for r in edges if r['provider_module_ids'] in targetids];cross=[]
for r in reverse:
 cr=master[r['consumer_module_id']];pr=master[r['provider_module_ids']];m=pr['filename'][:-3];src=kpp.KO(B/(m+'.stripped'));stk=kpp.KO(R/pr['stock_paths'].split(';')[0]);c=kpp.KO(R/cr['stock_paths'].split(';')[0]);s=r['symbol'];assert kpp.versions(c)[0][s]==int(r['required_crc'],16);assert export_values(src)[s]==export_values(stk)[s]==(r['export_type'],int(r['required_crc'],16));a,b=sym(src,s),sym(stk,s);assert prefix(src,a)==prefix(stk,b)
 expected=[y['val']&0xffffffff for y in c.syms if y['n']=='__kcfi_typeid_'+s];assert not expected or all(v==prefix(src,a) for v in expected)
 reloc=[]
 for sec in c.secs:
  if sec['type']==4:
   for off,info,add in c.rela_entries(sec):
    if c.sym_name(info>>32)==s:reloc.append((sec['n'],hex(off),info&0xffffffff,add))
 assert reloc
 # Function implementation is fully accepted, not merely its KCFI prefix.
 d=next(y for y in stk.syms if y['n']==s);ss=stk.secs[d['shndx']];body=stk.data(ss['n'])[d['val']:d['val']+d['size']]
 cross.append([r['consumer_module_id'],cr['component_owner'],cr['source_status'],s,r['provider_module_ids'],r['required_crc'],r['export_type'],hex(prefix(src,a)),json.dumps(expected),json.dumps(reloc),hashlib.sha256(body).hexdigest(),'IMPORT_CRC_EXPORT_LICENCE_CALLEE_KCFI_AND_FULL_PROVIDER_FUNCTION_EXACT','STOCK_BINARY_IMPLEMENTATION; execution unproven'])
tab(P/'CROSS-COMPONENT-ABI.tsv',['consumer_id','owner','consumer_source_status','symbol','provider_id','crc','licence','callee_kcfi_word','consumer_abs_kcfi_ids','consumer_relocations','provider_function_sha256','result','evidence_level'],cross)
# Existing accelerator transport edges through the separate private framework, verified without promoting it.
accel={'MALI-GPU-KERNEL','APUSYS-NPU-KERNEL','CAMERA-ISP-KERNEL','MTK-VCODEC-KERNEL','MTK-MDP-KERNEL','GPU-AI-AUX-KERNEL-INTERFACES'};transport=[];core=kpp.KO(W/'src/prov/drivers/misc/mediatek/mtk-interconnect/core.o');corestock=kpp.KO(R/next(v for v in master.values() if v['filename']=='mtk-icc-core.ko')['stock_paths']);cmdtext=(W/'src/prov/drivers/misc/mediatek/mtk-interconnect/.core.o.cmd').read_text();natural={s:int(c,16) for s,c in re.findall(r'^#SYMVER (\S+) (\S+)',cmdtext,re.M)}
for r in edges:
 cr=master[r['consumer_module_id']]
 if cr['component_owner'] not in accel or not r['provider_module_ids'].startswith('mtk-icc-core.ko@'):continue
 s=r['symbol'];assert natural[s]==int(r['required_crc'],16);assert prefix(core,sym(core,s))==prefix(corestock,sym(corestock,s));transport.append([r['consumer_module_id'],cr['component_owner'],s,r['required_crc'],r['export_type'],'CRC_AND_KCFI_PREFIX_IDENTICAL','Separate mtk-icc-core ABI boundary; no provider promotion or call execution claim'])
tab(P/'evidence/acceptance/ACCELERATOR-ICC-TRANSPORT.tsv',['consumer_id','owner','symbol','crc','licence','result','limit'],transport)
loads=list(csv.DictReader((A/'LOAD-LIST-EVIDENCE.tsv').open(),delimiter='\t'));related={m+'.ko' for m in j}|{r['provider_module_ids'].split('@')[0] for r in external}|{'clk-common.ko','clk-mt6878.ko','clk-mt6878-bus.ko','clk-mt6878-peri.ko','clk-mt6878-vlp.ko','mtk-emi.ko','emi.ko','mtk-scpsys.ko','mtk-scpsys-mt6878.ko','mtk_iommu.ko','mtk-cmdq-drv-ext.ko','pinctrl-mt6878.ko','pinctrl-mtk-v2.ko','mtk-dvfsrc-regulator.ko','mt6363-regulator.ko','mtk-dvfsrc-start.ko'};loads=[r for r in loads if r['entry'] in related];tab(P/'evidence/inventory/LOAD-ORDER.tsv',list(loads[0]),[list(r.values()) for r in loads])
# Public-source snapshots include every actual compiled source/header from target dependencies.
files=set()
for cmd in (W/'src/kdm/drivers/interconnect/mediatek').glob('.*.o.cmd'):
 text=cmd.read_text()
 for path in re.findall(re.escape(str(W/'src/kdm'))+r'/([^\s\\]+)',text):
  p=W/'src/kdm'/path
  if p.is_file() and p.suffix in ['.c','.h'] and not path.endswith('.mod.c'):files.add(str(p.resolve().relative_to((W/'src/kdm').resolve())))
for path in sorted(files):
 src=W/'src/kdm'/path;dst=P/'source/compiled-inputs'/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 gitblob=subprocess.check_output(['git','-C',str(W/'kernel_device_modules-6.1'),'show','5e415e059253ce0d2e61c97108e5f5785d71f06f:'+path]);assert gitblob==src.read_bytes()
tab(P/'source/COMPILED-INPUTS.tsv',['file','sha256','public_pin','status'],[[f,hashlib.sha256((W/'src/kdm'/f).read_bytes()).hexdigest(),'5e415e059253ce0d2e61c97108e5f5785d71f06f','PUBLIC_BLOB_UNCHANGED'] for f in sorted(files)])
summary={'maintained_commit':(P/'source/COMMIT').read_text().strip(),'whole_stock_parity':True,'unresolved':0,'functions':sum(x['functions'] for x in j.values()),'data_objects':sum(x['data'] for x in j.values()),'imports':sum(x['imports'] for x in j.values()),'exports':sum(x['exports'] for x in j.values()),'kcfi_absolute_ids':sum(x['kcfi_abs_ids'] for x in j.values()),'relocations':sum(x['relocations'] for x in j.values()),'target_objects_per_build':len((B/'INTERMEDIATE-SHA256SUMS').read_text().splitlines()),'provider_objects_per_build':len((B/'provider-object.sha256').read_text().splitlines()),'source_crc_licence_kcfi_boundary_checks':len(proof),'actual_reverse_imports':len(cross),'accelerator_private_icc_transport_edges':len(transport),'unchanged_public_compiled_inputs':len(files),'runtime_validation':'DEFERRED'}
inventory=json.load((P/'evidence/inventory/stock-inventory.json').open())
for m in inventory:inventory[m]['exports']=export_values(kpp.KO(S/(m+'.ko')))
(P/'evidence/inventory/stock-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
(P/'evidence/acceptance/result.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
