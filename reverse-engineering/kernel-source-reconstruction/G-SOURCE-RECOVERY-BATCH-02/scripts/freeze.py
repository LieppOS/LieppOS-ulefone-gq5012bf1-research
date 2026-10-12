#!/usr/bin/env python3
"""Read-only canonical/owner inspection; exact identity freeze before source work."""
from pathlib import Path
import csv,json,subprocess,hashlib,os,collections,re
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent;C=ROOT/'ulefone-gq5012bf1-research';old=ROOT/'ulefone-gq5012bf1-research-codex-g-source/reverse-engineering/kernel-source-reconstruction/G-SOURCE-RECOVERY-BATCH-01';E=P/'evidence';tab=lambda p:list(csv.DictReader(p.open(),delimiter='\t'));sha=lambda b:hashlib.sha256(b).hexdigest();by={r['filename']:r for r in tab(C/'reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv')};prior={r['filename']:r for r in tab(old/'G-REMAINING-INVENTORY.tsv')};ex=tab(P/'OWNERSHIP-EXCLUSIONS.tsv');excluded={r['module_id'] for r in ex};targets={'board_io':['extdev_io_class.ko','rt5133-regulator.ko','spi-mt65xx.ko','leds-rgb-aw2013.ko','yft_gpio_keys.ko'],'camera_aux':['aw36515.ko','aw36518.ko','aw36518_v2.ko','camera_eeprom_v4l2.ko'],'biometric_transport':['fingerprint.ko','microarray_fp_tee.ko','tkcore_drv.ko']};rows=[]
for family,names in targets.items():
 for n in names:
  a=by[n];h=prior[n];assert a['source_status']=='G' and a['module_id'] not in excluded
  f=R/a['stock_paths'].split(';')[0];b=f.read_bytes();assert sha(b)==a['stock_sha256'] and len(b)==int(a['stock_size'])
  source=h['public_source_candidate'];rev=h['public_revision'];confidence='PINNED_ALPS_COMPLETE_NO_C_DELTA_EXPECTED';rationale='CompleteALPSKbuild/header target, historicwholeparity; sharedsource/provider graph'
  if n=='leds-rgb-aw2013.ko':source='GKI drivers/leds/leds-aw2013.c + historicaldocumentedODMdelta';rev='6b18f0b574ab3267615ae6ce642d5a7c3c21ac09';confidence='EXACT_GKI_DONOR_PLUS_RECOVERED_C_DELTA';rationale='Publicupstreamdriver/completeGPL reconstructedC; independentlyverify allmetadata andlayout'
  elif n=='yft_gpio_keys.ko':source='GKI drivers/input/keyboard/gpio_keys.c + documentedsevenlineYFTdelta';rev='6b18f0b574ab3267615ae6ce642d5a7c3c21ac09';confidence='EXACT_GKI_DONOR_PLUS_RECOVERED_C_DELTA';rationale='Directcomplete23functionfamily; includeallYFTdata/metadata source changes'
  elif n.startswith('aw365'):source='MotorolaMobilityLLC/kernel-mtk flashlight AW36518 family + savedODM source delta';rev='ecf0e8f4448b5464d80c5dcd13b7573e9b2d39de';confidence='PUBLIC_FAMILY_SOURCE_PLUS_DOCUMENTED_ODM_C_DELTA';rationale='3coherentflashconsumers; existingfullC/header sources; rejectresiduals instead ofnewexceptions'
  elif n=='camera_eeprom_v4l2.ko':source='NothingOSS/android_kernel_modules_nothing_mt6878 mtkcam/cam_cal + recoveredODM14units';rev='5f75a3b13e8135d45b4b0b70ec893345144f70df';confidence='COMPLETE_PUBLIC_NKM_PLUS_RECOVERED_ODM_SOURCES_PROVENANCE_REVIEW';rationale='Onecompletecomposite, no calibration/blobtabletransplants; naturalGKIimports'
  elif n=='microarray_fp_tee.ko':source='HelloVolla/UT-kernel-volla-mt6768 MicroArrayv4.0.06 + recoveredODMdelta';rev='981578e37858_FULL_COMMIT_TO_RESOLVE';confidence='PUBLIC_FAMILY_PLUS_COMPLETE_ODM_C_TWO_UNITS';rationale='ConsumerofselectedSPI/fingerprint and existingCtkcore; sourcebuiltprovideronly'
  elif n=='tkcore_drv.ko':source='Ozobot/anvil-kernel publicTrustKernel subtree + documentedolderrelease armtzdelta';rev='ff290548332880265d6bc920b1fb8011959db54e_LOCAL_PUBLIC_IMPORT';confidence='PUBLIC44_FILE_SOURCE_PLUS_RELEASE_DELTA_PROVIDER_C_GAP_PRESERVED';rationale='Complete50function4TUbackend; srcversion/privatecontextABIresiduals mustnotbehidden'
  elif n=='fingerprint.ko':source='HistoricalcompleteYFTnormalworldplatformglueC; exactliteralOEMsourceunavailable';rev='a56d3d54167dd9e39a8734839fcd430fdfee8f76_RESEARCH_ARCHIVE_NOT_OEM_RELEASE';confidence='RECONSTRUCTED_C_NO_PUBLIC_LITERAL_LINEAGE_PROVENANCE_GAP';rationale='EssentialunownedGproducerforselectedMicroarray; boundedfullsource/provenancecheck, preserveG/Cifauthenticinputgatefails'
  rows.append(dict(module_id=a['module_id'],filename=n,stock_paths=a['stock_paths'],partitions=a['partitions'],stock_sha256=a['stock_sha256'],stock_size=a['stock_size'],original_category='G',subsystem=family,public_source_candidate=source,source_revision=rev,maintained_owner='CODEX:G-SOURCE-RECOVERY-BATCH-02:'+family,dependency_group=family,expected_compiler_inputs='GKI6b18f0/ALPS5e415e/config957dac/Clang7775eb; independentstockKconfig/LTO_NONE/faddrsig/GNU20only',source_recovery_confidence=confidence,selection_rationale=rationale,historical_source_path=h['historical_source_path'],existing_source_owner=a['source_owner']))
assert len(rows)==12 and len({r['module_id'] for r in rows})==12
# Fail if a new Claude manifest now includes any frozen target. Existing certified batches are not reused.
worktrees=subprocess.check_output(['git','-C',str(C),'worktree','list','--porcelain'],text=True);collisions=[]
for block in worktrees.split('\n\n'):
 if 'refs/heads/claude/' not in block:continue
 w=next((Path(l[9:]) for l in block.splitlines() if l.startswith('worktree ')),None)
 if not w:continue
 for f in (w/'reverse-engineering/kernel-source-reconstruction').glob('*/BATCH-MANIFEST.tsv'):
  t=tab(f)
  for x in t:
   identity=x.get('module_id',x.get('identity_key',''));s=x.get('stock_sha256','')
   if identity in {r['module_id'] for r in rows} or s and s in {r['stock_sha256'] for r in rows}:collisions.append(str(f)+':'+identity)
assert not collisions,collisions
f=P/'BATCH-MANIFEST.tsv';assert not f.exists(),'Immutablemanifest already frozen'
with f.open('w') as o:w=csv.DictWriter(o,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
(P/'BATCH-MANIFEST.sha256').write_text(sha(f.read_bytes())+'  BATCH-MANIFEST.tsv\n');state=dict(phase='FROZEN12_BEFORE_SOURCE_CHANGES',baseline_head=subprocess.check_output(['git','-C',str(C),'rev-parse','HEAD'],text=True).strip(),canonical_counts=dict(collections.Counter(r['source_status'] for r in by.values())),canonical_certified=391,completed_Batch01_unmerged22A1C=True,completed_Claude5_already_integrated=True,effective_certified=413,manifest_sha256=sha(f.read_bytes()),selected12=[r['module_id'] for r in rows],excluded8Claude=[r['module_id'] for r in ex if r['owner']=='CLAUDE:DISPLAY8_RESERVED'],processed=0,new_certifications=0,targets={r['module_id']:dict(status='G_FROZEN_NOT_CERTIFIED',family=r['subsystem'],source_confidence=r['source_recovery_confidence']) for r in rows},resource_policy='4CPUs/JOBS4/nice10/min20GiBfree/no cleanup; compactsharedimmutableinputs but freshindependent perproofbootstrap')
(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n');(E/'freeze-owner-check.txt').write_text(worktrees+'\nNO_CLAUDE_IDENTITY_HASH_COLLISIONS;8reserved+2extradisplayexcluded; sourcechangesnotstarted\n')
print('FROZEN12',sha(f.read_bytes()),collections.Counter(r['subsystem'] for r in rows))
