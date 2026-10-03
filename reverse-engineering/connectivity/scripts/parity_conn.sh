#!/bin/bash
# parity_conn.sh <module> [...]  (REBUILT=<path> overrides search under $CS and KDM out)
. /tmp/connenv.sh
mkdir -p /tmp/stripped "$CR/binary-analysis/per-module"
for m in "$@"; do
  s=$(find "$VR" "$VD" -name "$m.ko" | head -1)
  r=${REBUILT:-$(find $CO $G/lieppos/audio/kernel_device_modules-6.1 -name "$m.ko" 2>/dev/null | head -1)}
  [ -z "$r" ] && { echo "$m	NOT-BUILT"; continue; }
  llvm-strip --strip-debug -o /tmp/stripped/$m.ko "$r"
  python3 "$CR/../power-charging/scripts/abi_parity.py" "$s" /tmp/stripped/$m.ko --label $m --tsv "$CR/binary-analysis/per-module/$m.abi-parity.tsv" ${ABIV:+-v}
  python3 "$KI/scripts/ko_parity.py" "$s" /tmp/stripped/$m.ko --label $m \
     --tsv "$CR/binary-analysis/per-module/$m.function-parity.tsv" \
     --data-tsv "$CR/binary-analysis/per-module/$m.data-parity.tsv"
done
