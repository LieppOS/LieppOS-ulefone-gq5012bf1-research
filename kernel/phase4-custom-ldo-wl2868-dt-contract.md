# Device-tree contract — corrected closure version

Frozen merged board node:

```dts
pmu@wl2864c {
        compatible = "will,wl2864c_pmu";
        reg = <0x29>;
        id_reg = <0x00>;
        id_val = <0x01>;
        id_reg_2868c = <0x00>;
        id_val_2868c = <0x82>;
        reset-gpios = <... 0>; /* active high */
};
```

- OF table: `will,wl2864c_pmu`; I2C ID/driver/misc name: `wl2864c`.
- Probe requests consumer `vin1` first with `GPIOD_OUT_HIGH`. The board node has no `vin1-gpios`, and this lookup failure is non-fatal. The stock error text misleadingly says `vin1_en`.
- Probe then requests consumer `reset` with `GPIOD_OUT_HIGH`; the board supplies active-high `reset-gpios`.
- No VIN2 DT property is parsed. The global integer remains zero after probe.
- Stock parses none of the ID properties, performs no ID register read, forces `client->addr=0x2f`, and hardcodes software ID 0x82.
- The bus/address declaration remains 11/0x29 for device enumeration; the forced 0x2f is the operational transfer address.

No regulator child-node contract exists. Full evidence: `phase4-custom-ldo-wl2868-probe-contract.md`, `-gpio-contract.md`, and `-chip-variant-contract.md`.
