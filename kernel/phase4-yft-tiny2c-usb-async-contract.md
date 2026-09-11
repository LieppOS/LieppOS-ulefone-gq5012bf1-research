# yft_tiny2c_usb asynchronous behavior

**None.**

Proof from the complete stock ELF:

- 12 defined functions; no timer, hrtimer, work, delayed-work, tasklet, thread, notifier or
  callback function beyond platform/I2C/sysfs callbacks.
- No timer/work/notifier/kthread imports.
- The 20-byte private structure contains only four GPIO integers and one flags word.
- No async object appears in `.data`, `.bss`, or relocations.

The 400 ms sleep and two possible 10 ms busy-delay blocks execute synchronously in I2C probe.
The paired extcon driver's delayed USB-route work is separate and is not behavior of this
module.
