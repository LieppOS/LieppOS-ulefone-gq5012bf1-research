# Exact GQ5012BF1 GKI Binary Identity

The stock Ulefone GQ5012BF1 boot kernel was compared against Android CI
`kernel_aarch64` build 12901745.

## Provenance

- Android Common tag: `android14-6.1-2024-12_r4`
- kernel/common commit:
  `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
- CI build: `12901745`
- target: `kernel_aarch64`
- Linux: `6.1.115`

## Compressed kernel identity

Stock boot.img kernel:

- size: 16,498,955 bytes
- format: LZ4
- SHA256:
  `1f2a9e9b1c1d2533ca649a472c29df42b029b63dac677c5d439a358ede67e722`

Google `Image.lz4`:

- size: 16,498,955 bytes
- format: LZ4
- SHA256:
  `1f2a9e9b1c1d2533ca649a472c29df42b029b63dac677c5d439a358ede67e722`

Direct `cmp` result:

`BIT-FOR-BIT IDENTICAL`

## Raw kernel identity

Both the Ulefone stock boot kernel and Google Image.lz4 were decompressed.

Google raw Image:

`3d435e01db1063d7d7ab60a25a06dc2a60b97512f3d582d751e79b2c06b7f873`

Google Image.lz4 decompressed:

`3d435e01db1063d7d7ab60a25a06dc2a60b97512f3d582d751e79b2c06b7f873`

Ulefone boot kernel decompressed:

`3d435e01db1063d7d7ab60a25a06dc2a60b97512f3d582d751e79b2c06b7f873`

All raw Images are byte-identical.

## ABI identity

Comparison against official build 12901745 `vmlinux.symvers`:

- complete stock kernel-facing ABI: 2,946 / 2,946 exact CRC matches
- transition binary ABI: 354 / 354 exact CRC matches
- hard ULEFONE_ONLY ABI: 304 / 304 exact CRC matches
- CRC mismatches: 0
- missing symbols: 0

## Conclusion

The GQ5012BF1 stock firmware ships Google's exact published GKI kernel binary
from Android CI build 12901745.

The device-specific kernel functionality therefore resides outside the GKI
core, primarily in vendor/device modules, DT/DTBO, vendor_boot integration and
Ulefone-specific peripheral drivers.

LieppOS kernel development should use this exact Android Common revision as the
kernel-core baseline and treat Nothing MT6878 sources as BSP/vendor-driver
source donors.
