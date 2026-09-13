# `tmem_ffa.ko` — exact TEEC call flow (TrustKernel peer)

Every sequence below is `PROVEN_EXACT`: it is read from stock disassembly and
reproduced byte-for-byte by the source-built module (141/141).

## 1. Objects

```c
struct TEE_GP_SESSION_DATA {              /* kmalloc(0x140) */
        struct TEEC_Context      context;      /* @0x000, 0x108 bytes */
        struct TEEC_Session      session;      /* @0x108, 8 bytes      */
        struct TEEC_SharedMemory wsm;          /* @0x110, 0x28 bytes   */
        void                    *wsm_buffer;   /* @0x138               */
};
static struct TEE_GP_SESSION_DATA *g_sess_data;   /* .bss +0x430 */
static bool is_sess_ready;                         /* .bss +0x42c */
static struct mutex g_sess_lock;                   /* .data +0x1b90 */
```

Offsets are stock facts: `add x1, x0, #0x108` (session), `[x8, #0x110]` (wsm),
`[x8, #0x138]` (wsm_buffer), `mov w2, #0x140` at the `kmalloc_trace` call.

## 2. UUID and identifiers

| item | value | status |
|---|---|---|
| TA UUID (`SECMEM_TL_GP_UUID`) | `08030000-0000-0000-0000-000000000000` | `PROVEN_EXACT` |
| TEE name passed to `TEEC_InitializeContext` | `NULL` | `PROVEN_EXACT` (stock `mov x0, xzr`) |
| login method | `TEEC_LOGIN_PUBLIC` (0) | `PROVEN_EXACT` |
| shared-memory flags | `TEEC_MEM_INPUT | TEEC_MEM_OUTPUT` = 3 | `PROVEN_EXACT` |
| wsm size | `sizeof(struct secmem_ta_msg_t)` = 64 (`mov w2, #0x40`-class zeroing) | `PROVEN_EXACT` |

## 3. Session open — `tee_session_open()` → `tee_session_open_single_session_unlocked()`

| # | step | object | notes |
|---|---|---|---|
| 1 | `mutex_lock(&g_sess_lock)` | — | entry from `.session_open` op |
| 2 | early-out if `is_sess_ready` | — | idempotent |
| 3 | `kmalloc(0x140, GFP_KERNEL)` | `g_sess_data` | zeroed by callee |
| 4 | `kmalloc(sizeof(secmem_ta_msg_t))` | `wsm_buffer` | GFP_KERNEL |
| 5 | `TEEC_InitializeContext(NULL, &ctx)` | `TEEC_Context` | error → `err_initialize_context` |
| 6 | fill `wsm.buffer/size/flags`, `memset(buffer,0,size)` | `TEEC_SharedMemory` | INPUT\|OUTPUT |
| 7 | `TEEC_RegisterSharedMemory(&ctx, &wsm)` | shared memory | error → `err_register_shared_memory` |
| 8 | `TEEC_OpenSession(&ctx, &sess, &uuid, TEEC_LOGIN_PUBLIC, NULL, NULL, NULL)` | session | `connectionData`, `operation`, `returnOrigin` all NULL |
| 9 | `is_sess_ready = true` | — | |
| 10 | `mutex_unlock(&g_sess_lock)` | — | |

Cleanup ordering (strict reverse, stock-verified):

```
err_open_session:            pr_err("TEEC_ReleaseSharedMemory"); TEEC_ReleaseSharedMemory(&wsm);
err_register_shared_memory:  pr_err("TEEC_FinalizeContext");     TEEC_FinalizeContext(&ctx);
err_initialize_context:      kfree(wsm_buffer);
err_create_wsm_buffer:       kfree(g_sess_data); g_sess_data = NULL;
return TMEM_TEE_CREATE_SESSION_FAILED;
```

## 4. Command invocation — `secmem_execute(u32 cmd, struct secmem_param *param)`

| # | step | detail |
|---|---|---|
| 1 | `TEE_SESSION_LOCK()` | `mutex_lock(&g_sess_lock)` |
| 2 | reject if `!is_sess_ready` | returns `TMEM_TEE_SESSION_IS_NOT_READY` |
| 3 | `memset(wsm.buffer, 0, wsm.size)` | full message clear |
| 4 | fill `struct secmem_ta_msg_t` | `sec_handle`, `alignment`, `size`, `refcount` |
| 5 | `memset(&op, 0, sizeof(struct TEEC_Operation))` | stack object, `0x118` bytes |
| 6 | `op.paramTypes = TEEC_PARAM_TYPES(TEEC_MEMREF_PARTIAL_INOUT, NONE, NONE, NONE)` = `0x0000000F` | one INOUT registered memref |
| 7 | `op.params[0].memref = { .parent = &wsm, .offset = 0, .size = wsm.size }` | whole window |
| 8 | `TEEC_InvokeCommand(&session, cmd, &op, NULL)` | `returnOrigin = NULL` |
| 9 | on failure: `pr_err`, unlock, return the TEEC result verbatim | no retry |
| 10 | copy back `sec_handle`, `refcount`, `alignment`, `size` from the message | INOUT semantics |
| 11 | `TEE_SESSION_UNLOCK()` | |

`struct secmem_ta_msg_t` (`tee_gp_def.h`, 64 bytes):
`u64 alignment` (IN), `u64 size` (IN), `u32 refcount` (INOUT),
`u64 sec_handle` (OUT), `u8 name[32]` (debug), `u32 id` (debug).

## 5. Command IDs (`PROVEN_EXACT`, from `tee_impl/tee_ops.h`)

| op | SVP | WFD | 2D-FR | SDSP |
|---|---:|---:|---:|---:|
| alloc | 1 | 30 | 50 | 40 |
| alloc-zero | 13 | 34 | 54 | 44 |
| unref | 3 | 31 | 51 | 41 |
| region enable | 7 | 32 | 52 | 42 |
| region disable | 8 | 33 | 53 | 43 |

Control commands: `CMD_SEC_MEM_SET_PROT_REGION` 100, `CMD_SEC_MEM_DUMP_MEM_INFO`
101, `CMD_SEC_MEM_DYNAMIC_DEBUG_CONFIG` 102, `CMD_WFD_SMEM_DUMP_MEM_INFO` 103,
`CMD_SEC_MEM_FORCE_HW_PROTECTION` 104, `CMD_SEC_MEM_SET_MCHUNKS_REGION` 105
(not reachable on this device), `CMD_2D_FR_SMEM_DUMP_MEM_INFO` 106,
`CMD_SEC_MEM_SET_SVP_REGION` 107, `CMD_SEC_MEM_SET_WFD_REGION` 108,
`CMD_SEC_MEM_SET_SAPU_DATA_SHM_REGION` 109,
`CMD_SEC_MEM_SET_SAPU_ENGINE_SHM_REGION` 110, `CMD_SEC_MEM_DUMP_INFO` 255,
`CMD_SEC_MEM_INVALID` `0xFFFFFFFF`.

Command *semantics inside the TA* are **`UNKNOWN`** and are not fabricated
here; only the kernel-side encoding is proven.

## 6. Session close — `tee_session_close()`

`TEEC_CloseSession(&session)` → `TEEC_ReleaseSharedMemory(&wsm)` →
`TEEC_FinalizeContext(&ctx)` → `kfree(wsm_buffer)` → destroy session data →
`is_sess_ready = false`. Ordering is stock-verified and is the exact inverse of
open.

## 7. Paths NOT used

`TEEC_AllocateSharedMemory` and `TEEC_RequestCancellation` are **not** imported:
`tmem_ffa` only ever *registers* client-allocated memory. There is no
`TEEC_Operation.started` cancellation use, and `returnOrigin` is never read
(always `NULL`).

## 8. Confidence labels

| item | label |
|---|---|
| object layout, sizes, offsets | `PROVEN_EXACT` |
| call ordering + cleanup ordering | `PROVEN_EXACT` |
| paramTypes, flags, login, UUID, command IDs | `PROVEN_EXACT` |
| what each command does inside the TA | `UNKNOWN` |
| secure-world memory policy | `UNKNOWN` |
