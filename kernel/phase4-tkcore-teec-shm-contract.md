# GQ5012BF1 tkcore public TEEC shared-memory contract

Audit of the three public TEEC shared-memory APIs against stock. All three were **present but defective** before Phase 3B; each defect is proven from the stock ELF.

## Summary

| API | Stock offset | Stock / island size | KCFI | Call set | Class |
|---|---:|---:|---|---|---|
| `TEEC_RegisterSharedMemory` | `0x77d4` | 32 / 32 | `0x102c9243` | exact | **EXACT_BYTE** |
| `TEEC_AllocateSharedMemory` | `0x77f8` | 224 / 228 | `0x102c9243` | exact | CFG_EQUIVALENT |
| `TEEC_ReleaseSharedMemory` | `0x78dc` | 80 / 76 | `0x0dc79758` | exact | CFG_EQUIVALENT |

`Register` and `Allocate` share a KCFI id because they share a prototype: `TEEC_Result (TEEC_Context *, TEEC_SharedMemory *)`.

## `TEEC_SharedMemory` field usage

| Offset | Member | Register | Allocate | Release |
|---:|---|---|---|---|
| `0x00` | `buffer` | — | written (`shm->kaddr`) | cleared |
| `0x08` | `size` | — | read | — |
| `0x10` | `flags` | — | read + written | read (bit 17) |
| `0x18` | `d` | **zeroed (32-bit)** | written (64-bit ptr) | read (64-bit), then cleared |
| `0x20` | `registered` | **set to 1 (64-bit)** | set to 0 | read — early-return if non-zero |

## `TEEC_RegisterSharedMemory`

```c
if (!sharedMem) return TEEC_ERROR_BAD_PARAMETERS;
sharedMem->d.fd     = 0;      /* 32-bit store, stock: str wzr,[x1,#0x18] */
sharedMem->registered = 1;    /* 64-bit store, stock: str x8,[x1,#0x20]  */
return TEEC_SUCCESS;
```

- **`context` is completely ignored.** Stock performs no IDR lookup, no flags validation, no buffer or size validation, and calls nothing at all (32 bytes, empty call set). Registration is purely a marking operation.
- **Defect fixed:** the island wrote only `registered`, leaving a stale value in `d`. Since `TEEC_ReleaseSharedMemory` consumes `d` as a `struct tee_shm *`, a stale handle there is a latent wild pointer. Restoring the 32-bit zero store made the function byte-identical to stock.

## `TEEC_AllocateSharedMemory`

```c
struct tee_shm_io shm_io;
memset(&shm_io, 0, sizeof(shm_io));            /* all 24 bytes */

if (!context || !shared_memory || !context->fd)
        return TEEC_ERROR_BAD_PARAMETERS;

shm_io.size  = shared_memory->size;
shm_io.flags = shared_memory->flags | TEEC_MEM_KAPI;

ctx = tee_core_uuid2ptr(context->fd);
if (!ctx) { pr_err("bad context->fd %d provided\n", context->fd);
            return TEEC_ERROR_BAD_PARAMETERS; }

ret = tee_shm_alloc_io(ctx, &shm_io);
if (ret) { pr_err(...); return TEEC_ERROR_OUT_OF_MEMORY; }

shm = (struct tee_shm *)shm_io.buffer;         /* offset 0, NOT fd_shm */
shared_memory->flags      = shm_io.flags;
shared_memory->d.ptr      = shm;
shared_memory->registered = 0;
shared_memory->buffer     = shm->kaddr;
return TEEC_SUCCESS;
```

Allocate is **not** Register: it creates a new provider-backed `tee_shm` owned by the context (inserted into `ctx->list_shm` by `tee_shm_alloc_io`, holding a device reference, a provider reference and a context kref), and it sets `registered = 0` precisely so that `TEEC_ReleaseSharedMemory` *will* free it.

**Defect fixed — an uninitialized-pointer dereference.** Stock's `tee_shm_alloc_io` publishes the allocated object through `shm_io->buffer` (offset 0) on the kernel-client path:

```text
5df4: ldr w8, [x21, #0x8c]     ; ctx->usr_client
5df8: cbz w8, 0x5e70           ; kernel client ->
5e70: str x20, [x23]           ;   shm_io->buffer = shm
```

The island's `tee_shm_alloc_io` performed no such store, and the island's `TEEC_AllocateSharedMemory` read `shm_io.fd_shm` — a field written **only** on the `usr_client` path (`5e5c: str w0,[x23,#0x10]`). On a kernel client it was therefore reading uninitialized stack, truncating it through `int`, and dereferencing the result via `shm->kaddr`. Both halves are corrected and `shm_io` is now fully zeroed as stock does.

Zero-size behaviour is delegated unchanged to the provider `ops->alloc`; stock adds no special case.

## `TEEC_ReleaseSharedMemory`

```c
if (!shared_memory) return;
if (shared_memory->registered) return;                 /* caller-owned: not ours */
if (!(shared_memory->flags & TEEC_MEM_KAPI)) { BUG(); return; }

tee_shm_free_io((struct tee_shm *)shared_memory->d.ptr);

shared_memory->buffer = NULL;                          /* 64-bit */
shared_memory->d.ptr  = NULL;                          /* 64-bit */
```

Exact teardown order: `registered` check → KAPI guard → `tee_shm_free_io` (which removes the object from `ctx->list_shm` under `tee->lock`, calls `tkcore_shm_free`, then drops the provider reference, the context kref and the device reference) → clear `buffer` and `d`. The `flags` and `size` fields are deliberately **not** cleared, matching stock.

**The guard order is load-bearing.** `tmem_ffa` registers its buffer with `flags = 3` (`TEEC_MEM_INPUT|TEEC_MEM_OUTPUT`), i.e. **without** `TEEC_MEM_KAPI`, and then calls `TEEC_ReleaseSharedMemory` on it during every session teardown. Because `TEEC_RegisterSharedMemory` set `registered = 1`, the `registered` early-return fires first and the `BUG()` is never reached. Had the KAPI guard been placed first — an easy and plausible ordering mistake — this frozen consumer would `BUG()` on every normal close. The verifier asserts the source order explicitly.

**Two defects fixed:**

1. The island omitted the `TEEC_MEM_KAPI` guard and its `BUG()` entirely.
2. The island used `(struct tee_shm *)(long)shared_memory->d.fd` — an `int`→pointer cast that cannot round-trip a 64-bit kernel pointer. Stock loads the full 64-bit value (`7904: ldr x0,[x19,#0x18]`). This is the same truncation class the Phase-3A-R IDR work removed from the context/session APIs; Phase 3B removes the last instance of it.

## Error mapping

| Condition | Result |
|---|---|
| NULL `context`, `sharedMem`, or zero `context->fd` | `TEEC_ERROR_BAD_PARAMETERS` (`0xFFFF0006`) |
| IDR lookup failure | `TEEC_ERROR_BAD_PARAMETERS`, with a diagnostic naming the fd |
| `tee_shm_alloc_io` failure | `TEEC_ERROR_OUT_OF_MEMORY` (`0xFFFF000C`) |
| success | `TEEC_SUCCESS` |

`TEEC_ReleaseSharedMemory` returns `void`; every failure edge is a silent return or a `BUG()`.

## Cleanup on every failure edge

- `Register`: no allocation, nothing to unwind.
- `Allocate`: no partial state is published before `tee_shm_alloc_io` succeeds — `shared_memory` is untouched until the allocation returns 0. On failure the caller's structure is left exactly as it was.
- `Release`: the only failure edges are the two early returns and the `BUG()`; none of them frees anything or clears caller fields.
