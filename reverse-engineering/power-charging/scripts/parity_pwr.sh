#!/bin/bash
. /tmp/ispenv.sh
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
PR="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/power-charging"
OUTDM=$KO/../kernel_device_modules-6.1
mkdir -p /tmp/stripped "$PR/binary-analysis/per-module"
for m in "$@"; do
  s=$(find "$VR" "$VD" -name "$m.ko" | head -1)
  r=${REBUILT:-$(find $OUTDM -name "$m.ko" 2>/dev/null | head -1)}
  [ -z "$r" ] && { echo "$m	NOT-BUILT"; continue; }
  llvm-strip --strip-debug -o /tmp/stripped/$m.ko "$r"
  python3 "$PR/scripts/abi_parity.py" "$s" /tmp/stripped/$m.ko --label $m --tsv "$PR/binary-analysis/per-module/$m.abi-parity.tsv" ${ABIV:+-v}
  python3 "$KI/scripts/ko_parity.py" "$s" /tmp/stripped/$m.ko --label $m \
     --tsv "$PR/binary-analysis/per-module/$m.function-parity.tsv" \
     --data-tsv "$PR/binary-analysis/per-module/$m.data-parity.tsv"
done
