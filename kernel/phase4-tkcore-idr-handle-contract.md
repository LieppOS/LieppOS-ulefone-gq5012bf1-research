# GQ5012BF1 tkcore opaque-handle (IDR) contract

All three helpers are reconstructed **byte-identically** to stock.

| Function | Stock offset | Size | KCFI | Phase-3A-R |
|---|---:|---:|---|---|
| `tee_core_alloc_uuid` | `0x19a0` | 168 | `0x89fb613d` | **EXACT_BYTE** |
| `tee_core_uuid2ptr` | `0x1a4c` | 40 | `0xb382e080` | **EXACT_BYTE** |
| `tee_core_free_uuid` | `0x1a78` | 40 | `0x019c0cac` | **EXACT_BYTE** |

## Why this exists

`TEEC_Context` carries a 32-bit identifier at offset `0x100` and `TEEC_Session` carries one at offset `0x00`. The OP-TEE donor stored a **truncated kernel pointer** there:

```c
context->fd = (int)(uintptr_t)ctx;
BUG_ON(ctx != (struct tee_context *)(uintptr_t)context->fd);
```

Its own comment admitted `will not work on 64-bit platform`. On arm64 that either truncates a real pointer or trips the `BUG_ON`.

Stock does not do this. It keeps a module-global IDR and stores a small positive id. That is proven by the relocations in all four TEEC entry points and by the three helpers below.

## Globals

| Object | Location | Role |
|---|---|---|
| id allocator | `.bss+0x10` | `struct idr` |
| lock | `.bss+0x8` | `spinlock_t` guarding allocation |

Both are statically initialised (`DEFINE_IDR` / `DEFINE_SPINLOCK`).

## `tee_core_alloc_uuid(void *ptr)`

```c
idr_preload(GFP_KERNEL);              /* 0xcc0 */
spin_lock(&tee_idr_lock);
rv = idr_alloc(&tee_idr, ptr, 1, 0, GFP_NOWAIT);   /* start=1, end=0, gfp=0x800 */
if (rv < 0)
        pr_err("Bad alloc tee_uuid. rv: %d\n", rv);
spin_unlock(&tee_idr_lock);
idr_preload_end();
return rv;
```

Proven details, all reproduced:

- **`start = 1`**: id `0` is never handed out, so `0` doubles as "no handle". Every caller relies on this (`if (!context->fd) ...`).
- **`end = 0`**: no upper bound (full `INT_MAX` range).
- **`GFP_NOWAIT` inside the lock**, with the sleeping allocation hoisted into `idr_preload` outside it. This is the standard IDR pattern and is what makes a spinlock legal here.
- The error message is emitted **while still holding the lock** (stock branches to the print, then falls through to the unlock).
- The raw allocator result is returned, including the negative errno.

## `tee_core_uuid2ptr(int uuid)`

```c
return idr_find(&tee_idr, uuid);
```

No lock. Stock relies on the caller-visible lifetime rule that a handle is only looked up while its owner is alive; this is reproduced rather than "improved" with RCU or a lock that stock does not take.

## `tee_core_free_uuid(int uuid)`

```c
idr_remove(&tee_idr, uuid);
```

Also unlocked in stock.

## Handle lifetime by owner

| Owner | Allocated in | Freed in | Field |
|---|---|---|---|
| `struct tee_context` | `TEEC_InitializeContext` | `TEEC_FinalizeContext` | `TEEC_Context.fd` @`0x100` |
| `struct tee_session` | `TEEC_OpenSession` | `TEEC_CloseSession` | `TEEC_Session.fd` @`0x00` |

Both release paths free the id **before** destroying the object, so a concurrent lookup can never resolve a handle to memory that is already being torn down.

## Error mapping

`tee_core_alloc_uuid` failures reach the GlobalPlatform surface through a shared mapping:

| errno | TEEC result |
|---|---|
| `-ENOSPC` (`-28`) | `TEEC_ERROR_OUT_OF_MEMORY` (`0xFFFF000C`) |
| `-ENOMEM` (`-12`) | `TEEC_ERROR_OUT_OF_MEMORY` |
| `-EINVAL` (`-22`) | `TEEC_ERROR_BAD_PARAMETERS` (`0xFFFF0006`) |
| anything else | `TEEC_ERROR_GENERIC` (`0xFFFF0000`) |

Stock asymmetry, reproduced: `TEEC_InitializeContext` logs `context->fd is invalid` on the `-EINVAL` case, `TEEC_OpenSession` maps the same value silently.

## Consequence for the island

No pointer is ever cast into an `int`. `TEEC_Context` and `TEEC_Session` keep their proven sizes (`0x108` / `0x8`) and their identifier unions, but only the 32-bit member is ever written or read. The two out-of-scope functions that still consume those identifiers (`TEEC_InvokeCommand`, `TEEC_AllocateSharedMemory`) were switched to `tee_core_uuid2ptr()` as well, so no latent handle/pointer type confusion is left behind; their command and shared-memory bodies were not otherwise touched.
