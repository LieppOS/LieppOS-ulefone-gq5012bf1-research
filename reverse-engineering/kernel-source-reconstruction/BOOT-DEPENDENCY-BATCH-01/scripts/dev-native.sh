#!/bin/bash
# Development-only native stage, identical command to bulk-build.sh native block.
set -euo pipefail
N='/home/armol/androido_dalykai/LieppOS custom ROM/android_kernel_modules_boot_dependencies_ulefone_gq5012bf1'
cd /tmp; source "$N/scripts/lib.sh"; need_ws "$1"; TAG=$2; OUT=$WS/out/$TAG; mkdir -p "$OUT"
export KBUILD_BUILD_USER=lieppos KBUILD_BUILD_HOST=boot-dependency-build KBUILD_BUILD_VERSION=1 KBUILD_BUILD_TIMESTAMP='Thu Oct 8 12:00:00 UTC 2026'
NK=$WS/native-kout
NATIVE="drivers/perf/arm_dsu_pmu.ko drivers/iio/buffer/kfifo_buf.ko drivers/iio/buffer/industrialio-triggered-buffer.ko"
MAP="-ffile-prefix-map=$WS=/lieppos-audio-shared-ws -fdebug-prefix-map=$WS=/lieppos-audio-shared-ws"
rm -rf "$NK"; cp -a "$KOUT" "$NK"; rm -f "$NK/vmlinux" "$NK/Module.symvers"
make -C "$COMMON" O="$NK" ARCH=arm64 LLVM=1 LLVM_IAS=1 KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ KBUILD_MIXED_TREE="$WS/btfbase" \
 KERNELRELEASE="$KERNEL_RELEASE" module_scmversion=g945dff7bc1bf \
 HOSTCFLAGS="-Wno-error=incompatible-pointer-types-discards-qualifiers $MAP" KAFLAGS="$MAP" KCPPFLAGS_COMPAT="$MAP" \
 KCFLAGS="-D__ANDROID_COMMON_KERNEL__ -faddrsig -fdebug-prefix-map=$WS/=/lieppos-audio-shared-ws/" \
 PAHOLE="$WS/kernel-build-tools/linux-x86/bin/pahole" -j"${JOBS:-4}" $NATIVE > "$OUT/native.log" 2>&1 && echo 0 > "$OUT/native-exit" || echo $? > "$OUT/native-exit"
for pair in $NATIVE; do [ -f "$NK/$pair" ] && { m=$(basename $pair .ko); cp "$NK/$pair" "$OUT/$m.ko"; llvm-strip --strip-debug -o "$OUT/$m.stripped" "$OUT/$m.ko"; } || true; done
log "dev native exit=$(cat $OUT/native-exit)"
