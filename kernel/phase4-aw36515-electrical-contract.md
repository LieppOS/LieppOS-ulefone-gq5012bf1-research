# AW36515 electrical contract (GQ5012BF1)

Every number below was recovered from the stock `aw36515.ko` binary.  Units
are stated explicitly for each quantity; **no value was copied from the
AW36518 phase or from the public donor without binary confirmation**, and
where the donor disagreed the donor value was discarded (see
`phase4-aw36515-delta-ledger.tsv`, rows D01–D08).

## Unit discipline

| quantity | unit | how it is proved |
|---|---|---|
| V4L2 `FLASH_INTENSITY` / `TORCH_INTENSITY` values | **microamperes (µA)** | the control minima/steps are the datasheet LSB values (3910/7830 and 980/1960) and the driver converts them to an 8-bit code by subtracting the minimum and dividing by the step before writing |
| register `0x03`/`0x04`/`0x05`/`0x06` contents | **8-bit register code** | written through `regmap_update_bits(..., 0xFF, code)` |
| V4L2 `FLASH_TIMEOUT` | **milliseconds** | min 40 / step 40 / max 1600, divided by 40 before the write |
| register `0x08[3:0]` | **register code** | `code = ms / 40` |
| thermal cooling table entries | **microamperes (µA)** | fed straight into `aw36515_torch_brt_ctrl()`, which applies the µA→code conversion |
| `flashlight_arg.level` | **index**, scaled by 25000 µA per step | `level * 25000` then µA→code |
| cooling `state` | **index** 0…5 | bounds-checked against `max_state = 5`, used as `table[state - 1]` |

## Flash channel currents

```
min   3910 uA      (V4L2 control minimum, register code 0)
step  7830 uA      (one LSB)
max   2000560 uA   (= 3910 + 255 * 7830, register code 255)
code  = (uA - 3910) / 7830          [LED0 -> reg 0x03, LED1 -> reg 0x04]
```

Proof: `v4l2_ctrl_new_std(..., V4L2_CID_FLASH_INTENSITY, min #0xf46,
max = pdata->max_flash_brt, step #0x1e96, def = max)` and the reciprocal
multiplication `w8 * 0x085eaf1d >> 40` (exactly `/7830`) in
`aw36515_set_ctrl`.  A requested value below 3910 µA does **not** write a
current at all — it disables the channel (`aw36515_enable_ctrl(..., false)`).

## Torch channel currents

```
min   980 uA
step  1960 uA
max   500780 uA    (= 980 + 255 * 1960)
code  = (uA - 980) / 1960           [LED0 -> reg 0x05, LED1 -> reg 0x06]
```

Proof: the control definition (min `#0x3d4`, step `#0x7a8`) and the
`((uA - 980) >> 3) * 0x216fcdd9 >> 37` sequence (exactly `/1960`) in
`aw36515_torch_brt_ctrl`.  Below 980 µA the channel is disabled instead.

## Timeout

```
min   40 ms, step 40 ms, max 1600 ms
code  = ms / 40   into register 0x08 mask 0x0F
init  always programs 0x0A = 400 ms
```

The public donor used a `(tout/600) - 1` staircase with mask `0x1f`; the stock
binary uses the plain `/40` encoding with mask `0x0f`, and the V4L2 control is
created with a 40 ms step.  The donor form was discarded.

## Mode and enable

| operation | register write |
|---|---|
| standby | `0x01`, mask `0x0C`, value `0x00` |
| torch | `0x01`, mask `0x0C`, value `0x08` |
| flash | `0x01`, mask `0x0C`, value `0x0C` |
| enable LED0 | `0x01`, mask `0x01`, value `0x01` |
| disable LED0 | `0x01`, mask `0x01`, value `0x00` |
| enable LED1 | `0x01`, mask `0x02`, value `0x02` |
| disable LED1 | `0x01`, mask `0x02`, value `0x00` |
| software strobe source | `0x01`, mask `0x2C`, value `0x0C` |
| external strobe source | `0x01`, mask `0x2C`, value `0x20` |

`V4L2_CID_FLASH_LED_MODE = FLASH` is a deliberate no-op at the register level
(the control returns 0 without writing); the flash mode bits are programmed by
`V4L2_CID_FLASH_STROBE`.

## Thermal cooling

```
cooling device name : "flashlight_cooler"   (registered on the DT node)
max_state           : 5
state 0             : no limit; target_current restored to 2000560 uA and both
                      channels' torch current restored to 500780 uA
state 1..5          : torch current of BOTH channels clamped to
                      flash_state_to_current_limit[state - 1] =
                      {200000, 150000, 100000, 50000, 25000} uA
```

While a limit is active (`need_cooler == 1`):

* `aw36515_torch_brt_ctrl()` clamps any request above `target_current` down to
  it and prints `thermal limit current:%d`;
* `aw36515_flash_brt_ctrl()` clamps the same way but prints nothing;
* if the clamped value falls below the control minimum the register code
  becomes 0.

While no limit is active (`need_cooler == 0`) `aw36515_torch_brt_ctrl()`
records the requested value in `flash->ori_current`.

## Fixed operating points

| entry point | current | mode | note |
|---|---|---|---|
| `FLASH_IOC_SET_ONOFF` (`0x80045373`), `arg != 0` | **80000 µA** torch on the addressed channel | torch | donor used 25000 µA; stock's `0x13880` is decisive |
| `FLASH_IOC_SET_ONOFF`, `arg == 0` | channel off | standby | no-op if `led_mode` is already `NONE` |
| any other ioctl | — | — | returns `-ENOTTY` |
| `flashlight_strobe_store` | **`level × 25000` µA** torch for `arg.dur` ms | torch | wrapped in `set_driver(1)` / `set_driver(0)` |
| `aw36515_init()` | timeout 400 ms | standby | also clears `0x05`/`0x03` bit 7 and reads `0x0A` |

## Faults

Register `0x0A` is read by `V4L2_CID_FLASH_FAULT` (a volatile control) and
mapped to:

| `0x0A` bit | V4L2 fault |
|---|---|
| 0 | `V4L2_FLASH_FAULT_TIMEOUT` (`0x02`) |
| 2 | `V4L2_FLASH_FAULT_OVER_TEMPERATURE` (`0x04`) |
| 4 (LED1 short) | `V4L2_FLASH_FAULT_SHORT_CIRCUIT` (`0x08`) |
| 5 (LED0 short) | `V4L2_FLASH_FAULT_SHORT_CIRCUIT` (`0x08`) |

The control is declared with maximum `0x0F`, i.e. the over-voltage bit
(`0x01`) is reachable by the control range but is never set by this driver.
Any other control id in `get_ctrl` returns `-EINVAL`.

## Safety-relevant statements

* The driver contains **no** current clamp other than the thermal cooling
  ladder and the V4L2 control ranges; nothing prevents both channels from
  running at their maxima simultaneously.
* The only hardware timeout is register `0x08`, shared by both channels, and
  it is programmed to 400 ms on the first `set_driver(1)`.
* The reconstruction adds **no** additional gate, clamp or safety interlock:
  it is behaviourally identical to stock, including the debug `reg` sysfs
  write path, which must stay root-only in LieppOS policy.
