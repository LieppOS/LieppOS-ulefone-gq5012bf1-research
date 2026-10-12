#!/usr/bin/env python3
from pathlib import Path
import subprocess,os,json
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];S=P.parents[2].parent/'android_kernel_modules_camera_aux_ulefone_gq5012bf1';T=Path('/home/armol/kernel-work/g-source-recovery-batch-02/camera-nkm-layouts-correct');assert not T.exists();T.mkdir();subprocess.run(['git','init','-q',str(T)],check=True);paths=[]
for name in ['gc16b3c','gc16b3ctxd','imx882','imx882txd']:
 p='mtkcam/cam_cal/src_v4l2/custom/layout/'+name+'_mtk_eeprom.c';b=subprocess.check_output(['git','--git-dir=/home/armol/kernel-work/public-mtk/nkm.git','show','5f75a3b13e8135d45b4b0b70ec893345144f70df:'+p]);f=T/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);paths.append(p)
subprocess.run(['git','-C',str(T),'add','-A'],check=True);subprocess.run(['git','-C',str(T),'commit','-qm','ExactoriginalNothing-onlysourcepaths'],check=True)
for p in paths:(T/p).unlink()
subprocess.run(['git','-C',str(T),'add','-A'],check=True);(S/'patches/nkm/0002-remove-authentic-Nothing-only-4-layout-source-units-per-GQ-source-list.patch').write_bytes(subprocess.check_output(['git','-C',str(T),'diff','--cached']))
(P/'evidence/camera-D2-partial-and-exact-layout-paths.json').write_text(json.dumps(dict(D1='Missing3providerPTslots; allsource compiledexceptprovider',D2='Genuineproviderflags corrected all4external slots andalltargetcompile/link; NKMcal4extraneousunits stillpresent',setup_failed='Guessed _cust filenameswrong; onlyuncommittednewscript failed; no stockchange. ExactimmutableGitpaths recovered _mtk',source_deletions=paths,classification='NoAclaimedfromD1D2; originalproviderclasses preserved'),indent=2)+'\n');print('Actual4Nothing-onlyoriginalsourceunits omittedin GQ; correctsourcepathpatchpreserved')
