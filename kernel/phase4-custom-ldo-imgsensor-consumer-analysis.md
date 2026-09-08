# Stock `imgsensor.ko` consumer analysis for `custom_ldo`

## Oracle and scope

* Stock module: `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/imgsensor.ko`
* SHA-256: `9243061cec77e96e3072b19f14a4d0f893e768586585830fa86f0a5129ce3558`
* Analysis was static and offline. `imgsensor` was not reconstructed or run.
* Raw bounded call-site evidence:
  `workspace/phase4-custom-ldo/imgsensor-custom-ldo-callsites.txt`.

## Every static call site — PROVEN_FROM_STOCK

There are exactly four relocations in stock `imgsensor.ko`:

| owner | offset | target | arguments at call |
|---|---:|---|---|
| `set_custom_ldo` | `.text+0x2078` | `custom_ldo_vout` | `w0 = custom channel`, `w1 = incoming power-sequence value` |
| `set_custom_ldo` | `.text+0x2094` | `custom_ldo_en` | `w0 = same custom channel`, `w1 = 1` |
| `unset_custom_ldo` | `.text+0x21b4` | `custom_ldo_vout` | `w0 = custom channel`, `w1 = incoming power-sequence value` |
| `unset_custom_ldo` | `.text+0x21d0` | `custom_ldo_en` | `w0 = same custom channel`, `w1 = 0` |

`set_custom_ldo` and `unset_custom_ldo` are each 312 bytes. Both range-check
the hardware ID against 14 entries, load the channel from the per-sensor DT
mapping array at context offset `0x900 + 4*hw_id`, and pass both channel and
value without arithmetic. They ignore both wrapper return values and return
zero. The disable path deliberately programs the same voltage first, then
disables the rail.

The generic stock power-on loop loads `w2` directly from the `val` field at
offset `+4` of a 12-byte power-sequence entry and invokes `op->set(ctx,
op->data, ent->val)`. Power-off walks the sequence in reverse and invokes the
unset callback with that same `ent->val`.

## Hardware IDs and DT channel map — PROVEN_FROM_STOCK

The stock string/relocation table maps hardware IDs 0–13 to
`custom_avdd`, `custom_dvdd`, `custom_dovdd`, `custom_afvdd`,
`custom_afvdd1`, `custom_avdd1`, `custom_avdd2`, `custom_avdd3`,
`custom_avdd4`, `custom_dvdd1`, `custom_dvdd2`, `custom_oisvdd`,
`custom_oisen`, and `custom_rst`.

The merged stock DT provides these active mappings:

| sensor slot / names | AVDD | DVDD | DOVDD | AFVDD |
|---|---:|---:|---:|---:|
| sensor0: `imx989`, `s5kgm2sp`, `imx989cts`, `s5kgn1sp` | LDO3 | LDO2 | LDO7 | LDO5 |
| sensor1: `s5kjn1`, `ov32b40`, `s5kjn1cts` | LDO4 | LDO1 | LDO7 | not custom |
| sensor2: `s5kjn1main2` | LDO4 | LDO1 | LDO7 | LDO6 |
| sensor4: `ov64b` | LDO4 | LDO1 | LDO7 | LDO5 |

Exact per-driver stage index, value, delay, and resulting channel are frozen in
`kernel/phase4-custom-ldo-imgsensor-custom-stages.tsv`. The observed custom
rail values are 1,100,000, 1,200,000, 1,800,000, and 2,800,000.

Power-on ordering is the forward order in each driver's `pw_seq`: each custom
stage performs `vout(channel, value)` then `en(channel, 1)`, followed by that
entry's delay. Power-off traverses `pw_seq` in reverse: each custom stage
performs `vout(channel, value)` then `en(channel, 0)`; the stock off loop does
not apply the entry delay.

## Voltage unit — PROVEN_FROM_STOCK

This closes the former WL2868 `value`-unit residual.

1. Stock `do_hw_power_on` loads the 32-bit `ent->val` field unchanged and
   supplies it as the third argument to whichever backend is installed for
   that hardware ID.
2. Stock `set_custom_ldo` moves that argument unchanged into `w1` for
   `custom_ldo_vout`; the shim then forwards it unchanged to `will_ldo_vout`.
3. Stock `set_reg`, the alternative backend for the same camera hardware IDs,
   saves the same incoming `w2` and passes it unchanged as both `w1` and `w2`
   to `regulator_set_voltage(regulator, min_uV, max_uV)`.
4. Linux's regulator consumer API names and defines those two integer arguments
   in microvolts. The stock sequence constants (1,100,000 through 2,800,000)
   are therefore microvolt setpoints, not millivolts, selector values, or an
   opaque vendor scale.

Accordingly the exact public semantic contract is:

```c
int will_ldo_vout(int ldo_num, int value_uV);
```

The identifier `value_uV` is explanatory; the ABI remains `int, int`.

## Named camera context — PROVEN_FROM_STOCK

Nine compiled `pw_seq` objects were associated by stock symbol-table grouping:
`imx989`, `imx989cts`, `s5kgm2sp`, `s5kgn1sp`, `ov32b40`, `s5kjn1`,
`s5kjn1cts`, `s5kjn1main2`, and `ov64b`. Stock DT `sensor-names` ties these to
sensor slots 0, 1, 2, and 4 as shown above.

## Confidence labels

* **PROVEN_FROM_STOCK:** four call sites; unchanged channel/value forwarding;
  enable values 1/0; ignored returns; order; sequence constants; DT mappings;
  regulator-backend microvolt equivalence.
* **STRONGLY_INFERRED:** none required for the unit conclusion.
* **UNKNOWN:** which alternate sensor name is physically populated when a DT
  node lists several compatible stock subdrivers; this does not change the
  wrapper or voltage-unit contract.
