#!/usr/bin/env python3
"""Record configured platform nodes independently of a module alias/binding claim."""
from pathlib import Path
import sys,json,re,csv
P=Path(__file__).resolve().parents[1];R=P.parents[2];sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'reverse-engineering/kernel-source-reconstruction/INTERCONNECT-EMI/scripts'));from dtlib import live,strings,decode,status
N=live(R/'workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar');out=[]
for p,v in N.items():
 c=strings(v.get('compatible',b''));tag=p+' '+','.join(c)
 if not re.search(r'gce|cmdq|smi|scpsys|dvfsrc|mmdvfs|pmic|spmi|devapc',tag,re.I):continue
 if not c:continue
 out.append({'node':p,'compatible':';'.join(c),'effective_status':status(N,p),'configured_resources':json.dumps({k:decode(b) for k,b in v.items() if k in ['reg','interrupts','interrupt-parent','clocks','clock-names','power-domains','mboxes','mbox-names','mediatek,gce-events','mediatek,secure','iommus']},separators=(',',':')),'evidence_level':'SAVED_DT_CONFIGURATION_ONLY_NO_MODULE_BIND_OR_RUNTIME_SUCCESS'})
with (P/'evidence/hardware/CONFIGURED-PLATFORM-NODES.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(out)
print('independent platform nodes',len(out))
for x in out:
 if any(t in x['compatible'] for t in ['gce','smi-common','scpsys','dvfsrc','pmic']):print(x['node'],x['compatible'],x['effective_status'],x['configured_resources'][:1000])
