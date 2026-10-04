# FT3680 device-tree contract

## Evidence

The authoritative node is the merged stock base FDT, not a donor DTS:

- merged source: `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`
- focused verbatim extract: `workspace/phase4-focaltech-ft3680/gq5012bf1-touchscreen-dt-window.dts`
- the stock DTBO has no FocalTech/touch/SPI3 node; the contract comes from the `vendor_boot` base FDT
- the live-tree snapshot contains the same `/soc/spi3@11013000/focaltech@39` node

## Exact node

| property | stock value | resolved meaning |
|---|---:|---|
| path | `/soc/spi3@11013000/focaltech@39` | child of MediaTek SPI3 |
| `compatible` | `"focaltech,fts"` | matches both module OF aliases |
| `reg` | `<0>` | chip select 0; `@39` is only the node name |
| `status` | `"ok"` | enabled |
| `spi-max-frequency` | `<0x5b8d80>` | 6,000,000 Hz |
| `interrupt-parent` | `<0x89>` | SoC pinctrl/EINT controller |
| `interrupts` | `<7 2 7 0>` | GPIO/EINT 7, falling edge |
| `focaltech,irq-gpio` | `<0x89 7 0>` | GPIO 7 |
| `focaltech,reset-gpio` | `<0x89 6 0>` | GPIO 6, active-high encoding |
| `vddi-gpio` | `<0x89 183 0>` | GPIO 183, active-high encoding |
| `vdd-supply` | `<0xd8>` | `mt6369_vtp`, fixed 3.3 V |
| `focaltech,max-touch-number` | `<10>` | ten MT-B slots |
| `focaltech,display-coords` | `<0 0 1080 2400>` | report range |
| `lcminfo` | `<0xad>` | resolves to `/chosen`; not consumed by any stock FT3680 function |

The regulator node fixes VDD at 3,300,000 µV and specifies a 680 µs enable ramp. There is no `iovcc-supply`; the optional `regulator_get(dev, "iovcc")` therefore follows the invalid/absent path. IO power is controlled by `vddi-gpio` instead.

## SPI controller

Parent `/soc/spi3@11013000` is `mediatek,mt6989-spi` at `0x11013000`, with `mediatek,pad-select=<0>`, `mediatek,tickdly=<2 0>`, and `clock-source-type="univpll"`. The child supplies CS 0 and 6 MHz. The stock probe additionally sets:

- `spi->mode = SPI_MODE_0` (CPOL=0, CPHA=0)
- `bits_per_word = 8`
- protocol header 6 bytes, 3 dummy bytes, 4096-byte frame maximum, three retries and 150 µs CS-high delay

## IRQ contract

`fts_irq_registration()` converts GPIO 7 with `gpio_to_irq()` and requests a threaded IRQ with:

```c
IRQF_TRIGGER_FALLING | IRQF_ONESHOT
```

The DT trigger and driver flags therefore agree. Gesture suspend calls `enable_irq_wake(irq)`; resume calls `disable_irq_wake(irq)`.

## Parsed-but-absent properties

The driver supports, but this device does not provide, `focaltech,have-key`, key arrays/coordinates, `iovcc-supply`, and any firmware/panel/vendor/config selector. There are no `pinctrl-names` or `pinctrl-N` properties on the touch node, and the shipped module imports no pinctrl API.

## Panel relationship

There is no usable panel phandle in this node. `lcminfo` points to `/chosen` and the module never reads it. Panel state reaches touch through `mtk_disp_notify`, registered under the exact source label `Touch_fts`; this software notifier, not a DT panel link, drives suspend/resume.
