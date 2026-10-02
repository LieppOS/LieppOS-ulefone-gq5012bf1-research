#!/bin/bash
# usage: cambuild.sh [sensor list]
. /tmp/camenv.sh
D=$G/vendor/mediatek/kernel_modules/mtkcam/imgsensor/src-v4l2
SENS=${1:-"$(. /tmp/sensors.sh)"}
cd $D
make -C $G/common O=$W/kout M=$G/common/../vendor/mediatek/kernel_modules/mtkcam/imgsensor/src-v4l2 ARCH=arm64 LLVM=1 LLVM_IAS=1 KBUILD_MODPOST_WARN=1 DEVICE_MODULES_PATH=$W/tree/kernel_device_modules CONFIG_MTK_V4L2_IMGSENSOR=m CONFIG_MTK_IMGSENSOR_PROJECT=k6878v1_64 CONFIG_CUSTOM_KERNEL_IMGSENSOR="$SENS" module_scmversion= KCFLAGS="-faddrsig -Wno-error -DCONFIG_MTK_AEE_FEATURE=1 -DCONFIG_MTK_AEE_AED_MODULE=1" KBUILD_EXTRA_SYMBOLS=$W/stock-imgsensor-imports.symvers modules > build.log 2>&1
rc=$?; echo rc=$rc; [ $rc = 0 ] || grep -E "error|Error" build.log | head -30
