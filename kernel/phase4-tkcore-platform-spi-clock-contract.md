# GQ5012BF1 tkcore platform SPI clock contract

Static recovery from stock `plat_register_spi_clk` (`0x9630`, 296 bytes, KCFI `0x36b1c5a6`) and `tee_peridev_init` (`0x951c`, 28 bytes, same KCFI). No hardware was touched.

## Entry point

```c
int tee_peridev_init(void)   /* stock: tail-call into plat_register_spi_clk, returns its value */
int plat_register_spi_clk(void)
```

`tee_peridev_init` is unconditional: it contains exactly one call and no guards. Both share KCFI `0x36b1c5a6`, i.e. `int (*)(void)`.

## Exact loop contract

```
pr_info("tkcore: register platform spi clk\n")
for (index = 0; index < 20; index++) {
        sprintf(name, "spi%d", index);
        node = of_find_node_by_name(NULL, name);
        if (!node)
                break;                       /* stop the scan entirely */
        clk = of_clk_get_by_name(node, "spi-clk");
        if (IS_ERR_OR_NULL(clk)) {
                pr_warn("tkcore: of_clk_get_by_name: failed with %ld\n", PTR_ERR(clk));
                continue;                    /* skip this index only */
        }
        tee_clkmgr_register("spi", index, mtk_enable_clk, mtk_disable_clk,
                            clk, NULL, NULL, 1);
}
return 0;
```

| Item | Stock evidence |
|---|---|
| Loop bound | `cmp w19, #0x14` → indices `0..19`, at most 20 nodes |
| Name format | `sprintf` with `.rodata.str1.1+0x9ec` = `spi%d`; buffer is 10 stack bytes, zeroed before the loop |
| Node lookup | `of_find_node_by_name(NULL, name)` — a global by-name search, **not** a path lookup, so the DT node name matters and its unit address does not |
| Clock name | `.rodata.str1.1+0x160` = `spi-clk` |
| Clock getter | `of_clk_get_by_name(node, "spi-clk")` |
| Missing node | `cbz x0` → branch to function exit: the scan **stops** at the first absent index |
| Bad clock | NULL or `IS_ERR` (`cmn x4,#1,lsl#12; b.hi`) → warn and **continue** to the next index |
| Registration name | always the literal `spi` (`.rodata.str1.1+0x964`), never the node name |
| Registered index | the loop counter |
| Callbacks | `mtk_enable_clk` (`.text+0x975c`), `mtk_disable_clk` (`.text+0x97a0`) |
| Per-entry data | `arg0 = clk`, `arg1 = NULL`, `arg2 = NULL`, `argnum = 1` |
| Return | always `0`; `tee_clkmgr_register`'s result is ignored |

Because `spi%d` is used for the DT search, the effective naming contract is node **name** `spi0` … `spi19` (a node written `spi@1100a000` with name `spi` would not match; MediaTek DTs used here name the nodes `spiN`).

## Callbacks

Both are `void (*)(void *)` — KCFI `0xa488ebfc`, confirmed by an exact-ID toolchain search — and both are reconstructed **byte-identically**:

```c
static void mtk_enable_clk(void *data)   /* clk_prepare; clk_enable; on failure clk_unprepare */
static void mtk_disable_clk(void *data)  /* clk_disable; clk_unprepare */
```

`mtk_enable_clk` returns early without enabling if `clk_prepare` fails, and unprepares if `clk_enable` fails. Neither callback is invoked during Phase 3P: they are only stored in the registration records. Runtime dispatch belongs to `tee_clkmgr_handle`, which stays out of scope.

## Faithfully reproduced stock quirks

- **No `of_node_put`.** Stock never drops the reference taken by `of_find_node_by_name`, leaking one node reference per registered SPI controller. The island reproduces this rather than silently changing device-tree refcount behaviour; it is recorded here instead.
- **Return value ignored.** A failing `tee_clkmgr_register` neither aborts the scan nor changes the return value.
- **Registration errors are invisible** to `tee_core_add`, which therefore cannot fail because of clock registration.
