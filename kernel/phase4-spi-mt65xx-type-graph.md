# GQ5012BF1 `spi-mt65xx` exported type graph

## Complete exported declarations

| export | exact declaration | stock/rebuilt KCFI | declaration origin |
|---|---|---:|---|
| `mt_spi_enable_master_clk` | `void mt_spi_enable_master_clk(struct spi_device *spidev)` | `0xe397d461` | exact source line 1792 |
| `mt_spi_disable_master_clk` | `void mt_spi_disable_master_clk(struct spi_device *spidev)` | `0xe397d461` | exact source line 1782 |
| `mtk_spi_set_autosuspend_delay` | `void mtk_spi_set_autosuspend_delay(struct spi_device *spi, int delay_ms)` | `0xa1815d14` | exact source line 1729 |

All three are defined/exported in the `.c`; there is no shared public vendor
prototype header in this snapshot. Independent Goodix declarations confirm the
clock signatures. The rebuilt KCFI IDs equal stock exactly, proving the
function type/arity and the `struct spi_device` tag spelling.

## Type dependencies

```
exported functions
  └── struct spi_device *       common/include/linux/spi/spi.h
        └── struct spi_controller * master
              └── controller devdata = struct mtk_spi (private .c type)
                    └── struct clk *spi_clk
```

`int delay_ms` is the ordinary C `int`; no typedef spelling is involved.
Neither `struct mtk_spi` nor `struct mtk_chip_config` crosses the export ABI:
the exported parameter is `struct spi_device *`, and private data is recovered
inside each function with `spi_master_get_devdata(spi->master)`.

## Private vendor header

Exact source also requires:

```
struct mtk_chip_config {
    u32 sample_sel;
    u32 cs_setuptime;
    u32 cs_holdtime;
    u32 cs_idletime;
    u32 tick_delay;
};
```

Origin:
`device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f/include/linux/platform_data/spi-mt65xx.h`
(SHA256 `8971388cc7e30c6eaaae662c8eb7aaef67ecf89d7ebd76810f7bbbbba156ea16`).

GKI Common's same-path header omits the three `cs_*time` members, while the
exact driver reads all three in `spi_dump_config`. Building exact C against
that wrong header fails at compile time; the final wrapper redirects only this
include to the pinned vendor header. This is header provenance/include-path
plumbing, not a behavioral delta.

## CRC influence and the failed old witness

The former two-function ABI witness used the visually identical clock
prototypes but generated `0x6753a548` and `0x6d9b7fda`, not stock. That proves a
prototype string alone is insufficient evidence for this translation unit's
genksyms result: exact preprocessing/declaration history matters. The full
pinned C/header graph naturally generates:

- enable: `0x1cc49782`
- disable: `0xccc1e350`
- autosuspend: `0xd3e99558`

No type-name brute force, copied CRC, witness symvers, or private-member-name
search is used in the provider build.
