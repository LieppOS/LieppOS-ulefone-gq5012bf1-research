#!/bin/bash
# Natural provider build of the public TrustKernel tkcore core/ (tkcore.ko),
# pristine donor (kernel_device_modules-6.1 commit ff29054 = anvil-kernel
# 8e1a0f39478f, tree 6b94428f), exact GKI 12901745, clang r487747c,
# stock config TEE_SUPPORT=m, RPMB=y, FP_SUPPORT=y. Output: Module.symvers.
set -e
# The donor tree is materialised once with:
#   git -C $G/kernel_device_modules-6.1 archive ff29054 drivers/tee/tkcore | tar -x -C $TKW
#   (mv drivers/tee/tkcore src; srcroot/drivers/tee/tkcore -> src); hashes: ../evidence/tkcore-core-donor-files.sha256
G=${G:-/home/armol/kernel-work/gki-12901745-workspace}
HERE=${TKW:-/home/armol/kernel-work/gki-12901745-workspace/lieppos/tkcore-core-natural}
KO=${KO:-$G/lieppos/nfc/kout}
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
REL=$(realpath --relative-to=$G/common "$HERE/src/core")
[ -f "$HERE/src/core/Makefile" ] || { echo "missing donor tree $HERE/src" >&2; exit 1; }
cd $G/common
make O=$KO M=$REL ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  TKCORE_ROOT_OVERRIDE= DEVICE_MODULES_PATH="$HERE/srcroot" \
  CONFIG_TRUSTKERNEL_TEE_SUPPORT=m CONFIG_TRUSTKERNEL_TEE_RPMB_SUPPORT=y CONFIG_TRUSTKERNEL_TEE_FP_SUPPORT=y \
  module_scmversion= KCFLAGS="-faddrsig -DCONFIG_TRUSTKERNEL_TEE_FP_SUPPORT=1" -j16 modules
