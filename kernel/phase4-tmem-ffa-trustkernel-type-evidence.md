# TrustKernel type evidence proved by `tmem_ffa.ko`

This is an independent, second consumer view of TrustKernel's client ABI
(the first was `microarray_fp_tee`, the third `tkcore_drv`). Everything below
is confirmed twice: once by stock disassembly, once by the fact that the
source-built module is **141/141 byte-identical** when compiled against these
types.

## 1. Headline

The TrustKernel TEEC type graph already reconstructed in
`lieppos/tkcore-recon/include/tk_tee_client_api.h` is **confirmed correct** by
an unrelated MediaTek consumer:

| type | size | independent proof from `tmem_ffa` |
|---|---:|---|
| `TEEC_Context` | `0x108` (264) | `session` sits at `+0x108` of the session-data block (`add x1, x0, #0x108`) |
| `TEEC_Session` | 8 | `wsm` sits at `+0x110`, i.e. 8 bytes after the session |
| `TEEC_SharedMemory` | `0x28` (40) | `wsm_buffer` sits at `+0x138`, i.e. 40 bytes after `wsm` |
| `TEE_GP_SESSION_DATA` | `0x140` (320) | `kmalloc_trace` size constant `mov w2, #0x140` |
| `TEEC_Operation` | `0x118` (280) | stack frame + `memset(&op, 0, sizeof op)` in `secmem_execute` |

The teei/510 (`MicroTrust`) header — whose `TEEC_Context` is a single
`struct file *` — is **excluded**: building against it changes
`secmem_execute`/`tee_session_open` code size. This is a hard, reproducible
discriminator.

## 2. `TEEC_Context`

| fact | status |
|---|---|
| total size 264 bytes | `PROVEN_EXACT` |
| embedded in a caller-allocated block, never allocated by the client API | `PROVEN_EXACT` |
| passed by address to `TEEC_InitializeContext`, `TEEC_RegisterSharedMemory`, `TEEC_OpenSession`, `TEEC_FinalizeContext` | `PROVEN_EXACT` |
| first member is a 256-byte device-name array; tail is an 8-byte union (`struct tee_context *` / `int fd`) | `PROVEN_SEMANTICS_OFFSETS_ONLY` (layout from `tkcore`'s own `TEEC_InitializeContext`; `tmem_ffa` only proves the total size) |
| the name argument may be `NULL` on this device | `PROVEN_EXACT` |
| member **spellings** (`devname`, `ctx`, `fd`) | **UNKNOWN** — cannot be recovered from stripped ELF |

## 3. `TEEC_Session`

- 8 bytes, embedded immediately after the context — `PROVEN_EXACT`.
- Written only by `TEEC_OpenSession`; read by `TEEC_InvokeCommand` and
  `TEEC_CloseSession` — `PROVEN_EXACT`.
- `tmem_ffa` never dereferences session fields itself: the object is opaque to
  the consumer. That is new, useful information — a reconstructed `tkcore` may
  choose any internally consistent 8-byte representation without breaking this
  consumer's code generation.

## 4. `TEEC_SharedMemory`

40 bytes. Members actually written by `tmem_ffa` (`PROVEN_EXACT`):

| offset | width | use |
|---:|---:|---|
| `0x00` | 8 | `buffer` — kernel pointer to the client-allocated message |
| `0x08` | 8 | `size` — `sizeof(struct secmem_ta_msg_t)` |
| `0x10` | 4 | `flags` — `TEEC_MEM_INPUT|TEEC_MEM_OUTPUT` = 3 |
| `0x18`,`0x20` | 8+8 | zeroed by the client before registration (`stp xzr, xzr`) — implementation-defined id/registration tail |

Ownership: the *buffer* is owned by `tmem_ffa` (`kmalloc`/`kfree`); the
*registration* is owned by `tkcore` between `TEEC_RegisterSharedMemory` and
`TEEC_ReleaseSharedMemory`. `TEEC_AllocateSharedMemory` is never used, so no
API-allocated buffer lifetime exists on this device.

## 5. `TEEC_Operation` and `TEEC_Parameter`

- 280 bytes, stack-allocated, fully zeroed before use — `PROVEN_EXACT`.
- `started` (`+0x00`) is left 0; `paramTypes` (`+0x04`) is set to `0x0000000F`
  (`TEEC_MEMREF_PARTIAL_INOUT` in slot 0) — `PROVEN_EXACT`.
- `params[0]` is used as a **registered** memref: `parent` (pointer to the
  `TEEC_SharedMemory`), `size`, `offset = 0`. `params[1..3]` stay `TEEC_NONE`.
- The 280-byte size implies the trailing implementation-defined area after the
  4×24-byte parameter array (session pointer + a 4×40-byte `memRefs` array +
  8-byte flags in the reconstructed header). `tmem_ffa` never touches that
  area — it is owned by the provider.
- Parameter-type encoding `TEEC_PARAM_TYPES(p0,p1,p2,p3) = p0|p1<<4|p2<<8|p3<<12`
  is confirmed by the literal `0xF`.

## 6. `TEEC_UUID`

16 bytes, `{uint32 timeLow, uint16 timeMid, uint16 timeHiAndVersion,
uint8 clockSeqAndNode[8]}`; the device's secure-memory TA is
`08030000-0000-0000-0000-000000000000`, materialised on the stack and passed by
const pointer to `TEEC_OpenSession` — `PROVEN_EXACT`.

## 7. `struct tee` / `struct tee_context` / `struct tee_ops`

`tmem_ffa` does **not** touch these types: it imports none of
`tee_core_alloc/add/del/free`, `__tee_get` or `tee_supp_cmd`. Therefore this
consumer adds **no** new evidence about them, and in particular cannot unblock
the 11 `PROVIDER_ABI_BLOCKED` tkcore CRCs that hash those structs' member
names. Stating that clearly is part of the result.

## 8. Semantics that become nameable

| semantic | evidence |
|---|---|
| a TEEC context is a *fat* client-side object (264 B), not a handle | `tmem_ffa` + `tkcore` agree |
| a session is a *thin* 8-byte handle | new here |
| shared memory is 40 B and registration-based on this device | new here |
| the client, not the API, owns shared buffers | new here |
| operations are one-shot, stack-allocated, fully zeroed, never cancelled | new here |
| `returnOrigin` is optional (`NULL` accepted) | new here |
| a `NULL` TEE name is accepted by `TEEC_InitializeContext` | new here |

## 9. What remains impossible

Binary evidence proves **offsets, sizes, directions, lifetimes and call
ordering**. It cannot prove the historical **C member spellings** inside
TrustKernel's private structs, which is precisely what genksyms hashes for the
11 blocked `tkcore` exports. No amount of additional consumer analysis changes
that; only an original TrustKernel header would.
