# GQ5012BF1 tkcore TEEC context lifecycle contract

Scope: `TEEC_InitializeContext` and `TEEC_FinalizeContext` only. Shared memory, command invocation, RPC/supplicant commands, and secure-SPI runtime remain excluded.

## ABI and closure

| API | Prototype | Stock offset | Stock / island size | KCFI | Calls | Closure |
|---|---|---:|---:|---|---|---|
| `TEEC_InitializeContext` | `TEEC_Result (const char *, TEEC_Context *)` | `0x7304` | `240 / 216` | exact `0x124b473b` | exact | **CFG_EQUIVALENT** |
| `TEEC_FinalizeContext` | `void (TEEC_Context *)` | `0x73f8` | `164 / 176` | exact `0xf4c49135` | exact | **CFG_EQUIVALENT** |

`TEEC_Context` remains `0x108` bytes. Its opaque identifier is the 32-bit `fd` at `+0x100`. It contains an IDR id, never a kernel pointer or a truncated pointer.

## `TEEC_InitializeContext`

Stock order and semantics reproduced:

1. NULL `context` returns `TEEC_ERROR_BAD_PARAMETERS`.
2. Set `context->fd = 0` before lookup.
3. Copy `name`, or the stock default `"tkcore_client"` when `name == NULL`, into the fixed device-name field with `strncpy` and the full field size. This preserves stock's possible non-NUL-termination for a maximum-length input.
4. `tee_get_tee(context->devname)` performs `class_find_device()` on the captured misc class, accepts only a descriptor whose `name_lookup` byte is set, and returns the parent device's driver data (`struct tee *`). Of the three registered nodes only `tkcore_client` has `name_lookup = 1`.
5. Stock has no `put_device` call in `tee_get_tee`; the island does not invent one. The exact stock call set is `class_find_device`, `_printk`.
6. `tee_context_create(tee)` allocates and initializes a `0xd0` context, takes the provider ref through `tee_get`, then under `tee->lock` increments context statistics and tail-adds `ctx->entry` to `tee->list_ctx`.
7. A failed context creation returns `TEEC_ERROR_BAD_PARAMETERS`. The helper frees its own allocation and releases anything it acquired on its internal failure paths.
8. Set `ctx->usr_client = 0` and `ctx->ctx_priv = NULL`.
9. Allocate a positive IDR handle with `tee_core_alloc_uuid(ctx)` and store its raw result in `context->fd`.
10. IDR errors map exactly: `-ENOSPC`/`-ENOMEM` → `TEEC_ERROR_OUT_OF_MEMORY`; `-EINVAL` → `TEEC_ERROR_BAD_PARAMETERS` with the stock diagnostic; everything else → `TEEC_ERROR_GENERIC`.
11. Stock does **not** call `tee_context_destroy` after an IDR allocation error (proven by its call set), so the island does not silently add a cleanup call. The negative allocator result remains in `context->fd`.

Exact call multiset: `strncpy`, `tee_get_tee`, `tee_context_create`, `tee_core_alloc_uuid`, two `_printk` sites.

## `TEEC_FinalizeContext`

Stock valid-handle order reproduced:

1. Reject NULL or zero-handle input through the diagnostic path.
2. Resolve `context->fd` with `tee_core_uuid2ptr` (`idr_find`). A missing id logs and returns without destroying anything.
3. Remove the IDR id with `tee_core_free_uuid` **before** object destruction.
4. Call `tee_context_destroy(ctx)`.
5. Do not clear `context->fd`; stock has no such store.

`tee_context_destroy` locks `tee->lock` and drops the context kref. Final release, still under that lock, decrements statistics, removes `ctx->entry` from `tee->list_ctx`, frees the context, and drops the provider reference through `tee_put`.

Exact call multiset: `tee_core_uuid2ptr`, `tee_core_free_uuid`, `tee_context_destroy`, `strnlen`, two `_printk` sites, `fortify_panic`.

### Documented defensive divergence

Stock's malformed NULL/zero-handle diagnostic formats the device-name member even when `context == NULL`, which can fault. The island emits the same diagnostic shape but refuses to dereference a NULL pointer. This accounts for code-layout difference only; the valid lifecycle and all external calls remain stock-equivalent.

## Lifetime invariant

```text
provider lookup
  → tee_context_create
      → tee_get(provider)
      → list_ctx insertion under tee->lock
  → IDR handle published
  ...
  → IDR handle removed
  → tee_context_destroy
      → kref final release under tee->lock
      → list_ctx removal
      → context free
      → tee_put(provider)
```

The ID is removed before object destruction, so a later lookup cannot newly obtain a pointer to an already-destroying context. No pointer-to-int conversion exists.

## Layout gates

The build-enforced layout probe passes:

- `sizeof(TEEC_Context) == 0x108`
- `sizeof(struct tee_context) == 0xd0`
- `name == +0x08`
- `tgid == +0x88`
- `usr_client == +0x8c`
- `entry == +0x90`
- `list_sess == +0xa0`
- `list_shm == +0xb0`
- `refcount == +0xc0`

## Verdict

Both APIs have exact prototypes/KCFI and exact stock call sets. Context/provider references, list locking, IDR publication/removal, error mapping, and valid-handle cleanup ordering are closed statically.
