# GQ5012BF1 tkcore dma_buf_ops contract

Recovered from the stock ELF. Where stock differs from ordinary upstream dma-buf practice, **stock wins** and the divergence is called out.

## The table

`tee_static_shm_dma_buf_ops`, `const`, 144 bytes, `.rodata+0x420`. Exactly six slots are populated:

| Slot | Member | Target | Stock size | Stock KCFI |
|---:|---|---|---:|---|
| `+0x00` | `cache_sgt_mapping` | `false` | — | — |
| `+0x08` | `attach` | `__tee_shm_attach_dma_buf` | 92 | `0x975557fe` |
| `+0x10` | `detach` | `__tee_shm_detach_dma_buf` | 132 | `0x90d39919` |
| `+0x28` | `map_dma_buf` | `__tee_shm_dma_buf_map_dma_buf` | 308 | `0x7c6e5fbe` |
| `+0x30` | `unmap_dma_buf` | `__tee_shm_dma_buf_unmap_dma_buf` | 4 | `0xc0a08c9a` |
| `+0x38` | `release` | `__tee_shm_dma_buf_release` | 32 | `0xa80f535b` |
| `+0x60` | `mmap` | `__tee_shm_dma_buf_mmap` | 104 | `0xe4d3eb24` |

Every other slot is NULL — including `pin`, `unpin`, `begin_cpu_access`, `end_cpu_access`, `vmap` and `vunmap`.

**`mmap` at `+0x60`, not the mainline `+0x50`.** The Android GKI `struct dma_buf_ops` inserts `begin_cpu_access_partial` and `end_cpu_access_partial`, shifting `mmap` by two slots. Phase 3B therefore builds the table with **designated initialisers** and verifies the resulting relocation offsets against this oracle, rather than hardcoding any offset. Hardcoding would silently break if the header differed.

**`vmap`/`vunmap` must be absent.** The donor populates both. Stock does not. Keeping them would add two relocations and two functions that stock has no counterpart for, so they are removed rather than retained "because they look harmless".

## `__tee_shm_attach_dma_buf(struct dma_buf *dmabuf, struct dma_buf_attachment *attach)`

- Reads `shm = dmabuf->priv`, then `shm->tee`, then `tee->dev`.
- `devm_kmalloc(dev, sizeof(struct tee_shm_attach) /* 0x18 */, GFP_KERNEL | __GFP_ZERO)`.
- On failure returns `-ENOMEM`; no message.
- Sets `record->dir = DMA_NONE` and `attach->priv = record`.
- Returns `0`.
- No device parameter: Linux 5.0 `a19741e5e5a9` removed it, and the exact-GKI header reflects that.

## `__tee_shm_detach_dma_buf(struct dma_buf *dmabuf, struct dma_buf_attachment *attach)`

- `record = attach->priv`; if NULL, **print a diagnostic and return** (the donor returns silently — stock's message accounts for the 132 vs 116 size gap).
- `tee = ((struct tee_shm *)dmabuf->priv)->tee`.
- If `record->dir != DMA_NONE`: `dma_unmap_sg_attrs(attach->dev, record->sgt.sgl, record->sgt.nents, record->dir, 0)`. Note **`nents`**, not `orig_nents`, on the unmap side.
- `sg_free_table(&record->sgt)`, `devm_kfree(tee->dev, record)`, `attach->priv = NULL`.

## `__tee_shm_dma_buf_map_dma_buf(struct dma_buf_attachment *attach, enum dma_data_direction dir)`

Returns `struct sg_table *` (or an `ERR_PTR`).

1. `record = attach->priv`; `shm = attach->dmabuf->priv`.
2. **Cache hit:** if `record->dir == dir && record->is_mapped`, return `&record->sgt` immediately without touching anything.
3. `sg_alloc_table(&record->sgt, shm->sgt.orig_nents, GFP_KERNEL)`; on failure log and return `ERR_PTR(-ENOMEM)` — **without** freeing, because nothing was allocated.
4. Copy `shm->sgt.orig_nents` entries from `shm->sgt.sgl` into `record->sgt.sgl` using `sg_set_page(wr, sg_page(rd), rd->length, rd->offset)`, advancing both with `sg_next`. Stock's `bfxil` is exactly `sg_assign_page`'s preservation of the chain/end bits, so `sg_set_page` is the faithful expression.
5. If `dir != DMA_NONE`: `dma_map_sg_attrs(attach->dev, record->sgt.sgl, record->sgt.orig_nents, dir, 0)`; a `0` return means failure → log, `sg_free_table`, return `ERR_PTR(-EIO)`. Note the map side uses **`orig_nents`**.
6. On success set `record->dir = dir`, `record->is_mapped = true`, re-publish `attach->priv = record`, and return `&record->sgt`.

The `orig_nents` (map) vs `nents` (unmap) asymmetry is stock's, and is preserved.

## `__tee_shm_dma_buf_unmap_dma_buf(attach, sgt, dir)`

A deliberate no-op — 4 bytes, a bare `ret`. Teardown of the mapping is deferred entirely to `.detach`. This is not an omission and must not be "completed".

## `__tee_shm_dma_buf_mmap(struct dma_buf *dmabuf, struct vm_area_struct *vma)`

```c
shm  = dmabuf->priv;
size = vma->vm_end - vma->vm_start;
prot = (shm->flags & TEE_SHM_CACHED) ? vma->vm_page_prot
                                     : pgprot_noncached(vma->vm_page_prot);
ret  = remap_pfn_range(vma, vma->vm_start, shm->paddr >> PAGE_SHIFT, size, prot);
if (!ret)
        vma->vm_private_data = shm;
return ret;
```

The non-cached constant is proven: stock computes `(vm_page_prot & ~0x10) | 0xc | PTE_PXN | PTE_UXN`, i.e. `AttrIndx = MT_DEVICE_nGnRnE` plus both execute-never bits — the exact expansion of `pgprot_noncached()` on arm64. `vm_private_data` is written **only** on success.

## `__tee_shm_dma_buf_release(struct dma_buf *dmabuf)`

```c
tee_shm_free_io(dmabuf->priv);
```

Nothing else — no logging, no context dereference. The donor additionally reads `shm->ctx->tee` purely for a debug print; that dereference is removed because stock does not perform it and it is an avoidable fault risk on a teardown path.

## Cached-mapping exports (contract for `tee_map_cached_shm` / `tee_unmap_cached_shm`)

```c
void *tee_map_cached_shm(unsigned long pa, size_t len)
{
        if (pfn_is_map_memory(__phys_to_pfn(pa)))
                return __va(pa);
        return ioremap_prot(pa, len, pgprot_val(PAGE_KERNEL));
}

void tee_unmap_cached_shm(void *va)
{
        iounmap((volatile void __iomem *)va);
}
```

Proof of the protection value: stock materialises `0x0068000000000703` and ORs `0x800` when `arm64_use_ng_mappings` is set. Decoded, that is `PTE_TYPE_PAGE | PTE_AF | PTE_SHARED | PTE_WRITE | PTE_PXN | PTE_UXN | PTE_MAYBE_NG` with `AttrIndx = MT_NORMAL` — i.e. `PAGE_KERNEL`, a **cached** mapping, which is what the function name promises. The `arm64_use_ng_mappings` test is the expansion of `PTE_MAYBE_NG`, so writing `pgprot_val(PAGE_KERNEL)` reproduces it exactly and portably.

The linear-map fast path is `__va(pa)`: stock computes `(pa - memstart_addr) | 0xffffff8000000000`, which is `__phys_to_virt`.

Both functions are `EXPORT_SYMBOL` in stock and are consumed by `tkcore_drv`.
