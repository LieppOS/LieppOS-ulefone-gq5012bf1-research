#!/usr/bin/env python3
"""Exact27 changes; all431 others including four CMDQ C remain identical to baseline."""
from pathlib import Path
import csv,json,subprocess,hashlib,collections,sys
P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit';sys.dont_write_bytecode=True
rows=lambda path:list(csv.DictReader(path.open(),delimiter='\t'))
M=rows(P/'BATCH-MANIFEST.tsv');T=rows(P/'BATCH-PARITY.tsv');ids={r['module_id'] for r in M};old={r['module_id']:r for r in rows(P/'evidence/baseline/ALL-457-MODULES.tsv')};new={r['module_id']:r for r in rows(A/'ALL-457-MODULES.tsv')}
assert len(M)==len(T)==27 and len(new)==len(old)==458 and new.keys()==old.keys()
assert hashlib.sha256((P/'BATCH-MANIFEST.tsv').read_bytes()).hexdigest()=='6b4245dadf20a2ca0cb10058313101ab5d37d53694b0d28cacef661b27301b6f'
assert all(old[i]==new[i] for i in new.keys()-ids),'Unselected row drift'
immutable=['stock_paths','stock_sha256','stock_size','component_owner','component_status','canonical_component_status','runtime_status'];assert all(old[i][k]==new[i][k] for i in new for k in immutable)
assert collections.Counter(old[i]['source_status'] for i in ids)=={'D':21,'G':6};assert all(new[i]['source_status']=='A' for i in ids)
summary=json.loads((A/'evidence/audit-summary.json').read_text());assert summary['verified_A_B']==187 and summary['unverified_and_unexcluded']==271 and summary['source_status_counts']==dict(A=186,B=1,C=8,D=126,E=0,F=0,G=137)
v=json.loads((A/'evidence/validator-result.json').read_text());assert not v['errors'];mu=json.loads((P/'evidence/acceptance-mutation-tests.json').read_text());assert mu['all_pass'] and mu['count']==16
assert 'Ran 14 tests' in (P/'evidence/audit-mutation-tests.log').read_text() and (P/'evidence/audit-mutation-tests.log').read_text().rstrip().endswith('OK')
for r in rows(P/'SOURCE-REPOSITORIES.tsv'):
 n=(R/r['repository']).resolve();assert subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip()==r['commit'];assert not subprocess.check_output(['git','-C',str(n),'status','--porcelain'],text=True).strip()
 assert not any(f.endswith(('.o','.ko','.pyc')) for f in subprocess.check_output(['git','-C',str(n),'ls-files'],text=True).splitlines())
 bundle=P/r['family']/'source'/f'{n.name}.bundle';p=subprocess.run(['git','-C',str(n),'bundle','verify',str(bundle)],stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert p.returncode==0
source_changes=[]
for r in rows(P/'evidence/SOURCE-FILES.tsv'):
 # No C/H patch was applied:every stored source hash must equal the immutable original blob.
 f=r['path'];Tsrc=Path('/home/armol/kernel-work/platform-batch-02-cleancheck/ws/kernel_device_modules-6.1')
 b=subprocess.check_output(['git','-C',str(Tsrc),'show','5e415e059253ce0d2e61c97108e5f5785d71f06f:'+f],stderr=subprocess.DEVNULL)
 assert hashlib.sha256(b).hexdigest()==r['sha256'],f
cmdq=['cmdq-platform-mt6878.ko','cmdq-sec-drv.ko','cmdq-test.ko','mtk-cmdq-drv-ext.ko'];assert all(r['source_status']=='C' and r==old[r['module_id']] for r in new.values() if r['filename'] in cmdq)
graph=rows(P/'evidence/PROVIDER-GRAPH.tsv');assert sum(r['axis']=='IMPORT' for r in graph)==898 and sum(r['axis']=='EXPORT' for r in graph)==113
report={'result':'PASS','identities':458,'selected':27,'new_A':27,'new_B':0,'batch_unaccepted':0,'unselected_rows_field_identical':431,'four_CMDQ_C_rows_unchanged':True,'all_paths_hashes_sizes_owners_component_runtime_statuses_unchanged':True,'certified':187,'remaining':271,'audit_validator':v['result'],'audit_mutation_tests':14,'real_ELF_mutation_cases':16,'source_recovery_bundles_verified':4,'all_compiled_tree_C_H_hashes_public_unmodified':True,'source_file_count':len(rows(P/'evidence/SOURCE-FILES.tsv'))}
(P/'evidence/final-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
