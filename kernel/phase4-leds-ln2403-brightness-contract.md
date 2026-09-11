# `camplight_set_brightness` contract

Attribute mode is 0644 (chmod 0777 by stock init). Show prints the internal
`camplight_duty` integer as `%d\n`, not necessarily the last userspace input.
Store parses one signed decimal with `sscanf("%d")`; parse failure returns count.

For input `N == 0`: cached value remains 0; EN and POWER become 0; PWM3 is
disabled if active; GPIO22 is selected high and then low; the camping wake
source is relaxed.

For `N != 0`:

```text
capped = (N < 94) ? N : 94       // signed comparison; no lower clamp
duty = 100 - capped              // value retained and shown
DATA_WIDTH = 100
THRESH = duty
```

PWM is programmed immediately, then POWER=1 and EN=1, and the camping wake
source is held. Normal app inputs therefore map 1..93 to thresholds 99..7 and
94..100 to threshold 6. The stock app seekbar writes its progress dynamically,
defaulting restored values to 50 and enforcing its >90 high-use policy in
userspace. Negative nonzero input is accepted, produces duty >100, and wraps
when assigned to the provider's 16-bit threshold field. Brightness does not
update `camplight_mode`, cancel BLINK/SOS, or restore a prior mode; these stock
interactions/bugs are preserved.
