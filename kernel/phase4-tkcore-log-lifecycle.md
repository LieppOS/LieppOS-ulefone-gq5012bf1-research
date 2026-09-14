# GQ5012BF1 tkcore logging state lifecycle

Recovered statically from stock `tkcore.ko` (`03837d13…ed226`). No device was accessed.

## Objects

### Module-global log state — `klog`, `.bss+0x38`, ELF size 64

| Offset (in `klog`) | .bss | Field | Evidence |
|---:|---:|---|---|
| `0x00` | `0x38` | `struct tkcore_log_header *header` | `stp x8,x9,[x24]` in `tee_init_procfs`; `tee_log_open` null-checks it |
| `0x08` | `0x40` | `char *data` (`header + 0x100`) | same `stp`, second register is `x8 + 0x100` |
| `0x10` | `0x48` | `u32 size` | `str w1,[x24,#0x10]` where `w1 = header->size` |
| `0x14` | `0x4c` | `u8 wrapped` | `strb wzr,[x24,#0x14]`; set by `logd` |
| `0x18` | `0x50` | `wait_queue_head_t wq` | `__init_waitqueue_head(x24+0x18, "&klog->wq", …)`; the IRQ handler and `tee_exit_procfs` use `.bss+0x50` |
| `0x30` | `0x68` | `struct task_struct *task` | `str x19,[.bss+0x68]`; `tee_exit_procfs` loads `[x19,#0x18]` with `x19 = .bss+0x50` |

`klog_irq` is a separate `int` at `.bss+0x70`, written only after a successful `request_threaded_irq`.

### Shared secure-world header — first `0x100` bytes of `tee->log_shm`

| Offset | Field | Evidence |
|---:|---|---|
| `0x00` | magic/identifier (not validated by tkcore) | untouched |
| `0x04` | `u32 size` — payload length | compared against `log_shm_len - 0x100` |
| `0x18` | `u32 readers` | zeroed at init; `logd` increments on entry and decrements on exit |
| `0x1c` | `u32 write_pos` — producer cursor | read by readers and `logd` |
| `0x20` | `u32 logd_pos` — kernel-log drain cursor | advanced only by `logd` |

The payload ring starts at `header + 0x100` and is `header->size` bytes. Cursors are free-running 32-bit counters; the ring index is `pos % size`, and distance is `write_pos - pos` in modular arithmetic.

### Per-open reader — 24 bytes, `kmalloc(GFP_KERNEL)` in `tee_log_open`

| Offset | Field | Evidence |
|---:|---|---|
| `0x00` | `u32 pos` — this reader's cursor | `ldr w9,[x26]` in `tee_log_read` |
| `0x08` | `const char *pending` — pending literal to emit | `stp x8,x9,[x0,#8]` stores `.rodata+0x4e0` |
| `0x10` | `struct tkcore_log_state *log` | second half of the same `stp`, `= &klog` |

## Buffer ownership

tkcore never allocates the log ring. It is provider-supplied secure/shared memory described by `tee->log_shm` and `tee->log_shm_len`, and tkcore only maps cursors onto it. Consequently `tee_exit_procfs` frees no buffer — it only stops the consumers.

## Open

`tee_log_open` allocates the 24-byte reader, fails `-ENOMEM` if that fails, fails `-EIO` if `klog.header` is NULL (i.e. logging was never armed), presets `pending = "------ beginning of tee\n"` (`.rodata+0x4e0`) and `log = &klog`, calls `nonseekable_open`, and on error frees the reader and prints `open file failed with %d`. On success the reader becomes `file->private_data`.

## Read

`tee_log_read` rejects a missing reader with `file not open correctly` and `-EINVAL`, and returns `-EAGAIN` (`-0xb`) immediately for `O_NONBLOCK`.

Blocking wait: while nothing is pending and `reader->pos == header->write_pos`, it waits interruptibly on `klog.wq` with a 125-jiffy timeout; a signal returns `-EINTR` (`-4`).

Copy loop, per iteration:
1. If a literal is pending, copy as much of it as fits; a zero-byte copy prints `failed to copy flag to user` and stops.
2. When the literal is exhausted, the reader's cursor is (re)based: `0` if the producer has not yet wrapped (`write_pos < size` and `!wrapped`), otherwise `write_pos - size`.
3. Otherwise copy from the ring, clamped by both the remaining user space and the distance to the end of the ring; a zero-byte copy prints `failed to copy klog to user` and stops.
4. If the reader has fallen more than one ring behind (`write_pos - pos > size`), the literal `"------ interrupted\n"` (`.rodata+0x680`) is queued and the cursor is re-based on the next pass.

`*ppos` is advanced by the total number of bytes delivered, which is the return value.

## IRQ

`tkcore_log_irq_handler` performs a single `__wake_up(&klog.wq, TASK_NORMAL, 0, NULL)` and returns `IRQ_HANDLED`. It is registered only when the provider supplied a non-zero `tee->log_irq`.

## Thread `tee-log` (`logd`)

- Increments `header->readers` on entry, decrements on exit.
- Loops until `kthread_should_stop()`.
- When `logd_pos == write_pos`, waits on `klog.wq` with a 125-jiffy timeout. The stop condition is deliberately **not** part of the wait predicate; the timeout plus the explicit `wake_up` in `tee_exit_procfs` guarantee liveness. This matches stock, which calls `kthread_should_stop` exactly twice per loop and never inside the wait.
- Extracts one line at a time, terminating on NUL, `\n`, buffer limit or ring exhaustion, then emits it with `pr_info("tkcore: %s\n", line)`.
- If the producer has lapped the drain cursor (`write_pos - pos > size`), it emits `"---- interrupted"` through the same format and re-bases to `write_pos - size`.
- Publishes progress by storing the new cursor into `header->logd_pos`, and sets `klog.wrapped` once `write_pos` has reached the ring size.

Note the two distinct interruption strings: `logd` uses `"---- interrupted"` (`.rodata.str1.1+0xbf1`) as a `printk` argument, while the reader path uses the different literal `"------ interrupted\n"` (`.rodata+0x680`).

## Shutdown and unwind order

`tee_exit_procfs`:
1. `proc_remove(tee_proc_dir)` and null the five proc pointers.
2. If `klog_irq >= 1`, `free_irq(klog_irq, NULL)` and clear it.
3. `kthread_stop(klog.task)`, then clear `klog.task`.
4. `wake_up(&klog.wq)` to release any reader still blocked.

`tee_init_procfs` failure unwind mirrors this: IRQ freed if taken, `klog` zeroed, proc surface removed, `-1` returned.

### Documented divergence (crash safety)

Stock tests the `kthread_create_on_node` result with `cmn x0, #0x1, lsl #12` / `b.hi`, which **skips** `wake_up_process` for an `ERR_PTR`, then stores that `ERR_PTR` into `klog.task` and — because it is non-zero — returns success. Since `kthread_create_on_node` reports failure exclusively as an `ERR_PTR`, stock's `Failed to create kthread.` branch is only reachable for a NULL that cannot occur, and a real failure would later hand an `ERR_PTR` to `kthread_stop()`.

The island treats both NULL and `ERR_PTR` as failure and takes stock's own (otherwise dead) unwind path: message, IRQ release, `klog` zeroed, proc surface removed, `-1`. This is the only difference in `tee_init_procfs` observable behaviour and is deliberate.
