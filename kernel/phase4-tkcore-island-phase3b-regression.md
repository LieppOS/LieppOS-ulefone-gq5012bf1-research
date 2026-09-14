# GQ5012BF1 tkcore island Phase 3B — three-way regression

Stock vs Phase-3A-R vs Phase-3B. All figures are measured from the ELFs, not predicted.

## Identity

| ELF | SHA-256 | Size |
|---|---|---:|
| stock | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` | 221352 |
| Phase-3A-R | `9c6da05d238033de2a70b96c34bcbc081a9b62d13f64b72aee1713e86665315b` | 164032 |
| Phase-3B | `860ad5ee0c4da579627c202b19892b20e44ef34287054f11ab802b09e9933640` | 166120 |

Phase-3B module metadata: Build ID `f2ac7127bf1efe6590cbf97bd33fb7ddae8c7e19`, `srcversion` `0930BDEBAEE73D3CE34B030`, vermagic `6.1.115-android14-11-maybe-dirty SMP preempt mod_unload modversions aarch64`, `depends` **empty**, `license=GPL`.

## Headline movement

| Metric | Stock | Phase-3A-R | Phase-3B | Δ |
|---|---:|---:|---:|---|
| stock-function coverage | 122 | 91 | **104** | +13 |
| stock functions missing | 0 | 31 | **18** | −13 |
| byte-identical to stock | 122 | 33 | **44** | +11 |
| exports | 25 | 19 | **21** | +2 |
| undefined imports | 100 | 94 | 97 | +3 |
| defined objects | 54 | 50 | 50 | 0 |
| relocations | 3098 | 2288 | 2309 | +21 |
| total defined functions | 122 | 103 | 104 | +1 |
| **island-only functions** | 0 | 12 | **0** | −12 |

The last row is the most informative. Phase-3A-R carried 12 functions that existed under donor names with no stock counterpart. Phase 3B did not add 13 brand-new functions on top of them — it **renamed and corrected** those donor functions into their stock identities. Every function the island now defines is a stock function.

## Newly present stock functions (13)

`__tee_shm_attach_dma_buf`, `__tee_shm_detach_dma_buf`, `__tee_shm_dma_buf_map_dma_buf`, `__tee_shm_dma_buf_unmap_dma_buf`, `__tee_shm_dma_buf_mmap`, `__tee_shm_dma_buf_release`, `tee_map_cached_shm`, `tee_unmap_cached_shm`, `tkcore_alloc_shm`, `tkcore_shm_free`, `tkcore_shm_get`, `tkcore_shm_put`, `sg_nents`.

The nominal Phase-3B target was 12, giving 103/122. The measured result is **13, giving 104/122**, because `sg_nents` also closed: `tkcore_shm_get` calls it directly, and stock carries its own WEAK definition rather than importing the kernel's. Reproducing that both restored a stock function and removed a non-stock import. The extra function is therefore explained, not accidental.

## Remaining 18 missing stock functions

`__tee_shm_*` and `tkcore_*` are gone from this list. What remains is entirely outside Phase-3B scope:

- ioctl / command marshalling: `tee_internal_ioctl`, `tee_session_internal_ioctl`, `tee_session_compat_ioctl`, `tee_compat_ioctl`
- 32-bit compat: `convert_compat_tee_cmd`, `convert_compat_tee_shm_io`, `convert_compat_tee_spta_inst`
- clock runtime: `tee_clkmgr_handle`
- secure SPI proxy: `tee_spi_cfg_padsel`, `tee_spi_transfer`, `tee_spi_transfer_disable`
- platform / affinity / uaccess: `big_core_affinity_get_candidate_cpu`, `big_core_affinity_match_cpu`, `big_core_affinity_need_bind_cpu`, `plat_cpu_is_big`, `plat_tee_init`, `uaccess_ttbr0_disable`, `uaccess_ttbr0_enable`

## Byte-identical set: 33 → 44, nothing regressed

`BYTE_REGRESSED = []`. The 11 additions are the 6 dma-buf callbacks, both cached-SHM exports, `tkcore_shm_get`, `TEEC_RegisterSharedMemory`, and `sg_nents`.

## KCFI

No previously matching KCFI id regressed. All 15 Phase-3B in-scope functions plus `sg_nents` are KCFI-exact against stock, and every one has an **exact stock call multiset**.

One pre-existing mismatch remains and is explicitly **not** attributed to Phase 3B: `tee_shm_alloc_from_rpc` had a KCFI mismatch before this phase and still does. It is not one of the 12 targets nor a public TEEC SHM API, and Phase-3B policy forbids touching unrelated KCFI mismatches merely to improve the global number. It is recorded here so it is not mistaken for new damage.

## Imports

Three net new imports, **all four new names present in stock**:

| Import | In stock | Introduced by |
|---|---|---|
| `pfn_is_map_memory` | yes | `tee_map_cached_shm` |
| `ioremap_prot` | yes | `tee_map_cached_shm` |
| `arm64_use_ng_mappings` | yes | `pgprot_val(PAGE_KERNEL)` expansion |
| `iounmap` | yes | `tee_unmap_cached_shm` |

Removed: `sg_nents` (now defined locally, as in stock).

Island-only imports: **`_dev_err` only** (was `_dev_err` + `sg_nents`). `_dev_err` is pre-existing, used by 5 source files across the whole module, and eliminating it is not Phase-3B work. Within the shared-memory subsystem itself, every diagnostic was converted to `pr_*` so that each SHM function's call multiset matches stock exactly.

No import is unexplained and none is absent from stock except the documented pre-existing one.

## Section convergence toward stock

| Section | Stock | Phase-3A-R | Phase-3B |
|---|---:|---:|---:|
| `.text` | `0x9884` | `0x761c` | `0x766c` |
| `.data` | `0x20c` | `0x298` | **`0x208`** |
| `.bss` | `0xa1` | `0x88` | `0x88` |
| `.rodata` | `0x6a3` | `0x5f8` | **`0x688`** |

`.data` shrank by `0x90` and `.rodata` grew by the same `0x90`: the dma_buf_ops table moved out of `.data` into `.rodata` because it is now `const`, exactly where stock keeps `tee_static_shm_dma_buf_ops`. Both sections are now within a few bytes of stock.

## Unrelated-regression audit

- No previously closed Phase-3A-R function changed class: core lifecycle, IDR helpers and the four TEEC context/session APIs are untouched by Phase 3B.
- The only edits outside `tee_shm.c` / `tee_kernel_api.c` were: two diagnostic conversions in `tee_context.c` (`tee_context_alloc_shm_tmp`, a shared-memory helper), call-site renames in `tee_session.c`, and the new layout anchors.
- Layout anchors 51 → 83, all passing; no previously passing anchor was removed or weakened.
- Build remains clean: `BUILD_RC=0`, 0 warnings, 0 errors, 0 modpost warnings, 0 unresolved, 0 static-assert failures, `depends` empty.

**No unexplained regression.**
