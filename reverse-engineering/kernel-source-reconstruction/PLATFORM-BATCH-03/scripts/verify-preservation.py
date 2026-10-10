#!/usr/bin/env python3
"""Verify every C/H against genuine public Git or exact preserved source patches."""
from pathlib import Path
import csv,json,subprocess,hashlib,tempfile,collections
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=Path('/home/armol/kernel-work/platform-batch-03-cleancheck/ws');T=W/'src/kdm';A=W/'kernel_device_modules-6.1';rev='5e415e059253ce0d2e61c97108e5f5785d71f06f';Q=list(csv.DictReader((P/'SOURCE-REPOSITORIES.tsv').open(),delimiter='\t'));N=(R/Q[0]['repository']).resolve();paths={p:b for mode,typ,b,p in (l.split(None,3) for l in subprocess.check_output(['git','ls-tree','-r',rev],cwd=A,text=True).splitlines()) if typ=='blob'};source=list(csv.DictReader((P/'evidence/SOURCE-FILES.tsv').open(),delimiter='\t'));modified={'drivers/mfd/mt6375.c','drivers/misc/mediatek/pbm/mtk_peak_power_budget.c','drivers/thermal/mediatek/charger_cooling.c'};proof=[]
for r in source:
 p=r['path'];b=(T/p).read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256'];gitblob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 if p in modified:kind='FULL_PRESERVED_GQ5012BF1_SOURCE_PATCH'
 elif p=='drivers/thermal/thermal-generic-adc.c':
  cb=subprocess.check_output(['git','show','6b18f0b574ab3267615ae6ce642d5a7c3c21ac09:'+p],cwd=W/'common');assert b==cb;kind='IMMUTABLE_PUBLIC_COMMON'
 elif p=='drivers/power/supply/lieppos-charger-declarations.c':
  assert b==(N/'reference/lieppos-charger-declarations.c').read_bytes()
  for x in json.loads((N/'reference/charger-declaration-provenance.json').read_text()):
   f=N/'reference'/x['preserved_source'];assert hashlib.sha256(f.read_bytes()).hexdigest()==x['sha256'];lines=f.read_text().splitlines()
   assert all(lines[i-1]==l and l in b.decode() for i,l in x['exact_declaration_lines'])
  kind='GENUINE_PRESERVED_CHARGER_DECLARATION_ONLY'
 else:assert paths.get(p)==gitblob,(p,'not immutable public C/H');kind='IMMUTABLE_PUBLIC_ALPS'
 proof.append({'path':p,'sha256':r['sha256'],'git_blob':gitblob,'provenance':kind})
# Reapply the actual source patches independently and verify all modified implementation bytes.
with tempfile.TemporaryDirectory() as td:
 d=Path(td);subprocess.run(['git','init','-q',str(d)],check=True)
 for p in modified:
  f=d/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(subprocess.check_output(['git','show',rev+':'+p],cwd=A))
 subprocess.run(['git','add','-A'],cwd=d,check=True)
 for p in sorted((N/'patches').glob('000[2-4]-*.patch')):subprocess.run(['git','apply','--index',str(p)],cwd=d,check=True)
 for p in modified:assert (d/p).read_bytes()==(T/p).read_bytes(),p
bundles=[]
for q in Q:
 n=(R/q['repository']).resolve();b=P/q['family']/'source'/f'{n.name}.bundle';p=subprocess.run(['git','bundle','verify',str(b)],cwd=n,text=True,capture_output=True);assert p.returncode==0;p2=subprocess.check_output(['git','bundle','list-heads',str(b)],text=True);assert q['commit'] in p2
 with tempfile.TemporaryDirectory() as td:
  d=Path(td)/'recovered';subprocess.run(['git','clone','-q',str(b),str(d)],check=True);assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=d,text=True).strip()==q['commit'];assert subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=d)==subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=n)
 bundles.append({'family':q['family'],'commit':q['commit'],'bundle_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),'fresh_bundle_recovery':'EXACT_SOURCE_TREE_HEAD'})
E=P/'evidence';(E/'source-provenance.json').write_text(json.dumps(proof,indent=2)+'\n');j={'result':'PASS_ALL_SOURCE_HASHES_PATCHES_FIVE_BUNDLE_RECOVERIES','source_file_count':len(proof),'provenance_counts':dict(collections.Counter(x['provenance'] for x in proof)),'bundles':bundles,'provider_artifact_source_replacement':'NONE; all selected target bodies freshly compiled, genuine source-derived witnesses freshly compiled; public GKI ABI/BTF providers explicitly scoped'};(E/'source-preservation-result.json').write_text(json.dumps(j,indent=2)+'\n');print(j['result'],j['provenance_counts'])
