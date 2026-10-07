#!/usr/bin/env bash
# Two independent clean builds (B1, B2) of the unmodified NothingOSS MT6878
# dw9781c.c with the exact GKI ab/12901745 toolchain (clang r487747c), then
# the Kleaf install step (strip --strip-debug).  Offline, host-only.
#
#   * KCFLAGS=-faddrsig      stock objects carry .llvm_addrsig (Kleaf build);
#                            the plain modules_prepare kbuild here does not
#                            emit it without the flag
#   * llvm-objcopy --strip-debug   == INSTALL_MOD_STRIP=1 (vendor_dlkm install)
#   * hf_manager export CRCs are taken verbatim from the stock __versions table
#
# Requires the kout/ (modules_prepare) tree prepared by
# ../../scripts/build_donor_camera_modules.sh.
set -euo pipefail
GKI=${GKI:-/home/armol/kernel-work/gki-12901745-workspace}
NOTH=${NOTH:-"/home/armol/androido_dalykai/LieppOS custom ROM/kernel-research/nothing-mt6878"}
BASE=${BASE:-$GKI/lieppos/camera-imgsensor}
OUT=${OUT:-$GKI/lieppos/dw9781c-b1b2}
export PATH=$GKI/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
[ -f "$BASE/kout/Makefile" ] || { echo "run build_donor_camera_modules.sh first" >&2; exit 1; }
K="make -C $GKI/common O=$BASE/kout ARCH=arm64 LLVM=1 LLVM_IAS=1"
SRC="$NOTH/device_modules/drivers/misc/mediatek/lens/ois/dw9781c/dw9781c.c"
# Both builds run from the same absolute directory (DWARF comp_dir is
# path-dependent and feeds the link-time build-id); each is a fresh tree.
for b in B1 B2; do
  rm -rf "$OUT/work" "$OUT/$b"; mkdir -p "$OUT/work" "$OUT/$b"; cd "$OUT/work"
  cp "$SRC" .
  printf 'obj-m += dw9781c.o\nccflags-y += -I%s/devmods/drivers/misc/mediatek/sensor/2.0/core -I%s/devmods/include -I%s/mtkcam/include -Wno-error\n' "$BASE" "$BASE" "$BASE" > Makefile
  printf '0x4d0971f6\thf_device_register_manager_create\tvendor/hf_manager\tEXPORT_SYMBOL_GPL\t\n0x18ee6460\thf_device_unregister_manager_destroy\tvendor/hf_manager\tEXPORT_SYMBOL_GPL\t\n' > hf_manager.stock-import.symvers
  $K M="$PWD" KBUILD_EXTRA_SYMBOLS="$PWD/hf_manager.stock-import.symvers" KCFLAGS=-faddrsig modules > build.log 2>&1
  llvm-objcopy --strip-debug dw9781c.ko dw9781c.stripped.ko
  cp dw9781c.ko dw9781c.stripped.ko dw9781c.o build.log "$OUT/$b/"
  (cd "$OUT/$b" && sha256sum dw9781c.o dw9781c.ko dw9781c.stripped.ko)
done
echo "source sha256: $(sha256sum "$SRC" | cut -d' ' -f1)"
for f in dw9781c.o dw9781c.ko dw9781c.stripped.ko; do
  cmp "$OUT/B1/$f" "$OUT/B2/$f" && echo "B1 == B2 ($f byte-identical)"
done
