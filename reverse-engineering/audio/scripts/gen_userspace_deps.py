#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,hashlib,sys
root=Path(sys.argv[1])
out=Path(__file__).resolve().parents[1]/'userspace/library-dependencies.tsv'
patterns=[
'bin/hw/android.hardware.audio.service.mediatek','lib64/hw/android.hardware.audio@7.1-impl-mediatek.so',
'lib64/hw/audio.primary.mediatek.so','lib64/hw/audio.primary.mt6878.so',
'lib64/libMtkSpeechEnh.so','lib64/libMtkSpeechEnh_swb.so','lib64/hw/awinic.audio.effect.so',
'lib64/libaudiosmartpamtk.so','lib64/libawinicsmartpaparse.so','lib64/libaudio_param_parser-vnd.so',
'lib64/libaudiocomponentengine_vendor.so','lib64/soundfx/libaudiopreprocessing_mtk.so']
with out.open('w') as f:
 f.write('file\tsize\tsha256\tneeded\n')
 for n in patterns:
  p=root/n
  if not p.exists():continue
  d=p.read_bytes(); o=subprocess.run(['llvm-readelf','-d',str(p)],capture_output=True,text=True).stdout
  need=[re.search(r'\[(.*)\]',x).group(1) for x in o.splitlines() if '(NEEDED)' in x]
  f.write(f'{n}\t{len(d)}\t{hashlib.sha256(d).hexdigest()}\t{";".join(need)}\n')
