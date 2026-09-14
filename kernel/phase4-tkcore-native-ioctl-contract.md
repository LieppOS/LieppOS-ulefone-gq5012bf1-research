# GQ5012BF1 tkcore native ioctl contract

## Prototypes and KCFI

```c
static long tee_internal_ioctl(struct tee_context *ctx,
                               unsigned int cmd, unsigned long arg);
static long tee_session_internal_ioctl(struct tee_session *sess,
                                       unsigned int cmd, unsigned long arg);
```

Both are stock-local and direct-call-only. Stock emits no KCFI type word for either; `NOT_EMITTED_DIRECT_ONLY` is the exact ABI state.

## Core dispatch — `tee_internal_ioctl`

Stock offset `0x1f4c`, size 3260. Accepted commands:

1. `0xc03074a1` open session: copy 48 bytes; reject `fd_sess >= 1`, NULL op/UUID, or mismatched data pointer/size; call `tee_session_create_fd`; always attempt to publish `err` and `origin`, and publish `fd_sess` only when backend creation returned 0.
2. `0xc01874a5` allocate SHM: copy 24 bytes; require NULL buffer, fd 0, at least one bit shared with `tee->shm_flags`, registered 0; call `tee_shm_alloc_io`; publish fd and possibly adjusted flags.
3. `0xc01874a7` RPC SHM fd: first require `ctx->ctx_priv` and its proven `supplicant` byte at +0x18; copy 24; require non-NULL buffer, nonzero size, fd 0, registered 0, and a nonempty flag subset; call `tee_shm_fd_for_rpc`; publish fd.
4. `0x800474b7` feature query: require non-NULL arg; copy 4-byte `nsdrv_feature_flags` object to user. Stock never writes that BSS object, so it is static zero in this module.

All other commands print the stock unknown-command diagnostic and return `-EINVAL`.

The validation asymmetry is exact: alloc checks only `(flags & tee->shm_flags) != 0` (the donor's out-of-mask check is commented); RPC-fd checks both no outside bits and at least one inside bit.

## Session dispatch — `tee_session_internal_ioctl`

Stock offset `0x4b7c`, size 1996. Accepted commands:

### Invoke `0xc03074a3`

- BUG unless `sess`, `sess->ctx`, `ctx->tee`, and `sess->sessid` are valid.
- Copy 48-byte `tee_cmd_io` using `tee_copy_from_user`, preserving kernel-client memcpy semantics.
- Require `op!=NULL`, `uuid==NULL`, `data==NULL`, `data_size==0`.
- Zero the complete local `struct tee_cmd` before `_init_tee_cmd`.
- `_init_tee_cmd(sess,&k_cmd,&cmd)`.
- Call provider `tee->ops->invoke` (slot +0x30) with stock KCFI indirect-call guard.
- On provider success call `_update_client_tee_cmd`; on provider failure transfer `cmd.origin`/`cmd.err` into `k_cmd`.
- Always `_release_tee_cmd` after successful init and also on its partial-failure path by helper contract.
- Publish `err` and `origin` to caller; return backend/Linux status.

### Cancellation `0xc03074a4`

Same initial copy/validation/init, then provider `cancel` (slot +0x38), followed by release. It does not update output parameters. Stock publishes `err` and `origin` only when the cancel backend return is zero; backend failure retains the Linux return and logs it.

Unknown session commands return `-EINVAL` (no generic Linux compat fallback).

## User-copy conventions

Native core ioctl operates only on userspace contexts (`BUG_ON(!ctx->usr_client)`) and uses kernel uaccess directly. Session ioctl may also serve the kernel API path, so it uses `tee_copy_from_user` and the paired kernel/user-aware `tee_put_user` behavior. Stock uaccess hardening expands into TTBR0 toggling and bounds checks; reconstruction invokes the exact GKI helpers/macros rather than copying assembly.
