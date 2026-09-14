# GQ5012BF1 Phase 3C-R — static tmem_ffa output-update trace

```text
RESULT: PASS_STATIC_OUTPUT_UPDATE
```

Static only. `tmem_ffa.ko` was read from the frozen stock oracle and **not modified**. No module was loaded and no command was issued.

## Consumer surface

`tmem_ffa` imports exactly seven TrustKernel client APIs:

```text
TEEC_InitializeContext   TEEC_FinalizeContext
TEEC_OpenSession         TEEC_CloseSession
TEEC_RegisterSharedMemory  TEEC_ReleaseSharedMemory
TEEC_InvokeCommand
```

`TEEC_AllocateSharedMemory` is **not** imported: tmem_ffa registers caller-owned memory rather than allocating provider-owned memory.

## The path is the affected one

There is exactly one `TEEC_InvokeCommand` call site. The `paramTypes` immediate reaching it is:

```text
0x000f  ->  param0 = 0xf = TEEC_MEMREF_PARTIAL_INOUT
            param1..3 = 0 = TEEC_NONE
```

`TEEC_MEMREF_PARTIAL_INOUT` is one of the three types (`WHOLE`, `PARTIAL_OUTPUT`, `PARTIAL_INOUT`) that stock dispatches to the registered-memref output path. tmem_ffa therefore exercises precisely the branch this task corrected — this is not a bystander consumer.

## Client class is decisive

```text
TEEC_InitializeContext:  823c: str wzr, [x0, #0x8c]     ->  ctx->usr_client = 0
tee_ctx_open:            1194: str w8,  [x0, #0x8c]     ->  ctx->usr_client = 1
tee_supp_open:           125c: str w8,  [x19, #0x8c]    ->  ctx->usr_client = 1
```

tmem_ffa reaches tkcore through `TEEC_InitializeContext`, so it is a **kernel client** (`usr_client == 0`).

`tee_context_copy_from_client` branches on exactly that field:

| Client | Branch |
|---|---|
| `usr_client != 0` | `__check_object_size` + `__arch_copy_from_user` |
| `usr_client == 0` | `memcpy` |

## Consequence for tmem_ffa

For a kernel client the refreshed operation copy is a `memcpy` from the same kernel `TEEC_Operation` the previous island code dereferenced directly. The values observed by the registered-memref output path are therefore **identical before and after this change**.

```text
tmem_ffa behavioural delta: NONE
tmem_ffa regression risk:   NONE
```

The correction matters for the **user-client** path, where `cmd_io->op` is a `__user` pointer and the previous direct dereference was an unchecked kernel-context read of a user address. tmem_ffa was never exposed to that defect; the ioctl consumers were.

## Lifecycle compatibility

| Stage | Interaction with the corrected code | Status |
|---|---|---|
| `TEEC_InitializeContext` | sets `usr_client = 0`; selects the `memcpy` branch | unaffected |
| `TEEC_RegisterSharedMemory` | populates the caller's `TEEC_SharedMemory`; cached into `cmd->param.c_shm[idx]` by `_init_tee_cmd` | unaffected — the parent record is still read from the cache, not re-read |
| `TEEC_OpenSession` | no output publication through this function | unaffected |
| `TEEC_InvokeCommand` | `PARTIAL_INOUT` reaches the corrected output path; `offset`/`size` now come from the refreshed local | values identical for a kernel client |
| `TEEC_CloseSession` | release path untouched | unaffected |
| `TEEC_ReleaseSharedMemory` | ownership untouched; this function never puts or frees | unaffected |

## Ownership and lifetime

The corrected function still performs **no** `tkcore_shm_put`, `tkcore_shm_free`, list insertion, or dma-buf operation — its call set contains none of them. Provider-owned allocation lifetime and foreign-memory reference lifetime remain separated exactly as Phase 3B established. No double put, double free, stale pointer use, or transient memref list insertion is introduced.

## Scope honoured

`tmem_ffa.ko` was read only. This trace is static reasoning over the frozen oracle and the rebuilt tkcore ELF; it is **not** a runtime acceptance result, and the three-consumer acceptance remains deferred.
