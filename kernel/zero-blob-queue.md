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

- `tkcore` — **NO_PUBLIC_SOURCE_FOUND / PROVIDER_ABI_PARTIAL — NOT
  RECONSTRUCTED**; stock oracle frozen and fully inventoried (122 functions,
  25 exports, 101 MODVERSIONs, 3098 relocations); **14/25 export CRCs +
  KCFI type ids naturally regenerated** against exact GKI 12901745 by
  `//lieppos/tkcore-recon` (build-only ABI witness, never loadable);
  **11/25 declared `PROVIDER_ABI_BLOCKED`** because their genksyms CRCs expand
  TrustKernel's private `struct tee` / `struct tee_context` member names, which
  exist in no binary and no public source; 36/36 fail-closed verifier.
  See `kernel/phase4-tkcore-provider-abi.md`,
  `kernel/phase4-tkcore-stock-inventory.md`,
  `kernel/phase4-tkcore-source-candidates.md`.

## Active remaining queue

- `tkcore` — blocked on original TrustKernel headers only (no further binary
  analysis can unblock it); stays a stock vendor binary meanwhile
- `tkcore_drv`
- connectivity and panel/provider work per remaining-module triage

Do not reopen frozen targets. Hynitron's stock provider remains stock
`yft_devinfo`; this queue does not mark yft_devinfo reconstructed.

`microarray_fp_tee` being frozen does **not** mark `spi-mt65xx` or `tkcore` as
reconstructed or source-pure. Those remain stock vendor binaries; only their
published export CRCs were read out of the shipped ELFs so the consumer can
link against them. Source purity of the consumer is a separate question from
source purity of those providers.

The `tkcore` work above upgrades one of those edges: `tee_spi_transfer` is no
longer "read out of the shipped ELF" — its prototype is now confirmed by the
stock KCFI type id `0xffeb18b3` and its CRC `0x184ce7da` is regenerated
naturally from C. The other 10 `tkcore_drv` / 4 `tmem_ffa` blocked edges are
not, and `tkcore` itself remains stock.
