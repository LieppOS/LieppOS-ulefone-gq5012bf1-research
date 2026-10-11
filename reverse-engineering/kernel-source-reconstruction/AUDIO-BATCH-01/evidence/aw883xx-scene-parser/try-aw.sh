#!/bin/bash
# try-aw.sh <variant aw883xx_bin_parse.c>
set -euo pipefail
WS=/home/armol/kernel-work/codex-audio-batch-01/dev
REC='/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_audio_ulefone_gq5012bf1'
T=$WS/src/kdm; export PATH=$WS/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
export KBUILD_BUILD_USER=lieppos KBUILD_BUILD_HOST=audio-build KBUILD_BUILD_VERSION=1 KBUILD_BUILD_TIMESTAMP='Thu Oct 8 12:00:00 UTC 2026'
cp "$1" $T/sound/soc/codecs/aw883xx/aw883xx_bin_parse.c
COMMON=$WS/common KO=$WS/kout KDM_DIR=$T bash "$REC/scripts/kb.sh" -j16 KBUILD_EXTRA_SYMBOLS=$WS/out/D1/provider/natural-external-provider.symvers modules > /tmp/codex-audio-scratch/tryaw.log 2>&1 || { grep -m5 error /tmp/codex-audio-scratch/tryaw.log; exit 1; }
O=/tmp/codex-audio-scratch/tryaw; mkdir -p $O
llvm-strip --strip-debug -o $O/aw.stripped $T/sound/soc/codecs/aw883xx/aw883xx_driver.ko
cd "$REC" && PYTHONDONTWRITEBYTECODE=1 python3 scripts/ko-pair-parity.py /home/armol/kernel-work/codex-audio-batch-01/stock/aw883xx_driver.ko $O/aw.stripped | grep -E 'byte-exact|FUNCTIONS|FUNC-DIFF|ONE-SIDED|DATA OBJ' | head
{ cmp -l /home/armol/kernel-work/codex-audio-batch-01/stock/aw883xx_driver.ko $O/aw.stripped 2>/dev/null || true; } | wc -l
W=/tmp/codex-audio-scratch/aw-dis
llvm-objdump -d -r --no-show-raw-insn --disassemble-symbols=aw883xx_dev_cfg_load $T/sound/soc/codecs/aw883xx/aw883xx_driver.ko | sed -E 's/^ *[0-9a-f]+:\s*//' | grep -v '^$' | sed -E 's/\+0x[0-9a-f]+$//; s/#0x[0-9a-f]{3,}/#IMM/' | tail -n +2 | grep -v R_AARCH64 | sed -E 's/0x[0-9a-f]+ <aw883xx_dev_cfg_load\+0x[0-9a-f]+>/L/' > $W/T2.s
echo "asm lines stock=$(tail -n +2 $W/A2.s | wc -l) try=$(wc -l < $W/T2.s) diffcount=$(diff <(tail -n +2 $W/A2.s) $W/T2.s | grep -c '^[<>]')"
