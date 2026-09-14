# GQ5012BF1 tkcore — `tee_clkmgr_handle` recovered contract

Source of truth: stock `tkcore.ko` `0x8d88`, 308 bytes, KCFI `0x06da45e1`.
Recovered from the disassembly itself, not inferred from `tee_clkmgr_register`.

## Answers to the 23 required questions

| # | Question | Answer |
|---|---|---|
| 1 | prototype | `int tee_clkmgr_handle(uint32_t cmd, uint32_t val)` |
| 2 | stock KCFI | `0x06da45e1` |
| 3 | stock export CRC | historical `0x6913f6b2` |
| 4 | return type | `int` |
| 5 | token format | `(index << 1) \| class \| 1` (from `tee_clkmgr_register`) |
| 6 | token validation | none; the key is normalised as `cmd \| 1` |
| 7 | class extraction | not performed by `handle` — it compares the whole word |
| 8 | index extraction | not performed by `handle` |
| 9 | enable/disable selector | `val & 1`: **set → enable**, **clear → disable** |
| 10 | name lookup | none; `handle` matches the numeric token only |
| 11 | mutex | `mutex_lock(&clk_lock)` on entry; `mutex_unlock` on every exit |
| 12 | list traversal | forward `list_for_each_entry` over the global record list |
| 13 | duplicate handling | first match wins (`break`) |
| 14 | missing record | unlock, return `(int)TEEC_ERROR_ITEM_NOT_FOUND` = `-65528` |
| 15 | callback ABI | untyped pointer called with 0..3 pointer args (see below) |
| 16 | argument count | `argnum > 3` → `pr_err` + `(int)TEEC_ERROR_NOT_SUPPORTED` |
| 17 | argument order | `arg0→x0`, `arg1→x1`, `arg2→x2` |
| 18 | callback return | **ignored**; success always returns literal `0` |
| 19 | error mapping | `-65528` not found, `-65526` NULL callback / bad argnum |
| 20 | logging | exactly one `pr_err("tkcore: unsupported token %u argnum %zu\n", key, argnum)` |
| 21 | NULL callbacks | returns `-65526` **silently**, no log |
| 22 | malformed tokens | indistinguishable from "not found" → `-65528` |
| 23 | teardown/races | all record fields are snapshotted under the mutex; the callback runs **after** `mutex_unlock` |

## Decoded control flow

```text
mutex_lock(&clk_lock)
key = cmd | 1
for (pos = head->next; pos != head; pos = pos->next)
        if (*(u32 *)(pos - 0x38) == key) break;        // 8dd0..8dd8
if (pos == head) goto notfound                         // 8dcc
if ((struct record *)(pos - 0x38) == NULL) goto notfound   // 8ddc  cmp x8,#0x38
fn   = (val & 1) ? *(pos - 0x30) : *(pos - 0x28)       // 8dec/8df8 csel
arg0 = *(pos - 0x20); arg1 = *(pos - 0x18)             // 8dfc ldp
arg2 = *(pos - 0x10); argnum = *(pos - 0x08)           // 8e00 ldp
mutex_unlock(&clk_lock)                                // 8e08
if (!fn) return -65526                                 // 8e0c cbz
if (argnum > 3) { pr_err(...); return -65526; }        // 8e10 cmp #3, b.hi
switch (argnum) { ... }                                // 8e20 jump table
return 0
```

## Selector polarity — proven, and it inverts the existing header constants

`tst w20, #0x1` then `csel x9, x10, x9, eq` where `x9 = pos-0x30`, `x10 = pos-0x28`.
`eq` holds when `(val & 1) == 0`, so:

```text
(val & 1) == 0  ->  pos - 0x28  =  record + 0x10
(val & 1) == 1  ->  pos - 0x30  =  record + 0x08
```

`tee_clkmgr_register` fixes which field is which:

```text
8ee8: mov x19, x2      ; x2 = arg #3 = enable
8f0c: mov x24, x3      ; x3 = arg #4 = disable
8f94: stp x19, x24, [x0, #0x8]   ; +0x08 = enable, +0x10 = disable
```

Therefore **`val` bit 0 set selects `enable`**, clear selects `disable`.

`tee_clkmgr.h` currently defines `TEE_CLKMGR_OP_ENABLE 0` and
`TEE_CLKMGR_OP_DISABLE 1`, which is the exact inverse. Those constants have
**zero uses** in the entire tree, so they were never exercised. They are
corrected in Phase 3D to match stock.

## Record layout — confirms the existing 72-byte foundation

| Offset | Field | Access in `handle` |
|---|---|---|
| `+0x00` | `u32 token` | `ldur w10, [x8, #-0x38]` |
| `+0x08` | `void *enable` | `pos - 0x30` |
| `+0x10` | `void *disable` | `pos - 0x28` |
| `+0x18` | `void *arg0` | `ldp ..., [x8, #-0x20]` |
| `+0x20` | `void *arg1` | same `ldp` |
| `+0x28` | `void *arg2` | `ldp ..., [x8, #-0x10]` |
| `+0x30` | `size_t argnum` | same `ldp` |
| `+0x38` | `struct list_head entry` | traversal cursor |

Total `0x48` = 72 bytes, matching the already-closed registration subsystem and
its existing `static_assert`s. **No change to that foundation is required.**

## Return values are TEEC codes truncated to int

```text
mov w0, #-0xfff8  ->  -65528  ->  0xFFFF0008  =  TEEC_ERROR_ITEM_NOT_FOUND
mov w0, #-0xfff6  ->  -65526  ->  0xFFFF000A  =  TEEC_ERROR_NOT_SUPPORTED
```

Both constants already exist in `tee_client_api.h`; `(int)` truncation of the
`0xFFFF00xx` value reproduces the exact immediates.
