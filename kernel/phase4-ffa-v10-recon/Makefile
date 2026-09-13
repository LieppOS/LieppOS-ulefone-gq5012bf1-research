# Exact-GKI out-of-tree build of the in-tree FF-A transport, module basename
# ffa_v10 (matching the GQ5012BF1 stock vendor module).
#
# Sources are byte-identical copies of
#   common/drivers/firmware/arm_ffa/{bus.c,driver.c,smccc.c,common.h}
# at common commit 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09.  No delta.
#
# Two config symbols must be visible, both proven by the stock ELF:
#   CONFIG_ARM_FFA_TRANSPORT_MODULE - stock is a module, and without it
#       include/linux/arm_ffa.h hides the real prototypes behind
#       !IS_REACHABLE() stubs, which would change every export CRC.
#   CONFIG_ARM_FFA_SMCCC - stock contains __arm_ffa_fn_smc/__arm_ffa_fn_hvc
#       and a real (non-stub) ffa_transport_init.
ifneq ($(KERNELRELEASE),)
ccflags-y += -DCONFIG_ARM_FFA_TRANSPORT_MODULE=1
ccflags-y += -DCONFIG_ARM_FFA_SMCCC=1
obj-m += ffa_v10.o
ffa_v10-y := bus.o driver.o smccc.o
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
