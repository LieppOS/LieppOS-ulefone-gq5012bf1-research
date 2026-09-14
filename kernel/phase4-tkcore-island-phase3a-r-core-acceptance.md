# GQ5012BF1 tkcore island Phase 3A-R — core lifecycle acceptance

Stock `03837d13…ed226` vs Phase-3A-R `9c6da05d238033de2a70b96c34bcbc081a9b62d13f64b72aee1713e86665315b`.

## Verdict

All five core APIs are closed. **No `INCOMPLETE`, no `STRUCTURAL_ONLY`.**

| Function | Stock size | Island size | KCFI | Call set | Class |
|---|---:|---:|---|---|---|
| `tee_core_alloc` | 344 | 340 | exact | exact | CFG_EQUIVALENT |
| `tee_core_add` | 576 | 568 | exact | exact | CFG_EQUIVALENT |
| `tee_core_del` | 192 | 192 | exact | exact | **EXACT_BYTE** |
| `tee_core_free` | 60 | 60 | exact | exact | **EXACT_BYTE** |
| `__tee_get` | 320 | 312 | exact | exact | CFG_EQUIVALENT |

## `tee_core_alloc`

Corrections applied against the Phase-2 donor shape:

1. **No misc device is created here.** The donor allocated a `tee_misc_dev` inside `tee_core_alloc`; stock creates all three records in `tee_core_add`. The donor's extra `devm_kmalloc` and `list_add` are gone.
2. **The name is copied verbatim.** Stock's format string is `"%s"`, not the donor's `"optee%s%02d"`. Proven by the `snprintf` call site (one vararg, `.rodata.str1.1+0x481` = `%s`). This matters: `/dev` node names come from `tee_device_configs`, not from `tee->name`.
3. **`tee_supp_init` failure is now handled.** Stock frees the object with `devm_kfree` and returns NULL; the donor ignored the result.
4. Allocation is `devm_kmalloc(dev, len + sizeof(struct tee), GFP_KERNEL|__GFP_ZERO)` — the length argument is added to `0x138`, matching `add x1, x4, #0x138`.
5. Mandatory `ops` slots verified at `+0x20`, `+0x28`, `+0x40`, `+0x48` = `open`, `close`, `alloc`, `free`.
6. `dev->release` is defaulted to `tee_plt_device_release` only when NULL (`device+0x328`).
7. Field initialisation matches the proven offsets exactly, including the single 64-bit store that sets `state = 0` and `shm_flags = 0x00040003`.

## `tee_core_add`

Now the full stock registration:

- Iterates exactly three `tee_device_configs` entries (`0x28` stride) and honours the per-entry `available` callback (all three NULL on GQ5012BF1, so all three register).
- Allocates a `0x68` record with `devm_kmalloc(..., GFP_KERNEL|__GFP_ZERO)` and fills `minor = MISC_DYNAMIC_MINOR`, `name`, `fops`, `parent = tee->dev`, `desc` at `+0x50`.
- `misc_register`, then tail-append `node` (`+0x58`) to `tee->list_misc`.
- Class capture: the first record's `this_device->class` becomes the module-global misc class; a NULL class or a mismatch is a `BUG` selecting `-ENOENT`.
- Then, in order: `tee_init_procfs(tee)` → `tee_init_sysfs(tee)` → `tee_peridev_init()`.
- `tee_init_sysfs` failure calls `tee_exit_procfs()` before unwinding, exactly as stock.
- Final loop prints one registration line per record with `dev_name`, `tee->id` and the assigned minor.

**Exact descriptor mapping reproduced** (from `.rela.data`):

| Node | fops | supplicant | name lookup |
|---|---|---|---|
| `tkcore_admin` | `tee_admin_fops` | 1 | 0 |
| `tkcore_client` | `tee_client_fops` | 0 | 1 |
| `tkcore_fp` | `tee_client_fops` | 0 | 0 |

**Stock allocation quirk reproduced, not silently fixed:** records are obtained with `devm_kmalloc` but released with plain `kfree` on both the add-failure path and in `tee_core_del`. This is centralised in `tee_misc_unwind()` and called out in the source comment.

## `tee_core_del`

Byte-identical. Order: `tee_peridev_exit()` → `tee_cleanup_sysfs(tee)` → deregister/unlink/`kfree` every record → `tee_supp_deinit(tee)` → `devm_kfree(tee->dev, tee)` → `0`. It does **not** call `tee_core_free`, and it does **not** call `tee_exit_procfs` (stock leaves proc teardown to module exit). NULL returns `0`.

## `tee_core_free`

Unchanged and still byte-identical: NULL → `0`; otherwise `tee_supp_deinit` then `devm_kfree`.

## `__tee_get`

Newly implemented and **now exported**.

- Prototype is `int __tee_get(struct tee *)`. The Phase-2 header declared `struct tee *__tee_get(struct tee *)`; that was wrong and is corrected.
- NULL reaches a `BUG` and returns `-EINVAL`.
- Atomic increment of `refcount` at `0xb8`.
- If the new count is not 1: `dev_warn` and return `-1`, **without undoing the increment** — the stock misuse behaviour, deliberately preserved.
- `try_module_get(tee->ops->owner)` under a `BUG_ON`, then `get_device(tee->dev)`.
- No `ops->start` → return `0`.
- `ops->start` failure → log, `put_device`, `module_put`, atomic decrement, return the backend error.

### Refcount split

Stock's `tee_get`/`tee_put` contain **no calls at all** (112 / 96 bytes). They are pure refcount helpers:

- `tee_get`: `BUG_ON(!tee)`, increment, `BUG_ON(new == 1)`, update `max_refcount` at `0xbc`, return 0.
- `tee_put`: `BUG_ON(!tee)`, decrement, `BUG_ON(new == 0)`, return 0.

The donor had merged the module/device/start logic into `tee_get`. Splitting it restores the stock invariant that only `__tee_get` may take the 0→1 transition and only it may touch the backend.

## Residual differences

All five have exact KCFI and exact call multisets; the small size deltas come from branch layout around the `BUG` sites and from stock's slightly different register allocation. No behavioural difference is known or intended.

## Forbidden techniques

None: no success stub, no fake provider, no stock object inclusion, no CRC injection, no ELF patching. The one deliberately deferred item is the `compat_ioctl` slot of both `file_operations` objects, whose stock implementation depends on the excluded 32-bit `convert_compat_*` marshalling helpers; it is recorded rather than substituted.
