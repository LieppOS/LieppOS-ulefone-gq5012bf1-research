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

/*
 * Operation selector carried in the second argument of tee_clkmgr_handle().
 *
 * Stock polarity, proven at tkcore.ko 0x8dec..0x8df8:
 *
 *	tst  w20, #0x1
 *	csel x9, x10, x9, eq	; x9 = rec+0x08 (enable), x10 = rec+0x10 (disable)
 *
 * so bit 0 SET selects ->enable and CLEAR selects ->disable.  Earlier
 * revisions of this header had these two constants inverted; they had zero
 * uses, so nothing was ever built against the wrong values.
 */
#define TEE_CLKMGR_OP_DISABLE	0
#define TEE_CLKMGR_OP_ENABLE	1

/*
 * Dispatch one clock request coming from the secure world.
 * PROVEN_EXACT prototype (historical CRC natural).
 */
int tee_clkmgr_handle(uint32_t cmd, uint32_t val);

/*
 * Register one token and its untyped dispatch callbacks/arguments.
 *
 * PROVEN_EXACT from stock KCFI 0xe70e59df and the eight-register call site in
 * plat_register_spi_clk().  The stock dispatcher supports callbacks taking
 * zero through three pointer arguments; callback typing is deliberately
 * erased at this registration boundary.
 */
int tee_clkmgr_register(const char *name, int index,
			void *enable, void *disable,
			void *arg0, void *arg1, void *arg2,
			size_t argnum);

#endif /* __TRUSTKERNEL_TEE_CLKMGR_H__ */
