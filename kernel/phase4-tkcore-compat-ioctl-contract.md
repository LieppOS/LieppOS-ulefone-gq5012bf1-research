# GQ5012BF1 tkcore compat ioctl contract

## Entry points

```c
static long tee_compat_ioctl(struct file *filp,
                             unsigned int cmd, unsigned long arg);
static long tee_session_compat_ioctl(struct file *filp,
                                     unsigned int cmd, unsigned long arg);
```

Both stock callbacks have KCFI `0xe01408cd`, the exact `file_operations` ioctl prototype.

## Core compat entry

Stock `tee_compat_ioctl` (offset `0x15e8`, 244 bytes):

1. obtains `ctx=filp->private_data`; BUGs on NULL context/tee;
2. canonicalises `arg` with `compat_ptr(arg)` (the emitted conditional mask follows exact GKI `compat_ptr`);
3. runs in-place conversion before native dispatch:
   - alloc SHM (`0xc01874a5`) and RPC SHM fd (`0xc01874a7`) → `convert_compat_tee_shm_io`;
   - open session (`0xc03074a1`) → `convert_compat_tee_cmd`;
   - stock's compat-only SPTA literal (`0xc01874ae`) → `convert_compat_tee_spta_inst`;
4. returns `-EFAULT` if a converter is nonzero;
5. otherwise calls `tee_internal_ioctl(ctx,cmd,(unsigned long)uarg)` unchanged.

All other commands, including the feature-flags query, fall through directly to native. The SPTA command is converted then rejected as unknown by native with `-EINVAL`; this apparently dead path is preserved exactly.

## Session compat entry

Stock `tee_session_compat_ioctl` (offset `0x4670`, 132 bytes):

1. obtains `sess=filp->private_data`; BUGs on NULL session/context/tee;
2. identifies exactly the adjacent native encodings `0xc03074a3` and `0xc03074a4` through unsigned range arithmetic;
3. calls `convert_compat_tee_cmd((struct tee_cmd_io __user *)arg)` for those two only;
4. maps converter failure to `-EFAULT`;
5. calls `tee_session_internal_ioctl(sess,cmd,arg)`.

Stock does not call `compat_ptr` in this wrapper; it passes the callback's `unsigned long arg` through exactly.

## Native and compat command numbers

No command number translation occurs. Pointer-bearing structures reserve explicit upper 32-bit words, so `_IOC_SIZE` is already native-sized for 32-bit clients. Conversion mutates only the high words in user memory and native dispatch then consumes the same command.

## Unsupported behavior

- Unknown commands reach native and return `-EINVAL`.
- Compat SPTA nr 174 is pre-converted but still returns native `-EINVAL`.
- The nr 173 literal is only a compare boundary in stock; it receives no converter and no handler.
- Converter failures return `-EFAULT`, regardless of whether caused by invalid parameter type or user access.
- NULL converter argument returns `-EINVAL` inside the helper; the wrapper maps any nonzero helper result to `-EFAULT`.
