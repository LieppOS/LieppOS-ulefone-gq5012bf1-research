# Isolated out-of-tree build (CI-12901745 GKI, clang r487747c, LTO=none):
#   make -C <gki>/common O=<kout> M=$PWD ARCH=arm64 LLVM=1 LLVM_IAS=1 modules
# Requires gImage_logo.inc (stock boot bitmap, NOT distributed here; see README)
# and provider symvers for hynitron + yft_devinfo.
obj-m += spi_tiny_co5300_lcd.o
KBUILD_EXTRA_SYMBOLS += $(src)/hynitron.symvers $(src)/yft-devinfo.symvers
