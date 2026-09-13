# `gz_tz_system.ko` — export / consumer ABI audit

All **471** stock `.ko` files in every partition (vendor_boot, vendor_dlkm,
system_dlkm, recovery ramdisk) were scanned symbol-by-symbol via their
`__versions` tables. Machine table: `kernel/phase4-gz-tz-system-consumer-edges.tsv`.

## Summary

| | |
|---|---:|
| exports | 27 |
| export CRCs regenerated **naturally** | **27/27** |
| direct consumers found | **5** |
| consumer edges | **35** |
| consumer edges **NATURAL** | **35/35** |
| consumers that would break | **0** |
| exports with at least one consumer | 16/27 |

Every consumer's required CRC equals the stock provider CRC **and** the
source-built provider CRC. No stock module becomes ABI-broken.

## Per-consumer detail

### `tmem_ffa.ko` — 9 symbols, all NATURAL

MediaTek Trusted Memory Driver (V:152) - already source-closed and FROZEN. The acceptance rebuild in `kernel/phase4-gz-tz-system-tmem-ffa-acceptance.md` upgrades these 9 edges from stock-runtime witnesses to real source-built provider edges.

| symbol | consumer requires | stock provider | source-built provider | status |
|---|---|---|---|---|
| `KREE_AppendSecureMultichunkmem` | `0x9a19c31a` | `0x9a19c31a` | `0x9a19c31a` | **NATURAL** |
| `KREE_CloseSession` | `0x5878d629` | `0x5878d629` | `0x5878d629` | **NATURAL** |
| `KREE_ConfigSecureMultiChunkMemInfo` | `0xbdb6a34b` | `0xbdb6a34b` | `0xbdb6a34b` | **NATURAL** |
| `KREE_CreateSession` | `0x552d4efc` | `0x552d4efc` | `0x552d4efc` | **NATURAL** |
| `KREE_ION_AllocChunkmem` | `0x3d5d5254` | `0x3d5d5254` | `0x3d5d5254` | **NATURAL** |
| `KREE_ION_UnreferenceChunkmem` | `0x8dceb484` | `0x8dceb484` | `0x8dceb484` | **NATURAL** |
| `KREE_ION_ZallocChunkmem` | `0x0175c8da` | `0x0175c8da` | `0x0175c8da` | **NATURAL** |
| `KREE_ReleaseSecureMultichunkmem` | `0x44781e48` | `0x44781e48` | `0x44781e48` | **NATURAL** |
| `KREE_TeeServiceCall` | `0xec19e146` | `0xec19e146` | `0xec19e146` | **NATURAL** |

### `gz_main_mod.ko` — 15 symbols, all NATURAL

GenieZone main driver (V:150) - the largest consumer and the module that owns the GenieZone **userspace** ABI. Not reconstructed; out of scope for this task.

| symbol | consumer requires | stock provider | source-built provider | status |
|---|---|---|---|---|
| `KREE_AppendSecureMultichunkmem` | `0x9a19c31a` | `0x9a19c31a` | `0x9a19c31a` | **NATURAL** |
| `KREE_CloseSession` | `0x5878d629` | `0x5878d629` | `0x5878d629` | **NATURAL** |
| `KREE_CreateSession` | `0x552d4efc` | `0x552d4efc` | `0x552d4efc` | **NATURAL** |
| `KREE_ION_AllocChunkmem` | `0x3d5d5254` | `0x3d5d5254` | `0x3d5d5254` | **NATURAL** |
| `KREE_ION_QueryChunkmem_TEST` | `0x14085470` | `0x14085470` | `0x14085470` | **NATURAL** |
| `KREE_ION_ReferenceChunkmem` | `0x5df7236c` | `0x5df7236c` | `0x5df7236c` | **NATURAL** |
| `KREE_ION_UnreferenceChunkmem` | `0x8dceb484` | `0x8dceb484` | `0x8dceb484` | **NATURAL** |
| `KREE_ION_ZallocChunkmem` | `0x0175c8da` | `0x0175c8da` | `0x0175c8da` | **NATURAL** |
| `KREE_RegisterSharedmem` | `0xfbdd82be` | `0xfbdd82be` | `0xfbdd82be` | **NATURAL** |
| `KREE_ReleaseSecureMultichunkmem` | `0x44781e48` | `0x44781e48` | `0x44781e48` | **NATURAL** |
| `KREE_TeeServiceCall` | `0xec19e146` | `0xec19e146` | `0xec19e146` | **NATURAL** |
| `KREE_TeeServiceCallPlus` | `0xf45addc2` | `0xf45addc2` | `0xf45addc2` | **NATURAL** |
| `KREE_UnregisterSharedmem` | `0xd9a6d5ea` | `0xd9a6d5ea` | `0xd9a6d5ea` | **NATURAL** |
| `_map_user_pages` | `0x6e8b0474` | `0x6e8b0474` | `0x6e8b0474` | **NATURAL** |
| `tz_system_dev` | `0xebab6727` | `0xebab6727` | `0xebab6727` | **NATURAL** |

### `cmdq-sec-drv.ko` — 5 symbols, all NATURAL

MediaTek secure CMDQ driver - secure command-queue submission.

| symbol | consumer requires | stock provider | source-built provider | status |
|---|---|---|---|---|
| `KREE_CloseSession` | `0x5878d629` | `0x5878d629` | `0x5878d629` | **NATURAL** |
| `KREE_CreateSession` | `0x552d4efc` | `0x552d4efc` | `0x552d4efc` | **NATURAL** |
| `KREE_RegisterSharedmem` | `0xfbdd82be` | `0xfbdd82be` | `0xfbdd82be` | **NATURAL** |
| `KREE_TeeServiceCallPlus` | `0xf45addc2` | `0xf45addc2` | `0xf45addc2` | **NATURAL** |
| `KREE_UnregisterSharedmem` | `0xd9a6d5ea` | `0xd9a6d5ea` | `0xd9a6d5ea` | **NATURAL** |

### `sapu.ko` — 3 symbols, all NATURAL

MediaTek SAPU (secure APU) driver - secure AI/NPU memory.

| symbol | consumer requires | stock provider | source-built provider | status |
|---|---|---|---|---|
| `KREE_CloseSession` | `0x5878d629` | `0x5878d629` | `0x5878d629` | **NATURAL** |
| `KREE_CreateSession` | `0x552d4efc` | `0x552d4efc` | `0x552d4efc` | **NATURAL** |
| `KREE_TeeServiceCall` | `0xec19e146` | `0xec19e146` | `0xec19e146` | **NATURAL** |

### `mtk-cam-isp7sp.ko` — 3 symbols, all NATURAL

MediaTek ISP7sp camera driver - secure camera buffers.

| symbol | consumer requires | stock provider | source-built provider | status |
|---|---|---|---|---|
| `KREE_CloseSession` | `0x5878d629` | `0x5878d629` | `0x5878d629` | **NATURAL** |
| `KREE_CreateSession` | `0x552d4efc` | `0x552d4efc` | `0x552d4efc` | **NATURAL** |
| `KREE_TeeServiceCall` | `0xec19e146` | `0xec19e146` | `0xec19e146` | **NATURAL** |

## Exports with no stock consumer (11)

These reproduce naturally too, but nothing on this device imports them. They
are a legacy/test surface kept exported by the vendor:

`KREE_AllocSecuremem`, `KREE_AllocSecurememWithTag`, `KREE_ZallocSecuremem`,
`KREE_ZallocSecurememWithTag`, `KREE_ReferenceSecuremem`,
`KREE_UnreferenceSecuremem`, `KREE_ReferenceSecureMultichunkmem`,
`KREE_QueryChunkmem_TEST`, `KREE_GetSystemCnt`, `KREE_GetSystemCntFrq`,
`KREE_SessionToTID`.

## Indirect / transitive dependents

`modules.dep` lists 17 modules whose dependency closure includes
`gz_tz_system` (via `tmem_ffa`, `mtk_sec_heap` or `cmdq-sec-drv`):
`mtk_sec_heap`, `mtk_heap_debug`, `widevine_driver`, `mtk_disp_sec`,
`mtk_aie`, `mtk_aie_debug_7sp_2`, `mtk_imgsys_cmdq`, `mtk_imgsys_v4l2`,
`mtk_imgsys_isp7sp`, `mali_kbase_mt6878_r44`, `cmdq-test` and the five direct
consumers above. None of them imports a `gz_tz_system` symbol directly, so
none adds an ABI constraint beyond the 35 edges already verified.
