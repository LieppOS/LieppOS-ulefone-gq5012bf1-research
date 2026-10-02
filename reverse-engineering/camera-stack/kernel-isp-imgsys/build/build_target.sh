#!/bin/bash
# build_target.sh <pkg-subdir under mtkcam> [dep-subdir ...]
# Emulates one kleaf define_mgk_ko target: own M=, extra symbols = device-modules
# (here: stock-derived symvers) + Module.symvers of declared deps.
. /tmp/ispenv.sh
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
T=$1; shift
OUTMC=$KO/../vendor/mediatek/kernel_modules/mtkcam
EXTRA=$G/lieppos/camera-isp/stock-ext.symvers
for d in "$@"; do EXTRA="$EXTRA $OUTMC/$d/Module.symvers"; done
SENS="imx989_mipi_raw imx989cts_mipi_raw s5kgm2sp_mipi_raw s5kgn1sp_mipi_raw ov32b40_mipi_raw s5kjn1_mipi_raw s5kjn1cts_mipi_raw s5kjn1main2_mipi_raw ov64b_mipi_raw"
cd $G/common
make O=$KO M=../vendor/mediatek/kernel_modules/mtkcam/$T ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  'DEVICE_MODULES_PATH=$(srctree)/$(DEVICE_MODULES_REL_DIR)' 'DEVCIE_MODULES_INCLUDE=-I$(DEVICE_MODULES_PATH)/include' \
  KBUILD_MODPOST_WARN=1 module_scmversion= KCFLAGS="-faddrsig" \
  CONFIG_MTK_IMGSENSOR_PROJECT=k6878v1_64 CONFIG_CUSTOM_KERNEL_IMGSENSOR="$SENS" \
  KBUILD_EXTRA_SYMBOLS="$EXTRA" -j16 modules
