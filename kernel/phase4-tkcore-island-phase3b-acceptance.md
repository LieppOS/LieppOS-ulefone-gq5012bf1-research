# GQ5012BF1 tkcore island Phase 3B — shared-memory acceptance

## Result

**TKCORE_ISLAND_PHASE3B_SHARED_MEMORY_CLOSED**

The Linux-side shared-memory / dma-buf subsystem is statically reconstructed against the stock oracle. This does **not** mean tkcore is complete, replacement-ready, runtime validated, secure-world tested, or naturally linked by its consumers.

## Acceptance classes — no `INCOMPLETE`, no `STRUCTURAL_ONLY`

Every one of the 15 in-scope functions has **exact KCFI** and an **exact stock call multiset**.

### dma-buf callbacks — all byte-identical

| Function | Stock / island size | Class |
|---|---:|---|
| `__tee_shm_attach_dma_buf` | 92 / 92 | **EXACT_BYTE** |
| `__tee_shm_detach_dma_buf` | 132 / 132 | **EXACT_BYTE** |
| `__tee_shm_dma_buf_map_dma_buf` | 308 / 308 | **EXACT_BYTE** |
| `__tee_shm_dma_buf_unmap_dma_buf` | 4 / 4 | **EXACT_BYTE** |
| `__tee_shm_dma_buf_mmap` | 104 / 104 | **EXACT_BYTE** |
| `__tee_shm_dma_buf_release` | 32 / 32 | **EXACT_BYTE** |

### Cached-SHM exports — both byte-identical

| Function | Stock / island size | Class |
|---|---:|---|
| `tee_map_cached_shm` | 112 / 112 | **EXACT_BYTE** |
| `tee_unmap_cached_shm` | 28 / 28 | **EXACT_BYTE** |

### tkcore internal SHM lifetime

| Function | Stock / island size | Class |
|---|---:|---|
| `tkcore_shm_get` | 672 / 672 | **EXACT_BYTE** |
| `tkcore_alloc_shm` | 408 / 432 | CFG_EQUIVALENT |
| `tkcore_shm_put` | 192 / 172 | CFG_EQUIVALENT |
| `tkcore_shm_free` | 116 / 112 | CFG_EQUIVALENT |

### Public TEEC SHM APIs

| Function | Stock / island size | Class |
|---|---:|---|
| `TEEC_RegisterSharedMemory` | 32 / 32 | **EXACT_BYTE** |
| `TEEC_AllocateSharedMemory` | 224 / 228 | CFG_EQUIVALENT |
| `TEEC_ReleaseSharedMemory` | 80 / 76 | CFG_EQUIVALENT |

Totals: **10 EXACT_BYTE, 5 CFG_EQUIVALENT, 0 INCOMPLETE.**

`sg_nents` was additionally closed (56 / 56, **EXACT_BYTE**) because `tkcore_shm_get` calls it directly and stock carries its own WEAK definition; reproducing it removed a non-stock import.

## What Phase 3B actually was

Not a from-scratch implementation. The island already carried OP-TEE-donor equivalents under different names. Phase 3B renamed them to stock symbols **and** corrected them against the stock oracle:

| Donor symbol | Stock symbol |
|---|---|
| `_tee_shm_attach_dma_buf` … `_tee_shm_dma_buf_release` | `__tee_shm_*` (double underscore) |
| `tee_shm_alloc` / `tee_shm_free` | `tkcore_alloc_shm` / `tkcore_shm_free` |
| `tee_shm_get` / `tee_shm_put` | `tkcore_shm_get` / `tkcore_shm_put` |
| `_tee_shm_dma_buf_ops` (`.data`) | `tee_static_shm_dma_buf_ops` (`const`, `.rodata`) |

Two donor callbacks — `.vmap` and `.vunmap` — have **no stock counterpart** and were removed rather than retained.

## Defects found and fixed, each proven from stock

1. **`TEEC_AllocateSharedMemory` dereferenced uninitialized stack.** Stock `tee_shm_alloc_io` publishes the allocated `struct tee_shm *` through `shm_io->buffer` (offset 0) on the kernel-client path (`5e70: str x20,[x23]`). The island performed no such store, and `TEEC_AllocateSharedMemory` read `shm_io.fd_shm` — written only on the *user*-client path — then dereferenced it via `shm->kaddr`. Both halves are corrected, and `shm_io` is now fully zeroed as stock does.

2. **`TEEC_ReleaseSharedMemory` truncated a kernel pointer** through `int d.fd`, and omitted stock's `TEEC_MEM_KAPI` guard. Both fixed; the handle is now read at full 64-bit width via `d.ptr`.

3. **`TEEC_RegisterSharedMemory` left a stale handle.** Stock performs two stores; the island performed one. The missing 32-bit zero into `d` is restored.

4. **`tkcore_alloc_shm` wrote through an error pointer.** The donor assigned `shm->tee` immediately after `ops->alloc`, before validating the result. Stock assigns it last, on every path, guarded by `!IS_ERR_OR_NULL`.

5. **`tkcore_shm_put` dereferenced `shm` before its own NULL check** (inside a debug print). Stock's guard order — `ctx`, `ctx->tee`, `shm`, then the `TEE_SHM_MEMREF` flag — is restored.

## Ownership model, stated explicitly

| Question | Answer |
|---|---|
| Who owns allocated memory? | the provider backend, via `ops->alloc` / `ops->free` |
| Who owns the `tee_shm` object? | the context (`ctx->list_shm`) — except memref shm, which the command owns |
| Who owns an **exported** dma_buf? | userspace, via the fd; `.release` then destroys the shm |
| Who owns an **imported** dma_buf reference? | the `tee_shm`, via `dma_buf_get` / `dma_buf_put` |
| Who owns the attachment? | the `tee_shm_dma_buf` record, `kfree`d after `dma_buf_detach` |
| Who owns the mapped `sg_table`? | **the exporter** — returned via `dma_buf_unmap_attachment`; tkcore never frees it |
| Which lock guards list membership? | `tee->lock` |

`get`/`put` (reference to foreign memory) and `alloc`/`free` (object the provider owns) are kept as distinct axes and never merged, despite the donor conflating them.

## Stock quirks reproduced rather than "fixed"

- `tkcore_alloc_shm` builds an sg-table describing exactly **one** `PAGE_SIZE` page regardless of the requested size.
- Its failure paths return the offending `struct page *` cast to `struct tee_shm *`, not a uniform errno.
- `__tee_shm_dma_buf_unmap_dma_buf` is an intentional 4-byte no-op; teardown is deferred to `.detach`.
- `map_dma_buf` uses `orig_nents` while `detach` unmaps with `nents`.
- `tee_unmap_cached_shm` calls `iounmap()` unconditionally, including for linear-mapped addresses (safe on arm64, and what stock does).
- `TEEC_ReleaseSharedMemory` checks `registered` **before** the `TEEC_MEM_KAPI` guard — load-bearing, because `tmem_ffa` registers with `flags = 3` and would otherwise `BUG()` on every session teardown.

## Layout

Layout anchors moved 51 → **83**, all build-enforced and all passing, plus 7 island-local `static_assert`s in `tee_shm.c`. New coverage: full `struct tee_shm` (0x68), `tee_shm_dma_buf` (0x18), `tee_shm_attach` (0x18), `tee_shm_io` (0x18), `TEEC_SharedMemory.d`/`registered`, and the foreign `dma_buf` / `dma_buf_attachment` / `vm_area_struct` / `dma_buf_ops` offsets the stock code depends on.

The `dma_buf_ops` table is built with **designated initialisers**; its six relocation offsets were then verified equal to stock's (`+0x08`, `+0x10`, `+0x28`, `+0x30`, `+0x38`, `+0x60`) with no extra slots. Nothing was hardcoded.

## Static consumer traces

- `tmem_ffa`: **PASS_STATIC_SHM** — full `Initialize → Register → OpenSession → CloseSession → Release → Finalize` lifecycle.
- `tkcore_drv`: **PASS_STATIC_SHM** — its single `tee_map_cached_shm` edge; `tee_unmap_cached_shm` honestly recorded as NOT_CALLED.

## Forbidden techniques

None used: no speculative success stub, no fake provider, no stock object inclusion, no CRC injection, no `__versions` edit, no `kcrctab` edit, no ELF patch, no `KBUILD_MODPOST_WARN`, no forced symvers fabrication.

## Status — unchanged at the top level

- Overall tkcore: **PARTIAL**
- Runtime readiness: **NOT RUNTIME READY**
- Runtime provider: **STOCK RUNTIME PROVIDER**
- Replacement ready: **NO**
- Next: **PHASE 3C IOCTL / COMMAND-MARSHALLING RECONSTRUCTION**
