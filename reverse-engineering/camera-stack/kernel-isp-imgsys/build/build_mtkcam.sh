#!/bin/bash
# build the whole mtkcam ext-module tree like the MTK mixed build
. /tmp/ispenv.sh
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
SENS="imx989_mipi_raw imx989cts_mipi_raw s5kgm2sp_mipi_raw s5kgn1sp_mipi_raw ov32b40_mipi_raw s5kjn1_mipi_raw s5kjn1cts_mipi_raw s5kjn1main2_mipi_raw ov64b_mipi_raw"
cd $G/common
make O=$KO M=../vendor/mediatek/kernel_modules/mtkcam ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  'DEVICE_MODULES_PATH=$(srctree)/$(DEVICE_MODULES_REL_DIR)' 'DEVCIE_MODULES_INCLUDE=-I$(DEVICE_MODULES_PATH)/include' \
  KBUILD_MODPOST_WARN=1 module_scmversion= KCFLAGS="-faddrsig" \
  CONFIG_MTK_IMGSENSOR_PROJECT=k6878v1_64 CONFIG_CUSTOM_KERNEL_IMGSENSOR="$SENS" \
  KBUILD_EXTRA_SYMBOLS=$G/lieppos/camera-isp/stock-ext.symvers -j16 "$@" modules
