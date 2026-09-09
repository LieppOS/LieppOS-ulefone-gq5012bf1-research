# Hardware contract — closure summary

- Family: Will Semiconductor WL2864C/WL2868C-compatible seven-output camera PMU.
- Board enumeration: I2C bus 11, DT address 0x29, compatible `will,wl2864c_pmu`, live-bound as `11-0029` in the frozen snapshot.
- Operational stock behavior: probe overwrites `client->addr` with 0x2f and all raw `i2c_transfer` messages use that mutated address.
- Probe does not read identity register 0x00. It hardcodes software dispatch byte 0x82. The DT declares ID metadata 0x01/0x82, which supports WL2868C board intent but is not a physical-die read.
- VOUT registers are 0x03–0x09; enable is 0x0e.
- Stock uses raw I2C, exported `will_ldo_vout`/`will_ldo_en`, and a misc character device—not regmap or Linux regulator children.
- GPIO consumers are optional `vin1` and required `reset`; the misleading log calls `vin1` `vin1_en`. A separate zero-default integer VIN2 path uses `gpio_to_desc` and `gpiod_set_raw_value` without ownership.

Authoritative contracts: `phase4-custom-ldo-wl2868-{probe,gpio,chip-variant,voltage,enable,i2c,lifecycle}-contract.md`. No live hardware operation was performed.
