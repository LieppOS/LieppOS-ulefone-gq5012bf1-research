# GQ5012BF1 `_update_client_tee_cmd` — recovered stock contract

Source: relocation-aware disassembly of stock `tkcore.ko`, `_update_client_tee_cmd` at `0x3d64`, size 1652, LOCAL, direct-call-only (no KCFI type word, no `R_AARCH64_ABS64` reference).

```c
static void _update_client_tee_cmd(struct tee_session *sess,
                                   struct tee_cmd_io *cmd_io,
                                   struct tee_cmd *cmd);
```

Returns `void`. No status is propagated to the caller under any failure.

## Correction to the Phase-3C audit hypothesis

The Phase-3C audit recorded the residual as "stock re-reads the parent `TEEC_SharedMemory` record". **That description is wrong in detail and is superseded by this contract.**

What stock actually re-reads is the **entire `TEEC_Operation`**, once, at function entry:

```text
3d9c: add  x0, sp, #0x8
3da0: mov  w1, wzr
3da4: mov  w2, #0x118            // 280 = sizeof(TEEC_Operation)
3dac: bl   memset                // zero the local operation
...
3dcc: add  x1, sp, #0x8          // dst = local operation
3dd0: ldr  x2, [x20, #0x20]      // src = cmd_io->op   (client pointer)
3dd4: mov  x0, x21               // ctx
3dd8: mov  w3, #0x118            // 280
3de8: bl   tee_context_copy_from_client
3dec: cbnz w0, 0x4364            // failure -> diagnostic, then return
```

The parent `TEEC_SharedMemory` record is **not** re-read. It continues to come from the cached `cmd->param.c_shm[idx]` captured during `_init_tee_cmd` (`x25 = cmd + 0x30` is `&cmd->param.c_shm[0].size`).

The real invariant is a **read/write split**:

| Role | Source |
|---|---|
| every client-supplied field read during output publication | the **local** re-read copy (`x4 = sp + 8`) |
| every output written back to the caller | the **client** object (`cmd_io->op`, `x20 + 0x20`) |
| trusted-side sizes and shm handles | kernel-side `cmd->param.params[idx]` (`x23 = cmd + 0xc8`) |
| parent shared-memory record | cached `cmd->param.c_shm[idx]` (`x25 = cmd + 0x30`) |

## Answers to the recovery questions

1. **Which parameter types cause a parent re-read?** None individually. The operation is re-read once, unconditionally, before the parameter loop.
2. **When is `tee_context_copy_from_client` called?** Exactly once, at `0x3de8`, after the four `BUG_ON` guards and after `err`/`origin` have already been published, and before any parameter is examined.
3. **Arguments?** `(ctx, &local_op, cmd_io->op, 0x118)` — `ctx` is `sess->ctx` loaded from `x22 + 0x10`.
4. **What is re-read?** The whole `TEEC_Operation`, 280 bytes, into a zeroed stack local.
5. **Fields consumed from the refreshed record?** `params[idx].tmpref.size`, `params[idx].tmpref.buffer`, `params[idx].memref.offset`, `params[idx].memref.size`.
6. **Fields written back to the caller?** `params[idx].value` (8 bytes), `params[idx].tmpref.size`, the tmpref buffer contents, and `params[idx].memref.size`.
7. **Authoritative size?** The trusted-side `cmd->param.params[idx].shm->size_req` is authoritative for what is published; the client-supplied size from the refreshed local is the bound it is checked against.
8. **Re-read failure?** `_printk("tkcore: Failed to copy op from client\n")` then immediate return. `err`/`origin` remain published; no parameter is processed.
9. **Error/origin propagation?** `cmd_io->origin = cmd->origin` and `cmd_io->err = cmd->err` are stored *before* the re-read and are therefore always published, even when the re-read fails.
10. **Temporary objects still owned here?** All of them. This function never releases anything.
11. **Any `tkcore_shm_put`/free here?** No. Neither appears in the call set. Release happens later in `_release_tee_cmd`.
12. **Per type** — decoded from the 16-entry jump table at `.rodata+0x288`:

| Type | Target | Behaviour |
|---|---|---|
| `TEEC_NONE` (0) | `+0x478` | skip |
| `TEEC_VALUE_INPUT` (1) | `+0x478` | skip |
| `TEEC_VALUE_OUTPUT` (2) | `+0x110` | copy `value` back |
| `TEEC_VALUE_INOUT` (3) | `+0x110` | copy `value` back |
| `TEEC_MEMREF_TEMP_INPUT` (5) | `+0x478` | skip |
| `TEEC_MEMREF_TEMP_OUTPUT` (6) | `+0x20` | publish updated size, copy buffer back |
| `TEEC_MEMREF_TEMP_INOUT` (7) | `+0x20` | publish updated size, copy buffer back |
| `TEEC_MEMREF_WHOLE` (12) | `+0x10` | registered-memref output path |
| `TEEC_MEMREF_PARTIAL_INPUT` (13) | `+0x478` | **skip** |
| `TEEC_MEMREF_PARTIAL_OUTPUT` (14) | `+0x10` | registered-memref output path |
| `TEEC_MEMREF_PARTIAL_INOUT` (15) | `+0x10` | registered-memref output path |
| 4, 8, 9, 10, 11 | `+0x474` | `"type is invalid (type %02x)"`, then continue |

13. **Re-read for every registered memref or only output-capable ones?** The re-read is not per-parameter at all. Within the loop only the output-capable registered memrefs (12, 14, 15) consume the refreshed offset/size; `PARTIAL_INPUT` (13) is skipped outright.
14. **Is `memset` semantic?** Partly. It zeroes the 280-byte local before the copy, so any field the client copy fails to populate reads as zero rather than as stack residue. It is retained as defensive behaviour, not chased for codegen similarity.

## Guard order

```text
BUG_ON(!cmd_io)          -> brk at 0x43a8
BUG_ON(!cmd_io->op)      -> brk at 0x43b4
BUG_ON(!cmd)             -> brk at 0x43bc
BUG_ON(!sess->ctx)       -> brk at 0x43c8
```

Then `if (cmd->param.type_original == 0) return;` (`ldr w8,[x19,#0x24]; cbz w8`).

## Why the island form is a defect, not a style difference

The island reads client-supplied fields by dereferencing `cmd_io->op` directly:

```c
if (size_new != cmd_io->op->params[idx].tmpref.size)      /* island, before */
offset = cmd_io->op->params[idx].memref.offset;
```

For a user client `cmd_io->op` is a `__user` pointer. Dereferencing it from kernel context is not a stale-data problem only — it is an unchecked raw access to a user address, performed without the uaccess machinery that stock routes through `tee_context_copy_from_client`. Stock never dereferences that pointer for reads; it uses it solely as a write destination.

This makes the residual materially more important than the Phase-3C audit implied.

## Secondary observation, not changed here

On an invalid type nibble stock prints `"type is invalid (type %02x)"` and **continues to the next parameter**. The island instead reaches `BUG_ON(!tee_session_is_supported_type(...))`, which panics. The nibble originates from `cmd->param.type_original`, which `_init_tee_cmd` already validates, so this is defence-in-depth rather than a reachable path. It is recorded here and deliberately **not** altered in this task, because changing a panic into a continue is a separate semantic decision outside the authorized residual.
