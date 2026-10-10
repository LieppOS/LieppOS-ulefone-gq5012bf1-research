#!/usr/bin/env python3
"""Exact34 processed:33 A/1 C; all424 unselected rows including CMDQ unchanged."""
from pathlib import Path
import csv,json,subprocess,hashlib,collections,sys
P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit';sys.dont_write_bytecode=True
rows=lambda p:list(csv.DictReader(p.open(),delimiter='\t'));M=rows(P/'BATCH-MANIFEST.tsv');T=rows(P/'BATCH-PARITY.tsv');ids={r['module_id'] for r in M};old={r['module_id']:r for r in rows(P/'evidence/baseline/ALL-457-MODULES.tsv')};new={r['module_id']:r for r in rows(A/'ALL-457-MODULES.tsv')}
assert len(M)==len(T)==34 and len(new)==len(old)==458 and new.keys()==old.keys()
assert hashlib.sha256((P/'BATCH-MANIFEST.tsv').read_bytes()).hexdigest()=='07940aeefe13a9c3fa50a2ba2e8fb9cee75ce1e057942b0d5da34215896246d5'
assert all(old[i]==new[i] for i in new.keys()-ids),'Unselected row drift'
immutable=['stock_paths','stock_sha256','stock_size','component_owner','component_status','canonical_component_status','runtime_status'];assert all(old[i][k]==new[i][k] for i in new for k in immutable)
assert collections.Counter(old[i]['source_status'] for i in ids)=={'D':28,'G':6}
assert collections.Counter(new[i]['source_status'] for i in ids)=={'A':33,'C':1}
assert next(new[i] for i in ids if new[i]['source_status']=='C')['filename']=='thermal-generic-adc.ko'
summary=json.loads((A/'evidence/audit-summary.json').read_text());assert summary['verified_A_B']==220 and summary['unverified_and_unexcluded']==238 and summary['source_status_counts']==dict(A=219,B=1,C=9,D=98,E=0,F=0,G=131)
v=json.loads((A/'evidence/validator-result.json').read_text());assert not v['errors'];mu=json.loads((P/'evidence/acceptance-mutation-tests.json').read_text());assert mu['all_pass'] and mu['count']==16
assert 'Ran 14 tests' in (P/'evidence/audit-mutation-tests.log').read_text() and (P/'evidence/audit-mutation-tests.log').read_text().rstrip().endswith('OK')
for r in rows(P/'SOURCE-REPOSITORIES.tsv'):
 n=(R/r['repository']).resolve();assert subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip()==r['commit'];assert not subprocess.check_output(['git','-C',str(n),'status','--porcelain'],text=True).strip()
 assert not any(f.endswith(('.o','.ko','.pyc')) for f in subprocess.check_output(['git','-C',str(n),'ls-files'],text=True).splitlines())
 b=P/r['family']/'source'/f'{n.name}.bundle';p=subprocess.run(['git','-C',str(n),'bundle','verify',str(b)],capture_output=True);assert p.returncode==0
source=json.loads((P/'evidence/source-preservation-result.json').read_text());assert source['result']=='PASS_ALL_SOURCE_HASHES_PATCHES_FIVE_BUNDLE_RECOVERIES' and source['source_file_count']==6619 and len(source['bundles'])==5
contracts=json.loads((P/'evidence/SOURCE-TO-HARDWARE-CONTRACTS.json').read_text());assert {r['module_id'] for r in contracts}==ids and sum(len(r['compiled_units']) for r in contracts)==68 and not any(r['runtime_control_tested'] for r in contracts)
cmdq=['cmdq-platform-mt6878.ko','cmdq-sec-drv.ko','cmdq-test.ko','mtk-cmdq-drv-ext.ko'];assert all(r['source_status']=='C' and r==old[r['module_id']] for r in new.values() if r['filename'] in cmdq)
graph=rows(P/'evidence/PROVIDER-GRAPH.tsv');assert sum(r['axis']=='IMPORT' for r in graph)==1434 and sum(r['axis']=='EXPORT' for r in graph)==320
nextrows=rows(P/'evidence/NEXT-BATCH-PROPOSAL.tsv');assert len(nextrows)==30 and len({r['module_id'] for r in nextrows})==30
assert collections.Counter(r['current_class'] for r in nextrows)=={'D':7,'G':23} and all(new[r['module_id']]['source_status']==r['current_class'] for r in nextrows)
clean=json.loads((P/'evidence/cleancheck-result.json').read_text());assert clean['fresh_complete_compilations']==10 and clean['accepted_each_run']==33 and clean['explicit_C_blockers_each_run']==1
report={'result':'PASS_WITH_ONE_EXPLICIT_UNACCEPTED_C_BTF_TARGET','identities':458,'stock_occurrences':471,'selected_processed_built':34,'new_A':33,'new_B':0,'batch_unaccepted_C':1,'unselected_rows_field_identical':424,'four_CMDQ_C_rows_unchanged':True,'all_paths_hashes_sizes_owners_component_runtime_statuses_unchanged':True,'certified':220,'remaining':238,'source_status_counts':summary['source_status_counts'],'audit_validator':v['result'],'audit_mutation_tests':14,'real_ELF_mutation_cases':16,'source_recovery_bundles_verified_and_fresh_recovered':5,'all_compiled_tree_C_H_hashes_public_or_complete_preserved_patches':True,'source_file_count':6619,'actual_compiled_C_units':68,'complete_builds':10,'deterministic_modules_each_run':34,'deterministic_intermediate_objects_each_run':132,'imports':1434,'exports':320,'next_proposed':30,'next_classes':{'D':7,'G':23},'no_live_phone_or_push':True}
(P/'evidence/final-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
