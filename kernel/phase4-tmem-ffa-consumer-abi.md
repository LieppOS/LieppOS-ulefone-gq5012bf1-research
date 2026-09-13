# `tmem_ffa.ko` — export / downstream-consumer audit

`tmem_ffa` is **not** a leaf: it exports 15 symbols and three stock modules
consume them.

## 1. Export surface (15/15 natural in the rebuild)

| # | symbol | class | stock CRC | rebuilt CRC | status |
|---:|---|---|---|---|---|
| 1 | `ssmr_offline` | `EXPORT_SYMBOL` | `0x6ce41c25` | `0x6ce41c25` | NATURAL EXACT |
| 2 | `ssmr_online` | `EXPORT_SYMBOL` | `0xb8313cbf` | `0xb8313cbf` | NATURAL EXACT |
| 3 | `trusted_mem_api_alloc` | `EXPORT_SYMBOL` | `0x65e5c101` | `0x65e5c101` | NATURAL EXACT |
| 4 | `trusted_mem_api_alloc_zero` | `EXPORT_SYMBOL` | `0x7c09b0e3` | `0x7c09b0e3` | NATURAL EXACT |
| 5 | `trusted_mem_api_get_page_replace` | `EXPORT_SYMBOL` | `0x48ea315b` | `0x48ea315b` | NATURAL EXACT |
| 6 | `trusted_mem_api_get_region_info` | `EXPORT_SYMBOL` | `0x4e506fde` | `0x4e506fde` | NATURAL EXACT |
| 7 | `trusted_mem_api_query_pa` | `EXPORT_SYMBOL` | `0x9d856127` | `0x9d856127` | NATURAL EXACT |
| 8 | `trusted_mem_api_unref` | `EXPORT_SYMBOL` | `0x7be62965` | `0x7be62965` | NATURAL EXACT |
| 9 | `trusted_mem_disable_high_freq` | `EXPORT_SYMBOL` | `0x331d7047` | `0x331d7047` | NATURAL EXACT |
| 10 | `trusted_mem_enable_high_freq` | `EXPORT_SYMBOL` | `0xd389fafb` | `0xd389fafb` | NATURAL EXACT |
| 11 | `trusted_mem_ffa_query_pa` | `EXPORT_SYMBOL` | `0x2f0213b6` | `0x2f0213b6` | NATURAL EXACT |
| 12 | `trusted_mem_is_ffa_enabled` | `EXPORT_SYMBOL` | `0x41b7fbbb` | `0x41b7fbbb` | NATURAL EXACT |
| 13 | `trusted_mem_is_page_v2_enabled` | `EXPORT_SYMBOL` | `0x03d3b7a5` | `0x03d3b7a5` | NATURAL EXACT |
| 14 | `trusted_mem_page_based_alloc` | `EXPORT_SYMBOL` | `0x7830573a` | `0x7830573a` | NATURAL EXACT |
| 15 | `trusted_mem_page_based_free` | `EXPORT_SYMBOL` | `0x20d3a271` | `0x20d3a271` | NATURAL EXACT |

All CRCs are produced by genksyms from the vendor headers
(`public/trusted_mem_api.h`, `ssmr/memory_ssmr.h`) — no injection, no patching.

## 2. Consumer scan (all stock modules in both partitions)

411 stock `.ko` files were scanned (`vendor_dlkm/lib/modules` +
`vendor-ramdisks/platform-extracted/lib/modules`) for undefined references to
the 15 exports.

| consumer | symbols required | consumer-required CRCs |
|---|---|---|
| `mtk_sec_heap.ko` | `trusted_mem_api_alloc`, `trusted_mem_api_unref`, `trusted_mem_api_query_pa`, `trusted_mem_api_get_region_info`, `trusted_mem_ffa_query_pa`, `trusted_mem_is_ffa_enabled`, `trusted_mem_is_page_v2_enabled`, `trusted_mem_page_based_alloc`, `trusted_mem_page_based_free`, `trusted_mem_enable_high_freq`, `trusted_mem_disable_high_freq` (11) | identical to the stock CRCs above |
| `gz_main_mod.ko` | `ssmr_online`, `ssmr_offline` (2) | identical |
| `mali_kbase_mt6878_r44.ko` | `trusted_mem_ffa_query_pa` (1) | identical |

Indirect dependants via `mtk_sec_heap` (per `modules.dep`): `mtk-cam-isp7sp`,
`sapu`, `mtk_heap_debug`, `widevine_driver`, `mtk_disp_sec`,
`mali_kbase_mt6878_r44`, `gz_main_mod`.

## 3. Consequence

Because the source-built module regenerates all 15 export CRCs **naturally and
exactly**, every existing stock consumer keeps loading unchanged: no consumer
needs a witness, a re-link, or a CRC override. `tmem_ffa` can be swapped to the
source-built binary without touching `mtk_sec_heap`, `gz_main_mod` or
`mali_kbase`.
