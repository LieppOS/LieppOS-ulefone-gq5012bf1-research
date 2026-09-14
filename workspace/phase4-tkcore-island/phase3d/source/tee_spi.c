// SPDX-License-Identifier: GPL-2.0
/*
 * TrustKernel TKCore - secure-SPI proxy.
 *
 * Reconstructed from stock tkcore.ko:
 *
 *	tee_spi_cfg_padsel		0x90c8, 332 bytes, KCFI 0xab53c5c9
 *	tee_spi_transfer		0x9218, 452 bytes, KCFI 0xffeb18b3
 *	tee_spi_transfer_disable	0x93e0, 300 bytes, KCFI 0x36b1c5a6
 *
 * These are NOT hardware SPI drivers.  Each one is a self-contained TEE client
 * that opens its own context and session to a single SPI proxy TA, invokes one
 * command, and tears the session down again.  Stock touches no pinctrl, no SPI
 * controller, no spi_message/spi_transfer, no clock and no lock, and keeps no
 * mutable global state whatsoever - the only shared datum is the constant TA
 * UUID below.  See kernel/phase4-tkcore-secure-spi-state.md.
 *
 * The three commands multiplexed onto that one TA are:
 *
 *	0	transfer		paramTypes 0x75
 *	1	transfer_disable	paramTypes 0x00
 *	2	cfg_padsel		paramTypes 0x01
 *
 * The session boilerplate is deliberately repeated in each function rather
 * than factored into a helper, because stock repeats it too.
 */

#include <linux/errno.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/printk.h>
#include <linux/string.h>
#include <linux/types.h>

#include <trustkernel/tee_client_api.h>
#include <trustkernel/tee_spi.h>

/*
 * TrustKernel secure-SPI proxy TA: 966d3f7c-04ef-1beb-08b7-57f37a6d87f9.
 * Recovered verbatim from stock .data+0x1f8 and identical to the UUID the
 * frozen microarray_fp_tee reconstruction uses for chip identification.
 *
 * Deliberately not "const": stock keeps this object in .data, not .rodata.
 */
static TEEC_UUID tee_spi_ta_uuid = {
	0x966d3f7c, 0x04ef, 0x1beb,
	{ 0x08, 0xb7, 0x57, 0xf3, 0x7a, 0x6d, 0x87, 0xf9 }
};

/* Command IDs understood by the proxy TA. */
#define TEE_SPI_CMD_TRANSFER		0
#define TEE_SPI_CMD_TRANSFER_DISABLE	1
#define TEE_SPI_CMD_CFG_PADSEL		2

int tee_spi_cfg_padsel(uint32_t spi_padsel)
{
	TEEC_Context context;
	TEEC_Session session;
	TEEC_Operation operation;
	uint32_t return_origin = 0;
	TEEC_Result ret;

	pr_info("tkcore: padsel=0x%x\n", spi_padsel);

	memset(&context, 0, sizeof(context));
	/* Stock clears the session identifier with a 32-bit store. */
	session.fd = 0;
	memset(&operation, 0, sizeof(operation));

	ret = TEEC_InitializeContext(NULL, &context);
	if (ret) {
		pr_err("tkcore: TEEC_InitializeContext() failed with 0x%08x\n",
		       ret);
		return ret;
	}

	ret = TEEC_OpenSession(&context, &session, &tee_spi_ta_uuid,
			       0, NULL, NULL, &return_origin);
	if (ret) {
		pr_err("tkcore: TEEC_OpenSession failed with 0x%x returnOrigun: %u\n",
		       ret, return_origin);
		goto out_finalize;
	}

	operation.paramTypes = TEEC_PARAM_TYPES(TEEC_VALUE_INPUT, TEEC_NONE,
						TEEC_NONE, TEEC_NONE);
	operation.params[0].value.a = spi_padsel;

	ret = TEEC_InvokeCommand(&session, TEE_SPI_CMD_CFG_PADSEL,
				 &operation, &return_origin);
	if (ret)
		pr_err("tkcore: TEEC_InvokeCommand() failed with 0x%08x returnOrigin: %u\n",
		       ret, return_origin);

	TEEC_CloseSession(&session);
out_finalize:
	TEEC_FinalizeContext(&context);
	return ret;
}
EXPORT_SYMBOL(tee_spi_cfg_padsel);

int tee_spi_transfer(void *conf, uint32_t conf_size,
		     void *txbuf, void *rxbuf, uint32_t len)
{
	TEEC_Context context;
	TEEC_Session session;
	TEEC_Operation operation;
	uint32_t return_origin = 0;
	TEEC_Result ret;

	pr_info("tkcore: conf=%p conf_size=%u inbuf=%p outbuf=%p size=%u\n",
		conf, conf_size, txbuf, rxbuf, len);

	if (!conf || !txbuf || !rxbuf) {
		pr_err("tkcore: Bad parameters NULL buf\n");
		return -EINVAL;
	}

	if (!len) {
		pr_err("tkcore: zero buf size\n");
		return -EINVAL;
	}

	memset(&context, 0, sizeof(context));
	session.fd = 0;
	memset(&operation, 0, sizeof(operation));

	/*
	 * The TA performs an in-place full-duplex exchange on the second
	 * parameter, so the caller's TX bytes are staged into the RX buffer
	 * before the call and overwritten by the RX bytes on return.
	 */
	memcpy(rxbuf, txbuf, len);

	ret = TEEC_InitializeContext(NULL, &context);
	if (ret) {
		pr_err("tkcore: TEEC_InitializeContext() failed with 0x%08x\n",
		       ret);
		return ret;
	}

	ret = TEEC_OpenSession(&context, &session, &tee_spi_ta_uuid,
			       0, NULL, NULL, &return_origin);
	if (ret) {
		pr_err("tkcore: TEEC_OpenSession failed with 0x%x returnOrigun: %u\n",
		       ret, return_origin);
		goto out_finalize;
	}

	operation.paramTypes = TEEC_PARAM_TYPES(TEEC_MEMREF_TEMP_INPUT,
						TEEC_MEMREF_TEMP_INOUT,
						TEEC_NONE, TEEC_NONE);
	operation.params[0].tmpref.buffer = conf;
	operation.params[0].tmpref.size = conf_size;
	operation.params[1].tmpref.buffer = rxbuf;
	operation.params[1].tmpref.size = len;

	ret = TEEC_InvokeCommand(&session, TEE_SPI_CMD_TRANSFER,
				 &operation, &return_origin);
	if (ret)
		pr_err("tkcore: TEEC_InvokeCommand() failed with 0x%08x returnOrigin: %u\n",
		       ret, return_origin);

	TEEC_CloseSession(&session);
out_finalize:
	TEEC_FinalizeContext(&context);
	return ret;
}
EXPORT_SYMBOL(tee_spi_transfer);

int tee_spi_transfer_disable(void)
{
	TEEC_Context context;
	TEEC_Session session;
	TEEC_Operation operation;
	uint32_t return_origin = 0;
	TEEC_Result ret;

	memset(&context, 0, sizeof(context));
	session.fd = 0;
	memset(&operation, 0, sizeof(operation));

	ret = TEEC_InitializeContext(NULL, &context);
	if (ret) {
		pr_err("tkcore: TEEC_InitializeContext() failed with 0x%08x\n",
		       ret);
		return ret;
	}

	ret = TEEC_OpenSession(&context, &session, &tee_spi_ta_uuid,
			       0, NULL, NULL, &return_origin);
	if (ret) {
		pr_err("tkcore: TEEC_OpenSession failed with 0x%x returnOrigun: %u\n",
		       ret, return_origin);
		goto out_finalize;
	}

	operation.paramTypes = TEEC_PARAM_TYPES(TEEC_NONE, TEEC_NONE,
						TEEC_NONE, TEEC_NONE);

	ret = TEEC_InvokeCommand(&session, TEE_SPI_CMD_TRANSFER_DISABLE,
				 &operation, &return_origin);
	if (ret)
		pr_err("tkcore: TEEC_InvokeCommand() failed with 0x%08x returnOrigin: %u\n",
		       ret, return_origin);

	TEEC_CloseSession(&session);
out_finalize:
	TEEC_FinalizeContext(&context);
	return ret;
}
EXPORT_SYMBOL(tee_spi_transfer_disable);
