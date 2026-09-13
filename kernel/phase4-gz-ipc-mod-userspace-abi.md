# `gz_ipc_mod` userspace ABI audit

## Result

`gz_ipc_mod` **does expose a userspace TIPC character-device ABI**. It also exports a separate kernel API; these must not be conflated.

| Surface | Result | Proof |
|---|---|---|
| `/dev` | yes, dynamic cdev per probed TEE virtio device | `alloc_chrdev_region`, `cdev_add`, `device_create` |
| `/proc` | none | no procfs objects/imports |
| `/sys` | generic class/device entries only | class `KBUILD_MODNAME`; no custom attribute group |
| debugfs | none | no debugfs object/import |
| ioctl | `TIPC_IOC_CONNECT` | `_IOW('r', 0x80, char *)`; native and compat entry points |
| read | yes, message-oriented | `.read_iter = tipc_read_iter` |
| write | yes, message-oriented | `.write_iter = tipc_write_iter` |
| mmap | none | no `.mmap` |
| poll | yes | `.poll = tipc_poll` |
| custom uevent | none | only generic `device_create` uevent behavior |
| module parameters | none | no `parm=` metadata |

## Device creation

Module init reserves four device numbers and creates class `gz_ipc_mod` (`KBUILD_MODNAME`), then registers Trusty and Nebula virtio drivers. Probe derives the node name from secure/virtio config:

```text
<config.dev_name.tee_name>-ipc-<config.dev_name.cdev_name>
```

Therefore a literal `/dev` basename is not hard-coded in the ELF and is not fabricated here. Up to the source allocator's available minor IDs can be created; teardown deletes each cdev/device and releases the region.

## File operations

- `open`: pins the virtio device, allocates 200-byte downstream state, initializes mutex/waitqueue/completion/RX list, sets DISCONNECTED, creates a channel, and stores it in `file->private_data`.
- `ioctl(TIPC_IOC_CONNECT)`: copies a service name of at most 256 bytes, sends a connect request, then waits interruptibly for a bounded reply. Unknown magic/command returns `-EINVAL`. Compat uses `compat_ptr` before the same handler.
- `read_iter`: returns one complete message. Empty CONNECTED queues block interruptibly; nonblock returns `-EAGAIN`; signal returns `-ERESTARTSYS`; too-small iterator returns `-EMSGSIZE` without consuming.
- `write_iter`: obtains one TX buffer (zero timeout for nonblock), rejects oversized messages, copies one complete message and queues it; returns bytes written.
- `poll`: always advertises `POLLOUT|POLLWRNORM`; adds `POLLIN|POLLRDNORM` for queued RX; adds `POLLERR` when not CONNECTED.
- `release`: marks STALE, wakes waiters, frees pending RX, requests shutdown, destroys channel; final channel release frees downstream state.

No mmap, stream fragmentation/reassembly ABI, or partial-message read is present.
