# `gz_tz_system.ko` — secure-memory API contract

Linux-side only. **No secure-memory API was invoked on the device.** All
behaviour below is read from the closed source, which rebuilds byte-identically
to stock.

## 0. Correction to the assumed prototypes

The task brief carried a 4-argument form for the two ION allocators. The
authoritative vendor header (`geniezone/public/kree/mem.h` at the pinned
revision) and the stock implementation both show **five** arguments, with a
`KREE_SHAREDMEM_HANDLE chm_handle` in second position:

```c
/* BRIEF (assumed, incorrect):
 *   KREE_ION_AllocChunkmem(session, mem_handle, alignment, size)   -- 4 args
 * ACTUAL: */
TZ_RESULT KREE_ION_AllocChunkmem(KREE_SESSION_HANDLE session,
                                 KREE_SHAREDMEM_HANDLE chm_handle,
                                 KREE_SECUREMEM_HANDLE *secmHandle,
                                 uint32_t alignment,
                                 uint32_t size);
```

This is confirmed three ways: the header, the C definition, and the kCFI type
id `0x1845c8fb` which both allocators share and which the source build
reproduces exactly. The same applies to `KREE_ION_ZallocChunkmem`.

Also note the handle type: the header uses `KREE_SECUREMEM_HANDLE *`, not
`KREE_ION_SECUREMEM_HANDLE *`. Both are `uint32_t` aliases, so the ABI is
identical, but the declared type is `KREE_SECUREMEM_HANDLE`.

## 1. Handle and parameter types

```c
typedef uint32_t KREE_SHAREDMEM_HANDLE;   /* a registered chunk-memory window */
typedef uint32_t KREE_SECUREMEM_HANDLE;   /* an allocation inside such a window */
#define KREE_SHAREDMEM_PARAM struct kree_shared_mem_param
struct KREE_SHM_RUNLENGTH_ENTRY {         /* run-length-coded PA array */
        uint32_t high;                    /* start PA = (high << 32) | low */
        uint32_t low;
        uint32_t size;
};
```

`struct kree_shared_mem_param` ends with a `void *mapAry` pointing at the
run-length array. `0` is the reserved invalid value for both handle types —
every release path checks `if (handle == 0) return TZ_RESULT_ERROR_BAD_PARAMETERS`.

## 2. `KREE_ION_AllocChunkmem` / `KREE_ION_ZallocChunkmem`

| | |
|---|---|
| CRC | `0x3d5d5254` / `0x0175c8da` |
| size | 288 / 288 bytes |
| kCFI | `0x1845c8fb` (shared — identical prototype) |

```c
*secmHandle = 0;                                  /* always cleared first */
ret = KREE_AllocSecureMultichunkmem(session, chm_handle, &mem_handle,
                                    alignment, size);   /* Zalloc -> KREE_Zalloc… */
if (ret != TZ_RESULT_SUCCESS || !mem_handle) {
        KREE_ERR("[%s]alloc Fail: mem_hd=0x%x, ret=0x%x)\n", __func__, mem_handle, ret);
        return TZ_RESULT_ERROR_GENERIC;           /* NOTE: original ret is discarded */
}
*secmHandle = mem_handle;
return TZ_RESULT_SUCCESS;
```

Recovered semantics:

* **Units** — `size` and `alignment` are in **bytes**, `uint32_t`, passed
  through unmodified to the multichunk layer; this module performs no rounding.
* **Output is cleared on entry**, so the caller's handle is always defined even
  on failure.
* **Zero handle is treated as failure** even when the call returned success.
* **Error remapping**: both allocators collapse every failure to
  `TZ_RESULT_ERROR_GENERIC`. The underlying `ret` is only logged, never
  returned. Callers cannot distinguish causes.
* **Zeroing**: the only difference between the two is `Alloc` vs `Zalloc` in
  the multichunk call, i.e. whether the secure world zeroes the region. Linux
  never touches the memory.

## 3. `KREE_ION_UnreferenceChunkmem`

| | |
|---|---|
| CRC | `0x8dceb484`, size 184, kCFI `0xd58853ad` |

```c
TZ_RESULT KREE_ION_UnreferenceChunkmem(KREE_SESSION_HANDLE session,
                                       KREE_SECUREMEM_HANDLE secmHandle);
```

Two arguments (the brief's form was correct here). Drops one reference on the
allocation. kCFI `0xd58853ad` is shared by every
`(KREE_SESSION_HANDLE, uint32_t)` API — `KREE_ION_ReferenceChunkmem`,
`KREE_ReferenceSecuremem`, `KREE_UnreferenceSecuremem`,
`KREE_ReleaseSecureMultichunkmem`, `KREE_UnregisterSharedmem`,
`KREE_ReferenceSecureMultichunkmem`.

Reference semantics are maintained **in the secure world**, not in Linux;
this module holds no refcount of its own.

## 4. `KREE_AppendSecureMultichunkmem`

| | |
|---|---|
| CRC | `0x9a19c31a`, size 32, kCFI `0x3900744c` |

```c
TZ_RESULT KREE_AppendSecureMultichunkmem(KREE_SESSION_HANDLE session,
                                         KREE_SHAREDMEM_HANDLE *cm_handle,
                                         KREE_SHAREDMEM_PARAM *param)
{ return _kree_mcm_Append(session, cm_handle, param,
                          TZCMD_MEM_APPEND_MULTI_CHUNKMEM_ION); }
```

A 32-byte thunk. The `_basic` sibling (`KREE_AppendSecureMultichunkmem_basic`,
present but **not exported**) is identical except it passes
`TZCMD_MEM_APPEND_MULTI_CHUNKMEM` — the non-ION command.

`_kree_mcm_Append` behaviour:
* takes `chmem_mutex` (interruptible, retried while `-EINTR`)
* marshals the run-length PA array from `param`
* on service-call failure: logs
  `"[%s]append chmem(cm_hd=0x%x) Fail(0x%x)"`, **unlocks**, returns
  `TZ_RESULT_ERROR_GENERIC`
* on success, the `CONFIG_GZ_VPU_WITH_M4U` block would map the region through
  M4U — **this device has that config off**, so no M4U call occurs
* unlocks and returns

**Ownership**: the caller owns the PA array and the buffer it describes; the
secure world owns the resulting `cm_handle`. Linux stores nothing.

## 5. `KREE_ReleaseSecureMultichunkmem`

| | |
|---|---|
| CRC | `0x44781e48`, size 32, kCFI `0xd58853ad` |

```c
TZ_RESULT KREE_ReleaseSecureMultichunkmem(KREE_SESSION_HANDLE session,
                                          KREE_SHAREDMEM_HANDLE cm_handle)
{ return _kree_mcm_Release(session, cm_handle, TZCMD_MEM_RELEASE_CHUNKMEM_ION); }
```

`_kree_mcm_Release`:
```c
if (cm_handle == 0) return TZ_RESULT_ERROR_BAD_PARAMETERS;
do { locktry = mutex_lock_interruptible(&chmem_mutex);
     if (locktry && locktry != -EINTR) return TZ_RESULT_ERROR_GENERIC;
} while (locktry);
p[0].value.a = (uint32_t)cm_handle;
ret = KREE_TeeServiceCall(session, cmd, TZ_ParamTypes1(TZPT_VALUE_INPUT), p);
if (ret != TZ_RESULT_SUCCESS) { KREE_ERR("[%s] release Fail(0x%x)"); mutex_unlock(); return ret; }
/* CONFIG_GZ_VPU_WITH_M4U: gz_do_m4u_umap(cm_handle) -- OFF on this device */
mutex_unlock(&chmem_mutex);
return TZ_RESULT_SUCCESS;
```

Note the asymmetry, recorded as observed: the failure path returns the real
`ret`, the success path returns a hardcoded `TZ_RESULT_SUCCESS`.

Cleanup ordering is therefore **service call first, unlock second** — the lock
is held across the secure-world round trip.

## 6. `KREE_ConfigSecureMultiChunkMemInfo`

| | |
|---|---|
| CRC | `0xbdb6a34b`, size 128, kCFI `0x89b5982d` |

```c
TZ_RESULT KREE_ConfigSecureMultiChunkMemInfo(KREE_SESSION_HANDLE session,
                                             uint64_t pa, uint32_t size,
                                             uint32_t region_id);
```

Parameter packing — this is the exact wire encoding:

```c
p[0].value.a = (pa >> 32);          /* PA high 32 */
p[0].value.b = (pa & 0xFFFFFFFF);   /* PA low 32  */
p[1].value.a = size;
p[1].value.b = region_id;
ret = KREE_TeeServiceCall(session, TZCMD_MEM_CONFIG_CHUNKMEM_INFO_ION,
                          TZ_ParamTypes3(TZPT_VALUE_INPUT, TZPT_VALUE_INPUT,
                                         TZPT_VALUE_OUTPUT), p);
if (ret != TZ_RESULT_SUCCESS) return ret;      /* transport failure */
ret = p[2].value.a;                            /* TA-level status   */
if (ret != TZ_RESULT_SUCCESS) return ret;
```

Recovered semantics:

* **`size == 0` means "turn the region off".** The `CONFIG_GZ_VPU_WITH_M4U`
  block makes this explicit (`is_region_on = (size == 0) ? false : true`),
  and it is the only place the convention is visible. That config is off here,
  so on this device the Linux side does nothing extra — but the convention is
  still what the secure world is being told.
* **Two-level status**: transport result *and* `p[2].value.a` are both checked.
  A caller that only checks the return value of the service call would miss
  TA-level failures; this function checks both and returns whichever failed.
* No lock is taken — this API is not serialised against the chunk-memory mutex.
* `region_id` is opaque `uint32_t`, passed through.

## 7. Legacy secure-memory APIs (exported, unused on this device)

| export | CRC | size | kCFI | shape |
|---|---|---:|---|---|
| `KREE_AllocSecuremem` | `0x991643ee` | 216 | `0x38260786` | `(session, *handle, alignment, size)` |
| `KREE_ZallocSecuremem` | `0x83a1b948` | 216 | `0x38260786` | same |
| `KREE_AllocSecurememWithTag` | `0x1c007570` | 216 | `0x40d15212` | + tag |
| `KREE_ZallocSecurememWithTag` | `0x6c132e7e` | 216 | `0x40d15212` | + tag |
| `KREE_ReferenceSecuremem` | `0xded08df4` | 168 | `0xd58853ad` | `(session, handle)` |
| `KREE_UnreferenceSecuremem` | `0x1e3d6e2c` | 168 | `0xd58853ad` | `(session, handle)` |
| `KREE_ReferenceSecureMultichunkmem` | `0x435d935a` | 192 | `0xd58853ad` | `(session, handle)` |
| `KREE_QueryChunkmem_TEST` | `0x06f77776` | 232 | `0x1c467870` | `(session, handle, cmd)` |
| `KREE_ION_QueryChunkmem_TEST` | `0x14085470` | 200 | `0x1c467870` | `(session, handle, cmd)` |

All nine reproduce naturally. No stock module imports any of them.

## 8. Internal, non-exported helpers

`KREE_AllocSecureMultichunkmem`, `KREE_ZallocSecureMultichunkmem`,
`KREE_UnreferenceSecureMultichunkmem`,
`KREE_AppendSecureMultichunkmem_basic`,
`KREE_ReleaseSecureMultichunkmem_basic`, `_kree_mcm_Alloc`, `_kree_mcm_Append`,
`_kree_mcm_Release`, `kree_register_sharedmem`. Present in the stock binary as
module-local symbols; all byte-identical after closure.

## 9. Locking summary

| API family | lock |
|---|---|
| multichunk append / release | `chmem_mutex` (interruptible, held across the secure-world call) |
| shared-memory register / unregister | `shared_mem_mutex_trusty` or `shared_mem_mutex_nebula`, selected by TEE id |
| `KREE_ConfigSecureMultiChunkMemInfo` | **none** |
| ION alloc/zalloc | none of their own; inherit the multichunk lock |
