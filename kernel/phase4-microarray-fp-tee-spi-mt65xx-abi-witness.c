// SPDX-License-Identifier: GPL-2.0
/*
 * Build-only ABI witness for the GQ5012BF1 stock spi-mt65xx.ko vendor delta.
 *
 * The real runtime provider is stock spi-mt65xx.ko.  This file defines only
 * the two vendor-added exports consumed by microarray_fp_tee.ko so that
 * genksyms/modpost derive their MODVERSION CRCs naturally from C, with no
 * fake symvers, CRC patching or ELF editing.
 *
 * Expected generated CRCs (must match the stock consumer __versions table):
 *   mt_spi_enable_master_clk  0x1cc49782
 *   mt_spi_disable_master_clk 0xccc1e350
 *
 * This module must never be installed or loaded as a SPI controller driver.
 */
#include <linux/module.h>
#include <linux/spi/spi.h>

void mt_spi_enable_master_clk(struct spi_device *spidev)
{
}
EXPORT_SYMBOL(mt_spi_enable_master_clk);

void mt_spi_disable_master_clk(struct spi_device *spidev)
{
}
EXPORT_SYMBOL(mt_spi_disable_master_clk);

MODULE_DESCRIPTION("Build-only ABI witness for stock spi-mt65xx master clock exports");
MODULE_LICENSE("GPL v2");
