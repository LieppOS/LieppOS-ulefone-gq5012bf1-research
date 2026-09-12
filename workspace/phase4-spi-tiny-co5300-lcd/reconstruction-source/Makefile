ifneq ($(KERNELRELEASE),)
obj-m += spi_tiny_co5300_lcd.o
KBUILD_EXTRA_SYMBOLS += $(src)/hynitron-rebuilt.Module.symvers
KBUILD_EXTRA_SYMBOLS += $(src)/stock-yft-devinfo.symvers
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) \
		KBUILD_EXTRA_SYMBOLS="$(CURDIR)/hynitron-rebuilt.Module.symvers $(CURDIR)/stock-yft-devinfo.symvers" modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
