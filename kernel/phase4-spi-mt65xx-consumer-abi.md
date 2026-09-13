# GQ5012BF1 `spi-mt65xx` complete stock-consumer ABI

## Method

All **471 physical `.ko` placements** in the committed stock tree were scanned,
not merely `modules.dep`. For every ELF with `__versions`, each 64-byte
MODVERSION record was decoded and tested against the provider's complete
three-symbol export set. The result was cross-checked against
`kernel/stock-module-imports.tsv`, `kernel/stock-intermodule-abi.csv`, and
`modules.dep`.

Provider oracle: SHA256
`5463e06c205623e4b1b713416836e3b5235dc246c7d536595f6613ba3492d712`.

## Result

Exactly **one stock consumer / two edges** exist. No module consumes
`mtk_spi_set_autosuspend_delay`.

| provider | consumer | symbol | provider stock CRC | consumer-required CRC | prototype | provider KCFI | stock load relation | result |
|---|---|---|---:|---:|---|---:|---|---|
| `spi-mt65xx` | `microarray_fp_tee` | `mt_spi_enable_master_clk` | `0x1cc49782` | `0x1cc49782` | `void (struct spi_device *)` | `0xe397d461` | provider P:119/R:117; consumer P:182/R:186 | stock exact; rebuilt provider `0x1cc49782` NATURAL |
| `spi-mt65xx` | `microarray_fp_tee` | `mt_spi_disable_master_clk` | `0xccc1e350` | `0xccc1e350` | `void (struct spi_device *)` | `0xe397d461` | provider P:119/R:117; consumer P:182/R:186 | stock exact; rebuilt provider `0xccc1e350` NATURAL |

The provider is loaded 63 normal-list entries and 69 recovery-list entries
before its sole consumer. `modules.dep` independently records:

```
/lib/modules/spi-mt65xx.ko:
/lib/modules/microarray_fp_tee.ko: /lib/modules/tkcore.ko /lib/modules/spi-mt65xx.ko /lib/modules/fingerprint.ko
```

## Source-tree callers are not stock consumers

The pinned Nothing tree also contains compile-time callers in Goodix TUI,
Goodix fingerprint, and ST54SPI NFC source. None of their corresponding
GQ5012BF1 stock modules imports these symbols in the 471-module population;
they are not added to the stock consumer list.

## Acceptance rule

Because all three rebuilt provider export CRCs equal stock naturally, every
stock consumer is ABI-compatible. The sole available source-reconstructed
consumer, `microarray_fp_tee`, is additionally rebuilt against the real
provider's `Module.symvers` in this task; that acceptance result is recorded in
the authoritative reconstruction report.
