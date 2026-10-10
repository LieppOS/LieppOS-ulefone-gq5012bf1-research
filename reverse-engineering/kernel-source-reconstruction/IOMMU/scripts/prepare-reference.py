#!/usr/bin/env python3
"""Freeze original four identities and ONLY canonical queue's mtk_iommu build scope.
Usage: prepare-reference.py <recipe> <scratch> <public git with pins>
Historical pre-build generator; not a hidden build dependency.
"""
from pathlib import Path
import csv,sys,subprocess,hashlib,json
sys.dont_write_bytecode=True
N,W,G=map(lambda s:Path(s).resolve(),sys.argv[1:]);R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parents[1];A=R/'reverse-engineering/kernel-source-parity-audit'
from dtlib import tab,export_values
sys.path.insert(0,str(N/'scripts'));from normalize import normalized,kpp
names=['mtk_iommu.ko','iommu_debug.ko','iommu_secure.ko','iommu_test.ko'];assert json.load((A/'evidence/audit-summary.json').open())['next_modules']==['mtk_iommu.ko']
allrows=list(csv.DictReader((A/'ALL-457-MODULES.tsv').open(),delimiter='\t'));rows=[r for r in allrows if r['filename'] in names];assert len(rows)==4 and all(r['source_status']=='D' for r in rows)
tab(P/'evidence/inventory/audit-baseline-four.tsv',list(rows[0]),[list(r.values()) for r in rows]);refs=[];info={}
for r in rows:
 paths=r['stock_paths'].split(';');ko=kpp.KO(R/paths[0]);sha=hashlib.sha256(ko.b).hexdigest();assert sha==r['stock_sha256'] and len(ko.b)==int(r['stock_size']);assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==sha for p in paths)
 b,off,count=normalized(ko);m=r['filename'][:-3]
 if m=='mtk_iommu':refs.append([m,len(b),sha,hashlib.sha256(b).hexdigest(),hex(off),count])
 info[m]={'stock_sha256':sha,'bytes':len(b),'paths':paths,'owner':r['component_owner'],'source_group':r['source_group'],'scope':'OWNED_TARGET' if m=='mtk_iommu' else 'SEPARATE_SOURCE_PROJECT_UNCERTIFIED','modinfo':[v.decode(errors='replace') for v in ko.data('.modinfo').split(b'\0') if v],'build_id_range':[off,count],'sections':len(ko.secs),'functions':sum(y['info']&15==2 and 0<y['shndx']<len(ko.secs) for y in ko.syms),'data':sum(y['info']&15==1 and 0<y['shndx']<len(ko.secs) for y in ko.syms),'imports':kpp.versions(ko)[0],'exports':export_values(ko),'relocations':sum(s['size']//24 for s in ko.secs if s['type']==4),'kcfi_ids':[(y['n'],hex(y['val']&0xffffffff)) for y in ko.syms if y['n'].startswith('__kcfi_typeid_')]}
tab(N/'reference/stock-normalized.tsv',['module','bytes','stock_sha256','normalized_sha256','build_id_offset','build_id_length'],refs);(P/'evidence/inventory/stock-inventory.json').write_text(json.dumps(info,indent=2)+'\n')
edges=list(csv.DictReader((A/'DEPENDENCY-EDGES.tsv').open(),delimiter='\t'));ids={r['module_id'] for r in rows};target=next(r['module_id'] for r in rows if r['filename']=='mtk_iommu.ko');selected=[r for r in edges if r['consumer_module_id'] in ids or r['provider_module_ids'] in ids];tab(P/'evidence/inventory/provider-edges-four.tsv',list(edges[0]),[list(r.values()) for r in selected]);external=[r for r in edges if r['consumer_module_id']==target and r['provider_module_ids']!='GKI_CORE'];lines=[]
for r in external:
 assert ';' not in r['provider_module_ids'];name=r['provider_module_ids'].split('@')[0][:-3];lines.append(f"{r['required_crc']}\t{r['symbol']}\tproviders/{name}\t{r['export_type']}\t\n")
(N/'reference/external-provider.symvers').write_text(''.join(lines))
base='5e415e059253ce0d2e61c97108e5f5785d71f06f';new='957dac185efe46cbf6336b0fff9516d84c8cd78f';lineage=[]
files=['drivers/iommu/'+s for s in ['mtk_iommu.c','mtk_iommu.h','Makefile','Kconfig']]+['drivers/misc/mediatek/iommu/'+s for s in ['iommu_debug.c','iommu_secure.c','iommu_test.c','iommu_debug.h','iommu_secure.h','Makefile','Kconfig']]+['drivers/misc/mediatek/smi/mtk-smi-dbg.c']
for f in files:
 blobs=[subprocess.check_output(['git','-C',str(G),'rev-parse',c+':'+f],text=True).strip() for c in [base,new]];lineage.append([f,*blobs,'IDENTICAL' if blobs[0]==blobs[1] else 'DIFFERENT'])
tab(P/'evidence/inventory/source-candidate-blobs.tsv',['file','alps_blob','nothing_blob','comparison'],lineage)
t=W/'kdm';t.mkdir(parents=True,exist_ok=True);ar=subprocess.Popen(['git','-C',str(G),'archive',base],stdout=subprocess.PIPE);subprocess.run(['tar','-x','-C',str(t)],stdin=ar.stdout,check=True);ar.stdout.close();assert ar.wait()==0
subprocess.run(['git','init','-q',str(t)],check=True);subprocess.run(['git','-C',str(t),'add','-Af'],check=True);subprocess.run(['git','-C',str(t),'-c','user.name=LieppOS','-c','user.email=lieppos@local','-c','core.hooksPath=/dev/null','commit','-qm','pinned ALPS'],check=True)
(t/'Kbuild').write_text('# SPDX-License-Identifier: GPL-2.0\n# One owned module; retain upstream vendor includes and flags.\nLINUXINCLUDE := $(DEVCIE_MODULES_INCLUDE) $(LINUXINCLUDE)\nsubdir-ccflags-y += -Werror -I$(srctree)/$(src)/include -I$(srctree)/$(src)/include/uapi\nobj-y += drivers/iommu/\n')
(t/'drivers/iommu/Kbuild').write_text('# SPDX-License-Identifier: GPL-2.0\ninclude $(src)/Makefile\n# Explicitly exclude unrelated ARM/SMMUv3 drivers.\nobj-m := mtk_iommu.o\nobj-y :=\n')
subprocess.run(['git','-C',str(t),'add','-Af'],check=True);(N/'patches/0001-owned-iommu-build-scope.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--cached']));(N/'reference/kdm-tree.txt').write_text(subprocess.check_output(['git','-C',str(t),'write-tree'],text=True));(N/'reference/prov-tree.txt').write_text(subprocess.check_output(['git','-C',str(G),'rev-parse',base+'^{tree}'],text=True))
print('Frozen four identities; only one owned target;',len(external),'real external witnesses')
