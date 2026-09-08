# Voltage and enable contracts

## Voltage

`wl286[48]c_ldo_vout(int ldo_num, int value)` accepts LDO numbers 1–7 and maps register `ldo_num + 2`. Invalid LDO numbers return `-1`. The compiler-visible arithmetic is:

- WL2864C offsets: `{-6000,-6000,-12000,-12000,-12000,-12000,-12000}`; limit table `{60000,60000,120000,120000,120000,120000,120000}`.
- WL2868C offsets: `{-4960,-4960,-15040,-15040,-15040,-15040,-15040}`; limit table `{49600,49600,150400,150400,150400,150400,150400}`.
- `scaled = signed(value / 100)` and candidate `vset = (scaled + offset[ldo-1]) / 125`.
- The stock compare/csel path selects zero when the recovered limit comparison fails. It then performs raw register-pointer/readback transfers and logs `write_val` and `read_val`.

Follow-up stock-consumer analysis closes the former unit uncertainty. Stock `imgsensor` loads `ent->val` unchanged from each 12-byte camera power-sequence entry and dispatches that same field to either its standard regulator backend or its Ulefone custom-LDO backend. The standard backend passes the value unchanged as both `min_uV` and `max_uV` to `regulator_set_voltage`; `set_custom_ldo` passes it unchanged to `custom_ldo_vout`, whose byte-identical shim passes it unchanged to `will_ldo_vout`. Compiled values are 1,100,000, 1,200,000, 1,800,000, and 2,800,000. Therefore `value` is **PROVEN_FROM_STOCK to be microvolts**. Evidence: `phase4-custom-ldo-imgsensor-consumer-analysis.md`.

## Enable

`wl286[48]c_ldo_en(int ldo_num, int enable)` reads register `0x0e`, sets or clears bit `ldo_num-1`, and writes it back. Invalid LDO numbers log/return zero in the stock branch. WL2868C adds bit7 when the resulting low-seven-bit bitmap is zero. I2C errors propagate as negative returns.

## GPIO sequencing

Probe sets `reset` high, then pulses `vin1_en` high → 10–11 ms delay → low → 10–11 ms delay → high, followed by 1 ms sleep. These transitions were only reconstructed statically and were never executed.
