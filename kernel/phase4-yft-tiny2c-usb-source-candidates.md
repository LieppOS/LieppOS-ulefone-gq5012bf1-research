# yft_tiny2c_usb source candidates

## Result

**`NO_USEFUL_SOURCE`**

**`NO_PUBLIC_DONOR_FOUND`**

No public or local kernel implementation can be built and then compared as the target.
The reconstruction therefore starts from the explicit empty-source RED and uses the stock
ELF as oracle.

## Bounded exact-identifier search

Searches were performed for:

- identity/binding: `yft_tiny2c_usb`, `yft-tiny2c-usb`,
  `mediatek,yft_tiny2c_usb`, `mediatek,tiny2c_usb`, `tiny2c_usb-sensor`;
- functions: `tiny2c_usb_power_init`, `tiny2c_usb_mode_show`,
  `tiny2c_usb_mode_store`, `tiny2c_usb_i2c_read`, `tiny2c_usb_read_chipid`,
  `tiny2c_usb_i2c_probe`, `tiny2c_usb_parse_dts`;
- ABI/DT: `tiny2c_usb_mode`, `sensor_id`, `tiny2c_usb_vdd_1v8`,
  `tiny2c_usb_vdd_3v3`, `tiny2c_usb_vdd_5v`, `tiny2c_usb_vddio_3v3`,
  `yft_usb_flag`;
- exact metadata/logs: `Module For tiny2c_usb`, `yft-drv`,
  `gpio_1v8=%d,gpio_3v3=%d,gpio_5v=%d,gpio_io3v3:%d`,
  `read sensor-id fail`;
- broader context: `ThermoVue`, `Ulefone thermal USB`, `YFT thermal camera`,
  `mt6375 thermal camera`, `mt6375 otg tiny2c`, `tiny2c USB mode`.

Local search covered the research repository, exact-GKI workspace, local
`kernel-research/nothing-mt6878`, device/vendor trees and prior extracted-source evidence.
Public search covered general web/code indexes plus GitHub/Gitee-focused queries and the
named NothingOSS, MediaTek BSP, Motorola, MiCode, OnePlus, OPPO/realme, Transsion, Sony and
Ulefone/YFT namespaces. Exact identifiers returned no implementation.

## Candidate classification

| candidate | class | disposition |
|---|---|---|
| local Nothing/MediaTek `drivers/power/supply/mt6375-charger.c` | `SAME_FRAMEWORK_DIFFERENT_BOARD` | provider framework only; lacks Ulefone `yft_usb_flag` delta and is not this leaf driver |
| stock `extcon-mtk-usb.ko` plus available MediaTek extcon sources | `STRUCTURAL_DONOR_ONLY` | owns paired USB role/mux ABI, not thermal rail/I2C driver |
| Raytron Tiny2-C public product/datasheet results | `SAME_NAME_HARDWARE_CONTEXT` | hardware/product material, no Linux driver; cannot establish fitted GQ5012BF1 silicon by itself |
| generic `i2c-tiny-usb` and TinyUSB projects | `UNRELATED` | USB-to-I2C firmware or generic USB stack; naming collision only |
| local decompiled `GPIOUtils`/FactoryMode classes | `EXACT_USERSPACE_CLIENT` | proves ABI usage, not kernel source |
| stock ELF `yft_tiny2c_usb.ko` | `STOCK_BINARY_ORACLE` | authoritative reconstruction input |

No `EXACT_SOURCE` or `STRONG_SOURCE_MATCH` kernel candidate was found. Public source
availability is therefore not used as completion evidence; all final claims require oracle
comparison and exact-GKI verification.
