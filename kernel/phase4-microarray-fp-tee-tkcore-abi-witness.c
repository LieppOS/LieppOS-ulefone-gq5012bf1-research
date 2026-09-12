// SPDX-License-Identifier: GPL-2.0
/*
 * Build-only ABI witness for the GQ5012BF1 stock tkcore.ko TrustKernel export
 * consumed by microarray_fp_tee.ko.
 *
 * The real runtime provider is stock tkcore.ko.  Its implementation was read
 * out of the stock binary: tee_spi_transfer() validates its arguments, copies
 * txbuf into rxbuf, opens a TEEC session to the TrustKernel SPI proxy TA
 * 966d3f7c-04ef-1beb-08b7-57f37a6d87f9, and invokes command 0 with
 * paramTypes 0x75 = (MEMREF_TEMP_INPUT(conf, conf_len),
 * MEMREF_TEMP_INOUT(rxbuf, len), NONE, NONE).  None of that behaviour is
 * reimplemented here; this file exists only so genksyms/modpost derive the
 * MODVERSION CRC naturally from C, with no fake symvers or CRC patching.
 *
 * Expected generated CRC (must match the stock consumer __versions table):
 *   tee_spi_transfer  0x184ce7da
 *
 * This module must never be installed or loaded as a TEE provider.
 */
#include <linux/module.h>

int tee_spi_transfer(void *conf, int conf_size, const char *txbuf,
		     char *rxbuf, int len)
{
	return -ENODEV;
}
EXPORT_SYMBOL(tee_spi_transfer);

MODULE_DESCRIPTION("Build-only ABI witness for stock tkcore tee_spi_transfer");
MODULE_LICENSE("GPL v2");
