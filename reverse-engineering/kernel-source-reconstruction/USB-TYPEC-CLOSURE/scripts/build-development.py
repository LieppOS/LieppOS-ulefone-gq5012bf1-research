#!/usr/bin/env python3
"""Build isolated source experiment; keep raw logs and all target operands."""
from pathlib import Path
import subprocess, os, sys, json, hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[2]
N=R.parent/'android_kernel_modules_usb_typec_ulefone_gq5012bf1-usb-typec-closure'
W=Path('/home/armol/kernel-work/usb-typec-closure-01');T=W/'src/kdm';D=T/'drivers/misc/mediatek/typec/tcpc'
tag=sys.argv[1];O=W/'out'/tag;E=P/'evidence'/tag;O.mkdir(parents=True,exist_ok=True);E.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,COMMON=str(W/'common'),KO=str(W/'kout'),KDM_DIR=str(T),PYTHONDONTWRITEBYTECODE='1',TMPDIR='/tmp',KBUILD_BUILD_USER='lieppos',KBUILD_BUILD_HOST='platform-build',KBUILD_BUILD_VERSION='1',KBUILD_BUILD_TIMESTAMP='Thu Oct 8 12:00:00 UTC 2026')
clang=W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin';env['PATH']=str(clang)+os.pathsep+env['PATH']
# No change to source composition or provider CRC inputs.
cmd=['bash',str(N/'scripts/kb.sh'),'-k','-j12','KBUILD_EXTRA_SYMBOLS='+str(W/'out/baseline/provider/natural-external-provider.symvers'),'modules']
with (E/'modules.log').open('w') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
(E/'exit.json').write_text(json.dumps({'returncode':p.returncode,'command':cmd,'environment':{k:env[k] for k in ['COMMON','KO','KDM_DIR','KBUILD_BUILD_USER','KBUILD_BUILD_HOST','KBUILD_BUILD_VERSION','KBUILD_BUILD_TIMESTAMP']}} ,indent=2)+'\n')
assert p.returncode==0,'Build failure: see '+str(E/'modules.log')
rows=[]
for m in ['charger_class','mtk_chg_type_det','rt_pd_manager','tcpc_mt6375','tcpc_class']:
 paths=list(T.rglob(m+'.ko'));assert len(paths)==1,(m,paths)
 raw=O/(m+'.ko');raw.write_bytes(paths[0].read_bytes());stripped=O/(m+'.stripped')
 subprocess.run([str(clang/'llvm-strip'),'--strip-debug','-o',str(stripped),str(raw)],check=True)
 rows.append({'module':m,'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'stripped_sha256':hashlib.sha256(stripped.read_bytes()).hexdigest()})
(E/'module-sha256.json').write_text(json.dumps(rows,indent=2)+'\n')
# The Git index is the maintained pre-experiment source baseline.
files=['pd_policy_engine.c','tcpc_mt6375.c','pd_process_evt.c','tcpci_typec.c','tcpci_core.c','tcpci_alert.c','pd_process_evt_com.c','tcpci_event.c','pd_dpm_core.c','tcpci_timer.c','inc/tcpci_pd_config.h']
patch=subprocess.check_output(['git','-C',str(T),'diff','--']+['drivers/misc/mediatek/typec/tcpc/'+f for f in files],text=True)
(E/'source.patch').write_text(patch)
for f in files:
 dst=E/f;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((D/f).read_bytes())
print(tag,'build exit',p.returncode,'saved',len(rows),'modules',O)
