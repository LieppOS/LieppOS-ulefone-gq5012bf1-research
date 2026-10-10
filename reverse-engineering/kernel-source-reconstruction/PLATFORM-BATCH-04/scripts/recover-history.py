#!/usr/bin/env python3
"""Recover whole historical implementation and immutable TCPC31 before new RE."""
from pathlib import Path
import csv,json,subprocess,hashlib,tarfile,lzma,io,difflib,re,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[2];G=Path('/home/armol/kernel-work/gki-12901745-workspace');B=Path('/home/armol/kernel-work/platform-batch-03-cleancheck/ws/kernel_device_modules-6.1');O=G/'kernel_device_modules-6.1';U=G/'lieppos/usb/trees/5e41';C=R.parent/'Reverse Engineer - DONE/TCPC-CLASS/source';V=Path('/home/armol/kernel-work/vendor-reference/MiCode-MTK-kernel-device-modules-chagall-2.0.31');REV='5e415e059253ce0d2e61c97108e5f5785d71f06f';TCPC='drivers/misc/mediatek/typec/tcpc';vrev='2d6f27aa19d521409f443c8d821e2d475bdc72b6';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=V,text=True).strip()==vrev
E=P/'evidence/historical';E.mkdir(parents=True,exist_ok=True);S=E/'whole-source';S.mkdir(exist_ok=True);mapunits={}
def add(m,d,units):mapunits[m]={'directory':d,'objects':units.split()}
power='drivers/power/supply'
for m in ['adapter_class','charger_class','mtk_charger_algorithm_class','mtk_chg_type_det','mtk_pd_adapter','mt6375-charger']:add(m,power,m+'.o')
add('mtk_charger_framework',power,'mtk_charger.o mtk_charger_intf.o mtk_basic_charger.o mtk_pulse_charger.o mtk_adapter_switch.o');add('mtk_pd_charging',power,'mtk_pd.o mtk_pd_hal.o')
for m,stem in [('mtk_pep','mtk_pe'),('mtk_pep40','mtk_pe4'),('mtk_pep50','mtk_pe5')]:add(m,power,stem+'.o '+stem+'_hal.o')
add('mt6375-battery',power,'mtk_battery_coulomb_service.o mtk_battery.o mtk_battery_algo.o mt6375-gauge.o mtk_battery_daemon.o')
for m in ['mt6375-adc','mt6375-auxadc']:add(m,'drivers/iio/adc',m+'.o')
mk=(C/'Makefile').read_text();section=mk.split('tcpc_class-objs :=',1)[1].split('# Reproduce',1)[0];objs=re.findall(r'\b[\w-]+\.o\b',section);assert len(objs)==34;add('tcpc_class',TCPC,' '.join(objs))
for m in ['tcpc_mt6375','pd_dbg_info','rt_pd_manager','tcpci_late_sync']:add(m,TCPC,m+'.o')
add('mux_switch','drivers/misc/mediatek/typec/mux','mux_switch.o')
usb={
'mtu3':('drivers/usb/mtu3','mtu3_plat.o mtu3_trace.o mtu3_host.o mtu3_core.o mtu3_gadget_ep0.o mtu3_gadget.o mtu3_qmu.o mtu3_dr.o mtu3_debugfs.o'),
'xhci-mtk-hcd-v2':('drivers/misc/mediatek/usb/usb_xhci','xhci.o xhci-mem.o xhci-ext-caps.o xhci-ring.o xhci-hub.o xhci-dbg.o xhci-trace.o xhci-mtk.o xhci-mtk-sch.o quirks.o xhci-debugfs.o'),
'phy-mtk-xsphy':('drivers/phy/mediatek','phy-mtk-xsphy.o'),'extcon-mtk-usb':('drivers/misc/mediatek/extcon','extcon-mtk-usb.o'),
'usb_meta':('drivers/misc/mediatek/usb/usb_meta','usb_meta.o'),'usb_boost':('drivers/misc/mediatek/usb/usb_boost','usb_boost_common.o usb_boost_plat.o'),
'usb_logger':('drivers/misc/mediatek/usb/usb_logger','u_logger.o u_logger_trace.o'),'mtk_u_ether':('drivers/misc/mediatek/usb/usb_rndis','u_ether.o'),
'mtk_usb_f_rndis':('drivers/misc/mediatek/usb/usb_rndis','f_rndis.o rndis.o'),'usb_offload':('drivers/misc/mediatek/usb/usb_offload','usb_offload_common.o usb_offload_mem.o')}
for m,(d,objs) in usb.items():add(m,d,objs)
rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));assert set(mapunits)=={r['filename'].removesuffix('.ko') for r in rows};(E/'compiled-unit-plan.json').write_text(json.dumps(mapunits,indent=2)+'\n')
basepaths=subprocess.check_output(['git','ls-tree','-r','--name-only',REV],cwd=B,text=True).splitlines();base={};sources={}
for m,v in mapunits.items():
 d=v['directory']
 for obj in v['objects']:
  p=d+'/'+obj.removesuffix('.o')+'.c';f=(C/Path(p).name if d==TCPC else U/p if m in usb or m=='mux_switch' else O/p)
  if m=='tcpc_mt6375':f=R.parent/'Reverse Engineer - DONE/TCPC-MT6375/source/tcpc_mt6375.c'
  if m=='pd_dbg_info':f=R.parent/'Reverse Engineer - DONE/PD-DBG-INFO/source/pd_dbg_info.c'
  if m in ['rt_pd_manager','tcpci_late_sync']:f=U/p
  assert f.exists(),f;sources[p]=f
# Recover actual shared type headers. Power comes from fully modified charger tree;
# TCPC header set comes from preserved2.0.31 implementation, not old public2.0.30.
for p in basepaths:
 if p.startswith(power+'/') and p.endswith('.h') and (O/p).exists():sources[p]=O/p
for d in {v['directory'] for m,v in mapunits.items() if m in usb or m=='mux_switch'}:
 for p in basepaths:
  if p.startswith(d+'/') and p.endswith('.h') and (U/p).exists():sources[p]=U/p
for f in C.glob('*.h'):
 candidates=[p for p in basepaths if p.startswith(TCPC+'/') and Path(p).name==f.name]
 if candidates:assert len(candidates)==1;sources[candidates[0]]=f
proof=[];patch='';tcpc_base={}
# Pin public TCPC subtree as an exact recoverable source archive; it includes its own
# Kbuild/Kconfig and all genuine C/H. No public target objects enter the archive.
raw=subprocess.check_output(['git','archive',vrev+':'+TCPC],cwd=V);(E/'tcpc31-public.tar.xz').write_bytes(lzma.compress(raw));tree=subprocess.check_output(['git','rev-parse',vrev+':'+TCPC],cwd=V,text=True).strip()
for member in tarfile.open(fileobj=io.BytesIO(raw)):
 if member.isfile():tcpc_base[TCPC+'/'+member.name]=tarfile.open(fileobj=io.BytesIO(raw)).extractfile(member).read()
for p,f in sorted(sources.items()):
 b=f.read_bytes();target=S/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
 orig=tcpc_base[p] if p.startswith(TCPC+'/') else subprocess.check_output(['git','show',REV+':'+p],cwd=B)
 same=b==orig;proof.append({'target_path':p,'historical_path':str(f),'historical_sha256':hashlib.sha256(b).hexdigest(),'base_revision':vrev if p.startswith(TCPC+'/') else REV,'base_sha256':hashlib.sha256(orig).hexdigest(),'identical_to_public':same})
 if not same:patch+=''.join(difflib.unified_diff(orig.decode().splitlines(True),b.decode().splitlines(True),fromfile='a/'+p,tofile='b/'+p))
(E/'source-recovery.json').write_text(json.dumps(proof,indent=2)+'\n');(E/'complete-historical-source-deltas.patch').write_text(patch)
(E/'tcpc31-public-pin.json').write_text(json.dumps({'url':'https://github.com/MiCode/MTK_kernel_device_modules','commit':vrev,'subtree':TCPC,'tree_id':tree,'archive_sha256':hashlib.sha256((E/'tcpc31-public.tar.xz').read_bytes()).hexdigest(),'archive_format':'git archive commit:subtree tar then xz','upstream_branch':'bsp-chagall-w-oss','limits':'Public31 reference minus recovered OEM source patches; not automatically stock-exact; known historical699/707TCPC andsrcversion residuals retained'},indent=2)+'\n')
recipes=sorted({r['historical_build_script'] for r in rows if r['historical_build_script']!='UNKNOWN'});risks=[]
for p in recipes:
 f=R/p;assert f.exists();risks.append({'path':p,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'old_script_executed':False,'hidden_inputs':'Prepared/mutable camera-ISP or NFC/GKI workspaces; stock-harvested symvers; absolute private paths/config defines; source31 and reconstructed complete patches recovered first','replacement':'Immutable ALPS/common/toolchain/config, pinnedpublicTCPC31source archive, full preserved source delta, fresh target/provider compilation with natural ABI generation'})
(E/'recipe-input-risks.json').write_text(json.dumps(risks,indent=2)+'\n');print('Recovered30 targets',len(proof),'whole C/H',sum(not p['identical_to_public'] for p in proof),'full changed files; publicTCPC31',vrev,tree)
