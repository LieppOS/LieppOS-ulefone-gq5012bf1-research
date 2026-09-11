ifneq ($(KERNELRELEASE),)
obj-m += hynitron.o
KBUILD_EXTRA_SYMBOLS += $(src)/stock-yft-devinfo.symvers
ccflags-y += -DHYNITRON_ALLOW_FW_PROGRAMMING=0
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) KBUILD_EXTRA_SYMBOLS="$(CURDIR)/stock-yft-devinfo.symvers" modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
