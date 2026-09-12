# `spi_tiny_co5300_lcd` fail-closed verifier

Run:

```sh
kernel/scripts/phase4_spi_tiny_co5300_lcd_verify_recon.py
```

Frozen result:

```text
30/30 CHECKS PASSED
```

The verifier checks stock/source/rebuild hashes, final artifact placement,
25-function name and applicable-KCFI parity, all 58 MODVERSION names/CRCs,
four exact vendor provider edges, zero exports, critical byte-identical
objects, all five driver attributes, module/OF identity, SPI frequencies,
geometry/frame sizes, controller IDs, all 11 ioctl values, TE work, power
sequencing, YFT/Hynitron calls, boot-mode gating, provider-symvers provenance,
absence of ABI fabrication, and the clean exact-GKI build log.

It is static by design. It does not load the module or operate live SPI, GPIO,
power, reset, IRQ, ioctl, sysfs, DT, flash, or reboot paths.
