#!/usr/bin/env bash
# Reproduce the camera donor builds used by the camera-stack analysis.
# Offline, host-only. Nothing is installed or sent to a device.
#
#   GKI   = exact GKI ab/12901745 kleaf workspace (modules_prepare tarball + vmlinux.symvers)
#   NOTH  = kernel-research/nothing-mt6878 (NothingOSS MT6878 kernel_modules + device_modules)
#
# Produces under $OUT:
#   layout/probe.o                 DWARF struct-layout probe (pahole) for subdrv/adaptor structs
#   donor-subdrv/*.o               imx989 / imx989lite / ov64b donor sub-driver objects (oracle input)
#   donor-dw9781c/dw9781c.ko       Nothing dw9781c.c built unmodified (stock parity: 19/19 byte-identical)
#   imgsensor-build/imgsensor.ko   Nothing src-v4l2 framework + imx989 + ov64b, unmodified ("RED")
#   imgsensor-recon/imgsensor.ko   same + reconstruction/imgsensor-adaptor-ctx-custom-ldo-slot.patch
set -euo pipefail
GKI=${GKI:-/home/armol/kernel-work/gki-12901745-workspace}
NOTH=${NOTH:-"/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878"}
OUT=${OUT:-$GKI/lieppos/camera-imgsensor}
HERE=$(cd "$(dirname "$0")/.." && pwd)
export PATH=$GKI/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
mkdir -p "$OUT/kout" "$OUT/tree/kernel_device_modules" "$OUT/tree/vendor/mediatek/kernel_modules"
# kbuild cannot cope with the space in the workspace path -> symlinks
ln -sfn "$NOTH/kernel_modules/mtkcam" "$OUT/mtkcam"
ln -sfn "$NOTH/device_modules" "$OUT/devmods"
for d in include drivers arch; do ln -sfn "$NOTH/device_modules/$d" "$OUT/tree/kernel_device_modules/$d"; done
ln -sfn "$NOTH/kernel_modules/mtkcam" "$OUT/tree/vendor/mediatek/kernel_modules/mtkcam"
[ -f "$OUT/kout/Makefile" ] || tar -C "$OUT/kout" -xzf "$GKI/bazel-bin/common/kernel_aarch64_modules_prepare/modules_prepare_outdir.tar.gz"
cp "$GKI/bazel-bin/common/kernel_aarch64/vmlinux.symvers" "$OUT/kout/Module.symvers"
K="make -C $GKI/common O=$OUT/kout ARCH=arm64 LLVM=1 LLVM_IAS=1"
INC="-I$OUT/mtkcam/imgsensor/src-v4l2 -I$OUT/mtkcam/imgsensor/src-v4l2/frame-sync -I$OUT/mtkcam/imgsensor/src-v4l2/virt-sensor -I$OUT/mtkcam/camsys/isp7sp/cam -I$OUT/mtkcam/imgsensor/inc -I$OUT/devmods/drivers/misc/mediatek/imgsensor/inc -I$OUT/mtkcam -I$OUT/mtkcam/include -I$OUT/devmods/include -I$OUT/devmods/drivers/misc/mediatek/include/mt-plat"

# 1. layout probe
mkdir -p "$OUT/layout"; cd "$OUT/layout"
cat > probe.c <<'EOF'
#include <linux/module.h>
#include "adaptor-subdrv.h"
#include "adaptor.h"
struct subdrv_mode_struct a1; struct subdrv_static_ctx a2; struct subdrv_entry a3; struct subdrv_pw_seq_entry a4;
struct mtk_mbus_frame_desc_entry a5; struct SENSOR_WINSIZE_INFO_STRUCT a6; struct mtk_csi_param a7; struct SET_PD_BLOCK_INFO_T a8;
struct subdrv_ops a9; struct subdrv_ctx a10; struct eeprom_info_struct a11; struct mtk_sensor_saturation_info a12; struct dcg_info_struct a13;
MODULE_LICENSE("GPL");
EOF
printf 'obj-m += probe.o\nccflags-y += %s -g -gdwarf-4 -Wno-error\n' "$INC" > Makefile
$K M="$PWD" modules >build.log 2>&1 || true
pahole -C subdrv_mode_struct probe.o | grep 'size: 440'
pahole -C subdrv_static_ctx probe.o | grep 'size: 800'

# 2. donor sub-driver objects (only the .o files are used; modpost warnings expected)
mkdir -p "$OUT/donor-subdrv"; cd "$OUT/donor-subdrv"
for d in imx989_mipi_raw imx989lite_mipi_raw ov64b_mipi_raw; do mkdir -p $d; cp -f "$OUT/mtkcam/imgsensor/src-v4l2/common/$d/"* $d/; done
cat > Makefile <<EOF
obj-m += donor_imx989.o donor_imx989lite.o donor_ov64b.o
donor_imx989-objs := imx989_mipi_raw/imx989mipiraw_Sensor.o
donor_imx989lite-objs := imx989lite_mipi_raw/imx989litemipiraw_Sensor.o
donor_ov64b-objs := ov64b_mipi_raw/ov64bmipiraw_Sensor.o
ccflags-y += $INC -Wno-error
EOF
$K M="$PWD" KBUILD_MODPOST_WARN=1 modules >build.log 2>&1 || true

# 3. dw9781c unmodified (hf_manager CRCs taken from the stock import table)
mkdir -p "$OUT/donor-dw9781c"; cd "$OUT/donor-dw9781c"
cp "$OUT/devmods/drivers/misc/mediatek/lens/ois/dw9781c/dw9781c.c" .
printf 'obj-m += dw9781c.o\nccflags-y += -I%s/devmods/drivers/misc/mediatek/sensor/2.0/core -I%s/devmods/include -I%s/mtkcam/include -Wno-error\n' "$OUT" "$OUT" "$OUT" > Makefile
printf '0x4d0971f6\thf_device_register_manager_create\tvendor/hf_manager\tEXPORT_SYMBOL_GPL\t\n0x18ee6460\thf_device_unregister_manager_destroy\tvendor/hf_manager\tEXPORT_SYMBOL_GPL\t\n' > hf_manager.stock-import.symvers
$K M="$PWD" KBUILD_EXTRA_SYMBOLS="$PWD/hf_manager.stock-import.symvers" modules >build.log 2>&1

# 4. imgsensor framework RED + recon
for v in imgsensor-build imgsensor-recon; do
  rm -rf "$OUT/$v"; mkdir -p "$OUT/$v"; cp -r "$OUT/mtkcam/imgsensor/src-v4l2/." "$OUT/$v/"
  cd "$OUT/$v"
  [ $v = imgsensor-recon ] && patch -p1 < "$HERE/reconstruction/imgsensor-adaptor-ctx-custom-ldo-slot.patch"
  $K M="$PWD" KBUILD_MODPOST_WARN=1 DEVICE_MODULES_PATH="$OUT/tree/kernel_device_modules" \
     CONFIG_MTK_V4L2_IMGSENSOR=m CONFIG_MTK_IMGSENSOR_PROJECT=k6878v1_64 \
     CONFIG_CUSTOM_KERNEL_IMGSENSOR="imx989_mipi_raw ov64b_mipi_raw" \
     KCFLAGS="-Wno-error -DCONFIG_MTK_AEE_FEATURE=1" modules >build.log 2>&1
done
echo "done: $OUT"
