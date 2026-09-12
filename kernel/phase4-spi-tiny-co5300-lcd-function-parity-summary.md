# `spi_tiny_co5300_lcd` function/object/provider parity summary

## Functions

Stock and rebuild each contain exactly 25 functions, and the function-name sets
are identical. Every address-taken callback has the same KCFI type ID:

- module init/exit;
- SPI probe/remove;
- TE work and IRQ handlers;
- all five sysfs show/store pairs;
- native/compat ioctl;
- open/release.

Five direct-call helpers do not carry independent KCFI words in stock; the word
immediately before those symbols is an adjacent instruction and is not treated
as a type ID. See `phase4-spi-tiny-co5300-lcd-function-parity.tsv`.

## Objects

Stock has 64 symbolized objects and the rebuild 55. Forty-four names are shared.
Critical ABI/behavior objects are byte-identical, including `gImage_logo`,
`init_setting`, the SPI driver, file operations, misc device, dimensions,
status, OF table, delayed work, pinctrl pointers, and five driver attributes.

The count difference is explained by:

- stock compiler-generated `g_data.0` ... `g_data.13` fragments represented as
  one typed `g_data` structure in reconstructed source;
- compiler-generated unique-ID numbering;
- the rebuilt named SPI ID table used to emit stock alias `spi:SSD1317`.

None is exported. See `phase4-spi-tiny-co5300-lcd-object-parity.tsv`.

## Providers/imports

All 58 stock MODVERSION names and CRCs are reproduced exactly and the module
still exports zero symbols. Provider proof is in
`phase4-spi-tiny-co5300-lcd-provider-parity.tsv`; every row is `PASS`.

Fail-closed verification: **30/30 checks passed**.
