# Hynitron device-tree contract

## PRESENT IN DT

Live path: `/sys/firmware/devicetree/base/soc/i2c@11c20000/hynitron@15`
(canonical DTS path `/soc/i2c@11c20000/hynitron@15`). Independent live-property
capture and three decompiled stock DT witnesses agree byte-for-byte:

```dts
hynitron@15 {
    compatible = "hynitron,hyn_ts";
    reg = <0x15>;
    clock-frequency = <400000>;
    interrupt-parent = <0x89>;
    interrupts = <11 2 11 0>;
    hynitron,reset-gpio = <0x89 32 0>;
    hynitron,irq-gpio = <0x89 11 0>;
    hynitron,vdd-gpio = <0x89 119 0>;
    hynitron,max-touch-number = <1>;
    hynitron,display-coords = <340 340>;
    status = "okay";
};
```

Phandle `0x89` is the MT6878 GPIO/EINT controller. Exact SoC GPIOs are:
IRQ GPIO 11, reset GPIO 32, VDD enable GPIO 119. All three GPIO specifier flags
are zero (active-high/logical polarity is not inverted by DT). Interrupt flag
cell `2` is `IRQ_TYPE_EDGE_FALLING`; the stock handler is therefore invoked on
the falling touch interrupt. The four-cell MediaTek specifier is preserved as
stock data rather than rewritten.

No pinctrl states, regulator supplies, touchscreen-size-x/y, swap/invert,
rotation, virtual-key, gesture, firmware-name, or wakeup-source property is
present on this node.

## ACTUALLY CONSUMED BY STOCK MODULE

The stock driver's OF table consumes `compatible`. I2C/OF core consumes `reg`,
`status`, `clock-frequency`, `interrupt-parent` and `interrupts`. Stock
`hyn_platform_data_init`/DT parsing contains exact string relocations for and
reads only:

- `hynitron,irq-gpio`
- `hynitron,reset-gpio`
- `hynitron,vdd-gpio`
- `hynitron,max-touch-number`
- `hynitron,display-coords`
- optional key properties `hynitron,have-key`, `hynitron,key-number`,
  `hynitron,key-y-coord`, `hynitron,key-code`, and historical literal
  `#hynitron,key-x-coord` (none are present here)

The stock driver does not call pinctrl, regulator, generic touchscreen-property,
or firmware request APIs. Consequently absent generic donor properties must not
be invented. On GQ5012BF1 the consumed values are one touch and raw/display
bounds 340 by 340, with optional key handling disabled by property absence.

## Evidence

- `qwen_hardware/qwen-thermal/evidence/local/dt/sys/firmware/devicetree/base/soc/i2c@11c20000/hynitron@15/`
- `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`
- `workspace/phase4-fingerprint/oracle/vendor_boot.entry0.dtb.dts`
- stock string and relocation inventories
