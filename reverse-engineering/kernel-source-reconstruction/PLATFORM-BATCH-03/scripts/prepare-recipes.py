#!/usr/bin/env python3
"""Reuse preserved offline engine; retain existing repository history and ownership."""
from pathlib import Path
import json,csv,shutil,subprocess,hashlib,difflib
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=R.parent;state=json.loads((P/'BATCH-STATE.json').read_text());base=W/'android_kernel_modules_memory_platform_ulefone_gq5012bf1';old=Path('/home/armol/kernel-work/gki-12901745-workspace/kernel_device_modules-6.1');T=Path('/home/armol/kernel-work/platform-batch-02-dev/kernel_device_modules-6.1');rev=state['source_pins']['alps'];E=P/'evidence/historical';E.mkdir(parents=True,exist_ok=True)
files=['drivers/thermal/mediatek/backlight_cooling.c','drivers/mfd/mtk-spmi-pmic.c','drivers/iio/adc/mtk-spmi-pmic-adc.c','drivers/mfd/mt6375.c','drivers/mfd/mt6685-core.c']+[str(f.relative_to(old)) for f in (old/'drivers/misc/mediatek/clkbuf').rglob('*') if f.is_file() and f.suffix in ['.c','.h']]
proof=[];patch=''
for p in files:
 b=subprocess.check_output(['git','show',rev+':'+p],cwd=T);f=old/p;assert f.exists();same=f.read_bytes()==b
 proof.append({'historical_path':str(f),'public_revision':rev,'public_path':p,'historical_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'public_sha256':hashlib.sha256(b).hexdigest(),'exact':same})
 if not same:
  assert p=='drivers/mfd/mt6375.c',p
  patch+=''.join(difflib.unified_diff(b.decode().splitlines(True),f.read_text().splitlines(True),fromfile='a/'+p,tofile='b/'+p))
(E/'source-recovery.json').write_text(json.dumps(proof,indent=2)+'\n');(E/'mt6375-historical-irq-delta.patch').write_text(patch)
recipepaths=[R/'reverse-engineering/audio/scripts/build_aud.sh',W/'Reverse Engineer - DONE/MT6375-CHARGER/scripts/build_b1_b2.sh',W/'Reverse Engineer - DONE/BACKLIGHT-DISPLAY-GLUE/scripts/glue.py',R/'reverse-engineering/connectivity/scripts/rebuild_all.sh',R/'reverse-engineering/connectivity/scripts/build_kdm.sh']
(E/'recipe-input-risks.json').write_text(json.dumps([{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'old_script_executed':False,'hidden_inputs':'Mutable GKI/vendor/isolated glue tree, /tmp environment, prepared camera/audio/connectivity output and stock-ext.symvers','replacement':'Immutable mirror and verified config, fresh target/provider compilation and source-derived slots'} for f in recipepaths],indent=2)+'\n')
rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'))
for family,name in state['repositories'].items():
 n=W/name;exists=n.exists();prev=None
 if exists:
  assert not subprocess.check_output(['git','status','--porcelain'],cwd=n,text=True);prev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=n,text=True).strip()
  prior=json.loads((n/'families/OWNERSHIP.json').read_text());(n/'reference/PRIOR-CERTIFIED-RECIPE.json').write_text(json.dumps({'commit':prev,'ownership':prior,'instruction':'git checkout exact prior commit to reproduce already certified Batch02; new joint engine is Batch03 only'},indent=2)+'\n')
 else:
  for d in ['scripts','reference','patches','families']:(n/d).mkdir(parents=True,exist_ok=True)
  for f in ['SOURCE-PINS.tsv','LICENSE']:shutil.copyfile(base/f,n/f)
  for f in ['gki-vmlinux.symvers.sha256','gki-12901745-vmlinux.symvers.xz','vendor-kout.config.sha256']:shutil.copyfile(base/'reference'/f,n/'reference'/f)
  subprocess.run(['git','init','-q',str(n)],check=True)
 for f in (base/'scripts').iterdir():
  if f.is_file():shutil.copyfile(f,n/'scripts'/f.name)
 for f in (n/'patches').glob('*.patch'):f.unlink()
 for f in ['kdm-tree.txt','stock-normalized.tsv','joint-stock-normalized.tsv','provider-boundaries.json','external-provider.symvers']:
  q=n/'reference'/f
  if q.exists():q.unlink()
 shutil.copyfile(P/'BATCH-MANIFEST.tsv',n/'reference/BATCH-MANIFEST.tsv');shutil.copyfile(E/'mt6375-historical-irq-delta.patch',n/'patches/0002-mt6375-historical-irq-ack.patch')
 (n/'families/OWNERSHIP.json').write_text(json.dumps({'family':family,'owned_modules':state['families'][family],'all_families':state['repositories'],'prior_certified_recipe_commit':prev,'joint_build_rationale':'Joint34 source-derived provider dependencies; other targets/witnesses not owned or automatically certified. Canonical component ownership unchanged.'},indent=2)+'\n')
 (n/'README.md').write_text(f'# {family} — GQ5012BF1 Batch03 maintained source\n\nScope:families/OWNERSHIP.json. Complete pinned public source retrieval, original\nlicenses, patches, generated headers/config/provider witnesses and full ELF acceptance.\nJoint34 build does not transfer ownership or certify external provider implementations.\nPrior Batch02 source recipe is preserved at exact commit in PRIOR-CERTIFIED-RECIPE.json\nwhere applicable; never amend its certified inputs.\n\nOffline:set LIEPPOS_IOMMU_MIRROR=/path/to/preserved/public/mirror and run\n`bash scripts/bootstrap.sh /space-free/ws`, `bash scripts/bulk-build.sh /space-free/ws B1`\nand B2. Each build freshly assembles target/provider source. Independent full validation\nin canonical PLATFORM-BATCH-03/BUILD-REPRODUCTION.md. No phone or push.\n')
 for f in (n/'scripts').glob('*.sh'):f.chmod(0o755)
print('Prepared five recipes; recovered',len(proof),'historical C/H;',sum(not x['exact'] for x in proof),'genuine historical delta')
