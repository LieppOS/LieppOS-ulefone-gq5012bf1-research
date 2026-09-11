# Hynitron lifecycle contract

`init_module` logs driver version, calls
`yft_touchpanel_device_add(&hynitron_i2c_driver,0)` and ignores its return, then
registers the I2C driver. `cleanup_module` deletes that driver.

Probe publishes the singleton early, parses DT, owns GPIO/power/reset, reads
identity/firmware, initializes input/workqueue and IRQ, creates debug/gesture
sysfs, final-resets/enables IRQ, then marks `"hyn_ts"` used in yft_devinfo.
Failure labels unwind the resources reached; YFT used-state is never set on
failure. Exact order and errors are in the probe contract.

Remove removes gesture/main sysfs groups, frees IRQ, flushes work, unregisters/
frees input and GPIO/memory according to stock ownership. The stock driver has
no separate shutdown callback and does not clear the YFT used registry or
`second_touch_fw_version` on remove. It does not explicitly power VDD low.
Suspend/resume are external-export driven, not I2C PM callbacks.
