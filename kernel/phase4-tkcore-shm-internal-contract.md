# GQ5012BF1 tkcore internal shared-memory contract

`tkcore_alloc_shm`, `tkcore_shm_get`, `tkcore_shm_put`, `tkcore_shm_free`.

All four are **GLOBAL but not exported** in stock. The donor carried them as `tee_shm_alloc` / `tee_shm_get` / `tee_shm_put` / `tee_shm_free`; Phase 3B renamed them to their stock identities and corrected their bodies.

## The axis that must not be collapsed

| Axis | Functions | Governs |
|---|---|---|
| object lifetime | `tkcore_alloc_shm` / `tkcore_shm_free` | a `tee_shm` the **provider** owns |
| reference lifetime | `tkcore_shm_get` / `tkcore_shm_put` | a reference to memory **someone else** owns |

They share no state and never call one another. The donor blurred this; stock does not, and neither does the reconstruction.

## `tkcore_alloc_shm(struct tee *tee, size_t size, uint32_t flags)`

Stock `0x57fc`, 408 bytes, KCFI `0x45b20ce9` — **identical to the `ops->alloc` slot id**, which is itself the proof that the island's `struct tee_ops` prototype is right.

```c
shm = tee->ops->alloc(tee, size, flags);          /* slot +0x40 */
if (IS_ERR_OR_NULL(shm)) { pr_err(...); goto out; }

page = phys_to_page(shm->paddr);
if (IS_ERR_OR_NULL(page)) {
        pr_err(...);
        tee->ops->free(shm);                      /* slot +0x48 */
        shm = (struct tee_shm *)page;             /* stock returns the page ptr */
        goto out;
}

ret = sg_alloc_table_from_pages(&shm->sgt, &page, 1, 0, PAGE_SIZE, GFP_KERNEL);
if (ret < 0) { pr_err(...); tee->ops->free(shm); shm = ERR_PTR(ret); }

out:
if (!IS_ERR_OR_NULL(shm))
        shm->tee = tee;                           /* LAST, on every path */
return shm;
```

Proven details, all reproduced:

- **`shm->tee` is assigned last**, guarded, and every path flows through the assignment (`0x58b8`: `cbz` then `cmn x20,#0x1000 / b.hi`, i.e. `!IS_ERR_OR_NULL`). The donor assigned it immediately after the allocation, which **writes through an error pointer** when `ops->alloc` fails. That was a real bug.
- **One page, `PAGE_SIZE`, always** — stock passes literal `1` and `0x1000` regardless of `size` (`58a4: mov w4, #0x1000`). Reproduced, not "fixed".
- `sg_alloc_table_from_pages()` is the static-inline wrapper that calls `sg_alloc_table_from_pages_segment(..., UINT_MAX, gfp)`, which is why stock's undefined import is the `_segment` form.
- The page-failure path returns the **page pointer** cast to `struct tee_shm *`; the sg-failure path returns `ERR_PTR(ret)`. Two different error conventions in one function — stock's, preserved.
- Diagnostics are `pr_err` (3 × `_printk`), not `dev_err`.
- The caller (`tee_shm_alloc_io`, `tee_shm_alloc_from_rpc`, `tee_context_alloc_shm_tmp`) already holds `tee->lock`; this function must not take it.

## `tkcore_shm_free(struct tee_shm *shm)`

Stock `0x5998`, 116 bytes, KCFI `0xa7e6969f`.

```c
if (IS_ERR_OR_NULL(shm)) return;
if (!shm->tee) { BUG(); return; }
sg_free_table(&shm->sgt);
shm->tee->ops->free(shm);
```

Stock's `brk #0x800` on the NULL-`tee` path is a `BUG()`, not a warning. The donor emitted `pr_warn`, and additionally re-tested `shm->tee == NULL` after already loading `tee` from it — dead code. Both corrected.

## `tkcore_shm_get(struct tee_context *ctx, TEEC_SharedMemory *c_shm, size_t size, int offset)`

Stock `0x6084`, 672 bytes, KCFI `0x00b73c2b`. **Byte-identical** in the island.

```c
mutex_lock(&tee->lock);
shm = kzalloc(sizeof(*shm) /* 0x68 */, GFP_KERNEL);
shm->{ctx,tee,dev,size_req} = ...; shm->size_alloc = 0;
shm->flags = c_shm->flags | TEE_SHM_MEMREF;

if (c_shm->flags & TEEC_MEM_KAPI) {
        parent = c_shm->d.ptr;  require parent;
        shm->paddr = parent->paddr;
        require parent->size_alloc >= size + offset;
} else if (c_shm->d.fd) {
        dmabuf = dma_buf_get(fd);                 /* +1 ref */
        sdb = kzalloc(0x18); shm->sdb = sdb;
        require dmabuf->size >= offset + size;
        sdb->attach = dma_buf_attach(dmabuf, tee->dev);
        sdb->sgt    = dma_buf_map_attachment(attach, DMA_NONE);
        require sg_nents(sgt->sgl) == 1;          /* single contiguous segment */
        shm->paddr  = sg_phys(sgt->sgl) + offset;
        shm->flags |= TEEC_MEM_DMABUF;
        sdb->tee_allocated = (dmabuf->ops->attach == __tee_shm_attach_dma_buf);
} else if (!c_shm->buffer) {
        /* pass through */
} else {
        -EINVAL;
}
mutex_unlock(&tee->lock);
```

- Branch order is stock's: KAPI pointer path, then fd path, then the empty-buffer pass-through, then `-EINVAL`.
- `dma_buf_map_attachment` is called with **`DMA_NONE`**, and `tkcore_shm_put` unmaps with `DMA_NONE` to match.
- The single-segment requirement (`sg_nents == 1`) is a hard constraint: tkcore only accepts physically contiguous imported buffers.
- `sdb->tee_allocated` is derived by comparing the foreign exporter's `.attach` slot against tkcore's own callback — this is how stock recognises a buffer it exported itself.
- Stock computes `shm->paddr` as `page_to_phys(sg_page(sgl)) + sgl->offset + offset`, i.e. `sg_phys(sgl) + offset`; the disassembly's `vmemmap` arithmetic (`VMEMMAP_START = 0xFFFFFFFE00000000`, `sizeof(struct page) = 64`) was decoded to confirm this exactly.
- **A memref shm is never inserted into `ctx->list_shm`** and takes no context reference. Its lifetime belongs to the command that created it.
- Five diagnostics, all `pr_err`, matching stock's five `_printk`.

## `tkcore_shm_put(struct tee_context *ctx, struct tee_shm *shm)`

Stock `0x6328`, 192 bytes, KCFI `0x2309a7a5`.

```c
BUG_ON(!ctx); BUG_ON(!ctx->tee); BUG_ON(!shm);
BUG_ON(!(shm->flags & TEE_SHM_MEMREF));
mutex_lock(&tee->lock);
if (shm->flags & TEEC_MEM_DMABUF) {
        dma_buf = sdb->attach->dmabuf;
        dma_buf_unmap_attachment(sdb->attach, sdb->sgt, DMA_NONE);
        dma_buf_detach(dma_buf, sdb->attach);
        dma_buf_put(dma_buf);
        kfree(sdb);
}
kfree(shm);
mutex_unlock(&ctx->tee->lock);
```

- Stock validates **`ctx` and `ctx->tee` as well**, which the donor did not.
- The donor read `shm->flags` inside a debug print **before** its own `BUG_ON(!shm)` — it could fault on exactly the input the check existed to reject. Guard order is now stock's.
- `TEE_SHM_MEMREF` is `BUG()`-enforced, which is why `tkcore_shm_get` sets it unconditionally.
- **The `sg_table` is never freed here.** It was obtained from `dma_buf_map_attachment` and belongs to the exporter; it is returned via `dma_buf_unmap_attachment`. Calling `sg_free_table` on it would corrupt the exporter's state. The verifier asserts `sg_free_table` does not appear in this function.
- Stock re-loads `ctx->tee` for the unlock; reproduced.

## Reference ledger

| Acquired in | Reference | Released in |
|---|---|---|
| `tkcore_shm_get` | `dma_buf_get` | `tkcore_shm_put` (`dma_buf_put`) |
| `tkcore_shm_get` | `dma_buf_attach` | `tkcore_shm_put` (`dma_buf_detach`) |
| `tkcore_shm_get` | `dma_buf_map_attachment` | `tkcore_shm_put` (`dma_buf_unmap_attachment`) |
| `tkcore_alloc_shm` | provider allocation | `tkcore_shm_free` (`ops->free`) |
| `tkcore_alloc_shm` | `shm->sgt` | `tkcore_shm_free` (`sg_free_table`) |

Every acquisition has exactly one matching release, in the reverse order of acquisition.
