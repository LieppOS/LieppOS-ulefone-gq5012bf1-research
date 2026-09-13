# tkcore ABI-evidence delta contributed by `tmem_ffa.ko`

Strategic deliverable. `tkcore` itself was **not** modified, rebuilt or
reclassified by this task; it remains
`NO_PUBLIC_SOURCE_FOUND / PROVIDER_ABI_PARTIAL / NOT RECONSTRUCTED / STOCK
RUNTIME PROVIDER`.

## 1. Which tkcore exports does `tmem_ffa` consume?

Seven, independently rediscovered from the stock ELF (not assumed):

`TEEC_InitializeContext`, `TEEC_RegisterSharedMemory`, `TEEC_OpenSession`,
`TEEC_FinalizeContext`, `TEEC_InvokeCommand`, `TEEC_CloseSession`,
`TEEC_ReleaseSharedMemory`.

Not consumed: `TEEC_AllocateSharedMemory`, and none of the
`tee_core_*`/`__tee_get`/`tee_supp_cmd`/`tee_wait_queue_*`/`tee_clkmgr_*`/
`tee_spi_*`/`tee_map_cached_shm` families.

## 2. Which are in tkcore's NATURAL 14/25 group?

3 — `TEEC_InvokeCommand` (`0x202b681e`), `TEEC_CloseSession` (`0xcb193c37`),
`TEEC_ReleaseSharedMemory` (`0xc4d15e1c`).

## 3. Which are in the PROVIDER_ABI_BLOCKED 11/25 group?

4 — `TEEC_InitializeContext` (`0x89b94f9a`), `TEEC_RegisterSharedMemory`
(`0xa7bb0a46`), `TEEC_OpenSession` (`0xe821e2a3`), `TEEC_FinalizeContext`
(`0x7b3bc43f`). All four are blocked for one reason: they take
`struct TEEC_Context *`, whose implementation-defined tail names
`struct tee_context`, whose *member spellings* genksyms hashes recursively.

## 4. What exact prototypes does `tmem_ffa` prove?

Argument count, order, widths, constness and return-consumption are now
confirmed by a second, independent consumer:

```c
TEEC_Result TEEC_InitializeContext(const char *name, struct TEEC_Context *ctx);      /* name may be NULL */
TEEC_Result TEEC_RegisterSharedMemory(struct TEEC_Context *, struct TEEC_SharedMemory *);
TEEC_Result TEEC_OpenSession(struct TEEC_Context *, struct TEEC_Session *,
                             const struct TEEC_UUID *, uint32_t connectionMethod,
                             const void *connectionData, struct TEEC_Operation *,
                             uint32_t *returnOrigin);                                /* last three NULL-able */
TEEC_Result TEEC_InvokeCommand(struct TEEC_Session *, uint32_t commandID,
                               struct TEEC_Operation *, uint32_t *returnOrigin);     /* returnOrigin NULL-able */
void        TEEC_CloseSession(struct TEEC_Session *);
void        TEEC_ReleaseSharedMemory(struct TEEC_SharedMemory *);
void        TEEC_FinalizeContext(struct TEEC_Context *);
```

## 5. What KCFI evidence is added?

`tmem_ffa` calls all seven **directly** (`R_AARCH64_CALL26`), so it adds no new
provider-side KCFI type ids beyond those already recorded in
`phase4-tkcore-exports.tsv`. It does add 16 *consumer-side* KCFI ids for the
peer-ops callbacks (`kernel/phase4-tmem-ffa-kcfi-prototypes.tsv`), all
reproduced exactly — which validates the indirect-call contract that any future
source-built TEE island must preserve.

## 6. What TEEC object sizes/offsets are newly confirmed?

| type | size | how `tmem_ffa` proves it |
|---|---:|---|
| `TEEC_Context` | `0x108` | `session` at `+0x108` of the session block |
| `TEEC_Session` | `8` | `wsm` at `+0x110` |
| `TEEC_SharedMemory` | `0x28` | `wsm_buffer` at `+0x138` |
| `TEEC_Operation` | `0x118` | stack object zeroed with `sizeof` |
| session block | `0x140` | `kmalloc_trace` size literal |

This is the first *independent* confirmation: the same numbers were previously
derived only from `tkcore`'s own code and `microarray_fp_tee`.

## 7. Lifetime / ownership semantics newly confirmed

- One context + one session + one registered window, module-lifetime, mutex
  serialised.
- Context and session memory are **caller-owned**; the provider only owns the
  opaque tail.
- Shared-memory *buffers* are caller-owned (`kmalloc`/`kfree`); only the
  *registration* is provider-owned.
- `TEEC_AllocateSharedMemory` is unnecessary for a working TEE client on this
  device.

## 8. Error / cleanup behaviour newly confirmed

- TEEC result codes are propagated verbatim to the caller (no remapping).
- Cleanup is strictly reverse-ordered:
  `CloseSession → ReleaseSharedMemory → FinalizeContext → kfree(buffer)`.
- On `OpenSession` failure the client releases the shared memory *before*
  finalizing the context; on `RegisterSharedMemory` failure it finalizes only.
- `returnOrigin` is never read, so a reconstructed provider may ignore it.

## 9. Which private member semantics become known?

- `TEEC_Context` = 256-byte name area + 8-byte implementation union
  (semantics known, spelling unknown).
- `TEEC_Session` = a single 8-byte opaque field (this consumer never reads it).
- `TEEC_SharedMemory` = `{buffer, size, flags, <8B id/reserved>, <8B
  registration>}`; the last 16 bytes are zeroed by the client and written by
  the provider.
- `TEEC_Operation` tail (after the 4-parameter array) is provider-private.

## 10. What remains impossible?

The historical **C spellings** of TrustKernel's private members
(`struct tee_context`, `struct tee`, and the `TEEC_Context` union arms). Those
are exactly what the 11 blocked CRCs hash. `tmem_ffa` cannot recover them —
and neither can any other stripped consumer. Only an original TrustKernel
header would.

## 11. Does this materially reduce uncertainty?

**Yes, but not for the historical CRCs.** It:

- doubles the independent confirmation of the TEEC type graph (sizes/offsets);
- proves the four-object lifetime model end-to-end;
- proves that a *self-consistent* TrustKernel header is sufficient to rebuild a
  real MediaTek TEE consumer **byte-for-byte** (141/141) — the strongest
  evidence yet that the planned ABI island is viable;
- confirms that 3 of the 7 edges a future source-built `tkcore` must serve are
  already naturally reproducible, and isolates the remaining 4 to one struct.

It does **not** unblock any of the 11 blocked CRCs, and it adds no evidence at
all about `struct tee`, `struct tee_ops`, `__tee_get` or `tee_supp_cmd`.

## 12. Which tkcore functions should be reconstructed first, given this evidence?

1. `TEEC_InvokeCommand`, `TEEC_CloseSession`, `TEEC_ReleaseSharedMemory` —
   already NATURAL, and now proven to be the entire hot path of a second
   consumer.
2. `TEEC_InitializeContext` / `TEEC_FinalizeContext` — the context lifecycle
   pair; both consumers use exactly the same two-call pattern, so the
   `TEEC_Context` tail semantics can be settled with only these two.
3. `TEEC_RegisterSharedMemory` — registration-only model is now proven; the
   allocate variant can be deferred.
4. `TEEC_OpenSession` — highest argument complexity, but three arguments are
   always NULL in both known consumers.
5. Only afterwards the `tee_core_*` / `__tee_get` / `tee_supp_cmd` family,
   for which `tmem_ffa` supplies no evidence.
