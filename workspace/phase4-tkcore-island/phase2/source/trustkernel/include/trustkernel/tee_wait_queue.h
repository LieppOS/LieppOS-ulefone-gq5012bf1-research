/* SPDX-License-Identifier: GPL-2.0 */
/*
 * TrustKernel TKCore - wait-queue island header.
 *
 * The private object is PROVEN_EXACT at 0x40 bytes with a mutex at 0x00 and a
 * list_head at 0x30 (recovered in kernel/phase4-tkcore-provider-abi.md).  All
 * four exported entry points already reproduce their HISTORICAL stock CRCs
 * naturally from this definition, so nothing here may be renamed.
 */
#ifndef __TRUSTKERNEL_TEE_WAIT_QUEUE_H__
#define __TRUSTKERNEL_TEE_WAIT_QUEUE_H__

#include <linux/list.h>
#include <linux/mutex.h>
#include <linux/types.h>

/**
 * struct tee_wait_queue_private - head of the per-TEE wait-queue list.
 *
 * PROVEN_EXACT: sizeof == 0x40, mutex @0x00, list_head @0x30.
 *
 * Measured against exact GKI ab/12901745, struct mutex is 0x30 bytes, so the
 * proven anchors are satisfied by mutex + list_head with NO padding at all.
 * That exact fit is independent corroboration of the recovered layout.
 */
struct tee_wait_queue_private {
	struct mutex mu;	/* 0x00, 0x30 bytes on this kernel */
	struct list_head db;	/* 0x30 */
};

void tee_wait_queue_init(struct tee_wait_queue_private *priv);
void tee_wait_queue_exit(struct tee_wait_queue_private *priv);
void tee_wait_queue_sleep(struct device *dev,
			  struct tee_wait_queue_private *priv, u32 key);
void tee_wait_queue_wakeup(struct device *dev,
			   struct tee_wait_queue_private *priv, u32 key);

#endif /* __TRUSTKERNEL_TEE_WAIT_QUEUE_H__ */
