# Phase-3F final TrustKernel source-island acceptance for microarray_fp_tee.
#
# microarray_fp_tee.c is a symlink to the frozen //lieppos/microarray-fp-tee-recon
# reconstruction; not one byte of driver source changes here.
#
# ABI inputs - ALL real source-built providers, zero stock witnesses:
#   fingerprint-recon/Module.symvers  real source-built yft_* provider
#   spi-mt65xx/Module.symvers         real source-built SPI provider
#   tkcore-island/Module.symvers      final reconstructed tkcore provider,
#                                     supplying the single tee_spi_transfer edge
#
# The historical tkcore-provider.symvers stock-runtime record is deliberately
# NOT present in this package.
LIEPPOS_PROVIDER_SYMVERS := \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/fingerprint-recon/Module.symvers) \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/spi-mt65xx/Module.symvers) \
	$(wildcard $(COMMON_OUT_DIR)/lieppos/tkcore-island/Module.symvers)

ifneq ($(KERNELRELEASE),)
ccflags-y += -faddrsig
obj-m += microarray_fp_tee.o
KBUILD_EXTRA_SYMBOLS += $(LIEPPOS_PROVIDER_SYMVERS)
else
.PHONY: all modules modules_install clean
all modules:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) \
		KBUILD_EXTRA_SYMBOLS="$(LIEPPOS_PROVIDER_SYMVERS)" modules
modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) modules_install
clean:
	$(MAKE) -C $(KERNEL_SRC) M=$(M) clean
endif
