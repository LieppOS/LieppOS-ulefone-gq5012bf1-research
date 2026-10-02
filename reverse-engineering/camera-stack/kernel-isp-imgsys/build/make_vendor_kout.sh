#!/bin/bash
# Recreate the vendor (mixed-build) kernel output used for all camera modules.
# Inputs: GKI 12901745 common/ (= stock IKCONFIG, verified identical) and
# NothingOSS kernel_device_modules-6.1 (957dac1, pristine git archive) at $G/kernel_device_modules-6.1.
# MTK kleaf user build: gki_defconfig + mgk_64_k61_defconfig with KCONFIG_EXT_PREFIX.
set -e
G=$1; KO=$2
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
cd $G/common
cat arch/arm64/configs/gki_defconfig ../kernel_device_modules-6.1/arch/arm64/configs/mgk_64_k61_defconfig > arch/arm64/configs/zz_lieppos_vendor_defconfig
make O=$KO ARCH=arm64 LLVM=1 LLVM_IAS=1 KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ zz_lieppos_vendor_defconfig
rm -f arch/arm64/configs/zz_lieppos_vendor_defconfig
# host libbpf of this tree does not build with the host clang: reuse a prepared tools/ dir if given
[ -n "$3" ] && rsync -a "$3/tools/" $KO/tools/ && find $KO/tools -type f -exec touch {} +
make O=$KO ARCH=arm64 LLVM=1 LLVM_IAS=1 KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ -j16 modules_prepare
REL=6.1.115-android14-11-g945dff7bc1bf
echo "#define UTS_RELEASE \"$REL\"" > $KO/include/generated/utsrelease.h
echo $REL > $KO/include/config/kernel.release
