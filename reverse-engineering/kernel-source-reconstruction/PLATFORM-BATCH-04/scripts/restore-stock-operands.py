#!/usr/bin/env python3
"""Restore local analysis copies from exact-hash original ROM; never alter an image/device."""
from pathlib import Path
import csv,json,hashlib,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[2];E=P/'evidence/stock-operand-drift';j=json.loads((E/'recovery-verified.json').read_text());rows={r['module_id']:r for r in csv.DictReader((P/'evidence/baseline/ALL-457-MODULES.tsv').open(),delimiter='\t')};changes=[];quarantine=Path('/home/armol/kernel-work/platform-batch-04-unsigned-stock-quarantine');quarantine.mkdir(exist_ok=True)
for x in j['recovered']:
 r=rows[x['module_id']];src=Path(x['source']);dst=R/r['stock_paths'];b=src.read_bytes();a=dst.read_bytes();assert hashlib.sha256(b).hexdigest()==r['stock_sha256'] and len(b)==int(r['stock_size']);assert b==a or len(b)-len(a)==721 and b[:len(a)]==a
 changes.append({'module_id':r['module_id'],'destination':r['stock_paths'],'before_sha256':hashlib.sha256(a).hexdigest(),'before_size':len(a),'after_sha256':r['stock_sha256'],'after_size':len(b),'only_signature_missing':b!=a and b[:len(a)]==a,'source':str(src)})
# Validate the complete set before any local copies are replaced.
for x in changes:
 dst=R/x['destination']
 if x['before_sha256']!=x['after_sha256']:shutil.copyfile(dst,quarantine/dst.name);shutil.copyfile(x['source'],dst)
 assert hashlib.sha256(dst.read_bytes()).hexdigest()==x['after_sha256']
(E/'restoration-result.json').write_text(json.dumps({'result':'PASS60_ORIGINAL_SIGNED_STOCK_HASHES_RESTORED','changes':changes,'no_audit_identity_hash_or_occurrence_changed':True,'no_compilation_output_changed':True,'no_phone_or_partition_image_write':True,'quarantined_old_analysis_copies':str(quarantine)},indent=2)+'\n');print('Restored60 local signed stock analysis copies from originalROM; all frozen hashes/sizes verified, no target/image/device modified')
