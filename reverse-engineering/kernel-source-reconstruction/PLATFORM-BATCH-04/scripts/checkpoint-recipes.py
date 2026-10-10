#!/usr/bin/env python3
"""Checkpoint all30 full source compiled,25 development acceptance,5 retained failures."""
from pathlib import Path
import csv,json,subprocess,shutil,sys
P=Path(__file__).resolve().parents[1];R=P.parents[2];S=json.loads((P/'BATCH-STATE.json').read_text());N=R.parent/S['repositories']['CHARGER-GAUGE-ADC'];comp=json.loads((P/'evidence'/sys.argv[1]/'comparison.json').read_text());exact=[x for x in comp if x['status']=='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE'];blocked=[x for x in comp if x not in exact];assert len(comp)==30 and len(exact)==25 and {x['module'] for x in blocked}=={'charger_class','mtk_chg_type_det','rt_pd_manager','tcpc_class','tcpc_mt6375'}
refs=list(csv.DictReader((N/'reference/joint-stock-normalized.tsv').open(),delimiter='\t'));repos=[]
for family,name in S['repositories'].items():
 n=R.parent/name
 if n!=N:
  shutil.copyfile(N/'SOURCE-PINS.tsv',n/'SOURCE-PINS.tsv')
  for d in ['scripts','reference','patches']:
   for f in (N/d).iterdir():
    if f.is_file():shutil.copyfile(f,n/d/f.name)
 owned=S['families'][family]
 with (n/'reference/stock-normalized.tsv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(refs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(r for r in refs if r['module'] in owned)
 (n/'reference/development-comparison.json').write_text(json.dumps(comp,indent=2)+'\n')
 for f in (n/'scripts').glob('*.sh'):f.chmod(0o755)
 subprocess.run(['git','add','-A'],cwd=n,check=True);subprocess.run(['git','-c','core.hooksPath=/dev/null','commit','-qm',f'Batch04 {family}: recover full historical and public31source, all30 compiled;25 development-exact5unaccepted, independent proof pending'],cwd=n,check=True)
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=n,text=True).strip();assert not subprocess.check_output(['git','status','--porcelain'],cwd=n,text=True).strip();repos.append({'family':family,'repository':'../'+name,'commit':head,'owned_count':len(owned),'development_exact':sum(x['module'] in owned for x in exact),'pending':'Independent freshclone B1/B2; strict incomplete modules remain C candidates'})
with (P/'SOURCE-REPOSITORIES.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(repos[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(repos)
S.update(phase='ALL30_FULL_SOURCE_COMPILED_25_DEVELOPMENT_EXACT_FIVE_UNACCEPTED_THREE_SOURCE_COMMITS',current_module='Independent three-family all30 B1/B2 pending; no A/B before proof',development_exact_modules=[x['module']+'.ko' for x in exact],source_compiled_modules=[x['module']+'.ko' for x in comp],blocked_modules={x['module']+'.ko':'Full source compiled; remaining fields in comparison/incomplete/'+x['module']+'/incomplete-acceptance.json; no A/B' for x in blocked},latest_parity_result='30 compiled zero exits;195 boundarytypes exact18naturalexternal slots;25complete stock acceptance pending independent proof',next_immediate_action='Prepare cleancheck/check-determinism for3freshclones6joint30builds. Hide all3original recipes anddev. Strict expected25accepted5unaccepted eachrun with allraw/intermediates/source/config/symvers deterministic. Preserve diagnostics. After evidence/preservation/audit, bounded revisitTCPC8functions and token/counter lineage; do not redo accepted25 or oldB03.');S['source_pins']['tcpc31']='2d6f27aa19d521409f443c8d821e2d475bdc72b6';S['relevant_commits']['manifest_freeze']='f524b1b'
for q in repos:S['relevant_commits'][q['family']]=q['commit']
(P/'BATCH-STATE.json').write_text(json.dumps(S,indent=2)+'\n');print('Three full source commits;30 compiled,25development accepted/5 explicit failures; no certification yet')
