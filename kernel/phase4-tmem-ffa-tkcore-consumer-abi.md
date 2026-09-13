# `tmem_ffa.ko` → `tkcore` consumer ABI (exact edge report)

Seven tkcore edges were **independently rediscovered** by inventorying the
stock ELF's undefined symbols and `__versions` table — not taken from prior
notes. `TEEC_AllocateSharedMemory` and `TEEC_RequestCancellation` are *not*
consumed; the count is exactly seven.

| # | symbol | stock CRC (consumer `__versions` = provider `__kcrctab`) | tkcore export set |
|---|---|---|---|
| 1 | `TEEC_InitializeContext` | `0x89b94f9a` | **BLOCKED** 11/25 |
| 2 | `TEEC_RegisterSharedMemory` | `0xa7bb0a46` | **BLOCKED** 11/25 |
| 3 | `TEEC_OpenSession` | `0xe821e2a3` | **BLOCKED** 11/25 |
| 4 | `TEEC_FinalizeContext` | `0x7b3bc43f` | **BLOCKED** 11/25 |
| 5 | `TEEC_InvokeCommand` | `0x202b681e` | NATURAL 14/25 |
| 6 | `TEEC_CloseSession` | `0xcb193c37` | NATURAL 14/25 |
| 7 | `TEEC_ReleaseSharedMemory` | `0xc4d15e1c` | NATURAL 14/25 |

Split for this consumer: **3 NATURAL / 4 PROVIDER_ABI_BLOCKED**. All four
blocked ones are blocked for the same reason — they take `TEEC_Context *`,
whose tail union names `struct tee_context`.

---

## 1. `TEEC_InitializeContext` — `0x89b94f9a`

- **Prototype** (provider KCFI `0x124b473b`):
  `TEEC_Result TEEC_InitializeContext(const char *name, struct TEEC_Context *context)`
- **Call sites**: 1 — `tee_session_open` (inlining
  `tee_session_open_single_session_unlocked`).
- **Arguments**: `x0 = NULL` (stock `mov x0, xzr`), `x1 = &g_sess_data->context`
  (offset `+0x00` of a freshly `kmalloc`'d 320-byte block).
- **Return handling**: compared against `TEEC_SUCCESS` (0); non-zero →
  `pr_err("TEEC_InitializeContext failed: %x")` and jump to
  `err_initialize_context`.
- **Error path**: `kfree(wsm_buffer)` then destroy session data; the context is
  *not* finalized (correct: it was never initialized).
- **Ownership/lifetime**: the context memory is owned by `tmem_ffa` for the
  whole module lifetime; tkcore owns whatever the tail union points at between
  initialize and finalize.
- **Structures**: `TEEC_Context` (264 B) only.
- **Constants**: `NULL` name — a hard fact about this device's TrustKernel
  build (it accepts a default TEE).

## 2. `TEEC_RegisterSharedMemory` — `0xa7bb0a46`

- **Prototype** (KCFI `0x102c9243`, shared with `TEEC_AllocateSharedMemory`):
  `TEEC_Result TEEC_RegisterSharedMemory(struct TEEC_Context *, struct TEEC_SharedMemory *)`
- **Call sites**: 1 — `tee_session_open`.
- **Arguments**: `x0 = &ctx` (`+0x00`), `x1 = &wsm` (`+0x110`), with
  `wsm.buffer` = `kmalloc(sizeof(secmem_ta_msg_t))`, `wsm.size` = 64,
  `wsm.flags` = `TEEC_MEM_INPUT|TEEC_MEM_OUTPUT` (3), and the implementation
  tail pre-zeroed by the caller.
- **Return handling**: non-zero → `pr_err("TEEC_RegisterSharedMemory failed: %x")`
  → `err_register_shared_memory` → `TEEC_FinalizeContext` → `kfree` → destroy.
- **Ownership**: buffer owned by the consumer; registration owned by tkcore
  until `TEEC_ReleaseSharedMemory`.
- **Evidence value**: proves registration (not allocation) is the model here,
  and that the caller zeroes the implementation-defined tail before the call.

## 3. `TEEC_OpenSession` — `0xe821e2a3`

- **Prototype** (KCFI `0xde69c0a6`):
  `TEEC_Result TEEC_OpenSession(struct TEEC_Context *, struct TEEC_Session *,
  const struct TEEC_UUID *, uint32_t connectionMethod, const void *connectionData,
  struct TEEC_Operation *, uint32_t *returnOrigin)`
- **Call sites**: 1 — `tee_session_open`.
- **Arguments**: `x0 = &ctx`, `x1 = &session` (`+0x108`), `x2 = &uuid`
  (stack copy of `08030000-0000-0000-0000-000000000000`), `w3 = 0`
  (`TEEC_LOGIN_PUBLIC`), `x4 = NULL`, `x5 = NULL`, `x6 = NULL`.
- **Return handling**: non-zero → `pr_err("TEEC_OpenSession failed: %x")` →
  `err_open_session` → release shm → finalize ctx → free → destroy.
- **Evidence value**: 7-argument ABI confirmed; three trailing NULLs prove the
  optional-ness of `connectionData`, `operation` and `returnOrigin`.

## 4. `TEEC_FinalizeContext` — `0x7b3bc43f`

- **Prototype** (KCFI `0xf4c49135`): `void TEEC_FinalizeContext(struct TEEC_Context *)`
- **Call sites**: 2 — `tee_session_open` (error unwind) and `tee_session_close`
  (normal teardown).
- **Arguments**: `x0 = &ctx`. No return value is consumed (`void`).
- **Ordering**: always *after* `TEEC_ReleaseSharedMemory` and, on the normal
  path, after `TEEC_CloseSession`. Always *before* `kfree(wsm_buffer)`.

## 5. `TEEC_InvokeCommand` — `0x202b681e` (NATURAL)

- **Prototype** (KCFI `0x593c5866`):
  `TEEC_Result TEEC_InvokeCommand(struct TEEC_Session *, uint32_t commandID,
  struct TEEC_Operation *, uint32_t *returnOrigin)`
- **Call sites**: 1 — `secmem_execute`, under `g_sess_lock`.
- **Arguments**: `x0 = &session`, `w1 = cmd` (the `CMD_*` table in
  `phase4-tmem-ffa-teec-call-flow.md` §5), `x2 = &op` (stack, 280 B, zeroed,
  `paramTypes = 0xF`, `params[0].memref = {&wsm, size, offset 0}`),
  `x3 = NULL`.
- **Return handling**: any non-zero result is logged
  (`"TEEC_InvokeCommand failed! cmd:%d, ret:0x%x"`), the session lock is
  dropped and the **TEEC result is returned verbatim** to the trusted-memory
  core — TEEC error codes propagate outward unchanged.
- **Post-conditions**: on success the INOUT message is copied back
  (`sec_handle`, `refcount`, `alignment`, `size`).

## 6. `TEEC_CloseSession` — `0xcb193c37` (NATURAL)

- **Prototype** (KCFI `0x31bed4ef`): `void TEEC_CloseSession(struct TEEC_Session *)`
- **Call sites**: 1 — `tee_session_close`; first step of teardown.

## 7. `TEEC_ReleaseSharedMemory` — `0xc4d15e1c` (NATURAL)

- **Prototype** (KCFI `0x0dc79758`): `void TEEC_ReleaseSharedMemory(struct TEEC_SharedMemory *)`
- **Call sites**: 2 — `tee_session_open` error unwind and `tee_session_close`.
- **Arguments**: `x0 = &wsm` (`ctx + 0x110`, visible as `add x0, x8, #0x110`).

---

## 8. Consumer-side invariants this report establishes

1. One global context, one global session, one registered 64-byte window,
   serialised by one mutex — no per-operation session churn.
2. The client never allocates through the TEE API and never cancels.
3. Error propagation is transparent: TEEC results are returned as-is.
4. Cleanup is strictly reverse-ordered and is identical on both paths.
5. A `NULL` TEE name and a `NULL` `returnOrigin` are both accepted by this
   TrustKernel build.
