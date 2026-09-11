# ZERO-BLOB stock-oracle queue

## Frozen/source-ready

- `yft_gpio_keys` — FROZEN FOR RE
- `leds_ln2403` — FROZEN FOR RE
- `yft_tiny2c_usb` — FROZEN FOR RE
- `hynitron` — **STOCK_BEHAVIORAL_RECONSTRUCTION_COMPLETE**;
  SOURCE_RECONSTRUCTED; SOURCE_NOW; FROZEN FOR RE; 34/34 verifier; stock
  `yft_devinfo` provider ABI pinned; both `spi_tiny_co5300_lcd` consumer edges
  READY/EXACT

## Active remaining queue

- `spi_tiny_co5300_lcd` — next rear-display consumer; not done
- `microarray_fp_tee`
- `tkcore`
- `tkcore_drv`
- connectivity and panel/provider work per remaining-module triage

Do not reopen frozen targets. Hynitron's stock provider remains stock
`yft_devinfo`; this queue does not mark yft_devinfo reconstructed.
