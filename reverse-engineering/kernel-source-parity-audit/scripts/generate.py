#!/usr/bin/env python3
"""Deterministically derive the complete audit tables and dependency-aware queue."""
import collections
import csv
import hashlib
import json
import lzma
from pathlib import Path
import re
from inventory import ROOT, AUDIT, WORKSPACE, STOCK_ROOTS, read_table

STOCK=json.loads((AUDIT/'evidence/stock-identities.json').read_text())
REVIEWS=json.loads((AUDIT/'evidence/source-reviews.json').read_text())
BASE=json.loads((AUDIT/'evidence/workspace-baseline.json').read_text())
LOAD={r['module']:r for r in read_table(ROOT/'reverse-engineering/boot/module-loading/module-classification.tsv')}
NORM=lambda x:x.removesuffix('.ko').replace('-','_')

def write_tsv(path, rows, fields=None):
    fields=fields or list(rows[0])
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n',extrasaction='ignore')
        w.writeheader();w.writerows(rows)

def ref(p):
    p=Path(p).resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else '../'+str(p.relative_to(WORKSPACE)) if p.is_relative_to(WORKSPACE) else str(p)

# Complete import/export graph; providers are resolved by both export name and CRC.
symvers=WORKSPACE/'android_kernel_modules_camera_isp_ulefone_gq5012bf1/reference/gki-12901745-vmlinux.symvers.xz'
core={}
for line in lzma.decompress(symvers.read_bytes()).decode().splitlines():
    x=line.split()
    if len(x)>=4 and x[2]=='vmlinux':core[x[1]]=(int(x[0],16),x[3])
providers=collections.defaultdict(list)
for identity,row in STOCK.items():
    for name,definition in row['exports'].items():providers[name].append((identity,definition))
EDGES=[];reverse=collections.defaultdict(set);dependencies=collections.defaultdict(set)
for identity,row in STOCK.items():
    for symbol,crc in sorted(row['imports'].items()):
        matching=[(pid,e) for pid,e in providers.get(symbol,[]) if e['crc']==crc]
        raw=[pid for pid,e in providers.get(symbol,[])]
        kernel=core.get(symbol)
        if kernel and kernel[0]==crc:
            resolved='GKI_CORE';ptype=kernel[1];result='CRC_MATCH'
        elif matching:
            resolved=';'.join(sorted(pid for pid,e in matching));ptype=';'.join(sorted({e['export_type'] for pid,e in matching}));result='CRC_MATCH' if len(matching)==1 else 'MULTIPLE_CRC_MATCHING_IDENTITIES_RUNTIME_PROVIDER_UNPROVEN'
            for pid,e in matching:reverse[pid].add(identity);dependencies[identity].add(pid)
        else:
            resolved='UNKNOWN';ptype='UNKNOWN';result='PROVIDER_UNRESOLVED' if not raw and not kernel else 'NO_STOCK_EXPORT_CRC_MATCH'
        EDGES.append(dict(consumer_module_id=identity,symbol=symbol,required_crc=f'0x{crc:08x}',provider_module_ids=resolved,
            export_type=ptype,result=result,nonmatching_stock_provider_candidates=';'.join(sorted(set(raw)-{pid for pid,e in matching})) or 'NONE',
            kcfi_requirement='CRC equality does not establish provider KCFI; callsite/type proof required during reconstruction',
            evidence='reverse-engineering/kernel-source-parity-audit/evidence/stock-identities.json'))
write_tsv(AUDIT/'DEPENDENCY-EDGES.tsv',EDGES)

# Independently record actual load-list mentions, keyed to partition-specific binaries.
LISTS=[];mentions=collections.defaultdict(list)
for partition,root in STOCK_ROOTS.items():
    for path in sorted((root/'lib/modules').glob('modules.load*')):
        if not path.is_file():continue
        for sequence,line in enumerate(path.read_text().splitlines(),1):
            name=line.split('#',1)[0].strip()
            if not name:continue
            matches=[identity for identity,row in STOCK.items() if partition in row['partitions'] and NORM(row['filename'])==NORM(Path(name).name)]
            item=dict(partition=partition,list_path=ref(path),list_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),sequence=sequence,entry=name,
                matching_module_ids=';'.join(matches) or 'UNKNOWN',kind='RECOVERY' if 'recovery' in path.name else 'NORMAL')
            LISTS.append(item)
            for identity in matches:mentions[identity].append(ref(path)+':'+str(sequence))
write_tsv(AUDIT/'LOAD-LIST-EVIDENCE.tsv',LISTS)

# Source-input snapshots are metadata hashes, never binary/source payload copies.
INPUTS={}
for identity,review in REVIEWS.items():
    refs=set(review['parity_evidence'])
    for field in ['component_evidence','candidate_evidence','source_pin','build_script','binding_evidence']:
        value=review.get(field,'UNKNOWN')
        if value!='UNKNOWN' and (ROOT/value).is_file():refs.add(value)
    src=ROOT/review['source_snapshot_path'] if review['source_snapshot_path']!='UNKNOWN' else None
    if src and src.is_dir():
        for p in src.rglob('*'):
            if p.is_file() and (p.suffix in ['.c','.h','.S','.inc','.patch','.diff','.sh','.py','.symvers'] or p.name in ['Makefile','Kbuild','Kconfig','SOURCE-PINS.tsv']):refs.add(ref(p))
    records={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(refs) if (ROOT/p).is_file()}
    INPUTS[identity]=records
(AUDIT/'evidence/review-input-hashes.json').write_text(json.dumps(INPUTS,indent=2,sort_keys=True)+'\n')

CLOCK_CORE=['clk-common.ko','clk-mt6878.ko','clk-mt6878-bus.ko','clk-mt6878-peri.ko','clk-mt6878-vlp.ko','clk-fmeter-mt6878.ko']
assert all(sum(s['filename']==n for s in STOCK.values())==1 for n in CLOCK_CORE)
ALL=[]
for identity,stock in STOCK.items():
    review=dict(REVIEWS[identity]);load=LOAD[NORM(stock['filename'])]
    if load['resolved_phase']=='first-stage':
        review.update(necessity='REQUIRED_BY_RETAINED_FIRST_STAGE_LOAD_CONTRACT',necessity_evidence='reverse-engineering/boot/module-loading/module-classification.tsv')
    if stock['filename'] in CLOCK_CORE and review['source_status'] not in ['A','B','F']:
        review['source_group']='BOOT-CLOCK-CORE';review['priority']='P0_BOOT'
    elif review['source_status'] in ['A','B']:review['priority']='VERIFIED_NO_RECONSTRUCTION'
    elif review['optional_review']:review['priority']='P4_DIAGNOSTIC_OR_REFERENCE'
    elif load['resolved_phase']=='first-stage':review['priority']='P0_BOOT'
    elif any(s in review['source_group'] for s in ['CONNECTIVITY','MODEM','GNSS','BT','WIFI','GZ-','TKCORE','TRUSTKERNEL','TMEM','FFA']):review['priority']='P1_RADIO_OR_SECURITY'
    elif any(s in review['source_group'] for s in ['AUDIO','SENSOR','DISPLAY','TOUCH','NFC','FUEL','CHARG','CAMERA','LDO','PWM','LED','KEY','COMPANION','USB']):review['priority']='P2_ACTIVE_FEATURE'
    elif review['runtime_status']=='RECORDED_LOADED':review['priority']='P3_LOADED_PLATFORM_OR_OPTIONAL'
    review['source_owner']=review['source_group']
    review['public_source_pins']=review['source_pin']
    if review['source_status']=='C':
        # The immutable reconstructed-source snapshot is a pin even when no public original exists.
        material=''.join(f'{p}\t{h}\n' for p,h in sorted(INPUTS[identity].items()))
        review['source_pin']='sha256:'+hashlib.sha256(material.encode()).hexdigest()
    row=dict(module_id=identity,filename=stock['filename'],stock_paths=';'.join(stock['stock_paths']),stock_sha256=stock['stock_sha256'],stock_size=stock['stock_size'],partitions=';'.join(stock['partitions']))
    row.update(review);row['parity_evidence']=';'.join(review['parity_evidence']) or 'UNKNOWN'
    row.update(load_list_mentions=';'.join(mentions[identity]) or 'NONE_IN_EXTRACTED_LISTS',
        consumed_status='STATIC_IMPORT_PROVIDER_ONLY_EXECUTION_UNPROVEN' if reverse[identity] else 'NO_SHIPPED_REVERSE_IMPORT_NOT_PROOF_OF_NO_CONSUMER',
        stock_functions=stock['function_count'],stock_data_objects=stock['data_count'],stock_imports=len(stock['imports']),stock_exports=len(stock['exports']),
        stock_kcfi_abs_ids=stock['kcfi_abs_count'],stock_relocations=stock['relocation_count'],stock_sections=stock['section_count'],
        reverse_importer_count=len(reverse[identity]),provider_dependencies=';'.join(sorted(dependencies[identity])) or 'GKI_CORE_ONLY_OR_UNRESOLVED',
        dependency_evidence='reverse-engineering/kernel-source-parity-audit/DEPENDENCY-EDGES.tsv',
        source_review_evidence='reverse-engineering/kernel-source-parity-audit/evidence/source-reviews.json',
        input_hash_evidence='reverse-engineering/kernel-source-parity-audit/evidence/review-input-hashes.json')
    ALL.append(row)
fields=list(ALL[0])
for row in ALL:
    for key in row:
        if key not in fields:fields.append(key)
for row in ALL:
    for key in fields:
        if key not in row or row[key]=='':row[key]='UNKNOWN'
write_tsv(AUDIT/'ALL-457-MODULES.tsv',ALL,fields)
GAPS=[r for r in ALL if r['source_status'] not in ['A','B','F']]
write_tsv(AUDIT/'SOURCE-GAPS.tsv',GAPS,fields)
write_tsv(AUDIT/'DONE-SOURCE-EVIDENCE-DISCREPANCIES.tsv',[r for r in GAPS if r['component_status']=='DONE'],fields)
RISKS=[]
for row in ALL:
    if row['source_status'] not in ['C','G']:continue
    p=ROOT/row['build_script'];text=p.read_text(errors='replace') if p.is_file() else ''
    lines=[l.strip() for l in text.splitlines() if any(s in l for s in ['/tmp/','kernel-work','stock-all.symvers','stock-ext.symvers','KERNEL_SRC','KBUILD_EXTRA_SYMBOLS','COMMON_OUT_DIR','gImage_logo','sinofs_afi','/lieppos/','$G/lieppos'])]
    RISKS.append(dict(module_id=row['module_id'],filename=row['filename'],source_status=row['source_status'],recipe=row['build_script'],
        observed_recipe_input_references=' | '.join(lines[:8]) or 'NO_SELF_CONTAINED_BOOTSTRAP_OR_INPUT_ASSERTIONS_IDENTIFIED',
        historical_proof=row['parity_evidence'],source_snapshot=row['source_snapshot_path'],
        unresolved_evidence='Independent reconstruction of exact source/headers/config/provider inputs from the preserved recipe has not been demonstrated by the reviewed records. This is not a finding that known code must be reverse-engineered again.'))
write_tsv(AUDIT/'REPRODUCIBILITY-RISKS.tsv',RISKS)
write_tsv(AUDIT/'SOURCE-OWNERSHIP.tsv',[dict(module_id=r['module_id'],filename=r['filename'],component_owner=r['component_owner'],
    component_status=r['component_status'],canonical_component_status=r['canonical_component_status'],source_owner=r['source_owner'],
    source_repo=r['source_repo'],source_commit=r['source_commit'],evidence=r['component_evidence']) for r in ALL])

# Reevaluate ALL 15 old unused/reference names; no unproved F exclusions.
OPTIONAL=[]
for row in ALL:
    if not row['optional_review']:continue
    name=row['filename'];role='MET profiling/engineering helper' if name.startswith('met') else 'Mali DMA-BUF diagnostic test' if name.startswith('mali_dmabuf_test') else 'generic NFC core (ST21 uses separate misc-device path)' if name=='nfc.ko' else 'alternative TFA98xx amplifier driver' if name=='snd-soc-tfa98xx.ko' else 'scheduler extension; old MET grouping does not prove purpose or dispensability'
    stock=STOCK[row['module_id']]
    OPTIONAL.append(dict(module_id=row['module_id'],filename=name,source_status=row['source_status'],role=role,
        normal_load_list=row['normal_load_list'],runtime_status=row['runtime_status'],reverse_importers=';'.join(sorted(reverse[row['module_id']])) or 'NONE_IN_SHIPPED_IMPORT_GRAPH',
        dt_aliases=';'.join(stock['modinfo'].get('alias',[])) or 'NO_ALIAS_DECLARED_NOT_PROOF_OF_NO_HARDWARE',
        userspace_consumers='UNKNOWN: absence not established exhaustively',
        engineering_use='POTENTIALLY_USEFUL' if name!='nfc.ko' and name!='snd-soc-tfa98xx.ko' else 'CONFIGURATION_DEPENDENT',
        production_necessity='INSUFFICIENTLY_VERIFIED; no authorized production exclusion policy',
        removal_safety='UNPROVEN: adjust loader/config and test boot/subsystem impact before exclusion',
        exclusion_decision='NOT_F; retain in source audit',
        evidence='reverse-engineering/coverage-audit/notes/KERNEL-MODULES.md;reverse-engineering/boot/module-loading/module-classification.tsv;reverse-engineering/kernel-source-parity-audit/DEPENDENCY-EDGES.tsv'))
assert len(OPTIONAL)==15
write_tsv(AUDIT/'OPTIONAL-15-REVIEW.tsv',OPTIONAL)

# Every gap belongs to one finite source project. Dependency blockers remain separate from effort.
groups=collections.defaultdict(list)
for row in GAPS:groups[row['source_group']].append(row)
PROJECTS=[]
for group,rows in groups.items():
    own={r['module_id'] for r in rows};dep={p for r in rows for p in dependencies[r['module_id']] if p not in own}
    blocked=sorted({r['source_group'] for r in ALL if r['module_id'] in dep and r['source_status'] not in ['A','B','F']})
    priority=min(r['priority'] for r in rows)
    rank=0 if group=='BOOT-CLOCK-CORE' else 1 if group.startswith('PRESERVE:STORAGE') else 2 if 'regulator' in group or 'pinctrl' in group else 3 if any(t in group for t in ['iommu','interconnect','smi','cmdq']) else 4
    effort='SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction' if all(r['gap_kind']=='RECIPE_PRESERVATION_OR_ACCEPTANCE_EVIDENCE' for r in rows) else 'SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred' if all(r['source_status']=='D' for r in rows) else 'TARGETED_MISSING_CODE_ABI_OR_EQUIVALENCE_PROOF; exact blockers in SOURCE-GAPS.tsv'
    PROJECTS.append(dict(project=group,priority=priority,rank=rank,module_ids=';'.join(r['module_id'] for r in rows),modules=';'.join(r['filename'] for r in rows),count=len(rows),
        statuses=','.join(f'{s}:{n}' for s,n in sorted(collections.Counter(r['source_status'] for r in rows).items())),
        external_provider_ids=';'.join(sorted(dep)) or 'NONE',dependency_blocker_projects=';'.join(blocked) or 'NONE',
        effort=effort,source_locations=';'.join(sorted({r['candidate_path'] if r['source_status']=='D' else r['source_snapshot_path'] for r in rows})),
        proof_needed='Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing'))
PROJECTS.sort(key=lambda r:(r['priority'],r['rank'],r['project']))
write_tsv(AUDIT/'RECONSTRUCTION-PROJECTS.tsv',PROJECTS)

counts={s:sum(r['source_status']==s for r in ALL) for s in 'ABCDEFG'}
metrics=dict(distinct_stock_identities=len(ALL),unique_filenames=len({r['filename'] for r in ALL}),stock_occurrences=sum(len(r['stock_paths'].split(';')) for r in ALL),
    source_status_counts=counts,verified_A_B=counts['A']+counts['B'],unverified_and_unexcluded=len(GAPS),
    required_by_retained_first_stage_contract=sum(r['necessity'].startswith('REQUIRED') for r in ALL),
    required_boot_contract_gaps=sum(r['necessity'].startswith('REQUIRED') for r in GAPS),
    runtime_necessity_unknown=sum(r['necessity']=='UNKNOWN' for r in ALL),
    source_available_with_successful_historical_build=sum(r['source_status'] in ['C','G'] and r['historical_parity']!='UNKNOWN' for r in ALL),
    source_candidates_unverified=counts['D'],source_missing=counts['E'],legitimately_excluded=counts['F'],source_class_unresolved=counts['G'],
    dependency_import_records=len(EDGES),provider_resolution_counts=dict(collections.Counter(r['result'] for r in EDGES)),source_projects=len(PROJECTS),
    recorded_bound_modules=sum(r['bound_probe_status']=='RECORDED_DRIVER_MODULE_SYMLINK' for r in ALL),
    unmatched_load_list_entries=[r for r in LISTS if r['matching_module_ids']=='UNKNOWN'],
    completed_projects=['BOOT-CLOCK-CORE (6 identities D->A, 2026-10-09)','PRESERVE:STORAGE (10 identities G->A, 2026-10-09)','PINCTRL (4 identities D->A, 2026-10-09)','REGULATORS (4 identities D->A, 2026-10-09)','INTERCONNECT-EMI (3 identities D->A, 2026-10-09)','IOMMU (1 identity D->A, 2026-10-10)'],
    next_project=PROJECTS[0]['project'],next_modules=PROJECTS[0]['modules'].split(';'),
    source_counts_are_not_component_DONE_counts=True)
(AUDIT/'evidence/audit-summary.json').write_text(json.dumps(metrics,indent=2,sort_keys=True)+'\n')

queue=['# Dependency-aware kernel source reconstruction queue','',
'Frozen audit: 458 binary identities / 457 filenames. This queue does not alter existing components.',
'','## Acceptance and order','',
'1. Essential retained boot contract and storage; 2. radio/security interfaces; 3. active peripherals; 4. optional/diagnostic features.',
'Completed: BOOT-CLOCK-CORE (6 first-stage clock modules, D->A on 2026-10-09; reverse-engineering/kernel-source-reconstruction/BOOT-CLOCK-CORE). It no longer appears below.',
'Completed: PRESERVE:STORAGE (10 UFS/RPMB/MMC modules, G->A on 2026-10-09; reverse-engineering/kernel-source-reconstruction/STORAGE). It no longer appears below.',
'Completed: PINCTRL (4 pinctrl/GPIO/EINT modules, D->A on 2026-10-09; reverse-engineering/kernel-source-reconstruction/PINCTRL). It no longer appears below.',
'Completed: REGULATORS (4 regulator modules, D->A on 2026-10-09; reverse-engineering/kernel-source-reconstruction/REGULATORS). It no longer appears below.',
'Completed: INTERCONNECT-EMI (3 MMQoS/EMI modules, D->A on 2026-10-09; reverse-engineering/kernel-source-reconstruction/INTERCONNECT-EMI). It no longer appears below.',
'Completed: IOMMU (mtk_iommu only, D->A on 2026-10-10; reverse-engineering/kernel-source-reconstruction/IOMMU). Separate iommu_debug/secure/test remain uncertified.',
'The first project listed below is the current queue head.',
'`PRESERVE:*` projects must preserve/reproduce existing exact source work, not reverse-engineer it again. `G` is a finite evidence/input-closure question, not a missing-code claim.',
'All dependency entries below are stock symbol/CRC requirements. A provider gap is recorded separately from implementation effort; retained provider ABI records may support compilation but do not close that provider.',
'Firmware stays proprietary where documented. Runtime loading never proves successful hardware binding.','',
'## Complete finite project list','']
for i,p in enumerate(PROJECTS,1):
    queue += [f"### {i}. {p['project']} — {p['priority']}",f"- Modules ({p['count']}): `"+'`, `'.join(p['modules'].split(';'))+'`.',
              '- Source statuses: '+p['statuses']+'.','- Source locations: `'+p['source_locations']+'`.',
              '- Effort: '+p['effort']+'.','- Separate provider blockers: `'+p['dependency_blocker_projects']+'`.',
              '- Required proof: '+p['proof_needed']+'.','']
(AUDIT/'RECONSTRUCTION-QUEUE.md').write_text('\n'.join(queue)+'\n')
print(json.dumps(metrics,indent=2))
