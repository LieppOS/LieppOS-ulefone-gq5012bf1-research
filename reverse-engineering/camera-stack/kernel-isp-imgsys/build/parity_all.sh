#!/bin/bash
. /tmp/ispenv.sh
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
OUTMC=$KO/../vendor/mediatek/kernel_modules/mtkcam
OUTDM=$KO/../kernel_device_modules-6.1
mkdir -p /tmp/stripped "$KI/binary-analysis/per-module"
for m in "$@"; do
  s=$(find "$VD" "$VR" -name "$m.ko" | head -1)
  r=$(find $OUTMC $OUTDM -name "$m.ko" 2>/dev/null | head -1)
  [ -z "$r" ] && { echo "$m	NOT-BUILT"; continue; }
  llvm-strip --strip-debug -o /tmp/stripped/$m.ko "$r"
  python3 "$KI/scripts/ko_parity.py" "$s" /tmp/stripped/$m.ko --label $m \
     --tsv "$KI/binary-analysis/per-module/$m.function-parity.tsv" \
     --data-tsv "$KI/binary-analysis/per-module/$m.data-parity.tsv"
done
