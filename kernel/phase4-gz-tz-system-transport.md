# `gz_tz_system.ko` — GenieZone transport architecture

Nothing here is assumed. Every component was recovered from the stock import
set and the closed source. The hypervisor / secure-world side is explicitly
**not** reconstructed.

## 1. The transport is TIPC over Trusty, not a raw SMC

`gz_tz_system` reaches GenieZone through **two** sibling modules, which is
exactly what its `depends=gz_ipc_mod,gz_trusty_mod` records:

```
   userspace / other kernel modules
              │  (27 KREE exports)
              ▼
      ┌──────────────────┐
      │  gz_tz_system    │  V:149   THIS MODULE
      └──────────────────┘
         │                    │
         │ 5 tipc_k_* edges   │ 2 trusty_* edges
         ▼                    ▼
   ┌─────────────┐      ┌────────────────┐
   │ gz_ipc_mod  │      │ gz_trusty_mod  │
   │   V:146     │      │    V:145       │
   └─────────────┘      └────────────────┘
         │                    │
         └────────┬───────────┘
                  ▼
          SMC / HVC to EL2
                  ▼
        GenieZone hypervisor  (NOT in scope)
                  ▼
         Trusty / Nebula TEE OS  (NOT in scope)
```

Both providers load **before** it (145, 146 → 149), matching the dependency
direction.

## 2. Imported transport symbols (7 of 50)

### From `gz_ipc_mod` — the TIPC channel layer (5)

| symbol | stock CRC | role |
|---|---|---|
| `tipc_k_connect` | `0x6d3e778c` | open a channel to a named port |
| `tipc_k_disconnect` | `0x389e0025` | tear a channel down |
| `tipc_k_read` | `0xe9bc90dd` | receive a message |
| `tipc_k_write` | `0xd5b2fc22` | send a message |
| `port_lookup_tid` | `0x141326e4` | resolve a port name → TEE id |

### From `gz_trusty_mod` — the SMC layer (2)

| symbol | stock CRC | role |
|---|---|---|
| `trusty_std_call32` | `0x1816bb67` | issue a standard 32-bit Trusty SMC |
| `trusty_enqueue_nop` | `0x0d91978b` | queue a NOP to kick the secure world |

Both provider records are read directly from those modules' own `__kcrctab`
(`stock-provider.provenance.json`). Neither module is reconstructed; they
remain **genuine stock runtime providers** and are a declared, open boundary.

## 3. Named ports

```c
#define GZ_SYS_SERVICE_NAME_TRUSTY "com.mediatek.geniezone.srv.sys"
#define GZ_SYS_SERVICE_NAME_NEBULA "nebula.com.mediatek.geniezone.srv.sys"
#define GZ_MEM_SERVICE_NAME_TRUSTY "com.mediatek.geniezone.srv.mem"
#define GZ_MEM_SERVICE_NAME_NEBULA "nebula.com.mediatek.geniezone.srv.mem"
static char *gz_sys_service_name[] = { …TRUSTY, …NEBULA };
```

Only the two **sys** names appear in the stock `.rodata` — the `mem` service
names are compiled-out constants here because the memory service is reached by
a session the *caller* creates (this is why `com.mediatek.geniezone.srv.mem`
shows up as a string inside `tmem_ffa`, not inside `gz_tz_system`).

`"com.default.tee_id"` is the third and last port-name string, used solely by
`KREE_SessionToTID`'s fallback.

## 4. Channel objects

```c
struct tipc_k_handle { void *dn; … };     /* dn -> struct tipc_dn_chan */
struct tipc_dn_chan  { … enum tee_id_t tee_id; int32_t session; int cpumask; … };
enum tipc_chan_state { TIPC_DISCONNECTED = 0, TIPC_CONNECTING,
                       TIPC_CONNECTED, TIPC_STALE };
```

`_HandleToChanInfo()` is the single accessor turning a handle into a channel.
`chan_p->tee_id` is what selects Trusty vs Nebula for every subsequent
operation; `chan_p->session` carries the *secure-world* session id, distinct
from the Linux handle.

## 5. Message envelope

```c
struct gz_syscall_cmd_param {
        uint32_t command;
        uint32_t paramTypes;
        union MTEEC_PARAM param[4];
        uint32_t payload_size;
        char     data[GZ_MSG_DATA_MAX_LEN];   /* inline payload area */
        …
};
```

The envelope is zeroed with `memset` before every call. `MEM_OUTPUT` /
`MEM_INOUT` buffers are rewritten by `GZ_RewriteParamMemAddr()` to point into
`data[]`, so output memory travels **inline inside the message**, not by
address. `DYNAMIC_TIPC_LEN` is defined, so only `payload_size` bytes are
actually transferred rather than the full fixed buffer.

## 6. Round trip

```
_gz_client_cmd(Fd, session, cmd, param, param_size)
        handle = _FdToHandle(Fd)               /* NULL -> "get tipc handle failed" */
        _tipc_k_write_retry(handle, param, param_size, O_RDWR)

_gz_client_wait_ret(Fd, param)
        _tipc_k_read_retry(handle, param, sizeof(*param), O_RDWR)
```

Both wrappers loop on `_tipc_retry_check_and_wait()`, which retries only on
`-ERESTARTSYS`, sleeps `TIPC_RETRY_WAIT_MS` via `msleep()`, and on exhaustion
logs `"%s: system error, please check(%d)!"` with tag `0` (read) or `1`
(write). The connect path uses tag `2` and calls `tipc_k_disconnect()` before
each retry and once more on final failure.

`_GzServiceCall_body` (1932 B, kCFI `0x3747dee1`) drives the loop: send the
command, then repeatedly read replies, servicing any inbound REE request via
`_Gz_KreeServiceCall_body` until the final result arrives.

## 7. The SMC boundary

```c
int tz_system_std_call32(u32 smcnr, u32 a0, u32 a1, u32 a2)
{ return trusty_std_call32(tz_system_dev->dev.parent, smcnr, a0, a1, a2); }
```

This is the only direct SMC path in the module, and it is why
`tz_system_dev` — the exported `struct platform_device *` — exists: the SMC
must be issued against the **parent** device (the Trusty node), not the
`trusty-tz` child. `trusty_enqueue_nop` is the asynchronous counterpart used
to kick the secure world without blocking.

## 8. Threads and work

| object | purpose |
|---|---|
| `ree_dummy_task` | kthread created in `tz_system_probe` via `kthread_create(ree_dummy_thread, pdev, "ree_dummy_task")`, `set_user_nice(-20)`, then `wake_up_process()` |
| `ree_dummy_event` | `struct completion`, `init_completion` in probe, signalled by the thread |
| `ree_service_threads()` | spawns additional REE-service worker threads on demand, driven by `REE_SERVICE_CMD_NEW_THREAD` / `_64` from the secure world |

`ree_dummy_thread` pins itself with `set_cpus_allowed_ptr(ree_dummy_task,
&ree_cpumask)` and completes `ree_dummy_event`. The imports
`sched_setscheduler`, `set_user_nice`, `set_cpus_allowed_ptr`, `cpu_all_bits`,
`nr_cpu_ids`, `cpu_number`, `_find_first_bit` all serve this CPU-affinity
machinery.

**No workqueues, no tasklets, no timers, no IRQ handlers** exist in this
module — verified by absence from the import set.

## 9. Device-tree binding

```c
#define MODULE_NAME "trusty_tz"
static const struct of_device_id tz_system_of_match[] = {
        { .compatible = "mediatek,trusty-tz", },
        {},
};
MODULE_DEVICE_TABLE(of, tz_system_of_match);
struct platform_driver tz_system_driver = {
        .probe = tz_system_probe, .remove = tz_system_remove,
        .driver = { .name = "trusty_tz", .owner = THIS_MODULE,
                    .of_match_table = tz_system_of_match, },
};
```

Matches the two stock aliases exactly:
`of:N*T*Cmediatek,trusty-tz` and `of:N*T*Cmediatek,trusty-tzC*`.
The node is a **child** of the Trusty node — `pdev->dev.parent` is used for
both `wakeup_source_register()` and `trusty_std_call32()`.

## 10. Lifecycle

`tz_system_probe`:
1. `perf_boost_cnt = 0`
2. `wakeup_source_register(pdev->dev.parent, "KREE_TeeServiceCall")`; on
   failure returns `TZ_RESULT_ERROR_GENERIC`
3. `init_completion(&ree_dummy_event)`
4. create + nice + wake `ree_dummy_task`; on failure logs
   `"Unable to start kernel thread %s"` and propagates `PTR_ERR`
5. `tz_system_dev = pdev`

`tz_system_remove` logs and returns `0` — it does **not** stop the kthread,
release the wake-lock source, or clear `tz_system_dev`. Recorded as observed
stock behaviour; unloading this module is not something the device does.

## 11. Explicitly out of scope

GenieZone hypervisor internals, Trusty/Nebula TEE OS internals, TA code, the
secure-memory manager behind `TZCMD_MEM_*`, and the meaning of any SMC
function number. None of these is present in this module and none was invented.
