#!/usr/bin/env python3
"""Recover historical G lineage without executing mutable historical build scripts."""
from pathlib import Path
import subprocess,re,json,hashlib,csv
P=Path(__file__).resolve().parents[1];R=P.parents[2];B=R.parent;W=Path('/home/armol/kernel-work/platform-batch-01-dev');T=W/'kernel_device_modules-6.1';C=W/'common';pin='5e415e059253ce0d2e61c97108e5f5785d71f06f';common='6b18f0b574ab3267615ae6ce642d5a7c3c21ac09';proof=[]
paths=subprocess.check_output(['git','-C',str(T),'ls-tree','-r','--name-only',pin],text=True).splitlines();cp=subprocess.check_output(['git','-C',str(C),'ls-tree','-r','--name-only',common],text=True).splitlines()
for owner in ['MTK-MBOX','MTK-TINYSYS-IPI','MTK-RPMSG-MBOX']:
 S=B/'Reverse Engineer - DONE'/owner/'source'
 for f in sorted(S.iterdir()):
  if f.suffix not in ['.c','.h']:continue
  matches=[]
  for tree,rev,ls in [(T,pin,paths),(C,common,cp),(T,'957dac185efe46cbf6336b0fff9516d84c8cd78f',paths)]:
   for p in ls:
    if Path(p).name!=f.name:continue
    b=subprocess.check_output(['git','-C',str(tree),'show',rev+':'+p])
    if b==f.read_bytes():matches.append({'revision':rev,'path':p})
  proof.append({'historical_file':str(f.relative_to(B)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'immutable_public_matches':matches});assert matches,f
# Recover actual prior thermal implementation even though the old recipe needed /tmp envs.
old=Path('/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1')
for n in ['mtk_low_battery_throttling','pmic_lbat_service']:
 p='drivers/misc/mediatek/power_throttling/'+n+'.c';src=old/p;b=subprocess.check_output(['git','-C',str(T),'show',pin+':'+p]);assert src.exists(),src
 same=src.read_bytes()==b;proof.append({'historical_file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'immutable_public_matches':[{'revision':pin,'path':p}] if same else [],'requires_diff_investigation':not same});assert same,p
scripts=[]
for f in [B/'Reverse Engineer - DONE/MTK-TINYSYS-IPI/scripts/build-all.sh',B/'Reverse Engineer - DONE/MTK-RPMSG-MBOX/scripts/build-all.sh',R/'reverse-engineering/connectivity/scripts/rebuild_all.sh',R/'reverse-engineering/connectivity/scripts/build_kdm.sh']:
 scripts.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'hidden_inputs':'absolute mutable TinySys working tree/sb.sh/prepared GKI/provider symvers' if 'TinySys' in f.read_text() else '/tmp/connenv.sh or /tmp/ispenv.sh, mutable connectivity KDM/kout, camera stock-ext.symvers','replacement':'verified immutable ALPS/common/config/Clang, full fresh target/provider compilation, naturally regenerated CRC slots'})
E=P/'evidence/historical';E.mkdir(parents=True,exist_ok=True);(E/'source-recovery.json').write_text(json.dumps({'historical_files':proof,'historical_recipes':scripts,'result':'HISTORICAL_C_HEADER_FILES_RECOVERED_WITH_EXPLICIT_PUBLIC_REVISIONS','old_scripts_executed':False},indent=2)+'\n');print('Recovered',len(proof),'historical source/header files;4 recipe hidden-input boundaries eliminated')
