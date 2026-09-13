ifneq ($(KERNELRELEASE),)
ccflags-y += -Wno-missing-prototypes -Wno-missing-declarations
obj-m += kcfi_probe.o
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) KBUILD_MODPOST_WARN=1 modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
