# GQ5012BF1 tkcore island Phase 3A-R — tmem_ffa static lifecycle trace

**Result: PASS_STATIC**

This is an offline relocation/disassembly trace of the frozen stock consumer. No module was loaded and no runtime or secure-world claim is made.

## Consumer oracle

- Module: `workspace/phase4-tkcore/oracle/tmem_ffa.ko`
- SHA-256: `707e26674abbe7f9c695bb949d74fd5de04972d4bbb991cddc3a2ea9ab45f01b`
- Size: `151456` bytes
- Disassembly capture: `workspace/phase4-tkcore-island/phase3a-r/tmem_ffa.objdump.txt`

## Proven call edges

| Consumer function | Offset | Direct tkcore relocation |
|---|---:|---|
| `tee_session_open` | `0x5a6c` | `TEEC_InitializeContext` |
| `tee_session_open` | `0x5ac8` | `TEEC_OpenSession` |
| `tee_session_close` | `0x5c28` | `TEEC_CloseSession` |
| `tee_session_close` | `0x5c3c` | `TEEC_FinalizeContext` |

Thus the requested static lifecycle is present in order:

```text
TEEC_InitializeContext
  → TEEC_OpenSession
  → TEEC_CloseSession
  → TEEC_FinalizeContext
```

## Argument and layout trace

`tmem_ffa` allocates and zeroes a `0x140`-byte state object.

- `TEEC_Context` begins at state `+0x000`.
- `TEEC_Session` begins at state `+0x108`, exactly after the proven `0x108` context.
- Its shared-memory record begins at `+0x110`; that separate subsystem is outside this acceptance.

The open call sequence proves:

1. `TEEC_InitializeContext(NULL, state + 0x000)`. The NULL-name path therefore requires the stock default `"tkcore_client"`, which the Phase-3A-R implementation now uses.
2. `TEEC_OpenSession(state + 0x000, state + 0x108, &uuid, 0, NULL, NULL, NULL)`.
   - `connectionMethod = 0`;
   - `connectionData = NULL`;
   - `operation = NULL`, exercising the accepted dummy-operation path;
   - `returnOrigin = NULL`, which both stock and island permit.
3. On final close, `TEEC_CloseSession(state + 0x108)` executes before `TEEC_FinalizeContext(state + 0x000)`.

The four target KCFI ids exactly match stock:

| API | KCFI |
|---|---|
| `TEEC_InitializeContext` | `0x124b473b` |
| `TEEC_OpenSession` | `0xde69c0a6` |
| `TEEC_CloseSession` | `0x31bed4ef` |
| `TEEC_FinalizeContext` | `0xf4c49135` |

All four symbols are present in both stock and Phase-3A-R exports. Export CRCs are not claimed natural yet; the island still has different private type names, which is one reason this is static acceptance rather than runtime readiness.

## Scope boundary

The real `tmem_ffa` sequence also calls `TEEC_RegisterSharedMemory` between context initialization and session open, and `TEEC_ReleaseSharedMemory` between session close and context finalization. Those calls are explicitly outside Phase 3A-R. Their presence does not invalidate the requested four-API lifecycle trace, but it prevents treating this result as full tmem runtime acceptance.

`secmem_execute` also calls `TEEC_InvokeCommand`; that path remains excluded.

## Verdict

The frozen consumer's context/session object placement, argument convention, direct call order, default-name requirement, and KCFI signatures are compatible with the closed Phase-3A-R lifecycle APIs.

**PASS_STATIC** — context/session lifecycle only. `tmem_ffa` as a complete runtime consumer remains unaccepted until shared-memory and command paths are reconstructed.
