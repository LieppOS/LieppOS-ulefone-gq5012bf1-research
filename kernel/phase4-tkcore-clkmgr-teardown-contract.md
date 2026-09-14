# GQ5012BF1 tkcore clock-manager teardown contract

Static recovery from stock `tee_peridev_exit` (`0x953c`, 168 bytes, KCFI `0xa540670c`). The island reconstruction of this function is **byte-identical** to stock.

## Prototype

```c
void tee_peridev_exit(void);
```

KCFI `0xa540670c` is `void (*)(void)`, the same ID as `tee_exit_procfs`.

## Exact behaviour

1. `mutex_lock(&tee_clkmgr_lock)` — the same global mutex at `.data+0x1b8` used by `tee_clkmgr_register`.
2. Walk the global list at `.data+0x1e8` from the head.
3. For each node: recover the record by subtracting `0x38` (`ldr x23,[x20],#-0x38` loads the next pointer and rebases in one step), validate and unlink with `__list_del_entry_valid`, then `kfree` the record.
4. `mutex_unlock(&tee_clkmgr_lock)`.

The iteration is a safe list walk: the successor pointer is loaded **before** the current record is unlinked and freed, which is exactly what `list_for_each_entry_safe` generates.

## Locking

- The mutex is held for the **entire** drain, including every `kfree`. Registration and teardown can therefore never interleave.
- No other lock is taken, and no callback is invoked while the mutex is held.

## Resource release

| Resource | Released here? | Note |
|---|---|---|
| Registration record (72 bytes) | Yes, `kfree` | allocated by `tee_clkmgr_register` |
| `struct clk` handles in `arg0` | **No** | stock never calls `clk_put`; the reference obtained by `of_clk_get_by_name` is not returned |
| Device-tree node references | **No** | never dropped, see the platform SPI contract |
| Clock hardware state | **No** | teardown never toggles a clock; `mtk_disable_clk` is not called |

The list head itself is left correctly empty and reusable, so a later `tee_core_add` can register again.

## Ordering inside `tee_core_del`

Stock calls `tee_peridev_exit()` **first**, before sysfs cleanup, misc-device teardown and the supplicant/RPC release. Phase 3P preserves that: the function is self-contained, takes no arguments and depends on no `struct tee` state, so it can be called at exactly the stock position.

## Poison values

Stock materialises `0xdead000000000100` and `0xdead000000000122` before the loop, i.e. `LIST_POISON1`/`LIST_POISON2` for the failed-validation path of `__list_del_entry_valid`. The island reproduces this implicitly by using the standard `list_del` machinery, which is why the function comes out byte-identical.
