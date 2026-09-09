# Voltage and enable contracts — superseded summary

This historical combined note is superseded by the closed authoritative contracts:

- `phase4-custom-ldo-wl2868-voltage-contract.md`
- `phase4-custom-ldo-wl2868-enable-contract.md`
- `phase4-custom-ldo-wl2868-reconstruction.md`

The stock-proven input unit is microvolts. WL2864C uses divisors/bases corresponding to 12,500 uV steps (600,000 uV for channels 1–2; 1,200,000 uV for channels 3–7). WL2868C uses 8,000 uV steps (496,000 uV for channels 1–2; 1,504,000 uV for channels 3–7). Stock uses factor-ten-low zero thresholds, no upper clamp, and u8 truncation/wrap; see the full table for exact arithmetic.

Enable is a register-0x0e read-modify-write, channel N → bit N−1. On WL2868C, after changing the selected bit stock writes zero only if the entire intermediate byte is zero; otherwise it ORs bit 7. A previously read bit 7 can therefore remain set after the final low bit is cleared.

Probe requests optional consumer `vin1`, then pulses `reset` logical 1→0→1 with a 10–11 ms delay after every level, then sleeps 1 ms. It performs no I2C identity read or default register write, forces client address 0x2f, and stores software ID 0x82. These findings are static/offline only.
