# hynitron.ko (GQ5012BF1 rear touch) - Hynitron V2.1 20201222 reconstruction
# Exact-parity build: CI-12901745 GKI tree, clang r487747c, CONFIG_LTO_NONE.
ifneq ($(KERNELRELEASE),)
obj-m += hynitron.o
hynitron-y := hynitron_core.o hynitron_i2c.o hynitron_esd_check.o hynitron_tool_debug.o \
              hynitron_update_firmware.o hynitron_gesture.o hynitron_proximity.o
# NOTE: build with KCFLAGS=-faddrsig (global: also applies to hynitron.mod.o); see build.sh
KBUILD_EXTRA_SYMBOLS += $(src)/stock-yft-devinfo.symvers
endif
