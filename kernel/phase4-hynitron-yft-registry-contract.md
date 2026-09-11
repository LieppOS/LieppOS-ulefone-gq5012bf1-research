# Hynitron YFT registry/device-info contract

At module init, before I2C registration, stock calls
`yft_touchpanel_device_add(&hynitron_i2c_driver, 0)` and ignores the result.
This advertises the candidate as initially unused. Only after complete probe,
input/IRQ/sysfs/gesture initialization and final reset does it call
`yft_set_touch_device_used("hyn_ts", 1)`; that result is also ignored. Remove
and failure paths do not clear the registry.

`second_touch_fw_version` is a stock yft_devinfo-owned `char[30]`. On each
successful CST8xx 0xa6 read, Hynitron formats:

```
Vno: %x. %x. %x. %x.\n
```

Arguments are running firmware version, checksum, module ID and project ID, in
that order. It reports the running controller, not the packaged image. The same
read fields back `/sys/hynitron_debug/hyntpfwver`.

Provider CRCs are exact stock ABI: object `0x7198d58d`, candidate-add
`0xf5ba4446`, set-used `0x0a0f3b69`. Final modpost uses the frozen stock
provider witness; reconstructed yft_devinfo is intentionally not linked.
