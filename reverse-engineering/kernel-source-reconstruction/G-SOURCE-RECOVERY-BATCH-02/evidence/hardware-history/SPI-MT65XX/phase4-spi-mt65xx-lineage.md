# GQ5012BF1 `spi-mt65xx` lineage

## Verdict

The stock module is the **MediaTek-modified split-module variant** in pinned
Nothing MT6878 `device_modules`, not the upstream Android Common driver.

Exact lineage:

```
device_modules@957dac185efe46cbf6336b0fff9516d84c8cd78f
  drivers/spi/spi-mt65xx.c
  include/linux/platform_data/spi-mt65xx.h
```

The one C source and one vendor header are sufficient. The source target is
`CONFIG_DEVICE_MODULES_SPI_MT65XX` / `spi-mt65xx.o`.

## Stock-to-source proof

An exact-GKI external build, with only a one-line include-path redirect needed
to make Kleaf select the pinned vendor header rather than GKI's shorter
same-path header, produces:

- 31/31 same defined function rows (section, offset, size, binding, KCFI)
- 31/31 function bytes exact
- 65/65 undefined kernel imports exact
- 66/66 MODVERSION records exact (including `module_layout`)
- 3/3 exports exact, all naturally generated and all `EXPORT_SYMBOL`
- exact OF alias set, platform alias, driver callbacks, PM ops, and metadata

This makes source identity stronger than a name/compatible match.

## Why upstream/Common is not exact

The GKI Common source is 1425 lines/38286 bytes versus the vendor source's
1818 lines/50038 bytes; a source diff is 1735 lines. Common lacks:

- all three exported vendor APIs
- `mt6983`, `mt6985`, and `mt6989` compatible-data variants
- MT6989 `enhance_packet_len` handling (`CFG5`, up to 4 GiB encoded length)
- vendor `tee-only` CS behavior
- dynamic `mediatek,autosuspend-delay` and exported update helper
- `spi_log` sysfs/debug-register support
- the exact vendor PIO polling and SPI-memory deltas
- the vendor header fields `cs_setuptime`, `cs_holdtime`, `cs_idletime`

Therefore upstream is only a structural ancestor.

## Correct MT6878 variant

Although the SoC is MT6878/MT6878T, the merged stock DT binds all eight SPI
controllers using `compatible = "mediatek,mt6989-spi"`. The exact source's
`mt6989_compat` is consequently the active quirk row:

```
need_pad_sel=true
must_rx=false
must_tx=false
enhance_timing=true
dma_ext=true
ipm_design=true
support_quad=true
sw_cs=true
enhance_packet_len=true
```

That row, all 14 OF matches, and every compatible-data object are present in
the stock ELF and the rebuilt ELF with exact object layout/relocations apart
from separately documented build-provenance metadata.

## Residual `.ko` identity

The rebuilt `.ko` is not whole-file byte-identical: stock is 58144 bytes and
the RED build is 57936 bytes. The executable function surface, KCFI, import
ABI, MODVERSION ABI, and natural exports are exact. The remaining difference
is confined to module/build provenance (`vermagic` suffix/build ID and
compiler-generated `.modinfo` unique-symbol numbering/section layout), not
Linux-visible behavior or provider ABI. Full section/object classification is
in the parity tables and RED report.
