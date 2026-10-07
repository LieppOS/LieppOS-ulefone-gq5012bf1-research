# TKCore shared memory (normal-world side)

| region | allocation | size | mapping / cache | registered with secure world | owner |
|---|---|---|---|---|---|
| shared window ("shm pool") | DT reserved-memory `tkcore_shared_mem` (`trustkernel,shared_mem`, dynamic, `no-map`, 1–3 GiB window) via `of_reserved_mem_lookup`; fallback `__get_free_pages(GFP_KERNEL, 10)` | 32 MiB (DT) / 4 MiB (fallback) | `tee_map_cached_shm()` (tkcore.ko export, cacheable kernel mapping); fallback is linear-map memory (`__pa`) | fast call `0xf2005704` (PA, length, cacheable=1) — physical address handed over directly (no FF-A MEM_SHARE) | tkcore_drv pool |
| pool chunks | `tkcore_shm_pool_alloc(dev, pool, size, align)`: ordered first-fit chunk list (`struct shm_pool`, `devm`), per-chunk refcount, `pool->lock` mutex | page-rounded for `tz_alloc`, 8-byte aligned for RPC args, 4 KiB for `alloc_tee_arg` | addresses converted with `tee_shm_pool_p2v/v2p` (range-checked, "not in the shm pool" errors) | implicitly (inside the registered window) | tkcore_drv |
| command buffers | `teesmc64_arg` (+ params, 0x30 + n·0x18) and `teesmc_meta_open_session` (36 B) from the pool | per call | cached | passed by PA in a1 | tkcore_drv |
| RPC argument buffers | secure world asks via RPC ALLOC_ARG (0xffff0000), freed via FREE_ARG | per request | cached | PA returned in a1 | tkcore_drv pool on behalf of the secure OS |
| client shared memory | `TEE_ALLOC_SHM_IOC` → `tz_alloc` → pool chunk; exported to userspace as an fd by tkcore (dma-buf, mmap by userspace through tkcore) | page-rounded | `TEE_SHM_CACHED` flag set because the pool is cached | memref attr `(0xa << 4)` (inner/outer write-back) and PA | tkcore (fd) / tkcore_drv (memory) |
| supplicant payload | RPC 0xffff5700 → `tee_supp_cmd(ALLOCATE)` → teed allocates via tkcore → shm; cookie in the handle DB (`handle_get`, start 4 slots, doubling) | per request | per tkcore | PA + cookie returned | teed/tkcore |
| secure log ring | `__get_free_pages(GFP_KERNEL, 5)` | 128 KiB | linear map | fast call `0xf2005705` with `virt_to_phys(ring)` | tkcore drains it |

Not present in tkcore_drv: page pinning of user memory (`pin_user_pages`/`get_user_pages`),
user mappings (`mmap`), DMA API / coherent allocations, explicit cache maintenance
(`dcache_*`, `dma_sync_*`), FF-A memory-sharing ABIs (`memory_share`/`reclaim`; the public
source keeps them behind `USE_FFA_MEM_SHARE_API`, not compiled in either version). Coherency
relies on both worlds mapping the window cacheable (shareable normal memory).

## Ownership boundary

| NORMAL WORLD KNOWN | SECURE WORLD OPAQUE |
|---|---|
| window base/size, registration call, pool allocator, every chunk's PA/size/refcount, arg/meta/param layouts (`teesmc64_arg`, `teesmc_meta_open_session`), RPC protocol, log ring placement | how TKCore maps the window (attributes, VA), which secure objects live in RPC-allocated buffers, the internal format of the log ring, secure-side validation of PAs |
