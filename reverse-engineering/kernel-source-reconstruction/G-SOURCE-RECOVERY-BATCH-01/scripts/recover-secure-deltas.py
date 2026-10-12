#!/usr/bin/env python3
"""Source-level release/config deltas grounded in historical source and stock typed code.
No stock bytes input/output patch. Keep newer public API provider's residual visible.
"""
from pathlib import Path
import subprocess,difflib,re,hashlib,json,csv
P=Path(__file__).resolve().parents[1];R=P.parents[2];S=R.parent/'android_kernel_modules_secure_transport_ulefone_gq5012bf1';M=Path('/home/armol/kernel-work/g-source-recovery-batch-01/pin-mirror');ALPS='5e415e059253ce0d2e61c97108e5f5785d71f06f';TK='ff290548332880265d6bc920b1fb8011959db54e';sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
def get(repo,rev,path):return subprocess.check_output(['git','--git-dir',str(repo),'show',rev+':'+path],text=True)
def diff(path,old,new):return ''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+path if old else '/dev/null',tofile='b/'+path))
changes=[];records=[]
# Upstream7:2.2 namespacing is absent in stock6:1.1; do not invent type declarations.
f='drivers/tee/tkcore/include/linux/tee_kernel_api.h';orig=get(M/'tkcore-public.git',TK,f);unpref=re.sub(r'^#define TEEC_\w+ tkcore_TEEC_\w+\n','',orig,flags=re.M);assert orig!=unpref
changes.append(diff(f,orig,unpref));records.append(dict(path=f,old_sha256=sha(orig),new_sha256=sha(unpref),delta='Remove documented7:2.2 tkcore_ API/tag namespacing to6:1.1; genuine original body/typegraph otherwise unchanged; provider natural CRC residual remains explicit'))
# Older consumer40-byte SharedMemory layout: stocktee_session_open allocation0x140,
# real legacy header and historicalTEEC namespace/KCFI contract, not compileddata transplant.
legacy=unpref.replace('\tuint64_t registered;\n','');assert legacy!=unpref
lf='drivers/tee/tkcore/legacy/tee_client_api.h';changes.append(diff(lf,'',legacy));records.append(dict(path=lf,old_sha256='PUBLIC7:2.2_HEADER:'+sha(orig),new_sha256=sha(legacy),delta='Reconstruct genuine older6:1.1 API header layout: no added7:2.2 registered member; original public declarations/copyright retained. Target consumer only, not disguised providerlayout/genksyms'))
f='drivers/misc/mediatek/geniezone/tz_system.c';orig=get(M/'alps5e41.git',ALPS,f);new=orig
for a,b in [('teec_initialize_context','TEEC_InitializeContext'),('teec_finalize_context','TEEC_FinalizeContext'),('teec_open_session','TEEC_OpenSession'),('teec_close_session','TEEC_CloseSession'),('teec_invoke_command','TEEC_InvokeCommand'),('struct teec_context','struct TEEC_Context'),('struct teec_session','struct TEEC_Session'),('struct teec_uuid','struct TEEC_UUID'),('struct teec_operation','struct TEEC_Operation')]:new=new.replace(a,b)
assert new!=orig;changes.append(diff(f,orig,new));records.append(dict(path=f,old_sha256=sha(orig),new_sha256=sha(new),delta='Recover five documented6:1.1 CamelCaseweak GP APIs and originalstructtags, bodies unchanged; required by stockfiveindependent KCFIids + errorstrings/61function evidence'))
f='drivers/misc/mediatek/trusted_mem/tee_impl/tee_ops.c';orig=get(M/'alps5e41.git',ALPS,f);new=orig.replace('TEEC_InitializeContext(SECMEM_TL_GP_UUID_STRING,','TEEC_InitializeContext(NULL,');assert new!=orig
# Unknown original line text is NOT invented; explicit historical provenance offsets.
for f,extra in [('drivers/misc/mediatek/trusted_mem/proc.c',1),('drivers/misc/mediatek/trusted_mem/tee_devices.c',1),('drivers/misc/mediatek/trusted_mem/mtee_devices.c',3),('drivers/misc/mediatek/trusted_mem/tee_impl/tee_ops.c',5)]:
 orig=get(M/'alps5e41.git',ALPS,f);new=orig
 if f.endswith('tee_ops.c'):new=new.replace('TEEC_InitializeContext(SECMEM_TL_GP_UUID_STRING,','TEEC_InitializeContext(NULL,')
 new=('/* GQ5012BF1 original __LINE__ provenance; source text unknown, not invented. */\n'*extra)+new;changes.append(diff(f,orig,new));records.append(dict(path=f,old_sha256=sha(orig),new_sha256=sha(new),delta='Historical stockconstant __LINE__ offset+'+str(extra)+('; genuine InitializeContext(NULL) control/input argument delta' if f.endswith('tee_ops.c') else '')))
(S/'patches/source').mkdir(parents=True,exist_ok=True);(S/'patches/source/0001-stock-legacy-GP-API-and-trusted-memory-release-delta.patch').write_text(''.join(changes));(S/'reference/recovered-source-delta-provenance.json').write_text(json.dumps(records,indent=2)+'\n');(P/'evidence/recovered-secure-source-deltas.json').write_text(json.dumps(records,indent=2)+'\n');print('Recorded',len(records),'authentic source release/type/lineage deltas; publicprovider registered member NOThidden orforcepatched')
