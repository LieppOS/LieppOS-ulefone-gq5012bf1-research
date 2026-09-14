# GQ5012BF1 tkcore clock-manager registration contract

Static recovery from stock `tee_clkmgr_register` (`0x8ec0`, 516 bytes, KCFI `0xe70e59df`), cross-checked against `plat_register_spi_clk` (`0x9630`) and `tee_peridev_exit` (`0x953c`).

## Prototype

The historical export CRC is reproduced naturally only by an **untyped** callback boundary. A brute-force KCFI search over 36 candidate signatures with the exact GKI toolchain (`clang-r487747c`, `-fsanitize=kcfi`) yields exactly one match for `0xe70e59df`:

```c
int tee_clkmgr_register(const char *name, int index,
                        void *enable, void *disable,
                        void *arg0, void *arg1, void *arg2,
                        size_t argnum);
```

This corrects the earlier island header, which declared a typed `int (*enable)(void *, uint32_t)` plus `mask`/`shift` — that shape cannot produce the stock KCFI ID.

## Registration record — 72 bytes (`0x48`), `kmalloc(GFP_KERNEL)`

| Offset | Field | Source argument | Evidence |
|---:|---|---|---|
| `0x00` | `u32 token` | derived | `str w24,[x0]` |
| `0x08` | `void *enable` | arg 3 | `stp x19,x24,[x0,#8]` |
| `0x10` | `void *disable` | arg 4 | same `stp` |
| `0x18` | `void *arg0` | arg 5 | `stp x23,x22,[x0,#0x18]` |
| `0x20` | `void *arg1` | arg 6 | same `stp` |
| `0x28` | `void *arg2` | arg 7 | `stp x21,x20,[x0,#0x28]` |
| `0x30` | `size_t argnum` | arg 8 | same `stp` |
| `0x38` | `struct list_head entry` | – | `__list_add_valid(x25+0x38, head, first)` |

All eight anchors are enforced by `static_assert` in the island source and validated by the build.

## Name storage

The name is **not** stored. It is folded into the token by an exact `strcmp` classification:

| Name | Class bits |
|---|---|
| `spi` | `0x00000` |
| `i2c` | `0x10000` |
| `i2c-dma` | `0x20000` |

Any other name prints `invalid clkname %s` and returns `-EINVAL`.

## Token

```
token = class | ((u32)index << 1) | 1
```

The low bit is always set, which is what makes the runtime dispatcher's `orr w19, w19, #1` on the incoming command word meaningful. The shifted index must satisfy `(index << 1) < 0x10000`, else stock prints `%s-%d: invalid id` and returns `-EINVAL`.

## Validation order and return values

1. Trace `clkname=%s id=%d`.
2. `argnum > 3` → `does not support argnum %zu`, `-EINVAL`.
3. Name classification → `invalid clkname %s`, `-EINVAL`.
4. Index range → `%s-%d: invalid id`, `-EINVAL`.
5. Allocation failure → `-ENOMEM` (no message).
6. Success → `0`.

Note the ordering quirk faithfully reproduced by the island: the `argnum` check happens **before** the name check, and the allocation happens **before** the duplicate scan.

## Duplicate behaviour

Under the global mutex, the list is scanned for a record with the same token. If one exists, its `enable`, `disable`, `arg0`, `arg1`, `arg2` and `argnum` are overwritten in place, the mutex is dropped, the freshly allocated record is `kfree`d, and `0` is returned. The list is never given two records with the same token.

## Locking and linkage

- Global mutex at `.data+0x1b8`.
- Global list head at `.data+0x1e8`, self-linked in `.data` (both relocations point at `.data+0x1e8`), i.e. a statically initialised `LIST_HEAD`.
- New records are inserted at the **head**.
- The mutex is held across the duplicate scan and the insertion; it is not held while the record is allocated or freed.

## Teardown

Records are owned by the clock manager and released only by `tee_peridev_exit`; see `phase4-tkcore-clkmgr-teardown-contract.md`.

## Out of scope

`tee_clkmgr_handle` (`0x8d88`) consumes these records to dispatch enable/disable requests from the secure world, selecting `enable` for even command words and `disable` for odd ones and calling through with `argnum` pointer arguments. It is deliberately **not** implemented in Phase 3P: registration and teardown do not depend on it, and it is the runtime secure-world control surface reserved for the dedicated clock-manager phase. Its record layout requirements are nevertheless satisfied by the reconstructed record above.
