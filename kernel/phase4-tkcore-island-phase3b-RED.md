# GQ5012BF1 tkcore island Phase 3B — RED (pre-implementation evidence)

Frozen **before** any Phase-3B source edit. This file is historical and must not be rewritten after implementation.

- Research HEAD at capture: `26977fef2da90df49f7aaca97d795c5f995f6e91`
- Stock oracle: `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` (221352 bytes, 122 functions)
- Island baseline (Phase-3A-R): `9c6da05d238033de2a70b96c34bcbc081a9b62d13f64b72aee1713e86665315b` (164032 bytes, 103 functions)
- Baseline build: `BUILD_RC=0`, 0 warnings, 0 errors, 0 modpost warnings, 0 unresolved, layout probe PASS, Phase-3A-R verifier 158/158 PASS.

## A. The 12 target stock functions — all ABSENT from the island

| # | stock function | stock offset | stock size | stock KCFI | stock call set | island state |
|---|---|---:|---:|---|---|---|
| 1 | `__tee_shm_attach_dma_buf` | `0x63ec` | 92 | `0x975557fe` | `devm_kmalloc` | **MISSING** |
| 2 | `__tee_shm_detach_dma_buf` | `0x644c` | 132 | `0x90d39919` | `dma_unmap_sg_attrs`, `sg_free_table`, `devm_kfree`, `_printk` | **MISSING** |
| 3 | `__tee_shm_dma_buf_map_dma_buf` | `0x64d4` | 308 | `0x7c6e5fbe` | `sg_alloc_table`, `sg_next`×2, `dma_map_sg_attrs`, `_printk`×2, `sg_free_table` | **MISSING** |
| 4 | `__tee_shm_dma_buf_unmap_dma_buf` | `0x660c` | 4 | `0xc0a08c9a` | (none — bare `ret`) | **MISSING** |
| 5 | `__tee_shm_dma_buf_mmap` | `0x6638` | 104 | `0xe4d3eb24` | `remap_pfn_range` | **MISSING** |
| 6 | `__tee_shm_dma_buf_release` | `0x6614` | 32 | `0xa80f535b` | `tee_shm_free_io` | **MISSING** |
| 7 | `tee_map_cached_shm` | `0x1c` | 112 | `0x455697f2` | `pfn_is_map_memory`, `ioremap_prot` | **MISSING** |
| 8 | `tee_unmap_cached_shm` | `0x90` | 28 | `0xa488ebfc` | `iounmap` | **MISSING** |
| 9 | `tkcore_alloc_shm` | `0x57fc` | 408 | `0x45b20ce9` | `sg_alloc_table_from_pages_segment`, `_printk`×3, `__stack_chk_fail` | **MISSING** |
| 10 | `tkcore_shm_get` | `0x6084` | 672 | `0x00b73c2b` | `mutex_lock`, `kmalloc_trace`×2, `dma_buf_get`, `dma_buf_attach`, `dma_buf_map_attachment`, `sg_nents`, `dma_buf_unmap_attachment`, `dma_buf_detach`, `dma_buf_put`, `kfree`×2, `mutex_unlock`×2, `_printk`×5 | **MISSING** |
| 11 | `tkcore_shm_put` | `0x6328` | 192 | `0x2309a7a5` | `mutex_lock`, `dma_buf_unmap_attachment`, `dma_buf_detach`, `dma_buf_put`, `kfree`×2, `mutex_unlock` | **MISSING** |
| 12 | `tkcore_shm_free` | `0x5998` | 116 | `0xa7e6969f` | `sg_free_table` | **MISSING** |

Binding facts: the six `__tee_shm_*` callbacks are **LOCAL** (static) in stock; the four `tkcore_*` are **GLOBAL** but not exported; only `tee_map_cached_shm` and `tee_unmap_cached_shm` appear in `__ksymtab`.

## B. Not "absent" but *misnamed* — the real starting position

The island is **not** empty here. It carries OP-TEE-donor equivalents under different symbol names. This is a rename-plus-correct problem, not a from-scratch problem, and RED records it honestly:

| island donor symbol | island size | stock symbol | stock size |
|---|---:|---|---:|
| `_tee_shm_attach_dma_buf` | 92 | `__tee_shm_attach_dma_buf` | 92 |
| `_tee_shm_detach_dma_buf` | 116 | `__tee_shm_detach_dma_buf` | 132 |
| `_tee_shm_dma_buf_map_dma_buf` | 328 | `__tee_shm_dma_buf_map_dma_buf` | 308 |
| `_tee_shm_dma_buf_unmap_dma_buf` | 4 | `__tee_shm_dma_buf_unmap_dma_buf` | 4 |
| `_tee_shm_dma_buf_mmap` | 104 | `__tee_shm_dma_buf_mmap` | 104 |
| `_tee_shm_dma_buf_release` | 32 | `__tee_shm_dma_buf_release` | 32 |
| `_tee_shm_dma_buf_vmap` | 36 | *(no stock counterpart)* | — |
| `_tee_shm_dma_buf_vunmap` | 4 | *(no stock counterpart)* | — |
| `tee_shm_alloc` | 432 | `tkcore_alloc_shm` | 408 |
| `tee_shm_free` | 128 | `tkcore_shm_free` | 116 |
| `tee_shm_get` | 696 | `tkcore_shm_get` | 672 |
| `tee_shm_put` | 152 | `tkcore_shm_put` | 192 |

Two donor callbacks (`vmap`, `vunmap`) have **no stock counterpart** and must be removed, not kept.

## C. The three public TEEC SHM APIs — present but not behaviourally closed

| API | stock offset | stock size | island size | stock KCFI | island call set vs stock |
|---|---:|---:|---:|---|---|
| `TEEC_RegisterSharedMemory` | `0x77d4` | 32 | 28 | `0x102c9243` | both empty |
| `TEEC_AllocateSharedMemory` | `0x77f8` | 224 | 220 | `0x102c9243` | same names |
| `TEEC_ReleaseSharedMemory` | `0x78dc` | 80 | 64 | `0x0dc79758` | island lacks the flag guard |

### Concrete pre-existing defects proven from stock

1. **`TEEC_RegisterSharedMemory` is incomplete.** Stock performs two stores — a 32-bit `0` into `TEEC_SharedMemory.d` (`+0x18`) and a 64-bit `1` into `registered` (`+0x20`). The island writes only `registered`, leaving `d` stale.

2. **`TEEC_ReleaseSharedMemory` truncates a kernel pointer.** Stock loads the full 64-bit `struct tee_shm *` from `+0x18` (`ldr x0,[x19,#0x18]`). The island does `(struct tee_shm *)(long)shared_memory->d.fd`, i.e. an `int`→pointer cast — the same truncation class the Phase-3A-R IDR work eliminated elsewhere. The island also omits stock's mandatory `TEEC_MEM_KAPI` guard and its `BUG()` on violation.

3. **`TEEC_AllocateSharedMemory` dereferences uninitialized stack.** Stock zeroes all 24 bytes of `struct tee_shm_io`, and stock `tee_shm_alloc_io` publishes the resulting `struct tee_shm *` into `shm_io->buffer` (offset 0) on the kernel-client path (`5e70: str x20, [x23]`). The island's `tee_shm_alloc_io` performs **no such store**, and the island's `TEEC_AllocateSharedMemory` neither zeroes `shm_io` nor reads offset 0 — it reads `shm_io.fd_shm`, which on a kernel client is never written by either branch. It then dereferences that value via `shm->kaddr`.

   This is a genuine uninitialized-pointer dereference on the kernel allocation path, and it exists precisely because the Phase-3B helper chain was absent. Stock supplies the exact fix.

## D. dma_buf_ops table

Stock exports one `const` table, `tee_static_shm_dma_buf_ops`, 144 bytes in `.rodata+0x420`, with exactly six populated slots:

| slot | callback |
|---|---|
| `+0x08` | `attach` |
| `+0x10` | `detach` |
| `+0x28` | `map_dma_buf` |
| `+0x30` | `unmap_dma_buf` |
| `+0x38` | `release` |
| `+0x60` | `mmap` |

`cache_sgt_mapping` at `+0x00` is `false`. `mmap` at `+0x60` (rather than mainline's `+0x50`) reflects the Android GKI `begin/end_cpu_access_partial` additions. All other slots are NULL — notably `vmap`/`vunmap`, which the donor populates.

## E. RED verdict

- 12 / 12 target stock functions absent under their stock names.
- 2 donor callbacks present that stock does not have.
- 3 public TEEC SHM APIs present but each provably divergent, one with an uninitialized-pointer dereference.
- `tee_map_cached_shm` / `tee_unmap_cached_shm` absent from `__ksymtab` (19/25 exports).

**Phase 3B is required. Nothing in this section is speculative; every claim above is read from the stock ELF or the island ELF.**
