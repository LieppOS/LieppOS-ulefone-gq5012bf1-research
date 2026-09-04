# Exact Android GKI CRC comparison

Baseline:

- Android Common tag: `android14-6.1-2024-12_r4`
- common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
- Android CI target: `kernel_aarch64`
- Android CI build: `12901745`
- Linux version: `6.1.115`
- vmlinux.symvers symbols: 7993

## FULL STOCK KERNEL ABI

- requirements: 2946
- exact CRC matches: 2946
- CRC mismatches: 0
- missing symbols: 0

## TRANSITION BINARY ABI

- requirements: 354
- exact CRC matches: 354
- CRC mismatches: 0
- missing symbols: 0

## HARD ULEFONE-ONLY ABI

- requirements: 304
- exact CRC matches: 304
- CRC mismatches: 0
- missing symbols: 0

## Interpretation

A MATCH means both the symbol name and CONFIG_MODVERSIONS CRC
required by the stock Ulefone module agree with Google's exact
GKI build 12901745.

A MISMATCH means the symbol exists in the exact GKI but its
generated ABI CRC differs.

A MISSING result means the symbol is not present in that
vmlinux.symvers export table.
