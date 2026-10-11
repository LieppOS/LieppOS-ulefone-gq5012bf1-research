#!/bin/bash
# try-accdet.sh <variant.c> : rebuild only mt6369-accdet in the Codex dev tree and report residue.
set -euo pipefail
WS=/home/armol/kernel-work/codex-audio-batch-01/dev
REC='/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_audio_ulefone_gq5012bf1'
T=$WS/src/kdm; export PATH=$WS/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
export KBUILD_BUILD_USER=lieppos KBUILD_BUILD_HOST=audio-build KBUILD_BUILD_VERSION=1 KBUILD_BUILD_TIMESTAMP='Thu Oct 8 12:00:00 UTC 2026'
cp "$1" $T/sound/soc/codecs/mt6369-accdet.c
COMMON=$WS/common KO=$WS/kout KDM_DIR=$T bash "$REC/scripts/kb.sh" -j16 KBUILD_EXTRA_SYMBOLS=$WS/out/D1/provider/natural-external-provider.symvers modules > /tmp/codex-audio-scratch/try.log 2>&1 || { grep -m5 error /tmp/codex-audio-scratch/try.log; exit 1; }
O=/tmp/codex-audio-scratch/tryout; mkdir -p $O
llvm-strip --strip-debug -o $O/mt6369-accdet.stripped $T/sound/soc/codecs/mt6369-accdet.ko
cd "$REC" && PYTHONDONTWRITEBYTECODE=1 python3 scripts/ko-pair-parity.py /home/armol/kernel-work/codex-audio-batch-01/stock/mt6369-accdet.ko $O/mt6369-accdet.stripped | grep -E 'byte-exact|byte-identical|ONE-SIDED|semantic deltas|differs \(' | head
cmp -l /home/armol/kernel-work/codex-audio-batch-01/stock/mt6369-accdet.ko $O/mt6369-accdet.stripped | wc -l
python3 - <<'PY'
import sys,importlib.util,difflib
R='/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_audio_ulefone_gq5012bf1/scripts/'
sys.path.insert(0,R);sys.dont_write_bytecode=True
sp=importlib.util.spec_from_file_location('kpp',R+'ko-pair-parity.py');kpp=importlib.util.module_from_spec(sp);sp.loader.exec_module(kpp)
A=kpp.KO('/home/armol/kernel-work/codex-audio-batch-01/stock/mt6369-accdet.ko');B=kpp.KO('/tmp/codex-audio-scratch/tryout/mt6369-accdet.stripped')
def lay(k):
  i=k.secs.index(k.sec('.bss'));return sorted((y['val'],y['n']) for y in k.syms if y['shndx']==i and y['info']&15==1)
print('bss A',lay(A)[:5]);print('bss B',lay(B)[:5])
sa=[x.decode(errors='replace') for x in A.data('.rodata.str1.1').split(b'\0')];sb=[x.decode(errors='replace') for x in B.data('.rodata.str1.1').split(b'\0')]
print('\n'.join(l[:100] for l in difflib.unified_diff(sa,sb,lineterm='',n=0) if l[:1] in '+-' and l[:3] not in('+++','---')))
PY
