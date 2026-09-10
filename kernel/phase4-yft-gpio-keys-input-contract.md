# yft_gpio_keys input-device ABI

## Device identity

- name: `yft-gpio-keys` (no parent DT `label`, so `pdev->name` from `/yft-gpio-keys`)
- phys: `gpio-keys/input0`
- parent: platform device `/yft-gpio-keys`
- bustype/vendor/product/version: `BUS_HOST`, `0x0001`, `0x0001`, `0x0100`
- keycode storage: two `unsigned short` entries; `keycodesize=2`, `keycodemax=2`
- capabilities: `EV_KEY`, `KEY_F1` (59), `KEY_F2` (60)
- EV_SW: none; EV_REP: absent because parent `autorepeat` is absent
- input properties: none explicitly set
- open/close: stock `gpio_keys_open`/`gpio_keys_close`; they call optional platform enable/disable and report state on open
- event callback: none; sysfs driver groups expose `keys`, `switches`, `disabled_keys`, `disabled_switches`

## Emission sequence

For these GPIO keys, `gpio_keys_gpio_report_event()` reads the logical GPIO and calls `input_event(input, EV_KEY, code, state)`. `input_report_key` compiles to the same `input_event` call for the suspended synthetic press.

- initial registration: input device registration; state is first reported by input open, one event per GPIO, then one `input_sync()`.
- IRQ press/release: hard ISR disables that IRQ, starts hrtimer or delayed work for the debounce interval/fallback; completion emits `EV_KEY code state`, then `input_sync()`, then wake relax (if applicable), then re-enables the IRQ.
- normal press: `EV_KEY(KEY_F1/KEY_F2,1)` then `SYN_REPORT`.
- normal release: `EV_KEY(KEY_F1/KEY_F2,0)` then `SYN_REPORT`.
- suspended wake IRQ: before debounce completion, emits a synthetic press `EV_KEY(code,1)` without immediate sync; the debounce completion emits sampled state and then syncs. This preserves the upstream stock quirk/order.
- resume: reports both sampled key states, then one sync.

After every successful GPIO sample, stock logs it and changes the IRQ type: logical pressed -> rising (next physical release for active-low); logical released -> falling (next physical press). Errors reading GPIO emit no input event, but the debounce completion still syncs, relaxes and re-enables the IRQ.
