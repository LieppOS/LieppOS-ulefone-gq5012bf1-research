# GQ5012BF1 tkcore TEEC session lifecycle contract

Scope: `TEEC_OpenSession` and `TEEC_CloseSession`, plus only the already-present marshalling/lifetime subset directly reached while opening or closing a session. This does not reconstruct or accept general `TEEC_InvokeCommand` behavior.

## ABI and closure

| API | Prototype | Stock offset | Stock / island size | KCFI | Calls | Closure |
|---|---|---:|---:|---|---|---|
| `TEEC_OpenSession` | `TEEC_Result (TEEC_Context *, TEEC_Session *, const TEEC_UUID *, uint32_t, const void *, TEEC_Operation *, uint32_t *)` | `0x74a0` | `412 / 412` | exact `0xde69c0a6` | exact | **SIZE_EXACT_SEMANTIC_EXACT** |
| `TEEC_CloseSession` | `void (TEEC_Session *)` | `0x7640` | `96 / 96` | exact `0x31bed4ef` | exact | **EXACT_BYTE** |

`TEEC_Session` remains `0x08` bytes. Its 32-bit `fd` at `+0x00` is a positive IDR id, never a kernel pointer or a truncated pointer.

## `TEEC_OpenSession`

### Inputs and command setup

1. A NULL `operation` is permitted by GlobalPlatform. Stock creates a zeroed stack `TEEC_Operation` and substitutes its address.
2. NULL `context`, `session`, or `destination` returns `TEEC_ERROR_BAD_PARAMETERS`.
3. After parameter validation, set `session->fd = 0`.
4. Resolve `context->fd` through `tee_core_uuid2ptr`. A missing context logs, writes `TEEC_ORIGIN_COMMS` when `return_origin` is non-NULL, and returns `TEEC_ERROR_BAD_PARAMETERS`.
5. Reset `struct tee_cmd_io`: `fd_sess = -1`, `cmd = 0`, `uuid = NULL`, `origin = TEEC_ORIGIN_API`, `err = TEEC_SUCCESS`, null data/op fields.
6. Set `cmd.op = operation` and `cmd.uuid = destination`.

### UUID and connection semantics

- The destination UUID is passed by pointer in `cmd.uuid`; `_init_tee_cmd` copies exactly `sizeof(TEEC_UUID)` into a temporary input buffer before the provider `open` call.
- `connectionMethod` and `connectionData` are intentionally unused. Stock performs no load, branch, copy, or validation based on either argument. The island does not invent login semantics absent from this stock binary.
- Open-session operation parameters use the existing `_init_tee_cmd` / `_update_client_tee_cmd` / `_release_tee_cmd` path. Only this open-time use is accepted here; the shared-memory subsystem and general invocation path remain Phase 3B/later work.

### Backend and lifetime order

`tee_session_create_and_open(ctx, &cmd)` performs the required sequence:

1. Take a provider reference with `tee_get`.
2. Allocate and zero `struct tee_session`.
3. Take a context kref and set `sess->ctx`.
4. Set `sess->sessid = 0`, initialize the command, and call `tee->ops->open(sess, &tee_cmd)`.
5. On a successful backend return, copy returned error/origin/operation state back to `cmd`; on backend failure, propagate backend `err` and `origin`.
6. Release temporary command buffers.
7. Under `tee->lock`, require `ret == 0`, nonzero `sessid`, and `cmd.err == TEEC_SUCCESS`; otherwise drop provider/context references and free the session.
8. On success under the same lock, increment session statistics and tail-add `sess->entry` to `ctx->list_sess`.

The top-level then allocates the session IDR handle and stores the raw result in `session->fd`.

### Return-origin and failure rules

- Failed create/open: `*return_origin = cmd.origin` when nonzero, otherwise `TEEC_ORIGIN_COMMS`; return `cmd.err` when nonzero, otherwise `TEEC_ERROR_COMMUNICATION`.
- Save `cmd.origin` before ID allocation.
- ID allocation failure: call `tee_session_close_and_destroy(sess)` before returning; set origin to `TEEC_ORIGIN_COMMS`; map `-ENOSPC`/`-ENOMEM` to `TEEC_ERROR_OUT_OF_MEMORY`, `-EINVAL` to `TEEC_ERROR_BAD_PARAMETERS`, and all other errors to `TEEC_ERROR_GENERIC`.
- Success: publish the saved origin when requested and return `cmd.err`.

Exact top-level call multiset: two `memset` sites, `tee_core_uuid2ptr`, `tee_session_create_and_open`, `tee_core_alloc_uuid`, `tee_session_close_and_destroy`, `_printk`, `__stack_chk_fail`.

## `TEEC_CloseSession`

Exact stock behavior and order:

1. NULL session or zero handle is a no-op.
2. Resolve the id with `tee_core_uuid2ptr`; a missing id logs and returns.
3. Remove the IDR id with `tee_core_free_uuid` **before** beginning backend/object teardown.
4. Call `tee_session_close_and_destroy(sess)`.

The destroy helper validates the object and nonzero secure-world `sessid`, calls `tee->ops->close(sess)`, then clears `sessid`. Under `tee->lock` it decrements session statistics, removes the session from `ctx->list_sess`, frees the session, drops the context kref, drops the provider reference, and unlocks. The backend close result is internal because `TEEC_CloseSession` returns `void`.

Exact call multiset: `tee_core_uuid2ptr`, `tee_core_free_uuid`, `tee_session_close_and_destroy`, `_printk`.

## IDR ordering invariant

```text
successful backend open
  → session linked under tee->lock
  → positive IDR id published in TEEC_Session.fd
  ...
  → IDR id removed
  → backend close
  → sessid cleared
  → list/stat/reference teardown under tee->lock
```

A handle therefore cannot newly resolve after object teardown starts.

## Layout gates

The build-enforced layout probe passes:

- `sizeof(TEEC_Session) == 0x08`
- `TEEC_Session.fd == +0x00`
- `sizeof(struct tee_context) == 0xd0`
- `struct tee_context.list_sess == +0xa0`

## Scope boundary

No general `TEEC_InvokeCommand`, shared-memory registration/allocation/release, supplicant/RPC command handling, or secure-SPI runtime was reconstructed or accepted here. OpenSession's destination UUID and optional open operation are the only command-marshalling use included.

## Verdict

`TEEC_OpenSession` is size-exact and semantically exact with exact KCFI/call set. `TEEC_CloseSession` is byte-identical. UUID handling, stock-unused connection arguments, backend order, origin propagation, IDR lifecycle, and close/error cleanup are statically closed.
