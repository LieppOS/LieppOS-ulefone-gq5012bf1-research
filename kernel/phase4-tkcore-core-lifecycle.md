# GQ5012BF1 stock tkcore core/provider lifecycle oracle

## Result

The five core targets were fully disassembled and their local semantics recovered. `tee_core_free` was already byte-identical. **Phase-3A nevertheless stops BLOCKED at its Phase-6 core gate** because `tee_core_add` and `tee_core_del` have mandatory direct edges into procfs/log/IRQ/thread and SPI/clock-manager subsystems which the task explicitly excludes. Returning success from placeholders would be speculative and would violate the acceptance rules.

All addresses below are `.text` offsets in stock `tkcore.ko` SHA256 `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226`.

## `tee_core_alloc`

- Prototype: `struct tee *tee_core_alloc(struct device *, char *, int, const struct tee_ops *, size_t)`
- Offset/size/KCFI: `0x1aa4` / 344 / `0x89819660`
- Input guards: rejects null device, name or ops; requires ops slots at `+0x20`, `+0x28`, `+0x40`, `+0x48` (`open`, `close`, `alloc`, `free`).
- Allocation: `devm_kmalloc(dev, len + 0x138, 0xdc0)`. Flags `0xdc0` include zeroing; allocation is therefore equivalent to a zeroing managed allocation.
- If `dev->release` (`device+0x328`) is null, stores `tee_plt_device_release`.
- Stores `id@0x60`; `priv = tee + 0x138 @0x88`; `ops@0x90`; `dev@0x98`.
- Formats the 64-byte name at `0x20` with stock format `optee%s%02d`.
- Initializes mutex `tee+0xf8`, refcount `0@0xb8`, and list heads at `0xa0`, `0xd8`, `0xe8`.
- One 64-bit store at `0x128` initializes `state=0` and `shm_flags=0x00040003`.
- Calls `tee_supp_init(tee)`. On nonzero return it calls `devm_kfree(dev, tee)` and returns null.
- Otherwise returns the allocated object.

### Allocation ownership

The provider owns the returned managed object until `tee_core_add` transfers it into registered-device lifetime. Failure before registration uses `tee_core_free`; normal removal uses `tee_core_del`, which frees directly after subsystem teardown.

## `tee_core_free`

- Prototype: `int tee_core_free(struct tee *)`
- Offset/size/KCFI: `0x1c08` / 60 / `0xa1200a70`
- Phase-2 status: **EXACT_BYTE**.
- Null is a no-op returning 0.
- Non-null order: `tee_supp_deinit(tee)` → `devm_kfree(tee->dev, tee)` → 0.
- It performs no registration teardown; it is the pre-registration/failure-path free.

## `__tee_get`

- Prototype: `int __tee_get(struct tee *)` (the provisional public declaration returning `struct tee *` was disproved by stock KCFI and the frozen `tkcore_drv` witness).
- Offset/size/KCFI: `0x168` / 320 / `0xa1200a70`.
- Null input reaches a stock `BUG_ON` site.
- Atomically increments `refcount@0xb8` with acquire/release ordering.
- If the new count is not 1, emits `_dev_warn(tee->dev, ...)` and returns `-1`; stock does **not** undo this increment on that misuse path.
- Requires `try_module_get(tee->ops->owner)` (stock BUG site on false), then `get_device(tee->dev)`.
- If `ops->start@+0x10` is null: returns 0.
- Otherwise calls `ops->start(tee)` with KCFI `0xa1200a70`.
- Start failure order: `_printk` → `put_device` → `module_put` → atomic decrement → return backend error.
- Success returns 0 and leaves the one provider reference active.

The related non-exported `tee_get` and `tee_put` use the same refcount anchor. `tee_get` warns if its increment reaches 1 and updates `max_refcount@0xbc`; `tee_put` warns if its decrement reaches 0. They deliberately do not call backend start/stop.

## `tee_core_add`

- Prototype: `int tee_core_add(struct tee *)`
- Offset/size/KCFI: `0x1c48` / 576 / `0xa1200a70`.
- Null returns `-EINVAL`.
- Iterates exactly three `tee_device_configs` entries, stride `0x28`.
- Reads optional availability callback at descriptor `+0x20`; all three GQ5012BF1 entries are null.
- Per enabled entry allocates zeroed 104-byte `tee_misc_dev` using `devm_kmalloc(tee->dev, 0x68, 0xdc0)`.
- Record layout proven by stores and list arithmetic:
  - embedded `struct miscdevice @0x00`
  - `minor@0x00 = 0xff` (`MISC_DYNAMIC_MINOR`)
  - descriptor name/fops copied to `+0x08/+0x10`
  - parent `tee->dev` stored at `+0x28`
  - descriptor pointer stored at `+0x50`
  - list node at `+0x58`
- Exact descriptor relocations:
  - `tkcore_admin` → `tee_admin_fops`
  - `tkcore_client` → `tee_client_fops`
  - `tkcore_fp` → `tee_client_fops`
- Calls `misc_register(record)`, appends `record+0x58` to `tee->list_misc@0xa0`, then obtains `this_device->class`. The first class becomes the global misc-class pointer; later records must match it. Null/mismatch reaches a stock BUG site and selects `-ENOENT`.
- After all three registrations, mandatory order is:
  1. `tee_init_procfs(tee)`; unwind misc records on error.
  2. `tee_init_sysfs(tee)`; on error call `tee_exit_procfs`, then unwind misc records.
  3. `tee_peridev_init()`.
  4. Print registration information for every linked record; return 0.
- Allocation/misc failure returns `-ENOMEM` or `misc_register` error and unwinds all already-linked records.
- Unwind order per record: `misc_deregister(&record->miscdev)` → list deletion → `kfree(record)`.

### Stock allocator quirk

Stock obtains each record using `devm_kmalloc` but explicitly releases it with `kfree` on add failure and normal deletion. This is observable in relocations and is recorded as a stock quirk; it must not be silently rewritten as `devm_kfree` in a fidelity claim.

## `tee_core_del`

- Prototype: `int tee_core_del(struct tee *)`
- Offset/size/KCFI: `0x1e8c` / 192 / `0xa1200a70`.
- Null returns 0.
- Exact non-null teardown order:
  1. `tee_peridev_exit()`
  2. `tee_cleanup_sysfs(tee)`
  3. For every node on `list_misc@0xa0`: recover record by subtracting `0x58`, `misc_deregister`, list delete, `kfree(record)`
  4. `tee_supp_deinit(tee)`
  5. `devm_kfree(tee->dev, tee)`
  6. return 0
- It does not call `tee_core_free`; it reproduces that final pair after registered-subsystem teardown.

## Direct blocker closure

| Required callee | Stock size | What it does | Why it cannot be replaced in Phase 3A |
|---|---:|---|---|
| `tee_init_procfs` | 760 | proc directory/files, log state, optional IRQ, waitqueue, kernel log thread, complete failure unwind | Explicit Phase 3F procfs/log exclusion |
| `tee_exit_procfs` | 140 | proc removal, IRQ free, kthread stop, wake | Explicit Phase 3F exclusion |
| `tee_peridev_init` | 28 | unconditional `plat_register_spi_clk()` | Leads directly to excluded SPI/clock-manager work |
| `plat_register_spi_clk` | 296 | scans 20 `spi@%d` DT nodes/clocks and invokes `tee_clkmgr_register` | Explicit Phase 3E SPI/clkmgr exclusion |
| `tee_peridev_exit` | 168 | locked destruction of all clock-manager records | Explicit Phase 3E exclusion |

`tee_init_sysfs` is also a Phase-3A direct helper and has a Phase-2 KCFI mismatch (`void` donor vs stock `int`), but that mismatch is recoverable. It is not the blocking ambiguity.

## Gate decision

The source implementation was restored byte-for-byte to the proven Phase-2 source snapshot after the blocker was established. No success-returning boundary stub, weak fake provider, stock object inclusion, CRC injection or ELF patch is retained.

Classification at the mandatory core gate:

- `tee_core_free`: `EXACT_BYTE`
- `tee_core_alloc`: `INCOMPLETE` (source not changed; recovered oracle documented)
- `__tee_get`: `INCOMPLETE` (source not changed; recovered oracle documented)
- `tee_core_add`: `INCOMPLETE_BLOCKED_BY_EXCLUDED_3E_3F_CLOSURE`
- `tee_core_del`: `INCOMPLETE_BLOCKED_BY_EXCLUDED_3E_3F_CLOSURE`

Because Phase 6 requires **no INCOMPLETE among all five**, work must stop before TEEC context/session implementation.
