#!/usr/bin/env python3
"""Materialize conservative source-evidence reviews without rebuilding or changing owners.

A/B require a preserved pinned recipe AND independent clean-build parity evidence.
Historical exact artifacts with unclosed recipe/input preservation are G, not A or C.
C is reserved for existing buildable reconstructions with incomplete stock acceptance.
D requires a located public source candidate. UNKNOWN is never converted to missing code.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
from inventory import ROOT, AUDIT, WORKSPACE, read_table

BASE = json.loads((AUDIT/'evidence/workspace-baseline.json').read_text())
STOCK = json.loads((AUDIT/'evidence/stock-identities.json').read_text())
COVERAGE = {r['module']:r for r in read_table(ROOT/'reverse-engineering/coverage-audit/kernel-modules.tsv')}
LOAD = {r['module']:r for r in read_table(ROOT/'reverse-engineering/boot/module-loading/module-classification.tsv')}
INDEX = read_table(ROOT/'kernel/nothing-module-index.csv')
MASTER = {r['sha256']:r for r in read_table(ROOT/'kernel/stock-module-master.csv')}
NORM = lambda s:s.removesuffix('.ko').replace('-','_')


def ref(path):
    path=Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else '../'+str(path.relative_to(WORKSPACE)) if path.is_relative_to(WORKSPACE) else str(path)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def pack(owner):
    return ROOT/BASE['components'][owner]['path']

PUBLIC = {}
for name in ['kernel','device_modules','kernel_modules']:
    path=WORKSPACE/'kernel-research/nothing-mt6878'/name
    PUBLIC[name]=dict(path=ref(path),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip(),
        tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=path,text=True).strip())

REVIEW = {}

def add(stock, **values):
    REVIEW[stock['module_id']].update(values)

for identity, stock in STOCK.items():
    cov=COVERAGE[stock['filename']];load=LOAD[NORM(stock['filename'])]
    candidates=[r for r in INDEX if NORM(r['module_name'])==NORM(stock['filename'])]
    candidate=next((r for r in candidates if r['source_root'] in PUBLIC and (ROOT/PUBLIC[r['source_root']]['path']/r['source_dir']).exists()),None)
    owner=cov['component'];cp=BASE['components'].get(owner)
    row=dict(module_id=identity, component_owner=owner, component_status=cp['status'] if cp else 'N/A',
        canonical_component_status=cov['component_status'],component_evidence=cp['path']+'/README.md' if cp else 'reverse-engineering/coverage-audit/kernel-modules.tsv',
        source_status='D' if candidate else 'G', source_repo='UNKNOWN',source_commit='UNKNOWN',source_pin='UNKNOWN',build_script='UNKNOWN',
        source_snapshot_path='UNKNOWN',candidate_path='UNKNOWN',candidate_evidence='kernel/nothing-module-index.csv',
        parity_evidence=[],historical_exact_functions='UNKNOWN',exact_functions='UNKNOWN',equivalent_functions='UNKNOWN',unresolved_functions='UNKNOWN',
        abi_status='UNKNOWN',crc_status='UNKNOWN',kcfi_status='UNKNOWN',reproduction_status='NO_INDEPENDENT_BUILD_DEMONSTRATED',
        historical_parity='UNKNOWN',verified_difference_classification='UNKNOWN',preservation_risk='UNKNOWN',
        blocker='No independently reproducible stock-compatible build or complete parity ledger found for this identity.',
        gap_kind='SOURCE_INTEGRATION_AND_MEASURED_PARITY' if candidate else 'SOURCE_EVIDENCE_UNRESOLVED',
        runtime_status='RECORDED_LOADED' if load['loaded_in_capture']=='y' else 'NOT_OBSERVED_IN_CAPTURE' if load['loaded_in_capture']=='n' else 'UNKNOWN',
        runtime_evidence='reverse-engineering/boot/module-loading/module-classification.tsv', bound_probe_status='UNKNOWN',
        observed_bindings='UNKNOWN',binding_evidence='UNKNOWN',
        runtime_identity_status='NAME_ONLY_CAPTURE' if stock['filename']=='bluetooth.ko' else 'UNAMBIGUOUS_SHIPPED_NAME',
        necessity='REQUIRED_BY_RETAINED_FIRST_STAGE_LOAD_CONTRACT' if load['vb_load']=='y' else 'UNKNOWN',
        necessity_evidence='reverse-engineering/boot/module-loading/module-classification.tsv' if load['vb_load']=='y' else 'UNKNOWN',
        normal_load_list=load['vb_load']+';'+load['sd_load']+';'+load['vd_load'],recovery_load_list=load['vb_recovery'],
        load_phase=load['resolved_phase'] or 'UNKNOWN',load_order=load['resolved_seq'] or 'UNKNOWN',
        exclusion_justification='UNKNOWN',optional_review=cov['coverage']=='D',
        firmware_boundary='UNKNOWN; no proprietary firmware reconstruction is inferred',source_group='SOURCE-EVIDENCE-UNRESOLVED',priority='P0_BOOT' if load['vb_load']=='y' else 'P4_OPTIONAL_OR_UNESTABLISHED')
    if candidate:
        public=PUBLIC[candidate['source_root']]
        directory=candidate['source_dir']
        if directory=='.' and candidate['evidence'].startswith(candidate['source_root']+'/'):
            directory=str(Path(candidate['evidence'].split('/',1)[1]).parent)
            if Path(directory).name=='build':directory=str(Path(directory).parent)
        assert (ROOT/public['path']/directory).is_dir(), directory
        row.update(source_repo=public['path'],source_commit=public['commit'],source_pin=public['commit'],
            candidate_path=public['path']+'/'+directory,source_group='CANDIDATE:'+candidate['source_root']+':'+directory,
            candidate_configs=candidate['kconfig_symbols'] or 'UNKNOWN',candidate_files=candidate['source_files'] or 'UNKNOWN',
            blocker='Public candidate target at '+directory+'; clean stock-compatible integration/config/provider-CRC/KCFI and full parity are not demonstrated. No missing implementation or compiler failure is assumed.')
    if stock['filename']=='bluetooth.ko':row['runtime_status']='RECORDED_NAME_LOADED_BINARY_IDENTITY_UNPROVEN'
    REVIEW[identity]=row

# Accepted accelerator recipes: independently cloned/rebuilt; exact stock hash binding.
ACC={
'MALI-GPU-KERNEL':'android_kernel_modules_gpu_ulefone_gq5012bf1',
'APUSYS-NPU-KERNEL':'android_kernel_modules_apusys_ulefone_gq5012bf1',
'MTK-VCODEC-KERNEL':'android_kernel_modules_vcodec_ulefone_gq5012bf1',
'MTK-MDP-KERNEL':'android_kernel_modules_mdp_ulefone_gq5012bf1',
'GPU-AI-AUX-KERNEL-INTERFACES':'android_kernel_modules_gpu_ai_aux_ulefone_gq5012bf1',
'CAMERA-ISP-KERNEL':'android_kernel_modules_camera_isp_ulefone_gq5012bf1'}
for owner,repository in ACC.items():
    source=WORKSPACE/repository;head=BASE['maintained_repositories'][repository]['head']
    assert (source/'scripts/b1b2.sh').is_file() and (source/'SOURCE-PINS.tsv').is_file()
    if owner=='MALI-GPU-KERNEL':
        proof=pack(owner)/'evidence/source-preservation/acceptance-B1';baseline=read_table(proof/'stock-baseline.tsv')
        hashes={r['sha256'] for r in read_table(ROOT/'reverse-engineering/accelerator-preparation/MALI-GPU-KERNEL/stock-modules.tsv')}
        evidence=[ref(proof/'stock-baseline.tsv'),ref(proof/'function-parity.tsv'),ref(pack(owner)/'evidence/source-preservation/final-commit-9d05ae8-mirror-b1b2-verify.log.txt')]
    else:
        proof=ROOT/'reverse-engineering/accelerator-preparation'/owner/'evidence/reconstruction/acceptance/acceptance.json'
        results=json.loads(proof.read_text());hashes={r['stock_sha256'] for r in results.values()};evidence=[ref(proof),ref(ROOT/'reverse-engineering/accelerator-preparation'/owner/'SOURCE.md')]
    for stock in STOCK.values():
        if COVERAGE[stock['filename']]['component']!=owner:continue
        assert stock['stock_sha256'] in hashes,(owner,stock['filename'],hashes)
        semantic=stock['filename']=='imgsensor.ko'
        add(stock,source_status='B' if semantic else 'A',source_repo=ref(source),source_commit=head,
            source_pin=ref(source/'SOURCE-PINS.tsv'),build_script=ref(source/'scripts/b1b2.sh'),
            source_snapshot_path=ref(source/'patches'),parity_evidence=evidence,
            exact_functions=stock['function_count']-int(semantic),equivalent_functions=int(semantic),unresolved_functions=0,
            historical_exact_functions=stock['function_count']-int(semantic),historical_parity='FULL_ACCEPTANCE',
            abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',
            verified_difference_classification='PROVEN_SEMANTIC_EQUIVALENT' if semantic else 'COMPILER_ONLY_PRIVATE_NAMES_AND_BUILD_METADATA' if stock['filename']=='mtk_imgsys_cmdq.ko' else 'BUILD_METADATA_ONLY',
            preservation_risk='LOW: immutable recipe, complete patches and local history; public input availability remains a dependency',
            source_group=owner,blocker='NONE',gap_kind='NONE',firmware_boundary='Proprietary processor firmware / userspace algorithms remain outside kernel-source proof')

# BOOT-CLOCK-CORE (2026-10-09): maintained pinned recipe, independent clean-checkout B1/B2 and
# full stock acceptance bound to each exact stock SHA256. Ownership (COVERED-GENERIC) unchanged.
CLK_REPO=WORKSPACE/'android_kernel_modules_boot_clock_ulefone_gq5012bf1'
CLK_PACK=ROOT/'reverse-engineering/kernel-source-reconstruction/BOOT-CLOCK-CORE'
CLK_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=CLK_REPO,text=True).strip()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=CLK_REPO,text=True).strip(), 'boot-clock repo dirty'
clk_acceptance=json.loads((CLK_PACK/'evidence/acceptance/acceptance.json').read_text())
clk_hashes={v['stock_sha256']:k for k,v in clk_acceptance.items()}
assert len(clk_hashes)==6 and all(v['unresolved']==0 and v['raw_differing_bytes']<=v['allowed_range'][1]==20 for v in clk_acceptance.values())
for stock in STOCK.values():
    if stock['stock_sha256'] not in clk_hashes:continue
    m=clk_hashes[stock['stock_sha256']];assert m+'.ko'==stock['filename']
    assert clk_acceptance[m]['functions']==stock['function_count'],(m,stock['function_count'])
    add(stock,source_status='A',source_repo=ref(CLK_REPO),source_commit=CLK_HEAD,
        source_pin=ref(CLK_REPO/'SOURCE-PINS.tsv'),build_script=ref(CLK_REPO/'scripts/b1b2.sh'),
        source_snapshot_path=ref(CLK_REPO/'patches'),
        parity_evidence=[ref(CLK_PACK/'evidence/acceptance/acceptance.json'),ref(CLK_PACK/'module-parity.tsv'),
                         ref(CLK_PACK/'evidence/build/b1b2-clean-checkout.log'),ref(CLK_PACK/'RECONSTRUCTION-REPORT.md')],
        exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,
        historical_exact_functions=stock['function_count'],historical_parity='FULL_ACCEPTANCE',
        abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',
        verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',
        preservation_risk='LOW: immutable public pins, complete patches, local history and research bundle; public input availability remains a dependency',
        source_group='BOOT-CLOCK-CORE',blocker='NONE',gap_kind='NONE',
        firmware_boundary='NONE; runtime clock behaviour not validated (Slot B procedure pending)')

# PRESERVE:STORAGE (2026-10-09): the historical exact storage rebuilds are now a maintained
# pinned recipe with independent clean-checkout B1/B2 and full stock acceptance bound to each
# exact stock SHA256. Ownership (UFS-RPMB-KERNEL, co-owner MICROSD-KERNEL) unchanged.
STOR_REPO=WORKSPACE/'android_kernel_modules_storage_ulefone_gq5012bf1'
STOR_PACK=ROOT/'reverse-engineering/kernel-source-reconstruction/STORAGE'
STOR_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=STOR_REPO,text=True).strip()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=STOR_REPO,text=True).strip(), 'storage repo dirty'
stor_acceptance=json.loads((STOR_PACK/'evidence/acceptance/acceptance.json').read_text())
stor_hashes={v['stock_sha256']:k for k,v in stor_acceptance.items()}
assert len(stor_hashes)==10 and all(v['unresolved']==0 and v['raw_differing_bytes']<=v['allowed_range'][1]==20 for v in stor_acceptance.values())
for stock in STOCK.values():
    if stock['stock_sha256'] not in stor_hashes:continue
    m=stor_hashes[stock['stock_sha256']];assert m+'.ko'==stock['filename']
    assert stor_acceptance[m]['functions']==stock['function_count'],(m,stock['function_count'])
    add(stock,source_status='A',source_repo=ref(STOR_REPO),source_commit=STOR_HEAD,
        source_pin=ref(STOR_REPO/'SOURCE-PINS.tsv'),build_script=ref(STOR_REPO/'scripts/b1b2.sh'),
        source_snapshot_path=ref(STOR_REPO/'patches'),
        parity_evidence=[ref(STOR_PACK/'evidence/acceptance/acceptance.json'),ref(STOR_PACK/'module-parity.tsv'),
                         ref(STOR_PACK/'evidence/build/b1b2-clean-checkout.log'),ref(STOR_PACK/'RECONSTRUCTION-REPORT.md')],
        exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,
        historical_exact_functions=stock['function_count'],historical_parity='FULL_ACCEPTANCE (historical 2026-10-04 artifacts also re-verified exact)',
        abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',
        verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',
        preservation_risk='LOW: immutable public pins, complete patches, local history and research bundle; public input availability remains a dependency',
        source_group='PRESERVE:STORAGE',blocker='NONE',gap_kind='NONE',
        firmware_boundary='NONE for the module source; RPMB secure-world consumers (TrustKernel teed/TAs) and ATF SiP services are outside the proof; runtime not validated')

# PINCTRL (2026-10-09): unchanged ALPS 5e41 C, maintained scope-only recipe; independent
# fresh clone B1/B2 and full stock ELF acceptance. Exact four identities, owners unchanged.
PIN_REPO=WORKSPACE/'android_kernel_modules_pinctrl_ulefone_gq5012bf1'
PIN_PACK=ROOT/'reverse-engineering/kernel-source-reconstruction/PINCTRL'
PIN_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=PIN_REPO,text=True).strip()
assert PIN_HEAD==(PIN_PACK/'source/COMMIT').read_text().strip(), 'pinctrl accepted source commit changed'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=PIN_REPO,text=True).strip(), 'pinctrl repo dirty'
pin_acceptance=json.loads((PIN_PACK/'evidence/acceptance/acceptance.json').read_text())
pin_targets={
    'pinctrl-mt6363':'19d1558e52ed4af589713c185451ef50444175944d8a874faa2b51146f984f03',
    'pinctrl-mt6878':'c1e98148b06a21fdf2ac81bb67e3f0089fa43789d6a57a0bfd4cd8b41c0ac72a',
    'pinctrl-mtk-common-v2_debug':'878aa15128051972047732a2c051a74c6d04c5f223bbff870b01ed58b9bf69be',
    'pinctrl-mtk-v2':'54b28c83c8f20cba2ce4b7c770fc4534120eba6aaddd1eff11e09bee22b61ef6'}
assert set(pin_acceptance)==set(pin_targets)
assert all(v['stock_sha256']==pin_targets[m] and v['unresolved']==0 and
           v['raw_differing_bytes']<=v['allowed_range'][1]==20 for m,v in pin_acceptance.items())
for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','SOURCE-TREE','config.sha256','gki-symvers.sha256','pinctrl.Module.symvers']:
    assert (PIN_PACK/'evidence/build'/('B1-'+f)).read_bytes()==(PIN_PACK/'evidence/build'/('B2-'+f)).read_bytes(), 'pinctrl B1/B2 '+f
for stock in STOCK.values():
    m=stock['filename'].removesuffix('.ko')
    if m not in pin_targets:continue
    assert stock['stock_sha256']==pin_targets[m] and pin_acceptance[m]['functions']==stock['function_count']
    add(stock,source_status='A',source_repo=ref(PIN_REPO),source_commit=PIN_HEAD,
        source_pin=ref(PIN_REPO/'SOURCE-PINS.tsv'),build_script=ref(PIN_REPO/'scripts/b1b2.sh'),
        source_snapshot_path=ref(PIN_REPO/'patches'),
        parity_evidence=[ref(PIN_PACK/'evidence/acceptance/acceptance.json'),ref(PIN_PACK/'MODULE-PARITY.tsv'),
                         ref(PIN_PACK/'evidence/build/b1b2-clean-checkout.log'),ref(PIN_PACK/'RECONSTRUCTION-REPORT.md')],
        exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,
        abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',
        verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',
        preservation_risk='LOW: immutable public pins, complete scope patch, local committed recipe and research bundle; public input availability remains a dependency',
        source_group='PINCTRL',blocker='NONE',gap_kind='NONE',
        firmware_boundary='NONE required by the module source proof; physical wiring, selected pad states, GPIO bases and replacement runtime are not certified')

# GKI: both independently cleaned builds prove complete ELF bodies, not vendor variants.
system=pack('SYSTEM-DLKM');gki_lines=(system/'parity/system-dlkm-parity-B1.txt').read_text().splitlines()
proven={l.split('\t')[0] for l in gki_lines if '\tIDENTICAL BODY, signature differs' in l};assert len(proven)==60
assert proven=={l.split('\t')[0] for l in (system/'parity/system-dlkm-parity-B2.txt').read_text().splitlines() if '\tIDENTICAL BODY, signature differs' in l}
for stock in STOCK.values():
    if stock['partitions']!=['system_dlkm']:continue
    assert stock['filename'] in proven
    add(stock,source_status='A',source_repo='../kernel-research/android-common-gq5012bf1',source_commit='6b18f0b574ab3267615ae6ce642d5a7c3c21ac09',
        source_pin='kernel/phase4-gki-build-pins.tsv',build_script=ref(system/'scripts/build_gki_stamped.sh'),
        source_snapshot_path='kernel/phase4-gki-effective-manifest.xml',
        parity_evidence=[ref(system/'parity/system-dlkm-parity-B1.txt'),ref(system/'parity/system-dlkm-parity-B2.txt'),ref(system/'parity/b1-b2.txt')],
        exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,historical_exact_functions=stock['function_count'],
        historical_parity='COMPLETE_ELF_BODY_EXACT',abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',
        reproduction_status='STAMPED_SOURCE_BUILD_BAZEL_CLEAN_B1_B2',verified_difference_classification='APPENDED_SIGNATURE_ONLY',
        preservation_risk='MEDIUM: manifest and stamping script preserved; workspace bootstrap is not a maintained standalone repository',
        source_group='SYSTEM-DLKM',blocker='NONE (integration must retain an appropriate module-signature policy; release signing key is unavailable)',gap_kind='NONE',firmware_boundary='NONE_REQUIRED_BY_KERNEL_MODULE_PROOF')

# Retain successful historical source builds, but do not silently invent standalone recipes.
# These inventories state real source builds and identify their modules, rather than mere mentions.
BUILT={}
sets=[('reverse-engineering/connectivity/kernel/module-inventory.tsv','CONNECTIVITY','reverse-engineering/connectivity/scripts/rebuild_all.sh'),
      ('reverse-engineering/modem/kernel/module-inventory.tsv','MODEM','reverse-engineering/modem/scripts/rebuild_all.sh'),
      ('reverse-engineering/audio/kernel/module-inventory.tsv','AUDIO','reverse-engineering/audio/scripts/build_aud.sh'),
      ('reverse-engineering/sensors/kernel/module-inventory.tsv','SENSOR-HUB','reverse-engineering/audio/scripts/build_dm.sh')]
for path,group,recipe in sets:
    for x in read_table(ROOT/path):
        BUILT[NORM(x['module'])]=dict(group=group,proof=path,recipe=recipe,source=path.rsplit('/kernel/',1)[0],
            historical_exact=x.get('functions_exact','UNKNOWN'),note='Historical source-built full function/data/ABI parity is retained; independent input/recipe closure is not established.')
for path,group,recipe in [
 ('reverse-engineering/storage/kernel/module-inventory.tsv','STORAGE','reverse-engineering/storage/scripts/build-all.sh'),
 ('reverse-engineering/usb/kernel/module-inventory.tsv','USB','reverse-engineering/usb/scripts/build-all.sh'),
 ('reverse-engineering/display-input/backlight-glue/module-inventory.tsv','DISPLAY-GLUE','../Reverse Engineer - DONE/BACKLIGHT-DISPLAY-GLUE/scripts/glue.py')]:
    for x in read_table(ROOT/path):
        state=x.get('parity A vs B',x.get('status',''))
        if not state.startswith('EXACT'):continue
        name=x.get('filename',x.get('module'))
        exact=re.search(r'(\d+)/(\d+)',x.get('functions',x.get('functions (byte-identical/total)','')))
        BUILT[NORM(name)]=dict(group=group,proof=path,recipe=recipe,source=path.rsplit('/kernel/',1)[0],historical_exact=exact.group(1) if exact else 'UNKNOWN',note=state)

# Whole-module scopes verified in legacy packages, not every module casually assigned to them.
MANUAL={
'camera_eeprom_v4l2':('CAMERA-EEPROMS','scripts/build.sh'),
'dw9781c':('DW9781C-OIS','scripts/build_b1_b2.sh'),
'rt5133-regulator':('RT5133-POWER-IC','scripts/sb.sh'), 'extdev_io_class':('RT5133-POWER-IC','scripts/sb.sh'),
'gz_trusty_mod':('GZ-TRANSPORT','README.md'),'gz_ipc_mod':('GZ-TRANSPORT','README.md'),'gz_irq_mod':('GZ-TRANSPORT','README.md'),
'gz_log_mod':('GZ-TRANSPORT','README.md'),'gz_virtio_mod':('GZ-TRANSPORT','README.md'),
'gz_tz_system':('GZ-TZ-SYSTEM','source/Makefile'),'gz_main_mod':('GZ-MAIN-MOD','source/Makefile'),
'ffa_v10':('FFA-V10','source/Makefile'),'tmem_ffa':('TMEM-FFA','source/Makefile'),
'spi-mt65xx':('SPI-MT65XX','source/Makefile'),'fingerprint':('FINGERPRINT-PLATFORM-SHIM','source/Makefile'),
'microarray_fp_tee':('MICROARRAY-FP-TEE','source/Makefile'),
'mtk-mbox':('MTK-MBOX','README.md'),'mtk-mbox-mailbox':('MTK-MBOX','README.md'),
'mtk_rpmsg_mbox':('MTK-RPMSG-MBOX','scripts/build-all.sh'),'mtk_tinysys_ipi':('MTK-TINYSYS-IPI','scripts/build-all.sh'),
'mtk_disp_notify':('MTK-DISP-NOTIFY','source/Makefile'),'mtk_panel_ext':('MEDIATEK-DRM','scripts/build.sh'),
'mediatek-drm':('MEDIATEK-DRM','scripts/build.sh'),'mediatek-drm-panel-drv':('MEDIATEK-DRM','scripts/build.sh'),
'panel-ky-vtdr6115-dphy-cmd':('VTDR6115-DISPLAY','source/Makefile'),
'aw36515':('AW36515-FLASH','source/Makefile'),'aw36518':('AW36518-FLASH','source/Makefile'),
'aw36518_v2':('AW36518-V2-FLASH','source/Makefile'),'aw883xx_driver':('AW883XX-SPEAKER-AMP','source/Makefile'),
'custom-ldo':('CUSTOM-LDO','source/Makefile'),'custom-ldo-wl2868':('WL2868-CAMERA-LDO','source/Makefile'),
'leds-ln2403':('LN2403-CAMPLIGHT','source/Makefile'),'leds-rgb-aw2013':('AW2013-RGB-LED','source/Makefile'),
'sc851x_charger':('SC8510-BIDIRECTIONAL-CHARGE-PUMP','README.md'),'sc8571_charger':('SC8571-CHARGE-PUMP','README.md'),
'sh366003_fg':('SH366003-FUEL-GAUGE','scripts/build_sh366003.sh'),
'yft_gpio_keys':('PROGRAMMABLE-KEYS','source/Makefile'),'yft_tpd_gesture':('YFT-TPD-GESTURE','source/Makefile'),
'yft_tiny2c_usb':('FM78100-COMPANION','scripts/build.sh'),
'spi_tiny_co5300_lcd':('CO5300-REAR-DISPLAY','source/Makefile'),'hynitron':('HYNITRON-REAR-TOUCH','source/build.sh'),
'mt6375':('MT6375-CHARGER','scripts/build_b1_b2.sh'),'mt6375-adc':('MT6375-CHARGER','scripts/build_b1_b2.sh'),
'mt6375-auxadc':('MT6375-CHARGER','scripts/build_b1_b2.sh'),'mt6375-charger':('MT6375-CHARGER','scripts/build_b1_b2.sh'),
'mt6375-battery':('MT6375-CHARGER','scripts/build_b1_b2.sh'),
'mtk_charger_framework':('USB-CHARGER-INTEGRATION','scripts/build_b1_b2.sh'),
'charger_class':('USB-CHARGER-INTEGRATION','scripts/build_b1_b2.sh'),'mtk_chg_type_det':('USB-CHARGER-INTEGRATION','scripts/build_b1_b2.sh'),
'adapter_class':('CHARGER-CLASS','README.md'),'mtk_charger_algorithm_class':('CHARGER-CLASS','README.md'),
'pd_dbg_info':('PD-DBG-INFO','source/Makefile'),'tcpc_class':('TCPC-CLASS','source/Makefile'),
' tcpc_mt6375':('TCPC-MT6375','source/Makefile'), 'tkcore_drv':('TKCORE-DRV','scripts/build_tkcore_drv.sh')}
# Preserve narrow source owners from the primary records but use actual proof packages.
MANUAL['tcpc_mt6375']=MANUAL.pop(' tcpc_mt6375')
for name,(owner,recipe) in MANUAL.items():
    if owner not in BASE['components']:continue
    p=pack(owner);r=p/recipe
    if not r.exists():r=p/'README.md'
    BUILT[NORM(name)]=dict(group=owner,proof=ref(p/'README.md'),recipe=ref(r),source=ref(p/'source') if (p/'source').exists() else ref(p),
        historical_exact='UNKNOWN',note='Named whole-module reconstruction exists; retain its actual parity level without inferring independent preserved-input acceptance.')
for name in ['main_vcm','main2_vcm','main3_vcm','main4_vcm','sub_vcm','camera_af_media']:
    p=pack('CAMERA-VCMS');BUILT[NORM(name)]=dict(group='CAMERA-VCMS',proof=ref(p/'README.md'),recipe=ref(p/'scripts/sb.sh'),source=ref(p/'source'),historical_exact='UNKNOWN',note='Unmodified public ALPS source; historical full parity and B1/B2; build relies on the old NFC output tree and stock-all.symvers.')

# Review specific unresolved reconstructions directly; do not call provider CRC incompatibility semantic equivalence.
INCOMPLETE={
'focaltech_touch_spi_ft3680':('FT3680-TOUCH','source/Makefile','binary-analysis/focaltech_touch_spi_ft3680.parity.txt',67,'Real opcode/call-boundary differences remain; 40 functions size-different and complete semantic proof absent.'),
'yft_devinfo':('YFT-DEVINFO','source/Makefile','binary-analysis/parity/yft_devinfo-parity-SUMMARY.txt',54,'10 exported device_add CRCs and 11 KCFI IDs differ; remaining provider enum/type graph and probe/sysfs codegen are unclosed.'),
'st21nfc':('ST21NFC','source/Makefile','binary-analysis/parity/st21nfc.parity.txt',22,'22/24 raw function matches; complete independent clean-input/relocation/semantic acceptance at current audit standard is not demonstrated.'),
}
for identity,stock in STOCK.items():
    row=REVIEW[identity];name=NORM(stock['filename'])
    if row['source_status'] in ['A','B']:continue
    if name in BUILT:
        b=BUILT[name];add(stock,source_status='G',source_repo='.',source_commit=BASE['research_baseline_commit'],
            source_pin=b['proof'],build_script=b['recipe'],source_snapshot_path=b['source'],parity_evidence=[b['proof']],
            historical_exact_functions=b['historical_exact'],exact_functions=b['historical_exact'],historical_parity=b['note'],source_group='PRESERVE:'+b['group'],
            abi_status='HISTORICAL_LEVEL_IN_LINKED_RECORDS; INDEPENDENT_INPUT_CLOSURE_UNVERIFIED',
            crc_status='HISTORICAL_RESULTS_PRESERVED; FRESH_INPUTS_UNVERIFIED',kcfi_status='HISTORICAL_RESULTS_PRESERVED; FRESH_INPUTS_UNVERIFIED',
            reproduction_status='HISTORICAL_BUILD_EXISTS_INDEPENDENT_RECIPE_CLOSURE_UNPROVEN',
            preservation_risk='HIGH: mutable old worktree / prepared output / provider inputs, or private include files; complete clean bootstrap is not preserved and verified',
            blocker='Independent source-input closure unproved. Existing artifact parity is not discarded; inspect '+b['recipe']+' and preserve all exact inputs before claiming A/B.',
            gap_kind='RECIPE_PRESERVATION_OR_ACCEPTANCE_EVIDENCE')
    if name in INCOMPLETE:
        owner,recipe,proof,exact,note=INCOMPLETE[name];p=pack(owner)
        add(stock,source_status='C',source_repo='.',source_commit=BASE['research_baseline_commit'],source_pin=ref(p/'README.md'),
            source_snapshot_path=ref(p/'source'),build_script=ref(p/recipe) if (p/recipe).exists() else ref(p/'README.md'),
            parity_evidence=[ref(p/proof)],historical_exact_functions=exact,exact_functions=exact,
            source_group='FINISH:'+owner,reproduction_status='SOURCE_AND_BUILD_RECIPE_EXIST_STOCK_ACCEPTANCE_INCOMPLETE',
            historical_parity='PARTIAL_SOURCE_BUILD_PARITY',blocker=note+' Recipe preservation also requires completion.',gap_kind='CODE_OR_ABI_PARITY',preservation_risk='HIGH: full standalone input closure pending',
            abi_status='INCOMPLETE_ACCEPTANCE',crc_status='10_EXPORT_CRC_MISMATCHES' if name=='yft_devinfo' else 'IMPORT_CRC_PARITY_REPORTED',
            kcfi_status='11_TYPE_ID_MISMATCHES' if name=='yft_devinfo' else 'FULL_SOURCE_ACCEPTANCE_NOT_CERTIFIED')
    if name=='tkcore':
        p=pack('TRUSTKERNEL-ABI-ISLAND');add(stock,source_status='C',source_repo='.',source_commit=BASE['research_baseline_commit'],
            source_pin='kernel/phase4-tkcore-island-phase3f-acceptance.md',source_snapshot_path=ref(p/'source'),build_script=ref(p/'source/Makefile'),
            parity_evidence=['kernel/phase4-tkcore-island-phase3f-acceptance.md'],historical_parity='122_FUNCTION_SOURCE_ABI_ISLAND_NOT_STOCK_DROP_IN',
            source_group='FINISH:TRUSTKERNEL-SOURCE-ABI',reproduction_status='SOURCE_ISLAND_BUILDS_BUT_STOCK_ABI_INCOMPATIBLE',
            blocker='Source island is statically complete, but only 5/19 consumer edges retain historical stock CRCs. 14 private-type CRC edges do not permit a stock-compatible single-module replacement.',
            gap_kind='STOCK_PRIVATE_ABI_AND_COMPATIBILITY_PROOF',crc_status='STOCK_ABI_INCOMPATIBLE_ISLAND',preservation_risk='HIGH: source island plus transport/consumer outputs need an immutable recipe',
            firmware_boundary='Secure OS and TAs remain proprietary; this audit concerns only normal-world stock-compatible ABI')
    if stock['filename'] in ['rt5133-regulator.ko','extdev_io_class.ko']:
        row['bound_probe_status']='RT5133_INITIAL_CHIP_READ_PROBE_FAILURE_DOCUMENTED' if stock['filename']=='rt5133-regulator.ko' else 'NO_CONSUMING_RT5133_REGULATORS_REGISTERED'
    if row['source_status'] not in ['A','B'] and row['source_group'].startswith('SOURCE-EVIDENCE'):
        row['blocker']='No sufficient per-module source/build evidence identified; source status unresolved, not asserted missing.'

# Direct recorded driver->module symlinks establish binding, not bus transactions,
# stream success, or whether the module is indispensable. Unresolved echo paths are ignored.
bus_capture=ROOT/'workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/buses.txt'
blocks=re.split(r'^===(.+)===$',bus_capture.read_text(),flags=re.M)
for i in range(1,len(blocks),2):
    device,body=blocks[i],blocks[i+1]
    match=re.search(r'^/sys/module/([A-Za-z0-9_]+)$',body,flags=re.M)
    if not match:continue
    for stock in STOCK.values():
        if NORM(stock['filename'])==match.group(1):
            row=REVIEW[stock['module_id']]
            paths=[] if row['observed_bindings']=='UNKNOWN' else row['observed_bindings'].split(';')
            paths.append(device)
            add(stock,bound_probe_status='RECORDED_DRIVER_MODULE_SYMLINK',observed_bindings=';'.join(sorted(set(paths))),binding_evidence=ref(bus_capture))

# The old index misses the DMA-BUF test's macro-selected output name. Inspect the
# pinned r44p1 public object directly; this is a candidate, NOT one of the eight closed GPU modules.
mirror=Path('/home/armol/kernel-work/public-mtk/nkm.git')
revision='580d08eac018657a993e56b1806407e41a3b9545'
directory='gpu/gpu_mali/mali_avalon/mali-r44p1/drivers/base/arm/dma_buf_test_exporter'
object_path=directory+'/dma-buf-test-exporter.c'
content=subprocess.check_output(['git','--git-dir',str(mirror),'show',revision+':'+object_path])
objects=dict(repository=str(mirror),public_url='https://github.com/NothingOSS/android_kernel_modules_nothing_mt6878',commit=revision,
             path=object_path,blob=subprocess.check_output(['git','--git-dir',str(mirror),'rev-parse',revision+':'+object_path],text=True).strip(),sha256=hashlib.sha256(content).hexdigest())
(AUDIT/'evidence/additional-candidate-git-object.json').write_text(json.dumps(objects,indent=2,sort_keys=True)+'\n')
for stock in STOCK.values():
    if stock['filename']=='mali_dmabuf_test_mt6878_r44.ko':
        add(stock,source_status='D',source_repo=str(mirror),source_commit=revision,source_pin=revision,
            candidate_path='git-object:'+object_path,candidate_evidence='reverse-engineering/kernel-source-parity-audit/evidence/additional-candidate-git-object.json',
            source_group='MALI-DMA-BUF-DIAGNOSTIC',blocker='Relevant public r44p1 DMA-BUF test source found in the pinned GPU donor; macro/output-name integration and stock parity have not been demonstrated.',
            gap_kind='SOURCE_INTEGRATION_AND_MEASURED_PARITY')

# Frozen evidence review inputs (metadata only) and deterministic result.
(AUDIT/'evidence/public-candidate-pins.json').write_text(json.dumps(PUBLIC,indent=2,sort_keys=True)+'\n')
(AUDIT/'evidence/source-reviews.json').write_text(json.dumps(REVIEW,indent=2,sort_keys=True)+'\n')
print('source classes',dict(collections.Counter(r['source_status'] for r in REVIEW.values())))
print('unclassified identities',sum(r['source_status']=='G' for r in REVIEW.values()))
print('source groups',len({r['source_group'] for r in REVIEW.values()}))
