LIEPPOS_PROVIDER_SYMVERS := \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/custom-ldo-wl2868-recon/stock-name/Module.symvers)

ifneq ($(KERNELRELEASE),)
KBUILD_EXTRA_SYMBOLS += $(LIEPPOS_PROVIDER_SYMVERS)
ccflags-y += -faddrsig
obj-m += custom_ldo.o
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) \
		KBUILD_EXTRA_SYMBOLS="$(LIEPPOS_PROVIDER_SYMVERS)" modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
