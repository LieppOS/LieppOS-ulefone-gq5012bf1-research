// SPDX-License-Identifier: GPL-2.0
/*
 * Build-only provider-ABI witness for the GQ5012BF1 stock tkcore.ko
 * (TrustKernel TKCore TEEC v1.0, vermagic 6.1.115-android14-11-g945dff7bc1bf).
 *
 * WHAT THIS IS
 * ------------
 * tkcore.ko exports 25 plain EXPORT_SYMBOL entries that three stock consumers
 * bind against (tkcore_drv.ko: 11, tmem_ffa.ko: 7, microarray_fp_tee.ko: 1).
 * This file re-declares the subset of that ABI whose genksyms type graph is
 * fully recoverable from the stock binary (scalar/opaque parameters and the
 * GlobalPlatform TEEC_* value types), so that modpost/genksyms derive the
 * MODVERSION CRCs *naturally* from C.  No CRC patching, no copied __versions,
 * no fabricated symvers.
 *
 * The 14 exports below reproduce the stock CRCs exactly:
 *
 *   tee_map_cached_shm        0x6a4e508b   tee_unmap_cached_shm     0xd793261b
 *   tee_spi_cfg_padsel        0x56729869   tee_spi_transfer         0x184ce7da
 *   tee_spi_transfer_disable  0xadb9b21c   tee_clkmgr_handle        0x6913f6b2
 *   tee_clkmgr_register       0x7a827d74   tee_wait_queue_init      0x03c4c343
 *   tee_wait_queue_exit       0xe773ba45   tee_wait_queue_sleep     0xcca24950
 *   tee_wait_queue_wakeup     0xe2de5bad   TEEC_CloseSession        0xcb193c37
 *   TEEC_InvokeCommand        0x202b681e   TEEC_ReleaseSharedMemory 0xc4d15e1c
 *
 * The remaining 11 stock exports (TEEC_InitializeContext, TEEC_FinalizeContext,
 * TEEC_OpenSession, TEEC_RegisterSharedMemory, TEEC_AllocateSharedMemory,
 * tee_core_alloc, tee_core_add, tee_core_del, tee_core_free, __tee_get,
 * tee_supp_cmd) take `struct tee *` / `struct tee_context *` (TEEC_Context
 * embeds a `struct tee_context *`).  genksyms expands those pointed-to struct
 * definitions in full, so their CRCs encode every member *name* of TrustKernel's
 * private struct tee (312 bytes) and struct tee_context (208 bytes).  Member
 * names are not present in the stripped stock binary and no public source
 * carries them, so those CRCs cannot be regenerated naturally.  They are
 * classified PROVIDER_ABI_BLOCKED; see
 * kernel/phase4-tkcore-provider-abi.md in the research repo.
 *
 * Prototypes were recovered from the stock binary itself: parameter/return
 * types were confirmed against the stock Clang 17.0.2 KCFI type hashes
 * (e.g. tee_spi_transfer 0xffeb18b3, tee_clkmgr_register 0xe70e59df) and the
 * struct layouts against stock instruction offsets and memset sizes
 * (TEEC_Context 0x108, TEEC_Operation 0x118, TEEC_SharedMemory 0x28,
 * tee_wait_queue_private mutex@0x0 + list_head@0x30).
 *
 * WHAT THIS IS NOT
 * ----------------
 * This module contains no TEE behaviour: every entry point fails closed.  The
 * real provider is the stock tkcore.ko, whose secure-world transport lives in
 * tkcore_drv.ko/ffa_v10.ko and is deliberately not modelled here.  This module
 * must never be installed, loaded, or shipped as a TEE provider.
 */
#include <linux/module.h>
#include <linux/types.h>
#include <linux/device.h>

#include "include/tk_tee_client_api.h"
#include "include/tk_tee_wait_queue.h"

/* ---- GlobalPlatform TEEC entry points with no struct tee_context edge ---- */

void TEEC_CloseSession(struct TEEC_Session *session)
{
}
EXPORT_SYMBOL(TEEC_CloseSession);

TEEC_Result TEEC_InvokeCommand(struct TEEC_Session *session, uint32_t commandID,
			       struct TEEC_Operation *operation,
			       uint32_t *returnOrigin)
{
	if (returnOrigin)
		*returnOrigin = TEEC_ORIGIN_API;
	return TEEC_ERROR_NOT_SUPPORTED;
}
EXPORT_SYMBOL(TEEC_InvokeCommand);

void TEEC_ReleaseSharedMemory(struct TEEC_SharedMemory *sharedMemory)
{
}
EXPORT_SYMBOL(TEEC_ReleaseSharedMemory);

/* ---- cached shared-memory mapping helpers (tkcore_drv edge) ---- */

void *tee_map_cached_shm(unsigned long paddr, size_t size)
{
	return NULL;
}
EXPORT_SYMBOL(tee_map_cached_shm);

void tee_unmap_cached_shm(void *vaddr)
{
}
EXPORT_SYMBOL(tee_unmap_cached_shm);

/* ---- RPC wait queue (tkcore_drv edge) ---- */

void tee_wait_queue_init(struct tee_wait_queue_private *priv)
{
}
EXPORT_SYMBOL(tee_wait_queue_init);

void tee_wait_queue_exit(struct tee_wait_queue_private *priv)
{
}
EXPORT_SYMBOL(tee_wait_queue_exit);

void tee_wait_queue_sleep(struct device *dev,
			  struct tee_wait_queue_private *priv, u32 key)
{
}
EXPORT_SYMBOL(tee_wait_queue_sleep);

void tee_wait_queue_wakeup(struct device *dev,
			   struct tee_wait_queue_private *priv, u32 key)
{
}
EXPORT_SYMBOL(tee_wait_queue_wakeup);

/* ---- secure peripheral clock manager (tkcore_drv edge) ---- */

int tee_clkmgr_handle(uint32_t id, uint32_t command)
{
	return -ENODEV;
}
EXPORT_SYMBOL(tee_clkmgr_handle);

int tee_clkmgr_register(const char *name, int id, void *enable, void *disable,
			void *arg1, void *arg2, void *arg3, size_t num_args)
{
	return -ENODEV;
}
EXPORT_SYMBOL(tee_clkmgr_register);

/* ---- secure SPI proxy (microarray_fp_tee edge) ---- */

int tee_spi_cfg_padsel(uint32_t padsel)
{
	return -ENODEV;
}
EXPORT_SYMBOL(tee_spi_cfg_padsel);

int tee_spi_transfer(void *conf, uint32_t conf_size, void *txbuf, void *rxbuf,
		     uint32_t len)
{
	return -ENODEV;
}
EXPORT_SYMBOL(tee_spi_transfer);

int tee_spi_transfer_disable(void)
{
	return -ENODEV;
}
EXPORT_SYMBOL(tee_spi_transfer_disable);

MODULE_DESCRIPTION("Build-only provider-ABI witness for stock tkcore.ko exports");
MODULE_AUTHOR("LieppOS GQ5012BF1 research");
MODULE_LICENSE("GPL v2");
