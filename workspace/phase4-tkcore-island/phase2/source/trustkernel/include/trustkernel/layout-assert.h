/* SPDX-License-Identifier: GPL-2.0 */
/*
 * TrustKernel island layout assertions.
 *
 * Every assertion below encodes an offset or size that was RECOVERED FROM THE
 * STOCK GQ5012BF1 ELFs.  This header is included by the island build, so a
 * layout regression breaks the build instead of silently shipping a wrong
 * type graph.
 *
 * Anchors marked PROVEN come from:
 *   kernel/phase4-tkcore-provider-abi.md      (struct tee, tee_context, wq)
 *   kernel/phase4-tmem-ffa-trustkernel-type-evidence.md  (TEEC_*)
 *   kernel/phase4-trustkernel-abi-island-header-plan.md
 */
#ifndef __TRUSTKERNEL_LAYOUT_ASSERT_H__
#define __TRUSTKERNEL_LAYOUT_ASSERT_H__

#include <linux/stddef.h>
#include <trustkernel/tee_client_api.h>
#include <trustkernel/tee_core.h>
#include <trustkernel/tee_wait_queue.h>

#define TK_ASSERT_SIZE(type, want) \
	static_assert(sizeof(type) == (want), \
		      #type " size must be " #want)
#define TK_ASSERT_OFF(type, member, want) \
	static_assert(offsetof(type, member) == (want), \
		      #type "." #member " must be at " #want)

/* ---- GlobalPlatform client types: PROVEN_EXACT from tmem_ffa ---------- */
TK_ASSERT_SIZE(TEEC_Context, 0x108);
TK_ASSERT_SIZE(TEEC_Session, 8);
TK_ASSERT_SIZE(TEEC_SharedMemory, 0x28);
TK_ASSERT_SIZE(TEEC_Operation, 0x118);
TK_ASSERT_SIZE(TEEC_UUID, 16);

TK_ASSERT_OFF(TEEC_SharedMemory, size, 8);
TK_ASSERT_OFF(TEEC_SharedMemory, flags, 0x10);
TK_ASSERT_OFF(TEEC_Operation, paramTypes, 4);
TK_ASSERT_OFF(TEEC_Operation, params, 8);

/* ---- struct tee: PROVEN anchors, total 0x138 -------------------------- */
TK_ASSERT_SIZE(struct tee, 0x138);
TK_ASSERT_OFF(struct tee, name, 0x20);
TK_ASSERT_OFF(struct tee, id, 0x60);
TK_ASSERT_OFF(struct tee, priv, 0x88);
TK_ASSERT_OFF(struct tee, ops, 0x90);
TK_ASSERT_OFF(struct tee, dev, 0x98);
TK_ASSERT_OFF(struct tee, list_misc, 0xa0);
TK_ASSERT_OFF(struct tee, list_ctx, 0xd8);
TK_ASSERT_OFF(struct tee, list_rpc_shm, 0xe8);
TK_ASSERT_OFF(struct tee, lock, 0xf8);
TK_ASSERT_OFF(struct tee, state, 0x128);
TK_ASSERT_OFF(struct tee, shm_flags, 0x12c);

/* ---- struct tee_context: PROVEN anchors, total 0xd0 ------------------- */
TK_ASSERT_SIZE(struct tee_context, 0xd0);
TK_ASSERT_OFF(struct tee_context, name, 8);
TK_ASSERT_OFF(struct tee_context, tgid, 0x88);
TK_ASSERT_OFF(struct tee_context, usr_client, 0x8c);
TK_ASSERT_OFF(struct tee_context, entry, 0x90);
TK_ASSERT_OFF(struct tee_context, list_sess, 0xa0);
TK_ASSERT_OFF(struct tee_context, list_shm, 0xb0);
TK_ASSERT_OFF(struct tee_context, refcount, 0xc0);

/* ---- wait-queue private object: PROVEN 0x40 --------------------------- */
TK_ASSERT_SIZE(struct tee_wait_queue_private, 0x40);
TK_ASSERT_OFF(struct tee_wait_queue_private, db, 0x30);

#endif /* __TRUSTKERNEL_LAYOUT_ASSERT_H__ */
