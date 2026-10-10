#!/usr/bin/env python3
"""Prepare four scoped family recipes with identical shared batch build engine inputs."""
from pathlib import Path
import csv,json,shutil,subprocess,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=R.parent
base=W/'android_kernel_modules_iommu_ulefone_gq5012bf1'
rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'))
repos={'CMDQ-MAILBOX':'android_kernel_modules_cmdq_ulefone_gq5012bf1','IOMMU-AUX':'android_kernel_modules_iommu_aux_ulefone_gq5012bf1','SMI-PLATFORM':'android_kernel_modules_smi_platform_ulefone_gq5012bf1','MTK-POWER-PLATFORM':'android_kernel_modules_power_platform_ulefone_gq5012bf1'}
for family,name in repos.items():
 n=W/name;assert not n.exists(),f'Existing recipe must be reviewed, not overwritten:{n}'
 for d in ['scripts','reference','patches','families']:(n/d).mkdir(parents=True,exist_ok=True)
 for f in ['SOURCE-PINS.tsv']:shutil.copyfile(base/f,n/f)
 for f in ['bootstrap.sh','make-kout.sh','kb.sh','normalize.py','ko-pair-parity.py','verify.py','test-verify.py']:
  if (base/'scripts'/f).exists():shutil.copyfile(base/'scripts'/f,n/'scripts'/f)
 for f in ['gki-vmlinux.symvers.sha256','gki-12901745-vmlinux.symvers.xz','vendor-kout.config.sha256']:shutil.copyfile(base/'reference'/f,n/'reference'/f)
 # All35 are joint provider compile scope; only this family's manifest is an owned target list.
 shutil.copyfile(P/'BATCH-MANIFEST.tsv',n/'reference/BATCH-MANIFEST.tsv')
 (n/'families/OWNERSHIP.json').write_text(json.dumps({'family':family,'owned_modules':[r['filename'].removesuffix('.ko') for r in rows if r['dependency_group']==family],'all_families':repos,'joint_build_rationale':'One source/config/header/provider environment; other families are dependency witnesses, not this recipe\'s certified ownership.'},indent=2)+'\n')
 (n/'README.md').write_text(f'# {family} — GQ5012BF1 maintained source recipe\n\nCanonical component owners stay unchanged. This repository owns only the modules in\n`families/OWNERSHIP.json`; the frozen35-module joint Kbuild scope regenerates shared\nprovider witnesses in one compatible environment. Other joint-scope modules are not\ncertified by this repository alone. No binary source transplantation or firmware payloads.\n\nImmutable upstream pins:`SOURCE-PINS.tsv`. Offline input mirror required.\nCommon toolchain/config bootstrap is reused from the accepted IOMMU machinery; batch\nengine scope/provider/parity scripts are maintained here. Public C/headers retain their\nupstream GPL/SPDX licensing; local build/evidence scripts use GPL-2.0-only.\n\nDevelopment/fresh-clone reproduction: see batch `BUILD-REPRODUCTION.md`.\nStatus: source candidate recipe being compiled; no acceptance claimed yet.\n')
 (n/'LICENSE').write_text('Public kernel source is retrieved without relicensing from immutable upstream trees.\nSee each source file SPDX header and upstream COPYING (GPL-2.0). Local reconstruction\nbuild/evidence scripts are GPL-2.0-only. No proprietary firmware is included.\n')
 subprocess.run(['git','init','-q',str(n)],check=True)
print('Prepared',len(repos),'family recipes, no compilation yet')
