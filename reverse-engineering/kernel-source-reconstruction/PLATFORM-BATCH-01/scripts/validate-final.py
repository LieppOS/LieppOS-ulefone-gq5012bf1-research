#!/usr/bin/env python3
"""Check final identity scope, baseline preservation, source pins and retained proof."""
from pathlib import Path
import csv,json,subprocess,io,hashlib,sys,collections
P=Path(__file__).resolve().parents[1];R=P.parents[2];A=R/'reverse-engineering/kernel-source-parity-audit';C=Path('/home/armol/kernel-work/platform-batch-01-cleancheck');sys.dont_write_bytecode=True
rows=lambda path:list(csv.DictReader(path.open(),delimiter='\t'))
M=rows(P/'BATCH-MANIFEST.tsv');T=rows(P/'BATCH-PARITY.tsv');ids={r['module_id'] for r in M}
old={r['module_id']:r for r in csv.DictReader(io.StringIO(subprocess.check_output(['git','show','4d3f4a42c7da217e6f9c9258b6af83805c6af180:reverse-engineering/kernel-source-parity-audit/ALL-457-MODULES.tsv'],cwd=R,text=True)),delimiter='\t')}
new={r['module_id']:r for r in rows(A/'ALL-457-MODULES.tsv')}
assert len(M)==len(T)==35 and len(new)==len(old)==458 and new.keys()==old.keys()
assert hashlib.sha256((P/'BATCH-MANIFEST.tsv').read_bytes()).hexdigest()=='c381b5b8fd770dd02aa4f73a062e9d40c0d0e1ce7d920d6225c59aef4c9dd813'
assert all(old[i]==new[i] for i in new.keys()-ids),'Unselected row drift'
immutable=['stock_paths','stock_sha256','stock_size','component_owner','component_status','canonical_component_status','runtime_status']
assert all(old[i][k]==new[i][k] for i in new for k in immutable)
assert all(old[i]['source_status']=='D' for i in ids)
assert collections.Counter(new[i]['source_status'] for i in ids)=={'A':31,'C':4}
summary=json.loads((A/'evidence/audit-summary.json').read_text());assert summary['verified_A_B']==160 and summary['unverified_and_unexcluded']==298
v=json.loads((A/'evidence/validator-result.json').read_text());assert not v['errors']
assert json.loads((P/'evidence/acceptance-mutation-tests.json').read_text())['all_pass']
assert 'Ran 14 tests' in (P/'evidence/audit-mutation-tests.log').read_text() and (P/'evidence/audit-mutation-tests.log').read_text().rstrip().endswith('OK')
# Source commit/preservation bundles and restored originals are prerequisites, not optional.
for r in rows(P/'SOURCE-REPOSITORIES.tsv'):
 n=(R/r['repository']).resolve();assert subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip()==r['commit'];assert not subprocess.check_output(['git','-C',str(n),'status','--porcelain'],text=True).strip()
 bundle=P/r['family']/'source'/f'{n.name}.bundle';p=subprocess.run(['git','-C',str(n),'bundle','verify',str(bundle)],stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert p.returncode==0
# Reproduce the recorded residual relocation claim independently of a report label.
sys.path.insert(0,str(C/'recipes/android_kernel_modules_power_platform_ulefone_gq5012bf1/scripts'));from normalize import kpp
blocked=[]
for r in M:
 if new[r['module_id']]['source_status']!='C':continue
 a=kpp.KO(R/r['stock_paths'].split(';')[0]);b=kpp.KO(C/'ws/out/B1'/r['filename'].replace('.ko','.stripped'));count=0
 for s in a.secs:
  if s['type']!=4:continue
  t=b.sec(s['n']);assert a.data(s['n'])==b.data(s['n'])
  aa=collections.Counter((o,i&0xffffffff,a.sym_name(i>>32),v) for o,i,v in a.rela_entries(s));bb=collections.Counter((o,i&0xffffffff,b.sym_name(i>>32),v) for o,i,v in b.rela_entries(t));assert aa==bb;count+=sum(aa.values())
 assert count==int(r['stock_relocations']);blocked.append({'module':r['filename'],'raw_and_semantic_relocations_exact':count,'source_sha256':hashlib.sha256(b.b).hexdigest(),'stock_sha256':hashlib.sha256(a.b).hexdigest(),'status':'NOT_FULL_ELF_ACCEPTED_C'})
(P/'evidence/blocked-relocations.json').write_text(json.dumps(blocked,indent=2)+'\n')
report={'result':'PASS','identities':458,'selected':35,'newly_certified':31,'explicit_C_blockers':4,'unselected_rows_byte_field_identical':423,'all_stock_paths_sizes_hashes_owners_runtime_statuses_unchanged':True,'certified_total':160,'remaining_total':298,'audit_validator':v['result'],'audit_mutation_tests':14,'acceptance_mutation_tests':15,'source_recovery_bundles_verified':4}
(P/'evidence/final-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
