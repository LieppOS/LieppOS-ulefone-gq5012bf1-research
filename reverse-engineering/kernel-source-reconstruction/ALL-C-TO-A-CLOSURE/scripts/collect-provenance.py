#!/usr/bin/env python3
"""Record immutable source/bundle/history provenance without changing any source tree."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--workspace', type=Path, default=Path('/home/armol/kernel-work/allc'))
args = parser.parse_args()
W = args.workspace.resolve()
configs = {
 'cmdq': ('059e2fe439309c3adc2e95b87aa547967e7e5f80', 'cmdq-allc.bundle'),
 'connectivity': ('40bf42967a213af6faa45a6a579571973b8e5d15', 'connectivity-allc.bundle'),
 'thermal_cooling': ('9e0e1a0df474f1e5a748d0302fba8445f13c996d', 'thermal-allc.bundle')}

pins, changes, bundles = [], [], []
for family, (tested, bundle_name) in configs.items():
    repo = R.parent/f'android_kernel_modules_{family}_ulefone_gq5012bf1-allc'
    def git(*a):
        return subprocess.check_output(['git','-C',str(repo),*a],text=True).strip()
    assert git('status','--porcelain') == '', repo
    head, tree = git('rev-parse','HEAD'), git('rev-parse','HEAD^{tree}')
    docs = git('diff','--name-only',tested,head).splitlines()
    assert set(docs).issubset({'README.md','scripts/__pycache__/normalize.cpython-314.pyc'}), docs
    for x in csv.DictReader((repo/'SOURCE-PINS.tsv').open(),delimiter='\t'):
        pins.append(dict(family=family,id=x['id'],url=x['url'],commit=x['commit'],
                         subtree=x['subtree'],tree_id=x['tree_id'],role=x['role']))
    pins.append(dict(family=family,id='maintained_recipe',url='../'+repo.name,
                     commit=head,subtree='.',tree_id=tree,role='Final maintained recipe; tested build commit '+tested))
    changes.append(dict(family=family,maintained_repo='../'+repo.name,build_commit=tested,
                        final_commit=head,post_build_changes=';'.join(docs) or 'NONE',
                        correction='Microtrust configuration/type visibility' if family=='cmdq' else
                                   'Reproduce OEM split-BTF base from pinned public MTK ACK; native module BTF encoding',
                        stock_binary_input='NONE',recovery_bundle='bundles/'+bundle_name))
    bundle=P/'bundles'/bundle_name
    v=subprocess.run(['git','-C',str(repo),'bundle','verify',str(bundle)],capture_output=True,text=True)
    assert v.returncode==0, v.stderr
    bundles.append(dict(family=family,path='bundles/'+bundle_name,bytes=bundle.stat().st_size,
                        sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),verify_exit=0,
                        final_commit=head,tree=tree))

def tsv(name,data):
    with (P/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(data[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(data)
legacy = json.loads((P/'evidence/legacy-source-search/zte-tkcore-manifest.json').read_text())
pins.append(dict(family='legacy-tkcore-candidate',id='zte-tkcore-3.2p3',
    url='https://github.com/'+legacy['repo'],commit=legacy['commit'],subtree='.',
    tree_id=legacy['tree'],role='Rejected drop-in candidate; normal-world tkcore core/include declarations provide historical constraints, not stock source acceptance'))
tsv('SOURCE-PINS.tsv',pins);tsv('SOURCE-CHANGES.tsv',changes)
(P/'evidence/bundle-verification.json').write_text(json.dumps(bundles,indent=2)+'\n')
history=[]
for name in ['nothing-kdm','micode-kdm']:
    repo=W/(name+'.git')
    refs=subprocess.check_output(['git','--git-dir',str(repo),'for-each-ref',
        '--format=%(refname)\t%(objectname)'],text=True).splitlines()
    url=subprocess.run(['git','--git-dir',str(repo),'remote','get-url','origin'],capture_output=True,text=True)
    history.append(dict(repo=name,recorded_origin=url.stdout.strip(),
                        refs=[dict(ref=l.split('\t')[0],commit=l.split('\t')[1]) for l in refs]))
(P/'evidence/srcversion/fetched-history-refs.json').write_text(json.dumps(history,indent=2)+'\n')
experiments = [
 ('CMDQ-OPAQUE-GRAPH','CMDQ','Recursive visibility subset search','Stock CRC hit for six opaque type nodes; diagnostic only, not installed','SUPPORTED_DIAGNOSTIC','evidence/cmdq/visibility-search-hit.log'),
 ('CMDQ-TEE-BOTH-OFF','CMDQ','Disable both Microtrust and Trustonic','GenieZone provider cannot compile without GP header include path','REJECTED','CMDQ-CRC-TYPE-GRAPHS.md'),
 ('CMDQ-MICROTRUST-OFF','CMDQ','Disable board-inapplicable Microtrust subtree','35/35 joint strict B1/B2, four selected modules A','ACCEPTED','evidence/cmdq/'),
 ('BTF-GKI','BTF','Use official GKI base BTF','130351 types; +15/+389 reference residual','REJECTED','OEM-BTF-BASE-INVESTIGATION.md'),
 ('BTF-MTK-GKI-CONFIG','BTF','MTK ACK with generic GKI config','130348 types; not stock base','REJECTED','OEM-BTF-BASE-INVESTIGATION.md'),
 ('BTF-MTK-VENDOR-RELEASE','BTF','MTK ACK vendor config, Kleaf flags and OEM release length','Exact base .BTF hash; four selected modules strict B1/B2 accepted','ACCEPTED','evidence/connectivity/;evidence/thermal/'),
 ('SRCV-NOTHING','USB','Coherent and one-file-varied historical inputs, upstream sumversion','1100 combinations across four modules; no stock srcversion hit','REJECTED_CANDIDATES','evidence/srcversion/history-scan.json'),
 ('SRCV-MICODE','USB','Fetched branch histories with same traced ordered inputs','4443 combinations across four modules; no stock srcversion hit','REJECTED_CANDIDATES','evidence/srcversion/history-scan-micode.json'),
 ('AW-GRID-1','AUDIO','Index/count type grid','15 builds; no accepted ELF','REJECTED_CANDIDATES','evidence/aw883xx/grid.log'),
 ('AW-GRID-2','AUDIO','Empty-list fast path x index/count type grid','30 builds; best heuristic diff 255 lines','REJECTED_CANDIDATES','evidence/aw883xx/grid2.log'),
 ('AW-GRID-3','AUDIO','64-bit indices/counts and bool/int parameter type grid','45 builds; no improvement on best diagnostic candidate','REJECTED_CANDIDATES','evidence/aw883xx/grid3.log'),
 ('AW-BEST-CORROBORATION','AUDIO','Rebuild best candidate for full function report','235/236 bodies exact; cfg_load 3564 vs stock3560; C retained','REJECTED','evidence/aw883xx/best-full-parity.txt'),
 ('ST21-VENDOR-ENV','LEGACY','Build historical source in generic current vendor environment','6/24 bodies exact, 25 functions; configuration mismatch, not useful baseline','REJECTED_ENVIRONMENT','LEGACY-C-RECONSTRUCTION.md'),
 ('ST21-HISTORICAL-ENV','LEGACY','Replay preserved historical flags with isolated outputs','24/24 bodies exact vs preserved object; 22/24 vs stock','BASELINE_REPRODUCED','evidence/st21nfc/historic-baseline-vs-preserved-object.txt'),
 ('ST21-PUBLIC-BLOBS','LEGACY','Full union C/header Cartesian product under reproduced historical command','28 pairs;4 compile;24 incompatible I2C probe API;no ioctl/ping matches','REJECTED_CANDIDATES','evidence/st21nfc/public-history-object-scan.json'),
 ('ST21-SRCV','LEGACY','Natural upstream fingerprint over authentic historical C/header pairs','Nothing20+MiCode28 tests;no stock fingerprint hit','REJECTED_CANDIDATES','evidence/srcversion/st21-nothing-kdm.json;evidence/srcversion/st21-micode-kdm.json')]
experiments.append(('TKCORE-ZTE-3.2P3','LEGACY','Pinned public TrustKernel core/include source and compile-only layout probe',
    '52 verified blobs;tee size0x158/context0xc8 versus stock0x138/0xd0;not compatible newer6:1.1-k6.6 lineage',
    'REJECTED_DROP_IN_HISTORICAL_CONSTRAINTS_RECOVERED','evidence/legacy-source-search/zte-tkcore-manifest.json;evidence/legacy-source-search/public-layout-result.json'))
tsv('EXPERIMENTS.tsv',[dict(id=a,group=b,hypothesis=c,measured_result=d,result=e,evidence=f) for a,b,c,d,e,f in experiments])
print(len(pins),'pin records;',len(changes),'maintained source families;',len(bundles),'verified bundles;',len(experiments),'experiment records')
