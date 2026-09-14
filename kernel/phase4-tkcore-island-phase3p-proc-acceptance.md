# GQ5012BF1 tkcore island Phase 3P — proc/log acceptance

Comparison base: stock `tkcore.ko` `03837d13…ed226` versus Phase-3P `tkcore.ko` `a5c1a06c68de6791c3ab5d73ec67c51ba297f1ff6f0f69edbe77eee87a097b2d`.

Classification rules used:
- `EXACT_BYTE` — identical `.text` bytes over the whole function.
- `SIZE_EXACT_SEMANTIC_EXACT` — identical size and identical relocation call multiset.
- `CFG_EQUIVALENT` — same decision structure and observable effects; instruction scheduling or call-site duplication differs.
- `INCOMPLETE` — behaviour missing, stubbed or unknown.

## Proc/log closure

| Function | Stock size | Phase-3P size | Stock KCFI | Phase-3P KCFI | Call multiset | Class |
|---|---:|---:|---|---|---|---|
| `tee_init_procfs` | 760 | 772 | `0xa1200a70` | `0xa1200a70` | exact (11 `_printk`) | CFG_EQUIVALENT |
| `tee_exit_procfs` | 140 | 152 | `0xa540670c` | `0xa540670c` | exact | CFG_EQUIVALENT |
| `tee_log_open` | 180 | 180 | `0x8f07ca55` | `0x8f07ca55` | exact | SIZE_EXACT_SEMANTIC_EXACT |
| `tee_log_read` | 1280 | 1244 | `0xe866e2f4` | `0xe866e2f4` | `_printk` 4→2, `finish_wait` 2→1 | CFG_EQUIVALENT |
| `tee_log_release` | 36 | 36 | `0x8f07ca55` | `0x8f07ca55` | exact | **EXACT_BYTE** |
| `drv_version_read` | 64 | 64 | `0xe866e2f4` | `0xe866e2f4` | exact | **EXACT_BYTE** |
| `copy_to_user_str` | 444 | 424 | direct-call only | direct-call only | exact | CFG_EQUIVALENT |
| `tee_version_read` | 176 | 176 | `0xe866e2f4` | `0xe866e2f4` | exact | SIZE_EXACT_SEMANTIC_EXACT |
| `teed_version_read` | 64 | 64 | `0xe866e2f4` | `0xe866e2f4` | exact | SIZE_EXACT_SEMANTIC_EXACT |
| `teed_version_write` | 404 | 420 | `0x9a660ea0` | `0x9a660ea0` | `memset` 1→2 | CFG_EQUIVALENT |
| `logd` | 808 | 648 | `0x89fb613d` | `0x89fb613d` | `_printk` 2→1, `kthread_should_stop` 2→2 | CFG_EQUIVALENT |
| `tkcore_log_irq_handler` | 52 | 52 | `0xf90f05f6` | `0xf90f05f6` | exact | SIZE_EXACT_SEMANTIC_EXACT |

**No `INCOMPLETE`.** `tee_init_procfs` and `tee_exit_procfs` are both CFG_EQUIVALENT with exact call multisets.

## Callback closure

Every callback reachable from the created proc surface is implemented and classified above:

- `tkcore_log`: `tee_log_open`, `tee_log_read`, `tee_log_release`
- `tkcore_drv_version`: `drv_version_read`
- `tkcore_os_version`: `tee_version_read`
- `tkcore_teed_version`: `teed_version_read`, `teed_version_write`
- IRQ: `tkcore_log_irq_handler`
- Thread: `logd`
- Shared read helper: `copy_to_user_str`

All four `proc_ops` objects and their slot assignments are reproduced (`proc_open@0x08`, `proc_read@0x10`, `proc_write@0x20`, `proc_release@0x30`).

## Residual differences, itemised

1. **`tee_log_read` `_printk` 4→2.** Stock duplicates the two diagnostic messages across four call sites, one of which is behind an unreachable fortify `brk`. The island emits each message once. Same messages, same conditions.
2. **`tee_log_read` `finish_wait` 2→1.** Stock's open-coded wait has a second `finish_wait` for the early-exit path; the `wait_event_interruptible_timeout` macro funnels both exits through one. Same wait predicate, same 125-jiffy timeout, same `-EINTR`.
3. **`teed_version_write` `memset` 1→2.** Compiler-emitted zeroing in addition to the partial-copy `memset`. Same observable writes.
4. **`logd` `_printk` 2→1.** Stock has separate call sites for a drained line and for the interruption notice; both use the same `"tkcore: %s\n"` format, so the island reaches them through one site with two possible arguments. Identical output text.
5. **`logd` size 808→648.** Stock unrolls the line extraction with a second interruption check inside the inner loop. The island re-checks the same condition at the top of each line iteration, which additionally re-evaluates `kthread_should_stop()` once per line — strictly more responsive to shutdown, with identical log output.
6. **Sizes of `tee_init_procfs`/`tee_exit_procfs` (+12 each).** Extra register moves from the shared unwind label; both call multisets are exact.

## Deliberate divergences (safety, recorded not replicated)

| Site | Stock behaviour | Island behaviour | Reason |
|---|---|---|---|
| `tee_init_procfs` kthread failure | `ERR_PTR` stored in `klog.task` and **success** returned; the real error path is dead code | `IS_ERR_OR_NULL` → stock's own unwind, `-1` | stock would later hand an `ERR_PTR` to `kthread_stop()` |
| `teed_version_write` terminator | writes index `count + 1`; out of bounds at `count == 50`, guarded by a fortify trap | clamps to the last in-bounds index | out-of-bounds write must not be reproduced |

Both are documented in `phase4-tkcore-log-lifecycle.md` and `phase4-tkcore-proc-log-contract.md`.

## Forbidden techniques

None used: no success-returning stub, no fake thread, no fake IRQ success, no CRC injection, no ELF patching, no stock object inclusion. The IRQ and thread are real; when the provider supplies no shared buffer or no IRQ, stock's own skip logic is preserved rather than faked.
