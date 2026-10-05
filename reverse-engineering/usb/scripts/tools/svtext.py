#!/usr/bin/env python3
"""srcversion of candidate source text(s) using the real scripts/mod/sumversion.c (tools/sv harness)."""
import os, subprocess, tempfile, sys
SV=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sv')
def sv(texts, name='m'):
    d=tempfile.mkdtemp(prefix='svw')
    objs=[]
    for i,t in enumerate(texts):
        c=f'{d}/{name}{i}.c'; o=f'{d}/{name}{i}.o'
        open(c,'wb').write(t if isinstance(t,bytes) else t.encode())
        open(f'{d}/.{name}{i}.o.cmd','w').write(f'cmd_{o} := x\n\nsource_{o} := {c}\n\ndeps_{o} := \\\n\n{o}: $(deps_{o})\n')
        objs.append(o)
    open(f'{d}/{name}.mod','w').write('\n'.join(objs)+'\n')
    r=subprocess.run([SV,f'{d}/{name}'],capture_output=True,text=True).stdout.strip()
    subprocess.run(['rm','-rf',d]); return r
if __name__=='__main__':
    print(sv([open(f,'rb').read() for f in sys.argv[1:]]))
