LIEPPOS_PROVIDER_SYMVERS := \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/mtk-pwm-provider/Module.symvers)

ifneq ($(KERNELRELEASE),)
ccflags-y += -I$(src)/include
obj-m += leds_ln2403.o
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
