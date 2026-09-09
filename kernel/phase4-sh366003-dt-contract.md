# SH366003 device-tree contract

## Exact live node

```dts
soc {
    i2c@11c24000 {
        sh366003@55 {
            compatible = "sh,sh366003";
            reg = <0x55>;
            status = "okay";
            clock-frequency = <400000>;
        };
    };
};
```

Live path: `/sys/firmware/devicetree/base/soc/i2c@11c24000/sh366003@55`

Live device: `/sys/bus/i2c/devices/9-0055`

## Consumed properties

The module imports no OF property-reading helpers. Probe consumes no child-node property directly; matching is through the OF table only. Consequently the exact consumed child contract is:

| Property | Value | Consumer |
|---|---:|---|
| `compatible` | `sh,sh366003` | I2C/OF core match |
| `reg` | `0x55` | I2C core client creation |
| `status` | `okay` | OF core |
| `clock-frequency` | 400000 | parent/controller setup, not parsed by this driver |

There is no stock evidence for interrupts, GPIOs, design capacity, design voltage, termination voltage, sense resistor, model, battery ID, firmware filename, AFI filename, profile filename, update-enable property, temperature threshold, or polling interval in the SH366003 node. None are invented.

## Global boot-mode lookup

The one DT read in driver code is not from the SH366003 node. Update work searches `/chosen`, then `/chosen@0`, reads `atag,boot`, and uses the boot-mode word at byte offset 8. AFI programming is skipped for boot modes 8 and 9. The frozen live property is 16 bytes:

`10000000020800410000000002000000`

which records boot mode 0 and boot type 2 in the fields consumed by stock.
