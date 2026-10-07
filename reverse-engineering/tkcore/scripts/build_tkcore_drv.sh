#!/bin/bash
# Build the GQ5012BF1 tkcore_drv.ko reconstruction against exact GKI 12901745
# (android14-6.1, clang r487747c).
#
# Prerequisite: $T holds the public TrustKernel tree
#   review.ozobot.com device/ozobot/anvil-kernel @ 6b94428fe0aae736e06693cda13bd284b88e93ed
#   (imported by 8e1a0f39478f "tee: Import TrustKernel driver used by Zinwa Q25"),
#   path drivers/tee/tkcore, verified against ../source/donor-manifest.tsv.
# The research source/ overlay (= donor + patches/0001) is copied on top.
#
# Config of the stock build (proven by the stock binary):
#   CONFIG_TRUSTKERNEL_TEE_SUPPORT=m, CONFIG_TRUSTKERNEL_TEE_RPMB_SUPPORT=y,
#   CONFIG_TRUSTKERNEL_TEE_FP_SUPPORT=y (clkmgr RPC path present).
# Provider CRCs: tkcore edges from the stock tkcore.ko __kcrctab
# (source/stock-tkcore.symvers), FF-A edges from the source-built ffa_v10.
set -e
G=${G:-/home/armol/kernel-work/gki-12901745-workspace}
HERE=$(cd "$(dirname "$0")/.." && pwd)
T=${T:-$G/kernel_device_modules-6.1/drivers/tee/tkcore}
KO=${KO:-$G/lieppos/nfc/kout}
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
for f in "$HERE"/source/armtz/*; do cp "$f" "$T/armtz/"; done
cp "$HERE/source/core/tee_supp_com.h" "$T/core/"
M=../kernel_device_modules-6.1/drivers/tee/tkcore/armtz
# KBUILD_EXTRA_SYMBOLS is space-separated: stage the provider records on a space-free path
SYM=$(mktemp -d); cp "$HERE/source/stock-tkcore.symvers" "$HERE/source/ffa_v10.natural.symvers" "$SYM/"
cd $G/common
[ "$1" = clean ] && make O=$KO M=$M ARCH=arm64 LLVM=1 clean >/dev/null
make O=$KO M=$M ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  'DEVICE_MODULES_PATH=$(srctree)/$(DEVICE_MODULES_REL_DIR)' 'DEVCIE_MODULES_INCLUDE=-I$(DEVICE_MODULES_PATH)/include' \
  CONFIG_TRUSTKERNEL_TEE_SUPPORT=m CONFIG_TRUSTKERNEL_TEE_RPMB_SUPPORT=y \
  module_scmversion= KCFLAGS="-faddrsig -DCONFIG_TRUSTKERNEL_TEE_FP_SUPPORT=1" \
  KBUILD_EXTRA_SYMBOLS="$SYM/stock-tkcore.symvers $SYM/ffa_v10.natural.symvers" -j16 modules
rm -rf "$SYM"
# result: $KO/../kernel_device_modules-6.1/drivers/tee/tkcore/armtz/tkcore_drv.ko
# compare: llvm-strip --strip-debug, then scripts/parity.sh
