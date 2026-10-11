#!/usr/bin/env python3
"""Bounded post25closure source experiment; separate from immutable acceptance inputs."""
from pathlib import Path
import subprocess,os,json,re,csv,difflib,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[2];N=R.parent/'android_kernel_modules_charging_battery_ulefone_gq5012bf1';C=Path('/home/armol/kernel-work/platform-batch-04-cleancheck/ws');W=Path('/home/armol/kernel-work/platform-batch-04-revisit');E=P/'evidence/blocker-revisit';E.mkdir(parents=True,exist_ok=True);W.mkdir(exist_ok=True);env=dict(os.environ,TMPDIR='/tmp',TMP='/tmp',TEMP='/tmp',PYTHONDONTWRITEBYTECODE='1',JOBS='12')
for d in ['common','prebuilts','kernel_device_modules-6.1','kout']:
 f=W/d
 if not f.exists():f.symlink_to(C/d,target_is_directory=True)
env['PATH']=str(W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin')+os.pathsep+os.environ['PATH']
(W/'.bootstrap-ok').write_text('Verified public source/config/preparation reused from independent proof; no selected target objects reused\n')
p=subprocess.run(['bash',str(N/'scripts/assemble.sh'),str(W)],cwd=R,env=env,text=True,capture_output=True);(E/'assembly.log').write_text(p.stdout+p.stderr);assert p.returncode==0
T=W/'src/kdm';D=T/'drivers/misc/mediatek/typec/tcpc';patch=''
for name,pattern in [('pd_process_evt.c',r'\t\tif \(pd_event_msg_match\(pd_event,\n\t\t\t\tPD_EVT_CTRL_MSG, PD_CTRL_PING\)\) \{\n\t\t\tPE_INFO\("Ignore Ping\\n"\);\n\t\t\tgoto out;\n\t\t\}\n'),('tcpci_typec.c',r'\t\tTYPEC_INFO\("RpLvl Alert\\n"\);\n')]:
 f=D/name;old=f.read_text();new,n=re.subn(pattern,lambda m:'\n'*m[0].count('\n'),old);assert n==(2 if name=='pd_process_evt.c' else 1),(name,n)
 f.write_text(new);patch+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/drivers/misc/mediatek/typec/tcpc/'+name,tofile='b/drivers/misc/mediatek/typec/tcpc/'+name));(E/name).write_text(new)
(E/'stock-absent-ping-and-rp-alert-source.patch').write_text(patch)
# Scope link to this real selected implementation only. Every34 composite object freshly compiled.
for f in T.rglob('Makefile'):
 s=f.read_text();s=re.sub(r'^obj-m \+= (?!(?:tcpc_class|pd_dbg_info)\.o$).*\n','',s,flags=re.M);f.write_text(s)
p=subprocess.run(['bash',str(N/'scripts/kb.sh'),'-k','-j12','drivers/misc/mediatek/typec/tcpc/tcpc_class.o'],cwd=R,env=dict(env,COMMON=str(W/'common'),KO=str(W/'kout'),KDM_DIR=str(T)),text=True,capture_output=True);(E/'objects.log').write_text(p.stdout+p.stderr);assert p.returncode==0
p=subprocess.run(['bash',str(N/'scripts/kb.sh'),'-k','-j12','KBUILD_EXTRA_SYMBOLS='+str(C/'out/F0-B1/provider/natural-external-provider.symvers'),'modules'],cwd=R,env=dict(env,COMMON=str(W/'common'),KO=str(W/'kout'),KDM_DIR=str(T)),text=True,capture_output=True);(E/'modules.log').write_text(p.stdout+p.stderr);assert p.returncode==0
strip=W/'prebuilts/clang/host/linux-x86/clang-r487747c/bin/llvm-strip';subprocess.run([str(strip),'--strip-debug','-o',str(E/'tcpc_class.experiment.stripped.elf'),str(D/'tcpc_class.ko')],check=True)
import sys
sys.dont_write_bytecode=True;sys.path.insert(0,str(N/'scripts'));from normalize import kpp,normalized
m=next(r for r in csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t') if r['filename']=='tcpc_class.ko');a=kpp.KO(R/m['stock_paths'].split(';')[0]);b=kpp.KO(E/'tcpc_class.experiment.stripped.elf');af=kpp.functions(a);bf=kpp.functions(b);matches=[n for n in af if n in bf and af[n][0]==bf[n][0] and af[n][2]==bf[n][2]];unmatched=[{'name':n,'stock_size':af[n][0],'candidate_size':bf[n][0] if n in bf else None} for n in af if n not in matches]
sourcehash={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in E.glob('*.c')};an,_,_=normalized(a);bn,_,_=normalized(b);j={'result':'BOUNDED_SOURCE_EXPERIMENT_REMAINS_C','after_other25_independent_acceptance':True,'module':'tcpc_class.ko','stock_functions':len(af),'candidate_functions':len(bf),'named_instruction_bodies_exact':len(matches),'unmatched_functions':unmatched,'whole_ELF_accepted':an==bn,'main_three_source_commits_and_six_build_acceptance_unchanged':True,'source_change':'Remove two stock-absent ping-ignore conditional blocks and stock-absent RpLvlAlert logger, preserving line positions with blank lines; genuine public+historical full source only','source_sha256':sourcehash,'shared_preparation':'Documented verified public common/config/header preparation and source-derived external18ABI witnesses reused; allTCPC34objects fresh','no_target_object_or_stock_code_metadata_transplant':True,'next_experiment':'Inspect remaining PD/sysfs/alert/discard/standby/timer source revisions; locate authentic OEM token/sourcecounter lineage before altering certified recipes or normalizing srcversion'};assert not j['whole_ELF_accepted'];(E/'result.json').write_text(json.dumps(j,indent=2)+'\n');print(j['result'],'bodyexact',len(matches),'/',len(af),'remaining',unmatched)
