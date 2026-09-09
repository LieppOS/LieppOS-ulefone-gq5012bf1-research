# Userspace/chardev contract — closure summary

Authoritative detail: `phase4-custom-ldo-wl2868-miscdev-contract.md`.

Stock registers `/dev/wl2864c` with fixed minor 250 and fops owner/llseek/read/write/open only.

- `open` is not single-owner. It requires the probe-ready byte, resets the global register cursor, and returns 0; if not ready it returns `-ENODEV`.
- `llseek` changes the global 32-bit cursor only: SEEK_CUR adds the low 32 bits of offset, every other whence resets it. It returns the existing `file->f_pos` unchanged.
- `read` allocates 128 bytes before validating count, rejects count >20, reads consecutive registers from the global cursor, emits uppercase `RR VV ` records, ignores `copy_to_user` failure, returns the requested register count, and does not advance cursor/ppos.
- `write` rejects count >128, uses `memdup_user`, parses permissive six-byte `RR VV ` records without validating separators, and writes arbitrary one-byte registers. A non-multiple-of-six count can read beyond the duplicated buffer. I2C error maps to `-ENODEV`; success returns count.
- No release/ioctl/compat/poll/mmap interface exists.

Raw writes can alter VOUT/enable registers and are dangerous. They were not exercised.
