#!/bin/bash
# build.sh <tag>: isolated M= build of yft_tiny2c_usb.ko from $W/src; stripped copy -> par/yft_tiny2c_usb-<tag>.ko
set -e
G=/home/armol/kernel-work/gki-12901745-workspace; W=$G/lieppos/thermal-fm78100; TAG=${1:-B1}
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
cd $W/src; rm -f *.o *.ko *.mod* .*.cmd modules.order Module.symvers
cd $G/common
make O=$G/lieppos/camera-isp/kout M=$W/src ARCH=arm64 LLVM=1 LLVM_IAS=1 module_scmversion= \
  KCFLAGS="-faddrsig ${XKCFLAGS}" KBUILD_EXTRA_SYMBOLS=$W/provider.symvers -j8 modules > $W/build-$TAG.log 2>&1 || { grep -E 'error|warning' $W/build-$TAG.log | head; exit 1; }
grep -E 'warning' $W/build-$TAG.log | head -5 || true
llvm-strip --strip-debug -o $W/par/yft_tiny2c_usb-$TAG.ko $W/src/yft_tiny2c_usb.ko
cp $W/src/yft_tiny2c_usb.ko $W/par/yft_tiny2c_usb-$TAG.unstripped.ko
sha256sum $W/par/yft_tiny2c_usb-$TAG.ko
