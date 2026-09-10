# GQ5012BF1 yft_gpio_keys DT contract

Oracle: decompiled `vendor_boot` entry-0 DTB, lines 3110-3128 of `workspace/phase4-fingerprint/oracle/vendor_boot.entry0.dtb.dts`.

## Present in DT

Exact path: `/yft-gpio-keys`

```dts
yft-gpio-keys {
    compatible = "yft-gpio-keys";
    key-custom1 {
        label = "customkeyf1";
        linux,code = <0x3b>;
        gpios = <&pio 13 GPIO_ACTIVE_LOW>;
        debounce-interval = <16>;
        wakeup-source;
    };
    key-custom2 {
        label = "customkeyf2";
        linux,code = <0x3c>;
        gpios = <&pio 8 GPIO_ACTIVE_LOW>;
        debounce-interval = <16>;
        wakeup-source;
    };
};
```

The decompiler represents `&pio` as phandle `0x89` and `GPIO_ACTIVE_LOW` as flag `0x01`. `status` is absent, hence OF default available/enabled. No parent `label`, `autorepeat`, `pinctrl-*`, interrupt properties or custom YFT properties are present. No child `linux,input-type`, `wakeup-event-action` or `linux,can-disable` is present.

## Actually consumed by stock

Relocations/strings/disassembly and byte-identical reconstruction prove consumption of:

- parent: `compatible`, child count, optional `autorepeat`, optional `label`;
- child: `linux,code`, `label`, `linux,input-type`, GPIO specifier, `wakeup-source`/legacy `gpio-key,wakeup`, `wakeup-event-action`, `linux,can-disable`, `debounce-interval`;
- GPIO polarity through the descriptor and `gpiod_is_active_low()`.

For this DT: two children; EV_KEY default; no autorepeat; no can-disable; wakeup true; wakeup action defaults EV_ACT_ANY; debounce exactly 16 ms; IRQ obtained from each GPIO descriptor with `gpiod_to_irq()`.

The driver supports the listed generic optional properties because the exact stock code reads them. It does not consume any additional YFT-specific DT property. Parent/child `status` and pinctrl are OF/core concerns, not explicitly parsed by this module.
