# GQ5012BF1 tkcore island Phase 3P — core-unblock check

Question: are the exact edges that blocked Phase 3A now implemented in the island, statically and without placeholders?

Evidence base: Phase-3P `tkcore.ko` `a5c1a06c68de6791c3ab5d73ec67c51ba297f1ff6f0f69edbe77eee87a097b2d`, built against exact GKI `ab/12901745`, `BUILD_RC=0`, 0 warnings, 0 unresolved symbols, `depends=` empty.

## Result

**PHASE3A_CORE_DEPENDENCIES_READY**

## Blocker-by-blocker

| Phase-3A blocker edge | Required prototype | Implemented | KCFI | Acceptance | Status |
|---|---|---|---|---|---|
| `tee_core_add → tee_init_procfs` | `int (struct tee *)` | yes | `0xa1200a70` exact | CFG_EQUIVALENT | **READY** |
| `tee_core_add → tee_init_sysfs` | `int (struct tee *)` | yes | `0xa1200a70` exact | EXACT_BYTE | **READY** |
| `tee_core_add → tee_peridev_init` | `int (void)` | yes | `0x36b1c5a6` exact | CFG_EQUIVALENT | **READY** |
| `tee_core_add unwind → tee_exit_procfs` | `void (void)` | yes | `0xa540670c` exact | CFG_EQUIVALENT | **READY** |
| `tee_core_del → tee_peridev_exit` | `void (void)` | yes | `0xa540670c` exact | EXACT_BYTE | **READY** |
| `tee_core_del → tee_cleanup_sysfs` | `void (struct tee *)` | yes | `0x246c186b` exact | EXACT_BYTE | **READY** |
| `tee_core_alloc → tee_supp_init` | `int (struct tee *)` | yes | `0xa1200a70` exact | EXACT_BYTE | **LIFECYCLE-SUFFICIENT** |
| `tee_core_free / tee_core_del → tee_supp_deinit` | `void (struct tee *)` | yes | `0x246c186b` exact | EXACT_BYTE | **LIFECYCLE-SUFFICIENT** |

Transitively required and also closed: `plat_register_spi_clk` (SIZE_EXACT_SEMANTIC_EXACT), `tee_clkmgr_register` (CFG_EQUIVALENT, exported), `mtk_enable_clk`/`mtk_disable_clk` (both EXACT_BYTE), and the full `tkcore_log` callback set.

## Why this is not a placeholder closure

- Every one of the eight edges resolves to a real function with the stock KCFI ID; four are byte-identical to stock.
- `tee_init_procfs` genuinely creates a proc directory and four files, arms a real waitqueue, requests a real IRQ when the provider supplies one, and starts a real `tee-log` kthread.
- `tee_peridev_init` genuinely scans the device tree and registers real `struct clk` handles with a real clock-manager list.
- `tee_peridev_exit` genuinely drains and frees those records under the same mutex.
- No function returns success without doing its work; no stub, no fake IRQ, no fake thread.

## Prototype corrections Phase 3A must adopt

1. `tee_init_sysfs` returns `int` (was `void` in Phase 2). `tee_core_add` must branch on it and call `tee_exit_procfs` before unwinding the misc records.
2. `tee_init_procfs` returns `int` and takes the `struct tee *`; it returns `-1` (not a negative errno) on every failure, matching stock.
3. `tee_exit_procfs`, `tee_peridev_init` and `tee_peridev_exit` take **no** arguments.
4. `tee_clkmgr_register`'s stock prototype is the untyped eight-argument form; the previous typed island declaration was wrong.

## `struct tee` fields Phase 3A can now rely on

`tee_core_alloc` must leave these zeroed unless the provider sets them, because `tee_init_procfs` reads them:

- `log_shm` `@0x70`, `log_shm_len` `@0x78`, `log_irq` `@0x80` — control whether logging, the IRQ and the thread are armed.
- `version_major/minor/patch` `@0x64/0x68/0x6c` — surfaced by `/proc/tkcore/tkcore_os_version`.
- `rpc` `@0xb0` — populated by `tee_supp_init`.
- `refcount` `@0xb8`, `max_refcount` `@0xbc`, `stats` `@0xc0` — corrected anchors, now build-enforced.

All are covered by the 41/41 layout assertions.

## Residual constraint for the Phase-3A rerun

`tee_init_procfs` requires a non-NULL `tee->priv` (stock `BUG_ON`), so `tee_core_alloc` must keep assigning `priv = tee + 1` before `tee_core_add` runs. This is already the case in the Phase-2 source and is unchanged.

## What is still NOT unblocked

Nothing in the core group. Out of scope and still missing by design: `tee_clkmgr_handle`, shared memory, `TEEC_InvokeCommand`, supplicant commands and the secure SPI transfer surface. Those do not appear on any `tee_core_alloc/add/del/free` or `__tee_get` edge.

## Status

- PHASE3A_CORE_DEPENDENCIES_READY
- TKCORE REPLACEMENT READY: **NO**
- STOCK TKCORE RUNTIME DEPENDENCY: **STILL PRESENT**
- Runtime validation: **not performed**
