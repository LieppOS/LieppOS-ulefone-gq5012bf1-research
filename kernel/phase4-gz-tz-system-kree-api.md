# `gz_tz_system.ko` — exported KREE API contract

27 exports, all `EXPORT_SYMBOL` (none `_GPL`). **27/27 CRCs regenerate
naturally** from the source build; **27/27 kCFI type ids exact.**
Machine table: `kernel/phase4-gz-tz-system-kree-api.tsv`.

## 0. Handle and parameter types

```c
typedef int32_t  KREE_SESSION_HANDLE;        /* kree/mem.h */
typedef uint32_t KREE_SHAREDMEM_HANDLE;
typedef uint32_t KREE_SECUREMEM_HANDLE;
typedef uint32_t KREE_ION_SECUREMEM_HANDLE;  /* same width, distinct alias */
typedef uint32_t TZ_RESULT;

union MTEEC_PARAM {                          /* tz_cross/trustzone.h */
	struct MTEEC_MEM    mem;
	struct MTEEC64_MEM  mem64;
	struct MTEEC32_MEM  mem32;
	struct MTEEC_MEMREF memref;
	struct MTEEC_VALUE  value;               /* { uint32_t a, b; } */
};

enum TZ_PARAM_TYPES {
	TZPT_NONE = 0,
	TZPT_VALUE_INPUT = 1, TZPT_VALUE_OUTPUT = 2, TZPT_VALUE_INOUT = 3,
	TZPT_MEM_INPUT   = 4, TZPT_MEM_OUTPUT   = 5, TZPT_MEM_INOUT   = 6,
	TZPT_MEMREF_INPUT= 7, TZPT_MEMREF_OUTPUT= 8, TZPT_MEMREF_INOUT= 9,
};
/* paramTypes packs 4 nibbles: TZ_ParamTypes(t1,t2,t3,t4) */
```

None of these is config-dependent — which is why the export CRCs are stable.

## 1. Session APIs

| export | stock CRC | size | kCFI |
|---|---|---:|---|
| `KREE_CreateSession` | `0x552d4efc` | 716 | `0xa2b4a296` |
| `KREE_CloseSession` | `0x5878d629` | 628 | `0x00050794` |
| `KREE_SessionToTID` | `0x79393b5e` | 244 | `0xee5a313a` |

```c
TZ_RESULT KREE_CreateSession(const char *ta_uuid, KREE_SESSION_HANDLE *pHandle);
TZ_RESULT KREE_CloseSession(KREE_SESSION_HANDLE handle);
TZ_RESULT KREE_SessionToTID(KREE_SESSION_HANDLE session, uint32_t *o_TID);
```

`KREE_CreateSession` semantics recovered from source:
rejects `NULL` `pHandle` or `ta_uuid` with `TZ_RESULT_ERROR_BAD_PARAMETERS`;
takes `session_mutex`; `KREE_OpenFd(ta_uuid,&chan_fd)` connects the TIPC
channel; derives `tee_id` from the channel (`chan_p->tee_id`, Trusty or
Nebula); lazily opens the per-TEE *system* service FD once
(`_sys_service_Fd[tee_id] < 0 → KREE_OpenSysFd(tee_id)`); then issues the
create-session service call. Error paths all funnel through a single
`create_session_out` label that unlocks `session_mutex`.

## 2. Service-call APIs

| export | stock CRC | size | kCFI |
|---|---|---:|---|
| `KREE_TeeServiceCall` | `0xec19e146` | 32 | `0xc843babe` |
| `KREE_TeeServiceCallPlus` | `0xf45addc2` | 944 | `0x322755bd` |

```c
TZ_RESULT KREE_TeeServiceCall(KREE_SESSION_HANDLE handle, uint32_t command,
                              uint32_t paramTypes, union MTEEC_PARAM param[4]);
TZ_RESULT KREE_TeeServiceCallPlus(KREE_SESSION_HANDLE handle, uint32_t command,
                                  uint32_t paramTypes, union MTEEC_PARAM param[4],
                                  int32_t cpumask);
```

`KREE_TeeServiceCall` is a 32-byte thunk: `return KREE_TeeServiceCallPlus(h, cmd,
pt, param, -1);`. The `-1` cpumask is what selects the global
`servicecall_lock` serialisation path. Detail in
`kernel/phase4-gz-tz-system-service-call.md`.

## 3. Shared-memory APIs (`API_sharedMem`)

| export | stock CRC | size | kCFI |
|---|---|---:|---|
| `KREE_RegisterSharedmem` | `0xfbdd82be` | 104 | `0x3900744c` |
| `KREE_UnregisterSharedmem` | `0xd9a6d5ea` | 160 | `0xd58853ad` |

```c
TZ_RESULT KREE_RegisterSharedmem(KREE_SESSION_HANDLE session,
                                 KREE_SHAREDMEM_HANDLE *shm_handle,
                                 KREE_SHAREDMEM_PARAM *param);
TZ_RESULT KREE_UnregisterSharedmem(KREE_SESSION_HANDLE session,
                                   KREE_SHAREDMEM_HANDLE shm_handle);
```

## 4. Secure-memory APIs (`API_secureMem`)

| export | stock CRC | size | kCFI |
|---|---|---:|---|
| `KREE_AllocSecuremem` | `0x991643ee` | 216 | `0x38260786` |
| `KREE_ZallocSecuremem` | `0x83a1b948` | 216 | `0x38260786` |
| `KREE_AllocSecurememWithTag` | `0x1c007570` | 216 | `0x40d15212` |
| `KREE_ZallocSecurememWithTag` | `0x6c132e7e` | 216 | `0x40d15212` |
| `KREE_ReferenceSecuremem` | `0xded08df4` | 168 | `0xd58853ad` |
| `KREE_UnreferenceSecuremem` | `0x1e3d6e2c` | 168 | `0xd58853ad` |

The Alloc/Zalloc pairs share a kCFI id and size — same prototype, different
command constant. The `WithTag` pair shares a *different* kCFI id because it
carries the extra tag argument.

## 5. Multi-chunk secure-memory APIs

| export | stock CRC | size | kCFI |
|---|---|---:|---|
| `KREE_AppendSecureMultichunkmem` | `0x9a19c31a` | 32 | `0x3900744c` |
| `KREE_ReleaseSecureMultichunkmem` | `0x44781e48` | 32 | `0xd58853ad` |
| `KREE_ReferenceSecureMultichunkmem` | `0x435d935a` | 192 | `0xd58853ad` |
| `KREE_ConfigSecureMultiChunkMemInfo` | `0xbdb6a34b` | 128 | `0x89b5982d` |

`Append` (32 B) and `Release` (32 B) are thin wrappers over the static
`_kree_mcm_Append` / `_kree_mcm_Release` bodies, which hold `chmem_mutex`.
`Append` shares kCFI `0x3900744c` with `KREE_RegisterSharedmem` — identical
prototype shape `(handle, uint32_t*, KREE_SHAREDMEM_PARAM*)`.

## 6. Chunk-memory (ION) APIs (`API_chunkMem`)

| export | stock CRC | size | kCFI |
|---|---|---:|---|
| `KREE_ION_AllocChunkmem` | `0x3d5d5254` | 288 | `0x1845c8fb` |
| `KREE_ION_ZallocChunkmem` | `0x0175c8da` | 288 | `0x1845c8fb` |
| `KREE_ION_ReferenceChunkmem` | `0x5df7236c` | 192 | `0xd58853ad` |
| `KREE_ION_UnreferenceChunkmem` | `0x8dceb484` | 184 | `0xd58853ad` |
| `KREE_ION_QueryChunkmem_TEST` | `0x14085470` | 200 | `0x1c467870` |
| `KREE_QueryChunkmem_TEST` | `0x06f77776` | 232 | `0x1c467870` |

## 7. System-counter APIs

| export | stock CRC | size | kCFI |
|---|---|---:|---|
| `KREE_GetSystemCnt` | `0xf676ecc1` | 24 | `0x529c6ef0` |
| `KREE_GetSystemCntFrq` | `0xcb01e245` | 8 | `0x837de525` |

```c
u64 KREE_GetSystemCnt(void);     /* __arch_counter_get_cntvct() */
u32 KREE_GetSystemCntFrq(void);  /* arch_timer_get_cntfrq()     */
```

Pure register reads; no session, no locking, no secure-world entry. Zero stock
consumers.

## 8. Non-KREE exports

| export | stock CRC | kind |
|---|---|---|
| `_map_user_pages` | `0x6e8b0474` | function, 636 B, kCFI `0x1af08a48` — from `mtee-kree/tz_mmap.c` |
| `tz_system_dev` | `0xebab6727` | **data object** — `struct platform_device *`, set in `tz_system_probe` |

`tz_system_dev` is the only exported *object*; it is what lets
`tz_system_std_call32` reach `trusty_std_call32(tz_system_dev->dev.parent, …)`.

## 9. The 9 tmem_ffa-facing exports

Cross-checked against the frozen `tmem_ffa` oracle; every one natural after
closure:

| symbol | CRC | in tmem_ffa? |
|---|---|---|
| `KREE_CreateSession` | `0x552d4efc` | yes |
| `KREE_CloseSession` | `0x5878d629` | yes |
| `KREE_TeeServiceCall` | `0xec19e146` | yes |
| `KREE_ION_AllocChunkmem` | `0x3d5d5254` | yes |
| `KREE_ION_ZallocChunkmem` | `0x0175c8da` | yes |
| `KREE_ION_UnreferenceChunkmem` | `0x8dceb484` | yes |
| `KREE_AppendSecureMultichunkmem` | `0x9a19c31a` | yes |
| `KREE_ReleaseSecureMultichunkmem` | `0x44781e48` | yes |
| `KREE_ConfigSecureMultiChunkMemInfo` | `0xbdb6a34b` | yes |

## 10. Export surface actually consumed

16 of 27 exports have at least one stock consumer. The 11 with none are
`KREE_AllocSecuremem`, `KREE_AllocSecurememWithTag`, `KREE_ZallocSecuremem`,
`KREE_ZallocSecurememWithTag`, `KREE_ReferenceSecuremem`,
`KREE_UnreferenceSecuremem`, `KREE_ReferenceSecureMultichunkmem`,
`KREE_QueryChunkmem_TEST`, `KREE_GetSystemCnt`, `KREE_GetSystemCntFrq`,
`KREE_SessionToTID` — a legacy/test surface kept exported but unused on this
device. All 11 still reproduce naturally.
