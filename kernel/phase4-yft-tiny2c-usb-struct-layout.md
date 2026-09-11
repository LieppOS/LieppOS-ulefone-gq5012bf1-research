# yft_tiny2c_usb private-state layout

## Heap allocation

Stock `tiny2c_usb_probe` performs a zeroed 20-byte allocation (`kmalloc_trace` size `0x14`,
flags `0xdc0`) and stores its pointer in global `tiny2c_usb_chip_data`.

```c
struct tiny2c_usb_chip_data {       /* stock size 0x14 */
    int gpio_1v8;                   /* +0x00 */
    int gpio_3v3;                   /* +0x04 */
    int gpio_5v;                    /* +0x08 */
    int gpio_io3v3;                 /* +0x0c */
    enum of_gpio_flags gpio_flags; /* +0x10, reused for all four parses */
};
```

Instruction evidence: probe stores OF results at `x20+0,+4,+8,+0xc` and passes `x20+0x10`
as every flags output; power/show functions load the same four offsets. No unknown gaps exist.

## Static/global state

| symbol | section/size | meaning |
|---|---|---|
| `chip_id` | `.bss+0x0`, 4 | last I2C-probe result, shown by `sensor_id` |
| `tiny2c_usb_chip_data` | `.bss+0x8`, 8 | allocation pointer |
| `yft_usb_flag` | provider `.bss+0x4`, 4 | external charger USB-path exclusion state |

There is no stored device/platform-device/client pointer in private state; the registered
I2C/platform driver objects are static. There is no cached mode, power state, USB state,
charger handle, timer/work, lock, wake source, notifier, pinctrl object, regulator, clock, or
sysfs registration bitmap. Those fields are absent, not unknown.

Stock never frees the allocation, including platform remove and probe failures after
allocation. This lifecycle defect is part of the reconstructed contract.
