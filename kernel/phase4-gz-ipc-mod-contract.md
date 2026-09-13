# GQ5012BF1 `gz_ipc_mod` kernel-provider contract

## Scope and proof

This is the Linux TIPC-over-virtio provider used by GenieZone clients; it is not assumed to be another Android TIPC implementation. The contract is `PROVEN_EXACT`: unchanged pinned source reproduces 43/43 function bytes and KCFI IDs, 81/81 imports, and all 15 natural export CRCs.

## Export ABI

| Export | Exact prototype | KCFI | Contract |
|---|---|---:|---|
| `tipc_create_channel` | `struct tipc_chan *(struct device *, const struct tipc_chan_ops *, void *)` | `0x7c7400e4` | pins selected virtio device; allocates disconnected channel and local ID; returns `ERR_PTR` on failure |
| `tipc_chan_get_rxbuf` | `struct tipc_msg_buf *(struct tipc_chan *)` | `0xb494eb7f` | validates channel; allocates shareable receive buffer |
| `tipc_chan_put_rxbuf` | `void (struct tipc_chan *, struct tipc_msg_buf *)` | `0x0d0f1cb3` | returns/frees receive buffer |
| `tipc_chan_get_txbuf_timeout` | `struct tipc_msg_buf *(struct tipc_chan *, long)` | `0xbe9c8928` | obtains free TX buffer, waiting according to timeout |
| `tipc_chan_put_txbuf` | `void (struct tipc_chan *, struct tipc_msg_buf *)` | `0x0d0f1cb3` | returns TX buffer to device free list and wakes senders |
| `tipc_chan_queue_msg` | `int (struct tipc_chan *, struct tipc_msg_buf *)` | `0x95c518e0` | under channel mutex, queues only when CONNECTED; returns `-ENOTCONN`, `-ESHUTDOWN`, or `-EBADFD` by state |
| `tipc_chan_connect` | `int (struct tipc_chan *, const char *)` | `0xdee5bb08` | emits connection control request; DISCONNECTED→CONNECTING; same-service repeated call succeeds; different service gives `-EALREADY`/`-EISCONN` |
| `tipc_chan_shutdown` | `int (struct tipc_chan *)` | `0x6cec3ddc` | emits disconnect request if connecting/connected, then always sets STALE; otherwise `-ENOTCONN` |
| `tipc_chan_destroy` | `void (struct tipc_chan *)` | `0x62d85ff0` | removes channel from device IDR and drops final kref; release callback owns client-private free |
| `port_lookup_tid` | `int (const char *, enum tee_id_t *)` | `0x213d4795` | initializes output to routing-table default, matches first dot-separated service token, preserves default when unmatched |
| `tipc_k_connect` | `int (struct tipc_k_handle *, const char *)` | `0xae9cf010` | route port to TEE, allocate downstream channel, save `h->dn`, send connect request, interruptibly await reply |
| `tipc_k_disconnect` | `int (struct tipc_k_handle *)` | `0x887fdec4` | validates handle, marks STALE/wakes waiters, frees queued RX buffers, shuts down and destroys channel |
| `tipc_k_read` | `ssize_t (struct tipc_k_handle *, void *, size_t, unsigned int)` | `0x642761ad` | one complete queued message per call; blocking wait is interruptible; no truncation |
| `tipc_k_write` | `ssize_t (struct tipc_k_handle *, void *, size_t, unsigned int)` | `0x642761ad` | acquires TX buffer, copies one complete message, applies per-channel CPU affinity, queues or returns buffer on error |
| `tipc_set_default_cpumask` | `int (uint32_t)` | `0xab53c5c9` | rejects zero; masks against possible CPUs for every live TEE; returns last previous mask or `-1` if none |

## Kernel handle and routing

`struct tipc_k_handle` is exactly one pointer (8 bytes), `dn` at offset 0. A successful `tipc_k_connect` stores a 200-byte `tipc_dn_chan` in it. The service name's first token is matched against `tee_routing_config`; `TEE_ID_TRUSTY=0`, `TEE_ID_NEBULA=1`. On malformed/allocation failure `port_lookup_tid` returns an error with output already set to the default; an unmatched valid token returns 0 and leaves that default.

The device association is `vdev_array[tee_id]`. `tipc_open_channel` returns `-ENOENT` when no matching virtio device exists, allocates a downstream channel, initializes mutex/waitqueue/completion/list, sets DISCONNECTED and `cpumask=-1`, then creates the channel.

## Connect/disconnect and wait behavior

Connection waits up to `REPLY_TIMEOUT` via `wait_for_completion_interruptible_timeout`:

- signal: negative wait result is returned unchanged;
- timeout: marks STALE and returns `-ETIMEDOUT`;
- CONNECTED response: 0;
- DISCONNECTED with a queued message: 0, otherwise `-ENOTCONN`;
- any other completed state: `-EIO`.

Disconnect is synchronous on Linux ownership but does not wait for a secure-side acknowledgement. It marks STALE, completes pending connect, wakes readers, frees queued buffers, sends shutdown when possible, removes the channel, and allows the release callback to `kfree(dn)`.

## Read/write behavior

Both kernel calls use whole-message semantics.

`tipc_k_read` locks `dn->lock`. Empty CONNECTED queues block on `readq`; `O_NONBLOCK` returns `-EAGAIN`; a signal returns **`-ERESTARTSYS`**. Non-connected states return `-ENOTCONN` (DISCONNECTED/CONNECTING), `-ESHUTDOWN` (STALE), or `-EBADFD`. If the caller buffer is too small, it returns `-EMSGSIZE` and leaves the message queued. Success copies and consumes exactly one message.

`tipc_k_write` uses `TXBUF_TIMEOUT`, or zero for `O_NONBLOCK`. Invalid downstream/channel addresses return `-EFAULT`; oversized messages return `-EMSGSIZE`; allocation/wait and queue errors propagate. Success returns `len`. The `-ERESTARTSYS` seen by `gz_tz_system` comes naturally from the interruptible wait paths (read, connect completion, or TX-buffer wait) and remains available to its retry layer.

## Buffer ownership

A `tipc_msg_buf` is 56 bytes and owns a virtual address, physical address, size, read/write cursors, and list node. `get_*buf` transfers a buffer to the caller; successful `queue_msg` transfers TX ownership to virtio; failed queue requires `put_txbuf`; receive callback swaps in a fresh RX buffer and queues the filled buffer to the downstream channel; successful read returns it through `put_rxbuf`.

## Virtio lifecycle

Probe reads `tipc_dev_config`, builds a dynamic cdev name `<tee_name>-ipc-<cdev_name>`, selects one or per-CPU TX virtqueues depending on feature/API version, populates RX buffers, records message limits, starts OFFLINE, and derives the default CPU mask through `get_smcnr_dev` + `trusty_fast_call32`. Online/offline control messages transition device/channel state. Remove goes offline, marks DEAD, resets the virtio device, destroys IDRs/queues/buffers, removes cdev, clears `vdev_array`, and drops its kref.
