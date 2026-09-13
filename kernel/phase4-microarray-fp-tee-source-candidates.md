# MicroArray fingerprint TEE source candidates

## Search scope

Bounded exact-identifier searches covered local NothingOSS/MediaTek and other
kernel mirrors under `/home/armol`, GitHub/web indexes, Sourcegraph, and targeted
queries for all stock identifiers: `microarray_fp_tee`, `madev_finger`,
`madev0`, `mas_*`, `MAFP_`, the complete stock log strings, all seven provider
symbols, and `tee_spi_transfer`. Searches also covered older Android MicroArray
releases and the requested vendor families.

## Result

**NO_USEFUL_SOURCE** for the stock MT6878/TrustKernel module.

| candidate | classification | reason |
|---|---|---|
| Legacy `drivers/input/fingerprint/microarray/madev.c` described at cnblogs `cainyu/15045791` | STRUCTURAL_DONOR_ONLY | Qualcomm 3.18 integration description; no frozen source body; different DT (`microarray,fingerprint`), power, IRQ, controller and QSEE transport. |
| `wds204/kernel_sweet` `fs_tee/sf_ctl.c` | STRUCTURAL_DONOR_ONLY | Different Sunwave/Fortsense driver. It independently corroborates the five-argument `tee_spi_transfer(void *, int, const char *, char *, int)` call shape, but has different device/UAPI/lifecycle. |
| NothingOSS MT6878 Goodix `gf_spi_tee.c` | STRUCTURAL_DONOR_ONLY | Different sensor/vendor/UAPI. Useful only for the source prototype of MediaTek clock helpers. |
| `libfprint-microarray` USB project | SAME_SENSOR_VENDOR_DIFFERENT_TRANSPORT | USB userspace project for another MicroArray product; no stock kernel ABI match. |
| Stock `/vendor/lib64/libfprint-x64.so` and `microarray.fingerprint.default.so` | USERSPACE_ABI_EVIDENCE_ONLY | Exact fitted userspace binaries, not kernel source. |

No candidate reproduces the stock function set, `mediatek,madev_finger`, the
24-command accepted ioctl set (including its holes), the mixed normal-world SPI
and TrustKernel initialization path, or the exact lifecycle. No non-TEE SPI
driver is promoted to exact source.

## Provenance decision (historical pre-`spi-mt65xx` closure)

The original clean-room stock-oracle reconstruction used the frozen ELF,
relocation-aware disassembly, exact userspace binaries, frozen DT, frozen
`fingerprint` source-built provider, a stock `spi-mt65xx` witness, and a stock
`tkcore` witness as evidence inputs.

**Superseding acceptance provenance:** MicroArray behavior was not reopened.
The two SPI edges now come naturally from the source-built direct-match
`spi-mt65xx` provider; only `tee_spi_transfer` remains a stock-runtime witness
from unreconstructed `tkcore`. Current split: 65/66 natural, 1/66 stock-runtime
witness.
