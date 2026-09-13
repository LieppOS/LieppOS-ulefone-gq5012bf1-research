# GQ5012BF1 `spi-mt65xx` DT contract

Source: offline decompilation of the committed stock vendor_boot DTB,
`workspace/phase4-fingerprint/oracle/vendor_boot.entry0.dtb.dts`. No DT/DTBO
was modified and no live-device action was performed.

## Controller generation

GQ5012BF1/MT6878 exposes eight controller nodes at `0x11010000` through
`0x11017000`. All bind with **`mediatek,mt6989-spi`**, selecting the exact
source's `mt6989_compat` row—not an inferred `mediatek,mt6878-spi` row (none is
present).

Common properties on every node:

- register aperture: 0x100 bytes
- one SPI interrupt, level-high encoding (`... 0x04 0x00`)
- three clocks named exactly `parent-clk`, `sel-clk`, `spi-clk`
- one `mediatek,pad-select = <0>` value (therefore one chip-select)
- `mediatek,tickdly = <pad0 delay>`
- no `dmas`/`dma-names`: this driver performs streaming DMA mappings and writes
  bus addresses directly to controller registers, not a DT DMA-engine channel
- no controller `power-domains`, assigned clocks/rates, or explicit
  `mediatek,autosuspend-delay` in the merged stock DT; source default is 10 ms

| controller | base | SPI IRQ cell | clock source | tickdly | active child / role |
|---|---:|---:|---|---|---|
| `spi0` | `0x11010000` | `0x1cb` | `mainpll` | `<3 0>` | `spi_tiny_lcd@0`, rear mini-display; explicit `status="okay"`; controller pinctrl state list present |
| `spi1` | `0x11011000` | `0x1cc` | `univpll` | `<2 0>` | `fingerprint@0`, MicroArray TEE fingerprint |
| `spi2` | `0x11012000` | `0x1cd` | `univpll` | `<2 0>` | no child in merged DT |
| `spi3` | `0x11013000` | `0x1ce` | `univpll` | `<2 0>` | `focaltech@39`, main touch (`reg=<0>`) |
| `spi4` | `0x11014000` | `0x1cf` | `univpll` | `<3 0>` | no child in merged DT |
| `spi5` | `0x11015000` | `0x1d0` | `univpll` | `<2 0>` | no child in merged DT |
| `spi6` | `0x11016000` | `0x1d1` | `univpll` | `<2 0>` | no child in merged DT |
| `spi7` | `0x11017000` | `0x1d2` | `univpll` | `<2 0>` | no child in merged DT |

Nodes lacking `status` use DT's default enabled status; the table does not
invent unavailable runtime-use claims for childless controllers.

## SPI1 / MicroArray hard contract

```
spi1@11011000 {
    compatible = "mediatek,mt6989-spi";
    mediatek,pad-select = <0>;
    mediatek,tickdly = <2 0>;
    reg = <0 0x11011000 0 0x100>;
    interrupts = <0 0x1cc 4 0>;
    clocks = <...parent... ...selector... ...spi...>;
    clock-names = "parent-clk", "sel-clk", "spi-clk";
    clock-source-type = "univpll";
    tee-only;
    #address-cells = <1>;
    #size-cells = <0>;
    cs-gpios = <&pinctrl 61 0>;

    fingerprint@0 {
        compatible = "mediatek,madev_finger";
        vfp-supply = <...>;
        reg = <0>;
        spi-max-frequency = <8000000>;
        status = "okay";
    };
};
```

`tee-only` causes probe to leave `spi_controller.set_cs` unset. SPI core/GPIO
CS handling therefore owns SPI1's `cs-gpios`; the controller's vendor software
CS callback is not installed for this TEE path. The driver still installs
prepare/transfer/setup/cleanup/timing callbacks and runtime PM.

## Source enforcement

Probe requires all three named clocks, sets `sel-clk`'s parent to `parent-clk`,
reads the effective `spi-clk` rate, verifies `pad_num == num_chipselect`, and
rejects pad-select values above 3. For MT6989, it sets a 36-bit DMA mask and a
16 MiB maximum segment size.
