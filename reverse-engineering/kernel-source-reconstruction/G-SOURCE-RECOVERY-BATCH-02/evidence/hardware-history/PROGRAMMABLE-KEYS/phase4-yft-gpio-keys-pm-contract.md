# yft_gpio_keys wakeup and PM contract

Both DT keys have `wakeup-source`, so probe calls `device_init_wakeup(dev, true)`. Both are treated identically.

## Suspend

When `device_may_wakeup(dev)` is true, iterate both buttons, call `enable_irq_wake()` and set each `suspended=true`. `wakeup-event-action` is absent, so `wakeup_trigger_type=0`; suspend does not change the trigger type. On failure, unwind prior wake IRQs and suspended flags and return the exact error.

If wakeup is disabled administratively, suspend locks the input mutex and closes an enabled input device, disabling its keys through the inherited close path.

## Wake interrupt

The ISR calls `pm_stay_awake()` without a fixed timeout. While suspended it emits a synthetic EV_KEY press so a fast-released key is not lost. Debounce completion samples/reports/syncs and calls `pm_relax()`. There is no separate vendor wakelock object.

## Resume

For wake-capable operation, clear `suspended`; if IRQ wake is set, call `disable_irq_wake()`. Because wakeup trigger type is zero, no generic both-edge restore occurs. For non-wakeup operation, reopen an enabled input device. Finally sample both GPIOs and issue one sync.

Shutdown calls the same suspend routine and logs `failed to shutdown` on error. The custom normal-event edge arming remains in effect; PM introduces no F1/F2 asymmetry.
