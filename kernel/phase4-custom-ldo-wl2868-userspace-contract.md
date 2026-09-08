# Userspace/chardev contract

The stock `.rodata`/relocations prove a misc device named `wl2864c` with fops `llseek`, `read`, `write`, and `open`.

- `open` is single-owner: if the global opened byte is already set it returns `-ENODEV` (`-19`); otherwise it resets the global position to zero.
- `llseek` accepts `SEEK_CUR` and adds the offset; all other whence values reset position to zero. It logs the updated position as `%02X`.
- `read` rejects count > 20 with `-EINVAL`, allocates a 3264/128-cache object, issues raw register reads, and formats six bytes per register: `"%02X %02X "`. It copies the formatted result to userspace and advances the position.
- `write` rejects count > 128 with `-EINVAL`, uses `memdup_user`, parses six-byte records of the form `RR VV `, and writes register/value pairs using raw I2C. It returns the requested count on success and returns the I2C/user-copy error on failure.
- No ioctl/sysfs write ABI was found in the stock inventory. No chardev operation was executed.
