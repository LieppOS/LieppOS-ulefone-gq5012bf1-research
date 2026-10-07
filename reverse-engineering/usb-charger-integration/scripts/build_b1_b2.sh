#!/bin/bash
# GQ5012BF1 charger/PD policy modules (MODS=list of drivers/<dir>/<mod>): two clean builds (B1, B2) from the
# workspace KDM tree ($G/kernel_device_modules-6.1, commits 9f4d03b/6863ff1/6d18b45 on
# pristine ALPS e38092245fb4 / 5e415e059253 bases) against the vendor-config out-tree
# $G/lieppos/camera-isp/kout (kernel.release 6.1.115-android14-11-g945dff7bc1bf).
# Modules: mt6375 (MFD core), mt6375-adc, mt6375-auxadc, mt6375-charger, mt6375-battery.
# Provider CRCs: KBUILD_EXTRA_SYMBOLS = lieppos/camera-isp/stock-ext.symvers (stock-harvested,
# same convention as the DONE power-charging pass); our own modules export only yft_usb_flag.
set -euo pipefail
MODS="power/supply/charger_class power/supply/mtk_chg_type_det power/supply/mtk_charger_framework"; OUT=${OUT:-/home/armol/kernel-work/gki-12901745-workspace/lieppos/usb-charger-b1b2}
G=${G:-/home/armol/kernel-work/gki-12901745-workspace}
KO=$G/lieppos/camera-isp/kout; OUTDM=$KO/../kernel_device_modules-6.1
OUT=${OUT:?set OUT}
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
[ "$(cat $KO/include/config/kernel.release)" = 6.1.115-android14-11-g945dff7bc1bf ]
git -C $G/kernel_device_modules-6.1 diff --quiet HEAD -- drivers/mfd drivers/iio/adc drivers/power/supply include || { echo "KDM tree dirty" >&2; exit 1; }
git -C $G/kernel_device_modules-6.1 log --oneline -1
OFF="CONFIG_DEVICE_MODULES_CHARGER_MT6360= CONFIG_BATTERY_MT6359P= CONFIG_MTK_HVBP_SUPPORT= CONFIG_MTK_PUMP_EXPRESS_PLUS_20_SUPPORT= CONFIG_MTK_PUMP_EXPRESS_45_SUPPORT= CONFIG_MTK_PUMP_EXPRESS_50_PLUS_SUPPORT= CONFIG_CHARGER_RT9759= CONFIG_CHARGER_RT9490= CONFIG_CHARGER_RT9758= CONFIG_CHARGER_SC8541= CONFIG_CHARGER_UPM6720= CONFIG_CHARGER_NT= CONFIG_NT_USB_TS= CONFIG_GAUGE_BQ28Z610= CONFIG_CHARGER_MT6985_ALPHA_SUPPORT="

for b in B1 B2; do
  for d in mfd iio/adc power/supply; do find $OUTDM/drivers/$d -maxdepth 1 \( -name '*.o' -o -name '*.ko' -o -name '*.mod*' -o -name '.*.cmd' \) -delete 2>/dev/null || true; done
  (cd $G/common && make O=$KO M=../kernel_device_modules-6.1 ARCH=arm64 LLVM=1 LLVM_IAS=1 \
    KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
    'DEVICE_MODULES_PATH=$(srctree)/$(DEVICE_MODULES_REL_DIR)' 'DEVCIE_MODULES_INCLUDE=-I$(DEVICE_MODULES_PATH)/include' \
    KBUILD_MODPOST_WARN=1 module_scmversion= KCFLAGS="-faddrsig" LIEPPOS_ONLY="drivers/mfd/ drivers/iio/adc/ drivers/power/supply/" \
    $OFF KBUILD_EXTRA_SYMBOLS=$G/lieppos/camera-isp/stock-ext.symvers -j16 -k modules) > $OUT.$b.log 2>&1 || true
  mkdir -p $OUT/$b
  for m in $MODS; do n=$(basename $m)
    cp $OUTDM/drivers/$m.ko $OUT/$b/$n.ko
    llvm-strip --strip-debug -o $OUT/$b/$n.stripped.ko $OUT/$b/$n.ko
  done
  (cd $OUT/$b && sha256sum *.stripped.ko)
done
for f in $(cd $OUT/B1 && ls *.ko); do cmp -s $OUT/B1/$f $OUT/B2/$f && echo "B1 == B2 ($f)" || { echo "B1 != B2 ($f)"; exit 1; }; done
