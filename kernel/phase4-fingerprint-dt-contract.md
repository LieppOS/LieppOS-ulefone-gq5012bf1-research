# `fingerprint.ko` device-tree contract

## Exact merged node

The vendor_boot DT table has one FDT entry. Its merged node is exactly:

```text
/yft_finger
```

```dts
yft_finger {
    compatible = "mediatek,yft_finger";
    pinctrl-names = "default", "finger_reset_en0", "finger_reset_en1",
        "finger_power_en0", "finger_power_en1",
        "finger_spi0_mi_as_spi0_mi", "finger_spi0_mi_as_gpio",
        "finger_spi0_mo_as_spi0_mo", "finger_spi0_mo_as_gpio",
        "finger_spi0_clk_as_spi0_clk", "finger_spi0_clk_as_gpio",
        "finger_spi0_cs_as_spi0_cs", "finger_spi0_cs_as_gpio",
        "finger_eint_pull_down", "finger_eint_pull_up", "finger_eint_pull_dis";
    pinctrl-0 = <0x8a>;  pinctrl-1 = <0x8b>;  pinctrl-2 = <0x8c>;
    pinctrl-3 = <0x8d>;  pinctrl-4 = <0x8e>;  pinctrl-5 = <0x8f>;
    pinctrl-6 = <0x90>;  pinctrl-7 = <0x91>;  pinctrl-8 = <0x92>;
    pinctrl-9 = <0x93>;  pinctrl-10 = <0x94>; pinctrl-11 = <0x95>;
    pinctrl-12 = <0x96>; pinctrl-13 = <0x97>; pinctrl-14 = <0x98>;
    pinctrl-15 = <0x99>;
    reset-gpio = <0x89 0x1e 0x00>;
    int-gpio = <0x89 0x03 0x00>;
    interrupt-parent = <0x89>;
    interrupts = <0x03 0x01 0x03 0x00>;
    debounce = <0x03 0x00>;
    status = "okay";
};
```

Phandle `0x89` is `/soc/pinctrl`, compatible
`mediatek,mt6878-pinctrl`, and is both GPIO and interrupt controller.

## Properties directly consumed by this module

| property | consumer |
|---|---|
| `compatible` | platform OF match and every global node lookup |
| `pinctrl-names` / `pinctrl-1,2,5..15` | pinctrl core plus the 13 named state lookups |
| `reset-gpio` | `yft_finger_get_reset_gpio()` only |
| `int-gpio` | `yft_finger_get_irq_gpio()` only |
| `interrupt-parent`, first `interrupts` specifier | `yft_finger_get_irqnum()` through `irq_of_parse_and_map(node, 0)` |
| `status` | platform core binding |

The first interrupt specifier is GPIO/EINT 3 with raw type value 1
(`IRQ_TYPE_EDGE_RISING`). The module asks only for index 0; it never requests
or handles the IRQ itself.

## Present but not directly parsed by this module

- `default` is an empty pinctrl state; there is no explicit lookup/select.
- `finger_power_en0` and `finger_power_en1` are empty states. Despite matching
  global pointer names, stock code never looks them up and explicitly logs
  that GPIO power is unnecessary.
- `debounce = <3 0>` is present but never read by `fingerprint.ko`.
- The second two-cell interrupt specifier `<3 0>` is present but unused by
  `irq_of_parse_and_map(..., 0)`.

No regulator, clock, `wakeup-source`, CS-number, supply, or YFT-specific scalar
property is read. There is no DT allocation or cached GPIO/IRQ field.

## GPIO meaning

- `reset-gpio`: MT6878 GPIO 30, flags 0.
- `int-gpio`: MT6878 GPIO 3, flags 0.

These values are exposed by getter exports only. Reset and IRQ configuration in
the setters is performed through pinctrl states, not GPIO direction/value APIs.

## Evidence

- DT table container: `workspace/phase4-fingerprint/oracle/vendor_boot.dtb.stock`
- extracted FDT: `workspace/phase4-fingerprint/oracle/vendor_boot.entry0.dtb.stock`
- decompiled merged DTS: `workspace/phase4-fingerprint/oracle/vendor_boot.entry0.dtb.dts`
- YFT node: DTS lines 3130-3156
- pinctrl state nodes: DTS lines 3939-4091
