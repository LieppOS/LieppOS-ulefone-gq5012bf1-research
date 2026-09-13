# TrustKernel ABI-island header plan (ANALYSIS ONLY)

**Status: proposal. No existing header is replaced by this document, and no
frozen module is modified.**

Goal: one internally consistent TrustKernel type graph that
`tkcore`, `tkcore_drv`, `tmem_ffa` and `microarray_fp_tee` can all be
source-built against, for a future zero-stock-`.ko` TEE island.

## 1. Why this is now credible

`tmem_ffa` was rebuilt **141/141 byte-identical** against the project's
existing reconstructed TrustKernel header
(`lieppos/tkcore-recon/include/tk_tee_client_api.h`) plus a declarations-only
prototype block. A real MediaTek TEE consumer therefore already compiles to
stock-identical machine code on top of the reconstructed type graph.

## 2. Proposed layout

```
lieppos/trustkernel-abi/include/
    tk_tee_client_api.h      GlobalPlatform client types + prototypes
    tk_tee_core.h            struct tee, struct tee_context, struct tee_ops
    tk_tee_wait_queue.h      tee_wait_queue_private (already reconstructed)
    tk_tee_spi.h             tee_spi_transfer / tee_spi_cfg_padsel surface
```

Consumers:

| module | headers needed |
|---|---|
| `tmem_ffa` | `tk_tee_client_api.h` only |
| `microarray_fp_tee` | `tk_tee_client_api.h`, `tk_tee_spi.h` |
| `tkcore_drv` | `tk_tee_core.h`, `tk_tee_wait_queue.h` |
| `tkcore` | all four |

## 3. Classification of every definition

### `PROVEN_EXACT` (size, layout and semantics all proven; safe to freeze)

| definition | proof |
|---|---|
| `TEEC_Context` total size `0x108` | `tmem_ffa` offsets + `tkcore` code |
| `TEEC_Session` total size `8` | `tmem_ffa` offsets |
| `TEEC_SharedMemory` total size `0x28`, `{buffer@0, size@8, flags@0x10}` | `tmem_ffa` writes |
| `TEEC_Operation` total size `0x118`, `{started@0, paramTypes@4, params[4]@8}` | `tmem_ffa` `secmem_execute` |
| `TEEC_UUID` 16-byte RFC4122 layout | both consumers |
| `TEEC_PARAM_TYPES`, `TEEC_MEMREF_*`, `TEEC_MEM_*`, `TEEC_LOGIN_*`, `TEEC_SUCCESS` | literal constants in stock code |
| all seven TEEC prototypes | call-site ABI, twice |
| `tee_wait_queue_private` = `mutex@0x00 + list_head@0x30` | `tkcore` provider ABI report |
| `tee_spi_transfer` / `tee_spi_cfg_padsel` / `tee_spi_transfer_disable` prototypes | natural CRC + KCFI match |

### `PROVEN_SEMANTICS_OFFSETS_ONLY` (layout known, names not)

| definition | known | unknown |
|---|---|---|
| `TEEC_Context` interior | 256-byte device-name array + 8-byte union (`struct tee_context *` / `int`) | member spellings |
| `TEEC_SharedMemory` tail | 8-byte id/reserved + 8-byte registration word, client-zeroed | spellings |
| `TEEC_Operation` tail | session pointer + per-parameter shadow array + flags word | spellings |
| `struct tee` (312 B) | klist_node@0, `char name[64]`@0x20, `int id`@0x60, `priv`@0x88, `ops`@0x90, `dev`@0x98, misc list@0xa0, ctx list@0xd8, shm list@0xe8, `mutex`@0xf8, state@0x128, shm flags@0x12c | all member spellings |
| `struct tee_context` (208 B) | `tee*`@0, `char name[128]`@8, tgid@0x88, usr_client@0x8c, entry@0x90, sess list@0xa0, shm list@0xb0, kref@0xc0, extra ptr@0xc8 | all member spellings |

### `PLACEHOLDER_NAME` (must be chosen, cannot be recovered)

Every member name inside the four private structs above. The plan is to pick
descriptive names **once**, in this header set, and use them consistently
across all four modules. Any such choice yields *different* CRCs from the
historical Ulefone ones for the 11 blocked exports — accepted deliberately.

### `UNKNOWN`

- `struct tee_ops` member set and order (no consumer dereferences it).
- Secure-world command semantics behind `TEEC_InvokeCommand`.
- Any TrustKernel-private allocation policy.

## 4. Design rule

> Prefer correct semantics and one internally consistent source ABI over
> inventing historical private member names.

Consequences, stated plainly:

1. A future source-built island will reproduce **14/25** tkcore export CRCs
   naturally and will *not* reproduce the other 11.
2. Therefore the island must be built **as a set**: `tkcore` +
   `tkcore_drv` + `tmem_ffa` + `microarray_fp_tee` all linked against the same
   header graph, so their `__versions` agree internally.
3. Mixed deployment (source `tkcore` + stock consumers, or vice versa) stays
   impossible for those 11 edges; that is an ABI fact, not a defect.
4. Until the whole island is built and validated, all four modules keep their
   current statuses and the stock providers stay in place.

## 5. Sequencing proposal (not started here)

1. Extract the header set from the existing reconstructions (no new RE).
2. Rebuild `tmem_ffa` and `microarray_fp_tee` against it — both are expected to
   stay byte-identical (tmem_ffa already is).
3. Only then attempt `tkcore` itself, with `tkcore_drv` as the second consumer.
4. Validate the island by internal `__versions` consistency, never by CRC
   patching.
