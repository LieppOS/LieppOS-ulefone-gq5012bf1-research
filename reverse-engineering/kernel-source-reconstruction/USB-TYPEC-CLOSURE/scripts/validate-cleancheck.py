#!/usr/bin/env python3
"""Validate completed independent builds, including actual bytes and full ABI.
Build Module.symvers's producer field is an absolute workspace path. Compare its
same source-tree-relative producer identity explicitly, retaining all other fields.
This does NOT normalize any ELF byte, fingerprint or acceptance requirement.
"""
from pathlib import Path
import sys,json,hashlib,subprocess
P=Path(__file__).resolve().parents[1];C=Path(sys.argv[1]);E=P/'evidence/fresh-clones'
reports=[json.loads((E/(tag+'.json')).read_text()) for tag in ['F0-B1','F0-B2','F1-B1','F1-B2']]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
outputs=[Path(r['output']) for r in reports]
# Assert real payload bytes, not a manifest that also hashes path-bearing text.
module_names=sorted(p.name for p in outputs[0].glob('*.ko'))
assert len(module_names)==30
for name in module_names:
 for suffix in ['.ko','.stripped']:
  file=name.removesuffix('.ko')+suffix;values=[sha(o/file) for o in outputs];assert len(set(values))==1,('raw module bytes',file,values)
for f in ['INTERMEDIATE-SHA256SUMS','TARGET-SOURCE-TREE','provider/natural-external-provider.symvers','provider/provider-witnesses.json','provider/provider-errors.json']:
 values=[(o/f).read_bytes() for o in outputs];assert all(v==values[0] for v in values[1:]),f
for r,o in zip(reports,outputs):
 W=Path(r['workspace']);assert all((o/f).read_text().strip()=='0' for f in ['object-exit','module-exit'])
 for line in (o/'INTERMEDIATE-SHA256SUMS').read_text().splitlines():
  digest,path=line.split(maxsplit=1);assert sha(W/'src/kdm'/path)==digest,('intermediate object',r['tag'],path)
 for line in (o/'SHA256SUMS').read_text().splitlines():
  digest,path=line.split(maxsplit=1);assert sha(o/path)==digest,('original manifest consistency',r['tag'],path)
 assert len(r['outcomes'])==30
 assert sum(row['strict_verifier_exit']==0 for row in r['outcomes'])==25
 assert {row['module'] for row in r['outcomes'] if row['strict_verifier_exit']!=0}=={'charger_class','mtk_chg_type_det','rt_pd_manager','tcpc_mt6375','tcpc_class'}
 for key in ['source_recovered_from_bundle','original_owned_paths_unavailable','all_30_source_built']:assert r[key]
for f in ['.config','Module.symvers']:
 values=[(Path(r['workspace'])/'kout'/f).read_bytes() for r in reports];assert all(v==values[0] for v in values[1:]),f
abis=[]
for r,o in zip(reports,outputs):
 prefix=str(Path(r['workspace'])/'src/kdm')+'/'
 rows=[]
 for line in (o/'batch-full.Module.symvers').read_text().splitlines():
  fields=line.split('\t');assert len(fields)==5 and fields[2].startswith(prefix),fields
  # Same actual source producer, not simply dropping the owner column.
  owner=fields[2][len(prefix):];assert not owner.startswith('/') and '..' not in Path(owner).parts
  rows.append([fields[0],fields[1],owner,fields[3],fields[4]])
 abis.append(rows)
assert all(rows==abis[0] for rows in abis[1:]),'ABI records including producer identity differ'
assert len(abis[0])==437
for r in reports[1:]:assert (C/reports[0]['tag']/'five-comparison/summary.json').read_bytes()==(C/r['tag']/'five-comparison/summary.json').read_bytes()
M=Path('/home/armol/kernel-work/usb-typec-closure-proof/mirror');before=json.loads((P/'evidence/baseline/readonly-mirror.json').read_text())
for row in before['inputs']:
 if 'file' in row:assert sha(M/row['file'])==row['sha256']
 else:assert subprocess.check_output(['git','-C',str(M/(row['id']+'.git')),'rev-parse',row['commit']+'^{tree}'],text=True).strip()==row['tree']
assert not any(p.stat().st_mode&0o222 for p in M.rglob('*') if not p.is_symlink())
result={'result':'PASS_FOUR_FRESH_SOURCE_BUILDS_WITH_FIVE_EXPECTED_STRICT_REJECTIONS','runs':reports,'source_commits':json.loads((E/'source-commits.json').read_text()),'all_30_raw_and_stripped_modules_deterministic':True,'all_157_actual_intermediate_objects_deterministic':True,'config_core_symvers_and_provider_inputs_byte_identical':True,'joint_437_export_records_crc_name_license_namespace_and_relative_producer_exact':True,'joint_Module_symvers_raw_text_not_identical':'Only absolute producer workspace prefix differs; original files/hashes retained and verified. This is not an ELF/CRC/source-metadata exemption.','readonly_mirror_unchanged':True,'newly_certified':0,'normalization':'Strict ELF unchanged: structural GNU20 only, no metadata/fingerprint waiver'}
(E/'result.json').write_text(json.dumps(result,indent=2)+'\n');(E/'progress.json').write_text(json.dumps({'phase':'PASS_WITH_FIVE_DOCUMENTED_C_BLOCKERS'},indent=2)+'\n');print(result['result'],'30 raw/stripped modules and157 objects byte-identical;437 ABI records exact')
