#!/bin/bash
# build_ext.sh <module dir relative to connectivity/ e.g. conninfra> [make vars...] -- build an out-of-tree MTK kernel_modules dir against the GKI+KDM config
. /tmp/connenv.sh
M=../vendor/mediatek/kernel_modules/connectivity/$1
# modpost re-includes $M/Kbuild relative to the objtree; mirror it for leaf dirs that only carry Kbuild
mkdir -p $CO/$1; [ -e $CS/$1/Kbuild ] && [ ! -e $CS/$1/Makefile ] && ln -sf $CS/$1/Kbuild $CO/$1/Kbuild
shift
EXTRA=${CONN_EXTRA:-$G/lieppos/camera-isp/stock-ext.symvers}
cd $G/common
make O=$KOA M=$M ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  DEVICE_MODULES_PATH=$G/kernel_device_modules-6.1 DEVCIE_MODULES_INCLUDE=-I$G/kernel_device_modules-6.1/include \
  KERNEL_SRC=$G/common TARGET_BUILD_VARIANT=${TBV-} \
  KBUILD_MODPOST_WARN=1 module_scmversion= KCFLAGS="-faddrsig" \
  KBUILD_EXTRA_SYMBOLS="$EXTRA" -j16 "$@" modules
