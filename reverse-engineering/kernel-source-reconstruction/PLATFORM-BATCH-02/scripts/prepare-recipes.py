#!/usr/bin/env python3
"""Reuse accepted engine without Batch01 patches/targets; own27 frozen identities only."""
from pathlib import Path
import csv,json,shutil,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=R.parent;base=W/'android_kernel_modules_power_platform_ulefone_gq5012bf1'
repos={'INTERCONNECT-MEMORY':'android_kernel_modules_memory_platform_ulefone_gq5012bf1','PMIF-SPMI':'android_kernel_modules_pmif_spmi_ulefone_gq5012bf1','MAILBOX-TINYSYS':'android_kernel_modules_mailbox_tinysys_ulefone_gq5012bf1','POWER-POLICY':'android_kernel_modules_power_policy_ulefone_gq5012bf1'};rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'))
for family,name in repos.items():
 n=W/name;assert not n.exists(),n
 shutil.copytree(base/'scripts',n/'scripts',ignore=shutil.ignore_patterns('__pycache__'));(n/'reference').mkdir();(n/'patches').mkdir();(n/'families').mkdir()
 for f in ['SOURCE-PINS.tsv','LICENSE']:shutil.copyfile(base/f,n/f)
 for f in ['gki-vmlinux.symvers.sha256','gki-12901745-vmlinux.symvers.xz','vendor-kout.config.sha256']:shutil.copyfile(base/'reference'/f,n/'reference'/f)
 shutil.copyfile(P/'BATCH-MANIFEST.tsv',n/'reference/BATCH-MANIFEST.tsv')
 (n/'families/OWNERSHIP.json').write_text(json.dumps({'family':family,'owned_modules':[r['filename'].removesuffix('.ko') for r in rows if r['dependency_group']==family],'all_families':repos,'joint_build_rationale':'Shared immutable public source/config; joint27 targets compiled as real providers. Scope does not transfer component ownership or certify provider-only modules.'},indent=2)+'\n')
 (n/'README.md').write_text(f'# {family} — GQ5012BF1 Batch02 maintained source\n\nOwned modules:families/OWNERSHIP.json. Complete public pins/patches and shared\n27-target/provider engine. Exact inherited base config/Clang/GKI verification.\nNo cached objects or stock bytes as implementation. Upstream GPL/SPDX retained.\nOther joint modules are witnesses, not owned or automatically certified.\nNo phone, firmware operation or push.\n\nOffline clean checkout: set LIEPPOS_IOMMU_MIRROR to preserved public mirror;\nrun scripts/bootstrap.sh /space-free/ws then scripts/bulk-build.sh /space-free/ws B1\nand B2 (each freshly assembles all target/provider source). See canonical research\nPLATFORM-BATCH-02/BUILD-REPRODUCTION.md for complete independent acceptance.\n')
 subprocess.run(['git','init','-q',str(n)],check=True)
print('Prepared four scoped recipes')
