# Exact-GKI out-of-tree build of the reconstructed TrustKernel TKCore module
# (GQ5012BF1 stock vendor-ramdisk module, load index 100).
#
# This is a RECONSTRUCTION, not a vendor source drop:
#   * the private TrustKernel type graph lives in ../trustkernel/include and
#     is shared by every island module;
#   * the structural donor is OP-TEE optee_linuxdriver, which TrustKernel
#     itself derived tkcore from (67 of the 122 stock functions map onto it);
#   * TrustKernel-specific subsystems (log daemon, procfs, clock manager,
#     secure SPI proxy, compat conversion, dma-buf shm) are reconstructed from
#     the stock ELF and its consumers.
#
# Stock tkcore.ko has ZERO intermodule imports, so this module must resolve
# against exact GKI alone.  No KBUILD_MODPOST_WARN, no CRC injection, no
# witness symvers.
ifneq ($(KERNELRELEASE),)

ccflags-y += -I$(srctree)/$(src)/../trustkernel/include
ccflags-y += -I$(srctree)/$(src)/tkcore

obj-m += tkcore.o
tkcore-y += tkcore/tee_core.o
tkcore-y += tkcore/tee_context.o
tkcore-y += tkcore/tee_session.o
tkcore-y += tkcore/tee_shm.o
tkcore-y += tkcore/tee_supp_com.o
tkcore-y += tkcore/tee_wait_queue.o
tkcore-y += tkcore/tee_sysfs.o
tkcore-y += tkcore/tee_lifecycle_prereq.o
tkcore-y += tkcore/tee_kernel_api.o

else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
