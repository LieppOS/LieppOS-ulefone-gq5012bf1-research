ifneq ($(KERNELRELEASE),)
ccflags-y += -faddrsig -fno-builtin-strcmp -fno-builtin-strncpy
ccflags-y += -DSH366003_ALLOW_AFI_PROGRAMMING=$(SH366003_ALLOW_AFI_PROGRAMMING)
KBUILD_EXTRA_SYMBOLS += $(srctree)/$(src)/stock-yft-devinfo.symvers
obj-m += sh366003_fg.o
SH366003_ALLOW_AFI_PROGRAMMING ?= 0
else
.PHONY: all modules oracle-parity modules_install clean
SH366003_ALLOW_AFI_PROGRAMMING ?= 0
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) SH366003_ALLOW_AFI_PROGRAMMING=$(SH366003_ALLOW_AFI_PROGRAMMING) modules
oracle-parity:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) SH366003_ALLOW_AFI_PROGRAMMING=1 modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
