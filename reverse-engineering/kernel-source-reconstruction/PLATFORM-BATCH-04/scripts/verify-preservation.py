#!/usr/bin/env python3
"""Every compiled-tree C/H is public or exact full historical source, bundles fresh-recovered."""
from pathlib import Path
import csv,json,subprocess,hashlib,tarfile,io,lzma,tempfile,collections
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=Path('/home/armol/kernel-work/platform-batch-04-cleancheck/ws');T=W/'src/kdm';A=W/'kernel_device_modules-6.1';rev='5e415e059253ce0d2e61c97108e5f5785d71f06f';Q=list(csv.DictReader((P/'SOURCE-REPOSITORIES.tsv').open(),delimiter='\t'));N=(R/Q[0]['repository']).resolve();history={r['target_path']:r for r in json.loads((N/'reference/historical-source-provenance.json').read_text())};paths={p:b for mode,typ,b,p in (l.split(None,3) for l in subprocess.check_output(['git','ls-tree','-r',rev],cwd=A,text=True).splitlines()) if typ=='blob'};tcpc='drivers/misc/mediatek/typec/tcpc';raw=lzma.decompress((N/'reference/tcpc31-public.tar.xz').read_bytes());tar=tarfile.open(fileobj=io.BytesIO(raw));pub31={tcpc+'/'+m.name:tar.extractfile(m).read() for m in tar if m.isfile()};source=list(csv.DictReader((P/'evidence/SOURCE-FILES.tsv').open(),delimiter='\t'));proof=[]
for r in source:
 p=r['path'];b=(T/p).read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256'];gitblob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 if p in history:assert r['sha256']==history[p]['historical_sha256'];kind='EXACT_RECOVERED_WHOLE_HISTORICAL_C_H' if not history[p]['identical_to_public'] else 'IMMUTABLE_PUBLIC_VIA_HISTORICAL_RECOVERY'
 elif p.startswith(tcpc+'/'):assert b==pub31[p];kind='IMMUTABLE_PUBLIC_TCPC31'
 elif p=='drivers/iio/buffer/industrialio-triggered-buffer.c':assert b==subprocess.check_output(['git','show','6b18f0b574ab3267615ae6ce642d5a7c3c21ac09:'+p],cwd=W/'common');kind='IMMUTABLE_PUBLIC_COMMON'
 else:assert paths.get(p)==gitblob,(p,'not authentic immutable C/H');kind='IMMUTABLE_PUBLIC_ALPS'
 proof.append({'path':p,'sha256':r['sha256'],'git_blob':gitblob,'provenance':kind})
with tempfile.TemporaryDirectory() as td:
 d=Path(td);subprocess.run(['git','init','-q',str(d)],check=True)
 for p,h in history.items():
  if h['identical_to_public']:continue
  f=d/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(pub31[p] if p.startswith(tcpc+'/') else subprocess.check_output(['git','show',rev+':'+p],cwd=A))
 subprocess.run(['git','add','-A'],cwd=d,check=True);subprocess.run(['git','apply','--index',str(N/'patches/0002-complete-historical-implementations.patch')],cwd=d,check=True)
 for p,h in history.items():
  if not h['identical_to_public']:assert (d/p).read_bytes()==(T/p).read_bytes(),p
bundles=[]
for q in Q:
 n=(R/q['repository']).resolve();b=P/q['family']/'source'/f'{n.name}.bundle';p=subprocess.run(['git','bundle','verify',str(b)],cwd=n,text=True,capture_output=True);assert p.returncode==0;assert q['commit'] in subprocess.check_output(['git','bundle','list-heads',str(b)],text=True)
 with tempfile.TemporaryDirectory() as td:
  d=Path(td)/'recovered';subprocess.run(['git','clone','-q',str(b),str(d)],check=True);assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=d,text=True).strip()==q['commit'];assert subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=d)==subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=n)
 bundles.append({'family':q['family'],'commit':q['commit'],'bundle_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),'fresh_bundle_recovery':'EXACT_SOURCE_TREE_HEAD'})
E=P/'evidence';(E/'source-provenance.json').write_text(json.dumps(proof,indent=2)+'\n');j={'result':'PASS_ALL_SOURCE_HASHES_COMPLETE_HISTORICAL_PATCHES_THREE_BUNDLE_RECOVERIES','source_file_count':len(proof),'historical_whole_C_H_count':len(history),'complete_modified_files':sum(not h['identical_to_public'] for h in history.values()),'provenance_counts':dict(collections.Counter(x['provenance'] for x in proof)),'bundles':bundles,'no_compiled_target_substitution':True};(E/'source-preservation-result.json').write_text(json.dumps(j,indent=2)+'\n');print(j['result'],j['source_file_count'],j['provenance_counts'])
