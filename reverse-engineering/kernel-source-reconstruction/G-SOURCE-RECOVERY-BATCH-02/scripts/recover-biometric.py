#!/usr/bin/env python3
"""CompletepublicTrustKernel/Microarray plus documented olderrelease/ODM source deltas."""
from pathlib import Path
import subprocess,os,csv,json,hashlib,shutil,re
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2].parent;S=ROOT/'android_kernel_modules_biometric_transport_ulefone_gq5012bf1';W=Path('/home/armol/kernel-work/g-source-recovery-batch-02');G=Path('/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1');T=W/'biometric-full-source';assert not T.exists();T.mkdir();subprocess.run(['git','init','-q',str(T)],check=True);records=[];SHA=lambda b:hashlib.sha256(b).hexdigest()
# Verify44originalpublicsourcefilehashes BEFORE sourcechanges, no stock/privatecompiledinputs.
importpin='ff290548332880265d6bc920b1fb8011959db54e';manifest=ROOT/'Reverse Engineer - DONE/TKCORE-DRV/source/donor-manifest.tsv';rows=list(csv.DictReader(manifest.open(),delimiter='\t'));print('publicmanifest fields',list(rows[0]))
publicfiles=subprocess.check_output(['git','-C',str(G),'ls-tree','-r','--name-only',importpin,'drivers/tee/tkcore'],text=True).splitlines()
for p in publicfiles:
 b=subprocess.check_output(['git','-C',str(G),'show',importpin+':'+p]);f=T/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);d=S/'source/public'/p;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b);records.append(dict(path=p,source='PublicTrustKernellocalimport'+importpin+';upstreamcontent6b94428fe0aae736e06693cda13bd284b88e93ed',sha256=SHA(b),role='ORIGINAL_GPL_INPUT'))
for r in rows:
 p=r.get('path',r.get('file'));expected=r.get('sha256');assert p and expected,r
 f=T/('drivers/tee/tkcore/'+p) if not p.startswith('drivers/') else T/p;assert SHA(f.read_bytes())==expected,(p,'PUBLIC_SOURCE_HASH_MISMATCH')
subprocess.run(['git','-C',str(T),'add','-A'],check=True);subprocess.run(['git','-C',str(T),'commit','-qm','Verified44originalpublicTrustKernelfiles'],check=True)
patch=ROOT/'Reverse Engineer - DONE/TKCORE-DRV/patches/0001-tkcore_drv-gq5012bf1-stock-6.1.1-delta-over-public-7.2.2.patch';subprocess.run(['git','-C',str(T),'apply','--index',str(patch)],check=True);(S/'provenance').mkdir(exist_ok=True);shutil.copyfile(patch,S/'provenance'/patch.name);shutil.copyfile(manifest,S/'provenance/donor-manifest.tsv');shutil.copyfile(ROOT/'Reverse Engineer - DONE/TKCORE-DRV/notes/source-lineage.md',S/'provenance/tkcore-source-lineage.md')
# Scopeengine traversesrootKbuild, then source-onlyproviders and genuineownedtargetcomposites.
md=ROOT/'Reverse Engineer - DONE/MICROARRAY-FP-TEE';orig=S/'source/microarray-public';orig.mkdir(parents=True);rc=S/'source/recovered';rc.mkdir(exist_ok=True)
for line in (md/'donor/donor-files.sha256').read_text().splitlines():
 sha,name=line.split();b=(md/'donor'/name).read_bytes();assert SHA(b)==sha; (orig/name).write_bytes(b);records.append(dict(path='MicroArray/'+name,source='HelloVolla UT-kernel-volla-mt6768 981578e37858 publicfamily/contentpin; exactfullGitcommitnotlocallyavailable',sha256=sha,role='ORIGINAL_GPL_INPUT_CONTENT_VERIFIED'))
for d,dest in [(md/'source','drivers/input/fingerprint/microarray'),(ROOT/'Reverse Engineer - DONE/FINGERPRINT-PLATFORM-SHIM/source','drivers/input/fingerprint/lieppos')]:
 for f in d.iterdir():
  if f.is_file() and (f.suffix in ['.c','.h'] or f.name=='Makefile'):
   b=f.read_bytes();assert b'.incbin' not in b and b'asm(' not in b;out=T/dest/f.name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);rr=rc/dest/f.name;rr.parent.mkdir(parents=True,exist_ok=True);rr.write_bytes(b);records.append(dict(path=dest+'/'+f.name,source='CompleteGPL donor+documentedODMdelta' if 'microarray' in dest else 'Completehistoricalstock-provenYFTglueC; literalOEMsourceunknown; provenancegapexplicit',sha256=SHA(b),role='COMPLETE_RECONSTRUCTED_C_H_NOT_BINARY'))
shutil.copyfile(md/'README.md',S/'provenance/MICROARRAY-README.md')
# Fullpublicsubtree is a sourceadditiontoALPS. Materialize completepatchedsources;
# stock sourceversion/naturalCRCs notchanged/waived iforiginalprivategeneration differs.
for f in (T/'drivers/tee/tkcore').rglob('*'):
 if f.is_file():out=rc/f.relative_to(T);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(f.read_bytes())
# Take newsourceaddition patchagainstemptybaseline: ALPScontainsno tkcoreorownedOEMtargets.
subprocess.run(['git','-C',str(T),'add','-A'],check=True);files=subprocess.check_output(['git','-C',str(T),'ls-files'],text=True).splitlines();Q=W/'biometric-source-additions';Q.mkdir();subprocess.run(['git','init','-q',str(Q)],check=True);subprocess.run(['git','-C',str(Q),'commit','--allow-empty','-qm','EmptyALPSvendoradditionbase'],check=True)
for p in files:f=Q/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((T/p).read_bytes())
# NewtraversalMakefiles onlyroutegenuineC units; GPL sourceMakefiles retained.
f=Q/'drivers/tee/tkcore/armtz/Makefile';f.write_text(f.read_text()+'\nccflags-y += -DCONFIG_TRUSTKERNEL_TEE_FP_SUPPORT=1 -DCONFIG_TRUSTKERNEL_TEE_RPMB_SUPPORT=1\n');f=Q/'drivers/tee/tkcore/core/Makefile';f.write_text(f.read_text()+'\nccflags-y += -DCONFIG_TRUSTKERNEL_TEE_FP_SUPPORT=1 -DCONFIG_TRUSTKERNEL_TEE_RPMB_SUPPORT=1\n');subprocess.run(['git','-C',str(Q),'add','-A'],check=True);(S/'patches/source/0001-complete-original-public-TrustKernel-olderbackend-and-MicroArray-YFT-source.patch').write_bytes(subprocess.check_output(['git','-C',str(Q),'diff','--cached']))
# PublicFF-A implementation fromalreadymaintainedsecure_transport: sourceobject witnessonly.
u=json.loads((S/'reference/provider-build-units.json').read_text());u.pop('drivers/tee/ffa');u['drivers/misc/mediatek/trusted_mem']=['ffa_v10'];(S/'reference/provider-build-units.json').write_text(json.dumps(u,indent=2)+'\n')
with (S/'reference/SOURCE-LINEAGE.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(records)
(S/'README.md').write_text('# GQ5012BF1 normal-world biometric transport sources\n\nThreeownedGidentities: YFTfingerprintglue, two-TU MicroArrayv4.0.06, four-TU TrustKernelarmtz backend. Complete public44file TrustKernel/microarrayoriginalsource SHA/copyright and documentedC release/ODM patch preserved. LiteraloriginalYFTgluesource notfound; explicitlyreconstructedC notinventedpublicrevision. ExistingCtkcore provider andoutsideA FF-A/SPI are sourceobject ABIwitnessesonly, notcertifications. No stocksymvers, KCFI/CRC replacement, privatecontexttypingcoercion or forcedsrcversion. Any genuinefullmodule metadata/CRCgap staysC/G; strictGNU20 acceptanceunchanged. Firmware/secureTA notsourceclosed.\n')
print('Recovered3complete sourcecandidates/fullpublicdonorhashes/releasepatch,1explicitYFTprovenancegap; naturalpublicCprovider willnotbepatchedtofakeCRC')
