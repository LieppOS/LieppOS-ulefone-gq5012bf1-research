# GQ5012BF1 tkcore — shared memory vs context teardown

Phase 3A-R closed `TEEC_FinalizeContext`. Phase 3B must answer: what happens if registered or allocated shared memory still exists when the context is destroyed?

## The question, answered from stock

**Stock context teardown never walks `ctx->list_shm`.**

`tee_context_put` (stock `0x...`, call set `tee_dec_stats`, `__list_del_entry_valid`, `devm_kfree`, `tee_put`, `refcount_warn_saturate`) contains **no reference at all** to `ctx + 0xb0` or `ctx + 0xb8`, i.e. to the `list_shm` head or its tail pointer. The final release routine decrements context statistics, unlinks `ctx->entry` from `tee->list_ctx`, frees the context, and drops the provider reference. It does not free, unmap, or even inspect shared memory.

This was verified by scanning every instruction of the teardown chain for those displacements; the result is `NONE`.

## Why that is not a leak

Because the shm holds the context alive, not the other way round.

`tee_shm_alloc_io` takes a context reference for every context-owned shm:

```text
tee_shm_alloc_io:  ... tee_get(tee) ; tee_context_get(ctx) ; list_add_tail(&shm->entry, &ctx->list_shm)
tee_shm_free_io :  ... list_del(&shm->entry) ; tkcore_shm_free(shm) ; tee_put(tee) ; tee_context_put(ctx)
```

So while any context-owned shm is outstanding, `ctx->refcount` is at least 1 above the value that would trigger `_tee_context_do_release`. `TEEC_FinalizeContext` → `tee_context_destroy` → `tee_context_put` therefore **cannot** reach the final release path; it merely drops the caller's reference. The context object survives until the last shm is released, at which point that shm's `tee_context_put` performs the real teardown.

The ordering invariant is:

```text
last TEEC_ReleaseSharedMemory (or dma_buf .release)
        -> tee_shm_free_io
              -> list_del from ctx->list_shm
              -> tee_context_put   <-- this is the call that can free the context
```

## Consequences per ownership class

| Class | Outstanding at context teardown? | Who releases it | Context freed when |
|---|---|---|---|
| A. context-owned (`tee_shm_alloc_io`) | possible | `TEEC_ReleaseSharedMemory` / `tee_shm_free_io` | last shm's `tee_context_put` |
| C. exported dma-buf (usr_client) | possible — userspace still holds the fd | `__tee_shm_dma_buf_release` → `tee_shm_free_io` | when the fd is closed |
| D. imported memref (`tkcore_shm_get`) | **not listed**, so invisible here | `tkcore_shm_put` from `_release_tee_cmd` | n/a — never took a context kref |

Class D is the important asymmetry: a memref shm is *not* inserted into `ctx->list_shm` and takes no context reference, because its lifetime is bounded by the single command that created it. Treating it like class A — for example by "helpfully" adding it to the context list — would introduce a reference that stock does not take and would change teardown semantics.

## Was any Phase-3A-R decision invalidated?

No. The already-accepted context lifecycle is unchanged by Phase 3B:

- `TEEC_FinalizeContext` still frees the IDR handle before calling `tee_context_destroy`.
- `tee_context_destroy` still takes `tee->lock` and drops one kref.
- `_tee_context_do_release` still performs statistics, list removal, free, and `tee_put`.

Phase 3B adds no code to any of them and requires no correction to them. The only Phase-3B change in `tee_context.c` was converting two diagnostics in `tee_context_alloc_shm_tmp` from `dev_err` to `pr_err` so its call multiset matches stock; that function is a shared-memory helper, not part of the context lifecycle.

## Deliberate non-divergence

A reflexive "safety improvement" here would be to drain `ctx->list_shm` during finalisation. That would be **wrong**: it would free memory the dma-buf layer or an outstanding command still owns, and it would double-free once the real owner released it. Stock's refcount-based design already makes teardown-with-outstanding-shm safe, so the island reproduces it unchanged.
