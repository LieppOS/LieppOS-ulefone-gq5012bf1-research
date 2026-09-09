# WL2868 misc-device ABI

## Device and fops

Stock has an 80-byte `miscdevice` with fixed minor **250** (not `MISC_DYNAMIC_MINOR`, which is 255), exact name `wl2864c`, and a 272-byte `file_operations` containing only owner, llseek, read, write, and open. There is no release, ioctl, compat_ioctl, poll, mmap, sysfs, or debugfs ABI. Device node is `/dev/wl2864c` when registered.

## open

If the global probe-ready byte is zero, print `"wl2864c: open failed."` and return `-ENODEV`. Otherwise set the global 32-bit register cursor to zero and return 0. It does not set an opened flag and is not single-owner.

## llseek

If `whence == SEEK_CUR`, update the global 32-bit cursor with the low-32-bit addition of `offset`; every other `whence` resets that cursor to zero. Log the cursor as `%02X`. Return the existing `file->f_pos` unchanged; stock neither stores the cursor into `file->f_pos` nor uses `fixed_size_llseek`/`no_llseek`.

## read

- Allocate exactly 128 bytes with `kmalloc(...,GFP_KERNEL)` **before** validating count.
- Allocation failure logs and returns `-ENOMEM`.
- If count >20, free and return `-EINVAL`.
- Starting at the global cursor (not `*ppos`), read `count` consecutive 8-bit registers with raw two-message transfers.
- Format six uppercase ASCII bytes per register: `RR VV `, maximum 120 bytes.
- On I2C error, log, free, and return the raw negative transfer result.
- Call `copy_to_user` for `6*count` bytes, but stock ignores its residual/error result.
- Free and return the requested register count, **not** formatted byte length. It does not advance the global cursor or `*ppos`.

## write

- If count >128, return `-EINVAL`.
- `memdup_user(user,count)`; on error log and return `PTR_ERR`.
- Iterate `i=0; i<count; i+=6`; consume positions i, i+1 as register hex and i+3, i+4 as value hex. Bytes i+2 and i+5 are ignored—spaces are not validated.
- The nibble conversion is permissive and has no upper bounds: byte >=`a` maps to byte-`W`; else byte >=`A` maps to byte-`7`; else byte >`/` maps to byte-`0`; all lower bytes map to zero. Results are truncated into u8 after combining.
- The loop condition permits an out-of-bounds read of the duplicated buffer when nonzero count is not a multiple of six. This stock quirk is preserved in parity mode, not tested.
- Write each pair with one raw transfer. On a negative transfer, log, free, and return `-ENODEV` rather than the raw errno.
- On success free and return original count. `*ppos` is ignored.

The write interface can alter arbitrary one-byte registers, including VOUT and enable. It is dangerous and was not exercised.
