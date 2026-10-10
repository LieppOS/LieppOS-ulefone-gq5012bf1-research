#!/usr/bin/env python3
"""Record genuine recursive genksyms type graphs for the four unaccepted CMDQ modules."""
from pathlib import Path
import subprocess,os,shutil,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[2];N=R.parent/'android_kernel_modules_power_platform_ulefone_gq5012bf1';W=Path('/home/armol/kernel-work/platform-batch-01-dev');T=W/'src/kdm';O=P/'CMDQ-MAILBOX/evidence/type-investigation';O.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,COMMON=str(W/'common'),KO=str(W/'kout'),KDM_DIR=str(T),PATH=str(W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin')+':'+os.environ['PATH'])
goals=['cmdq_sec_mtee','cmdq-sec-mailbox','cmdq-sec-helper','mtk-cmdq-mailbox-ext','mtk-cmdq-helper-ext','cmdq-util','cmdq-test','cmdq-platform-mt6878']
# Force actual compilation: changing only the genksyms (-T) flag is not a CC cache key.
for m in goals:
 (T/'drivers/misc/mediatek/cmdq/mailbox'/(m+'.o')).unlink(missing_ok=True)
p=subprocess.run(['bash',str(N/'scripts/kb.sh'),'-j8','KBUILD_SYMTYPES=1']+['drivers/misc/mediatek/cmdq/mailbox/'+m+'.o' for m in goals],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(O/'symtypes-build.log').write_text(p.stdout);assert p.returncode==0,p.stdout[-1500:]
files=list((T/'drivers/misc/mediatek/cmdq/mailbox').glob('*.symtypes'))
for f in files:shutil.copyfile(f,O/f.name)
# Preserve public alternative investigation: both candidate pins have identical CMDQ headers.
paths=['include/linux/mailbox/mtk-cmdq-mailbox-ext.h','include/linux/soc/mediatek/mtk-cmdq-ext.h','drivers/misc/mediatek/cmdq/mailbox/cmdq-util.h','drivers/misc/mediatek/cmdq/mailbox/cmdq-sec.h'];same=[]
for f in paths:
 a=subprocess.check_output(['git','-C',str(W/'kernel_device_modules-6.1'),'show','5e415e059253ce0d2e61c97108e5f5785d71f06f:'+f]);b=subprocess.check_output(['git','-C',str(W/'kernel_device_modules-6.1'),'show','957dac185efe46cbf6336b0fff9516d84c8cd78f:'+f]);same.append({'path':f,'alps_and_nothing_identical':a==b})
(O/'public-header-investigation.json').write_text(json.dumps({'alternatives':same,'generated_type_files':len(files),'stock_private_type_graph_available':False,'next_experiment':'Compare preserved recursive genksyms graphs (cmdq_client/cmdq_util_platform_fp and secure pkt branches) against an OEM-matching header or additional preserved public revision. Recompile full drivers after a justified declaration change, verify all 23 export CRCs plus four consumed boundaries, KCFI, counter symbols and full ELF. Do not brute-force CRC bytes or patch __versions.'},indent=2)+'\n')
print('CMDQ recursive type files',len(files),'both public candidate headers identical; still not stock-ABI accepted')
