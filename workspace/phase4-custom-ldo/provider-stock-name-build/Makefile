ifneq ($(KERNELRELEASE),)
obj-m += custom-ldo-wl2868.o
custom-ldo-wl2868-y := custom_ldo_wl2868.o
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
