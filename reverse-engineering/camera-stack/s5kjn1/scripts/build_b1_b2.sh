#!/usr/bin/env bash
# Two clean builds (B1, B2) of the reconstructed imgsensor.ko (STOCK-PARITY
# mode) via ../../reconstruction/imgsensor/build/build.sh. Offline, host-only.
# Each build starts from a tree with every kbuild product removed.
set -euo pipefail
G=${G:-/home/armol/kernel-work/gki-12901745-workspace}
W=${W:-$G/lieppos/camera-imgsensor}
KOUT=${KOUT:-$W/kout}
KDM=${KDM:-$W/tree/kernel_device_modules}
OUT=${OUT:-$G/lieppos/s5kjn1-b1b2}
HERE=$(cd "$(dirname "$0")" && pwd)
BUILD="$HERE/../../reconstruction/imgsensor/build/build.sh"
DST=$G/vendor/mediatek/kernel_modules/mtkcam/imgsensor/src-v4l2
clean() {
  [ -d "$DST" ] || return 0
  find "$DST" \( -name '*.o' -o -name '*.ko' -o -name '*.mod' -o -name '*.mod.c' \
     -o -name '.*.cmd' -o -name 'modules.order' -o -name 'Module.symvers' \
     -o -name '*.usyms' -o -name '*.a' \) -delete
}
for b in B1 B2; do
  clean
  rm -rf "$OUT/$b"; mkdir -p "$OUT/$b"
  bash "$BUILD" "$G" "$KOUT" "$KDM" parity > "$OUT/$b/build.log" 2>&1
  cp "$DST/imgsensor.ko" "$OUT/$b/imgsensor.ko"
  cp "$DST/imgsensor.parity.stripped.ko" "$OUT/$b/imgsensor.parity.stripped.ko"
  cp "$DST/common/s5kjn1_mipi_raw/s5kjn1mipiraw_Sensor.o" "$DST/common/s5kjn1cts_mipi_raw/s5kjn1ctsmipiraw_Sensor.o" "$DST/common/ov32b40_mipi_raw/ov32b40mipiraw_Sensor.o" "$DST/adaptor-ctrls.o" "$DST/imgsensor.mod" "$OUT/$b/"
  (cd "$OUT/$b" && sha256sum imgsensor.ko imgsensor.parity.stripped.ko s5kjn1mipiraw_Sensor.o s5kjn1ctsmipiraw_Sensor.o ov32b40mipiraw_Sensor.o)
done
for f in imgsensor.ko imgsensor.parity.stripped.ko s5kjn1mipiraw_Sensor.o s5kjn1ctsmipiraw_Sensor.o ov32b40mipiraw_Sensor.o; do
  cmp "$OUT/B1/$f" "$OUT/B2/$f" && echo "B1 == B2 ($f byte-identical)"
done
