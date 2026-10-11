#!/usr/bin/env python3
"""Bounded new AW helper-composition experiment, private source outputs only.

The compared scene ordering is unchanged (new<=old inserts before equal keys).
A pointer-to-fixed-array parameter retains source-level bounds/traps; no flat
pointer, missing-bounds, profile/protection or hardware change is introduced.
These are diagnostic candidates, not an asserted original OEM release.
"""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[1]
W=Path('/home/armol/kernel-work/allc/aw/ws')
TARGET=W/'src/kdm/sound/soc/codecs/aw883xx/aw883xx_bin_parse.c'
BASE=P/'evidence/aw883xx/f1-int8_t-uint8_t.c'
ROOT=Path('/home/armol/kernel-work/allc/aw/helper-probe')
ROOT.mkdir(exist_ok=True)
REC=Path('/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_audio_ulefone_gq5012bf1')
reference=next(x for x in csv.DictReader((P/'C-CLOSURE-MANIFEST.tsv').open(),delimiter='\t') if x['filename']=='aw883xx_driver.ko')
STOCK=Path('/home/armol/kernel-work/allc/stock-ops')/reference['stock_partition']/reference['filename']
assert hashlib.sha256(STOCK.read_bytes()).hexdigest()==reference['stock_sha256']
source=BASE.read_text()
old='''\t\tfor (j = 0; j < num; j++)
\t\t\tif (cfg_dde[i].dev_profile <= cfg_dde[index[j]].dev_profile)
\t\t\t\tbreak;
\t\tfor (k = num; k > j; k--)
\t\t\tindex[k] = index[k - 1];
\t\tindex[j] = i;'''
assert source.count(old)==1
anchor='static int aw_dev_parse_scene_v_1_0_0_0('
assert source.count(anchor)==1
spec=importlib.util.spec_from_file_location('kpp',REC/'scripts/ko-pair-parity.py');kpp=importlib.util.module_from_spec(spec);spec.loader.exec_module(kpp)
a=kpp.KO(STOCK)
def funcs(k):
 return {(x['n'],x['size']):k.b[k.secs[x['shndx']]['off']+x['val']:k.secs[x['shndx']]['off']+x['val']+x['size']] for x in k.syms if x['info']&15==2 and 0<x['shndx']<len(k.secs)}
afunc=funcs(a)
if not (ROOT/'pre-experiment-input.c').exists():shutil.copy2(TARGET,ROOT/'pre-experiment-input.c')
variants=[('control',None,None),('helper-i8-i8','int8_t','int8_t'),('helper-int-i8','int','int8_t'),('helper-u8-i8','uint8_t','int8_t'),('helper-i8-int','int8_t','int')]
results=[]
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PATH':str(W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin')+':'+os.environ['PATH'],
 'COMMON':str(W/'common'),'KO':str(W/'kout'),'KDM_DIR':str(W/'src/kdm'),
 'KBUILD_BUILD_USER':'lieppos','KBUILD_BUILD_HOST':'audio-build','KBUILD_BUILD_VERSION':'1','KBUILD_BUILD_TIMESTAMP':'Thu Oct 8 12:00:00 UTC 2026'}
for name,jtype,ktype in variants:
 out=ROOT/name;out.mkdir(exist_ok=True)
 text=source
 if jtype:
  helper=f'''static void aw_scene_index_insert(struct aw_cfg_dde_v_1_0_0_0 *dde,
\t\tuint32_t (*slots)[AW_SCENE_INDEX_MAX], int entry, uint8_t count)
{{
\t{jtype} j;
\t{ktype} k;
\tfor (j = 0; j < count; j++)
\t\tif (dde[entry].dev_profile <= dde[(*slots)[j]].dev_profile)
\t\t\tbreak;
\tfor (k = count; k > j; k--)
\t\t(*slots)[k] = (*slots)[k - 1];
\t(*slots)[j] = entry;
}}

'''
  text=text.replace(old,'\t\taw_scene_index_insert(cfg_dde, &index, i, num);').replace(anchor,helper+anchor)
  text=text.replace('\tint8_t j, k;','\tint8_t k;')
 (out/'aw883xx_bin_parse.c').write_text(text);TARGET.write_text(text)
 cmd=['taskset','-c','0-3','nice','-n','19','bash',str(REC/'scripts/kb.sh'),'-j4','KBUILD_EXTRA_SYMBOLS='+str(W/'out/D1/provider/natural-external-provider.symvers'),'sound/soc/codecs/aw883xx/aw883xx_driver.ko']
 with (out/'build.log').open('w') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
 record=dict(name=name,command=cmd,compile_exit=r.returncode,source_sha256=hashlib.sha256(text.encode()).hexdigest())
 if r.returncode==0:
  src=TARGET.parent/'aw883xx_driver.ko';rebuilt=out/'aw883xx_driver.stripped'
  subprocess.run([str(W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin/llvm-strip'),'--strip-debug','-o',str(rebuilt),str(src)],check=True)
  b=kpp.KO(rebuilt);bf=funcs(b);match=sum(afunc[key]==bf.get(key) for key in afunc)
  target=[s for s in b.syms if s['n']=='aw883xx_dev_cfg_load' and s['info']&15==2]
  record.update(functions_stock=len(afunc),functions_rebuild=len(bf),raw_exact=match,cfg_load_bytes=target[0]['size'],bytes=len(b.b),rebuild_sha256=hashlib.sha256(b.b).hexdigest(),stock_sha256=hashlib.sha256(a.b).hexdigest(),verdict='REJECTED' if match!=len(afunc) else 'FUNCTION_CANDIDATE_ONLY')
  imports_a,_=kpp.versions(a);imports_b,_=kpp.versions(b);record['import_crc_equal']=imports_a==imports_b
  objdump=W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin/llvm-objdump'
  for label,file in [('stock',STOCK),('rebuild',rebuilt)]:
   x=subprocess.run([str(objdump),'-dr','--disassemble-symbols=aw883xx_dev_cfg_load',str(file)],capture_output=True,text=True);(out/(label+'-cfg-load.s')).write_text(x.stdout)
 else:record.update(verdict='COMPILE_FAILURE',diagnostic=(out/'build.log').read_text(errors='replace')[-3000:])
 results.append(record);(ROOT/'results.json').write_text(json.dumps(dict(hypothesis='Helper-local independent loop types and fixed-array bounds can account for stock insertion-loop/trap shape; compared with the preserved diagnostic best, not a repeated inline grid',scope='No whole-module acceptance or behavioral promotion',variants=results),indent=2)+'\n');print(name,record,flush=True)
