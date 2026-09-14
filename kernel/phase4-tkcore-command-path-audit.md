# GQ5012BF1 tkcore command-marshalling path — static audit

> **STATUS: the `_update_client_tee_cmd` finding below is CLOSED by Phase 3C-R.**
>
> Two corrections, recorded here so this report is not misread. They do not
> alter the audit's conclusion that the function was **present but not closed**,
> which was correct and is what triggered Phase 3C-R.
>
> 1. This report describes the residual as stock re-reading the parent
>    `TEEC_SharedMemory` record. That is **wrong in detail**. Stock re-reads
>    the entire 280-byte `TEEC_Operation` once, before the parameter loop; the
>    parent record legitimately stays cached. The authoritative description is
>    `phase4-tkcore-update-client-cmd-contract.md`.
> 2. The defect is **more severe** than "stale cached copy": the island was
>    dereferencing a `__user` operation pointer directly from kernel context.
>
> Closure evidence: `phase4-tkcore-island-phase3c-r-regression.md`.
> The historical text below is otherwise unmodified.

Scope: the five command-path functions named for the Phase-3C audit. All five were already **present** from earlier phases. This audit tests whether presence equals closure. It does not modify them.

Method: per-function stock-vs-island size, linkage, and complete `R_AARCH64_CALL26` call-edge set.

## Summary

| Function | Stock | Island | Linkage | Call edges | Verdict |
|---|---:|---:|---|---|---|
| `_release_tee_cmd` | 600 | 548 | LOCAL = LOCAL | **identical set** | CLOSED (static) |
| `tee_supp_cmd` | 340 | 336 | GLOBAL = GLOBAL | 7 shared, diagnostics only | CLOSED (static) |
| `_init_tee_cmd` | 808 | 804 | LOCAL = LOCAL | 7 shared, diagnostics only | CLOSED (static) |
| `TEEC_InvokeCommand` | 300 | 224 | GLOBAL = GLOBAL | 3 shared; stock also `memset`, `_printk` | CLOSED with caveat |
| `_update_client_tee_cmd` | 1652 | 1608 | LOCAL = LOCAL | **0 shared** | **NOT CLOSED** |

## Diagnostic-only divergence

`_printk` versus `_dev_err` appears in four of the five functions. This is a logging-macro choice (`pr_err` vs `dev_err`), not a behavioural difference in command marshalling, and it does not change any value crossing the ABI boundary. `memset` and `__stack_chk_fail` are compiler-emitted and track inlining and stack-protector placement.

These are recorded, not "fixed": changing them would alter log text without improving ABI fidelity.

## `_update_client_tee_cmd` — open finding

This is the one function where presence must not be read as closure.

```text
stock  call edges: __stack_chk_fail, _printk, memset, tee_context_copy_from_client
island call edges: _dev_err
shared: 0
```

The materially important entry is `tee_context_copy_from_client`. Stock re-reads the parent `TEEC_SharedMemory` record through the context copy helper while publishing results, whereas the island version consults the cached `cmd->param.c_shm[idx]` copy taken earlier in `_init_tee_cmd`.

Consequences, stated conservatively:

- For an unchanged parent record the two produce the same output.
- They can diverge if the parent record is modified between `_init_tee_cmd` and result publication, because stock observes the later value and the island observes the earlier one.
- The divergence is confined to the registered-memref output path (`TEEC_MEMREF_WHOLE`, `PARTIAL_OUTPUT`, `PARTIAL_INOUT`).

This function is **not** in the Phase-3C authorized target set. It was inherited from the Phase-3A-R / Phase-3B reconstruction. Correcting it would mean editing a function outside the authorized nine, so it is recorded here as an open item rather than silently rewritten.

```text
COMMAND_PATH_OPEN_ITEM=_update_client_tee_cmd
REASON=missing stock tee_context_copy_from_client re-read on the registered-memref output path
OWNING_PHASE=3B (TEEC shared memory)
AUTHORIZED_IN_PHASE_3C=NO
```

## `TEEC_InvokeCommand`

Island is 224 bytes against stock's 300, and stock carries `memset` and `_printk` edges the island does not. The three shared edges are the substantive ones. The smaller body is consistent with the island zeroing its local `struct tee_cmd` via a struct initialiser that Clang expands inline instead of calling `memset`, and with one fewer diagnostic. No missing semantic call edge was found.

## What this audit does not establish

Static call-edge equality is a necessary, not sufficient, condition. None of these functions has been executed. No secure-world interaction, supplicant request, or consumer rebuild was performed.
