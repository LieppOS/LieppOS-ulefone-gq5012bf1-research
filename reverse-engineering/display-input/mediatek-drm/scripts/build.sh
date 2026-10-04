#!/bin/bash
# usage: build.sh <kdm-root> [module=mediatek-drm] [subdir=drivers/gpu/drm/mediatek/mediatek_v2]
# Isolated M= build of a KDM module from an arbitrary KDM snapshot, stock-like flags:
#   CONFIG_LTO_NONE kout, KCFLAGS=-faddrsig, __FILE__ -> ../kernel_device_modules-6.1/
set -e
G=/home/armol/kernel-work/gki-12901745-workspace
R=$(readlink -f "$1"); MOD=${2:-mediatek-drm}; SUB=${3:-drivers/gpu/drm/mediatek/mediatek_v2}
M=$R/$SUB
cat > $M/Kbuild <<EOF
LINUXINCLUDE := -I$R/include \$(LINUXINCLUDE)
subdir-ccflags-y += -Werror -I$R/include -I$R/include/uapi
include \$(src)/Makefile
obj-y :=
obj-m := $MOD.o
KBUILD_EXTRA_SYMBOLS += $G/lieppos/glue/stock-all.symvers
EOF
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
cd $G/common
make O=$G/lieppos/nfc/kout M=$M ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_PATH=$R DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  module_scmversion= -j${J:-16} "KCFLAGS=-faddrsig -fmacro-prefix-map=$R/=../kernel_device_modules-6.1/ ${XKCFLAGS}" modules > $M/build.log 2>&1 || { grep -E 'error|Error' $M/build.log | head -20; exit 1; }
llvm-strip --strip-debug -o $M/$MOD.stripped.ko $M/$MOD.ko
ls -l $M/$MOD.stripped.ko
