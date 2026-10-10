#!/usr/bin/env python3
"""Freeze the exact audited three identities before compiling and prepare Kbuild-only scope.
Usage: prepare-reference.py <recipe> <scratch> <public git with pins>
"""
from pathlib import Path
import csv,sys,subprocess,hashlib,json,collections,re
from dtlib import export_values
N,W,G=map(lambda s:Path(s).resolve(),sys.argv[1:]);R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parents[1];A=R/'reverse-engineering/kernel-source-parity-audit'
sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import normalized,kpp
names=['mmqos-common.ko','mmqos-mt6878.ko','mtk-emi.ko'];assert json.load((A/'evidence/audit-summary.json').open())['next_modules']==names
allrows=list(csv.DictReader((A/'ALL-457-MODULES.tsv').open(),delimiter='\t'));rows=[r for r in allrows if r['filename'] in names];assert len(rows)==3 and all(r['source_status']=='D' for r in rows)
def tab(p,head,rr):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(head);w.writerows(rr)
tab(P/'evidence/inventory/audit-baseline-three.tsv',list(rows[0]),[list(r.values()) for r in rows]);refs=[];info={}
for r in rows:
 paths=r['stock_paths'].split(';');ko=kpp.KO(R/paths[0]);sha=hashlib.sha256(ko.b).hexdigest();assert sha==r['stock_sha256'] and len(ko.b)==int(r['stock_size'])
 assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==sha for p in paths)
 b,off,count=normalized(ko);m=r['filename'][:-3];refs.append([m,len(b),sha,hashlib.sha256(b).hexdigest(),hex(off),count])
 info[m]={'stock_sha256':sha,'bytes':len(b),'paths':paths,'owner':r['component_owner'],'modinfo':[v.decode(errors='replace') for v in ko.data('.modinfo').split(b'\0') if v], 'build_id_range':[off,count],'sections':len(ko.secs),'function_symbols':sum(y['info']&15==2 and 0<y['shndx']<len(ko.secs) for y in ko.syms),'data_symbols':sum(y['info']&15==1 and 0<y['shndx']<len(ko.secs) for y in ko.syms),'imports':len(kpp.versions(ko)[0]),'exports':export_values(ko),'relocations':sum(s['size']//24 for s in ko.secs if s['type']==4),'kcfi_ids':[(y['n'],hex(y['val']&0xffffffff)) for y in ko.syms if y['n'].startswith('__kcfi_typeid_')]}
tab(N/'reference/stock-normalized.tsv',['module','bytes','stock_sha256','normalized_sha256','build_id_offset','build_id_length'],refs)
(P/'evidence/inventory/stock-inventory.json').write_text(json.dumps(info,indent=2)+'\n')
edges=list(csv.DictReader((A/'DEPENDENCY-EDGES.tsv').open(),delimiter='\t'));ids={r['module_id'] for r in rows};edges=[r for r in edges if r['consumer_module_id'] in ids];tab(P/'evidence/inventory/provider-edges.tsv',list(edges[0]),[list(r.values()) for r in edges])
external=[r for r in edges if r['provider_module_ids']!='GKI_CORE' and r['provider_module_ids'] not in ids];assert len(external)==33
master={r['filename']:r for r in allrows}
# Modpost dependency spelling is the producer filename stem (hyphens preserved),
# not the kernel's underscore-normalized modinfo name.
lines=[]
for r in external:
 assert ';' not in r['provider_module_ids'];fn=r['provider_module_ids'].split('@')[0];pk=kpp.KO(R/master[fn]['stock_paths'].split(';')[0]);name=fn[:-3];lines.append(f"{r['required_crc']}\t{r['symbol']}\tproviders/{name}\t{r['export_type']}\t\n")
(N/'reference/external-provider.symvers').write_text(''.join(lines))
base='5e415e059253ce0d2e61c97108e5f5785d71f06f';new='957dac185efe46cbf6336b0fff9516d84c8cd78f';lineage=[]
files=['drivers/interconnect/mediatek/'+s for s in ['mmqos-mtk.c','mmqos-hrt.c','mmqos-vcp.c','mmqos-test.c','mmqos-mt6878.c','mtk-emi.c','Makefile','Kconfig','mmqos-mtk.h']]
for f in files:
 blobs=[subprocess.check_output(['git','-C',str(G),'rev-parse',c+':'+f],text=True).strip() for c in [base,new]];lineage.append([f,*blobs,'IDENTICAL' if blobs[0]==blobs[1] else 'DIFFERENT'])
tab(P/'evidence/inventory/source-candidate-blobs.tsv',['file','alps_blob','nothing_blob','comparison'],lineage)
t=W/'kdm';t.mkdir(parents=True,exist_ok=True)
ar=subprocess.Popen(['git','-C',str(G),'archive',base],stdout=subprocess.PIPE);subprocess.run(['tar','-x','-C',str(t)],stdin=ar.stdout,check=True);ar.stdout.close();assert ar.wait()==0
subprocess.run(['git','init','-q',str(t)],check=True);subprocess.run(['git','-C',str(t),'add','-Af'],check=True);subprocess.run(['git','-C',str(t),'-c','user.name=LieppOS','-c','user.email=lieppos@local','-c','core.hooksPath=/dev/null','commit','-qm','pinned ALPS'],check=True)
(t/'Kbuild').write_text('# SPDX-License-Identifier: GPL-2.0\n# Owned scope; preserve include order and original target flags.\nLINUXINCLUDE := $(DEVCIE_MODULES_INCLUDE) $(LINUXINCLUDE)\nsubdir-ccflags-y += -Werror -I$(srctree)/$(src)/include -I$(srctree)/$(src)/include/uapi\nobj-y += drivers/interconnect/mediatek/\n')
(t/'drivers/interconnect/mediatek/Kbuild').write_text('# SPDX-License-Identifier: GPL-2.0\ninclude $(src)/Makefile\n# Resolve define_trace.h\'s local includes in an absolute external tree.\nccflags-y += -I$(src)\nobj-m := mmqos-common.o mmqos-mt6878.o mtk-emi.o\nobj-y :=\n')
subprocess.run(['git','-C',str(t),'add','-Af'],check=True);(N/'patches/0001-owned-interconnect-build-scope.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--cached']));(N/'reference/kdm-tree.txt').write_text(subprocess.check_output(['git','-C',str(t),'write-tree'],text=True));(N/'reference/prov-tree.txt').write_text(subprocess.check_output(['git','-C',str(G),'rev-parse',base+'^{tree}'],text=True))
print('Frozen three identities,164 imports,33 external source witnesses; Kbuild-only target scope')
