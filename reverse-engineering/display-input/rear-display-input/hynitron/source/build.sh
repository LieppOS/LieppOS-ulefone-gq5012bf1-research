#!/bin/bash
# Offline exact-parity build against the CI-12901745 GKI kernel tree.
set -euo pipefail
: "${GKI_ROOT:?set GKI_ROOT to the gki-12901745-workspace root}"
: "${KOUT:?set KOUT to a configured CONFIG_LTO_NONE GKI output directory}"
D="$(cd "$(dirname "$0")" && pwd)"
case "$D" in *" "*) echo "Kbuild M= paths cannot contain spaces; copy source/ to a no-space build path" >&2; exit 1;; esac
[ -s "$D/firmware/capacitive_hynitron_cst8xx_update.h" ] || {
  echo "private firmware headers absent; run ./extract-firmware.py STOCK_HYNITRON.KO" >&2
  exit 1
}
export PATH="$GKI_ROOT/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH"
cd "$GKI_ROOT/common"
make O="$KOUT" M="$D" ARCH=arm64 LLVM=1 LLVM_IAS=1 KCFLAGS=-faddrsig \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ \
  DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  'DEVICE_MODULES_PATH=$(srctree)/$(DEVICE_MODULES_REL_DIR)' \
  module_scmversion= -j"$(nproc)" modules > "$D/build.log" 2>&1
llvm-strip --strip-debug -o "$D/hynitron.stripped.ko" "$D/hynitron.ko"
echo "built $D/hynitron.stripped.ko"
