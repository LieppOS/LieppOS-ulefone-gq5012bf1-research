# yft_gpio_keys lifecycle contract

- init: `platform_driver_register(&gpio_keys_device_driver)` via `module_init`.
- exit: `platform_driver_unregister(...)` via `module_exit`.
- probe: devm-managed allocations/GPIO/IRQ/quiesce; input registration; wakeup initialization.
- remove: no explicit `.remove` callback. Platform/devres teardown releases IRQs, descriptors, allocations and devm input device; registered quiesce actions cancel release/debounce hrtimers or delayed work.
- open: optional platform-data enable callback, then report all GPIO states and sync.
- close: disable every key IRQ, quiesce timers/work, optional platform-data disable callback.
- shutdown: invoke suspend and log on failure.
- suspend/resume: exact behavior documented in the PM contract.

No module-global timer, work item, GPIO descriptor, IRQ state or wakeup source exists. Per-button state is embedded in devm driver data, so there is no hidden manual free path. Lifecycle code is byte-identical to stock.
