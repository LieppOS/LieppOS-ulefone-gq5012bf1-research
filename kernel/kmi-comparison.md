# GQ5012BF1 Kernel Module Interface Analysis

## Scope

This analysis compares the stock Ulefone Armor 29 Pro Thermal / GQ5012BF1
module ABI against the Nothing MT6878 source donor.

The stock runtime kernel is Linux 6.1.115 Android14-11 generation.

The Nothing MT6878 donor kernel source is Linux 6.1.68.

Nothing source is therefore treated as a source/BSP donor, not as a
binary-compatible kernel.

## Stock module ABI

The complete stock module population contains:

- module placements: 471
- distinct module binaries: 458
- unique module filenames: 457
- versioned import records: 26,111
- exported symbol records: 4,875

The 26,111 imports collapse to:

- unique imported symbols: 5,207
- unique symbol/CRC requirements: 5,207
- symbols with conflicting CRC requirements: 0

The absence of CRC conflicts indicates that the stock module population forms
one coherent CONFIG_MODVERSIONS ABI contract.

## Kernel versus inter-module ABI

The 5,207 requirements split into:

- kernel/builtin-provided symbols: 2,946
- symbols provided by another stock module: 2,261

Therefore 2,946 symbol/CRC pairs represent the complete stock kernel-facing
module ABI.

The remaining 2,261 belong to module-to-module ABI and must be considered
separately when replacing individual proprietary modules.

## Nothing KMI symbol-name coverage

Of the 2,946 stock kernel-facing requirements:

- present in Nothing published KMI lists: 2,913
- absent from inspected published KMI lists: 33

Published-list name coverage is therefore 98.88%.

Direct source inspection of the 33 list gaps found:

- explicitly exported by Nothing source: 32
- not exported by Nothing 6.1.68 source: 1

The sole exception is:

- cpu_busy_with_softirqs
  - stock CRC: 0x3c5aab9e
  - stock consumer: scheduler.ko
  - scheduler classification: LIKELY_PLATFORM_MATCH

Nothing's source contains cpu_busy_with_softirqs as a static scheduler helper,
but does not export it.

This is therefore a source-version delta affecting a replaceable platform
module rather than an irreplaceable Ulefone-specific binary.

## Hard Ulefone-only binary KMI

If DIRECT_SOURCE_MATCH and LIKELY_PLATFORM_MATCH modules are rebuilt, and only
the currently ULEFONE_ONLY binaries are retained, the required kernel-facing
ABI contracts reduce from 2,946 to:

- ULEFONE_ONLY requirements: 304

Of those 304:

- names present in Nothing published KMI lists: 289
- names outside those lists: 15
- unlisted names explicitly exported by Nothing source: 15
- demonstrated source-level symbol/export blockers: 0
- exact CRC matches currently proven: 0
- exact CRCs still requiring verification: 304

Thus every kernel symbol required by the currently ULEFONE_ONLY binary set has
a source-level implementation/export path in the Nothing donor.

This does not prove binary compatibility. CONFIG_MODVERSIONS requires the
generated symbol CRC to match the stock Ulefone CRC.

## Transitional binary KMI

Before the five NEEDS_ULEFONE_PORT modules are rebuilt:

- ULEFONE_ONLY requirements: 304
- NEEDS_ULEFONE_PORT requirements: 157
- overlap: 107
- combined transition target: 354

Therefore a staged kernel/module migration initially needs to preserve at most
354 kernel-facing symbol/CRC contracts for these two binary groups.

Once the five porting modules are source-built, this falls to 304.

## Ulefone-only KMI reduction

Of the 304 hard requirements:

- 172 are currently exclusive to one ULEFONE_ONLY module
- 132 are shared by two or more ULEFONE_ONLY modules

Immediate single-module exclusive reductions include:

| Module | Total KMI imports | Exclusive requirements |
|---|---:|---:|
| tkcore | 101 | 44 |
| yft_gpio_keys | 65 | 36 |
| panel_ky_vtdr6115_dphy_cmd | 38 | 19 |
| tkcore_drv | 54 | 16 |
| microarray_fp_tee | 59 | 13 |
| spi_tiny_co5300_lcd | 54 | 9 |
| yft_devinfo | 40 | 9 |
| hynitron | 51 | 7 |
| sc8571_charger | 41 | 5 |
| sh366003_fg | 33 | 5 |

The greedy kernel-KMI reduction sequence is:

1. tkcore: -44, 260 remaining
2. yft_gpio_keys: -37, 223 remaining
3. tkcore_drv: -31, 192 remaining
4. panel_ky_vtdr6115_dphy_cmd: -19, 173 remaining
5. microarray_fp_tee: -16, 157 remaining
6. hynitron: -19, 138 remaining
7. spi_tiny_co5300_lcd: -17, 121 remaining
8. yft_devinfo: -13, 108 remaining
9. sh366003_fg: -13, 95 remaining
10. sc8571_charger: -11, 84 remaining
11. sc851x_charger: -15, 69 remaining
12. leds_ln2403: -10, 59 remaining
13. yft_tpd_gesture: -10, 49 remaining
14. custom_ldo_wl2868: -15, 34 remaining
15. yft_tiny2c_usb: -16, 18 remaining
16. fingerprint: -17, 1 remaining
17. custom_ldo: -1, 0 remaining

This sequence optimizes only kernel-facing KMI reduction. It is not an
engineering-difficulty ranking.

## Current conclusion

Nothing MT6878 is a strong source donor for the GQ5012BF1.

At the symbol-name/export level:

- complete proprietary hard KMI coverage: 304 / 304
- known symbol/export blockers: 0

The unresolved compatibility question is exact CONFIG_MODVERSIONS CRC
equivalence.

The practical strategy remains:

1. retain the stock Ulefone GKI initially
2. progressively replace source-available vendor modules
3. reconstruct/port Ulefone-specific drivers
4. build a Linux 6.1.115 / Android14-11 compatible kernel
5. compare generated Module.symvers against the required stock CRC contract
6. retain binary modules only where source reconstruction remains incomplete

Module-to-module ABI dependencies must be analyzed before choosing the final
driver reconstruction order.
