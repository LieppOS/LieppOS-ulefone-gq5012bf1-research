# gz_main_mod — shared-memory and user-memory contract

Three distinct memory paths reach the secure world from this module. They are
not interchangeable and are documented separately.

Nothing in this report was executed: no secure memory was allocated, no
session opened, no FF-A call issued.

---

## Path 1 — GP bounce buffers (`MTEE_CMD_TEE_SERVICE`)

Used for `TZPT_MEM_INPUT` / `TZPT_MEM_OUTPUT` / `TZPT_MEM_INOUT` parameters.

| property | value |
|---|---|
| mechanism | `kmalloc` bounce buffer + `copy_from_user` / `copy_to_user` |
| pinning | none — the user page is never pinned |
| hard size limit | `GP_MEM_MAX_LEN` = **1024 bytes** per slot, else `-ENOMEM` |
| validation | `access_ok()` for read when type != OUTPUT, for write when type != INPUT |
| compat | `compat_ptr(oparam[i].mem32.buffer)` and `mem32.size` when entered through `gz_compat_ioctl` |
| lifetime | freed before the ioctl returns, on both success and the `error:` unwind |
| ownership | kernel owns the bounce buffer end-to-end; the secure world never sees the user page |

`TZPT_MEMREF_*` slots are **passed through unchanged** — they carry an
already-registered shared-memory handle rather than a user pointer, so no
bounce and no pinning occurs for them.

---

## Path 2 — registered shared memory (`MTEE_CMD_SHM_REG` → `_reg_shmem_from_userspace`)

This is the path that `gz_tz_system` exports `_map_user_pages` for. The
gz_tz_system userspace-ABI report notes that this export exists to pin user
pages *on behalf of a kernel caller*; **this function is that caller**, and it
is the only call site in the whole module (one `R_AARCH64_CALL26` relocation).

### Sequence

1. Reject `size <= 0` or NULL buffer → `TZ_RESULT_ERROR_BAD_PARAMETERS`.
2. `pin = kvmalloc(sizeof(struct MTIOMMU_PIN_RANGE_T))`; `pin->pageArray = NULL`.
3. `_map_user_pages(pin, untagged_addr(buffer), size, /*control=*/0)`
   * `untagged_addr()` strips an MTE/TBI top-byte tag before the range is used.
   * On failure `pin->pageArray` is reset to NULL and
     `TZ_RESULT_ERROR_INVALID_HANDLE` is returned.
   * A NULL `pageArray` on apparent success is treated as
     `TZ_RESULT_ERROR_GENERIC`.
4. Build the physical-address table:
   * `map_p = kvmalloc(sizeof(uint64_t) * (nrPages + 1))`
   * `map_p[0] = nrPages` — **the element count is stored in slot 0**, the PAs
     follow from index 1. This is a length-prefixed array, not a
     scatter/run-length encoding.
   * If `pin->isPage`, entries come from `PFN_PHYS(page_to_pfn(page[i]))`;
     otherwise `pin->pageArray` is a raw pfn array and entries come from
     `PFN_PHYS(pfns[i])`. Both variants are compiled in.
5. `shm_param = { .buffer = NULL, .size = 0, .mapAry = map_p, .region_id = … }`
   and `KREE_RegisterSharedmem(session, shm_handle, &shm_param)`.
6. `kvfree(map_p)` immediately after registration — the secure world has
   already consumed the table.
7. `us_map_fail:` unwind, taken on **every** exit including success:
   * if `pin->pageArray`, and `pin->isPage`, `put_page()` each of the
     `nrPages` pages;
   * `kfree(pin->pageArray)`;
   * `kvfree(pin)`.

### Consequences worth stating

* A 32 KB soft-warning threshold exists for both `pin` and `map_p`
  (`SZ_32KB`), but in stock **both over-size checks only log** — the
  `return`/`goto` lines are commented out in the vendor source. Large
  registrations are therefore not rejected here.
* The pages are released before the ioctl returns. The unregister path
  (`KREE_UnregisterSharedmem`, 2 relocations) tears down the secure-side
  handle; it does not need to re-release Linux pages.
* `__folio_put` and `__page_pinner_put_page` are imported and
  `page_pinner_inited` is referenced — these are the GKI page-pinner
  accounting hooks reached through `put_page()`.

---

## Path 3 — dma-buf → secure handle (`MTEE_CMD_GET_CHM_HANDLE` → `DMAFd2MemHandle`)

| step | call | provider |
|---|---|---|
| 1 | `dma_buf_get(buf_fd)` | GKI |
| 2 | `dmabuf_to_secure_handle(dmabuf)` | **mtk_sec_heap** (the single stock-runtime edge) |
| 3 | `dma_buf_put(dmabuf)` | GKI |

The resulting `secm_handle` is copied back to userspace. The module declares
`MODULE_IMPORT_NS(DMA_BUF)`, which is why stock `.modinfo` carries
`import_ns=DMA_BUF`. No mapping is created and no page is pinned; the secure
handle refers to memory already owned by a secure heap.

---

## Chunk-memory and SSMR (unit-test paths)

`gz_chmem_ut.o` reaches secure chunk memory through
`KREE_ION_AllocChunkmem`, `KREE_ION_ZallocChunkmem`,
`KREE_ION_ReferenceChunkmem`, `KREE_ION_UnreferenceChunkmem`,
`KREE_ION_QueryChunkmem_TEST`, `KREE_AppendSecureMultichunkmem`,
`KREE_ReleaseSecureMultichunkmem`, and brackets them with `ssmr_offline()` /
`ssmr_online()` from **tmem_ffa**. These are reachable only by writing `4` to
the `gz_test` sysfs attribute, never by ioctl.

---

## What this module does NOT do

| capability | state | evidence |
|---|---|---|
| `mmap` of the device | **absent** | no `.mmap` in either `file_operations` |
| direct dma-buf export | absent | no `dma_buf_export`/`dma_buf_fd` import |
| long-lived page pinning across ioctls | absent | every pin is released in `us_map_fail` before return |
| cache maintenance | absent | no `dma_sync_*`/`__flush_dcache_area` import |
| IOMMU/M4U mapping | absent | `CONFIG_GZ_VPU_WITH_M4U` off; no `gz_do_m4u_map` reference |

Memory is therefore shared with the secure world by **physical-address table**
or by **secure heap handle**, never by mapping secure memory into a user
address space.
