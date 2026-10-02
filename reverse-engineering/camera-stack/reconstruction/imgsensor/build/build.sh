#!/bin/bash
# Reproducible build of the reconstructed GQ5012BF1 imgsensor.ko.
#
# usage: build.sh <gki-12901745-workspace> <kout> <kernel_device_modules> [parity|corrected]
#
#   <gki-12901745-workspace>  GKI android14-6.1 build 12901745 checkout (common/,
#                             prebuilts/clang/host/linux-x86/clang-r487747c,
#                             vendor/mediatek/kernel_modules/mtkcam/imgsensor/inc ...)
#   <kout>                    prepared O= dir of that kernel (gki_defconfig,
#                             `make modules_prepare`)
#   <kernel_device_modules>   MTK kernel_device_modules tree with
#                             patches/kernel_device_modules-kd_imgsensor.h-gq5012bf1-ids.patch applied
#
# Environment facts that matter for byte parity (all verified):
#   * clang r487747c (stock .comment section is identical);
#   * UTS_RELEASE "6.1.115-android14-11-g945dff7bc1bf" (stock vermagic);
#   * KCFLAGS -faddrsig (stock carries .llvm_addrsig) and the two AEE defines;
#   * no scmversion (stock tree was not a git checkout -> module_scmversion=);
#   * import CRCs/providers from stock-imgsensor-imports.symvers (modinfo depends=);
#   * sensor list/link order: see SENSORS below (IMGSENSOR_SUBDRVS order);
#   * M= given as common/../vendor/... (determines embedded __FILE__ strings);
#   * INSTALL_MOD_STRIP-style `llvm-strip --strip-debug` on the result.
set -euo pipefail
G=$(realpath "$1"); KOUT=$(realpath "$2"); KDM=$(realpath "$3"); MODE=${4:-parity}
HERE=$(cd "$(dirname "$0")" && pwd)
SRC="$HERE/../src"
DST=$G/vendor/mediatek/kernel_modules/mtkcam/imgsensor/src-v4l2
CLANG=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin
export PATH=$CLANG:$PATH
SENSORS="imx989_mipi_raw imx989cts_mipi_raw s5kgm2sp_mipi_raw s5kgn1sp_mipi_raw ov32b40_mipi_raw s5kjn1_mipi_raw s5kjn1cts_mipi_raw s5kjn1main2_mipi_raw ov64b_mipi_raw"

REL=6.1.115-android14-11-g945dff7bc1bf
echo "#define UTS_RELEASE \"$REL\"" > "$KOUT/include/generated/utsrelease.h"
echo "$REL" > "$KOUT/include/config/kernel.release"

mkdir -p "$DST"
rsync -a --exclude .git "$SRC/" "$DST/"
# kbuild cannot handle spaces in KBUILD_EXTRA_SYMBOLS: stage it next to the source
SYMVERS="$DST/../stock-imgsensor-imports.symvers"
cp "$HERE/stock-imgsensor-imports.symvers" "$SYMVERS"

EXTRA=""
[ "$MODE" = corrected ] && EXTRA="-DGQ5012BF1_CAM_CORRECTED"

# M= must be spelled relative to common/ ("common/../vendor/..."): with
# -fmacro-prefix-map=$G/common/= this makes __FILE__ "../vendor/mediatek/...",
# which is exactly what stock embeds in .rodata.str/.rodata.str1.1.
MREL="$G/common/../vendor/mediatek/kernel_modules/mtkcam/imgsensor/src-v4l2"
make -C "$G/common" O="$KOUT" M="$MREL" ARCH=arm64 LLVM=1 LLVM_IAS=1 \
	KBUILD_MODPOST_WARN=1 DEVICE_MODULES_PATH="$KDM" \
	CONFIG_MTK_V4L2_IMGSENSOR=m CONFIG_MTK_IMGSENSOR_PROJECT=k6878v1_64 \
	CONFIG_CUSTOM_KERNEL_IMGSENSOR="$SENSORS" \
	module_scmversion= \
	KCFLAGS="$EXTRA -faddrsig -Wno-error -DCONFIG_MTK_AEE_FEATURE=1 -DCONFIG_MTK_AEE_AED_MODULE=1" \
	KBUILD_EXTRA_SYMBOLS="$(realpath "$SYMVERS")" modules

llvm-strip --strip-debug -o "$DST/imgsensor.$MODE.stripped.ko" "$DST/imgsensor.ko"
echo "built: $DST/imgsensor.ko (unstripped, keeps DWARF for tooling)"
echo "       $DST/imgsensor.$MODE.stripped.ko (compare this one with stock)"
