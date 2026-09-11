# yft_tiny2c_usb lifecycle / PM contract

| lifecycle event | exact stock behavior |
|---|---|
| module init | register platform driver `yft_tiny2c_usb`; return registration result |
| platform probe | parse/request GPIOs, temporary rails-on I2C ID bind, rails-off, create two sysfs files |
| I2C probe | synchronous 400 ms settle plus ID reads and two optional 10 ms retry gaps |
| I2C remove | log, then unusually calls `i2c_unregister_device(client)` on the client being removed |
| platform remove | log source-style function/line (`tiny2c_usb_remove`, 346), return 0 only |
| module exit | unregister platform driver only |
| shutdown | absent |
| suspend/resume | absent; no PM ops |

Platform remove/module exit do **not** remove sysfs explicitly, unregister the dynamically
registered I2C driver, free GPIOs, free private data, force rails low, clear `yft_usb_flag`,
change USB role/VBUS, or cancel work. There is no work to cancel. Device core removal may
remove device-owned sysfs entries as a consequence, but the module supplies no cleanup calls.

No lifecycle path calls an MT6375 function or a USB API. Stock userspace, including
ActivityManager crash cleanup, is responsible for writing mode 0 in normal application
teardown/failure scenarios. Reconstruction preserves these quirks rather than adding safer
cleanup absent from stock.
