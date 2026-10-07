#!/bin/bash
# Build the binary-equivalent sh366003_fg.ko against GKI 12901745 (android14-6.1).
# Needs: $G (gki-12901745-workspace), the private sinofs_afi_data.inc next to the
# source (kernel/phase4-sh366003-recon/sinofs_afi_data.inc, sha256 c4c297b3...).
set -e
G=${G:-/home/armol/kernel-work/gki-12901745-workspace}
HERE=$(cd "$(dirname "$0")/.." && pwd)
SRC=$G/kernel_device_modules-6.1/drivers/power/supply/sh366003
KO=${KO:-$G/lieppos/nfc/kout}
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
python3 "$HERE/scripts/pad_lines.py" "$HERE/source/sh366003_fg.src.c" "$SRC/sh366003_fg.c"
cmp "$SRC/sh366003_fg.c" "$HERE/source/sh366003_fg.c"
cp "$HERE/source/Makefile" "$SRC/Makefile"
cd $G/common && make O=$KO M=../kernel_device_modules-6.1/drivers/power/supply/sh366003 ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  'DEVICE_MODULES_PATH=$(srctree)/$(DEVICE_MODULES_REL_DIR)' 'DEVCIE_MODULES_INCLUDE=-I$(DEVICE_MODULES_PATH)/include' \
  module_scmversion= KCFLAGS="-faddrsig" KBUILD_EXTRA_SYMBOLS="$HERE/source/stock-yft-devinfo.symvers" -j16 modules
# compare: llvm-strip --strip-debug, then reverse-engineering/scripts/ko-pair-parity.py stock B
