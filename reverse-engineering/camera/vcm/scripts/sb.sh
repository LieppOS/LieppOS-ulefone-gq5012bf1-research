#!/bin/bash
# sb.sh <kdm-root> <module> <subdir> "<objs>" [tag]
# isolated M= build of one KDM module from a full KDM tree + parity vs stock (A) into par/<module>[-tag]
set -e
G=/home/armol/kernel-work/gki-12901745-workspace
W=$G/lieppos/vcm
R=$(readlink -f "$1"); MOD=$2; SUB=$3; OBJS=$4; TAG=${5:+-$5}
M=$R/$SUB
[ -f $M/Kbuild.orig ] || { [ -f $M/Kbuild ] && ! grep -q "^# sb.sh" $M/Kbuild && cp $M/Kbuild $M/Kbuild.orig || true; }
MK=Makefile; [ -f $M/Kbuild.orig ] && MK=Kbuild.orig
cat > $M/Kbuild <<EOK
# sb.sh generated
LINUXINCLUDE := ${XLINUXINCLUDE} -I$R/include \$(LINUXINCLUDE)
include \$(src)/$MK
obj-y :=
obj-m := $MOD.o
$( [ "$OBJS" = "$MOD.o" ] || printf "%s-y := %s\n%s-objs :=" "$MOD" "$OBJS" "$MOD")
KBUILD_EXTRA_SYMBOLS += ${XSYMVERS:-$W/stock-all.symvers}
ccflags-y += ${XCCFLAGS}
EOK
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
cd $G/common
rm -f $M/$MOD.ko
make O=$G/lieppos/nfc/kout M=$M ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_PATH=$R DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  'DEVCIE_MODULES_INCLUDE=-I$(DEVICE_MODULES_PATH)/include' \
  ${MPW:+KBUILD_MODPOST_WARN=1} module_scmversion= -j${J:-16} "KCFLAGS=-faddrsig -fmacro-prefix-map=$R/=../kernel_device_modules-6.1/ ${XKCFLAGS}" modules > $M/build-$MOD.log 2>&1 || { grep -E 'error|Error' $M/build-$MOD.log | head -20; exit 1; }
llvm-strip --strip-debug -o $M/$MOD.stripped.ko $M/$MOD.ko
P=$W/par/$MOD$TAG; rm -rf $P; cp $M/$MOD.stripped.ko $P.ko
python3 '/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research/reverse-engineering/display-input/rear-display-input/scripts/ko-parity-tsv.py' $W/stock/$MOD.ko $M/$MOD.stripped.ko $P > $P.log 2>&1 || true
grep -h '^functions\|^data\|^imports\|^exports\|^modinfo' $P/SUMMARY.txt | cut -c1-170
python3 $W/secdiff.py $W/stock/$MOD.ko $M/$MOD.stripped.ko | tee $P.secdiff
