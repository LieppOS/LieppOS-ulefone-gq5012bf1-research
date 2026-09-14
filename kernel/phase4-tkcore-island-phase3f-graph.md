# Phase 3F — final accepted source ABI graph

Every edge below was measured from the Phase-3F artifacts. Legend:

- **[A]** `NATURAL_HISTORICAL_STOCK_CRC` — the final source provider emits the exact CRC the stock/frozen consumer imports
- **[B]** `ISLAND_NATURAL_PROVIDER_ABI` — provider and consumer agree naturally from the common headers; historical value unrecoverable
- **[N]** natural non-tkcore provider edge

```
                        exact GKI  ab/12901745  (6.1.115-android14-11)
                        common 6b18f0b574ab3267615ae6ce642d5a7c3c21ac09
                                          │
        ┌─────────────────────────────────┼──────────────────────────────┐
        │                                 │                              │
        │                            tkcore.ko                           │
        │                    (122/122, 25/25 exports)                    │
        │                                 │                              │
        │        ┌────────────────────────┼─────────────────────────┐    │
        │        │ 11 edges               │ 7 edges                 │ 1  │
        │        │ 4×[A] 7×[B]            │ 7×[B]                   │[A] │
        │        ▼                        ▼                         ▼    │
        │   tkcore_drv.ko            tmem_ffa.ko          microarray_fp_tee.ko
        │        ▲                    ▲       ▲              ▲        ▲
        │        │ 2×[N]              │1×[N]  │9×[N]         │4×[N]   │2×[N]
        │        │                    │       │              │        │
        │   ffa_v10.ko          ffa_v10.ko  gz_tz_system  fingerprint spi-mt65xx
        │   (source-closed)     (source)     (source)      (source)   (source)
        │
        └── 60 GKI edges (tmem_ffa) · 59 GKI edges (microarray) · GKI edges (tkcore_drv, tkcore)
```

## tkcore → tkcore_drv (11 edges)

| Symbol | Class |
|---|---|
| `tee_map_cached_shm` | **[A]** `0x6a4e508b` |
| `tee_clkmgr_handle` | **[A]** `0x6913f6b2` |
| `tee_wait_queue_init` | **[A]** `0x03c4c343` |
| `tee_wait_queue_exit` | **[A]** `0xe773ba45` |
| `tee_core_alloc` | **[B]** `0x00940cd5` |
| `tee_core_add` | **[B]** `0xe8b45b91` |
| `tee_core_del` | **[B]** `0xd3dca6f9` |
| `__tee_get` | **[B]** `0xf95a76a4` |
| `tee_supp_cmd` | **[B]** `0x82545465` |
| `tee_wait_queue_sleep` | **[B]** `0x305931a9` |
| `tee_wait_queue_wakeup` | **[B]** `0x258a3f0c` |

## tkcore → tmem_ffa (7 edges, all [B])

`TEEC_InitializeContext` `0xf395354f`, `TEEC_RegisterSharedMemory` `0x6f70dc3e`, `TEEC_OpenSession` `0x90aa6e1d`, `TEEC_InvokeCommand` `0xdd7b8804`, `TEEC_CloseSession` `0x811d3eaf`, `TEEC_ReleaseSharedMemory` `0xee29e3f5`, `TEEC_FinalizeContext` `0xd203900b`.

## tkcore → microarray_fp_tee (1 edge)

`tee_spi_transfer` — **[A]** `0x184ce7da`, stock KCFI `0xffeb18b3`.

## Non-tkcore intermodule edges — all [N] natural

| Edge | Symbols | Values |
|---|---:|---|
| `ffa_v10` → `tkcore_drv` | 2 | `ffa_driver_register` `0x0d53cde9`, `ffa_driver_unregister` `0x3c660e4c` |
| `ffa_v10` → `tmem_ffa` | 1 | `ffa_driver_register` `0x0d53cde9` |
| `gz_tz_system` → `tmem_ffa` | 9 | all nine `KREE_*` |
| `fingerprint` → `microarray_fp_tee` | 4 | all four `yft_*` |
| `spi-mt65xx` → `microarray_fp_tee` | 2 | `mt_spi_enable_master_clk` `0x1cc49782`, `mt_spi_disable_master_clk` `0xccc1e350` |

## Totals

- tkcore consumer edges: **19** — 5 **[A]**, 14 **[B]**, 0 blocked
- non-tkcore intermodule edges: **18**, all natural
- stock-tkcore ABI witnesses anywhere in the final source island: **0**
