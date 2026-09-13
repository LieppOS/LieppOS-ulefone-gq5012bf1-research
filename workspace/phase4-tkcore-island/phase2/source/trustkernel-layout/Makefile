# Analysis-only layout probe for the TrustKernel ABI island.
ifneq ($(KERNELRELEASE),)

ccflags-y += -I$(srctree)/$(src)/../trustkernel/include
ccflags-y += -I$(srctree)/$(src)/../trustkernel

obj-m += tk_layout_probe.o
tk_layout_probe-y += layout-probe.o

else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
