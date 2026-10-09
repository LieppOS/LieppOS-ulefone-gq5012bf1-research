#!/usr/bin/env python3
"""Record authoritative four-module baseline and generate scope-only patches from pinned ALPS.
Run once to prepare the maintained recipe; no binaries copied into generated source.
Usage: prepare-reference.py <maintained-repo> <space-free-scratch> <public-repo-with-both-pins>
"""
from pathlib import Path
import csv,sys,subprocess,hashlib,json
N,W,G=map(lambda s:Path(s).resolve(),sys.argv[1:]);R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parents[1];A=R/'reverse-engineering/kernel-source-parity-audit'
sys.path.insert(0,str(N/'scripts'));from normalize import normalized,kpp
j=json.load((A/'evidence/audit-summary.json').open());names=j['next_modules'];assert names==['mt6315-regulator.ko','mt6363-regulator.ko','mtk-dvfsrc-regulator.ko','rt6160-regulator.ko']
allrows=list(csv.DictReader((A/'ALL-457-MODULES.tsv').open(),delimiter='\t'));rows=[r for r in allrows if r['filename'] in names];assert len(rows)==4 and all(r['source_status']=='D' for r in rows)
def tab(p,head,rr):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(head);w.writerows(rr)
tab(P/'evidence/inventory/audit-baseline-four.tsv',list(rows[0]),[list(r.values()) for r in rows]);refs=[];info={}
for r in rows:
    path=R/r['stock_paths'];ko=kpp.KO(path);sha=hashlib.sha256(ko.b).hexdigest();assert sha==r['stock_sha256'] and len(ko.b)==int(r['stock_size'])
    b,off,count=normalized(ko);m=r['filename'][:-3];refs.append([m,len(b),sha,hashlib.sha256(b).hexdigest(),hex(off),count])
    info[m]={'stock_sha256':sha,'bytes':len(b),'paths':r['stock_paths'].split(';'),'owner':r['component_owner'],'modinfo':[v.decode(errors='replace') for v in ko.data('.modinfo').split(b'\0') if v], 'build_id_range':[off,count],'sections':len(ko.secs),'function_symbols':sum(y['info']&15==2 and 0<y['shndx']<len(ko.secs) for y in ko.syms),'data_symbols':sum(y['info']&15==1 and 0<y['shndx']<len(ko.secs) for y in ko.syms),'imports':len(kpp.versions(ko)[0]),'kcfi_ids':[(y['n'],hex(y['val']&0xffffffff)) for y in ko.syms if y['n'].startswith('__kcfi_typeid_')]}
tab(N/'reference/stock-normalized.tsv',['module','bytes','stock_sha256','normalized_sha256','build_id_offset','build_id_length'],refs)
(P/'evidence/inventory/stock-inventory.json').write_text(json.dumps(info,indent=2)+'\n')
edges=list(csv.DictReader((A/'DEPENDENCY-EDGES.tsv').open(),delimiter='\t'));ids={r['module_id'] for r in rows};edges=[r for r in edges if r['consumer_module_id'] in ids];tab(P/'evidence/inventory/provider-edges.tsv',list(edges[0]),[list(r.values()) for r in edges])
external=[r for r in edges if r['provider_module_ids'].startswith('mtk-dvfsrc.ko@')];assert len(external)==4
(N/'reference/external-provider.symvers').write_text(''.join(f"{r['required_crc']}\t{r['symbol']}\tdrivers/soc/mediatek/mtk-dvfsrc\t{r['export_type']}\t\n" for r in external))
base='5e415e059253ce0d2e61c97108e5f5785d71f06f';new='957dac185efe46cbf6336b0fff9516d84c8cd78f';lineage=[]
for r in rows:
    f='drivers/regulator/'+r['filename'][:-3]+'.c'
    blobs=[subprocess.check_output(['git','-C',str(G),'rev-parse',c+':'+f],text=True).strip() for c in [base,new]];lineage.append([f,*blobs,'IDENTICAL' if blobs[0]==blobs[1] else 'DIFFERENT'])
tab(P/'evidence/inventory/source-candidate-blobs.tsv',['file','alps_blob','nothing_blob','comparison'],lineage)
for kind,scope,obj,patch in [('kdm','drivers/regulator','mt6315-regulator.o mt6363-regulator.o mtk-dvfsrc-regulator.o rt6160-regulator.o','0001-owned-regulators-build-scope.patch'),('prov','drivers/soc/mediatek','mtk-dvfsrc.o','0002-dvfsrc-provider-witness-scope.patch')]:
    t=W/kind;t.mkdir(parents=True,exist_ok=True)
    archive=subprocess.Popen(['git','-C',str(G),'archive',base],stdout=subprocess.PIPE)
    subprocess.run(['tar','-x','-C',str(t)],stdin=archive.stdout,check=True);archive.stdout.close();assert archive.wait()==0
    subprocess.run(['git','init','-q',str(t)],check=True);subprocess.run(['git','-C',str(t),'add','-Af'],check=True);subprocess.run(['git','-C',str(t),'-c','user.name=LieppOS','-c','user.email=lieppos@local','-c','core.hooksPath=/dev/null','commit','-qm','pinned ALPS'],check=True)
    (t/'Kbuild').write_text('# SPDX-License-Identifier: GPL-2.0\n# Explicit owned scope; original include ordering and target flags retained.\nLINUXINCLUDE := $(DEVCIE_MODULES_INCLUDE) $(LINUXINCLUDE)\nsubdir-ccflags-y += -Werror -I$(srctree)/$(src)/include -I$(srctree)/$(src)/include/uapi\nobj-y += '+scope+'/\n')
    (t/scope/'Kbuild').write_text('# SPDX-License-Identifier: GPL-2.0\ninclude $(src)/Makefile\nobj-m := '+obj+'\nobj-y :=\n');subprocess.run(['git','-C',str(t),'add','-Af'],check=True)
    (N/'patches'/patch).write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--cached']))
    tree=subprocess.check_output(['git','-C',str(t),'write-tree'],text=True).strip();(N/'reference'/f'{kind}-tree.txt').write_text(tree+'\n');print(kind,tree)
print('recorded four identities,',len(edges),'provider edges; source candidate comparison',lineage)
