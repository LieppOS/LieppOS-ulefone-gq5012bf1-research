# WL2868 probe contract

Oracle function: `.text+0xa98`, 660 bytes, KCFI `0x5ef138aa`.

## Exact behavioral order

1. Save `client`; overwrite the entire 112-byte global `wl2864c_data` with zero except `client` at offset 0.
2. Print `"\0013%s: entry\n"` with `wl2864c_probe`.
3. Print the same entry format with `wl2864c_power_on`.
4. Call `devm_gpiod_get(&client->dev, "vin1", GPIOD_OUT_HIGH)` and store its result at state+0x38.
5. If the VIN1 result is an error pointer, `_dev_err(...,"failed to request vin1_en GPIO: %d\n",PTR_ERR(...))`; this failure is **non-fatal** and probe continues.
6. Otherwise log `"wl2868c: vin1_en GPIO set high\n"`, call `gpiod_set_value(desc,1)`, then immediately `devm_gpiod_put` it.
7. Call `devm_gpiod_get(&client->dev, "reset", GPIOD_OUT_HIGH)` and store its result at state+0x30.
8. On reset error, log `"failed to request reset GPIO: %d\n"`; for the normal nonzero errno path also print `"%s: wl2864c_power_on failed %d\n"` and return that `PTR_ERR`. No other cleanup occurs.
9. On reset success: set logical 1; `usleep_range_state(10000,11000,TASK_UNINTERRUPTIBLE)`; set 0; same delay; set 1; same delay; immediately `devm_gpiod_put`.
10. `msleep(1)`.
11. Overwrite `client->addr` with **0x2f**. The DT-instantiated/sysfs address remains 11-0029, but all subsequent stock transfer construction reads the mutated client address.
12. Store chip byte **0x82** at state+0x44. Stock probe performs **no chip-ID I2C read** and parses no ID DT property.
13. Print `"%s: ldo_vout=%d\n"`, function label `wl2864c_ldo_vout`, value 0, exactly seven times. These are logs only: there are no I2C calls/default register writes in probe.
14. `misc_register(&wl2864c_miscdev)`.
15. On negative misc error, print `"%s: failed to register wl2864c device\n"` and return the raw error. Client/address/chip fields remain changed; ready remains zero.
16. On success, print `"%s: wl2864c_probe successed! chip id = %d\n"`, store ready=1 at state+0x6c, and return 0.

## Error ledger

| Condition | Return | Resources/state at return | Cleanup stock performs |
|---|---:|---|---|
| VIN1 `devm_gpiod_get` error | none; continues | error pointer retained at +0x38 | log only |
| reset `devm_gpiod_get` error | `PTR_ERR(reset)` | client retained; VIN1 already put or failed; reset error pointer retained | two logs; no global clear |
| `misc_register` negative | raw errno | GPIOs put; client address already 0x2f; chip byte 0x82; ready 0 | log only |
| success | 0 | no GPIO retained; misc registered; ready 1 | none |

## Explicitly absent

No allocation, clientdata assignment, mutex init, chip read, ID validation, default register initialization, VIN2 setup, shutdown registration, or regulator-child registration exists in stock probe.
