# Phase 3F — stock-binary compatibility side check (informational)

This is **separate from** the source-island acceptance and does not affect it. It answers one deployment question: can the final Phase-3E `tkcore.ko` satisfy the **original stock consumer binaries**, unmodified?

Method: compare each stock consumer's own `__versions` CRC against the Phase-3E provider's exported CRC. A Linux module fails to load if *any* imported symbol's CRC disagrees with the provider.

The Phase-3E provider was **not** altered to improve this outcome.

## Result: 5 directly compatible, 14 source-island-only

| Consumer | tkcore edges | Compatible | Disagreeing | Stock binary loads against Phase-3E tkcore? |
|---|---:|---:|---:|---|
| `tkcore_drv` | 11 | 4 | 7 | **NO** |
| `tmem_ffa` | 7 | 0 | 7 | **NO** |
| `microarray_fp_tee` | 1 | 1 | 0 | **YES** |
| **Total** | **19** | **5** | **14** | — |

## Per-edge classification

### STOCK_BINARY_DIRECTLY_COMPATIBLE (5)

| Consumer | Symbol | CRC (stock == Phase-3E) |
|---|---|---|
| `tkcore_drv` | `tee_map_cached_shm` | `0x6a4e508b` |
| `tkcore_drv` | `tee_clkmgr_handle` | `0x6913f6b2` |
| `tkcore_drv` | `tee_wait_queue_init` | `0x03c4c343` |
| `tkcore_drv` | `tee_wait_queue_exit` | `0xe773ba45` |
| `microarray_fp_tee` | `tee_spi_transfer` | `0x184ce7da` |

### SOURCE_ISLAND_ONLY (14)

`tkcore_drv`: `tee_core_alloc`, `tee_core_add`, `tee_core_del`, `__tee_get`, `tee_supp_cmd`, `tee_wait_queue_sleep`, `tee_wait_queue_wakeup`.

`tmem_ffa`: `TEEC_InitializeContext`, `TEEC_RegisterSharedMemory`, `TEEC_OpenSession`, `TEEC_InvokeCommand`, `TEEC_CloseSession`, `TEEC_ReleaseSharedMemory`, `TEEC_FinalizeContext`.

Each of these is a category-B edge whose historical CRC hashes unrecoverable private member spellings; see `kernel/phase4-tkcore-island-phase3f-private-abi-provenance.md`.

## Answer to the deployment question

**tkcore cannot be swapped alone.** The stock `tkcore_drv.ko` and stock `tmem_ffa.ko` binaries would be rejected by the module loader with version-magic disagreement on those symbols.

The one genuinely good news is `microarray_fp_tee`: its sole tkcore edge is historically natural, so the **stock fingerprint TEE binary does not need rebuilding** on tkcore's account.

This is a static conclusion derived from CRC tables. No module was loaded, and no device operation was performed.
