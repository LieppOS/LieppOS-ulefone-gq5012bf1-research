# GQ5012BF1 tkcore island Phase 3B — tmem_ffa static shared-memory trace

**Result: PASS_STATIC_SHM**

Offline relocation/disassembly trace of the frozen stock consumer. Nothing was loaded, no ioctl issued, no secure world entered.

## Consumer oracle

- Module: `workspace/phase4-tkcore/oracle/tmem_ffa.ko`
- SHA-256: `707e26674abbe7f9c695bb949d74fd5de04972d4bbb991cddc3a2ea9ab45f01b`
- Disassembly: `workspace/phase4-tkcore-island/phase3b/tmem_ffa.objdump.txt`

## Full proven lifecycle

| Consumer function | Offset | tkcore edge |
|---|---:|---|
| `tee_session_open` | `0x5a6c` | `TEEC_InitializeContext` |
| `tee_session_open` | `0x5aa4` | **`TEEC_RegisterSharedMemory`** |
| `tee_session_open` | `0x5ac8` | `TEEC_OpenSession` |
| `tee_session_open` | `0x5b98` | **`TEEC_ReleaseSharedMemory`** (error unwind) |
| `tee_session_open` | `0x5bac` | `TEEC_FinalizeContext` (error unwind) |
| `tee_session_close` | `0x5c28` | `TEEC_CloseSession` |
| `tee_session_close` | `0x5c34` | **`TEEC_ReleaseSharedMemory`** |
| `tee_session_close` | `0x5c3c` | `TEEC_FinalizeContext` |

This is exactly the required sequence, now including the shared-memory calls that Phase 3A-R had to leave open:

```text
TEEC_InitializeContext
  → TEEC_RegisterSharedMemory
  → TEEC_OpenSession
  ...
  → TEEC_CloseSession
  → TEEC_ReleaseSharedMemory
  → TEEC_FinalizeContext
```

## Object placement — all three types in one state block

`tmem_ffa` allocates a single `0x140`-byte state object (`.bss+0x430`) and carves it up:

| State offset | Type | Proof |
|---:|---|---|
| `+0x000` | `TEEC_Context` (`0x108`) | `TEEC_InitializeContext(NULL, state+0)` |
| `+0x108` | `TEEC_Session` (`0x08`) | `add x1, x0, #0x108` into `TEEC_OpenSession` |
| `+0x110` | `TEEC_SharedMemory` (`0x28`) | `add x1, x0, #0x110` into `TEEC_RegisterSharedMemory` |
| `+0x138` | `void *` to a separately kmalloc'd `0x48` buffer | `ldr x9,[x0,#0x138]` |

`0x110 + 0x28 = 0x138`, so the three objects tile the state block exactly. This independently re-confirms `sizeof(TEEC_SharedMemory) == 0x28`.

## Registration field-by-field

```text
5a80: x9  = state->[0x138]          ; the 0x48-byte payload buffer
5a7c: x10 = 0x48                    ; size
5a78: w8  = 3                       ; flags
5a8c: stp x9, x10, [x0, #0x110]     ; shm.buffer = buf ; shm.size = 0x48
5a88: str w8,     [x0, #0x120]      ; shm.flags  = 3
5a90..5aa0: zero the 0x48 payload
5aa4: TEEC_RegisterSharedMemory(state+0x000, state+0x110)
```

Relative to the `TEEC_SharedMemory` base at `+0x110`: `buffer@+0x00`, `size@+0x08`, `flags@+0x10`. Exactly the layout Phase 3B asserts.

- `flags = 3` = `TEEC_MEM_INPUT | TEEC_MEM_OUTPUT`.
- The consumer does **not** set `TEEC_MEM_KAPI`.
- The consumer never writes `d` or `registered`; it relies on `TEEC_RegisterSharedMemory` to initialise both — which is precisely the store the island was missing and Phase 3B restored.

## The critical ordering check

Stock `TEEC_ReleaseSharedMemory` contains a `BUG()` when `TEEC_MEM_KAPI` is absent. `tmem_ffa` registers with `flags = 3`, which does **not** include `TEEC_MEM_KAPI`, and then calls `TEEC_ReleaseSharedMemory` on that very object.

This does not fire, because stock's guard order is:

1. `if (!shm) return;`
2. `if (shm->registered) return;` ← **tmem_ffa exits here**
3. `if (!(shm->flags & TEEC_MEM_KAPI)) { BUG(); return; }`
4. `tee_shm_free_io(shm->d.ptr); shm->buffer = NULL; shm->d.ptr = NULL;`

`TEEC_RegisterSharedMemory` sets `registered = 1`, so step 2 always short-circuits for a registered buffer. Had the island implemented the KAPI guard *before* the `registered` check — an easy and plausible mistake — this frozen consumer would `BUG()` on every normal session teardown. The island's order is stock's, and this trace is what proves it matters.

It also means `TEEC_ReleaseSharedMemory` is a no-op for `tmem_ffa`'s registered buffer: the payload is `kfree`d by the consumer itself (`0x5c48`/`0x5c54`), not by tkcore. Ownership stays with the consumer, exactly as the `registered` flag advertises.

## ABI

| API | Stock KCFI | Island KCFI | Class |
|---|---|---|---|
| `TEEC_RegisterSharedMemory` | `0x102c9243` | `0x102c9243` | **EXACT_BYTE** |
| `TEEC_AllocateSharedMemory` | `0x102c9243` | `0x102c9243` | CFG_EQUIVALENT |
| `TEEC_ReleaseSharedMemory` | `0x0dc79758` | `0x0dc79758` | CFG_EQUIVALENT |

All three are present in the island exports with exact KCFI and exact stock call multisets.

## Scope boundary

`secmem_execute` calls `TEEC_InvokeCommand`, which is **not** reconstructed in Phase 3B. This trace therefore covers the context/session/shared-memory lifecycle only and is not full `tmem_ffa` runtime acceptance.

## Verdict

Object placement, field layout, registration semantics, release ordering, ownership of the registered payload, and error-unwind ordering are all consistent with the reconstructed shared-memory subsystem.

**PASS_STATIC_SHM**
