#!/usr/bin/env python3
"""hunks.py list <patch> | pick <patch> <file-substr:idx,idx> [...]  -- hunk-level selection of a unified diff."""
import sys,re
def parse(p):
    files=[];cur=None
    for l in open(p).read().splitlines(keepends=True):
        if l.startswith('diff --git'):
            cur={'hdr':[l],'hunks':[],'name':l.split()[-1][2:]};files.append(cur)
        elif cur is not None and not cur['hunks'] and not l.startswith('@@'):
            cur['hdr'].append(l)
        elif l.startswith('@@'):
            cur['hunks'].append([l])
        else:
            cur['hunks'][-1].append(l)
    return files
fs=parse(sys.argv[2])
if sys.argv[1]=='list':
    for f in fs:
        for i,h in enumerate(f['hunks']):
            a=sum(1 for l in h[1:] if l.startswith('+')); d=sum(1 for l in h[1:] if l.startswith('-'))
            print(f"{f['name'].split('/')[-1]}:{i}\t+{a}/-{d}\t{h[0].strip()[:110]}")
else:
    sel={}
    for s in sys.argv[3:]:
        k,v=s.split(':'); sel[k]=set(range(len(fs)*1000)) if v=='all' else {int(x) for x in v.split(',')}
    for f in fs:
        for k,v in sel.items():
            if f['name'].endswith(k):
                hs=[h for i,h in enumerate(f['hunks']) if i in v]
                if hs: sys.stdout.write(''.join(f['hdr'])+''.join(''.join(h) for h in hs))
