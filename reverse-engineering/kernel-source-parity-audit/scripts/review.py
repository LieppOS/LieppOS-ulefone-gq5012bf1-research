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

# REGULATORS (2026-10-09): immutable unchanged ALPS C, explicit build scopes and real
# provider-source CRC witnesses; fresh committed clone independently passes B1/B2 and stock.
REG_REPO=WORKSPACE/'android_kernel_modules_regulators_ulefone_gq5012bf1'
REG_PACK=ROOT/'reverse-engineering/kernel-source-reconstruction/REGULATORS'
REG_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REG_REPO,text=True).strip()
assert REG_HEAD==(REG_PACK/'source/COMMIT').read_text().strip(), 'regulator accepted recipe commit changed'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REG_REPO,text=True).strip(), 'regulator recipe dirty'
reg_targets={
    'mt6315-regulator':'38c684d376fe58879b764e9b46a8657961113e9d7309411f0abcfaa5ff499ff7',
    'mt6363-regulator':'c827e52efea8a4e447707186e41114ce71facd5c6e548e4c5788def113772249',
    'mtk-dvfsrc-regulator':'ebd6147c7f4d803dbdfa1246efbf8a3487d744eb65cf53d12cbd6f3874a57073',
    'rt6160-regulator':'3fa85cc4811ab691ac337288056a2f0a518917ab8aa7e7b85946957b2378d45e'}
reg_acceptance=json.loads((REG_PACK/'evidence/acceptance/acceptance.json').read_text())
reg_refs={r['module']:r for r in read_table(REG_REPO/'reference/stock-normalized.tsv')}
assert set(reg_acceptance)==set(reg_targets)==set(reg_refs)
for m,v in reg_acceptance.items():
    assert v['stock_sha256']==reg_targets[m]==reg_refs[m]['stock_sha256'] and v['unresolved']==0
    assert v['normalized_sha256']==reg_refs[m]['normalized_sha256']
    assert v['allowed_range']==[int(reg_refs[m]['build_id_offset'],0),20]
    assert len(v['raw_difference_offsets'])==v['raw_differing_bytes']<=20
    assert all(v['allowed_range'][0]<=i<v['allowed_range'][0]+20 for i in v['raw_difference_offsets'])
for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','SOURCE-TREE','PROVIDER-TREE','config.sha256','gki-symvers.sha256','regulators.Module.symvers','natural-external-provider.symvers','crc-witnesses.tsv','provider-object.sha256']:
    assert (REG_PACK/'evidence/build'/('B1-'+f)).read_bytes()==(REG_PACK/'evidence/build'/('B2-'+f)).read_bytes(), 'regulator B1/B2 '+f
for stem,artifact in [('kdm','SOURCE-TREE'),('prov','PROVIDER-TREE')]:
    assert (REG_PACK/'evidence/build'/('B1-'+artifact)).read_text()==(REG_REPO/'reference'/(stem+'-tree.txt')).read_text()
assert (REG_PACK/'evidence/build/B1-natural-external-provider.symvers').read_bytes()==(REG_REPO/'reference/external-provider.symvers').read_bytes()
# Narrow metadata repair: actual hashed load files prove RT6160 normal124/recovery122.
reg_load=read_table(REG_PACK/'evidence/inventory/LOAD-ORDER.tsv')
for kind,seq in [('NORMAL','124'),('RECOVERY','122')]:
    r=next(r for r in reg_load if r['entry']=='rt6160-regulator.ko' and r['kind']==kind)
    assert r['sequence']==seq and digest(ROOT/r['list_path'])==r['list_sha256']
for stock in STOCK.values():
    m=stock['filename'].removesuffix('.ko')
    if m not in reg_targets:continue
    v=reg_acceptance[m]
    assert stock['stock_sha256']==reg_targets[m] and v['functions']==stock['function_count'] and v['data']==stock['data_count']
    add(stock,source_status='A',source_repo=ref(REG_REPO),source_commit=REG_HEAD,
        source_pin=ref(REG_REPO/'SOURCE-PINS.tsv'),build_script=ref(REG_REPO/'scripts/b1b2.sh'),source_snapshot_path=ref(REG_REPO/'patches'),
        parity_evidence=[ref(REG_PACK/'evidence/acceptance/acceptance.json'),ref(REG_PACK/'MODULE-PARITY.tsv'),
            ref(REG_PACK/'evidence/build/b1b2-clean-checkout.log'),ref(REG_PACK/'evidence/acceptance/provider-kcfi-witness.json'),ref(REG_PACK/'RECONSTRUCTION-REPORT.md')],
        exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,
        abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',
        verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',
        preservation_risk='LOW: full public pins, scope-only patches, clean recipe, verbatim main C/headers, independent public recovery mirror and recipe bundle; dependency source gaps remain separate',
        source_group='REGULATORS',blocker='NONE',gap_kind='NONE',
        firmware_boundary='NONE accessed/required for module reconstruction; runtime power/PMIC state, secure-world votes and physical population/binding not certified')
    if m=='rt6160-regulator':add(stock,load_order='124')

# INTERCONNECT-EMI: unchanged six ALPS C units, real 33-slot provider CRC/licence/CFI
# witnesses and independently committed clean-clone B1/B2 plus complete stock ELF parity.
ICC_REPO=WORKSPACE/'android_kernel_modules_interconnect_emi_ulefone_gq5012bf1'
ICC_PACK=ROOT/'reverse-engineering/kernel-source-reconstruction/INTERCONNECT-EMI'
ICC_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ICC_REPO,text=True).strip()
assert ICC_HEAD==(ICC_PACK/'source/COMMIT').read_text().strip(), 'interconnect accepted recipe commit changed'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ICC_REPO,text=True).strip(), 'interconnect recipe dirty'
icc_targets={
    'mmqos-common':'65282e4fca3867482de11c6f6e9d309cf757ec5ee57f72cfd5cedc25b059815c',
    'mmqos-mt6878':'d7ab05e65e8b1dfccc71dd842fe51e56855ec6cb3ba1717e712f3cda0c2f84f9',
    'mtk-emi':'72446c1929e0a397946c2fd784cb905767acc241cf35567607a03b9f5c4fbd60'}
icc_acceptance=json.loads((ICC_PACK/'evidence/acceptance/acceptance.json').read_text())
icc_refs={r['module']:r for r in read_table(ICC_REPO/'reference/stock-normalized.tsv')}
assert set(icc_acceptance)==set(icc_targets)==set(icc_refs)
for m,v in icc_acceptance.items():
    assert v['stock_sha256']==icc_targets[m]==icc_refs[m]['stock_sha256'] and v['unresolved']==0
    assert v['normalized_sha256']==icc_refs[m]['normalized_sha256']
    assert v['allowed_range']==[int(icc_refs[m]['build_id_offset'],0),20]
    assert len(v['raw_difference_offsets'])==v['raw_differing_bytes']<=20
    assert all(v['allowed_range'][0]<=i<v['allowed_range'][0]+20 for i in v['raw_difference_offsets'])
for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','SOURCE-TREE','PROVIDER-TREE','config.sha256','gki-symvers.sha256','interconnect.Module.symvers','natural-external-provider.symvers','crc-witnesses.tsv','provider-object.sha256']:
    assert (ICC_PACK/'evidence/build'/('B1-'+f)).read_bytes()==(ICC_PACK/'evidence/build'/('B2-'+f)).read_bytes(), 'interconnect B1/B2 '+f
for stem,artifact in [('kdm','SOURCE-TREE'),('prov','PROVIDER-TREE')]:
    assert (ICC_PACK/'evidence/build'/('B1-'+artifact)).read_text()==(ICC_REPO/'reference'/(stem+'-tree.txt')).read_text()
assert (ICC_PACK/'evidence/build/B1-natural-external-provider.symvers').read_bytes()==(ICC_REPO/'reference/external-provider.symvers').read_bytes()
icc_result=json.loads((ICC_PACK/'evidence/acceptance/result.json').read_text())
assert icc_result['unresolved']==0 and icc_result['source_crc_licence_kcfi_boundary_checks']==33 and icc_result['actual_reverse_imports']==7
assert icc_result['target_objects_per_build']==10 and icc_result['provider_objects_per_build']==12
icc_load=read_table(ICC_PACK/'evidence/inventory/LOAD-ORDER.tsv')
icc_positions={'mmqos-common':('61','59'),'mmqos-mt6878':('62','60'),'mtk-emi':('51','50')}
for m,(normal,recovery) in icc_positions.items():
    for kind,seq in [('NORMAL',normal),('RECOVERY',recovery)]:
        r=next(r for r in icc_load if r['entry']==m+'.ko' and r['kind']==kind)
        assert r['sequence']==seq and digest(ROOT/r['list_path'])==r['list_sha256']
for stock in STOCK.values():
    m=stock['filename'].removesuffix('.ko')
    if m not in icc_targets:continue
    v=icc_acceptance[m]
    assert stock['stock_sha256']==icc_targets[m] and v['functions']==stock['function_count'] and v['data']==stock['data_count']
    add(stock,source_status='A',source_repo=ref(ICC_REPO),source_commit=ICC_HEAD,
        source_pin=ref(ICC_REPO/'SOURCE-PINS.tsv'),build_script=ref(ICC_REPO/'scripts/b1b2.sh'),source_snapshot_path=ref(ICC_REPO/'patches'),
        parity_evidence=[ref(ICC_PACK/'evidence/acceptance/acceptance.json'),ref(ICC_PACK/'MODULE-PARITY.tsv'),
            ref(ICC_PACK/'evidence/build/b1b2-clean-checkout.log'),ref(ICC_PACK/'evidence/acceptance/PROVIDER-ABI-WITNESSES.tsv'),ref(ICC_PACK/'RECONSTRUCTION-REPORT.md')],
        exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,
        abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',
        verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',
        preservation_risk='LOW: immutable public pins, Kbuild-only patches, unchanged C/headers, independent recovery mirror and committed recipe/bundle; separate provider gaps remain',
        source_group='INTERCONNECT-EMI',blocker='NONE',gap_kind='NONE',load_order=icc_positions[m][0],
        firmware_boundary='VCP/secure-world/DRAMC/EMI controller policy remains separate; no firmware accessed/rebuilt or runtime bandwidth/channel/clock state certified')

# IOMMU: one authorized target, unchanged ALPS C/header inputs, genuine18 provider
# CRC/licence/CFI witnesses; debug/secure/test stay separate uncertified projects.
IOMMU_REPO=WORKSPACE/'android_kernel_modules_iommu_ulefone_gq5012bf1'
IOMMU_PACK=ROOT/'reverse-engineering/kernel-source-reconstruction/IOMMU'
IOMMU_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=IOMMU_REPO,text=True).strip()
assert IOMMU_HEAD==(IOMMU_PACK/'source/COMMIT').read_text().strip()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=IOMMU_REPO,text=True).strip(), 'iommu recipe dirty'
iommu_acceptance=json.loads((IOMMU_PACK/'evidence/acceptance/acceptance.json').read_text())
iommu_refs={r['module']:r for r in read_table(IOMMU_REPO/'reference/stock-normalized.tsv')}
assert set(iommu_acceptance)==set(iommu_refs)=={'mtk_iommu'}
iv=iommu_acceptance['mtk_iommu'];ir=iommu_refs['mtk_iommu']
assert iv['stock_sha256']==ir['stock_sha256']=='8398de841de67529967c09b144292faa88ca86685df110e05f46b4fb1d8b75c5'
assert iv['bytes']==int(ir['bytes'])==107408 and iv['unresolved']==0
assert iv['normalized_sha256']==ir['normalized_sha256']=='7f88162b28c3f45fdab0a38d29d12a7f2b9c24a40f35ccee46dde9a6b2dac4b0'
assert iv['allowed_range']==[int(ir['build_id_offset'],0),20]==[0xea50,20]
assert len(iv['raw_difference_offsets'])==iv['raw_differing_bytes']<=20
assert all(0xea50<=i<0xea64 for i in iv['raw_difference_offsets'])
for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','SOURCE-TREE','PROVIDER-TREE','config.sha256','gki-symvers.sha256','iommu.Module.symvers','natural-external-provider.symvers','crc-witnesses.tsv','provider-object.sha256']:
    assert (IOMMU_PACK/'evidence/build'/('B1-'+f)).read_bytes()==(IOMMU_PACK/'evidence/build'/('B2-'+f)).read_bytes(), 'iommu B1/B2 '+f
for stem,artifact in [('kdm','SOURCE-TREE'),('prov','PROVIDER-TREE')]:
    assert (IOMMU_PACK/'evidence/build'/('B1-'+artifact)).read_text()==(IOMMU_REPO/'reference'/(stem+'-tree.txt')).read_text()
assert (IOMMU_PACK/'evidence/build/B1-natural-external-provider.symvers').read_bytes()==(IOMMU_REPO/'reference/external-provider.symvers').read_bytes()
ii=json.loads((IOMMU_PACK/'evidence/acceptance/result.json').read_text())
assert ii['unresolved']==0 and ii['source_crc_licence_kcfi_boundary_checks']==18
assert ii['target_objects_per_build']==2 and ii['provider_objects_per_build']==3 and ii['actual_reverse_imports']==0
assert json.loads((IOMMU_PACK/'evidence/acceptance/mutation-tests.json').read_text())['all_pass']
iommu_load=read_table(IOMMU_PACK/'evidence/inventory/LOAD-ORDER.tsv')
for kind,seq in [('NORMAL','65'),('RECOVERY','63')]:
    r=next(r for r in iommu_load if r['entry']=='mtk_iommu.ko' and r['kind']==kind)
    assert r['sequence']==seq and digest(ROOT/r['list_path'])==r['list_sha256']
for stock in STOCK.values():
    if stock['filename']!='mtk_iommu.ko':continue
    assert stock['stock_sha256']==iv['stock_sha256'] and iv['functions']==stock['function_count'] and iv['data']==stock['data_count']
    add(stock,source_status='A',source_repo=ref(IOMMU_REPO),source_commit=IOMMU_HEAD,
        source_pin=ref(IOMMU_REPO/'SOURCE-PINS.tsv'),build_script=ref(IOMMU_REPO/'scripts/b1b2.sh'),source_snapshot_path=ref(IOMMU_REPO/'patches'),
        parity_evidence=[ref(IOMMU_PACK/'evidence/acceptance/acceptance.json'),ref(IOMMU_PACK/'MODULE-PARITY.tsv'),
            ref(IOMMU_PACK/'evidence/build/b1b2-clean-checkout.log'),ref(IOMMU_PACK/'evidence/acceptance/PROVIDER-ABI-WITNESSES.tsv'),ref(IOMMU_PACK/'RECONSTRUCTION-REPORT.md')],
        exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,
        abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',
        verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',
        preservation_risk='LOW: immutable public pins, Kbuild-only scope, unchanged22 public C/header inputs, independent clean builds/public mirror and committed recipe/bundle; providers remain separately uncertified',
        source_group='IOMMU',blocker='NONE',gap_kind='NONE',load_order='65',
        firmware_boundary='Exact normal-world host SMC/bank contract only; secure firmware, runtime translations/TTBR/groups/IRQ/PM state remain unvalidated; no hardware accessed')

# Frozen platform batch01:35 measured independent builds,31 accepted,4 explicit C residuals.
BATCH_PACK=ROOT/'reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-01'
batch_rows=read_table(BATCH_PACK/'BATCH-MANIFEST.tsv')
batch_parity={r['module_id']:r for r in read_table(BATCH_PACK/'BATCH-PARITY.tsv')}
batch_repos={r['family']:r for r in read_table(BATCH_PACK/'SOURCE-REPOSITORIES.tsv')}
batch_accept=json.loads((BATCH_PACK/'evidence/acceptance.json').read_text())
batch_clean=json.loads((BATCH_PACK/'evidence/cleancheck-result.json').read_text())
assert len(batch_rows)==len(batch_parity)==35 and len(batch_accept)==31
assert digest(BATCH_PACK/'BATCH-MANIFEST.tsv')=='c381b5b8fd770dd02aa4f73a062e9d40c0d0e1ce7d920d6225c59aef4c9dd813'
assert batch_clean['result']=='PASS_31_ACCEPTED_4_REPRODUCED_ABI_RESIDUALS'
assert batch_clean['original_development_and_all_four_recipes_unavailable_during_build']
assert batch_clean['raw_modules_deterministic']==batch_clean['stripped_modules_deterministic']==35
assert batch_clean['intermediate_object_count']==120
assert json.loads((BATCH_PACK/'evidence/acceptance-mutation-tests.json').read_text())['all_pass']
for family,q in batch_repos.items():
    repo=(ROOT/q['repository']).resolve()
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==q['commit']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip()
    assert (BATCH_PACK/family/'source/COMMIT').read_text().strip()==q['commit']
    owned=json.loads((repo/'families/OWNERSHIP.json').read_text())['owned_modules']
    assert set(owned)=={r['filename'].removesuffix('.ko') for r in batch_rows if r['dependency_group']==family}
for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','config.sha256','gki-symvers.sha256','TARGET-SOURCE-TREE','batch-full.Module.symvers','batch-stock-provider.Module.symvers','provider/natural-external-provider.symvers','provider/scpsys-dummy.symvers','provider/provider-witnesses.json','provider/scpsys-link-name-witnesses.json']:
    assert (BATCH_PACK/'evidence/build/B1'/f).read_bytes()==(BATCH_PACK/'evidence/build/B2'/f).read_bytes(), 'batch01 B1/B2 '+f
batch_comparison={r['module_id']:r for r in json.loads((BATCH_PACK/'evidence/comparison-B1.json').read_text())}
for r in batch_rows:
    stock=STOCK[r['module_id']];p=batch_parity[r['module_id']];q=batch_repos[r['dependency_group']];repo=(ROOT/q['repository']).resolve();m=stock['filename'].removesuffix('.ko')
    assert stock['stock_sha256']==r['stock_sha256']
    common=dict(source_repo=q['repository'],source_commit=q['commit'],source_pin=ref(repo/'SOURCE-PINS.tsv'),build_script=ref(repo/'scripts/bulk-build.sh'),source_snapshot_path=ref(repo/'patches'),
        reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',preservation_risk='LOW: immutable public pins/shared offline mirror, complete patches, four committed family clones and recovery bundles; original trees unavailable during independent35-module builds',
        firmware_boundary='Normal-world host source only; secure CMDQ/GZ, VCP/MCUPM/SSPM firmware, actual DMA/IRQ/clock/power transitions and runtime binding remain unvalidated')
    if p['final_class']=='A':
        v=batch_accept[m];assert v['stock_sha256']==stock['stock_sha256'] and v['functions']==stock['function_count'] and v['data']==stock['data_count'] and v['unresolved']==0
        refs={x['module']:x for x in read_table(repo/'reference/stock-normalized.tsv')};assert v['normalized_sha256']==refs[m]['normalized_sha256'] and v['bytes']==int(refs[m]['bytes'])
        assert v['allowed_range']==[int(refs[m]['build_id_offset'],0),20]
        assert len(v['raw_difference_offsets'])==v['raw_differing_bytes']<=20 and all(v['allowed_range'][0]<=i<v['allowed_range'][0]+20 for i in v['raw_difference_offsets'])
        add(stock,**common,source_status='A',source_group='PLATFORM-BATCH-01:'+r['dependency_group'],exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,
            abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',blocker='NONE',gap_kind='NONE',
            parity_evidence=[ref(BATCH_PACK/r['dependency_group']/'evidence/acceptance'/m/'acceptance.json'),ref(BATCH_PACK/'evidence/cleancheck-result.json'),ref(BATCH_PACK/'BATCH-PARITY.tsv'),ref(BATCH_PACK/'BUILD-REPRODUCTION.md')])
    else:
        x=batch_comparison[r['module_id']];assert p['final_class']=='C' and x['functions_exact']==stock['function_count']
        add(stock,**common,source_status='C',source_group='FINISH:CMDQ-MAILBOX-ABI',exact_functions=x['functions_exact'],equivalent_functions=0,
            historical_parity='PARTIAL_SOURCE_BUILD_PARITY_BATCH01',abi_status='INCOMPLETE_ACCEPTANCE',crc_status='SOURCE_CRC_GRAPH_MISMATCH',kcfi_status='ABS_IDS_AND_REQUIRED_PROVIDER_PREFIXES_MATCH_CRC_GRAPH_UNCLOSED',
            blocker='Deterministic full source build; all function bytes exact, but '+str(len(x['import_crc_mismatches']))+' import and '+str(len(x['export_crc_mismatches']))+' export CRC mismatches plus symbol-counter residue prevent full stock acceptance. Preserve recursive symtypes; OEM-matching declarations required, exact differing field unlocated.',gap_kind='CODE_OR_ABI_PARITY',
            parity_evidence=[ref(BATCH_PACK/'evidence/comparison-B1.json'),ref(BATCH_PACK/'BLOCKERS.tsv'),ref(BATCH_PACK/'CMDQ-MAILBOX/evidence/type-investigation/public-header-investigation.json')])

# Batch02:exact27 frozen identities,21D/6G ->A only after four real clone engines B1/B2.
BATCH02=ROOT/'reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-02'
b2rows=read_table(BATCH02/'BATCH-MANIFEST.tsv');b2repos={r['family']:r for r in read_table(BATCH02/'SOURCE-REPOSITORIES.tsv')}
b2accept=json.loads((BATCH02/'evidence/acceptance.json').read_text());b2clean=json.loads((BATCH02/'evidence/cleancheck-result.json').read_text())
assert len(b2rows)==len(b2accept)==27
assert digest(BATCH02/'BATCH-MANIFEST.tsv')=='6b4245dadf20a2ca0cb10058313101ab5d37d53694b0d28cacef661b27301b6f'
assert b2clean['result']=='PASS_ALL27_FOUR_INDEPENDENT_FAMILY_ENGINES_B1_B2'
assert b2clean['fresh_complete_compilations']==8 and b2clean['fresh_committed_source_clones']==4
assert b2clean['original_development_and_all_four_recipe_paths_unavailable_during_eight_compilations']
assert b2clean['all_27_accepted_each_run'] and b2clean['cross_family_source_config_abi_objects_raw_stripped_identical']
assert json.loads((BATCH02/'evidence/acceptance-mutation-tests.json').read_text())['all_pass']
for i,(family,q) in enumerate(b2repos.items()):
    repo=(ROOT/q['repository']).resolve();subprocess.run(['git','merge-base','--is-ancestor',q['commit'],'HEAD'],cwd=repo,check=True)
    # Advancing shared HEAD never changes the already accepted immutable Batch02 recipe.
    pinned=lambda path:subprocess.check_output(['git','show',q['commit']+':'+path],cwd=repo,text=True)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip()
    assert not any(p.endswith(('.o','.ko','.pyc')) for p in subprocess.check_output(['git','ls-files'],cwd=repo,text=True).splitlines())
    assert (BATCH02/family/'source/COMMIT').read_text().strip()==q['commit']
    assert set(json.loads(pinned('families/OWNERSHIP.json'))['owned_modules'])=={r['filename'].removesuffix('.ko') for r in b2rows if r['dependency_group']==family}
    for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','config.sha256','gki-symvers.sha256','TARGET-SOURCE-TREE','batch-full.Module.symvers','provider/natural-external-provider.symvers','provider/provider-witnesses.json','provider/provider-errors.json']:
        assert (BATCH02/f'evidence/build/F{i}-B1'/f).read_bytes()==(BATCH02/f'evidence/build/F{i}-B2'/f).read_bytes(),f
    assert b2clean['families'][i]['source_commit']==q['commit'] and b2clean['families'][i]['intermediate_object_count']==105
for r in b2rows:
    stock=STOCK[r['module_id']];m=stock['filename'].removesuffix('.ko');v=b2accept[m];q=b2repos[r['dependency_group']];repo=(ROOT/q['repository']).resolve()
    assert stock['stock_sha256']==r['stock_sha256']==v['stock_sha256']
    assert v['functions']==stock['function_count'] and v['data']==stock['data_count'] and v['unresolved']==0
    import io
    refs={x['module']:x for x in csv.DictReader(io.StringIO(subprocess.check_output(['git','show',q['commit']+':reference/stock-normalized.tsv'],cwd=repo,text=True)),delimiter='\t')};assert v['normalized_sha256']==refs[m]['normalized_sha256'] and v['bytes']==int(refs[m]['bytes'])
    assert v['allowed_range']==[int(refs[m]['build_id_offset'],0),20]
    assert len(v['raw_difference_offsets'])==v['raw_differing_bytes']<=20 and all(v['allowed_range'][0]<=i<v['allowed_range'][0]+20 for i in v['raw_difference_offsets'])
    add(stock,source_status='A',source_group='PLATFORM-BATCH-02:'+r['dependency_group'],source_repo=q['repository'],source_commit=q['commit'],source_pin=ref(repo/'SOURCE-PINS.tsv'),build_script=ref(repo/'scripts/bulk-build.sh'),source_snapshot_path=ref(repo/'patches'),
        exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',abi_status='VERIFIED',crc_status='VERIFIED',kcfi_status='VERIFIED',verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',blocker='NONE',gap_kind='NONE',
        preservation_risk='LOW: public immutable pins, full Kbuild-only patches, independent four-clone eight-build proof, source hashes and recovery bundles;no cached target/provider object inputs',
        firmware_boundary='Normal-world memory/PMIF/mailbox/policy host source only;secure calls,TinySys/MCUPM/SSPM/SCP/VCP/GPUEB firmware and actual MMIO/IRQ/traffic/startup remain separate and unvalidated',
        parity_evidence=[ref(BATCH02/r['dependency_group']/'evidence/acceptance'/m/'acceptance.json'),ref(BATCH02/'evidence/cleancheck-result.json'),ref(BATCH02/'evidence/PROVIDER-GRAPH.tsv'),ref(BATCH02/'BATCH-PARITY.tsv'),ref(BATCH02/'BUILD-REPRODUCTION.md')])

# Batch03:34 frozen identities,33 full-accepted A and one explicit native BTF C.
BATCH03=ROOT/'reverse-engineering/kernel-source-reconstruction/PLATFORM-BATCH-03'
b3rows=read_table(BATCH03/'BATCH-MANIFEST.tsv');b3parity={r['module_id']:r for r in read_table(BATCH03/'BATCH-PARITY.tsv')};b3repos={r['family']:r for r in read_table(BATCH03/'SOURCE-REPOSITORIES.tsv')}
b3accept=json.loads((BATCH03/'evidence/acceptance.json').read_text());b3clean=json.loads((BATCH03/'evidence/cleancheck-result.json').read_text())
assert len(b3rows)==len(b3parity)==34 and len(b3accept)==33
assert digest(BATCH03/'BATCH-MANIFEST.tsv')=='07940aeefe13a9c3fa50a2ba2e8fb9cee75ce1e057942b0d5da34215896246d5'
assert b3clean['result']=='PASS_ALL34_FIVE_INDEPENDENT_FAMILY_ENGINES_B1_B2'
assert b3clean['fresh_complete_compilations']==10 and b3clean['fresh_committed_source_clones']==5
assert b3clean['original_development_and_all_five_recipe_paths_unavailable_during_ten_compilations']
assert b3clean['accepted_each_run']==33 and b3clean['explicit_C_blockers_each_run']==1 and b3clean['all_34_built_each_run']
assert b3clean['cross_family_source_config_abi_objects_raw_stripped_identical']
assert json.loads((BATCH03/'evidence/acceptance-mutation-tests.json').read_text())['all_pass']
for i,(family,q) in enumerate(b3repos.items()):
    repo=(ROOT/q['repository']).resolve();assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==q['commit']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip()
    assert (BATCH03/family/'source/COMMIT').read_text().strip()==q['commit']
    assert set(json.loads((repo/'families/OWNERSHIP.json').read_text())['owned_modules'])=={r['filename'].removesuffix('.ko') for r in b3rows if r['dependency_group']==family}
    for f in ['SHA256SUMS','INTERMEDIATE-SHA256SUMS','NATIVE-INTERMEDIATE-SHA256SUMS','native-config.sha256','config.sha256','gki-symvers.sha256','TARGET-SOURCE-TREE','batch-full.Module.symvers','provider/natural-external-provider.symvers','provider/provider-witnesses.json','provider/provider-errors.json']:
        assert (BATCH03/f'evidence/build/F{i}-B1'/f).read_bytes()==(BATCH03/f'evidence/build/F{i}-B2'/f).read_bytes(),f
    assert b3clean['families'][i]['source_commit']==q['commit'] and b3clean['families'][i]['joint_modules_accepted']==33
for r in b3rows:
    stock=STOCK[r['module_id']];m=stock['filename'].removesuffix('.ko');p=b3parity[r['module_id']];q=b3repos[r['dependency_group']];repo=(ROOT/q['repository']).resolve()
    common=dict(source_repo=q['repository'],source_commit=q['commit'],source_pin=ref(repo/'SOURCE-PINS.tsv'),build_script=ref(repo/'scripts/bulk-build.sh'),source_snapshot_path=ref(repo/'patches'),exact_functions=stock['function_count'],equivalent_functions=0,unresolved_functions=0,reproduction_status='INDEPENDENT_CLEAN_CHECKOUT_B1_B2',crc_status='VERIFIED',kcfi_status='VERIFIED',preservation_risk='LOW: maintained pinned source, full patches, five committed clone ten-build proof and recovery bundles; metadata acceptance remains explicitly scoped',firmware_boundary='Normal-world host interfaces only; ARM secure RNG/SiP services, SSPM/SCMI firmware, crash capture and actual thermal/power/MMIO behavior remain separately unvalidated')
    if m=='thermal-generic-adc':
        v=json.loads((BATCH03/'THERMAL-COOLING/evidence/incomplete-acceptance/thermal-generic-adc/incomplete-acceptance.json').read_text())
        assert p['final_class']=='C' and v['unresolved']==1 and v['btf_bytes_different']==21
        assert v['stock_sha256']==stock['stock_sha256']==r['stock_sha256'] and v['functions']==stock['function_count'] and v['data']==stock['data_count']
        assert v['code_data_abi_raw_semantic_relocations_metadata_layout_exact']
        add(stock,**common,source_status='C',source_group='FINISH:NATIVE-COMMON-ADC-BTF-BASE',abi_status='CODE_DATA_CRC_KCFI_RELOCATIONS_EXACT_BTF_BASE_INCOMPLETE',verified_difference_classification='GNU20_BUILD_ID_PLUS21_BTF_REFERENCE_BYTES_UNACCEPTED',blocker=v['blocker']+'. '+v['next_experiment'],gap_kind='CODE_OR_ABI_PARITY',parity_evidence=[ref(BATCH03/'THERMAL-COOLING/evidence/incomplete-acceptance/thermal-generic-adc/incomplete-acceptance.json'),ref(BATCH03/'BLOCKERS.tsv'),ref(BATCH03/'evidence/cleancheck-result.json'),ref(BATCH03/'evidence/native-lineage-revisit/result.json')])
    else:
        v=b3accept[m];assert p['final_class']=='A' and stock['stock_sha256']==r['stock_sha256']==v['stock_sha256']
        assert v['functions']==stock['function_count'] and v['data']==stock['data_count'] and v['unresolved']==0
        refs={x['module']:x for x in read_table(repo/'reference/stock-normalized.tsv')};assert v['normalized_sha256']==refs[m]['normalized_sha256'] and v['bytes']==int(refs[m]['bytes'])
        assert v['allowed_range']==[int(refs[m]['build_id_offset'],0),20]
        assert len(v['raw_difference_offsets'])==v['raw_differing_bytes']<=20 and all(v['allowed_range'][0]<=i<v['allowed_range'][0]+20 for i in v['raw_difference_offsets'])
        add(stock,**common,source_status='A',source_group='PLATFORM-BATCH-03:'+r['dependency_group'],abi_status='VERIFIED',verified_difference_classification='BUILD_METADATA_ONLY (20-byte GNU build ID)',blocker='NONE',gap_kind='NONE',parity_evidence=[ref(BATCH03/r['dependency_group']/'evidence/acceptance'/m/'acceptance.json'),ref(BATCH03/'evidence/cleancheck-result.json'),ref(BATCH03/'evidence/PROVIDER-GRAPH.tsv'),ref(BATCH03/'BATCH-PARITY.tsv'),ref(BATCH03/'BUILD-REPRODUCTION.md')])

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
