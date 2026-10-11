#!/usr/bin/env python3
"""Read-only natural MD4 diagnostics over coherent local historical source inputs.
No hash preimage search, guessed tokens, modinfo assignment or source/ELF writes.
"""
from pathlib import Path
import ctypes,csv,hashlib,json,subprocess,collections
P=Path(__file__).resolve().parents[1]
W=Path('/home/armol/kernel-work/usb-typec-closure-01')
lib=ctypes.CDLL(str(W/'sumversion-probe.so'))
lib.hash_paths.argtypes=[ctypes.POINTER(ctypes.c_char_p),ctypes.c_char_p]
def fingerprint(paths):
    v=(ctypes.c_char_p*(len(paths)+1))(*[str(p).encode() for p in paths],None)
    out=ctypes.create_string_buffer(25);lib.hash_paths(v,out);return out.value.decode()
expected={'charger_class':'E4A92CD3F20A3D2142F16B6','mtk_chg_type_det':'F7A2E5433A38379D631644F','rt_pd_manager':'C4301583FE25F39BA52E75D','tcpc_mt6375':'D27BCF95DDC8F09B632224B'}
headers={'charger_class':['charger_class.h'],'mtk_chg_type_det':['mtk_charger.h','charger_class.h','adapter_class.h','mtk_charger_algorithm_class.h','mtk_smartcharging.h'],'rt_pd_manager':[],'tcpc_mt6375':[]}
# Respect ongoing checkouts: only read candidate files. No checkout/reset/git add.
cmd=['find','/home/armol/kernel-work','-type','d','(','-name','.git','-o','-name','prebuilts','-o','-name','out','-o','-name','kout',')','-prune','-o','-type','f','(']
for i,n in enumerate(expected):
    if i:cmd+=['-o']
    cmd+=['-name',n+'.c']
cmd+=[')','-print']
paths=[Path(s) for s in subprocess.check_output(cmd,text=True).splitlines()]
traces=json.loads((P/'evidence/srcversion/baseline-traces.json').read_text())
for t in traces:
    ps=[Path(x['path']) for x in t['hashed_files']]
    assert fingerprint(ps)==t['regenerated']
results=[];seen={};incomplete=[]
for f in paths:
    n=f.stem;ps=[f]+[f.parent/h for h in headers[n]]
    if not all(p.is_file() for p in ps):incomplete.append(str(f));continue
    sig=tuple(hashlib.sha256(p.read_bytes()).hexdigest() for p in ps)
    if (n,sig) in seen:seen[(n,sig)]['other_paths'].append(str(f));continue
    natural=fingerprint(ps)
    row={'module':n,'source_files':[{'path':str(p),'sha256':h} for p,h in zip(ps,sig)],'fingerprint':natural,'stock_fingerprint':expected[n],'matches_stock':natural==expected[n],'other_paths':[],'limit':'Candidate content verified; public/OEM provenance must be separately established before any acceptance'}
    seen[(n,sig)]=row;results.append(row)
(P/'evidence/srcversion/coherent-local-source-scan.json').write_text(json.dumps({'local_instances':len(paths),'unique_coherent_input_sets':len(results),'incomplete_source_sets':incomplete,'matches':[r for r in results if r['matches_stock']],'candidates':results},indent=2)+'\n')
print('Coherent local sets',len(results),'instances',len(paths),'by module',dict(collections.Counter(r['module'] for r in results)),'stock matches',[(r['module'],r['source_files'][0]['path']) for r in results if r['matches_stock']])
