#!/bin/bash
# Kbuild driver for the isolated MALI-GPU-KERNEL reconstruction.
#   kb.sh kdm <make goals...>   -> M=build/kdm  (kernel_device_modules-6.1 @957dac, gpu/mediatek only)
#   kb.sh gpu <make goals...>   -> M=build/gpu  (kernel_modules/gpu @5f75a3b, mt6878 mali r44p1)
# Exact GKI 12901745 common (6b18f0b574ab), vendor kout (gki_defconfig + mgk_64_k61_defconfig,
# kernel.release stamped to the stock 6.1.115-android14-11-g945dff7bc1bf), clang r487747c.
# KCFLAGS: -D__ANDROID_COMMON_KERNEL__ is what GKI build.config.common (HEAD) contributes to every
# Kleaf/build.sh module build; -faddrsig because stock carries .llvm_addrsig (host clang default drops it).
# Path provenance: MTK built with M relative to common (../kernel_device_modules-6.1,
# ../vendor/mediatek/kernel_modules/gpu); our trees live elsewhere, so __FILE__ is remapped
# with -fmacro-prefix-map to the stock spelling. That flag only rewrites __FILE__ text.
# clang applies the first matching map in descending key order, and headers reached via
# -I$(srctree)/<rel> arrive as "<common>/../../...", so that unnormalized spelling is mapped too.
set -euo pipefail
W=${W:-/home/armol/kernel-work/accelerator-mali-gpu-kernel}
G=${G:-/home/armol/kernel-work/gki-12901745-workspace}
KO=${KO:-$W/kout}
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
unit=$1; shift
COMMON=$G/common
KDM_ABS=${KDM_DIR:-$W/build/kdm}
KDM_REL=$(realpath --relative-to=$COMMON $KDM_ABS)
case $unit in
  kdm) M=$KDM_REL; MAP="-fmacro-prefix-map=$COMMON/$KDM_REL=../kernel_device_modules-6.1 -fmacro-prefix-map=$KDM_REL=../kernel_device_modules-6.1 -fmacro-prefix-map=$KDM_ABS=../kernel_device_modules-6.1";
       OPTS=() ;;
  gpu) GPU_DIR=${GPU_DIR:-$W/build/gpu}; GREL=$(realpath --relative-to=$COMMON $GPU_DIR); M=$GREL;
       MAP="-fmacro-prefix-map=$COMMON/$GREL=../vendor/mediatek/kernel_modules/gpu -fmacro-prefix-map=$COMMON/$KDM_REL=../kernel_device_modules-6.1 -fmacro-prefix-map=$GREL=../vendor/mediatek/kernel_modules/gpu -fmacro-prefix-map=$GPU_DIR=../vendor/mediatek/kernel_modules/gpu -fmacro-prefix-map=$KDM_REL=../kernel_device_modules-6.1 -fmacro-prefix-map=$KDM_ABS=../kernel_device_modules-6.1"
       # gpu/Makefile KBUILD_OPTIONS (stock build.config EXT_MODULES flow)
       OPTS=(BUILD_RULE=OOT CONFIG_MALI_MEMORY_GROUP_MANAGER=y CONFIG_MALI_PROTECTED_MEMORY_ALLOCATOR=y CONFIG_DMA_SHARED_BUFFER_TEST_EXPORTER=y) ;;
  *) echo "unit?"; exit 2 ;;
esac
[ "$(cat $KO/include/config/kernel.release)" = 6.1.115-android14-11-g945dff7bc1bf ]
cd $COMMON
[ "$(realpath -m $KO/$M)" = "$(realpath -m $COMMON/$M)" ] || { echo "relative M= must resolve identically from O= ($KO) and common" >&2; exit 1; }
exec make O=$KO M=$M ARCH=arm64 LLVM=1 LLVM_IAS=1 module_scmversion= \
  DEVICE_MODULES_PATH='$(srctree)/'$KDM_REL DEVICE_MODULES_REL_DIR=$KDM_REL \
  DEVCIE_MODULES_INCLUDE='-I$(srctree)/'$KDM_REL/include \
  KCFLAGS="-D__ANDROID_COMMON_KERNEL__ -faddrsig $MAP" "${OPTS[@]}" "$@"
