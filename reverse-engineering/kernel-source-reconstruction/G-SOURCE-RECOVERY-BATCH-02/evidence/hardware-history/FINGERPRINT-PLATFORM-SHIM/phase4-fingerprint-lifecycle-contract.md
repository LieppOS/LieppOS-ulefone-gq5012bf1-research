# `fingerprint.ko` lifecycle and PM contract

## Module init

`init_module` calls
`platform_driver_register(&yft_finger_pdrv)`. Success returns 0. Any nonzero
registration result prints `failed to register driver` and is replaced with
literal `-ENODEV` (`-19`); the original errno is not propagated.

## Probe

The probe publishes its platform-device pointer, logs, invokes the parser,
ignores its return, and always returns 0. Full ordering and error behavior are
in `phase4-fingerprint-probe-contract.md`.

## Remove

`yft_finger_plat_remove` only sets global `yft_finger_plat = NULL` and returns
0. It does not:

- wake the DT wait queue;
- select reset/IRQ/SPI/power states;
- call `yft_finger_power_deinit`;
- put or clear pinctrl state pointers;
- release GPIO/IRQ resources (none were requested directly).

## Module exit

`cleanup_module` only calls
`platform_driver_unregister(&yft_finger_pdrv)`. Driver-core remove therefore
clears the global platform pointer as above.

## Shutdown and PM

The platform-driver shutdown pointer is NULL. There are no suspend, resume,
freeze, thaw, restore, runtime-PM, or `dev_pm_ops` callbacks. Suspend/resume does
not change reset, IRQ bias, SPI pinmux, power, or IRQ wake in this module.
Wake-IRQ management seen in the chain belongs to `microarray_fp_tee.ko`.
