/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Small pointer<->handle database used for supplicant-allocated shared memory.
 * Stock tkcore_drv.ko keeps it inside the backend private area at offset 0x90
 * (16 bytes: pointer array + array size).
 */
#ifndef TKCORE_DRV_HANDLE_H
#define TKCORE_DRV_HANDLE_H

#include <linux/types.h>

/*
 * Stock layout (handle_get/handle_put/handle_lookup all use
 * "ldr w9,[db,#0x8]"): a pointer array plus a 32-bit capacity.
 */
struct handle_db {
	void **ptrs;
	u32 max_ptrs;
};

#define HANDLE_DB_INITIALIZER { NULL, 0 }

void handle_db_destroy(struct handle_db *db);
int handle_get(struct handle_db *db, void *ptr);
void *handle_put(struct handle_db *db, int handle);
void *handle_lookup(struct handle_db *db, int handle);

#endif /* TKCORE_DRV_HANDLE_H */
