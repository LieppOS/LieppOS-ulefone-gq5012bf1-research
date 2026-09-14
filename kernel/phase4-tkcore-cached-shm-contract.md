# GQ5012BF1 tkcore cached shared-memory export contract

`tee_map_cached_shm` and `tee_unmap_cached_shm` — the two shared-memory symbols stock exports. Both are **byte-identical** to stock in Phase 3B.

## ABI

| Function | Stock offset | Size | KCFI | Export | Class |
|---|---:|---:|---|---|---|
| `tee_map_cached_shm` | `0x1c` | 112 | `0x455697f2` | `__ksymtab` (`EXPORT_SYMBOL`) | **EXACT_BYTE** |
| `tee_unmap_cached_shm` | `0x90` | 28 | `0xa488ebfc` | `__ksymtab` (`EXPORT_SYMBOL`) | **EXACT_BYTE** |

Prototypes (frozen as PROVEN_EXACT in `trustkernel/tee_shm.h` since the ABI-witness work):

```c
void *tee_map_cached_shm(unsigned long pa, size_t len);
void  tee_unmap_cached_shm(void *va);
```

Both land in `__ksymtab`, not `__ksymtab_gpl`, matching stock's `___ksymtab+tee_map_cached_shm` section form — i.e. plain `EXPORT_SYMBOL`.

## Implementation

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

## Why `PAGE_KERNEL` is the exact protection value

Stock materialises `0x0068000000000703` and ORs `0x800` when `arm64_use_ng_mappings` is set:

| Bits | Meaning |
|---|---|
| `0x3` | `PTE_TYPE_PAGE` |
| `0x300` | `PTE_SHARED` (inner shareable) |
| `0x400` | `PTE_AF` (access flag) |
| AttrIndx (bits 2–4) = `0` | `MT_NORMAL` → **cached** |
| `1 << 51` | `PTE_WRITE` (DBM) |
| `1 << 53` | `PTE_PXN` |
| `1 << 54` | `PTE_UXN` |
| `0x800` when `arm64_use_ng_mappings` | `PTE_NG` |

That set is precisely `PAGE_KERNEL`, and the runtime `arm64_use_ng_mappings` test is the expansion of `PTE_MAYBE_NG`. Writing `pgprot_val(PAGE_KERNEL)` reproduces the constant **and** the conditional without hardcoding a magic number — and it is why `arm64_use_ng_mappings` appears as a new (stock-present) import.

`MT_NORMAL` is the load-bearing part: this is a *cached* mapping, as the function name promises, not a device mapping.

## Why the fast path is `__va(pa)`

Stock computes `(pa - memstart_addr) | 0xffffff8000000000`, which is `__phys_to_virt(pa)`. When the physical address is already covered by the kernel linear map, no new mapping is created and the linear-map address is returned directly.

## Deliberately reproduced asymmetry

The linear-map branch creates **no** mapping, yet `tee_unmap_cached_shm` calls `iounmap()` unconditionally. This is safe because arm64's `iounmap()` ignores addresses that are not in the vmalloc range, and it is exactly what stock does. No guard that stock lacks was added.

## Failure convention

`NULL`, never an `ERR_PTR`. Both branches satisfy this: `__va()` cannot yield NULL for a valid mapped PFN, and `ioremap_prot()` returns NULL on failure. The frozen `tkcore_drv` relies on this — `tz_start` tests the result with `cbz x0` alone.

## Consumer

`tkcore_drv:tz_start` at `0x148`:

```text
pool->cached = true
pool->paddr  = pa
va = tee_map_cached_shm(pa, len)
pool->vaddr  = va
if (!va) -> failure path
```

The provider caches the returned VA itself; tkcore stores nothing and owns nothing on this path.

`tee_unmap_cached_shm` has **no caller** in the frozen `tkcore_drv` and is recorded as NOT_CALLED rather than being written up as a verified edge. It is nevertheless implemented and exported because stock exports it.

## CRC note

Both symbols' historical stock export CRCs were already naturally reproducible from the existing common headers in the earlier ABI-witness work. Phase 3B changed nothing about that: no CRC was injected, no `__versions` entry was edited, no `kcrctab` was touched, and no export name was fabricated. Export count moved 19/25 → 21/25 purely by implementing the two functions.
