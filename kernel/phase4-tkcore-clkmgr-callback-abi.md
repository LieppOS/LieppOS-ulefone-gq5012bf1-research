# GQ5012BF1 tkcore — clock-manager callback ABI

Callback typing is erased to `void *` at the registration boundary, so the
runtime call ABI is derived from the **actual indirect call sites inside
`tee_clkmgr_handle`**, exactly as required.

## Dispatch table

`.rodata+0x69f`, four bytes, indexed by `argnum` and scaled by 4 from `0x8e30`:

| `argnum` | table byte | target | site |
|---:|---:|---|---|
| 0 | 0 | `0x8e30` | `blr x24` |
| 1 | 13 | `0x8e64` | `mov x0,x20; blr x24` |
| 2 | 17 | `0x8e74` | `mov x0,x20; mov x1,x21; blr x24` |
| 3 | 22 | `0x8e88` | `mov x0,x20; mov x1,x21; mov x2,x22; blr x24` |

`argnum > 3` is rejected before the table is consulted (`cmp x23, #3; b.hi`),
so the table is only ever indexed with 0..3 and needs no default entry.

## Per-`argnum` register contract

| `argnum` | x0 | x1 | x2 | stack args | return reg used? |
|---:|---|---|---|---|---|
| 0 | — | — | — | none | **no** |
| 1 | `arg0` | — | — | none | **no** |
| 2 | `arg0` | `arg1` | — | none | **no** |
| 3 | `arg0` | `arg1` | `arg2` | none | **no** |

- Arguments are passed as raw 64-bit pointers in `x0..x2`. No argument is ever
  placed on the stack, and `x3+` are never populated.
- The callback's return value in `w0`/`x0` is **discarded**: every successful
  path executes `mov w0, wzr` immediately after `blr`, so `tee_clkmgr_handle`
  returns literal `0` regardless of what the callback returns.
- Effective callee type is therefore `void (*)(void)`, `void (*)(void *)`,
  `void (*)(void *, void *)`, `void (*)(void *, void *, void *)`.

## KCFI on the indirect call

Stock `tkcore.ko` contains **no `kcfi_typeid` check at any of the four `blr`
sites** — the sequence is a bare `blr x24` with no preceding `ldur w16, [x24,#-4]`
/ `cmp` / `brk` triple. This is consistent with the module being built without
`CONFIG_CFI_CLANG` indirect-call checking on this path, and with the callback
type being fully erased through `void *`.

Consequence for the reconstruction: calling through a `void *` cast to a
concrete function-pointer type would make Clang emit a KCFI check under the
island's build flags, which stock does not have. The reconstruction therefore
routes the indirect call through an explicitly non-CFI-checked call, matching
stock's bare `blr`.

## Registered callbacks in practice

`plat_register_spi_clk()` (already closed) registers `mtk_enable_clk` /
`mtk_disable_clk` for names `spi`, `i2c`, `i2c-dma`. Both have the
`argnum == 1` shape, so the live path through the table is the `0x8e64` case
with `arg0` carrying the clock cookie.
