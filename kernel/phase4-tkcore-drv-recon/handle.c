// SPDX-License-Identifier: GPL-2.0
/*
 * Pointer<->handle database for tkcore_drv.
 *
 * Reconstruction of the stock handle_db_destroy()/handle_get()/handle_put()/
 * handle_lookup() quartet (stock .text 0x35c0..0x3734); the algorithm is the
 * classic OP-TEE armtz/handle.c one that TrustKernel forked, with the stock
 * growth step of 4 entries per krealloc() round.
 */
#include <linux/slab.h>
#include <linux/string.h>

#include "handle.h"

/*
 * Stock growth policy, read straight out of handle_get() (.text 0x35fc):
 *     w9  = max_ptrs << 1
 *     w22 = (max_ptrs == 0) ? 4 : w9
 *     krealloc(ptrs, w22 * 8, 0xcc0)   // 0xcc0 = GFP_KERNEL
 *     memset(ptrs + max_ptrs, 0, (w22 - max_ptrs) * 8)
 * i.e. start at 4 entries and double from there.
 */
#define HANDLE_DB_INITIAL	4

void handle_db_destroy(struct handle_db *db)
{
	if (db) {
		kfree(db->ptrs);
		db->ptrs = NULL;
		db->max_ptrs = 0;
	}
}

int handle_get(struct handle_db *db, void *ptr)
{
	u32 old_max;
	u32 new_max;
	void **p;
	u32 n;

	if (!db || !ptr)
		return -1;

	old_max = db->max_ptrs;

	/* Reuse a free slot if there is one. */
	for (n = 0; n < old_max; n++) {
		if (!db->ptrs[n]) {
			db->ptrs[n] = ptr;
			return n;
		}
	}

	/* No free slot: double the array (4 entries for the first grow). */
	new_max = old_max ? old_max * 2 : HANDLE_DB_INITIAL;
	p = krealloc(db->ptrs, (size_t)new_max * sizeof(void *), GFP_KERNEL);
	if (!p)
		return -1;

	db->ptrs = p;
	memset(db->ptrs + old_max, 0,
	       (size_t)(new_max - old_max) * sizeof(void *));
	db->max_ptrs = new_max;
	db->ptrs[old_max] = ptr;

	return old_max;
}

void *handle_put(struct handle_db *db, int handle)
{
	void *p;

	if (!db || handle < 0 || (u32)handle >= db->max_ptrs)
		return NULL;

	p = db->ptrs[handle];
	db->ptrs[handle] = NULL;

	return p;
}

void *handle_lookup(struct handle_db *db, int handle)
{
	if (!db || handle < 0 || (u32)handle >= db->max_ptrs)
		return NULL;

	return db->ptrs[handle];
}
