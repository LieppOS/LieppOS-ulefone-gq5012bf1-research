# source me: NFC parity environment
export G=/home/armol/kernel-work/gki-12901745-workspace
export R="/home/armol/androido_dalykai/LieppOS custom ROM/ulefone-gq5012bf1-research"
export NR="$R/reverse-engineering/nfc"
export PATH=$G/prebuilts/clang/host/linux-x86/clang-r487747c/bin:$PATH
export KON=$G/lieppos/nfc/kout
export NOUT=$G/lieppos/nfc/kernel_device_modules-6.1/drivers/misc/mediatek/nfc/st21nfc
export STK="$R/workspace/gq5012bf1/stock/vendor-ramdisks/platform-extracted/lib/modules/st21nfc.ko"
export SRC=$G/kernel_device_modules-6.1/drivers/misc/mediatek/nfc/st21nfc
nbuild(){ cd $G/common && make O=$KON M=../kernel_device_modules-6.1/drivers/misc/mediatek/nfc/st21nfc ARCH=arm64 LLVM=1 LLVM_IAS=1 \
  KCONFIG_EXT_PREFIX=../kernel_device_modules-6.1/ DEVICE_MODULES_REL_DIR=../kernel_device_modules-6.1 \
  'DEVICE_MODULES_PATH=$(srctree)/$(DEVICE_MODULES_REL_DIR)' 'DEVCIE_MODULES_INCLUDE=-I$(DEVICE_MODULES_PATH)/include' \
  KBUILD_MODPOST_WARN=1 module_scmversion= KCFLAGS="-faddrsig" -j16 modules; }
npar(){ python3 "$R/reverse-engineering/scripts/ko-pair-parity.py" "$STK" "$NOUT/st21nfc.ko"; }
