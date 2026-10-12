#!/bin/bash
# build.sh <tag>: isolated build of camera_eeprom_v4l2.ko from $W/trees/mtkcam (only cam_cal/ subtree), stripped copy -> par/camera_eeprom_v4l2-<tag>.ko
set -e
G=/home/armol/kernel-work/gki-12901745-workspace; W=$G/lieppos/eeprom; T=$W/trees/mtkcam; TAG=${1:-B1}
# root Kbuild: identical include/flag prologue to mtkcam/Kbuild, but only descend into cam_cal/
cd $T; git show HEAD:Kbuild | sed -n '1,/^subdir-ccflags-y/p' > Kbuild; echo 'obj-m += cam_cal/' >> Kbuild
git clean -qfdx cam_cal
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
cd $G/common
make O=$G/lieppos/camera-isp/kout M=$T ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  'DEVICE_MODULES_PATH=$(srctree)/$(DEVICE_MODULES_REL_DIR)' 'DEVCIE_MODULES_INCLUDE=-I$(DEVICE_MODULES_PATH)/include' \
  KBUILD_MODPOST_WARN=1 module_scmversion= KCFLAGS="-faddrsig" \
  CONFIG_MTK_IMGSENSOR_PROJECT=k6878v1_64 \
  KBUILD_EXTRA_SYMBOLS=$G/lieppos/camera-isp/stock-ext.symvers -j16 modules > $W/build-$TAG.log 2>&1 || { grep -E 'error' $W/build-$TAG.log | head; exit 1; }
M=$T/cam_cal/src_v4l2/custom/camera_eeprom_v4l2.ko
llvm-strip --strip-debug -o $W/par/camera_eeprom_v4l2-$TAG.ko $M
cp $M $W/par/camera_eeprom_v4l2-$TAG.unstripped.ko
sha256sum $W/par/camera_eeprom_v4l2-$TAG.ko
