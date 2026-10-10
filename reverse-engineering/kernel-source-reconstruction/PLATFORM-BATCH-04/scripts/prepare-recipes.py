#!/usr/bin/env python3
"""Three subsystem recipes; exact full historical patches and pinnedpublicTCPC31."""
from pathlib import Path
import json,csv,subprocess,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[2];S=json.loads((P/'BATCH-STATE.json').read_text());E=P/'evidence/historical';base=R.parent/'android_kernel_modules_secure_diagnostics_ulefone_gq5012bf1';pin=json.loads((E/'tcpc31-public-pin.json').read_text())
providers={'drivers/misc/mediatek/adsp':['adsp_reserved_mem','adsp_core','adsp_platform_driver'],'drivers/misc/mediatek/aee/aed':['aee-common'],'drivers/misc/mediatek/audio_ipi/common':['audio_messenger_ipi'],'drivers/misc/mediatek/mtprof':['bootprof'],'drivers/iio/buffer':['industrialio-triggered-buffer'],'drivers/soc/mediatek':['mtk-dvfsrc'],'drivers/misc/mediatek/power_throttling':['pmic_lbat_service'],'sound/soc/mediatek/common':['mtk-usb-offload-ops'],'drivers/clk/mediatek':['clk-mtk'],'drivers/gpu/drm/mediatek/mediatek_v2':['mtk_disp_notify'],'drivers/misc/mediatek/dvfsrc':['dvfsrc-helper'],'drivers/misc/mediatek/scp/rv':['scp_helper'],'drivers/misc/mediatek/rps':['rps_perf']}
for family,name in S['repositories'].items():
 n=R.parent/name;assert not n.exists(),n
 for d in ['scripts','reference','patches','families']:(n/d).mkdir(parents=True,exist_ok=True)
 for f in ['SOURCE-PINS.tsv','LICENSE']:shutil.copyfile(base/f,n/f)
 pins=(n/'SOURCE-PINS.tsv').read_text();pins='\n'.join(l for l in pins.splitlines() if not l.startswith('kernel-build-tools\t'))+'\n';pins+=f"tcpc31\t{pin['url']}\t{pin['commit']}\t{pin['subtree']}\t{pin['tree_id']}\t{pin['upstream_branch']}\tGenuine public TCPC2.0.31 full subtree, archived/pinned with complete OEM source delta; not auto-certified\n";(n/'SOURCE-PINS.tsv').write_text(pins)
 for f in ['gki-vmlinux.symvers.sha256','gki-12901745-vmlinux.symvers.xz','vendor-kout.config.sha256','host-config-drift.md']:shutil.copyfile(base/'reference'/f,n/'reference'/f)
 for f in (base/'scripts').iterdir():
  if f.is_file() and not f.name.startswith('native-'):shutil.copyfile(f,n/'scripts'/f.name)
 shutil.copyfile(P/'BATCH-MANIFEST.tsv',n/'reference/BATCH-MANIFEST.tsv');shutil.copyfile(E/'compiled-unit-plan.json',n/'reference/compiled-unit-plan.json');shutil.copyfile(E/'tcpc31-public.tar.xz',n/'reference/tcpc31-public.tar.xz');shutil.copyfile(E/'tcpc31-public-pin.json',n/'reference/tcpc31-public-pin.json');shutil.copyfile(E/'source-recovery.json',n/'reference/historical-source-provenance.json');shutil.copyfile(E/'complete-historical-source-deltas.patch',n/'patches/0002-complete-historical-implementations.patch')
 (n/'reference/provider-units.json').write_text(json.dumps(providers,indent=2)+'\n');(n/'families/OWNERSHIP.json').write_text(json.dumps({'family':family,'owned_modules':S['families'][family],'all_families':S['repositories'],'joint_build_rationale':'Selected30 mutually coupled source APIs; all jointly compiled without ownership transfer. External18source API witnesses not whole-provider certification. Canonical components unchanged.'},indent=2)+'\n')
 (n/'README.md').write_text(f'# {family} — maintained GQ5012BF1 Batch04 source\n\nFull immutable ALPS/common/toolchain/config retrieval, genuine publicTCPC31 archive with tree/SHA pin, all recovered whole C/header patches, actual composite unit map and natural source-only provider ABI generation. Owned targets only:families/OWNERSHIP.json. Other jointly built targets and external providers are not automatically owned/certified.\n\nOffline:set LIEPPOS_IOMMU_MIRROR to preserved public mirror; run scripts/bootstrap.sh WS then scripts/bulk-build.sh WS B1/B2. Documentation/strict acceptance/recovery evidence in canonical PLATFORM-BATCH-04. No phone/role/PD/register/firmware operation or push.\n')
 subprocess.run(['git','init','-q',str(n)],check=True)
 for f in (n/'scripts').glob('*.sh'):f.chmod(0o755)
# Adapt tested stock-only analysis tools; these cannot place stock bodies/metadata in builds.
for f in ['prepare-reference.py','compare-batch.py','test-acceptance.py']:
 t=(P.parent/'PLATFORM-BATCH-03/scripts'/f).read_text().replace('android_kernel_modules_secure_diagnostics_ulefone_gq5012bf1',S['repositories']['CHARGER-GAUGE-ADC']).replace('all34','all30').replace('Investigate all34','Investigate all30');(P/'scripts'/f).write_text(t)
print('Created three30-target source recipes with recovered169C/H38fullpatches and TCPC31archive pin')
