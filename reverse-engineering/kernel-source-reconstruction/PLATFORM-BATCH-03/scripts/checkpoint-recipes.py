#!/usr/bin/env python3
"""Commit each tested family; certification remains pending independent acceptance."""
from pathlib import Path
import csv,json,subprocess,shutil,sys
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=R.parent;state=json.loads((P/'BATCH-STATE.json').read_text());N=W/state['repositories']['SECURE-DIAGNOSTICS'];D=Path(state['build_directories']['development']);comp=json.loads((D/sys.argv[1]/'comparison.json').read_text());assert len(comp)==34
exact=[x for x in comp if x['status']=='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE'];blocked=[x for x in comp if x not in exact]
assert len(exact)==33 and len(blocked)==1 and blocked[0]['module']=='thermal-generic-adc'
assert blocked[0]['different_sections']==['.note.gnu.build-id','.BTF'] and blocked[0]['length_delta']==0
refs=list(csv.DictReader((N/'reference/joint-stock-normalized.tsv').open(),delimiter='\t'));repos=[]
for family,name in state['repositories'].items():
 n=W/name
 if n!=N:
  shutil.copyfile(N/'SOURCE-PINS.tsv',n/'SOURCE-PINS.tsv')
  for d in ['scripts','reference','patches']:
   for f in (N/d).iterdir():
    if f.is_file() and f.name not in ['PRIOR-CERTIFIED-RECIPE.json']:shutil.copyfile(f,n/d/f.name)
 own=json.loads((n/'families/OWNERSHIP.json').read_text())['owned_modules']
 with (n/'reference/stock-normalized.tsv').open('w') as o:
  w=csv.DictWriter(o,fieldnames=list(refs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(r for r in refs if r['module'] in own)
 for f in (n/'scripts').glob('*.sh'):f.chmod(0o755)
 (n/'reference/development-comparison.json').write_text(json.dumps([x for x in comp if x['module'] in own],indent=2)+'\n')
 assert not any(f.suffix in ['.ko','.o','.pyc'] for f in n.rglob('*') if f.is_file() and '.git' not in f.parts),'Source recipe must be artifact-free'
 subprocess.run(['git','-C',str(n),'add','-A'],check=True);subprocess.run(['git','-C',str(n),'-c','core.hooksPath=/dev/null','commit','-qm',f'{family.lower()}: Batch03 full owned source, pinned34-target engine and complete development stock acceptance'],check=True)
 head=subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip();repos.append({'family':family,'repository':'../'+name,'commit':head,'owned_count':len(own),'development_exact':sum(x['module'] in own for x in exact),'pending':'independent B1/B2; native ADC BTF C blocker only' if 'thermal-generic-adc' in own else 'independent B1/B2'});E=P/family/'evidence';E.mkdir(parents=True,exist_ok=True);(E/'development-comparison.json').write_text(json.dumps([x for x in comp if x['module'] in own],indent=2)+'\n');(P/family/'README.md').write_text(f'# {family}\n\nMaintained source:`../{name}` at `{head}`.\n{len(own)} owned targets compiled; {sum(x['module'] in own for x in exact)} development full-stock-exact. Independent clone pending. Native ADC, if owned, remains C for BTF-base mismatch.\nCanonical owners unchanged. Firmware/runtime are separate. Prior accepted recipe history retained.\n')
 state['relevant_commits'][family]=head
 with (P/'SOURCE-REPOSITORIES.tsv').open('w') as o:
  w=csv.DictWriter(o,fieldnames=list(repos[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(repos)
 state.update(phase='DEVELOPMENT_SOURCE_FAMILY_CHECKPOINTS_IN_PROGRESS',current_module=family,next_immediate_action='Continue source family checkpoints, then independent five-clone B1/B2')
 (P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['git','add','-f',str(P.relative_to(R))],cwd=R,check=True);subprocess.run(['git','-c','core.hooksPath=/dev/null','commit','-qm',f'batch03: checkpoint {family} actual committed source and development acceptance'],cwd=R,check=True)
state.update(phase='ALL34_SOURCE_BUILT_33_DEVELOPMENT_EXACT_ONE_BTF_BLOCKER_FIVE_SOURCE_COMMITS',current_module='Independent five-family B1/B2',development_exact_modules=[x['module']+'.ko' for x in exact],blocked_modules={'thermal-generic-adc.ko':'21 .BTF type/string-reference bytes mismatch to source-derived public GKI base; C, never normalized'},latest_parity_result='All34 compiled;33 full stock ELF exact except parsed GNU20-byte build ID; native ADC all other axes exact;89 source boundaries exact',next_immediate_action='Run cleancheck.sh with TMPDIR=/tmp and LIEPPOS_BATCH03_NATIVE_MIRROR: clone five recipes, hide originals and development tree, independently build all34 ten times; certify only actually full-accepted33');(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n');print('Five source commits;all34 source-built,33 development exact,1 explicit BTF C blocker;no A/B before independent proof')
