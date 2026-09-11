# `leds_ctl` red/blue contract

Attribute mode is 0644 (stock init chmod 0777). Show samples raw red/blue GPIOs
for logging but returns only the cached table string.

| value | show | immediate/timed output `(POWER,RED,BLUE)` |
|---:|---|---|
| 0 | `ALL_OFF` | `(0,0,0)`; relax warning-light wake source |
| 1 | `RED_ON` | `(1,1,0)` |
| 2 | `BLUE_ON` | `(1,0,1)` |
| 3 | `ALL_ON` | `(1,1,1)` |
| 4 | `RED_FLASH` | every 40 ms toggle state: `(1,1,0)` / `(0,0,0)` |
| 5 | `BLUE_FLASH` | every 40 ms toggle state: `(1,0,1)` / `(0,0,0)` |
| 6 | `RED_BLUE_FLASH` | 40-ms phases red-on, all-off, blue-on, all-off |

Store parses `%d`, cancels the timer, clears the simple flash state, caches the
new value, and resets red/blue phase to 3. Unsigned values outside 0..6
(including negative integers) return count after those state changes, without
changing GPIOs or relaxing a previously held wake source. Modes 1..6 hold
`redblue_led_wake_lock`; only mode 0 relaxes it. Flash modes do not force an
immediate phase; the first callback occurs after 40 ms. Stock userspace calls
these warning modes and writes 0 before each nonzero mode, supporting the
red/blue warning-light interpretation.
