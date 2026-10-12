# yft_gpio_keys debounce contract

Both DT children specify `debounce-interval=<16>` milliseconds. Stock also changes the missing-property default from upstream 5 ms to **16 ms**.

For each GPIO key stock calls `gpiod_set_debounce(desc, 16000)` (microseconds):

- success: controller hardware debounce is used; `software_debounce` remains zero;
- any negative return: `software_debounce=16` ms; the error is intentionally not propagated.

`gpiod_cansleep()` selects implementation independently of the set-debounce return:

- non-sleeping GPIO: `CLOCK_REALTIME`, `HRTIMER_MODE_REL`, delay `software_debounce * 1,000,000 ns`;
- sleeping GPIO: `mod_delayed_work(system_wq, ..., msecs_to_jiffies(software_debounce))`.

Thus hardware-debounce success still schedules a zero-delay completion, while failure schedules exactly 16 ms. The hard ISR disables the IRQ first; completion samples once, reports/syncs, relaxes wake and re-enables it. State and timers are per button.

The MediaTek pinctrl/EINT provider exposes `PIN_CONFIG_INPUT_DEBOUNCE` through `mtk_eint_set_debounce`; whether a given live EINT register configuration accepts it is provider/runtime state. This is not an unknown module behavior: both success and fallback paths are completely reconstructed and byte-identical.
