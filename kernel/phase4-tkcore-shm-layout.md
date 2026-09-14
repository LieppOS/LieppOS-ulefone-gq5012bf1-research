# GQ5012BF1 tkcore shared-memory type graph

Every offset below is read from the stock ELF (load/store displacement, relocation, or call-site argument), not inferred from the donor. Offsets marked **asserted** are enforced at compile time by `layout-assert.h` and fail the build if the island disagrees.

## `struct tee_shm` — size `0x68`

Proven by `kmalloc_trace(..., 0x68, ...)` in `tkcore_shm_get` (`60c8: mov w2, #0x68`).

| Offset | Width | Member | Meaning | Writer | Reader | Lock | Evidence |
|---:|---:|---|---|---|---|---|---|
| `0x00` | 16 | `entry` | context/RPC list linkage | `tee_shm_alloc_io`, `tee_shm_alloc_from_rpc` | `tee_shm_free_io` | `tee->lock` | `5ec4: stp x24,x22,[x20]` list insert |
| `0x10` | 8 | `ctx` | owning context | `tkcore_shm_get`, `tee_shm_alloc_io` | `tee_shm_free_io` | `tee->lock` | `5e74: str x21,[x20,#0x10]` |
| `0x18` | 8 | `tee` | owning provider | `tkcore_alloc_shm`, `tkcore_shm_get` | `__tee_shm_attach_dma_buf`, `__tee_shm_detach_dma_buf`, `tkcore_shm_free` | `tee->lock` | `58c4: str x19,[x20,#0x18]`; `640c: ldr x8,[x8,#0x18]` |
| `0x20` | 8 | `dev` | device reference held across the shm's life | `tee_shm_alloc_io` (`get_device`) | `tee_shm_free_io` (`put_device`) | `tee->lock` | `5e80: str x0,[x20,#0x20]` |
| `0x28` | 8 | `size_req` | requested size | `tkcore_shm_get`, provider | consumers | — | `60f8: stp x9,x24,[x20,#0x20]` |
| `0x30` | 8 | `size_alloc` | provider-allocated size | provider `ops->alloc` | `tkcore_shm_get` bounds check | — | `6138: ldr x1,[x8,#0x30]` |
| `0x38` | 4 | `flags` | `TEE_SHM_*` / `TEEC_MEM_*` | `tkcore_shm_get`, `tee_shm_alloc_io` | `__tee_shm_dma_buf_mmap`, `tkcore_shm_put` | `tee->lock` | `60fc: str w10,[x20,#0x38]` |
| `0x3c` | 4 | `pad_flags` | padding/reserved | — | — | — | never touched in stock |
| `0x40` | 8 | `kaddr` | kernel virtual address | provider | `TEEC_AllocateSharedMemory` | — | `7874: ldr x8,[x9,#0x40]` |
| `0x48` | 8 | `paddr` | physical address | provider, `tkcore_shm_get` | `tkcore_alloc_shm`, `__tee_shm_dma_buf_mmap` | — | `6224: str x8,[x20,#0x48]`; `6668: ldr x12,[x20,#0x48]` |
| `0x50` | 16 | `sgt` | scatter-gather table (`sgl@0x50`, `nents@0x58`, `orig_nents@0x5c`) | `tkcore_alloc_shm` | `__tee_shm_dma_buf_map_dma_buf` | — | `5894: add x0,x20,#0x50`; `6514: ldr w1,[x23,#0x5c]` |
| `0x60` | 8 | `sdb` | imported dma-buf record | `tkcore_shm_get` | `tkcore_shm_put` | `tee->lock` | `6184: str x22,[x20,#0x60]` |

The island's pre-existing `struct tee_shm` already matches **every** one of these offsets. No field was renamed or moved for Phase 3B.

## `struct tee_shm_attach` (per dma-buf attachment) — size `0x18`

Allocated by `__tee_shm_attach_dma_buf` with `devm_kmalloc(dev, 0x18, GFP_KERNEL|__GFP_ZERO)`.

| Offset | Width | Member | Meaning | Evidence |
|---:|---:|---|---|---|
| `0x00` | 16 | `sgt` | per-attachment `struct sg_table` | `6498: sg_free_table(x20)` where `x20` is the record base |
| `0x10` | 4 | `dir` | `enum dma_data_direction`, initialised to `DMA_NONE` | `642c: str w9,[x8,#0x10]` with `w9 = 3` |
| `0x14` | 1 | `is_mapped` | mapping already established | `650c: ldrb w8,[x19,#0x14]`, `65b4: strb w8,[x19,#0x14]` |

Because `sgt` is the first member, stock legitimately passes the record itself to `sg_free_table()`.

## `struct tee_shm_dma_buf` (imported buffer) — size `0x18`

Allocated by `tkcore_shm_get` with `kmalloc_trace(..., 0x18, GFP_KERNEL|__GFP_ZERO)`.

| Offset | Width | Member | Meaning | Evidence |
|---:|---:|---|---|---|
| `0x00` | 8 | `attach` | `struct dma_buf_attachment *` | `61a8: str x0,[x22]` after `dma_buf_attach` |
| `0x08` | 8 | `sgt` | `struct sg_table *` from `dma_buf_map_attachment` | `61c4: str x0,[x22,#0x8]` |
| `0x10` | 1 | `tee_allocated` | true when the imported buffer is itself a tkcore dma-buf | `6240: strb w8,[x22,#0x10]` from `cset` on `ops->attach == __tee_shm_attach_dma_buf` |

The `tee_allocated` flag is derived by comparing the foreign buffer's `dma_buf_ops->attach` against tkcore's own `__tee_shm_attach_dma_buf` (`6214: adrp x9, .text+0x63ec`). This is how stock recognises a buffer it exported itself.

## `TEEC_SharedMemory` — size `0x28`

| Offset | Width | Member | Evidence |
|---:|---:|---|---|
| `0x00` | 8 | `buffer` | `7878: str x8,[x19]`; `790c: str xzr,[x19]` |
| `0x08` | 8 | `size` | `7844: ldr x10,[x19,#0x8]` |
| `0x10` | 4 | `flags` | `783c: ldr w9,[x19,#0x10]`; byte `0x12` bit 1 = flags bit 17 (`TEEC_MEM_KAPI`) |
| `0x18` | 8 | `d` (union `{int fd; void *ptr;}`) | `7904: ldr x0,[x19,#0x18]` — read as a **full 64-bit pointer** |
| `0x20` | 8 | `registered` | `77e4: str x8,[x1,#0x20]` (u64 `1`); `78f4: ldr x8,[x0,#0x20]` |

The `d` union is written and read at 64-bit width by stock. Any `int`-mediated round trip truncates a kernel pointer; the island previously did exactly that and it is corrected in Phase 3B.

## `struct tee_shm_io` — size `0x18`

| Offset | Width | Member | Notes |
|---:|---:|---|---|
| `0x00` | 8 | `buffer` / `padding_buf` | **On the kernel-client path stock stores the resulting `struct tee_shm *` here** (`5e70: str x20,[x23]`) |
| `0x08` | 4 | `size` | `5dd8: ldp w1,w2,[x23,#0x8]` |
| `0x0c` | 4 | `flags` | same `ldp` |
| `0x10` | 4 | `fd_shm` | written only on the `usr_client` path (`5e5c: str w0,[x23,#0x10]`) |
| `0x14` | 4 | `registered` | |

This dual use of offset `0` is the key fact Phase 3B recovers: for a kernel client the field carries an object pointer, for a user client it carries nothing and `fd_shm` carries a descriptor.

## Flag bits, resolved against the island's existing constants

| Bit | Mask | Constant | Used by |
|---:|---|---|---|
| 16 | `0x00010000` | `TEEC_MEM_DMABUF` | set by `tkcore_shm_get`/`tee_shm_alloc_io`; tested by `tkcore_shm_put` (`ldrb [0x3a]`, bit 0) |
| 17 | `0x00020000` | `TEEC_MEM_KAPI` | selects the pointer path in `tkcore_shm_get` (`tbnz w8,#0x11`); guards `TEEC_ReleaseSharedMemory` (`ldrb [0x12]`, bit 1) |
| 28 | `0x10000000` | `TEE_SHM_MEMREF` | set unconditionally by `tkcore_shm_get`; `BUG()`-enforced by `tkcore_shm_put` (`ldrb [0x3b]`, bit 4) |
| 29 | `0x20000000` | `TEE_SHM_CACHED` | selects cached vs `pgprot_noncached` in `__tee_shm_dma_buf_mmap` (`tst w11,#0x20000000`) |

Every bit test in stock resolves to a constant the island already defines. None was invented.

## Referenced foreign layouts

These belong to the exact-GKI headers, so Phase 3B **asserts** them rather than assuming them:

| Type | Member | Offset | Evidence |
|---|---|---:|---|
| `struct dma_buf` | `priv` | `0xa0` | `63fc/664c/6620: ldr x?,[x0,#0xa0]` |
| `struct dma_buf` | `ops` | `0x20` | `6228: ldr x8,[x21,#0x20]` |
| `struct dma_buf` | `size` | `0x00` | `618c: ldr x1,[x21]` |
| `struct dma_buf_attachment` | `dmabuf` | `0x00` | `6378: ldr x22,[x0]` |
| `struct dma_buf_attachment` | `dev` | `0x08` | `6480: ldr x0,[x19,#0x8]` |
| `struct dma_buf_attachment` | `priv` | `0x40` | `6428: str x8,[x19,#0x40]` |
| `struct vm_area_struct` | `vm_page_prot` | `0x18` | `665c: ldr x10,[x19,#0x18]` |
| `struct vm_area_struct` | `vm_private_data` | `0x90` | `668c: str x20,[x19,#0x90]` |
| `struct tee` | `ops` / `dev` / `lock` | `0x90` / `0x98` / `0xf8` | carried over from Phase 3A-R, re-confirmed here |
| `struct tee_context` | `tee` / `usr_client` | `0x00` / `0x8c` | `60a0: ldr x25,[x0]`; `5df4: ldr w8,[x21,#0x8c]` |

## Provider ops slots re-confirmed

| Slot | Member | Signature | KCFI |
|---:|---|---|---|
| `0x40` | `ops->alloc` | `struct tee_shm *(*)(struct tee *, size_t, uint32_t)` | `0x45b20ce9` — identical to `tkcore_alloc_shm` |
| `0x48` | `ops->free` | `void (*)(struct tee_shm *)` | `0xa7e6969f` — identical to `tkcore_shm_free` |

The KCFI identity between each wrapper and the slot it dispatches through is itself the proof that the island's `struct tee_ops` prototypes are correct; a mismatched prototype would produce a different type id.
