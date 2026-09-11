# LN2403 timer/work contract

There are exactly two `struct hrtimer` objects and no `work_struct` or
`delayed_work`. Despite its name, `ln2403_pwm_work` is a synchronous helper.

| object/offset | initialization | callback | reschedule/cancel |
|---|---|---|---|
| red/blue timer `+0x68` | probe, CLOCK_MONOTONIC/REL | `redblue_led_timer_func` | starts at 40,000,000 ns; callback forwards by 40 ms and returns RESTART; every `leds_ctl` store first cancels |
| camping gate timer `+0xc8` | reinitialized on each enable, CLOCK_MONOTONIC/REL | `gpio_ctrl_timer_handler` | starts with current high interval; callback toggles GPIO91, forwards by selected interval, returns RESTART; mode transition cancels under mutex |

BLINK uses 50/50 ms. SOS begins with 200/200 ms and a transition counter. Before
each toggle: counts 0..5 use 200/200 ms; 6..11 use low interval 500 ms/high
interval 50 ms; 12..16 retain low 500 ms and set high 200 ms; count 17 sets low
1 s/high 200 ms; >17 resets count to 0 and 200/200 ms. The callback chooses the
low interval when changing high→low and the high interval when changing
low→high. This is the exact stock sequencing, regardless of ideal Morse timing.

Only camping timer start/cancel uses the global mutex. Red/blue timer and all
GPIO state are otherwise unlocked. Stock remove/module-exit do not cancel either
timer—an intentional lifecycle defect preserved and documented.
