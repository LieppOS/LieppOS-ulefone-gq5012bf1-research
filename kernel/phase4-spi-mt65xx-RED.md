# GQ5012BF1 `spi-mt65xx` mandatory RED

## Frozen baseline

RED used the pinned Nothing MT6878 MediaTek source at
`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f`:

- `drivers/spi/spi-mt65xx.c` — SHA256 `339e05e55161aa35696fa84fc6a0426e0d72b4a45e471f589e94e5cfe2e45669`
- `include/linux/platform_data/spi-mt65xx.h` — SHA256 `8971388cc7e30c6eaaae662c8eb7aaef67ecf89d7ebd76810f7bbbbba156ea16`

An initial exact-GKI compile using Common's same-path platform-data header
failed because that shorter header lacks `cs_setuptime`, `cs_holdtime`, and
`cs_idletime`, all dereferenced by the vendor C. This is header selection, not
a behavioral source delta.

The successful mandatory RED changes only the permitted external-build
plumbing: one include line names a flat, byte-identical copy of the pinned
vendor header. No declaration or executable statement changes. Build target:

```
tools/bazel build //lieppos/spi-mt65xx-red:spi_mt65xx_red
```

## RED result

`BUILD_RC=0`; compiler warnings 0; modpost warnings 0; unresolved symbols 0.
No `KBUILD_MODPOST_WARN`, stock symvers, CRC injection, fake provider, or ELF
patching was used.

| inventory | stock | RED | result |
|---|---:|---:|---|
| defined functions | 31 | 31 | exact rows; 31/31 bytes and KCFI exact |
| kernel imports | 65 | 65 | exact names and CRCs |
| MODVERSION records | 66 | 66 | exact, including `module_layout` |
| exports | 3 | 3 | exact names/classes; all CRCs natural |
| defined objects | 60 | 60 | functional objects exact; `.modinfo` offsets shift with vermagic |
| relocations | 545 | 545 | final target exact; RED has four `__bug_table` string-addend changes caused only by the shorter `__FILE__` path |
| strings | 120 | 120 | only `__FILE__` and vermagic strings differ |

Natural RED exports:

```
0xd3e99558 mtk_spi_set_autosuspend_delay EXPORT_SYMBOL
0xccc1e350 mt_spi_disable_master_clk     EXPORT_SYMBOL
0x1cc49782 mt_spi_enable_master_clk      EXPORT_SYMBOL
```

Stock is 58144 bytes; RED is 57936 bytes (SHA256
`048eaecac8f5f836bb24cd9d0f629d6d1287edc8bfffe21744ada4b7e0361b08`).
The bounded whole-file residual is build provenance: stock vermagic suffix
`-g945dff7bc1bf` versus workspace `-maybe-dirty`, build ID, and source-path
string/layout. There is no behavioral, KCFI, import, MODVERSION, export, table,
or callback delta.

## RED classification

The donor is **EXACT_SOURCE**. Since RED already closes every Linux-visible
stock contract naturally, no source-behavior delta or reverse engineering is
required. The final target merely moves the identical source/header pair to
the preferred `lieppos/spi-mt65xx/` package.
