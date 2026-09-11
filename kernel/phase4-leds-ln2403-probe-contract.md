# LN2403 probe/failure contract

Probe allocates one 0x118-byte (280-byte) zeroed object and publishes it globally. It reads
five named GPIOs in this exact order: EN, LN2403 POWER, LED POWER, RED, BLUE.
Each uses `of_get_named_gpio_flags(...,0)`, validates with `gpio_to_desc`, then
calls `gpio_request`; a negative number, null descriptor, or nonzero request
result fails probe with `-1`. Requests are never freed.

It acquires pinctrl, then looks up `ln2403_pwmoff_high`,
`ln2403_pwmoff_low`, and `ln2403_pwmon`; any pinctrl/get/lookup error collapses
to `-1`. It creates sysfs files in order `camplight_mode`, `leds_ctl`,
`camplight_set_brightness`, initializes the mutex, writes all five GPIOs raw-low,
initializes only the red/blue hrtimer, registers its wake source, clears the PWM
flag, selects `ln2403_pwmoff_low`, sets mode zero, and registers the camping wake
source. The module never calls a GPIO direction API; direction is board/pinctrl
precondition, while probe changes only raw output values.

Allocation failure is `-ENOMEM`; missing OF node is `-ENODEV`; GPIO/pinctrl
failures are `-1`; sysfs returns its creation errno. On any sysfs-create failure, stock starts at
the current (failed) attribute and calls `device_remove_file` for it and every
earlier attribute in reverse order; the null-terminated four-pointer table and
this quirk are preserved exactly. Other successful probe resources are retained
on all late failures, matching stock. Successful probe
leaves both logical modes and duty at zero, PWM disabled, all gates/LEDs raw-low,
GPIO22 selected low, timers stopped, and both wake sources inactive.
