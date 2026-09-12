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
- `microarray_fp_tee` — **NO_USEFUL_SOURCE / EMPTY-SOURCE RED /
  BEHAVIORALLY-COMPLETE, LOAD-COMPATIBLE, WITH DECLARED ABI PROVENANCE SPLIT**;
  FROZEN FOR RE; 27/27 functions; complete ioctl/UAPI/TEE/DT closure;
  **63/66 MODVERSION edges naturally regenerated, 3/66 inherited from real
  stock provider ABI witnesses (`mt_spi_enable_master_clk`,
  `mt_spi_disable_master_clk`, `tee_spi_transfer`), stock-compatible target
  66/66 exact**; `fingerprint` edges use the real source-built provider
  `Module.symvers`

## Active remaining queue

- `tkcore`
- `tkcore_drv`
- connectivity and panel/provider work per remaining-module triage

Do not reopen frozen targets. Hynitron's stock provider remains stock
`yft_devinfo`; this queue does not mark yft_devinfo reconstructed.

`microarray_fp_tee` being frozen does **not** mark `spi-mt65xx` or `tkcore` as
reconstructed or source-pure. Those remain stock vendor binaries; only their
published export CRCs were read out of the shipped ELFs so the consumer can
link against them. Source purity of the consumer is a separate question from
source purity of those providers.
