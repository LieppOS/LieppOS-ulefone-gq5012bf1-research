#!/usr/bin/env python3
"""Preserve rejected private AW source candidates as reproducible diffs and hashes."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('workspace',type=Path)
a=parser.parse_args()
base=(P/'evidence/aw883xx/v-switch.c').read_text()
output=P/'evidence/aw883xx/variants';output.mkdir(exist_ok=True)
manifest=[]
files=sorted(set(a.workspace.glob('g-*.c')) | set(a.workspace.glob('v-*.c')) |
             set(a.workspace.glob('h-*.c')) | set((a.workspace/'grid2').glob('*.c')) |
             set((a.workspace/'grid3').glob('*.c')))
for f in files:
    relative=f.relative_to(a.workspace)
    name=str(relative).replace('/','__')+'.patch'
    text=f.read_text()
    patch=''.join(difflib.unified_diff(base.splitlines(keepends=True),text.splitlines(keepends=True),
                                    fromfile='a/aw883xx_bin_parse.c',tofile='b/aw883xx_bin_parse.c'))
    (output/name).write_text(patch)
    manifest.append(dict(variant=str(relative),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
                         patch='variants/'+name,baseline='v-switch.c'))
(P/'evidence/aw883xx/variant-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(len(manifest),'candidate source variants preserved as baseline diffs (no accepted source replacement)')
