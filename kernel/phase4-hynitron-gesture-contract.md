# Hynitron gesture contract

`void tiny_tp_gesture_contorl(int enable)` (CRC `0x4e4b7919`, KCFI
`0x019c0cac`) is a binary policy toggle. Zero stores 0; every nonzero value
stores 1 in `tiny_tpgesture_status`. It performs no I2C or IRQ operation and
returns immediately if the global touch instance is unavailable. The LCD
consumer calls it before power-control transitions.

When display-off subsequently calls power-control with gesture policy enabled,
stock writes `0xec=1`, sleeps 10 ms, reads back 0xec, and retries enable up to
three times. It marks gesture-active, clears last gesture/key state, preserves
IRQ, and changes IRQ type to stock flags `IRQF_TRIGGER_FALLING |
IRQF_NO_SUSPEND` (`0x4002`) inside a disable/enable bracket. IRQ wake was
already enabled once during probe and is not toggled here. Resume clears active
state, restores the normal DT/request IRQ flags, and writes `0xec=0`.

Gesture IRQ processing first confirms register 0xec is 1, then reads 12 bytes
from 0xd3. Byte 0 is gesture ID; endpoint X/Y use bytes 8..11 nibble packing.
Supported ID→key mappings are: 0x20 DOWN, 0x21 RIGHT, 0x22 LEFT, 0x23 UP,
0x24 O, 0x31 W, 0x32 M, 0x33 E, 0x34 C, 0x46 S, 0x54 V, 0x65 Z, and
0xcc/0xe5 POWER. A recognized gesture emits key down + `SYN_REPORT`, then key
up + `SYN_REPORT`; duplicate cached key reports are suppressed.

Default gesture framework mode is enabled at probe, while the external LCD
policy toggle defaults zero. Sysfs exposes `hyn_gesture_mode` and
`hyn_gesture_buf` under `/sys/hynitron_debug/`.
