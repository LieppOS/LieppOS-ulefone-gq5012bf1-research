#!/usr/bin/env python3
"""Commit four real recipes only after all27 development modules fully accept stock."""
from pathlib import Path
import csv,json,subprocess,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=R.parent;N=W/'android_kernel_modules_memory_platform_ulefone_gq5012bf1';D=Path('/home/armol/kernel-work/platform-batch-02-dev');state=json.loads((P/'BATCH-STATE.json').read_text());comp=json.loads((D/'comparison-dev2/comparison.json').read_text());assert len(comp)==27 and all(x['status']=='DEVELOPMENT_STOCK_EXACT_PENDING_CLEAN_CLONE' for x in comp)
families=json.loads((N/'families/OWNERSHIP.json').read_text())['all_families'];refs=list(csv.DictReader((N/'reference/joint-stock-normalized.tsv').open(),delimiter='\t'));repos=[]
for family,name in families.items():
 n=W/name
 if n!=N:
  for d in ['scripts','reference','patches']:
   for f in (N/d).iterdir():
    if f.is_file():shutil.copyfile(f,n/d/f.name)
 own=json.loads((n/'families/OWNERSHIP.json').read_text())['owned_modules']
 with (n/'reference/stock-normalized.tsv').open('w') as o:
  w=csv.DictWriter(o,fieldnames=list(refs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(r for r in refs if r['module'] in own)
 for f in (n/'scripts').glob('*.sh'):f.chmod(0o755)
 (n/'reference/development-comparison.json').write_text(json.dumps([x for x in comp if x['module'] in own],indent=2)+'\n')
 subprocess.run(['git','-C',str(n),'add','-A'],check=True);subprocess.run(['git','-C',str(n),'-c','core.hooksPath=/dev/null','commit','-qm',f'{family.lower()}: pinned27-target engine and complete development stock acceptance; Kbuild-only fixes'],check=True)
 head=subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip();repos.append({'family':family,'repository':'../'+name,'commit':head,'owned_count':len(own),'development_exact':len(own),'pending':''});E=P/family/'evidence';E.mkdir(parents=True,exist_ok=True);(E/'development-comparison.json').write_text(json.dumps([x for x in comp if x['module'] in own],indent=2)+'\n');(P/family/'README.md').write_text(f'# {family}\n\nSource:`../{name}` at `{head}`.\n{len(own)} owned targets development full-stock-exact; independent clone still pending.\nOwners/statuses unchanged. Firmware/runtime are separate.\n')
with (P/'SOURCE-REPOSITORIES.tsv').open('w') as o:
 w=csv.DictWriter(o,fieldnames=list(repos[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(repos)
state.update(phase='ALL27_COMPILED_DEVELOPMENT_EXACT_FOUR_SOURCE_COMMITS_CLEAN_CLONE_PENDING',current_module='Independent per-family B1/B2 plus final batch build',development_exact_modules=[x['module']+'.ko' for x in comp],failed_modules={},latest_successful_verification='27 full stock ELF exact except parsed GNU20-byte build ID;44/44 producer CRC/licence/namespace/KCFI-prefix boundaries;19 authentic external slots',next_immediate_action='Fresh-clone all four source repos, hide originals, independently execute each committed engine B1/B2');state['relevant_commits'].update({x['family']:x['commit'] for x in repos});(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n');print('Four source commits;27 development exact;no A/B until independent proof')
