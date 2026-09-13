/* SPDX-License-Identifier: GPL-2.0 */
/*
 * TrustKernel TKCore - clock-manager island header.
 *
 * Both exported prototypes are PROVEN_EXACT: they already reproduce their
 * HISTORICAL stock CRCs naturally, so neither may be respelled.
 *
 * The clock manager lets the secure world ask the normal world to enable or
 * disable a platform clock by index; tkcore keeps a small registration table
 * and dispatches through it.
 */
#ifndef __TRUSTKERNEL_TEE_CLKMGR_H__
#define __TRUSTKERNEL_TEE_CLKMGR_H__

#include <linux/types.h>

/* Operation selectors carried in the clkmgr handle word. */
#define TEE_CLKMGR_OP_ENABLE	0
#define TEE_CLKMGR_OP_DISABLE	1

/*
 * Dispatch one clock request coming from the secure world.
 * PROVEN_EXACT prototype (historical CRC natural).
 */
int tee_clkmgr_handle(uint32_t cmd, uint32_t val);

/*
 * Register one clock under a name/index with enable and disable callbacks.
 * PROVEN_EXACT prototype (historical CRC natural).
 */
int tee_clkmgr_register(const char *name, uint32_t index, void *priv,
			int (*enable)(void *priv, uint32_t on),
			uint32_t mask, uint32_t shift);

#endif /* __TRUSTKERNEL_TEE_CLKMGR_H__ */
