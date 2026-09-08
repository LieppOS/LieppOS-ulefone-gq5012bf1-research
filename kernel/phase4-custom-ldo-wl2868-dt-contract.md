# Device-tree contract

Recovered directly from the stock `.rodata`/relocations and probe strings:

```dts
wl2864c@29 {
        compatible = "will,wl2864c_pmu";
        reg = <0x29>;
        reset-gpios = <...>;
        vin1_en-gpios = <...>;
        /* vin2 is consumed as a GPIO number by wl2864c_vin2_power. */
};
```

- OF match table contains `will,wl2864c_pmu` and terminates with an empty entry.
- I2C ID table contains `wl2864c`; the driver name/string is also `wl2864c`.
- Probe requests GPIO consumers named exactly `reset` and `vin1_en` using `devm_gpiod_get` with output-high flags.
- `vin2` is not present as an additional named gpiod import: the stock path loads a GPIO integer from its global data and calls `gpio_to_desc`, then `gpiod_set_raw_value`.
- The stock `.rodata` contains misc name `wl2864c`; no regulator child-node contract was found.

The address 0x29 and bus 11 are board-level evidence from the frozen research tree; the module itself only encodes the driver/OF contract and does not encode the bus number.
