# GQ5012BF1 tkcore shared-memory ownership and lifetime model

Derived from stock disassembly. Each path below answers the mandatory ownership questions explicitly.

## A. Context-owned shared memory (`tee_shm_alloc_io` → `tee_shm_free_io`)

```text
tee_shm_alloc_io(ctx, shm_io)
  mutex_lock(&tee->lock)
  shm = tkcore_alloc_shm(tee, shm_io->size, shm_io->flags)   -> provider ops->alloc + shm->sgt
  if (ctx->usr_client)
        dma_buf_export(...tee_static_shm_dma_buf_ops...)      -> dma_buf owns shm from here
        shm_io->fd_shm = dma_buf_fd(dmabuf, O_CLOEXEC)
        shm->flags |= TEEC_MEM_DMABUF
  else
        shm_io->buffer = shm                                  -> caller receives the object pointer
  shm->ctx = ctx
  shm->dev = get_device(tee->dev)
  tee_get(tee)
  tee_context_get(ctx)
  tee_inc_stats(); list_add_tail(&shm->entry, &ctx->list_shm)
  mutex_unlock(&tee->lock)
```

```text
tee_shm_free_io(shm)
  mutex_lock(&tee->lock)
  tee_dec_stats(); list_del(&shm->entry)
  tkcore_shm_free(shm)          -> sg_free_table + provider ops->free
  tee_put(tee)
  tee_context_put(ctx)
  put_device(shm->dev)
  mutex_unlock(&tee->lock)
```

- **Who owns the memory?** The provider backend; `tkcore_alloc_shm`/`tkcore_shm_free` only wrap `ops->alloc`/`ops->free` and own the `sg_table` around it.
- **Who owns the object?** The context, through `ctx->list_shm`.
- **References taken:** one device reference, one provider reference (`tee_get`), one context kref (`tee_context_get`). All three are released in `tee_shm_free_io`, in reverse-ish order (provider, context, device).
- **Lock:** `tee->lock` protects list membership and statistics on both sides.

## B. Cached shared memory (`tee_map_cached_shm` / `tee_unmap_cached_shm`)

This path owns **no object at all** — it is a pure address-space mapping service for the provider driver.

```text
tee_map_cached_shm(pa, len)
  if (pfn_is_map_memory(pa >> PAGE_SHIFT))
        return __va(pa)                 /* already linear-mapped: nothing is created */
  return ioremap_prot(pa, len, PAGE_KERNEL)   /* cached, MT_NORMAL */

tee_unmap_cached_shm(va)
  iounmap(va)
```

- **Who owns the memory?** Nobody here; the physical region belongs to the caller (`tkcore_drv`).
- **Ownership asymmetry, reproduced deliberately:** the linear-map branch creates no mapping, yet `tee_unmap_cached_shm` calls `iounmap()` unconditionally. This is safe because arm64's `iounmap()` is a no-op for non-vmalloc addresses, and it is exactly what stock does. The island does not add a guard stock does not have.
- **Lock:** none.

## C. dma-buf **exported** by tkcore (`tee_shm_alloc_io` usr_client path)

```text
dma_buf_export(exp_info{ .ops = &tee_static_shm_dma_buf_ops, .priv = shm, .size = shm->size_alloc })
        -> dma_buf holds shm
dma_buf_fd()  -> userspace holds the dma_buf
...
__tee_shm_dma_buf_release(dmabuf)   /* last dma_buf reference dropped */
        tee_shm_free_io(dmabuf->priv)
```

- **Who owns the dma_buf?** Userspace, via the fd. The shm does **not** hold a reference to its own dma_buf.
- **Who destroys the shm?** `__tee_shm_dma_buf_release`, i.e. the dma_buf outlives the fd and destroys the shm when it dies. This inverts path A's ownership: for an exported buffer the dma_buf is the owner of record.
- **Race:** `.release` runs from dma-buf teardown and immediately takes `tee->lock` inside `tee_shm_free_io`. It must never be called with that lock already held.

### Attachment sub-lifetime (foreign importer attaching to *our* buffer)

```text
.attach   -> devm_kzalloc(tee->dev, 0x18)  ; dir = DMA_NONE ; attach->priv = record
.map_dma_buf(attach, dir)
        if (record->dir == dir && record->is_mapped) return &record->sgt   /* cached */
        sg_alloc_table(&record->sgt, shm->sgt.orig_nents, GFP_KERNEL)
        copy shm->sgt entries into record->sgt
        if (dir != DMA_NONE) dma_map_sg_attrs(attach->dev, ...)
        record->dir = dir ; record->is_mapped = true
        return &record->sgt
.unmap_dma_buf -> deliberate no-op
.detach   -> if (dir != DMA_NONE) dma_unmap_sg_attrs(...)
             sg_free_table(record) ; devm_kfree(tee->dev, record) ; attach->priv = NULL
```

- **Who owns the attachment?** The dma-buf core.
- **Who owns the per-attachment `sg_table`?** tkcore, inside the `tee_shm_attach` record, allocated against `tee->dev`.
- **Why is `unmap_dma_buf` empty?** Because the mapping is intentionally cached across map/unmap cycles and torn down only at `.detach`. This is a real stock design decision, not a missing implementation — the stock function is 4 bytes (`ret`).
- **`devm_` on a per-attachment object:** records are attached to the provider device's devres list, so a leaked attachment is reclaimed at device teardown. Reproduced as-is.

## D. dma-buf **imported** by tkcore (`tkcore_shm_get` / `tkcore_shm_put`)

```text
tkcore_shm_get(ctx, c_shm, size, offset)
  mutex_lock(&tee->lock)
  shm = kzalloc(0x68)
  shm->{ctx,tee,dev,size_req} set ; shm->size_alloc = 0
  shm->flags = c_shm->flags | TEE_SHM_MEMREF

  if (c_shm->flags & TEEC_MEM_KAPI):            /* d.ptr is already a struct tee_shm * */
        parent = c_shm->d.ptr ; require parent
        shm->paddr = parent->paddr
        require parent->size_alloc >= size + offset
  elif (c_shm->d.fd):
        dmabuf = dma_buf_get(fd)                 /* +1 dma_buf ref */
        sdb = kzalloc(0x18) ; shm->sdb = sdb
        require dmabuf->size >= offset + size
        sdb->attach = dma_buf_attach(dmabuf, tee->dev)
        sdb->sgt    = dma_buf_map_attachment(attach, DMA_NONE)
        require sg_nents(sgt->sgl) == 1          /* single physically contiguous segment */
        shm->paddr = sg_phys(sgt->sgl) + offset
        shm->flags |= TEEC_MEM_DMABUF
        sdb->tee_allocated = (dmabuf->ops->attach == __tee_shm_attach_dma_buf)
  elif (!c_shm->buffer):
        /* nothing to bind: pass through */
  else:
        -EINVAL
  mutex_unlock(&tee->lock)
```

```text
tkcore_shm_put(ctx, shm)
  BUG_ON(!ctx); BUG_ON(!ctx->tee); BUG_ON(!shm); BUG_ON(!(shm->flags & TEE_SHM_MEMREF))
  mutex_lock(&tee->lock)
  if (shm->flags & TEEC_MEM_DMABUF):
        dma_buf = sdb->attach->dmabuf
        dma_buf_unmap_attachment(sdb->attach, sdb->sgt, DMA_NONE)
        dma_buf_detach(dma_buf, sdb->attach)
        dma_buf_put(dma_buf)                     /* -1 dma_buf ref */
        kfree(sdb)
  kfree(shm)
  mutex_unlock(&tee->lock)
```

- **Who owns the memory?** The external exporter. tkcore holds only a reference.
- **Who owns the dma_buf reference?** The `tee_shm`, acquired by `dma_buf_get` and released by `dma_buf_put` in `tkcore_shm_put`.
- **Who owns the attachment?** The `tee_shm_dma_buf` record, which is `kfree`d after `dma_buf_detach`.
- **Who owns the `sg_table`?** The **exporter** — it came from `dma_buf_map_attachment` and is returned via `dma_buf_unmap_attachment`. tkcore never frees it. This is the sharpest ownership distinction in the subsystem and the one most easily got wrong.
- **List interaction:** none. A memref shm is *not* inserted into `ctx->list_shm`; it is a transient parameter binding owned by the command that created it. It is therefore invisible to context teardown (see the context-teardown report).
- **Lock:** `tee->lock` is taken and released inside both functions.

## E. Provider-owned allocations (`ops->alloc` / `ops->free`)

`tkcore_alloc_shm` and `tkcore_shm_free` are thin wrappers whose only independent responsibility is the `sg_table`:

```text
tkcore_alloc_shm(tee, size, flags)
  shm = tee->ops->alloc(tee, size, flags)        /* KCFI 0x45b20ce9 */
  if (!shm || IS_ERR(shm)) -> log and return it unchanged
  page = phys_to_page(shm->paddr)
  if (!page || IS_ERR(page)) { log; ops->free(shm); return (struct tee_shm *)page; }
  sg_alloc_table_from_pages_segment(&shm->sgt, &page, 1, 0, PAGE_SIZE, UINT_MAX, GFP_KERNEL)
  if (ret) { log; ops->free(shm); return ERR_PTR(ret); }
  shm->tee = tee
  return shm

tkcore_shm_free(shm)
  if (!shm || IS_ERR(shm)) return
  if (!shm->tee) { BUG(); return; }
  sg_free_table(&shm->sgt)
  shm->tee->ops->free(shm)                       /* KCFI 0xa7e6969f */
```

- **get/put vs alloc/free are distinct axes and are not merged.** `tkcore_alloc_shm`/`tkcore_shm_free` manage an *object the provider owns*. `tkcore_shm_get`/`tkcore_shm_put` manage a *reference to memory someone else owns*. They share no state and never call one another.
- **Reproduced stock quirks:** the sg-table describes exactly one page of `PAGE_SIZE`, regardless of requested size; and both failure paths return the *page pointer* or `ERR_PTR(ret)` cast to `struct tee_shm *` rather than a uniform error. Both are stock behaviour and are documented rather than silently "improved".

## Race summary

| Callback | Entered from | `tee->lock` held on entry? | Takes `tee->lock`? |
|---|---|---|---|
| `.attach` / `.detach` / `.map_dma_buf` / `.unmap_dma_buf` | dma-buf core | no | no |
| `.mmap` | `mmap(2)` on the exported fd | no | no |
| `.release` | last dma_buf ref drop | **must not be** | yes, via `tee_shm_free_io` |
| `tkcore_shm_get` / `tkcore_shm_put` | command marshalling | no | yes, internally |
| `tkcore_alloc_shm` / `tkcore_shm_free` | `tee_shm_*_io` | **yes** | no |

The asymmetry in the last two rows is load-bearing: `tkcore_alloc_shm` is called with `tee->lock` already held by `tee_shm_alloc_io`, which is precisely why it must not take the lock itself.
