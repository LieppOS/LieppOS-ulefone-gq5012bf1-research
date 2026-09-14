# GQ5012BF1 tkcore island Phase 3B — tkcore_drv static shared-memory trace

**Result: PASS_STATIC_SHM**

Offline trace of the frozen stock provider. `tkcore_drv` was not modified, rebuilt, or loaded.

## Consumer oracle

- Module: `workspace/phase4-tkcore-drv/oracle/tkcore_drv.ko`
- SHA-256: `c13503baf7c13828d0d666cbd364d8cadaa7d1282442405c72d28073bd51235d`
- Disassembly: `workspace/phase4-tkcore-island/phase3b/tkcore_drv.objdump.txt`

## Shared-memory edges into tkcore

Every relocation from `tkcore_drv` into the tkcore shared-memory surface:

| Consumer function | Offset | tkcore export | Status |
|---|---:|---|---|
| `tz_start` | `0x148` | `tee_map_cached_shm` | present, **EXACT_BYTE** |
| — | — | `tee_unmap_cached_shm` | **NOT_CALLED** by this consumer |

That is the complete list. `tkcore_drv` imports no other tkcore shared-memory symbol.

### `tee_unmap_cached_shm` is genuinely unreferenced

There is no `R_AARCH64_CALL26` to `tee_unmap_cached_shm` anywhere in frozen `tkcore_drv`. The function is nevertheless reconstructed, exported, and byte-identical to stock, because stock exports it and some other consumer or a later teardown path may use it.

This is recorded as **NOT_CALLED**, not as a pass. It is the same honest accounting applied to `tee_core_free` in Phase 3A-R: a closed, exported API with no natural call edge in the frozen provider is reported as such rather than being written up as a verified edge.

### `tee_shm_pool_set_cached` / `tee_shm_pool_is_cached`

These appear in `tkcore_drv`'s relocations but are **`tkcore_drv`'s own internal functions**, not tkcore exports — stock tkcore neither defines nor exports them. They are listed here only to pre-empt the misreading that Phase 3B left two shared-memory symbols unimplemented.

## Call-site contract for `tee_map_cached_shm`

```text
 130: w8  = 1
 138: x0  = x20                     ; pa
 13c: x1  = x21                     ; len
 140: strb w8, [x23, #0x20]!        ; pool->cached = true
 144: stur x20, [x23, #-0x10]       ; pool->paddr  = pa
 148: bl   tee_map_cached_shm
 14c: stur x0,  [x23, #-0x8]        ; pool->vaddr  = returned VA
 150: cbz  x0, <failure>            ; NULL is the only failure signal
```

Confirmed properties, all satisfied by the reconstruction:

- **Signature** `void *tee_map_cached_shm(unsigned long pa, size_t len)` — two integer arguments, pointer return. Island KCFI `0x455697f2` matches stock exactly.
- **Failure convention** is a plain `NULL`, never an `ERR_PTR`. Both stock branches satisfy this: `__va()` cannot return NULL for a valid mapped PFN, and `ioremap_prot()` returns NULL on failure.
- **The provider caches the returned VA itself** (`pool->vaddr`) and pairs it with the physical address it passed in. tkcore stores nothing; it owns no object on this path, which matches the Phase-3B lifetime model's class B.
- The provider marks the pool `cached = true` before the call, consistent with the function contracting for a **cached** (`MT_NORMAL` / `PAGE_KERNEL`) mapping rather than a device mapping.

## ABI summary

| Export | Stock size | Island size | Stock KCFI | Island KCFI | Class |
|---|---:|---:|---|---|---|
| `tee_map_cached_shm` | 112 | 112 | `0x455697f2` | `0x455697f2` | **EXACT_BYTE** |
| `tee_unmap_cached_shm` | 28 | 28 | `0xa488ebfc` | `0xa488ebfc` | **EXACT_BYTE** |

Both are emitted into `__ksymtab` (non-GPL `EXPORT_SYMBOL`, matching stock's `___ksymtab+tee_map_cached_shm` section form). Export count moved 19/25 → 21/25 with nothing fabricated.

## Scope boundary

This report does not build `tkcore_drv` against the island and does not claim natural-link acceptance. Four stock exports (`tee_clkmgr_handle`, `tee_spi_cfg_padsel`, `tee_spi_transfer`, `tee_spi_transfer_disable`) are still absent, so a natural link is still impossible by construction.

## Verdict

The single real shared-memory edge resolves to a byte-identical export with matching KCFI and a satisfied failure convention; the one unreferenced export is accurately accounted rather than inflated into evidence.

**PASS_STATIC_SHM**
