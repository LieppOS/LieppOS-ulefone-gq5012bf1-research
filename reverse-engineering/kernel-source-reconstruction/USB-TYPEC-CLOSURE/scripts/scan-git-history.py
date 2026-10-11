#!/usr/bin/env python3
"""Immutable authentic revision candidates, read-only Git object extraction.
Compare natural hashes with the proven baseline dependency shape; never synthesize tokens.
"""
from pathlib import Path
import subprocess,tempfile,json,ctypes,hashlib
P=Path(__file__).resolve().parents[1];W=Path('/home/armol/kernel-work/usb-typec-closure-01');lib=ctypes.CDLL(str(W/'sumversion-probe.so'));lib.hash_paths.argtypes=[ctypes.POINTER(ctypes.c_char_p),ctypes.c_char_p]
repos=[Path('/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1')]+list(Path('/home/armol/kernel-work/vendor-reference').glob('MiCode*'))+[W/'kernel_device_modules-6.1']
plans={'charger_class':('drivers/power/supply',['charger_class.c','charger_class.h'],'E4A92CD3F20A3D2142F16B6'),'mtk_chg_type_det':('drivers/power/supply',['mtk_chg_type_det.c','mtk_charger.h','charger_class.h','adapter_class.h','mtk_charger_algorithm_class.h','mtk_smartcharging.h'],'F7A2E5433A38379D631644F'),'rt_pd_manager':('drivers/misc/mediatek/typec/tcpc',['rt_pd_manager.c'],'C4301583FE25F39BA52E75D')}
results=[];seen={}
with tempfile.TemporaryDirectory(prefix='authentic-srcversion-history-',dir=W) as td:
 for repo in repos:
  if not (repo/'.git').exists():continue
  for n,(directory,names,expected) in plans.items():
   commits=subprocess.check_output(['git','-C',str(repo),'log','--all','--format=%H','--',*[directory+'/'+f for f in names]],text=True).splitlines()
   for commit in commits:
    blobs=[]
    for f in names:
     p=subprocess.run(['git','-C',str(repo),'show',commit+':'+directory+'/'+f],capture_output=True)
     if p.returncode:break
     blobs.append(p.stdout)
    if len(blobs)!=len(names):continue
    sig=tuple(hashlib.sha256(b).hexdigest() for b in blobs)
    ref={'repository':str(repo),'commit':commit,'paths':[directory+'/'+f for f in names]}
    if (n,sig) in seen:seen[(n,sig)]['additional_git_references'].append(ref);continue
    ps=[]
    for i,b in enumerate(blobs):
     p=Path(td)/f'input-{i}';p.write_bytes(b);ps.append(p)
    ar=(ctypes.c_char_p*(len(ps)+1))(*[str(p).encode() for p in ps],None);out=ctypes.create_string_buffer(25);lib.hash_paths(ar,out);s=out.value.decode();row={'module':n,'reference':ref,'input_sha256':sig,'natural_srcversion_under_verified_dependency_order':s,'stock_srcversion':expected,'stock_match':s==expected,'additional_git_references':[],'limit':'Authentic Git objects, but candidate compiler dependency graph and stock behavior require separate validation; no new source acceptance from hashes alone'};seen[(n,sig)]=row;results.append(row)
(P/'evidence/srcversion/immutable-history-scan.json').write_text(json.dumps(results,indent=2)+'\n');print('Authentic immutable historical sets',len(results),'stock matches',[(r['module'],r['reference']) for r in results if r['stock_match']])
