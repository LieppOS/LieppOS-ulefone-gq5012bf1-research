# GQ5012BF1 tkcore sysfs lifecycle

Both functions are now **byte-identical** to stock.

## Prototypes

| Function | Stock offset | Size | KCFI | Prototype |
|---|---:|---:|---|---|
| `tee_init_sysfs` | `0x6dd0` | 508 | `0xa1200a70` | `int tee_init_sysfs(struct tee *)` |
| `tee_cleanup_sysfs` | `0x6fd0` | 144 | `0x246c186b` | `void tee_cleanup_sysfs(struct tee *)` |

The Phase-2 donor declared `tee_init_sysfs` as `void`, giving rebuilt KCFI `0x246c186b` against stock's `0xa1200a70`. That was the one in-scope KCFI mismatch and it is now resolved: `tee_core_add` needs the `int` return because a sysfs failure must trigger `tee_exit_procfs` and the misc unwind.

## Attribute target device — corrected

The donor created the files on `tee_primary_misc(tee)->miscdev.this_device` after checking `dev_get_drvdata()`. Stock does neither: every `device_create_file`/`device_remove_file` call loads `[x19, #0x98]`, i.e. **`tee->dev`**, the parent device passed to `tee_core_alloc`. There is no drvdata validation and no misc-device lookup. Removing that donor divergence is what makes both functions byte-exact.

## Attribute set — eight entries, not nine

Stock's array is at `.data+0x80` with stride `0x20` and is fully enumerated by `tee_cleanup_sysfs`, which removes exactly eight files:

| # | Name | `.data` | Mode | show | store |
|---:|---|---|---|---|---|
| 0 | `dump` | `0x80` | `0444` | `dump_show` (`0x7064`) | – |
| 1 | `stat` | `0xa0` | `0444` | `stat_show` (`0x70fc`) | – |
| 2 | `info` | `0xc0` | `0444` | `info_show` (`0x7160`) | – |
| 3 | `state` | `0xe0` | `0444` | `tee_show_state` (`0x71ac`) | – |
| 4 | `name` | `0x100` | `0444` | `name_show` (`0x7200`) | – |
| 5 | `refcount` | `0x120` | `0444` | `refcount_show` (`0x7240`) | – |
| 6 | `type` | `0x140` | `0444` | `type_show` (`0x7280`) | – |
| 7 | `conf` | `0x160` | `0444` | `conf_show` (`0x72c4`) | – |

The donor's writable `test` attribute (`test_show`/`test_store`) does **not** exist in stock: the array has no ninth entry, there is no store callback anywhere in it, and stock has no `kstrtoull` import. It has been removed, which also eliminated the last spurious `kstrtoull` import from the island build.

## Creation and failure behaviour

`tee_init_sysfs` returns `-EINVAL` for a NULL `tee`. It creates the eight files in order; on the first failure it prints `bad device_create_file(): %d` and removes exactly the attributes created so far, in reverse order, then returns the `device_create_file` error. A fully successful pass returns `0`.

## Cleanup order

`tee_cleanup_sysfs` is a no-op for a NULL `tee`; otherwise it removes all eight attributes from `tee->dev` in ascending index order and returns `void`.

## Lifecycle consequences for Phase 3A

- `tee_core_add` can now propagate a sysfs failure and run stock's unwind (`tee_exit_procfs`, then misc deregistration).
- `tee_core_del` can call `tee_cleanup_sysfs(tee)` at its stock position with matching semantics.
- Because the attributes live on `tee->dev`, sysfs teardown is independent of the misc-record list, which is what allows stock to clean sysfs up *before* deregistering the misc devices.
