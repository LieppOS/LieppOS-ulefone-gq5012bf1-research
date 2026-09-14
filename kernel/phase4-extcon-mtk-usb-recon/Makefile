# Provider ABI modules supplying the four non-GKI imports of the stock module:
#   tcpc_class   -> register_tcp_dev_notifier, tcpc_dev_get_by_name,
#                   tcpm_inquire_remote_cc  (+ inc/tcpm.h prototypes)
#   mt6375-charger-provider-abi -> yft_usb_flag
#
# Legacy (M=) builds link against whichever Module.symvers actually exists: the
# kleaf-restored output directory, the module's own build directory, or the
# checked-in baseline/ snapshot. LIEPPOS_SYMVERS overrides the whole list.
LIEPPOS_LB := $(KERNEL_SRC)/../lieppos

LIEPPOS_PROVIDER_SYMVERS ?= \
	$(wildcard $(OUT_DIR)/../lieppos/tcpc-class-recon/Module.symvers) \
	$(wildcard $(OUT_DIR)/../lieppos/pd-dbg-info-recon/Module.symvers) \
	$(wildcard $(LIEPPOS_LB)/tcpc-class-recon/baseline/Module.symvers) \
	$(wildcard $(LIEPPOS_LB)/mt6375-charger-provider-abi/Module.symvers)

LIEPPOS_TCPC_TREE := $(LIEPPOS_LB)/tcpc-class-recon

# Type-C / TCPM half of the reconstruction. Default y: stock's symbol table
# proves those paths were compiled into the shipping module (it imports
# register_tcp_dev_notifier, tcpc_dev_get_by_name, tcpm_inquire_remote_cc and
# the seq_file/procfs set, and stock's .modinfo says depends=tcpc_class,
# mt6375-charger). The gate has to be an explicit -D because an external module
# never sees a Kconfig symbol of its own: IS_ENABLED() only reads
# include/generated/autoconf.h, which belongs to the kernel build.
#
# The macro name is deliberately the vendor's own CONFIG_TCPC_CLASS: inc/tcpm.h
# switches between the real externs and TCPC_CLASS_NA stub inlines on exactly
# that spelling, so a private gate name would silently bind every Type-C call to
# a `return 0` stub and produce a module with no tcpc_class dependency at all.
LIEPPOS_EXTCON_TCPM ?= y

ifeq ($(LIEPPOS_EXTCON_TCPM),y)
ccflags-y += -DCONFIG_TCPC_CLASS=1 -I$(LIEPPOS_TCPC_TREE)/inc
endif

ifneq ($(KERNELRELEASE),)
obj-m += extcon_mtk_usb.o
# Kconfig spelling, for any build that does go through Kconfig.
ccflags-$(CONFIG_EXTCON_MTK_USB_RECON_TCPM) += -DCONFIG_TCPC_CLASS=1
KBUILD_EXTRA_SYMBOLS += $(LIEPPOS_PROVIDER_SYMVERS)
else
.PHONY: all modules modules_install clean
all modules:
	@echo "LIEPPOS_PROVIDER_SYMVERS=$(LIEPPOS_PROVIDER_SYMVERS)"
	@test -n "$(LIEPPOS_PROVIDER_SYMVERS)" || { \
		echo "ERROR: no provider Module.symvers found (tcpc_class / mt6375-charger)"; \
		exit 1; }
	$(MAKE) -C $(KERNEL_SRC) M=$(M) \
		KBUILD_EXTRA_SYMBOLS="$(LIEPPOS_PROVIDER_SYMVERS)" modules

modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) \
		KBUILD_EXTRA_SYMBOLS="$(LIEPPOS_PROVIDER_SYMVERS)" modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
