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
#include <linux/dma-buf.h>
#include <linux/mm_types.h>
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
TK_ASSERT_OFF(struct tee, version_major, 0x64);
TK_ASSERT_OFF(struct tee, version_minor, 0x68);
TK_ASSERT_OFF(struct tee, version_patch, 0x6c);
TK_ASSERT_OFF(struct tee, log_shm, 0x70);
TK_ASSERT_OFF(struct tee, log_shm_len, 0x78);
TK_ASSERT_OFF(struct tee, log_irq, 0x80);
TK_ASSERT_OFF(struct tee, priv, 0x88);
TK_ASSERT_OFF(struct tee, ops, 0x90);
TK_ASSERT_OFF(struct tee, dev, 0x98);
TK_ASSERT_OFF(struct tee, list_misc, 0xa0);
TK_ASSERT_OFF(struct tee, rpc, 0xb0);
TK_ASSERT_OFF(struct tee, refcount, 0xb8);
TK_ASSERT_OFF(struct tee, max_refcount, 0xbc);
TK_ASSERT_OFF(struct tee, stats, 0xc0);
TK_ASSERT_OFF(struct tee, list_ctx, 0xd8);
TK_ASSERT_OFF(struct tee, list_rpc_shm, 0xe8);
TK_ASSERT_OFF(struct tee, lock, 0xf8);
TK_ASSERT_OFF(struct tee, state, 0x128);
TK_ASSERT_OFF(struct tee, shm_flags, 0x12c);

/* ---- misc-device record + descriptor: PROVEN from tee_core_add ------- */
TK_ASSERT_SIZE(struct tee_misc_dev, 0x68);
TK_ASSERT_OFF(struct tee_misc_dev, miscdev, 0);
TK_ASSERT_OFF(struct tee_misc_dev, desc, 0x50);
TK_ASSERT_OFF(struct tee_misc_dev, node, 0x58);
TK_ASSERT_SIZE(struct tee_device_desc, 0x28);
TK_ASSERT_OFF(struct tee_device_desc, fops, 8);
TK_ASSERT_OFF(struct tee_device_desc, affinity, 0x10);
TK_ASSERT_OFF(struct tee_device_desc, supplicant, 0x18);
TK_ASSERT_OFF(struct tee_device_desc, name_lookup, 0x19);
TK_ASSERT_OFF(struct tee_device_desc, available, 0x20);

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

/* ---- Phase 3B: shared memory -----------------------------------------
 * Every anchor below is read from the stock ELF; see
 * kernel/phase4-tkcore-shm-layout.md for the per-field evidence.
 */

/* struct tee_shm: PROVEN 0x68 (kmalloc size in tkcore_shm_get) */
TK_ASSERT_SIZE(struct tee_shm, 0x68);
TK_ASSERT_OFF(struct tee_shm, entry, 0x00);
TK_ASSERT_OFF(struct tee_shm, ctx, 0x10);
TK_ASSERT_OFF(struct tee_shm, tee, 0x18);
TK_ASSERT_OFF(struct tee_shm, dev, 0x20);
TK_ASSERT_OFF(struct tee_shm, size_req, 0x28);
TK_ASSERT_OFF(struct tee_shm, size_alloc, 0x30);
TK_ASSERT_OFF(struct tee_shm, flags, 0x38);
TK_ASSERT_OFF(struct tee_shm, kaddr, 0x40);
TK_ASSERT_OFF(struct tee_shm, paddr, 0x48);
TK_ASSERT_OFF(struct tee_shm, sgt, 0x50);
TK_ASSERT_OFF(struct tee_shm, sdb, 0x60);

/* TEEC_SharedMemory handle/registered anchors (size/flags asserted above) */
TK_ASSERT_OFF(TEEC_SharedMemory, d, 0x18);
TK_ASSERT_OFF(TEEC_SharedMemory, registered, 0x20);

/*
 * struct tee_shm_io is island-local (tkcore/tee_ioc.h) and therefore not
 * visible here; its anchors are asserted in tee_shm.c instead.
 */

/* struct tee_shm_dma_buf: imported dma-buf record, PROVEN 0x18 */
TK_ASSERT_SIZE(struct tee_shm_dma_buf, 0x18);
TK_ASSERT_OFF(struct tee_shm_dma_buf, attach, 0x00);
TK_ASSERT_OFF(struct tee_shm_dma_buf, sgt, 0x08);
TK_ASSERT_OFF(struct tee_shm_dma_buf, tee_allocated, 0x10);

/* Foreign GKI layouts the stock SHM code depends on. */
TK_ASSERT_OFF(struct dma_buf, size, 0x00);
TK_ASSERT_OFF(struct dma_buf, ops, 0x20);
TK_ASSERT_OFF(struct dma_buf, priv, 0xa0);
TK_ASSERT_OFF(struct dma_buf_attachment, dmabuf, 0x00);
TK_ASSERT_OFF(struct dma_buf_attachment, dev, 0x08);
TK_ASSERT_OFF(struct dma_buf_attachment, priv, 0x40);
TK_ASSERT_OFF(struct vm_area_struct, vm_page_prot, 0x18);
TK_ASSERT_OFF(struct vm_area_struct, vm_private_data, 0x90);

/* dma_buf_ops slots consumed by tee_static_shm_dma_buf_ops. */
TK_ASSERT_OFF(struct dma_buf_ops, attach, 0x08);
TK_ASSERT_OFF(struct dma_buf_ops, detach, 0x10);
TK_ASSERT_OFF(struct dma_buf_ops, map_dma_buf, 0x28);
TK_ASSERT_OFF(struct dma_buf_ops, unmap_dma_buf, 0x30);
TK_ASSERT_OFF(struct dma_buf_ops, release, 0x38);
TK_ASSERT_OFF(struct dma_buf_ops, mmap, 0x60);

#endif /* __TRUSTKERNEL_LAYOUT_ASSERT_H__ */
