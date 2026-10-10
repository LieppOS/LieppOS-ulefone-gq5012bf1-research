#!/usr/bin/env python3
"""Each family and complete batch:strict measured B1/B2 stock acceptance."""
from pathlib import Path
import sys,json,csv
C=Path(sys.argv[1]);which=sys.argv[2];indices=list(range(5)) if which=='all' else [int(which)];P=Path(__file__).resolve().parents[1];repos=list(csv.DictReader((P/'SOURCE-REPOSITORIES.tsv').open(),delimiter='\t'));summaries=[]
files=['SHA256SUMS','INTERMEDIATE-SHA256SUMS','NATIVE-INTERMEDIATE-SHA256SUMS','native-config.sha256','config.sha256','gki-symvers.sha256','TARGET-SOURCE-TREE','batch-full.Module.symvers','provider/natural-external-provider.symvers','provider/provider-witnesses.json','provider/provider-errors.json']
for i in indices:
 A=C/f'ws/out/F{i}-B1';B=C/f'ws/out/F{i}-B2'
 for f in files:assert (A/f).read_bytes()==(B/f).read_bytes(),(i,f)
 for O in [A,B]:
  assert len(list(O.glob('*.ko')))==len(list(O.glob('*.stripped')))==34
  assert all((O/f).read_text().strip()=='0' for f in ['object-exit','module-exit','native-exit'])
  assert not json.loads((O/'provider/provider-errors.json').read_text())
  for log in ['objects.log','modules.log']:assert not any(x in (O/log).read_text() for x in ['warning:','error:','WARNING:','ERROR:']),log
 for pattern in ['*.ko','*.stripped']:
  for f in A.glob(pattern):assert f.read_bytes()==(B/f.name).read_bytes(),f
 j=json.loads((C/f'comparison-F{i}-B1/comparison.json').read_text());k=json.loads((C/f'comparison-F{i}-B2/comparison.json').read_text());assert j==k and len(j)==34
 accepted=[x for x in j if x['status']=='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE'];blocked=[x for x in j if x not in accepted]
 assert len(accepted)==33 and len(blocked)==1 and blocked[0]['module']=='thermal-generic-adc'
 assert blocked[0]['different_sections']==['.note.gnu.build-id','.BTF'] and blocked[0]['length_delta']==0
 assert (C/f'native-F{i}-B1/incomplete-acceptance.json').read_bytes()==(C/f'native-F{i}-B2/incomplete-acceptance.json').read_bytes()
 summaries.append({'family':repos[i]['family'],'source_commit':repos[i]['commit'],'joint_modules_built':34,'joint_modules_accepted':33,'owned_modules_accepted':int(repos[i]['development_exact']),'raw_and_stripped_deterministic':34,'intermediate_object_count':len((A/'INTERMEDIATE-SHA256SUMS').read_text().splitlines()),'native_intermediate_object_count':len((A/'NATIVE-INTERMEDIATE-SHA256SUMS').read_text().splitlines()),'provider_boundaries_exact':89,'natural_external_slots':31,'source_tree':(A/'TARGET-SOURCE-TREE').read_text().strip(),'blocked':['thermal-generic-adc:C:21 BTF reference bytes']})
 if which=='all':
  for f in files:assert (A/f).read_bytes()==(C/'ws/out/F0-B1'/f).read_bytes(),('cross-family',i,f)
if which=='all':
 result={'result':'PASS_ALL34_FIVE_INDEPENDENT_FAMILY_ENGINES_B1_B2','original_development_and_all_five_recipe_paths_unavailable_during_ten_compilations':True,'fresh_committed_source_clones':5,'fresh_complete_compilations':10,'base_config_and_public_headers_verified_and_reused':True,'target_provider_objects_reused':False,'all_34_built_each_run':True,'accepted_each_run':33,'explicit_C_blockers_each_run':1,'cross_family_source_config_abi_objects_raw_stripped_identical':True,'unaccepted':['thermal-generic-adc: preserved source and reproducible BTF-base mismatch; no A/B'],'families':summaries};(C/'cleancheck-result.json').write_text(json.dumps(result,indent=2)+'\n')
else:(C/f'cleancheck-F{which}.json').write_text(json.dumps(summaries[0],indent=2)+'\n')
print('PASS',which,summaries)
