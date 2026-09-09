# WL2868 lifecycle contract

## Initialization

`init_module` logs entry, calls `i2c_register_driver(THIS_MODULE,&wl2864c_i2c_driver)`, truncates the return to its low byte for its decision/return, logs success when that byte is zero and failure otherwise, and returns the zero-extended low byte. This low-byte truncation is a stock quirk.

## Probe success state

Probe registers the misc device and sets only the ready byte to 1 after the success log. GPIO descriptors have already been manually `devm_gpiod_put`; no GPIO remains intentionally owned by the driver. Client pointer, mutated client address 0x2f, chip byte 0x82, and stale descriptor values remain in global storage.

## Remove

The kernel-6.1 void remove callback does exactly:

1. `misc_deregister(&wl2864c_miscdev)`;
2. set ready byte at state+0x6c to zero;
3. print `"%s: deregister wl2864c device ok\n"`.

It does not disable any LDO, read/write register 0x0e, assert reset, change VIN1/VIN2, free GPIOs, clear client/chip/cursor, or clear the global pointer.

## Shutdown and exit

The `i2c_driver` shutdown slot is null. `cleanup_module` only calls `i2c_del_driver(&wl2864c_i2c_driver)`; normal driver-core removal is therefore the only misc deregistration path.

No invented safe-shutdown behavior is present. No lifecycle callback was exercised during this static task.
