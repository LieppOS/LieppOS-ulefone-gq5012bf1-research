ifneq ($(KERNELRELEASE),)

obj-m += panel-ky-vtdr6115-dphy-cmd.o

else

# Source-built provider symvers for the 7 MT6878 display-stack imports.
# See lieppos/panel-vtdr6115-provider-harness (build harness only).
PANEL_EXT_SYMVERS := $(OUT_DIR)/../lieppos/panel-vtdr6115-provider-harness/Module.symvers

.PHONY: all modules modules_install clean

all modules:
	@test -f "$(PANEL_EXT_SYMVERS)" || { \
		echo "missing panel-ext Module.symvers: $(PANEL_EXT_SYMVERS)"; \
		exit 1; \
	}
	$(MAKE) -C $(KERNEL_SRC) M=$(M) \
		KBUILD_EXTRA_SYMBOLS="$(PANEL_EXT_SYMVERS)" \
		modules

modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) \
		KBUILD_EXTRA_SYMBOLS="$(PANEL_EXT_SYMVERS)" \
		modules_install

clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean

endif
