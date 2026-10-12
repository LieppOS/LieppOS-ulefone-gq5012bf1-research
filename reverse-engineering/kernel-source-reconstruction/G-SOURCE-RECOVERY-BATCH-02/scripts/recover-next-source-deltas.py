#!/usr/bin/env python3
from pathlib import Path
import subprocess,os,json,hashlib
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2].parent;W=Path('/home/armol/kernel-work/g-source-recovery-batch-02')
def patch(S,T,old,new,name):
 assert not T.exists();T.mkdir();subprocess.run(['git','init','-q',str(T)],check=True)
 for p,b in old.items():f=T/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 subprocess.run(['git','-C',str(T),'add','-A'],check=True);subprocess.run(['git','-C',str(T),'commit','-qm','Actualprevioussourceinput'],check=True)
 for p,b in new.items():(T/p).write_bytes(b)
 subprocess.run(['git','-C',str(T),'add','-A'],check=True);b=subprocess.check_output(['git','-C',str(T),'diff','--cached']);(S/'patches/source'/name).write_bytes(b)
S=ROOT/'android_kernel_modules_camera_aux_ulefone_gq5012bf1';old={};new={}
for owner,n in [('AW36518-FLASH','aw36518.c'),('AW36518-V2-FLASH','aw36518_v2.c')]:
 p='drivers/misc/mediatek/flashlight/flashlights/'+n;old[p]=(S/'source/recovered'/p).read_bytes();new[p]=(ROOT/'Reverse Engineer - DONE'/owner/'source/2026-10-04'/n).read_bytes();assert b'asm(' not in new[p] and b'.incbin' not in new[p];d=S/'source/late-corrections'/n;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(new[p])
patch(S,W/'camera-actual-late-correction',old,new,'0003-preserved-2026-10-04-complete-AW36518-family-source-corrections.patch')
S=ROOT/'android_kernel_modules_biometric_transport_ulefone_gq5012bf1';p='drivers/tee/tkcore/core/tee_supp_com.h';old={p:(S/'source/recovered'/p).read_bytes()};new={p:(S/'source/public'/p).read_bytes()};patch(S,W/'biometric-original-provider-header',old,new,'0002-retain-genuine-public-core-provider-RPC-declaration-not-backend-private-alias.patch')
(P/'evidence/late-source-correction-plan.json').write_text(json.dumps(dict(camera='Useactualpreserved2026-10-04completepure-Ccorrections, notrerunearlier13/23knowncandidate; no fakeB bodyproof. Remainingscheduling/objectorder residualhonestCifgatefails',biometric='Oldbackendpatchremovednewnamed_shm field while genuinelynewpublicprovider source stillreferencesit; restorepristinepublicproviderdeclaration. WholelegacyCRC/contextgapmuststayvisible; no forceoldtypegraph'),indent=2)+'\n');print('Two meaningfulsourcecorrections recovered fromexistingauthenticatedhistory/publicsource; no ELF modification')
