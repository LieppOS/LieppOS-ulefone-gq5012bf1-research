#!/usr/bin/env python3
"""Replay preparation metadata and coverage generators; never rebuild kernel modules.
Hashes all generated handoffs/tables before/after. Existing captures/donors only.
"""
import hashlib
import json
import subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parent.parent;CA=HERE.parent/'coverage-audit'
scopes=json.loads((HERE/'scopes.json').read_text())['scopes']
files=[p for s in scopes for p in (HERE/s['component']).rglob('*') if p.is_file()]
files += [HERE/n for n in ['dt-ownership.tsv','dependency-edges.tsv','source-candidates.tsv','ownership-delta.tsv']]
files += [HERE.parent/'accelerator-re-roadmap.md',HERE.parent/'index.md']
files += sorted(CA.glob('*.tsv'))+sorted(CA.glob('*.md'))+sorted((CA/'notes').glob('*.md'))
files += [CA/'audit-evidence/pack-identity.tsv',CA/'audit-evidence/harvested-pack-artifact-claims.tsv']
files=sorted(set(files))
def hashes():return {str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
before=hashes();logs=[]
commands=['accelerator-preparation/'+n for n in ['inventory.py','contracts.py','write-plans.py']]
commands+=['coverage-audit/scripts/'+n for n in ['harvest-pack-identity.py','harvest-pack-artifact-claims.py','build-kernel-modules.py','build-devicetree.py','build-hardware.py','build-services.py','build-integration.py','build-components.py','build-reports.py']]
commands+=['accelerator-preparation/ownership-delta.py','accelerator-preparation/validate.py','coverage-audit/scripts/check-audit.py','coverage-audit/scripts/test-final-audit.py']
for rel in commands:
 result=subprocess.run(['python3',str(HERE.parent/rel)],cwd=REPO,capture_output=True,text=True)
 logs.append('## '+rel+'\n'+result.stdout+result.stderr)
 if result.returncode:
  (HERE/'validation/replay.log').write_text('\n'.join(logs));raise RuntimeError(rel+' failed: '+result.stderr[-2000:])
after=hashes();changes=[p for p in before if before[p]!=after[p]]
(HERE/'validation/replay.log').write_text('\n'.join(logs))
(HERE/'validation/reproducibility.json').write_text(json.dumps(dict(generated_files=len(files),commands=len(commands),changed_outputs=changes,sha256=after),indent=2,sort_keys=True)+'\n')
assert not changes,'generated metadata drift: '+str(changes)
print(f'PASS: {len(files)} generated files byte-identical across {len(commands)} offline metadata/check/test commands; no module reconstruction')
