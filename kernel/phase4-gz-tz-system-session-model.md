# `gz_tz_system.ko` — session and handle model

Everything below is Linux-side only, recovered from the closed source and
confirmed byte-identical against stock. No secure-world internals are inferred.

## 1. What a `KREE_SESSION_HANDLE` actually is

```c
typedef int32_t KREE_SESSION_HANDLE;
```

It is **not** a pointer and **not** a secure-world id. It is an index into a
module-global array, with two reserved values layered on top:

```c
#define KREE_SESSION_HANDLE_MAX_SIZE  (512)
#define KREE_SESSION_HANDLE_SIZE_MASK (511)
#define KREE_SESSION_HANDLE_TRUSTY    (512)          /* 512 + TEE_ID_TRUSTY */
                                                     /* 512 + TEE_ID_NEBULA */
```

| handle range | meaning |
|---|---|
| `0 … 511` | index into `_kree_session_handle_pool[]` — a normal TA session |
| `512 + TEE_ID_TRUSTY` | the per-TEE **system service** channel (Trusty) |
| `512 + TEE_ID_NEBULA` | the per-TEE **system service** channel (Nebula) |
| anything else | rejected by `_getSessionHandle` with `-1` |

## 2. Global state

```c
static struct tipc_k_handle _kree_session_handle_pool[512];  /* session table */
static uint32_t             _kree_session_handle_idx;        /* rotating cursor */
static int32_t              _sys_service_Fd[TEE_ID_END] = { [0 … ] = -1 };
static struct tipc_k_handle _sys_service_h[TEE_ID_END];
static char *gz_sys_service_name[] = {
        "com.mediatek.geniezone.srv.sys",
        "nebula.com.mediatek.geniezone.srv.sys",
};
struct platform_device *tz_system_dev;      /* EXPORTED */
struct task_struct     *ree_dummy_task;
struct wakeup_source   *TeeServiceCall_wake_lock;   /* CONFIG_PM_SLEEP */
```

State is **global per-module**, not per-process and not per-file-descriptor.
There is no `struct file` private data anywhere — this module has no character
device (see the userspace-ABI report).

## 3. Locks

| lock | protects |
|---|---|
| `fd_mutex` | the 512-slot session table (`_setSessionHandle` / `_clearSessionHandle`) |
| `session_mutex` | whole-session lifecycle: `KREE_CreateSession`, `KREE_CloseSession` |
| `servicecall_lock` | global serialisation of `KREE_TeeServiceCallPlus` when `cpumask == -1` |
| `perf_boost_lock` | the `perf_boost_cnt` refcount and the wake-lock |
| `chmem_mutex` | multi-chunk append/release |
| `shared_mem_mutex_trusty`, `shared_mem_mutex_nebula` | per-TEE shared-memory registration |

All are plain `DEFINE_MUTEX`; no spinlocks, no RCU, no atomics in the session
path.

## 4. Allocation — `_setSessionHandle`

Rotating linear scan for a free slot, under `fd_mutex`:

```c
for (i = 0; i < 512; i++) {
        if (_kree_session_handle_pool[_kree_session_handle_idx].dn == 0) break;
        _kree_session_handle_idx = (_kree_session_handle_idx + 1) % 512;
}
if (i == 512) { KREE_ERR("can not get empty slot for session!"); return -1; }
_kree_session_handle_pool[_kree_session_handle_idx].dn = h.dn;
session = _kree_session_handle_idx;
_kree_session_handle_idx = (_kree_session_handle_idx + 1) % 512;
```

* A slot is "free" iff its `.dn` pointer is `NULL`. `.dn` is the
  `struct tipc_dn_chan *` for the channel.
* **Recovered defect, stated as fact, not speculation:** the exhaustion path
  `return -1` happens **without** `mutex_unlock(&fd_mutex)`. If all 512 slots
  are ever occupied the module deadlocks on `fd_mutex`. This is present in the
  stock binary too — it is a property of the shipped device, not of the
  reconstruction. Out of scope to fix here; recorded for the later island work.

## 5. Lookup — `_getSessionHandle` / `_FdToHandle` / `_HandleToChanInfo`

```c
int _getSessionHandle(int32_t session, struct tipc_k_handle **h)
{
        if (session == 512 + TEE_ID_TRUSTY)      *h = &_sys_service_h[TEE_ID_TRUSTY];
        else if (session == 512 + TEE_ID_NEBULA) *h = &_sys_service_h[TEE_ID_NEBULA];
        else if (session >= 0 && session < 512)  *h = &_kree_session_handle_pool[session];
        else return -1;
        return 0;
}
struct tipc_dn_chan *_HandleToChanInfo(struct tipc_k_handle *h)
{ return h ? (struct tipc_dn_chan *)(h->dn) : NULL; }
```

Lookup is **unlocked** — only allocation and clearing take `fd_mutex`. Invalid
handles return `NULL`, which every caller turns into
`TZ_RESULT_ERROR_BAD_PARAMETERS` after logging
`"%s: NULL chan_p, invalid Fd"`.

## 6. Release — `_clearSessionHandle`

```c
void _clearSessionHandle(uint32_t session)
{ mutex_lock(&fd_mutex); _kree_session_handle_pool[session].dn = 0; mutex_unlock(&fd_mutex); }
```

Slot reuse is immediate. There is **no reference counting** on sessions: the
table stores a raw channel pointer, not a `kref`. Ownership of the channel
belongs to the TIPC layer (`gz_ipc_mod`).

## 7. Create sequence (`KREE_CreateSession`)

1. reject `NULL` `ta_uuid` / `pHandle` → `TZ_RESULT_ERROR_BAD_PARAMETERS`
2. `mutex_lock(&session_mutex)`
3. `KREE_OpenFd(ta_uuid, &chan_fd)` — TIPC connect to the TA's port, with the
   retry wrapper below
4. `chan_p = _HandleToChanInfo(_FdToHandle(chan_fd))`; `tee_id = chan_p->tee_id`
5. if `_sys_service_Fd[tee_id] < 0`, lazily `KREE_OpenSysFd(tee_id)` — the
   per-TEE system service channel is opened **once** for the module's lifetime
6. issue the session-create service call on the system channel
7. publish the handle to `*pHandle`
8. single exit label `create_session_out` → `mutex_unlock(&session_mutex)`

## 8. Close sequence (`KREE_CloseSession`)

1. `mutex_lock(&session_mutex)`
2. `chan_p = _HandleToChanInfo(_FdToHandle(handle))`; `NULL` →
   `TZ_RESULT_ERROR_BAD_PARAMETERS`
3. validate `is_tee_id(tee_id)` **and** `_sys_service_Fd[tee_id] >= 0`;
   otherwise `TZ_RESULT_ERROR_GENERIC` with `"sys service fd is not open."`
4. `p[0].value.a = chan_p->session;`
   `KREE_TeeServiceCall(_sys_service_Fd[tee_id], TZCMD_SYS_SESSION_CLOSE,
   TZ_ParamTypes1(TZPT_VALUE_INPUT), p)`
5. TIPC disconnect, then `_clearSessionHandle(Fd)`
6. single exit label `close_session_out` → `mutex_unlock(&session_mutex)`

Note the asymmetry that is real and worth recording: the *secure-world*
session id lives in `chan_p->session`, while the *Linux* handle is the table
index. They are different numbers.

## 9. Connection retry policy

`_tipc_retry_check_and_wait(err, retry_cnt, tag)`:

* retries only when `IS_RESTARTSYS_ERROR(err)` (i.e. `-ERESTARTSYS`)
* sleeps `TIPC_RETRY_WAIT_MS` via `msleep()` between attempts
* on exhaustion logs `"%s: system error, please check(%d)!"` and gives up
* tags: `0` = read, `1` = write, `2` = connect

Wrappers: `_tipc_k_read_retry`, `_tipc_k_write_retry`, and the connect loop
which calls `tipc_k_disconnect` before each retry and once more on final
failure.

## 10. Channel-state guard

```c
enum tipc_chan_state { TIPC_DISCONNECTED = 0, TIPC_CONNECTING, TIPC_CONNECTED, TIPC_STALE };
static bool _is_tipc_channel_connected(struct tipc_dn_chan *dn);
```

Used to avoid issuing calls on a stale channel.

## 11. `KREE_SESSION_LOCK` / `KREE_SESSION_UNLOCK`

Present as functions in the stock binary but **not exported**. They resolve
the handle to a channel and take a per-channel lock, letting a caller batch
several service calls on one session.

## 12. `KREE_SessionToTID`

```c
TZ_RESULT KREE_SessionToTID(KREE_SESSION_HANDLE session, enum tee_id_t *o_tid);
```

Returns the channel's `tee_id`. On an invalid handle it does **not** fail
silently: it falls back to `port_lookup_tid("com.default.tee_id", o_tid)`,
logs `"session %d to tee id failed, return default %d"`, and returns
`TZ_RESULT_ERROR_NO_DATA` — so the out-parameter is still populated. This is
the only consumer of the `port_lookup_tid` import and the only use of the
`com.default.tee_id` string.

## 13. Concurrency summary

* Session create/close: fully serialised by `session_mutex`.
* Service calls with `cpumask == -1` (i.e. every `KREE_TeeServiceCall`):
  fully serialised by `servicecall_lock`.
* Service calls with an explicit cpumask (`KREE_TeeServiceCallPlus`) skip that
  lock — this is the only concurrency the design allows.
* Table mutation is `fd_mutex`-protected; table *reads* are not, which is safe
  only because slots are never freed while a call is in flight on them.

## 14. Multi-TEE support

`TEE_ID_TRUSTY` and `TEE_ID_NEBULA` are both compiled in
(`gz_sys_service_name[]` has both entries and both strings are present in the
stock ELF). Which one a session uses is decided by the TA's port name at
connect time, not by a config.
