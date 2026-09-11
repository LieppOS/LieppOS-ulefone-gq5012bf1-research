# Hynitron power export contract

`void tiny_tp_power_contorl(int enable)` (CRC `0xfcc94fc7`, KCFI
`0x019c0cac`) preserves stock spelling and has binary semantics.

- unavailable singleton: return, no action
- `enable == 0`: if already suspended, return. Cache suspended, reset the
  controller. If `tiny_tpgesture_status != 0`, enter gesture mode and retain a
  wake IRQ; otherwise disable IRQ and write deep sleep `0xe5=0x03`.
- `enable != 0`: if already active, return. Clear suspended, reset with 40 ms
  settling, release any stale touch, clear gesture-active state; if gesture
  policy was selected, leave gesture mode/normalize IRQ, otherwise enable IRQ.

The export is idempotent through the cached suspended state and returns no
status; I2C/GPIO errors are not propagated to `spi_tiny_co5300_lcd`. Stock LCD
call sites invoke gesture-control first and power-control second on both off and
on paths. Calls may precede probe; the singleton guard makes those no-ops.
Neither path drives the VDD GPIO or any LCD GPIO directly.
