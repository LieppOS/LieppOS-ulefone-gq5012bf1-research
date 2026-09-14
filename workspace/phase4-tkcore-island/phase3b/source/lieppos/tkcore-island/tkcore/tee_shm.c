/*
 * Copyright (c) 2014, STMicroelectronics International N.V.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License Version 2 as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 */
#include <linux/slab.h>
#include <linux/types.h>
#include <linux/dma-buf.h>
#include <linux/hugetlb.h>
#include <linux/io.h>
#include <asm/memory.h>
#include <asm/pgtable.h>

#include <linux/sched.h>
#include <linux/mm.h>

#include "tee_core_priv.h"
#include "tee_shm.h"

#define INMSG() dev_dbg(_DEV(tee), "%s: >\n", __func__)
#define OUTMSG(val) dev_dbg(_DEV(tee), "%s: < %ld\n", __func__, (long)val)
#define OUTMSGX(val) dev_dbg(_DEV(tee), "%s: < %08x\n",\
		__func__, (unsigned int)(long)val)

/*
 * The donor left a commented-out size assertion here claiming
 * sizeof(TEEC_SharedMemory) == sizeof(struct tee_shm).  That premise is
 * false against stock - they are 0x28 and 0x68 respectively - and the intent
 * is now served properly by the build-enforced anchors in
 * trustkernel/layout-assert.h plus the static_asserts below.
 */
struct tee_shm_attach {
	struct sg_table sgt;
	enum dma_data_direction dir;
	bool is_mapped;
};

/*
 * Phase-3B layout anchors that are island-local and therefore cannot live in
 * trustkernel/layout-assert.h.  Evidence: kernel/phase4-tkcore-shm-layout.md.
 *
 * struct tee_shm_io carries the allocated object through its offset-0 union
 * on the kernel-client path, which is why offset 0 is load-bearing.
 */
static_assert(sizeof(struct tee_shm_io) == 0x18,
	      "stock struct tee_shm_io is 0x18 bytes");
static_assert(offsetof(struct tee_shm_io, size) == 0x08,
	      "stock tee_shm_io.size is at +0x08");
static_assert(offsetof(struct tee_shm_io, flags) == 0x0c,
	      "stock tee_shm_io.flags is at +0x0c");
static_assert(offsetof(struct tee_shm_io, fd_shm) == 0x10,
	      "stock tee_shm_io.fd_shm is at +0x10");

/* Per-attachment record: stock devm_kmalloc size is 0x18, dir at +0x10. */
static_assert(sizeof(struct tee_shm_attach) == 0x18,
	      "stock per-attachment record is 0x18 bytes");
static_assert(offsetof(struct tee_shm_attach, dir) == 0x10,
	      "stock per-attachment dir is at +0x10");
static_assert(offsetof(struct tee_shm_attach, is_mapped) == 0x14,
	      "stock per-attachment is_mapped is at +0x14");

/*
 * sg_nents()
 *
 * Stock tkcore carries its own WEAK definition (56 bytes, .text) rather than
 * importing the kernel's exported one.  Reproducing that removes a non-stock
 * undefined import and restores a stock function; the algorithm is identical,
 * so no behaviour changes.  It is in Phase-3B scope only because
 * tkcore_shm_get() calls it directly.
 */
int __weak sg_nents(struct scatterlist *sg)
{
	int nents;

	for (nents = 0; sg; sg = sg_next(sg))
		nents++;

	return nents;
}

/*
 * tee_map_cached_shm() / tee_unmap_cached_shm()
 *
 * Exported to tkcore_drv.  These map a physically contiguous secure/shared
 * region into the kernel as CACHED memory; they own no object and take no
 * lock.
 *
 * Stock materialises the protection constant 0x0068000000000703, ORing 0x800
 * when arm64_use_ng_mappings is set.  Decoded that is
 *   PTE_TYPE_PAGE | PTE_AF | PTE_SHARED | PTE_WRITE | PTE_PXN | PTE_UXN
 *   | PTE_MAYBE_NG, with AttrIndx = MT_NORMAL
 * i.e. exactly PAGE_KERNEL - the runtime arm64_use_ng_mappings test is simply
 * the expansion of PTE_MAYBE_NG.  Writing pgprot_val(PAGE_KERNEL) reproduces
 * it without hardcoding a magic number.
 *
 * The fast path is __va(pa): stock computes (pa - memstart_addr) | PAGE_OFFSET.
 *
 * Ownership asymmetry, reproduced deliberately: the linear-map branch creates
 * no mapping, yet tee_unmap_cached_shm() calls iounmap() unconditionally.
 * That is safe because arm64's iounmap() ignores non-vmalloc addresses, and
 * it is what stock does; no guard stock lacks is added here.
 */
void *tee_map_cached_shm(unsigned long pa, size_t len)
{
	if (pfn_is_map_memory(__phys_to_pfn(pa)))
		return __va(pa);

	return ioremap_prot(pa, len, pgprot_val(PAGE_KERNEL));
}
EXPORT_SYMBOL(tee_map_cached_shm);

void tee_unmap_cached_shm(void *va)
{
	iounmap((volatile void __iomem *)va);
}
EXPORT_SYMBOL(tee_unmap_cached_shm);

struct tee_shm *tee_shm_alloc_from_rpc(struct tee *tee, size_t size)
{
	struct tee_shm *shm;

	INMSG();

	mutex_lock(&tee->lock);
	shm = tkcore_alloc_shm(tee, size, TEE_SHM_TEMP | TEE_SHM_FROM_RPC);
	if (IS_ERR_OR_NULL(shm)) {
		pr_err("%s: buffer allocation failed (%ld)\n",
			__func__, PTR_ERR(shm));
		goto out;
	}

	tee_inc_stats(&tee->stats[TEE_STATS_SHM_IDX]);
	list_add_tail(&shm->entry, &tee->list_rpc_shm);

	shm->ctx = NULL;

out:
	mutex_unlock(&tee->lock);
	OUTMSGX(shm);
	return shm;
}

void tee_shm_free_from_rpc(struct tee_shm *shm)
{
	struct tee *tee;

	if (shm == NULL)
		return;
	tee = shm->tee;
	mutex_lock(&tee->lock);
	if (shm->ctx == NULL) {
		tee_dec_stats(&shm->tee->stats[TEE_STATS_SHM_IDX]);
		list_del(&shm->entry);
	}

	tkcore_shm_free(shm);
	mutex_unlock(&tee->lock);
}

/*
 * Stock name is tkcore_alloc_shm (GLOBAL, not exported).  It is a thin
 * wrapper over the provider ops->alloc whose only independent responsibility
 * is building shm->sgt.
 *
 * Two stock behaviours are reproduced rather than "fixed":
 *
 *  1. shm->tee is assigned at the very END, on every path, guarded by
 *     !IS_ERR_OR_NULL(shm).  The donor assigned it immediately after the
 *     allocation, which writes through an error pointer on the failure path.
 *
 *  2. The failure paths return the offending page pointer cast to
 *     struct tee_shm *, not a uniform error code.
 *
 * Caller (tee_shm_alloc_io / tee_shm_alloc_from_rpc) already holds tee->lock,
 * which is why this function must not take it.
 */
struct tee_shm *tkcore_alloc_shm(struct tee *tee, size_t size, uint32_t flags)
{
	struct tee_shm *shm;
	unsigned long pfn;
	unsigned int nr_pages;
	struct page *page;
	int ret;

	shm = tee->ops->alloc(tee, size, flags);
	if (IS_ERR_OR_NULL(shm)) {
		pr_err("%s: allocation failed (s=%d,flags=0x%08x) err=%ld\n",
			__func__, (int)size, flags, PTR_ERR(shm));
		goto out;
	}

	pfn = shm->paddr >> PAGE_SHIFT;
	page = pfn_to_page(pfn);
	if (IS_ERR_OR_NULL(page)) {
		pr_err("%s: pfn_to_page(%lx) failed\n", __func__, pfn);
		tee->ops->free(shm);
		shm = (struct tee_shm *)page;
		goto out;
	}

	/* Stock describes exactly one page of PAGE_SIZE, whatever was asked. */
	nr_pages = 1;

	ret = sg_alloc_table_from_pages(&shm->sgt, &page,
			nr_pages, 0, nr_pages * PAGE_SIZE, GFP_KERNEL);
	/*
	 * IS_ERR_VALUE() casts through void * and is not valid on a plain int
	 * under -Werror,-Wint-to-void-pointer-cast.  sg_alloc_table_from_pages()
	 * returns 0 or a negative errno, so "ret < 0" is the exact equivalent.
	 */
	if (ret < 0) {
		pr_err("%s: sg_alloc_table_from_pages() failed\n", __func__);
		tee->ops->free(shm);
		shm = ERR_PTR(ret);
	}

out:
	if (!IS_ERR_OR_NULL(shm))
		shm->tee = tee;
	return shm;
}

/*
 * Stock name is tkcore_shm_free.  A NULL shm->tee is a BUG() in stock, not a
 * warning; the donor's second "shm->tee == NULL" test was dead code because
 * tee was already loaded from it.
 */
void tkcore_shm_free(struct tee_shm *shm)
{
	if (IS_ERR_OR_NULL(shm))
		return;

	if (!shm->tee) {
		BUG();
		return;
	}

	sg_free_table(&shm->sgt);
	shm->tee->ops->free(shm);
}

/*
 * Linux 5.0 commit a19741e5e5a9 ("dma_buf: remove device parameter from
 * attach callback") dropped the struct device * argument.  The donor body
 * never used it (it allocates against _DEV(tee)), so removing the parameter
 * is signature-only and semantically identical.
 */
static int __tee_shm_attach_dma_buf(struct dma_buf *dmabuf,
					struct dma_buf_attachment *attach)
{
	struct tee_shm_attach *tee_shm_attach;
	struct tee_shm *shm;
	struct tee *tee;

	shm = dmabuf->priv;
	tee = shm->tee;

	INMSG();

	tee_shm_attach = devm_kzalloc(_DEV(tee),
			sizeof(*tee_shm_attach), GFP_KERNEL);
	if (!tee_shm_attach) {
		OUTMSG(-ENOMEM);
		return -ENOMEM;
	}

	tee_shm_attach->dir = DMA_NONE;
	attach->priv = tee_shm_attach;

	OUTMSG(0);
	return 0;
}

static void __tee_shm_detach_dma_buf(struct dma_buf *dmabuf,
					struct dma_buf_attachment *attach)
{
	struct tee_shm_attach *tee_shm_attach = attach->priv;
	struct sg_table *sgt;
	struct tee_shm *shm;
	struct tee *tee;

	shm = dmabuf->priv;
	tee = shm->tee;

	/*
	 * Stock emits a diagnostic on the missing-private path; the donor
	 * returned silently.  The message is part of the stock control flow
	 * (it accounts for the 132 vs 116 byte delta), so it is reproduced.
	 */
	if (!tee_shm_attach) {
		pr_err("can not find tee_shm_attach\n");
		return;
	}

	sgt = &tee_shm_attach->sgt;

	/*
	 * Stock unmaps with sgt->nents but maps with sgt->orig_nents.  The
	 * asymmetry is deliberate and preserved.
	 */
	if (tee_shm_attach->dir != DMA_NONE)
		dma_unmap_sg(attach->dev, sgt->sgl, sgt->nents,
			tee_shm_attach->dir);

	sg_free_table(sgt);
	devm_kfree(_DEV(tee), tee_shm_attach);
	attach->priv = NULL;
}

static struct sg_table *__tee_shm_dma_buf_map_dma_buf(
		struct dma_buf_attachment *attach, enum dma_data_direction dir)
{
	struct tee_shm_attach *tee_shm_attach = attach->priv;
	struct tee_shm *tee_shm = attach->dmabuf->priv;
	struct sg_table *sgt = NULL;
	struct scatterlist *rd, *wr;
	unsigned int i;
	int nents, ret;
	struct tee *tee;

	tee = tee_shm->tee;

	INMSG();

	/* just return current sgt if already requested. */
	if (tee_shm_attach->dir == dir && tee_shm_attach->is_mapped) {
		OUTMSGX(&tee_shm_attach->sgt);
		return &tee_shm_attach->sgt;
	}

	sgt = &tee_shm_attach->sgt;

	ret = sg_alloc_table(sgt, tee_shm->sgt.orig_nents, GFP_KERNEL);
	if (ret) {
		pr_err("failed to alloc sgt.\n");
		return ERR_PTR(-ENOMEM);
	}

	rd = tee_shm->sgt.sgl;
	wr = sgt->sgl;
	for (i = 0; i < sgt->orig_nents; ++i) {
		sg_set_page(wr, sg_page(rd), rd->length, rd->offset);
		rd = sg_next(rd);
		wr = sg_next(wr);
	}

	if (dir != DMA_NONE) {
		nents = dma_map_sg(attach->dev, sgt->sgl, sgt->orig_nents, dir);
		if (!nents) {
			pr_err("failed to map sgl with iommu.\n");
			sg_free_table(sgt);
			sgt = ERR_PTR(-EIO);
			goto err_unlock;
		}
	}

	tee_shm_attach->is_mapped = true;
	tee_shm_attach->dir = dir;
	attach->priv = tee_shm_attach;

err_unlock:
	OUTMSGX(sgt);
	return sgt;
}

/*
 * Deliberate no-op: stock is a bare `ret` (4 bytes).  The per-attachment
 * mapping is intentionally cached across map/unmap cycles and is torn down
 * only in .detach.  This is a stock design decision, not a gap to fill.
 */
static void __tee_shm_dma_buf_unmap_dma_buf(struct dma_buf_attachment *attach,
					  struct sg_table *table,
					  enum dma_data_direction dir)
{
}

/*
 * Stock is exactly one call.  The donor additionally dereferenced
 * shm->ctx->tee purely to emit a debug line; that dereference is removed
 * because stock does not perform it and it is an avoidable fault risk on a
 * teardown path that may run after the context is gone.
 */
static void __tee_shm_dma_buf_release(struct dma_buf *dmabuf)
{
	tee_shm_free_io(dmabuf->priv);
}

/*
 * Stock reads only shm->flags and shm->paddr; it never touches shm->ctx.
 * TEE_SHM_CACHED (bit 29) selects the cached mapping, otherwise the
 * protection is pgprot_noncached() - proven from the stock constant
 * (AttrIndx=MT_DEVICE_nGnRnE | PTE_PXN | PTE_UXN).
 */
static int __tee_shm_dma_buf_mmap(struct dma_buf *dmabuf,
				struct vm_area_struct *vma)
{
	struct tee_shm *shm = dmabuf->priv;
	size_t size = vma->vm_end - vma->vm_start;
	unsigned long pfn = shm->paddr >> PAGE_SHIFT;
	pgprot_t prot;
	int ret;

	if (shm->flags & TEE_SHM_CACHED)
		prot = vma->vm_page_prot;
	else
		prot = pgprot_noncached(vma->vm_page_prot);

	ret = remap_pfn_range(vma, vma->vm_start, pfn, size, prot);
	if (!ret)
		vma->vm_private_data = (void *)shm;

	return ret;
}

/*
 * Stock populates exactly six slots: attach(+0x08), detach(+0x10),
 * map_dma_buf(+0x28), unmap_dma_buf(+0x30), release(+0x38) and mmap(+0x60).
 * Every other slot - including .vmap/.vunmap, which the OP-TEE donor filled
 * in - is NULL in stock, so they are removed rather than retained.
 *
 * mmap sits at +0x60 rather than mainline's +0x50 because the Android GKI
 * struct dma_buf_ops inserts begin_cpu_access_partial/end_cpu_access_partial.
 * Designated initialisers are used deliberately so the exact-GKI header - not
 * a hardcoded offset - decides the placement; the resulting relocation
 * offsets are then verified against the stock oracle.
 */
const struct dma_buf_ops tee_static_shm_dma_buf_ops = {
	.attach = __tee_shm_attach_dma_buf,
	.detach = __tee_shm_detach_dma_buf,
	.map_dma_buf = __tee_shm_dma_buf_map_dma_buf,
	.unmap_dma_buf = __tee_shm_dma_buf_unmap_dma_buf,
	.release = __tee_shm_dma_buf_release,
	.mmap = __tee_shm_dma_buf_mmap,
};

/******************************************************************************/

static int export_buf(struct tee *tee, struct tee_shm *shm, int *export)
{
	struct dma_buf *dmabuf;
	int ret = 0;
	/* Temporary fix to support both older and newer kernel versions. */
#if defined(DEFINE_DMA_BUF_EXPORT_INFO)
	DEFINE_DMA_BUF_EXPORT_INFO(exp_info);

	exp_info.priv = shm;
	exp_info.ops = &tee_static_shm_dma_buf_ops;
	exp_info.size = shm->size_alloc;
	exp_info.flags = O_RDWR;

	dmabuf = dma_buf_export(&exp_info);
#else
	dmabuf = dma_buf_export(shm, &tee_static_shm_dma_buf_ops,
				shm->size_alloc, O_RDWR, 0);
#endif
	if (IS_ERR_OR_NULL(dmabuf)) {
		pr_err("%s: dmabuf: couldn't export buffer (%ld)\n",
			__func__, PTR_ERR(dmabuf));
		ret = -EINVAL;
		goto out;
	}

	*export = dma_buf_fd(dmabuf, O_CLOEXEC);
out:
	OUTMSG(ret);
	return ret;
}

int tee_shm_alloc_io(struct tee_context *ctx, struct tee_shm_io *shm_io)
{
	struct tee_shm *shm;
	struct tee *tee = ctx->tee;
	int ret;

	INMSG();

	if (ctx->usr_client)
		shm_io->fd_shm = 0;

	mutex_lock(&tee->lock);
	shm = tkcore_alloc_shm(tee, shm_io->size, shm_io->flags);
	if (IS_ERR_OR_NULL(shm)) {
		pr_err("%s: buffer allocation failed (%ld)\n",
			__func__, PTR_ERR(shm));
		ret = PTR_ERR(shm);
		goto out;
	}

	if (ctx->usr_client) {
		ret = export_buf(tee, shm, &shm_io->fd_shm);
		if (ret) {
			tkcore_shm_free(shm);
			ret = -ENOMEM;
			goto out;
		}

		shm->flags |= TEEC_MEM_DMABUF;
	} else {
		/*
		 * Kernel-client path.  Stock publishes the resulting object
		 * pointer through shm_io->buffer (offset 0) - this is the only
		 * channel by which TEEC_AllocateSharedMemory can learn the
		 * tee_shm, since fd_shm is written only for user clients.
		 * Omitting this store is what left the island's
		 * TEEC_AllocateSharedMemory reading uninitialised stack.
		 */
		shm_io->buffer = shm;
	}

	shm->ctx = ctx;
	shm->dev = get_device(_DEV(tee));
	ret = tee_get(tee);
	BUG_ON(ret);		/* tee_core_get must not issue */
	tee_context_get(ctx);

	tee_inc_stats(&tee->stats[TEE_STATS_SHM_IDX]);
	list_add_tail(&shm->entry, &ctx->list_shm);
out:
	mutex_unlock(&tee->lock);
	OUTMSG(ret);
	return ret;
}

void tee_shm_free_io(struct tee_shm *shm)
{
	struct tee_context *ctx = shm->ctx;
	struct tee *tee = ctx->tee;
	struct device *dev = shm->dev;

	mutex_lock(&ctx->tee->lock);
	tee_dec_stats(&tee->stats[TEE_STATS_SHM_IDX]);
	list_del(&shm->entry);

	tkcore_shm_free(shm);
	tee_put(ctx->tee);
	tee_context_put(ctx);
	if (dev)
		put_device(dev);
	mutex_unlock(&ctx->tee->lock);
}

/* Buffer allocated by rpc from fw and to be accessed by the user
 * Not need to be registered as it is not allocated by the user */
int tee_shm_fd_for_rpc(struct tee_context *ctx, struct tee_shm_io *shm_io)
{
	struct tee_shm *shm = NULL;
	struct tee *tee = ctx->tee;
	int ret;
	struct list_head *pshm;

	INMSG();

	shm_io->fd_shm = 0;

	mutex_lock(&tee->lock);
	if (!list_empty(&tee->list_rpc_shm)) {
		list_for_each(pshm, &tee->list_rpc_shm) {
			shm = list_entry(pshm, struct tee_shm, entry);
			if ((void *)shm->paddr == shm_io->buffer)
				goto found;
		}
	}

	pr_err("Can't find shm for %p\n", (void *)shm_io->buffer);
	ret = -ENOMEM;
	goto out;

found:
	ret = export_buf(tee, shm, &shm_io->fd_shm);
	if (ret) {
		ret = -ENOMEM;
		goto out;
	}

	shm->ctx = ctx;
	list_move(&shm->entry, &ctx->list_shm);

	shm->dev = get_device(_DEV(tee));
	ret = tee_get(tee);
	BUG_ON(ret);
	tee_context_get(ctx);

	BUG_ON(!tee->ops->shm_inc_ref(shm));
out:
	mutex_unlock(&tee->lock);
	OUTMSG(ret);
	return ret;
}

/******************************************************************************/

static int tee_shm_db_get(struct tee *tee, struct tee_shm *shm, int fd,
		unsigned int flags, size_t size, int offset)
{
	struct tee_shm_dma_buf *sdb;
	struct dma_buf *dma_buf;
	int ret = 0;

	dev_dbg(_DEV(tee), "%s: > fd=%d flags=%08x\n", __func__, fd, flags);

	dma_buf = dma_buf_get(fd);
	if (IS_ERR(dma_buf)) {
		ret = PTR_ERR(dma_buf);
		goto exit;
	}

	sdb = kzalloc(sizeof(*sdb), GFP_KERNEL);
	if (IS_ERR_OR_NULL(sdb)) {
		pr_err("can't alloc tee_shm_dma_buf\n");
		ret = PTR_ERR(sdb);
		goto buf_put;
	}
	shm->sdb = sdb;

	if (dma_buf->size < size + offset) {
		pr_err("dma_buf too small %zd < %zd + %d\n",
			dma_buf->size, size, offset);
		ret = -EINVAL;
		goto free_sdb;
	}

	sdb->attach = dma_buf_attach(dma_buf, _DEV(tee));
	if (IS_ERR_OR_NULL(sdb->attach)) {
		ret = PTR_ERR(sdb->attach);
		goto free_sdb;
	}

	sdb->sgt = dma_buf_map_attachment(sdb->attach, DMA_NONE);
	if (IS_ERR_OR_NULL(sdb->sgt)) {
		ret = PTR_ERR(sdb->sgt);
		goto buf_detach;
	}

	if (sg_nents(sdb->sgt->sgl) != 1) {
		ret = -EINVAL;
		goto buf_unmap;
	}

	shm->paddr = sg_phys(sdb->sgt->sgl) + offset;
	/*
	 * Stock recognises a buffer it exported itself by comparing the
	 * foreign dma_buf's .attach slot against its own callback.
	 */
	if (dma_buf->ops->attach == __tee_shm_attach_dma_buf)
		sdb->tee_allocated = true;
	else
		sdb->tee_allocated = false;

	shm->flags |= TEEC_MEM_DMABUF;

	dev_dbg(_DEV(tee), "fd=%d @p=%p is_tee=%d db=%p\n", fd,
			(void *)shm->paddr, sdb->tee_allocated, dma_buf);
	goto exit;

buf_unmap:
	dma_buf_unmap_attachment(sdb->attach, sdb->sgt, DMA_NONE);
buf_detach:
	dma_buf_detach(dma_buf, sdb->attach);
free_sdb:
	kfree(sdb);
buf_put:
	dma_buf_put(dma_buf);
exit:
	OUTMSG(ret);
	return ret;
}

#ifdef VA_GET_ENABLED
static unsigned int tee_shm_get_phy_from_kla(
		struct mm_struct *mm, unsigned int kla)
{
	pgd_t *pgd;
	pud_t *pud;
	pmd_t *pmd;
	pte_t *ptep, pte;
	unsigned int pa = 0;

	/* stolen from kernel3.10:mm/memory.c:__follow_pte */

	pgd = pgd_offset(mm, kla);
	if (pgd_none(*pgd) || pgd_bad(*pgd))
		return 0;

	pud = pud_offset(pgd, kla);
	if (pud_none(*pud) || pud_bad(*pud))
		return 0;

	pmd = pmd_offset(pud, kla);
	VM_BUG_ON(pmd_trans_huge(*pmd));
	if (pmd_none(*pmd) || pmd_bad(*pmd))
		return 0;

	/* We cannot handle huge page PFN maps.
	 * Luckily they don't exist. */
	if (pmd_huge(*pmd))
		return 0;

	ptep = pte_offset_map(pmd, kla);

	if (!ptep)
		return 0;

	pte = *ptep;

	if (pte_present(pte))
		pa = __pa(page_address(pte_page(pte)));

	if (!pa)
		return 0;

	return pa;

}

static int tee_shm_va_get(struct tee_context *ctx, struct tee_shm *shm,
		void *buffer, unsigned int flags, size_t size, int offset)
{
	int ret = 0;
	struct mm_struct *mm = current->mm;
	unsigned long va = (unsigned long)buffer;
	unsigned int virt_base = (va / PAGE_SIZE) * PAGE_SIZE;
	unsigned int offset_in_page = va - virt_base;
	unsigned int offset_total = offset_in_page + offset;
	struct vm_area_struct *vma;
	struct tee *tee = ctx->tee;

	dev_dbg(_DEV(tee), "%s: > %p\n", __func__, buffer);
	/* if the caller is the kernel api, active_mm is mm */
	if (!mm)
		mm = current->active_mm;

	BUG_ON(!mm);

	vma = find_vma(mm, virt_base);

	if (vma) {
		unsigned long pfn;
		/* It's a VMA => consider it a a user address */

		if (follow_pfn(vma, virt_base, &pfn)) {
			dev_err(_DEV(tee), "%s can't get pfn for %p\n",
				__func__, buffer);
			ret = -EINVAL;
			goto out;
		}

		shm->paddr = PFN_PHYS(pfn) + offset_total;

		if (vma->vm_end - vma->vm_start - offset_total < size) {
			dev_err(_DEV(tee), "%s %p:%x not big enough: %lx - %d < %x\n",
					__func__, buffer, shm->paddr,
					vma->vm_end - vma->vm_start,
					offset_total, size);
			shm->paddr = 0;
			ret = -EINVAL;
			goto out;
		}
	} else if (!ctx->usr_client) {
		/* It's not a VMA => consider it as a kernel address
		 * And look if it's an internal known phys addr
		 * Note: virt_to_phys is not usable since it can be a direct
		 * map or a vremap address
		*/
		unsigned int phys_base;
		int nb_page = (PAGE_SIZE - 1 + size + offset_total) / PAGE_SIZE;
		int i;

		spin_lock(&mm->page_table_lock);
		phys_base = tee_shm_get_phy_from_kla(mm, virt_base);

		if (!phys_base) {
			spin_unlock(&mm->page_table_lock);
			dev_err(_DEV(tee), "%s can't get physical address for %p\n",
					__func__, buffer);
			goto err;
		}

		/* Check continuity on size */
		for (i = 1; i < nb_page; i++) {
			unsigned int pa = tee_shm_get_phy_from_kla(mm,
					virt_base + i*PAGE_SIZE);
			if (pa != phys_base + i*PAGE_SIZE) {
				spin_unlock(&mm->page_table_lock);
				dev_err(_DEV(tee), "%s %p:%x not big enough: %lx - %d < %x\n",
						__func__, buffer, phys_base,
						i*PAGE_SIZE,
						offset_total, size);
				goto err;
			}
		}
		spin_unlock(&mm->page_table_lock);

		shm->paddr = phys_base + offset_total;
		goto out;
err:
		ret = -EINVAL;
	}

out:
	dev_dbg(_DEV(tee), "%s: < %d shm=%p vaddr=%p paddr=%x\n",
			__func__, ret, (void *)shm, buffer, shm->paddr);
	return ret;
}
#endif

/*
 * Stock name is tkcore_shm_get.  This binds an externally owned buffer to a
 * transient memref tee_shm.  It is NOT inserted into ctx->list_shm - a memref
 * shm is owned by the command that created it, not by the context.
 */
struct tee_shm *tkcore_shm_get(struct tee_context *ctx, TEEC_SharedMemory *c_shm,
		size_t size, int offset)
{
	struct tee_shm *shm;
	struct tee *tee = ctx->tee;
	int ret;

	mutex_lock(&tee->lock);
	shm = kzalloc(sizeof(*shm), GFP_KERNEL);
	if (IS_ERR_OR_NULL(shm)) {
		pr_err("can't alloc tee_shm\n");
		ret = -ENOMEM;
		goto err;
	}

	shm->ctx = ctx;
	shm->tee = tee;
	shm->dev = _DEV(tee);
	shm->flags = c_shm->flags | TEE_SHM_MEMREF;
	shm->size_req = size;
	shm->size_alloc = 0;

	if (c_shm->flags & TEEC_MEM_KAPI) {
		struct tee_shm *kc_shm = (struct tee_shm *)c_shm->d.ptr;

		if (!kc_shm) {
			pr_err("kapi fd null\n");
			ret = -EINVAL;
			goto err;
		}
		shm->paddr = kc_shm->paddr;

		if (kc_shm->size_alloc < size + offset) {
			pr_err("kapi buff too small %zd < %zd + %d\n",
				kc_shm->size_alloc, size, offset);
			ret = -EINVAL;
			goto err;
		}

		dev_dbg(_DEV(tee), "fd=%d @p=%p\n",
				c_shm->d.fd, (void *)shm->paddr);
	} else if (c_shm->d.fd) {
		ret = tee_shm_db_get(tee, shm,
				c_shm->d.fd, c_shm->flags, size, offset);
		if (ret)
			goto err;
	} else if (!c_shm->buffer) {
		dev_dbg(_DEV(tee), "null buffer, pass 'as is'\n");
	} else {
#ifdef VA_GET_ENABLED
		ret = tee_shm_va_get(ctx, shm,
				c_shm->buffer, c_shm->flags, size, offset);
		if (ret)
			goto err;
#else
		ret = -EINVAL;
		goto err;
#endif
	}

	mutex_unlock(&tee->lock);
	OUTMSGX(shm);
	return shm;

err:
	kfree(shm);
	mutex_unlock(&tee->lock);
	OUTMSGX(ERR_PTR(ret));
	return ERR_PTR(ret);
}

/*
 * Stock name is tkcore_shm_put.  Stock validates ctx and ctx->tee as well as
 * shm before touching anything; the donor dereferenced shm->flags inside a
 * debug print BEFORE its own BUG_ON(!shm), i.e. it could fault on exactly the
 * input the check was meant to reject.  The guard order below is stock's.
 *
 * The sg_table returned by dma_buf_map_attachment() belongs to the EXPORTER
 * and is handed back via dma_buf_unmap_attachment(); tkcore never frees it.
 */
void tkcore_shm_put(struct tee_context *ctx, struct tee_shm *shm)
{
	struct tee *tee;

	BUG_ON(!ctx);
	BUG_ON(!ctx->tee);
	BUG_ON(!shm);
	BUG_ON(!(shm->flags & TEE_SHM_MEMREF));

	tee = ctx->tee;

	mutex_lock(&tee->lock);
	if (shm->flags & TEEC_MEM_DMABUF) {
		struct tee_shm_dma_buf *sdb = shm->sdb;
		struct dma_buf *dma_buf = sdb->attach->dmabuf;

		dma_buf_unmap_attachment(sdb->attach, sdb->sgt, DMA_NONE);
		dma_buf_detach(dma_buf, sdb->attach);
		dma_buf_put(dma_buf);

		kfree(sdb);
	}

	kfree(shm);
	mutex_unlock(&ctx->tee->lock);
}

