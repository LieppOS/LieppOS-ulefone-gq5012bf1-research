# Phase-3F provider provenance only; all implementation sources are frozen
# symlinks to ../tkcore-drv-recon. No stock tkcore witness is accepted.
LIEPPOS_PROVIDER_SYMVERS := \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/tkcore-island/Module.symvers) \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/ffa-v10/Module.symvers)

ifneq ($(KERNELRELEASE),)
ccflags-y += -I$(srctree)/$(src)/include
ccflags-y += -I$(srctree)/$(src)/../trustkernel/include
ccflags-y += -DCONFIG_ARM_FFA_TRANSPORT_MODULE=1
ccflags-y += -faddrsig
obj-m += tkcore_drv.o
tkcore_drv-y := tkcore_drv_main.o tee_task.o tee_mem.o handle.o
KBUILD_EXTRA_SYMBOLS += $(LIEPPOS_PROVIDER_SYMVERS)
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
