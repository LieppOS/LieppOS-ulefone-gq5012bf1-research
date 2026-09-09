# WL2868 voltage contract

Public ABI: `int will_ldo_vout(int ldo_num, int value)` where `value` is proven by stock imgsensor callers to be microvolts.

## Common control flow

- Valid channels are 1–7; invalid channels log and helper returns -1.
- Register is `0x03 + (ldo_num-1)`.
- `q = trunc_toward_zero(value / 100)`. The helper logs `q`.
- If `q == 0` (input -99..99), return 0 without I2C.
- For the selected channel, if signed `value < threshold_literal`, code is 0. Otherwise calculate the signed expression below and pass its low 8 bits to I2C. There is no high clamp or overflow rejection.
- Write uses one raw `i2c_transfer`; readback then runs unconditionally, even after write failure. A negative write result is returned by the helper; a readback error is logged but does not affect its return. Any nonnegative transfer result is treated as success.
- The exported dispatcher discards the helper return and returns 0 for either supported chip byte. Only an unsupported chip byte returns -1 publicly.

## Exact table

`nominal_min_uV`/`nominal_max_uV` describe code 0/code 255 for the linear formula. `stock_zero_below_uV` is the actual (factor-ten-lower) comparison literal. Values above nominal max wrap modulo 256; values between the low comparison and nominal base can produce a negative quotient whose low byte wraps.

| Variant | Channels | Registers | nominal_min_uV | nominal_max_uV | step_uV | encoding before u8 truncation | stock_zero_below_uV | clamp |
|---|---|---|---:|---:|---:|---|---:|---|
| WL2864C | 1–2 | 0x03–0x04 | 600000 | 3787500 | 12500 | `(trunc(value/100)-6000)/125` | 60000 | only code=0 below literal; no high clamp; u8 wrap |
| WL2864C | 3–7 | 0x05–0x09 | 1200000 | 4387500 | 12500 | `(trunc(value/100)-12000)/125` | 120000 | same |
| WL2868C | 1–2 | 0x03–0x04 | 496000 | 2536000 | 8000 | `(trunc(value/100)-4960)/80` | 49600 | only code=0 below literal; no high clamp; u8 wrap |
| WL2868C | 3–7 | 0x05–0x09 | 1504000 | 3544000 | 8000 | `(trunc(value/100)-15040)/80` | 150400 | same |

All signed divisions truncate toward zero. There is no round-to-nearest.

## Channel/caller table

| Channel | Register | Family | Stock caller examples |
|---:|---:|---|---|
| 1 | 0x03 | low-voltage family | 1,100,000; 1,200,000 uV |
| 2 | 0x04 | low-voltage family | 1,100,000 uV |
| 3 | 0x05 | high-voltage family | 2,800,000 uV |
| 4 | 0x06 | high-voltage family | 2,800,000 uV |
| 5 | 0x07 | high-voltage family | 2,800,000 uV |
| 6 | 0x08 | high-voltage family | 2,800,000 uV |
| 7 | 0x09 | high-voltage family | 1,800,000 uV |

For the probe-selected WL2868C path, these examples encode as: channel 1 1.1 V→75 and 1.2 V→88; channel 2 1.1 V→75; channels 3–6 2.8 V→162; channel 7 1.8 V→37.
