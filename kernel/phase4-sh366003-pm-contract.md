# SH366003 PM, remove and shutdown contract

| Event | Stock behavior |
|---|---|
| suspend | No driver PM callback is registered |
| resume | No driver PM callback is registered |
| monitor during suspend | No explicit cancel/freeze; work is queued on `system_wq` and driver supplies no suspend gate |
| remove | `sh_fg_remove` returns 0 and performs no cancellation, class teardown, provider deregistration, or explicit power-supply unregister (registration is devm-managed) |
| shutdown | `sh_fg_shutdown` emits the stock shutdown log only; no reset, seal, flash write, or work cancellation |
| module exit | `i2c_del_driver(&sh_fg_driver)` |
| reboot notifier | None |

This intentionally records stock's sparse lifecycle behavior. The reconstruction does not invent a suspend/resume transaction or gauge reset. Development source may use safe cancellation only where required to avoid a reconstruction-only use-after-free, and any such divergence is listed as a residual.
