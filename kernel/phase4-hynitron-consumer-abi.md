# Stock downstream consumer ABI

Consumer: frozen stock `spi_tiny_co5300_lcd.ko`. Both imports are undefined
symbols in its ELF and carry the same MODVERSION CRCs exported by stock
Hynitron.

## Exact provider types

Both functions are `void name(int enable)`. This prototype naturally produces
the stock genksyms CRCs under the exact GKI type environment and both stock
functions have KCFI type ID `0x019c0cac`. The caller never reads a return value.

| Symbol | Stock/provider CRC | Prototype | KCFI | State/hardware meaning |
|---|---:|---|---:|---|
| `tiny_tp_gesture_contorl` | `0x4e4b7919` | `void tiny_tp_gesture_contorl(int enable)` | `0x019c0cac` | If probe singleton is absent, log and return. Otherwise zero clears global `tiny_tpgesture_status`; any nonzero sets it to one. It performs no I2C/GPIO/IRQ operation immediately. The flag selects gesture-suspend/resume behavior on the next power transition. |
| `tiny_tp_power_contorl` | `0xfcc94fc7` | `void tiny_tp_power_contorl(int enable)` | `0x019c0cac` | If singleton is absent, log and return. `0`: idempotent suspend; set suspended byte, reset with 10-ms high delay, then either enter gesture suspend or disable IRQ and send deep sleep. Nonzero: idempotent wake; reset with 40-ms high delay, release stale contacts, clear gesture-active byte, then gesture resume or normal IRQ enable. It does not switch GPIO119/VDD. |

## Every stock consumer call site

| Consumer function / offset | Call | Argument | Ordering/condition |
|---|---|---:|---|
| `tiny_lcd_tp_control_store+0x3c` (`.text+0x2dac`) | power | parsed sysfs value converted to boolean | direct manual touch-power control |
| `tiny_lcd_ioctl+0x2b0` (`0x30b8`) | power | 1 | immediately after `tiny_lcd_power_enable_func(1)` |
| `tiny_lcd_ioctl+0x420` (`0x3228`) | gesture | 1 | enable gesture policy |
| `tiny_lcd_ioctl+0x458`, `+0x460` (`0x3260`, `0x3268`) | power | 1, then 0 | explicit wake/reset followed by suspend sequence |
| `tiny_lcd_ioctl+0x4a0` (`0x32a8`) | gesture | 0 | disable gesture policy |
| `tiny_lcd_ioctl+0x4dc` (`0x32e4`) | power | 0 | before `tiny_lcd_power_enable_func(0)` |
| `tiny_lcd_ioctl+0x57c` (`0x3384`) | power | 0 | display-off path |

The consumer contains six power-call relocations and two gesture-call
relocations. Calls can race module selection/probe in principle; stock handles
that only by checking global `hyn_ts_data`, logging
`hynitron_power_contorl data pointor is null,no the device`, and returning
without an error channel.

## Hard gate

Required natural provider parity is 2/2 names, CRCs and KCFI types. The stock
consumer requires exactly `0x4e4b7919` and `0xfcc94fc7`; no consumer rebuild or
ELF/CRC patch is allowed.
