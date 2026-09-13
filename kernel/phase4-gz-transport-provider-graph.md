# GQ5012BF1 GenieZone transport provider graph

## True order

```text
exact GKI
  └── gz_trusty_mod.ko  V:145  [lowest provider]
        ├── gz_ipc_mod.ko V:146  [3 edges]
        │     ├── gz_tz_system.ko V:149 [5 edges]
        │     └── gz_main_mod.ko        [1 edge]
        ├── gz_irq_mod.ko        [5 edges]
        ├── gz_log_mod.ko        [6 edges]
        ├── gz_main_mod.ko       [5 edges]
        ├── gz_tz_system.ko      [2 edges]
        ├── gz_virtio_mod.ko     [11 edges]
        └── sapu.ko              [2 edges]
```

`gz_trusty_mod` imports 59 symbols and all are exact-GKI symbols. It imports nothing from `gz_ipc_mod` or any other GenieZone module. `gz_ipc_mod` imports 81 symbols: 78 exact-GKI plus exactly three from `gz_trusty_mod`. Therefore the only valid build/load order is **Trusty first, IPC second**.

## Exact intermodule edges

| Provider | Consumer | Symbol | Stock CRC | Natural rebuilt CRC | Load order | Source | Status |
|---|---|---|---:|---:|---|---|---|
| `gz_trusty_mod` | `gz_ipc_mod` | `get_smcnr_dev` | `0x5fdc32d1` | `0x5fdc32d1` | 145 → 146 | `smcnr-table.c` | `NATURAL_OK` |
| `gz_trusty_mod` | `gz_ipc_mod` | `trusty_fast_call32` | `0x0c06e871` | `0x0c06e871` | 145 → 146 | `trusty.c` | `NATURAL_OK` |
| `gz_trusty_mod` | `gz_ipc_mod` | `trusty_get_api_version` | `0xbfe5cfb0` | `0xbfe5cfb0` | 145 → 146 | `trusty.c` | `NATURAL_OK` |

`modules.dep` independently confirms:

```text
/vendor_dlkm/lib/modules/gz_trusty_mod.ko:
/vendor_dlkm/lib/modules/gz_ipc_mod.ko: /vendor_dlkm/lib/modules/gz_trusty_mod.ko
```

## `gz_tz_system` downstream edges

| Provider | Symbol | Natural CRC |
|---|---|---:|
| `gz_ipc_mod` | `tipc_k_connect` | `0x6d3e778c` |
| `gz_ipc_mod` | `tipc_k_disconnect` | `0x389e0025` |
| `gz_ipc_mod` | `tipc_k_read` | `0xe9bc90dd` |
| `gz_ipc_mod` | `tipc_k_write` | `0xd5b2fc22` |
| `gz_ipc_mod` | `port_lookup_tid` | `0x141326e4` |
| `gz_trusty_mod` | `trusty_std_call32` | `0x1816bb67` |
| `gz_trusty_mod` | `trusty_enqueue_nop` | `0x0d91978b` |

All seven are source-built and natural in `phase4-gz-transport-gz-tz-system-acceptance.tsv`.

## Full stock scan

All 471 committed stock module placements were scanned by `__versions` symbol/CRC, not by filename guesses:

- Trusty: 7 direct consumers, 34 edges, all 14 exports consumed.
- IPC: 2 direct consumers, 6 edges, 6 of 15 exports consumed.
- Total: **40 edges, 0 CRC mismatches**.

Machine tables: `phase4-gz-trusty-mod-consumer-edges.tsv`, `phase4-gz-ipc-mod-consumer-edges.tsv`, and `phase4-gz-transport-consumer-acceptance.tsv`.
