ifneq ($(KERNELRELEASE),)
ccflags-y += -faddrsig
KBUILD_EXTRA_SYMBOLS += $(srctree)/$(src)/charger_class-stock.symvers.h
obj-m += sc8571_charger.o
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
