/* SPDX-License-Identifier: GPL-2.0 */
/*
 * TrustKernel TKCore - shared-memory island header.
 *
 * tee_map_cached_shm / tee_unmap_cached_shm already reproduce their
 * HISTORICAL stock CRCs naturally and are consumed by tkcore_drv, so their
 * prototypes are PROVEN_EXACT and frozen.
 */
#ifndef __TRUSTKERNEL_TEE_SHM_H__
#define __TRUSTKERNEL_TEE_SHM_H__

#include <linux/types.h>

struct tee;
struct tee_shm;
struct tee_context;
struct tee_shm_io;

/*
 * Map a physically contiguous secure/shared region into the kernel as cached
 * memory.  PROVEN_EXACT prototype (historical CRC natural, tkcore_drv edge).
 */
void *tee_map_cached_shm(unsigned long pa, size_t len);

/*
 * Undo tee_map_cached_shm.
 * PROVEN_EXACT prototype (historical CRC natural).
 */
void tee_unmap_cached_shm(void *va);

/* Island-internal shared-memory helpers (not exported by stock tkcore). */
struct tee_shm *tkcore_alloc_shm(struct tee *tee, size_t size, u32 flags);
void tkcore_shm_free(struct tee_shm *shm);
struct tee_shm *tkcore_shm_get(struct tee_context *ctx, TEEC_SharedMemory *c_shm,
			       size_t size, int offset);
void tkcore_shm_put(struct tee_context *ctx, struct tee_shm *shm);

#endif /* __TRUSTKERNEL_TEE_SHM_H__ */
