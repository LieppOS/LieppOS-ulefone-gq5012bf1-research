# GQ5012BF1 TIPC state machine

## Channel states

```text
create/open
    │
    ▼
DISCONNECTED ── connect request queued ──► CONNECTING
     ▲                                          │
     │ remote disconnect / failed response      │ connection response success
     └──────────────────────────────────────────┤
                                                ▼
                                            CONNECTED
                                                │
              local shutdown / timeout / device offline
                                                ▼
                                              STALE
```

All state mutation is under the channel mutex (`tipc_chan.lock`) or downstream mutex (`tipc_dn_chan.lock`) for its mirrored client state.

| From | Trigger | To | Completion/wakeup | Error/result |
|---|---|---|---|---|
| new | channel allocation | DISCONNECTED | none | local ID allocated |
| DISCONNECTED | `tipc_chan_connect`, control message successfully queued | CONNECTING | none | 0 |
| CONNECTING | remote connection response accepted | CONNECTED | `reply_comp` complete | connect wait returns 0 |
| CONNECTING | remote rejection/disconnect | DISCONNECTED | complete + wake readers | `-ENOTCONN` unless queued response exists |
| CONNECTED | remote data message | CONNECTED | enqueue RX + wake `readq` | message retained until one read |
| CONNECTED/CONNECTING | local `tipc_chan_shutdown` | STALE | downstream shutdown completes/wakes | queue result or `-ENOTCONN` |
| any live | `dn_shutdown`, device offline, connect timeout | STALE | complete pending connect + wake all readers | timeout `-ETIMEDOUT`; reads `-ESHUTDOWN` |
| STALE | connect/queue attempted | STALE | none | `-ESHUTDOWN` |
| any | channel destroy | object released | release callback frees downstream state | no reconnect on destroyed object |

## Repeated connect

While CONNECTING or CONNECTED, a connect to the same saved service name returns 0. A different service returns `-EALREADY` while CONNECTING or `-EISCONN` while CONNECTED. STALE channels cannot reconnect; the caller must destroy and create a new channel.

## Control messages

Linux uses control destination 53. Connection request carries a bounded 256-byte service name. Disconnect request carries the remote endpoint. Successful connection records remote endpoint and negotiated message size/count. The report intentionally does not interpret secure-world service semantics.

## Blocking and interruption

- Connect: interruptible completion, bounded by `REPLY_TIMEOUT`; signal propagates the negative wait result; timeout marks STALE and returns `-ETIMEDOUT`.
- Read: while CONNECTED and empty, interruptible waitqueue; `O_NONBLOCK` gives `-EAGAIN`; signal gives **`-ERESTARTSYS`**.
- TX buffer: bounded wait (`TXBUF_TIMEOUT`) or zero with `O_NONBLOCK`; wait/allocation errors propagate.
- A read consumes exactly one complete message. Too-small output returns `-EMSGSIZE` without consuming it.

This exactly preserves the retry-relevant `-ERESTARTSYS` behavior used by `gz_tz_system`.

## Device state

`VDS_OFFLINE=0`, `VDS_ONLINE=1`, `VDS_DEAD=2`.

Virtio probe initializes OFFLINE after queues/buffers exist. Online control marks ONLINE and makes channels usable. Offline marks live channels stale/shutdown and wakes waiters. Remove first goes offline, then under device mutex sets DEAD and clears `vdev`, resets virtio, destroys IDRs/queues/buffers/cdev, and drops references.

## Destruction

Both userspace release and kernel disconnect perform:

1. mark downstream STALE;
2. complete connect waiters and wake readers;
3. free queued RX buffers;
4. request channel shutdown;
5. remove/destroy channel;
6. free `tipc_dn_chan` through `handle_release` on final channel kref.

There is no in-place reconnect after this sequence.
