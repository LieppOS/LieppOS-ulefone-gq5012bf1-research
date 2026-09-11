# Hynitron Linux input contract

Live stock snapshot and ELF agree:

- name `hyn_ts`; bus `BUS_I2C` (`0x18`); location/external flags unset
- vendor/product/version left zero
- direct-touch property; MT protocol **type A** (`SYN_MT_REPORT`, no slots)
- one contact (`hynitron,max-touch-number = 1`)
- `ABS_MT_TRACKING_ID` 0..1
- `ABS_MT_POSITION_X` 0..340; `ABS_MT_POSITION_Y` 0..340
- `ABS_MT_TOUCH_MAJOR` 0..255; `ABS_MT_WIDTH_MAJOR` 0..200
- `BTN_TOUCH`; no pressure axis and no orientation transform

Android's captured InputReader associates it with display id 0 because no IDC
or port association exists; that framework assignment is not a kernel ABI.

## CST820 packet

A register-0 read returns nine bytes. `count = packet[1] & 0x0f` and is clamped
to the configured one contact. For contact 0:

```
event = packet[2] >> 6
x     = ((packet[2] & 0x0f) << 8) | packet[3]
id    = packet[4] >> 4
y     = ((packet[4] & 0x0f) << 8) | packet[5]
area  = packet[7] >> 4
```

Events 0 (down) and 2 (contact) report tracking ID, touch-major (`area >> 3`),
X, Y, width-major (`area`, stock fallback 0x28), `BTN_TOUCH=1`, then
`SYN_MT_REPORT`. Up reports tracking ID -1, `BTN_TOUCH=0`, then
`SYN_MT_REPORT`. The work callback ends each frame with `SYN_REPORT`; the
zero-contact path emits the same up sequence. Resume flushes any stale contact.
Gesture key press/release sequences are separate from touch frames.
