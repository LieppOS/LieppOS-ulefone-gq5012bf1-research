// SPDX-License-Identifier: GPL-2.0
/*
 * Shared-memory pool for the TrustKernel backend (reconstruction of the stock
 * ../kernel_device_modules-6.1/drivers/tee/tkcore/armtz/tee_mem.c).
 *
 * The pool manages one physically contiguous window that is shared with the
 * secure world.  Chunks are tracked on a single ordered list, each with a
 * reference count so that a buffer handed to the secure world can be reused
 * by the supplicant path without being freed underneath it.
 *
 * Stock functions reproduced here (stock .text offsets):
 *   tee_shm_pool_dump 0x2ba8   tee_shm_pool_is_cached 0x2c7c
 *   tee_shm_pool_set_cached 0x2c88  tee_shm_pool_create 0x2c98
 *   tee_shm_pool_destroy 0x2dd4  tee_shm_pool_reset 0x2e30
 *   tee_shm_pool_p2v 0x2f2c    tee_shm_pool_v2p 0x2fd0
 *   tkcore_shm_pool_alloc 0x3074  tkcore_shm_pool_free 0x3318
 *   tee_shm_pool_incref 0x34fc
 */
#undef pr_fmt
#define pr_fmt(fmt) "tkcore_drv: " fmt

#include <linux/device.h>
#include <linux/list.h>
#include <linux/mutex.h>
#include <linux/slab.h>
#include <linux/spinlock.h>

#include "tee_mem.h"

#define TEE_MEM_ALIGN_MIN	8

struct mem_chunk {
	struct list_head node;
	unsigned long paddr;
	size_t size;
	int refcount;
};

struct shm_pool {
	spinlock_t lock;
	struct list_head chunks;
	void *vaddr;
	unsigned long paddr;
	size_t size;
	size_t used;
	bool cached;
};

static bool is_valid_paddr(struct shm_pool *pool, unsigned long paddr)
{
	return paddr >= pool->paddr && paddr < pool->paddr + pool->size;
}

static bool is_valid_vaddr(struct shm_pool *pool, void *vaddr)
{
	return vaddr >= pool->vaddr &&
	       (unsigned long)vaddr < (unsigned long)pool->vaddr + pool->size;
}

void tee_shm_pool_dump(struct device *dev, struct shm_pool *pool, bool forced)
{
	struct mem_chunk *chunk;

	if (!pool)
		return;

	if (!forced)
		return;

	spin_lock(&pool->lock);
	pr_info("%s() poolH(0x%p) pAddr=0x%p vAddr=0x%p size=%zu used=%zu(%zu%%)\n",
		 __func__, pool, (void *)pool->paddr, pool->vaddr, pool->size,
		 pool->used, pool->size ? pool->used * 100 / pool->size : 0);
	pr_info("  \\ HEAD next:[0x%p] prev:[0x%p]\n",
		 pool->chunks.next, pool->chunks.prev);
	pr_info("  |-[@]        next       prev       pAddr      size     refCount\n");
	list_for_each_entry(chunk, &pool->chunks, node)
		pr_info("  | [0x%p] 0x%p 0x%p 0x%p %08zu %d\n",
			 chunk, chunk->node.next, chunk->node.prev,
			 (void *)chunk->paddr, chunk->size, chunk->refcount);
	spin_unlock(&pool->lock);
}

bool tee_shm_pool_is_cached(struct shm_pool *pool)
{
	return pool->cached;
}

void tee_shm_pool_set_cached(struct shm_pool *pool)
{
	pool->cached = true;
}

struct shm_pool *tee_shm_pool_create(struct device *dev, size_t shm_size,
				     void *shm_vaddr, unsigned long shm_paddr)
{
	struct shm_pool *pool;

	pool = devm_kzalloc(dev, sizeof(*pool), GFP_KERNEL);
	if (!pool) {
		pr_err("kmalloc <struct shm_pool> failed\n");
		return NULL;
	}

	spin_lock_init(&pool->lock);
	INIT_LIST_HEAD(&pool->chunks);
	pool->vaddr = shm_vaddr;
	pool->paddr = shm_paddr;
	pool->size = shm_size;
	pool->used = 0;
	pool->cached = false;

	return pool;
}

void tee_shm_pool_reset(struct device *dev, struct shm_pool *pool)
{
	struct mem_chunk *chunk, *tmp;

	if (!pool)
		return;

	spin_lock(&pool->lock);
	list_for_each_entry_safe(chunk, tmp, &pool->chunks, node) {
		pr_err("Free lost chunkH=0x%p\n", chunk);
		list_del(&chunk->node);
		devm_kfree(dev, chunk);
	}
	pool->used = 0;
	spin_unlock(&pool->lock);
}

void tee_shm_pool_destroy(struct device *dev, struct shm_pool *pool)
{
	if (!pool)
		return;

	tee_shm_pool_reset(dev, pool);
	devm_kfree(dev, pool);
}

void *tee_shm_pool_p2v(struct device *dev, struct shm_pool *pool,
		       unsigned long paddr)
{
	if (!pool)
		return NULL;

	if (!is_valid_paddr(pool, paddr)) {
		pr_err("%s() paddr=0x%p not in the shm pool\n",
			__func__, (void *)paddr);
		return NULL;
	}

	return (void *)((unsigned long)pool->vaddr + (paddr - pool->paddr));
}

unsigned long tee_shm_pool_v2p(struct device *dev, struct shm_pool *pool,
			       void *vaddr)
{
	if (!pool)
		return 0;

	if (!is_valid_vaddr(pool, vaddr)) {
		pr_err("%s() vaddr=0x%p not in shm pool\n",
			__func__, vaddr);
		return 0;
	}

	return pool->paddr + ((unsigned long)vaddr - (unsigned long)pool->vaddr);
}

/*
 * Allocate `size` bytes with `alignment` from the shared window.  The stock
 * allocator is a first-fit walker over the ordered chunk list: it looks for a
 * gap between two live chunks (or after the last one) that is large enough
 * once the start address has been rounded up to the requested alignment.
 */
unsigned long tkcore_shm_pool_alloc(struct device *dev, struct shm_pool *pool,
				    size_t size, size_t alignment)
{
	struct mem_chunk *chunk, *new_chunk;
	struct list_head *insert_after;
	unsigned long candidate;
	size_t free_bytes;

	if (!pool || !size)
		return 0;

	if (alignment < TEE_MEM_ALIGN_MIN)
		alignment = TEE_MEM_ALIGN_MIN;

	new_chunk = devm_kzalloc(dev, sizeof(*new_chunk), GFP_KERNEL);
	if (!new_chunk) {
		pr_err("kmalloc <struct MemChunk> failed\n");
		return 0;
	}

	spin_lock(&pool->lock);

	candidate = ALIGN(pool->paddr, alignment);
	insert_after = &pool->chunks;

	list_for_each_entry(chunk, &pool->chunks, node) {
		if (candidate + size <= chunk->paddr)
			break;
		candidate = ALIGN(chunk->paddr + chunk->size, alignment);
		insert_after = &chunk->node;
	}

	if (candidate + size > pool->paddr + pool->size) {
		free_bytes = pool->size - pool->used;
		spin_unlock(&pool->lock);
		pr_err("%s() FAILED, size=0x%zx, align=0x%zx free=%zu\n",
			__func__, size, alignment, free_bytes);
		devm_kfree(dev, new_chunk);
		return 0;
	}

	new_chunk->paddr = candidate;
	new_chunk->size = size;
	new_chunk->refcount = 1;
	list_add(&new_chunk->node, insert_after);
	pool->used += size;

	spin_unlock(&pool->lock);

	return candidate;
}

int tkcore_shm_pool_free(struct device *dev, struct shm_pool *pool,
			 unsigned long paddr, size_t *size)
{
	struct mem_chunk *chunk;
	int ret = -1;

	if (!pool)
		return -1;

	if (!is_valid_paddr(pool, paddr)) {
		pr_err("%s() FAILED, pAddr=%p is not a valid @\n",
			__func__, (void *)paddr);
		return -1;
	}

	spin_lock(&pool->lock);
	list_for_each_entry(chunk, &pool->chunks, node) {
		if (chunk->paddr != paddr)
			continue;

		if (chunk->refcount <= 0) {
			spin_unlock(&pool->lock);
			pr_warn("< %s() WARNING, paddr=0x%p already released\n",
				 __func__, (void *)paddr);
			return -1;
		}

		if (--chunk->refcount == 0) {
			if (size)
				*size = chunk->size;
			pool->used -= chunk->size;
			list_del(&chunk->node);
			devm_kfree(dev, chunk);
		} else if (size) {
			*size = chunk->size;
		}
		ret = 0;
		break;
	}
	spin_unlock(&pool->lock);

	if (ret)
		pr_err("shm_pool_free failed: paddr=0x%lx not found\n",
			paddr);

	return ret;
}

bool tee_shm_pool_incref(struct device *dev, struct shm_pool *pool,
			 unsigned long paddr)
{
	struct mem_chunk *chunk;
	bool found = false;

	if (!pool)
		return false;

	spin_lock(&pool->lock);
	list_for_each_entry(chunk, &pool->chunks, node) {
		if (chunk->paddr == paddr) {
			chunk->refcount++;
			found = true;
			break;
		}
	}
	spin_unlock(&pool->lock);

	if (!found)
		pr_err("%s() paddr=0x%p not in the shm pool\n",
			__func__, (void *)paddr);

	return found;
}
