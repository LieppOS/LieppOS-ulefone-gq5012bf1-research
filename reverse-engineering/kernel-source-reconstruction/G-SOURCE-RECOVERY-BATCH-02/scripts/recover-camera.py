#!/usr/bin/env python3
from pathlib import Path
import subprocess,os,hashlib,csv,json,shutil,re
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2].parent;S=ROOT/'android_kernel_modules_camera_aux_ulefone_gq5012bf1';W=Path('/home/armol/kernel-work/g-source-recovery-batch-02');G=Path('/home/armol/kernel-work/gki-12901745-workspace');K=G/'kernel_device_modules-6.1';T=W/'camera-kdm-source-delta';assert not T.exists();T.mkdir();subprocess.run(['git','init','-q',str(T)],check=True);files={};records=[]
for name,filename in [('AW36515-FLASH','aw36515.c'),('AW36518-FLASH','aw36518.c'),('AW36518-V2-FLASH','aw36518_v2.c')]:
 d=ROOT/'Reverse Engineer - DONE'/name/'source';b=(d/filename).read_bytes();assert b'asm(' not in b and b'.incbin' not in b;dest='drivers/misc/mediatek/flashlight/flashlights/'+filename;files[dest]=b
 for f in d.glob('*.h'):files['drivers/misc/mediatek/flashlight/flashlights/'+f.name]=f.read_bytes()
 for f in (d.parent/'notes').glob('*reconstruction*.md'):a=S/'provenance'/name/f.name;a.parent.mkdir(parents=True,exist_ok=True);a.write_bytes(f.read_bytes())
 public=G/'lieppos/aw36518-recon/donor-build/aw36518.c';don=S/'source/public/aw36518-motorola-ecf0e8f4.c';don.parent.mkdir(parents=True,exist_ok=True);don.write_bytes(public.read_bytes());records.append(dict(path=dest,origin='Motorola kernel-mtk ecf0e8f4448b5464d80c5dcd13b7573e9b2d39de AW36518structuralfamily; boundedcompletepureCODMdelta',sha256=hashlib.sha256(b).hexdigest(),original_literal_OEM='NOT_CLAIMED',input_type='FULL_C_SOURCE_NOT_BINARY'))
# Genuine existingC provider source usedaswitnessonly; noCRCstocklinkrecords.
y=ROOT/'Reverse Engineer - PARTIAL/YFT-DEVINFO/source'
for f in y.iterdir():
 if f.is_file() and (f.suffix in ['.c','.h'] or f.name=='Makefile'):files['drivers/misc/mediatek/yft_devinfo/'+f.name]=f.read_bytes()
for p,b in files.items():f=T/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);d=S/'source/recovered'/p;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b)
# Baseline publicfiles inALPS that mustbe modified inadditionto newsource additions.
changed=['drivers/misc/mediatek/cam_cal/inc/cam_cal_format.h','drivers/misc/mediatek/imgsensor/inc/kd_imgsensor.h']
for p in changed:
 a=subprocess.check_output(['git','--git-dir=/home/armol/kernel-work/interconnect-pin-mirror/alps5e41.git','show','5e415e059253ce0d2e61c97108e5f5785d71f06f:'+p]);f=T/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(a)
# Snapshot justgenuine baselineexisting paths; staged additions are separatepatch below.
subprocess.run(['git','-C',str(T),'add',*changed],check=True);subprocess.run(['git','-C',str(T),'commit','-qm','Pinned originalALPS EEPROMinterface headers'],check=True)
for p,c in zip(changed,['f6e1549cef302829b9427699658f4d2749a00163','703d4733109391f0cb5c333954c284181a8a7971']):
 b=subprocess.check_output(['git','-C',str(K),'show',c+':'+p]);(T/p).write_bytes(b);d=S/'source/recovered'/p;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b);records.append(dict(path=p,origin='OriginalALPSheader + recoveredGQcalibration/sensoridentityCdelta '+c,sha256=hashlib.sha256(b).hexdigest(),original_literal_OEM='NOT_CLAIMED',input_type='FULL_H_SOURCE'))
# Originalflashlightfamily compileflags per TU, nofunctiondeclarations invented.
f=T/'drivers/misc/mediatek/flashlight/flashlights/Makefile';f.write_text('''# GPL-2.0; complete recoveredAWsource units\nccflags-y += -DCONFIG_MTK_FLASHLIGHT=1 -DCONFIG_MTK_FLASHLIGHT_DLPT=1\nCFLAGS_aw36515.o += -DCONFIG_MTK_FLASHLIGHT_PT=1\nobj-m += aw36515.o\nobj-m += aw36518.o\nobj-m += aw36518_v2.o\n''');subprocess.run(['git','-C',str(T),'add','-A'],check=True);patch=subprocess.check_output(['git','-C',str(T),'diff','--cached']);(S/'patches/source/0001-complete-camera-flash-ODM-source-calibration-interfaces-and-genuine-YFT-provider.patch').write_bytes(patch)
# Complete NKM public subtree andallsource deltas, not a transplantedcalibrationtable.
NM=Path('/home/armol/kernel-work/public-mtk/nkm.git');commit='5f75a3b13e8135d45b4b0b70ec893345144f70df';tree=subprocess.check_output(['git','--git-dir='+str(NM),'rev-parse',commit+'^{tree}'],text=True).strip();pins=list(csv.DictReader((S/'SOURCE-PINS.tsv').open(),delimiter='\t'));pins.append(dict(id='nkm',url='https://github.com/NothingOSS/android_kernel_modules_nothing_mt6878',commit=commit,subtree='.',tree_id=tree,branch_or_ref='mt6878/Tetris/u',role='Originalmtkcam cam_cal composite sources; othercamera/ISPtargets notowned'))
with (S/'SOURCE-PINS.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(pins[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(pins)
O=G/'lieppos/eeprom/trees/mtkcam';NT=W/'camera-nkm-delta';assert not NT.exists();NT.mkdir();subprocess.run(['git','init','-q',str(NT)],check=True)
# Materialize only sourcechangedcam_cal files; originalheadverified before sourcecomparison.
assert subprocess.check_output(['git','-C',str(O),'rev-parse','HEAD'],text=True).strip()=='133c6c15184a92aaee11d73800923d507ca0f9e8';ls=subprocess.check_output(['git','-C',str(O),'ls-tree','-r','--name-only','HEAD','cam_cal'],text=True).splitlines();new={}
for p in ls:
 b=subprocess.check_output(['git','-C',str(O),'show','HEAD:'+p]);a=subprocess.run(['git','--git-dir='+str(NM),'show',commit+':mtkcam/'+p],capture_output=True)
 if a.returncode==0:
  f=NT/('mtkcam/'+p);f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(a.stdout)
 new['mtkcam/'+p]=b
subprocess.run(['git','-C',str(NT),'add','-A'],check=True);subprocess.run(['git','-C',str(NT),'commit','-qm','AuthenticNKM cam_cal baseline'],check=True)
for p,b in new.items():
 f=NT/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);d=S/'source/nkm-recovered'/p;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b);records.append(dict(path=p,origin='NothingNKM5f75a3b + documented14ODM Cunits/privateABI delta at133c6c15184a92aaee11d73800923d507ca0f9e8',sha256=hashlib.sha256(b).hexdigest(),original_literal_OEM='DONOR_PLUS_RECONSTRUCTED_DELTA',input_type='COMPLETE_SOURCE_NO_BLOBTRANSPLANT'))
subprocess.run(['git','-C',str(NT),'add','-A'],check=True);(S/'patches/nkm').mkdir(exist_ok=True);(S/'patches/nkm/0001-authentic-NKM-cam-cal-plus-recovered-GQ5012BF1-ODM-source-delta.patch').write_bytes(subprocess.check_output(['git','-C',str(NT),'diff','--cached']))
with (S/'reference/SOURCE-LINEAGE.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(records)
# Actualpublicsource hash/copyright andhistorical14unitprovenance retained.
for f in (ROOT/'Reverse Engineer - DONE/CAMERA-EEPROMS/notes').glob('*'):
 if f.is_file() and f.name in ['yft-camera-eeprom-deltas.md','STATUS.md']:d=S/'provenance'/f.name;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(f.read_bytes())
(S/'README.md').write_text('# GQ5012BF1 camera auxiliaries\n\nFourownedGtargets:3AWflashlights and completeNKM cameraEEPROM composite. OriginalMotorolaGPLfamily/NKM5f75source plus explicitlyreconstructedODM C/header delta; completeunit/header/Kbuild/provenance/SHA preserved. No literaloriginalOEMtext claim; nocalibration/FWobject/tabletransplant. OriginalC YFTprovider wholeclassification unchanged; naturalcompiledexportonly. ThreeflashproviderexportsfromgenuineALPSflashlight composite. References comparisononly, notlinksymvers. Strictsourcebuild/B1B2/fullELFneeded beforeA; source/code/data/metadata residuals cannotbe waived.\n')
print('Recoveredcompletecamera4 sources,fullNKMcam_cal/sourcepatch,2authenticinterface deltas andsourceonlyproviders;othercamera sourceownershipunchanged')
