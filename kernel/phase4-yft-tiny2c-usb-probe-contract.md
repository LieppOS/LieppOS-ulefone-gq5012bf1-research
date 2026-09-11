# yft_tiny2c_usb probe contract

## Exact platform probe order

1. Log `tiny2c_usb_probe start`.
2. Allocate 20 zeroed bytes; publish pointer globally immediately. On NULL, log and return
   `-ENOMEM`; no publication rollback.
3. Read `pdev->dev.of_node`.
4. Parse/request 1v8, 3v3, optional 5v, io3v3 in that order. See GPIO contract.
5. On fatal GPIO parse/request result, log `tiny2c_usb_parse_dts failed` and return `-1`.
6. Call `tiny2c_usb_power_init(data, 1)` (io3v3, 5v slot, 3v3, 1v8 raw-high).
7. Read/log all four raw GPIO values.
8. Dynamically call `i2c_register_driver(THIS_MODULE, &tiny2c_usb_i2c_driver)`.
9. If registration fails, log `register tiny2c_usb driver failed (%d)` and return that errno.
   Rails remain high; allocation/GPIO requests remain.
10. Call `tiny2c_usb_power_init(data, 0)`; read/log raw values.
11. Log sysfs init begin. Create `tiny2c_usb_mode`, then `sensor_id` on `pdev->dev`.
12. On attribute failure, remove attributes from the static list through the stock backwards
    loop, log `failed to init_sysfs`, return the create errno. The I2C driver stays registered;
    GPIOs/allocation stay retained.
13. Log `tiny2c_usb_probe end`; return 0.

Probe does not set `platform_set_drvdata`, set GPIO direction, set `yft_usb_flag`, select
pinctrl, acquire a regulator, or register PM callbacks.

## I2C probe

1. Log client address.
2. `msleep(400)`.
3. Read chip ID, cache return.
4. If `0x4c59`, return 0.
5. Otherwise execute `mdelay(10)` (compiled as ten `__const_udelay(4295000)` calls), read and
   cache again; if `0x4c59`, return 0.
6. Otherwise another `mdelay(10)`, read/cache a third time.
7. Return 0 for any nonzero final value; if zero log `read sensor-id fail` and return `-1`.

`tiny2c_usb_read_chipid` reads register 0 and register 1 using separate two-message I2C
transfers (2-byte register pointer followed by 1-byte read), combines
`low | (high << 8)`, stores the global and returns it. A second-transfer failure is retried up
to five total attempts; successful zero is returned immediately. Nonnegative transfer counts
are treated as success without requiring exactly two messages. The first read's failure does
not abort the second read.

## Failure/cleanup matrix

| condition | errno | cleanup |
|---|---:|---|
| allocation NULL | `-ENOMEM` | none |
| 1v8/3v3/io3v3 request failure | `-1` | none |
| 5v request failure | none | log and continue |
| I2C register failure | original errno | none; rails remain high |
| first sysfs create failure | original errno | attempts removal of first attr; I2C remains |
| second sysfs create failure | original errno | removes second/first entries; I2C remains |
| I2C final cached ID zero | `-1` | I2C core handles failed bind; platform registration still succeeds if driver registration itself returned 0 |

Stock defects/leaks are preserved; no invented devm conversion or cleanup is permitted.
