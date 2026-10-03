#!/bin/bash
# parity_modem.sh <module> [...]  (REBUILT=<path> overrides search under $KDO)
. /tmp/modemenv.sh
mkdir -p /tmp/mstripped "$MR/binary-analysis/per-module"
for m in "$@"; do
  s=$(find "$VR" "$VD" -name "$m.ko" | head -1)
  r=${REBUILT:-$(find $KDO -name "$m.ko" 2>/dev/null | head -1)}
  [ -z "$r" ] && { echo "$m	NOT-BUILT"; continue; }
  llvm-strip --strip-debug -o /tmp/mstripped/$m.ko "$r"
  python3 "$MR/../power-charging/scripts/abi_parity.py" "$s" /tmp/mstripped/$m.ko --label $m --tsv "$MR/binary-analysis/per-module/$m.abi-parity.tsv" ${ABIV:+-v}
  python3 "$KI/scripts/ko_parity.py" "$s" /tmp/mstripped/$m.ko --label $m \
     --tsv "$MR/binary-analysis/per-module/$m.function-parity.tsv" \
     --data-tsv "$MR/binary-analysis/per-module/$m.data-parity.tsv"
done
