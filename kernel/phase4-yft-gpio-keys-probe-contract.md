# yft_gpio_keys probe contract

`gpio_keys_probe` is 2096 bytes in stock and reconstruction and is byte-identical.

## Exact order

1. Read platform data; when absent, count firmware children. Zero children -> `-ENODEV`.
2. Allocate DT platform data (`0x30+n*0x38`) with devm; failure -> `-ENOMEM`.
3. Parse parent `autorepeat` and `label`; iterate children and parse optional OF IRQ, mandatory `linux,code`, label, input type (default EV_KEY), wake booleans/action, can-disable, debounce (stock default 16 ms).
4. Allocate driver data (`0x48+n*0x158`) and two-byte-per-key keymap with devm. Either failure logs and returns `-ENOMEM`.
5. Allocate devm input device; failure logs and returns `-ENOMEM`.
6. Initialize pointers/mutex/platform/input drvdata and exact input identity/IDs/keycode fields; set EV_REP only if requested.
7. For each child, acquire `GPIOD_IN` descriptor. `-ENOENT` permits generic IRQ-only mode; other errors return unchanged (`-EPROBE_DEFER` is not logged).
8. For a GPIO key, read polarity; request 16,000-us hardware debounce; on failure set per-key software debounce to 16 ms; choose hrtimer when GPIO cannot sleep; derive IRQ with `gpiod_to_irq()`.
9. Initialize delayed work and debounce hrtimer; select GPIO ISR and initial rising|falling flags; derive optional wake trigger from wakeup-event-action.
10. Set keycode/capability and install devm quiesce action.
11. Add IRQF_SHARED because both DT buttons lack `linux,can-disable`; call `devm_request_any_context_irq()` with child label.
12. Track any wake-enabled button.
13. Release final child fwnode reference.
14. Register input device. Failure logs and returns the input error.
15. Call `device_init_wakeup(dev, true)` and return 0. Initial state is reported when input core opens the device, not directly before probe returns.

## Failure/cleanup ledger

All allocations, GPIO descriptors, IRQs and quiesce actions are devres-owned. Any setup failure returns its exact errno; already acquired resources unwind automatically. The quiesce action cancels the correct hrtimer or delayed work. Mandatory-keycode failure is `-EINVAL` after putting the current child. Missing expected child during setup is `-EINVAL`. No-GPIO/no-IRQ and non-EV_KEY IRQ-only configuration are `-EINVAL`. GPIO-to-IRQ error and request-IRQ error propagate. `device_init_wakeup()` has no returned error in this API.

Stock quirks are preserved: optional IRQ-only buttons, default debounce 16 rather than upstream 5, and no explicit state report inside probe.
