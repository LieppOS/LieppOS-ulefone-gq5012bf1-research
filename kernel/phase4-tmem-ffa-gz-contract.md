# `tmem_ffa.ko` → `gz_tz_system` contract (GenieZone KREE peer)

`modinfo depends=gz_tz_system,tkcore,ffa_v10` is explained here: nine KREE
symbols are imported, all from `mtee_impl/`.

## 1. Imported symbols (9/9, exact stock CRCs)

| symbol | stock CRC | call sites | prototype (vendor header `kree/mem.h`, `kree/system.h`) |
|---|---|---|---|
| `KREE_CreateSession` | `0x552d4efc` | `mtee_session_open`, `tmem_query_gz_handle_to_pa` | `TZ_RESULT KREE_CreateSession(const char *ta_uuid, KREE_SESSION_HANDLE *pHandle)` |
| `KREE_CloseSession` | `0x5878d629` | `mtee_session_close`, `tmem_query_gz_handle_to_pa` | `TZ_RESULT KREE_CloseSession(KREE_SESSION_HANDLE handle)` |
| `KREE_TeeServiceCall` | `0xec19e146` | `mtee_invoke_command`, `tmem_query_gz_handle_to_pa` | `TZ_RESULT KREE_TeeServiceCall(KREE_SESSION_HANDLE handle, uint32_t command, uint32_t paramTypes, union MTEEC_PARAM param[4])` |
| `KREE_ION_AllocChunkmem` | `0x3d5d5254` | `mtee_alloc` | `TZ_RESULT KREE_ION_AllocChunkmem(KREE_SESSION_HANDLE session, KREE_ION_SECUREMEM_HANDLE *, uint32_t alignment, uint32_t size)` |
| `KREE_ION_ZallocChunkmem` | `0x0175c8da` | `mtee_alloc` | zeroing variant |
| `KREE_ION_UnreferenceChunkmem` | `0x8dceb484` | `mtee_free` | `TZ_RESULT KREE_ION_UnreferenceChunkmem(KREE_SESSION_HANDLE, KREE_ION_SECUREMEM_HANDLE)` |
| `KREE_AppendSecureMultichunkmem` | `0x9a19c31a` | `mtee_mem_reg_add` | `TZ_RESULT KREE_AppendSecureMultichunkmem(KREE_SESSION_HANDLE, KREE_SECUREMEM_HANDLE *, KREE_SHAREDMEM_PARAM *)` |
| `KREE_ReleaseSecureMultichunkmem` | `0x44781e48` | `mtee_mem_reg_remove` | `TZ_RESULT KREE_ReleaseSecureMultichunkmem(KREE_SESSION_HANDLE, KREE_SECUREMEM_HANDLE)` |
| `KREE_ConfigSecureMultiChunkMemInfo` | `0xbdb6a34b` | `mtee_invoke_command` | `TZ_RESULT KREE_ConfigSecureMultiChunkMemInfo(KREE_SESSION_HANDLE, uint64_t pa, uint32_t size, uint32_t region_id)` |

All nine CRCs in the rebuilt module come from the stock `gz_tz_system.ko`
`__kcrctab` record (`stock-provider.symvers`), never from an invented
declaration.

## 2. Why the dependency exists

`gz_tz_system` is the only provider of the GenieZone REE API on this device.
Six of the ten configured trusted-memory devices (`MTEE_SVP`, `MTEE_PROT`,
`MTEE_WFD`, `MTEE_TUI`, `MTEE_AP_MD_SHM`, `MTEE_AP_SCP_SHM`, plus the two SAPU
SHM devices) use the KREE peer ops, so the dependency is **essential**, not
optional: without it those devices cannot open a session and
`trusted_mem_api_alloc()` fails for every MTEE class.

## 3. Session model

```c
struct MTEE_SESSION_DATA {
        KREE_SESSION_HANDLE   session_handle;    /* int32 */
        KREE_SECUREMEM_HANDLE append_mem_handle;
};
```

- Service name: `"com.mediatek.geniezone.srv.mem"` (`mem_srv_name`), unless a
  per-device `ops_data->service_name` overrides it.
- `mtee_session_open()` allocates the session data, takes `MTEE_SESSION_LOCK`,
  calls `KREE_CreateSession`, and stores the handle. `mtee_session_close()`
  calls `KREE_CloseSession` and frees it.
- `tmem_query_gz_handle_to_pa()` opens a **transient** session
  (`KREE_CreateSession` → `KREE_TeeServiceCall` → `KREE_CloseSession`) purely
  to resolve a secure handle to a physical address.

## 4. Memory grant/reclaim semantics

- `mtee_mem_reg_add()` fills a `KREE_SHAREDMEM_PARAM { buffer = pa, size,
  mapAry = NULL, region_id = mtee_chunks_id }` and calls
  `KREE_AppendSecureMultichunkmem`, storing the returned
  `append_mem_handle`. Logged as `"MTEE append reg mem PASS: PA=0x%llx, size=0x%x"`.
- `mtee_mem_reg_remove()` calls `KREE_ReleaseSecureMultichunkmem` with that
  handle; failure is logged (`"MTEE release reg mem failed:%d"`) and surfaced.
- `mtee_invoke_command()` routes region-configuration commands through
  `KREE_ConfigSecureMultiChunkMemInfo` and generic ones through
  `KREE_TeeServiceCall` with `tz_cross/ta_mem.h` command ids
  (`TZCMD_MEM_APPEND_MULTI_CHUNKMEM` 23, `TZCMD_MEM_RELEASE_CHUNKMEM` 24, …).
- `mtee_alloc()` selects `KREE_ION_ZallocChunkmem` when the caller asked for
  zeroed memory, otherwise `KREE_ION_AllocChunkmem`; `mtee_free()` uses
  `KREE_ION_UnreferenceChunkmem` (refcount semantics, not free).

## 5. Provider status and boundary

| item | value |
|---|---|
| provider module | stock `gz_tz_system.ko` (vendor_dlkm, load index 149) |
| source availability | vendor `drivers/misc/mediatek/geniezone/` exists at the pinned revision; **not built or reconstructed in this task** |
| ABI record used | stock `__kcrctab` extraction, 9 symbols, `GZ_PROVIDER_STOCK_RUNTIME` |
| blocker? | **no** — it does not block `tmem_ffa` closure; the consumer is byte-exact against the stock provider record |
| headers used at build time | byte-identical vendor `kree/*.h`, `tz_cross/*.h`, `gz-trusty/*.h` from the same pinned revision |

**Boundary declared and frozen:** `gz_tz_system` stays a stock runtime provider
for now. Reconstructing it is explicitly out of scope for this task.
