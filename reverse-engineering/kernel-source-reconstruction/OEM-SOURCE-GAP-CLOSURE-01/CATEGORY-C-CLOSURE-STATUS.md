# Category C closure status (canonical 4e47a5b9: 11 C)

| Module | Exact already | Remaining difference | Missing input (type) | Exhausted | New falsifiable experiment |
|---|---|---|---|---|---|
| **tmem_ffa** | 141/141 functions, data, KCFI, relocations | none after this session | — | — | **done: C→A proposed** (fresh B1/B2, CAS delta) |
| **tkcore** | 25/25 export CRCs (new); 103/122 functions (new) | 19 functions: plat/procfs/shm allocator; 7:2.2 user-pinning imports | 6:1.1 implementation (MISSING_SOURCE_IMPLEMENTATION) | 3.2p3, 3.2p8, 4.0p0, 7:2.2 | none without 6:1.x source |
| charger_class | 90/90 functions, data, ABI, relocations | srcversion | exact source tokens (MISSING_SOURCE_TOKEN_PROVENANCE) | ALPS, NothingOSS | srcversion test of any new file |
| mtk_chg_type_det | 8/8 functions, all else | srcversion | same | same | same |
| rt_pd_manager | 11/11 functions, all else | srcversion | same | same | same |
| tcpc_class | 709/709 functions, 113/114 data | srcversion, 6 `__LINE__` strings, 37 BUG lines | same | same | line-number fit |
| tcpc_mt6375 | 66/66 functions | +1 counter prefix, srcversion | same | same | counter-use check |
| aw883xx_driver | 235/236 functions, ABI | 1 function: v1.7.1 scene-parser loop shape | exact Awinic v1.7.1 text | Awinic public releases | test new v1.7.1 text |
| focaltech_touch_spi_ft3680 | 67/166 functions | 99 functions | ODM FocalTech revision | historical | test obtained revision |
| st21nfc | 22/24 functions (historical) | 2 functions + recipe preservation | exact ST 2.2.0.19 tree (SOURCE_EXISTS_PARITY_UNPROVEN) | historical | rebuild from ST 2.2.0.19 if located |
| yft_devinfo | 54/72 functions | 10 export CRCs, 11 KCFI, 18 functions | YFT private headers (MISSING_PRIVATE_HEADER) | historical | genksyms harness on obtained headers |

## Shared blockers

| Family | Rows | One input would close |
|---|---|---|
| Richtek/MediaTek srcversion | charger_class, mtk_chg_type_det, rt_pd_manager, tcpc_class, tcpc_mt6375 | the exact shipped source files; code is already identical |
| TrustKernel | tkcore (C), tmem_ffa (now A) | the declaration side is solved; tkcore needs the 6:1.1 implementation |

## Not changed

- **No C row was promoted on code parity alone.** Only `tmem_ffa`, which now passes full strict whole-file
  acceptance in two independent builds, is proposed.
- **Codex's USB/Type-C, audio and connectivity recipes were not modified.**
