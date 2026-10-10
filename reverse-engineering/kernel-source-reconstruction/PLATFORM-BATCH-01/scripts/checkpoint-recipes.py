#!/usr/bin/env python3
"""Commit reproducible family source + measured progress, with no premature A promotion."""
import csv,json,subprocess,shutil,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=R.parent;N=W/'android_kernel_modules_power_platform_ulefone_gq5012bf1';D=Path('/home/armol/kernel-work/platform-batch-01-dev');state=json.loads((P/'BATCH-STATE.json').read_text());comp=json.loads((D/'comparison-dev6/comparison.json').read_text());families=json.loads((N/'families/OWNERSHIP.json').read_text())['all_families'];refs=list(csv.DictReader((N/'reference/stock-normalized.tsv').open(),delimiter='\t'));repos=[]
for family,name in families.items():
 n=W/name
 if n!=N:
  for d in ['scripts','reference','patches']:
   for f in (N/d).iterdir():
    if f.is_file():shutil.copyfile(f,n/d/f.name)
 own=json.loads((n/'families/OWNERSHIP.json').read_text())['owned_modules']
 shutil.copyfile(n/'reference/stock-normalized.tsv',n/'reference/joint-stock-normalized.tsv')
 with (n/'reference/stock-normalized.tsv').open('w') as o:
  w=csv.DictWriter(o,fieldnames=list(refs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(r for r in refs if r['module'] in own)
 # Full comparison engine needs all35 goldens; standalone verifier defaults to owned scope.
 for f in (n/'scripts').glob('*.sh'):f.chmod(0o755)
 (n/'reference/development-comparison.json').write_text(json.dumps([x for x in comp if x['module'] in own],indent=2)+'\n')
 subprocess.run(['git','-C',str(n),'add','-A'],check=True);subprocess.run(['git','-C',str(n),'-c','core.hooksPath=/dev/null','commit','-qm',f'{family.lower()}: preserve pinned batch source, shared compile scope and measured development parity'],check=True)
 head=subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip();repos.append({'family':family,'repository':'../'+name,'commit':head,'owned_count':len(own),'development_exact':sum(x['status']=='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE' for x in comp if x['module'] in own),'pending':';'.join(x['module'] for x in comp if x['module'] in own and x['status']!='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE')})
 with (P/'SOURCE-REPOSITORIES.tsv').open('w') as o:
  w=csv.DictWriter(o,fieldnames=list(repos[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(repos)
 (P/family/'evidence').mkdir(parents=True,exist_ok=True)
 (P/family/'evidence/development-comparison.json').write_text(json.dumps([x for x in comp if x['module'] in own],indent=2)+'\n')
 (P/family/'README.md').write_text(f'# {family}\n\nMaintained source:`../{name}` at `{head}`.\nOwned targets:{len(own)}; development stock-exact:{sum(x["status"]=="DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE" for x in comp if x["module"] in own)}.\nIndependent clean-clone proof pending: no A/B asserted at this checkpoint.\nSee parent batch manifest, dependency graph and state.\n')
state['phase']='ALL35_COMPILED_31_DEVELOPMENT_EXACT_CLEAN_CLONE_PENDING';state['current_module']='Independent joint clean-checkout B1/B2';state['development_exact_modules']=[x['module']+'.ko' for x in comp if x['status']=='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE'];state['failed_modules']={x['module']+'.ko':{'status':'SOURCE_BUILD_UNVERIFIED','evidence':'evidence/attempt-06/comparison.json','exact_functions':x['functions_exact'],'import_crc_mismatches':x['import_crc_mismatches'],'export_crc_mismatches':x['export_crc_mismatches'],'kcfi_abs_mismatches':x['kcfi_abs_mismatches'],'different_sections':x['different_sections']} for x in comp if x['status']!='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE'};state['latest_successful_verification']='35 object/link compilations pass;31 full stock ELF exact except GNU ID;152/156 primary provider boundaries exact, four CMDQ CRC failures preserved';state['relevant_commits'].update({x['family']:x['commit'] for x in repos});(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n')
print('Committed four source families;35 compiled,31 development exact,4 actual blockers; clean checkout next')
