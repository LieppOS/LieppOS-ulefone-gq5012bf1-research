#!/usr/bin/env python3
"""Offline, metadata-only accelerator discovery. Never builds or runs a driver.
Run from the research repository: python3 reverse-engineering/accelerator-preparation/inventory.py
Writes only this preparation tree; does not register or move components.
"""
from __future__ import annotations
import collections
import csv
import hashlib
import importlib.util
import json
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
WS = REPO.parent
CA = REPO / 'reverse-engineering/coverage-audit'
STOCK = REPO / 'workspace/gq5012bf1/stock'
GKI = Path('/home/armol/kernel-work/gki-12901745-workspace')
ROOTS = {'KDM': WS/'kernel-research/nothing-mt6878/device_modules',
         'NKM': WS/'kernel-research/nothing-mt6878/kernel_modules',
         'CAM': GKI/'vendor/mediatek/kernel_modules/mtkcam',
         'ALPS': GKI/'lieppos/tinysys/trees/5e41',
         'RECON-KDM': GKI/'kernel_device_modules-6.1'}

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

PP = load_module('accelerator_parity', REPO/'reverse-engineering/scripts/ko-pair-parity.py')
FDT = load_module('accelerator_fdt', CA/'scripts/lib_fdt.py')
FULL_FDT = load_module('accelerator_full_fdt', HERE/'full-fdt.py')

def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter='\t' if path.suffix == '.tsv' else ','))

def table(path, data):
    if not data:  # Do not emit empty boilerplate inventories.
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(data)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(root, *args):
    p = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, check=True)
    return p.stdout.strip()

def cells(values):
    if values and str(values[0]).startswith('bytes:'):
        b = bytes.fromhex(values[0][6:])
        return list(struct.unpack('>'+str(len(b)//4)+'I', b)) if len(b)%4 == 0 else []
    try: return [int(x, 0) for x in values]
    except (TypeError, ValueError): return []

def text(values):
    if values and str(values[0]).startswith('bytes:'):
        return bytes.fromhex(values[0][6:]).rstrip(b'\0').decode(errors='replace').replace('\0', '; ')
    return '; '.join(str(x) for x in values)

def main():
    cfg = json.loads((HERE/'scopes.json').read_text())
    modules = rows(CA/'kernel-modules.tsv'); km = {x['module']: x for x in modules}
    initial = HERE/'ownership-changes.tsv'
    primary = {m:s['component'] for s in cfg['scopes'] for m in s['modules']}
    assert len(primary) == sum(len(s['modules']) for s in cfg['scopes']), 'duplicate primary owner'
    assert set(primary) <= set(km), 'invented stock module'
    if not initial.exists():
        table(initial, [dict(module=m, previous_owner=km[m]['component'], previous_class=km[m]['coverage'],
                            new_owner=primary[m], decision='AUTHORIZED REGISTRATION / SINGLE PRIMARY OWNER',
                            evidence='scopes.json; named DONE scope READMEs; exact ELF and source inventories')
                        for m in sorted(primary)])
    paths = collections.defaultdict(list)
    for p in sorted(STOCK.rglob('*.ko')):
        if p.is_file(): paths[p.name].append(p)
    stock_symbols = rows(REPO/'kernel/stock-intermodule-abi.csv')
    provider = {(x['symbol'],int(x['crc'],16)):x for x in stock_symbols}
    oem = rows(REPO/'kernel/module-map.csv')
    names = {x['module_name']:x['filename'] for x in oem}
    dtpath = REPO/'workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dtb'
    nodes = FULL_FDT.walk(str(dtpath), FDT._decode); bypath={n['path']:n for n in nodes}
    phandles = {v[0]:n for n in nodes if (v:=cells(n['props'].get('phandle',[])))}
    rootpins = {k:git(p,'rev-parse','HEAD') for k,p in ROOTS.items()}
    proofroot = REPO/'reverse-engineering/camera-stack/kernel-isp-imgsys/binary-analysis/per-module'
    all_source = []; dt_ownership = []; all_edges=[]
    for scope in cfg['scopes']:
        out = HERE/scope['component']; out.mkdir(exist_ok=True)
        inv=[]; funcs=[]; objects=[]; imports=[]; exports=[]; gaps=[]; witnesses=[]; source_rows=[]
        for m in scope['modules']:
            mp=paths[m]; assert mp, m
            hashes={sha(p) for p in mp}; assert len(hashes)==1, f'nonidentical stock variants {m}'
            p=mp[0]; ko=PP.KO(str(p))
            mi=collections.defaultdict(list)
            for v in ko.data('.modinfo').split(b'\0'):
                if b'=' in v:
                    k,val=v.decode(errors='replace').split('=',1); mi[k].append(val)
            vers,_=PP.versions(ko); exp=PP.exports(ko)
            fns=[s for s in ko.syms if s['info']&15==2 and s['shndx'] not in (0,0xfff1)]
            objs=[s for s in ko.syms if s['info']&15==1 and s['shndx'] not in (0,0xfff1)]
            for s in fns:
                funcs.append(dict(module=m, symbol=s['n'], section=ko.secs[s['shndx']]['n'], offset=hex(s['val']), bytes=s['size'], evidence=str(p.relative_to(REPO))))
            for s in objs:
                objects.append(dict(module=m, symbol=s['n'], section=ko.secs[s['shndx']]['n'], offset=hex(s['val']), bytes=s['size'], evidence=str(p.relative_to(REPO))))
            for n,crc in sorted(vers.items()):
                pr=provider.get((n,crc),{})
                pmods=[names.get(x,'UNKNOWN:'+x) for x in pr.get('provider_modules','').split(';') if x]
                imports.append(dict(module=m,symbol=n,crc=f'0x{crc:08x}',provider_kind=pr.get('provider_kind','GKI_OR_UNKNOWN'),providers=';'.join(pmods),evidence='kernel/stock-intermodule-abi.csv; ELF __versions'))
                for dep in pmods:
                    all_edges.append(dict(consumer=m,provider=dep,symbol=n,crc=f'0x{crc:08x}',consumer_owner=scope['component'],provider_owner=primary.get(dep,km.get(dep,{}).get('component','UNKNOWN')),evidence='ELF __versions + kernel/stock-intermodule-abi.csv'))
            for n in sorted(exp):
                exports.append(dict(module=m,symbol=n,export_metadata=json.dumps(exp[n],sort_keys=True),evidence='ELF __ksymtab/__kcrctab via canonical ko-pair-parity parser'))
            relocations=sum(s['size']//s['entsz'] for s in ko.secs if s['type'] in (4,9) and s['entsz'])
            fnproof=proofroot/(m[:-3]+'.function-parity.tsv'); datap=proofroot/(m[:-3]+'.data-parity.tsv')
            published=[]
            for axis,fp in [('function',fnproof),('data',datap)]:
                if fp.exists():
                    rr=rows(fp); c=collections.Counter(x['class'] for x in rr)
                    published.append(f'{axis}: '+', '.join(f'{k}={v}' for k,v in sorted(c.items()))+f' ({fp.relative_to(REPO)})')
            parity='; '.join(published) or 'UNKNOWN / no measured target rebuild parity located'
            src_key,rel=scope['sources'][m].split(':',1); src=ROOTS[src_key]/rel
            assert src.exists(), f'absent donor {src}'
            files=[src] if src.is_file() else sorted(p for p in src.rglob('*') if p.is_file() and p.suffix in ('.c','.h','.S') or p.is_file() and p.name in ('Makefile','Kbuild','Kconfig','BUILD.bazel'))
            # The fingerprints identify actual donor inputs, not equivalent stock source.
            fingerprint=hashlib.sha256(''.join(f'{p.relative_to(ROOTS[src_key])}\t{sha(p)}\n' for p in files).encode()).hexdigest()
            sr=dict(module=m,donor=str(src),repository=str(ROOTS[src_key]),commit=rootpins[src_key],input_files=len(files),input_fingerprint=fingerprint,availability='LOCAL SOURCE CANDIDATE; parity not implied',published_parity=parity,device_delta='UNKNOWN until measured; preserve existing camera patches')
            source_rows.append(sr); all_source.append(dict(scope=scope['component'],**sr))
            if src_key == 'KDM':
                for alternative in ('ALPS','RECON-KDM'):
                    q=ROOTS[alternative]/rel
                    if q.exists():
                        fs=[q] if q.is_file() else sorted(p for p in q.rglob('*') if p.is_file() and (p.suffix in ('.c','.h','.S') or p.name in ('Makefile','Kbuild','Kconfig','BUILD.bazel')))
                        digest=hashlib.sha256(''.join(f'{p.relative_to(ROOTS[alternative])}\t{sha(p)}\n' for p in fs).encode()).hexdigest()
                        alt=dict(sr,donor=str(q),repository=str(ROOTS[alternative]),commit=rootpins[alternative],input_files=len(fs),input_fingerprint=digest,availability='ALTERNATIVE PINNED LOCAL CANDIDATE; ALPS archive origin 5e415e059253' if alternative=='ALPS' else 'EXISTING PATCHED WORKSPACE; read-only candidate, do not edit')
                        source_rows.append(alt);all_source.append(dict(scope=scope['component'],**alt))
            for sec in ko.secs:
                if sec['type'] not in (1,) or not sec['n'].startswith(('.rodata','.data')): continue
                raw=ko.b[sec['off']:sec['off']+sec['size']]
                for match in re.finditer(rb'[ -~]{5,}',raw):
                    val=match.group().decode()
                    if re.search(r'(/dev/|ioctl|firmware|\.bin|\.img|r44p|request_|Mali|MDLA|MVPU|H264|H265|HEVC|VP9|AV1|/proc/)',val):
                        witnesses.append(dict(module=m,section=sec['n'],offset=hex(match.start()),string=val,evidence=str(p.relative_to(REPO))))
            inv.append(dict(module=m,owner=scope['component'],stock_paths=';'.join(str(p.relative_to(REPO)) for p in mp),sha256=next(iter(hashes)),bytes=p.stat().st_size,load_phase=km[m]['load_phase'],load_order=km[m]['load_order'],loaded_in_capture=km[m]['loaded_in_capture'],modinfo_depends=','.join(mi.get('depends',[])),modules_dep_transitive=km[m]['depends'],softdep=';'.join(mi.get('softdep',[])),vermagic=';'.join(mi.get('vermagic',[])),compiler=ko.data('.comment').rstrip(b'\0').decode(errors='replace').replace('\0',';'),functions=len(fns),data_symbols=len(objs),imports=len(vers),exports=len(exp),relocations=relocations,kcfi_abs_ids=sum(s['n'].startswith('__kcfi_typeid_') for s in ko.syms),cfi_function_entries=sum(s['n'].startswith('__cfi_') for s in ko.syms),aliases=';'.join(mi.get('alias',[])),published_parity=parity))
            gaps.append(dict(module=m,function_data_state=parity,whole_module_state='NOT ACCEPTED: full axes/B1-B2 closure not established by preparation',remaining='functions + all data/padding + import/export CRCs + KCFI + relocation semantics + symbols + strings + .modinfo/vermagic + B1/B2; cite only measured axes',donor=str(src),evidence=str(p.relative_to(REPO))))
        for filename,data in [('stock-modules.tsv',inv),('functions.tsv',funcs),('data-symbols.tsv',objects),('imports.tsv',imports),('exports.tsv',exports),('source-candidates.tsv',source_rows),('parity-gaps.tsv',gaps),('string-witnesses.tsv',witnesses)]:table(out/filename,data)
        dn=[]; provider_rows=[]
        for n in nodes:
            comps=n['props'].get('compatible',[])
            if not re.search(scope['dt_pattern'],' '.join(comps),re.I):continue
            # Secure APU service is an existing GenieZone interface, not a normal-world APU owner transfer.
            if any('trusty' in c for c in comps):continue
            dp=n['props']; parent=bypath.get(n['parent'],{'props':{}})['props']; rawreg=cells(dp.get('reg',[]))
            ac=(cells(parent.get('#address-cells',[])) or [2])[0]; sc=(cells(parent.get('#size-cells',[])) or [1])[0]
            ranges=[]
            if ac+sc and len(rawreg)%(ac+sc)==0:
                for i in range(0,len(rawreg),ac+sc):
                    addr=sum(v<<(32*(ac-j-1)) for j,v in enumerate(rawreg[i:i+ac])); size=sum(v<<(32*(sc-j-1)) for j,v in enumerate(rawreg[i+ac:i+ac+sc]))
                    ranges.append(f'parent-bus 0x{addr:x}+0x{size:x}')
            refs=[]
            for prop,ncells in [('clocks','#clock-cells'),('power-domains','#power-domain-cells'),('iommus','#iommu-cells'),('mboxes','#mbox-cells'),('resets','#reset-cells')]:
                cs=cells(dp.get(prop,[])); i=0
                while i<len(cs):
                    prov=phandles.get(cs[i]); width=(cells(prov['props'].get(ncells,[])) or [0])[0] if prov else None
                    if prov is None:refs.append(f'{prop}: UNKNOWN phandle 0x{cs[i]:x}');break
                    args=cs[i+1:i+1+width];refs.append(f'{prop}: {prov["path"]} args='+','.join(hex(x) for x in args))
                    provider_rows.append(dict(consumer=n['path'],property=prop,provider=prov['path'],compatible=';'.join(prov['props'].get('compatible',[])),args=','.join(hex(x) for x in args),evidence=str(dtpath.relative_to(REPO))))
                    i+=1+width
            for prop in sorted(dp):
                if prop.endswith('-supply') or prop in ('memory-region','interrupt-parent'):
                    for value in cells(dp[prop]):
                        prov=phandles.get(value)
                        if prov:
                            refs.append(f'{prop}: {prov["path"]}')
                            provider_rows.append(dict(consumer=n['path'],property=prop,provider=prov['path'],compatible=';'.join(prov['props'].get('compatible',[])),args='',evidence=str(dtpath.relative_to(REPO))))
            row=dict(path=n['path'],compatible=';'.join(comps),status=text(dp.get('status',['okay (implicit)'])),owner=scope['component'],register_ranges=';'.join(ranges) or 'NONE/UNKNOWN',reg_raw=' '.join(hex(v) for v in rawreg),interrupts_raw=text(dp.get('interrupts',[])) or 'NONE DECLARED',clock_names=text(dp.get('clock-names',[])) or 'NONE DECLARED',providers='; '.join(refs) or 'NONE DECLARED',memory_region=text(dp.get('memory-region',[])) or 'NONE DECLARED',properties=json.dumps(dp,sort_keys=True),evidence=str(dtpath.relative_to(REPO)))
            dn.append(row)
            for c in comps:
                if re.search(scope['dt_pattern'],c,re.I):
                    dt_ownership.append(dict(compatible=c,node=n['path'],new_owner=scope['component'],evidence='accelerator-preparation/'+scope['component']+'/dt-nodes.tsv; resolved module/source boundary'))
        table(out/'dt-nodes.tsv',dn);table(out/'dt-providers.tsv',provider_rows)
        fw=[x for x in rows(CA/'firmware.tsv') if re.search(scope['firmware_pattern'],x['artifact'],re.I)]
        table(out/'firmware-boundaries.tsv',[dict(artifact=x['artifact'],sha256=x['sha256'],bytes=x['bytes'],current_inventory_owner=x['component'],loader_claim=x['loader'],boundary='RETAIN BINARY; kernel-visible loader/protocol only; firmware algorithm and signatures excluded',evidence=x['evidence']) for x in fw])
        consumers=[]
        for fname,key in [('hals-services.tsv','artifact'),('vendor-services.tsv','service'),('userspace-libraries.tsv','library'),('android-integration.tsv','artifact')]:
            for x in rows(CA/fname):
                if re.search(scope['user_pattern'],x[key],re.I):
                    consumers.append(dict(axis=fname,artifact=x[key],owner=x['component'],coverage=x['coverage'],evidence=x.get('evidence',''),interpretation='STATIC CONSUMER CANDIDATE / not execution or firmware-algorithm proof'))
        table(out/'userspace-consumers.tsv',consumers)
    assert len({x['compatible'] for x in dt_ownership})==len(set((x['compatible'],x['new_owner']) for x in dt_ownership)), 'duplicate compatible owners'
    table(HERE/'dt-ownership.tsv',dt_ownership)
    table(HERE/'dependency-edges.tsv',sorted(all_edges,key=lambda x:(x['consumer'],x['provider'],x['symbol'])))
    table(HERE/'source-candidates.tsv',all_source)
    codec=[]
    for p in sorted((STOCK/'partitions/vendor/etc').glob('media_codecs*.xml')):
        tree=ET.parse(p)
        for node in tree.iter('MediaCodec'):
            codec.append(dict(name=node.get('name',''),mime=node.get('type',''),attributes=json.dumps(node.attrib,sort_keys=True),limits=json.dumps([child.attrib for child in node],sort_keys=True),source=str(p.relative_to(REPO)),sha256=sha(p),state='STOCK XML DECLARATION / not tested codec support or driver-parity proof'))
    table(HERE/'MTK-VCODEC-KERNEL/codec-capabilities.tsv',codec)
    print(f'{len(cfg["scopes"])} scopes; {len(primary)} unique modules; {len(dt_ownership)} node-compatible rows; {len(all_edges)} import/provider edges. Metadata only; no builds.')

if __name__ == '__main__': main()
