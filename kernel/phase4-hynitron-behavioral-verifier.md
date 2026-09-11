# Hynitron fail-closed behavioral verifier

Verifier: `kernel/scripts/phase4_hynitron_verify_recon.py`

Final offline result:

```text
34/34 CHECKS PASSED
```

The verifier checks the frozen stock hash, pinned reconstruction-source hash,
65-function set, applicable KCFI IDs, exact 54-entry MODVERSION/import map,
three stock `yft_devinfo` provider edges, both exported names/CRCs/KCFI types,
stock `spi_tiny_co5300_lcd.ko` consumer acceptance, OF/I2C/GPIO/IRQ identity,
CST820 detection and touch decoding, input/gesture/power/YFT behavior, both
embedded firmware hashes and byte content, update-selection logic, default-off
firmware-programming gate, sysfs/PM/lifecycle evidence, and successful
exact-GKI build with no compiler or modpost warning.

It exits nonzero on the first failed invariant. No check patches an ELF,
`__versions`, CRC, or consumer module.
