# GQ5012BF1 tkcore file-operations contract

Stock defines exactly three 272-byte objects in `.rodata`. Their symbol bindings and every non-NULL relocation are shown below. Member offsets reflect this exact GKI's randomized `struct file_operations`; implementation uses designated initialisers and never hardcodes them.

## `tee_client_fops` — GLOBAL, 272 bytes

| Stock object offset | Member | Target |
|---:|---|---|
| `+0x00` | `owner` | `__this_module` |
| `+0x50` | `unlocked_ioctl` | `tee_ioctl` |
| `+0x58` | `compat_ioctl` | `tee_compat_ioctl` |
| `+0x70` | `open` | `tee_ctx_open` |
| `+0x80` | `release` | `tee_ctx_release` |

Used by `tkcore_client` and `tkcore_fp`.

## `tee_admin_fops` — GLOBAL, 272 bytes

| Offset | Member | Target |
|---:|---|---|
| `+0x00` | `owner` | `__this_module` |
| `+0x10` | `read` | `tee_supp_read` |
| `+0x18` | `write` | `tee_supp_write` |
| `+0x50` | `unlocked_ioctl` | `tee_ioctl` |
| `+0x58` | `compat_ioctl` | `tee_compat_ioctl` |
| `+0x70` | `open` | `tee_supp_open` |
| `+0x80` | `release` | `tee_supp_release` |

Used by `tkcore_admin`.

## `tee_session_fops` — GLOBAL, 272 bytes

| Offset | Member | Target |
|---:|---|---|
| `+0x00` | `owner` | `__this_module` |
| `+0x50` | `unlocked_ioctl` | `tee_session_ioctl` |
| `+0x58` | `compat_ioctl` | `tee_session_compat_ioctl` |
| `+0x80` | `release` | `tee_session_release` |

Installed on the anonymous fd returned by `TEE_OPEN_SESSION_IOC`.

Every omitted field — including `llseek`, `poll`, `mmap`, `flush`, iterators, fsync and asynchronous hooks — is **NULL in stock**. No generic/default callback is added.

## Wrapper contract

`tee_ioctl` (stock 64 bytes) loads `filp->private_data` as `struct tee_context *`, BUGs on NULL context or `ctx->tee`, then calls `tee_internal_ioctl(ctx,cmd,arg)`.

`tee_session_ioctl` (56 bytes) loads `filp->private_data` as `struct tee_session *`, BUGs on NULL session/context/tee, then calls `tee_session_internal_ioctl(sess,cmd,arg)`.

Compat wrappers repeat the same guards, convert only the commands listed in the UAPI report, then enter the corresponding native internal function. They are not aliases to the native fops callback.
