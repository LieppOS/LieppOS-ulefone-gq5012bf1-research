# YFT GPIO keys source candidates

## Exact-GKI donor (STRONG_SOURCE_MATCH)

- Path: `/home/armol/kernel-work/gki-12901745-workspace/common/drivers/input/keyboard/gpio_keys.c`
- Common commit: `6b18f0b574ab3267615ae6ce642d5a7c3c21ac09`
- SHA-256: `22b787ef4dcd0bfb1fa3b5c693baf793da69642f604b0d1f82188e1b2bfd4b79`
- Related public ABI header: `common/include/linux/gpio_keys.h`.
- Related DT binding header: `common/include/dt-bindings/input/gpio-keys.h`.
- Exact-GKI assumptions evidenced by the stock/rebuild objects: AArch64, Clang 17 Android toolchain, CFI/KCFI, MODVERSIONS, OF, GPIOLIB, input, hrtimer/workqueue, PM sleep and sysfs support.

This donor is not merely structurally similar. The untouched build has the exact 23-function set, all 23 function sizes and all KCFI IDs. Reapplying the recovered seven-line/identity delta makes all 23 function byte ranges, `.text`, `.init.text`, `.exit.text`, `.data`, `.rodata`, `.rodata.str1.1` and `__versions` byte-identical to stock.

## Search results

Searches covered `yft_gpio_keys`, `yft-gpio-keys`, Ulefone programmable GPIO keys, MediaTek/YFT GPIO keys, F1/F2, Linux codes 59/60 and `0x3b/0x3c`, across GitHub/web results and the local Nothing/MediaTek/Motorola/MiCode/OnePlus/OPPO/realme/Transsion/Sony/Ulefone corpora already present in the project.

| Candidate | Classification | Result |
|---|---|---|
| Exact pinned Android common `gpio_keys.c` | STRONG_SOURCE_MATCH | Behavioral base and compiler-shape match; exact YFT delta recovered from ELF. |
| Current/upstream Linux `drivers/input/keyboard/gpio_keys.c` | SAME_FRAMEWORK_DIFFERENT_BOARD | Framework lineage only unless pinned to this baseline. |
| Generic vendor BSP copies of `gpio_keys.c` | STRUCTURAL_DONOR_ONLY | No GQ5012BF1 identity/delta proof. |
| Public file named `yft_gpio_keys.c` | NO_USEFUL_SOURCE | No independently verifiable public exact source found in the performed searches. |

## Conclusion

There is no need to trust an unverified public vendor drop. The frozen stock ELF proves that the pinned exact-GKI donor plus the delta documented in `phase4-yft-gpio-keys-yft-delta.md` reconstructs the stock implementation exactly at every function byte range.
