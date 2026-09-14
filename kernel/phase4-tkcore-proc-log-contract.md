# GQ5012BF1 tkcore proc/log contract

All offsets are `.text`/`.rodata`/`.data`/`.bss` offsets in stock `tkcore.ko` SHA256 `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226`. No runtime access was used.

## Correction to historical notes

Earlier research listed the runtime surfaces as `/proc/tkcore_log`, `/proc/teed_version`, `/proc/drv_version`, `/proc/os_version`. That is **wrong**. Stock creates a `tkcore` **directory** and four files inside it, and the file basenames themselves carry the `tkcore_` prefix:

```
/proc/tkcore/
    tkcore_log
    tkcore_drv_version
    tkcore_os_version
    tkcore_teed_version
```

Proven by `proc_mkdir("tkcore", NULL)` at `0x7c98` plus four `proc_create_data` calls whose name arguments are `.rodata.str1.1+0x959` = `tkcore_log`, `+0x908` = `tkcore_drv_version`, `+0x73d` = `tkcore_os_version`, `+0x1178` = `tkcore_teed_version`, each with the directory as parent.

## Proc entries

| Entry | Mode | ops | read | write | open | release | owner/lifetime | created | removed |
|---|---|---|---|---|---|---|---|---|---|
| `tkcore` (dir) | proc_mkdir default | – | – | – | – | – | module global `tee_proc_dir` | `tee_init_procfs` | `tee_exit_procfs` |
| `tkcore_log` | `0444` (`0x124`) | `.rodata+0x500` | `tee_log_read` | – | `tee_log_open` | `tee_log_release` | per-open reader object | `tee_init_procfs` | recursive with directory |
| `tkcore_drv_version` | `0444` | `.rodata+0x560` | `drv_version_read` | – | – | – | constant string | `tee_init_procfs` | recursive |
| `tkcore_os_version` | `0444` | `.rodata+0x5c0` | `tee_version_read` | – | – | – | reads `struct tee` version triple | `tee_init_procfs` | recursive |
| `tkcore_teed_version` | `0666` (`0x1b6`) | `.rodata+0x620` | `teed_version_read` | `teed_version_write` | – | – | 51-byte global `teed_version` | `tee_init_procfs` | recursive |

Every entry is created with `proc_create_data(..., tee)`, so each callback can reach the owning `struct tee` through `pde_data(file_inode(file))`. Callback slot offsets match the 6.1 `struct proc_ops` (`proc_open@0x08`, `proc_read@0x10`, `proc_write@0x20`, `proc_release@0x30`, size `0x60`), confirmed by the relocation set and by `teed_version_ops` having ELF size 96.

Removal is a single recursive `proc_remove(tee_proc_dir)`; the four child pointers are then nulled. The failure path inside `tee_init_procfs` performs exactly the same removal.

## Creation order and failure behaviour

1. `proc_mkdir("tkcore")` — on failure print `proc_mkdir tkcore failed.` and return `-1` **without** any removal (nothing exists yet).
2. `tkcore_log` — on failure print `proc_create failed.`
3. `tkcore_drv_version` — on failure print `proc_create tkcore_drv_version failed.`
4. `tkcore_os_version` — on failure print `proc_create tkcore_os_version failed.`
5. `tkcore_teed_version` — on failure print `proc_create tkcore_teed_version failed.`

Failures 2–5 fall into the shared unwind at `0x7e5c`: `proc_remove(dir)`, null all five pointers, return `-1`.

## Version surfaces

- `drv_version_read` returns the build constant `6:1.1-k6.6` (`.rodata+0x694`).
- `tee_version_read` formats `"%u.%u.%u-gp\n"` from three consecutive `u32` fields reached through `tee->priv` (`tee+0x88`) then `+0x2b8`, at `+0x64/+0x68/+0x6c` of that object, into a 32-byte stack buffer.
- `teed_version` is a 51-byte writable global initialised to `"unknown\n"` (`.data+0x180`, ELF size 51).
- All three reads share the local helper `copy_to_user_str` (`0x8534`), which computes `strlen(s)+1`, rejects `*ppos > length` with `-EINVAL` and the message `invalid pos: %lld len: %zu`, copies `min(count, length - *ppos)` bytes and advances `*ppos` by the number actually copied.

`teed_version_write` rejects `count > 50` with `-ENOMEM`, copies into the global, zero-fills the uncopied tail on partial copy, terminates the string and returns `count`.

### Documented divergence (memory safety)

Stock terminates with `teed_version[count + 1] = 0`. For `count == 50` that is an out-of-bounds store, and stock contains a fortify trap (`brk #0x5512`) on exactly that path. The island clamps the terminator to the last in-bounds index instead of reproducing an out-of-bounds write. This is recorded rather than replicated.

## Logging record

| Property | Stock evidence |
|---|---|
| IRQ source | `tee->log_irq` at `tee+0x80`, supplied by the provider; **not** discovered from DT by tkcore |
| IRQ skipped when | `tee->log_irq == 0` → prints `unknown tee log irq.` and continues without an IRQ |
| IRQ request | `request_threaded_irq(irq, tkcore_log_irq_handler, NULL, IRQF_TRIGGER_RISING, "tee_log_irq", NULL)` |
| IRQ failure | prints `failed to register klog_irq with %d`, unwinds |
| IRQ handler | `tkcore_log_irq_handler` wakes the log wait queue and returns `IRQ_HANDLED` |
| Waitqueue | `init_waitqueue_head(&klog.wq)` with lockdep name `&klog->wq` |
| Thread name | `tee-log` |
| Thread creation | `kthread_create_on_node(logd, &klog, NUMA_NO_NODE, "tee-log")` then `wake_up_process` |
| Thread handle | stored in `klog.task` |
| Shared buffer | `tee->log_shm` (`tee+0x70`), length `tee->log_shm_len` (`tee+0x78`) |
| Buffer skipped when | `log_shm == NULL` or `log_shm_len == 0` → proc surface stays up, logging disabled, return 0 |
| Size guards | `log_shm_len <= 0x100` → `init_klog_shm: shm_len %zu too small.`; `log_shm_len - 0x100 != header->size` → `Unexpected shm length: %u.` |
| Wake condition (reader) | `reader->pos != header->write_pos` |
| Wake condition (logd) | `header->logd_pos != header->write_pos` |
| Wait timeout | 125 jiffies in both readers and `logd` |
| Shutdown | `tee_exit_procfs` removes proc, frees the IRQ if one was taken, `kthread_stop`, clears the handle, then `wake_up` |

The conditional decision logic is preserved exactly: no shared buffer means no waitqueue/IRQ/thread but a successful return; a zero IRQ means no IRQ but a thread is still started.
