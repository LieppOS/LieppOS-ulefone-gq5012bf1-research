/* SPDX-License-Identifier: GPL-2.0 */
/*
 * TrustKernel TKCore - secure-SPI proxy island header.
 *
 * All three prototypes are PROVEN_EXACT: they already reproduce their
 * HISTORICAL stock CRCs naturally, and tee_spi_transfer additionally matches
 * the stock KCFI type id 0xffeb18b3 required by microarray_fp_tee.
 *
 * Do not change these signatures: microarray_fp_tee is frozen and consumes
 * tee_spi_transfer with stock CRC 0x184ce7da.
 */
#ifndef __TRUSTKERNEL_TEE_SPI_H__
#define __TRUSTKERNEL_TEE_SPI_H__

#include <linux/types.h>

/*
 * Configure the SPI pad selection for the secure world.
 * PROVEN_EXACT prototype (historical CRC natural).
 */
int tee_spi_cfg_padsel(uint32_t spi_padsel);

/*
 * Perform a secure SPI transfer on behalf of a normal-world driver.
 *
 * PROVEN_EXACT prototype; stock KCFI 0xffeb18b3, stock CRC 0x184ce7da.
 * microarray_fp_tee is the acceptance consumer.
 */
int tee_spi_transfer(void *conf, uint32_t conf_size,
		     void *txbuf, void *rxbuf, uint32_t len);

/*
 * Tear the secure SPI path down.
 * PROVEN_EXACT prototype (historical CRC natural).
 */
int tee_spi_transfer_disable(bool disable);

#endif /* __TRUSTKERNEL_TEE_SPI_H__ */
