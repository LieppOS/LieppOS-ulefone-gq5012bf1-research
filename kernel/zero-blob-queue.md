# ZERO-BLOB stock-oracle queue

## Frozen/source-ready

- `yft_gpio_keys` — FROZEN FOR RE
- `leds_ln2403` — FROZEN FOR RE
- `yft_tiny2c_usb` — FROZEN FOR RE
- `hynitron` — **STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE**;
  SOURCE_RECONSTRUCTED; SOURCE_NOW; FROZEN FOR RE; 34/34 verifier; stock
  `yft_devinfo` provider ABI pinned; both `spi_tiny_co5300_lcd` consumer edges
  READY/EXACT
- `spi_tiny_co5300_lcd` — **NO_PUBLIC_SOURCE_FOUND /
  STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE**; SOURCE_RECONSTRUCTED; SOURCE_NOW;
  FROZEN FOR RE; exact 25-function/58-MODVERSION sets; exact rebuilt-Hynitron
  and stock-YFT provider edges; 30/30 verifier

## Active remaining queue

- `microarray_fp_tee`
- `tkcore`
- `tkcore_drv`
- connectivity and panel/provider work per remaining-module triage

Do not reopen frozen targets. Hynitron's stock provider remains stock
`yft_devinfo`; this queue does not mark yft_devinfo reconstructed.
