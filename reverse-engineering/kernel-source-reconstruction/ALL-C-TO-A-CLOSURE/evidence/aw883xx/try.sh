#!/bin/bash
# try.sh <variant.c> : rebuild aw883xx in a PRIVATE reflinked KDM copy and diff aw883xx_dev_cfg_load
set -euo pipefail
W=/home/armol/kernel-work/allc/aw/ws; T=$W/src/kdm
REC='/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_audio_ulefone_gq5012bf1'
export PATH=$W/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
export KBUILD_BUILD_USER=lieppos KBUILD_BUILD_HOST=audio-build KBUILD_BUILD_VERSION=1 KBUILD_BUILD_TIMESTAMP='Thu Oct 8 12:00:00 UTC 2026'
cp "$1" $T/sound/soc/codecs/aw883xx/aw883xx_bin_parse.c
COMMON=$W/common KO=$W/kout KDM_DIR=$T nice -n 19 bash "$REC/scripts/kb.sh" -j16 KBUILD_EXTRA_SYMBOLS=$W/out/D1/provider/natural-external-provider.symvers sound/soc/codecs/aw883xx/aw883xx_driver.ko > try.log 2>&1 || { grep -m5 error try.log; exit 1; }
llvm-strip --strip-debug -o try.stripped $T/sound/soc/codecs/aw883xx/aw883xx_driver.ko
norm() { llvm-objdump -d -r --no-show-raw-insn --disassemble-symbols=aw883xx_dev_cfg_load $1 | sed -E 's/^ *([0-9a-f]+):\s*/\1 /' | grep -v '^$' | tail -n +4 | sed -E 's/^[0-9a-f]+ //; s/<aw883xx_dev_cfg_load\+0x[0-9a-f]+>/<L>/; s/0x[0-9a-f]+ <L>/L/; s/R_AARCH64_([A-Z0-9_]+)\s+.*/R_\1/; s/bl\s+0x[0-9a-f]+ </bl </'; }
norm try.stripped > t.s; norm stock.ko > s.s
echo "$(basename $1): size stock=$(stat -c%s stock.ko) try=$(stat -c%s try.stripped) lines stock=$(wc -l < s.s) try=$(wc -l < t.s) diff=$(diff s.s t.s | grep -c '^[<>]' || true) whole-file-diff-bytes=$(cmp -l stock.ko try.stripped 2>/dev/null | wc -l)"
