LIEPPOS_PROVIDER_SYMVERS := \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/mt6375-charger-provider-abi/Module.symvers)

ifneq ($(KERNELRELEASE),)
obj-m += yft_tiny2c_usb.o
KBUILD_EXTRA_SYMBOLS += $(LIEPPOS_PROVIDER_SYMVERS)
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
