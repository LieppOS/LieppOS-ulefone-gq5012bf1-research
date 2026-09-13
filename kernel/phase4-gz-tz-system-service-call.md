# `gz_tz_system.ko` — `KREE_TeeServiceCall` Linux-side contract

Scope is strictly the Linux encoding/transport path. TA command *semantics*
are not interpreted — no evidence for them exists in this module.

## 1. Prototypes

```c
TZ_RESULT KREE_TeeServiceCall(KREE_SESSION_HANDLE handle, uint32_t command,
                              uint32_t paramTypes, union MTEEC_PARAM param[4]);

TZ_RESULT KREE_TeeServiceCallPlus(KREE_SESSION_HANDLE handle, uint32_t command,
                                  uint32_t paramTypes, union MTEEC_PARAM param[4],
                                  int32_t cpumask);
```

| symbol | CRC | size | kCFI |
|---|---|---:|---|
| `KREE_TeeServiceCall` | `0xec19e146` | 32 | `0xc843babe` |
| `KREE_TeeServiceCallPlus` | `0xf45addc2` | 944 | `0x322755bd` |

`KREE_TeeServiceCall` is a pure thunk:

```c
return KREE_TeeServiceCallPlus(handle, command, paramTypes, param, -1);
```

Its kCFI id `0xc843babe` is shared with `_Gz_KreeServiceCall_body`, confirming
identical 4-argument shape.

## 2. Command and parameter widths

* `command` — `uint32_t`, opaque to Linux; passed through verbatim.
* `paramTypes` — `uint32_t` packing **four 4-bit type codes**, one per slot,
  built by `TZ_ParamTypes(t1,t2,t3,t4)` and read back with
  `TZ_GetParamTypes(types, i)`.
* `param` — a fixed array of exactly **4** `union MTEEC_PARAM`.

```c
enum TZ_PARAM_TYPES {
        TZPT_NONE         = 0,
        TZPT_VALUE_INPUT  = 1, TZPT_VALUE_OUTPUT  = 2, TZPT_VALUE_INOUT  = 3,
        TZPT_MEM_INPUT    = 4, TZPT_MEM_OUTPUT    = 5, TZPT_MEM_INOUT    = 6,
        TZPT_MEMREF_INPUT = 7, TZPT_MEMREF_OUTPUT = 8, TZPT_MEMREF_INOUT = 9,
};
```

Convenience macros `TZ_ParamTypes1/2/3` pad the unused slots with `TZPT_NONE`.

## 3. `union MTEEC_PARAM`

```c
union MTEEC_PARAM {
        struct MTEEC_MEM    mem;     /* { void *buffer; uint32_t size; }   */
        struct MTEEC64_MEM  mem64;   /* { uint64_t buffer; uint32_t size; }*/
        struct MTEEC32_MEM  mem32;
        struct MTEEC_MEMREF memref;
        struct MTEEC_VALUE  value;   /* { uint32_t a, b; }                 */
};
```

The union is unconditional — no `CONFIG_*` alters it, which is why every
export CRC that mentions it is config-stable.

## 4. Call sequence in `KREE_TeeServiceCallPlus`

```c
Fd     = handle;
chan_p = _HandleToChanInfo(_FdToHandle(handle));
if (!chan_p) {                          /* invalid session */
        KREE_ERR("%s: get tipc dn channel failed\n", __func__);
        return TZ_RESULT_ERROR_BAD_PARAMETERS;
}
chan_p->cpumask = cpumask;              /* pass cpumask to the channel */

memset(&cparam, 0, sizeof(cparam));     /* struct gz_syscall_cmd_param */
cparam.command    = command;
cparam.paramTypes = paramTypes;
memcpy(cparam.param, param, sizeof(union MTEEC_PARAM) * 4);

if (cpumask == -1) mutex_lock(&servicecall_lock);
KREE_SESSION_LOCK(Fd);
kree_perf_boost(1);

iret = _GzServiceCall_body(Fd, command, &cparam, param);

kree_perf_boost(0);
KREE_SESSION_UNLOCK(Fd);
if (cpumask == -1) mutex_unlock(&servicecall_lock);

memcpy(param, cparam.param, sizeof(union MTEEC_PARAM) * 4);   /* copy-back */
return iret;
```

Points that matter for a reimplementation:

* **Session validation is by channel lookup**, not by range check alone.
* The caller's `param[4]` is copied *in* before the call and copied *back*
  after — output parameters are written into the caller's array
  unconditionally, even on failure, because the `memcpy` is after the locks and
  before the `return`.
* `cpumask == -1` ⇒ global serialisation. Any other value skips
  `servicecall_lock` and instead pins the work via the channel.
* `KREE_SESSION_LOCK` / `UNLOCK` bracket the call in all cases.

## 5. Performance boost / wake lock

`kree_perf_boost(int on)` keeps a refcount `perf_boost_cnt` under
`perf_boost_lock`:

* first `on` (`perf_boost_cnt++ == 0`) → `__pm_stay_awake(TeeServiceCall_wake_lock)`
* last `off` (`perf_boost_cnt-- == 1`) → `__pm_relax(TeeServiceCall_wake_lock)`

Both arms are inside `#if IS_ENABLED(CONFIG_PM_SLEEP)`, which stock has on.
This is why the module imports `__pm_stay_awake` / `__pm_relax` /
`wakeup_source_register`.

## 6. Marshalling helpers

### `make_64_params_local(union MTEEC_PARAM *dst, uint32_t types)`

For every slot typed `TZPT_MEM_INPUT|MEM_INOUT|MEM_OUTPUT`, converts the
native pointer form into the explicit 64-bit form:

```c
addr = (long)dst[i].mem.buffer;
high = ((uint64_t)addr >> 32) << 32;
low  = addr & 0xffffffff;
dst[i].mem64.buffer = high | low;
dst[i].mem64.size   = dst[i].mem.size;
```

This normalises the pointer so the secure world always sees a 64-bit address
regardless of the caller's pointer width.

### `GZ_RewriteParamMemAddr(struct gz_syscall_cmd_param *param)`

For every slot typed `TZPT_MEM_OUTPUT` or `TZPT_MEM_INOUT`, repoints the
buffer into the message's own inline `data[]` payload area:

```c
size = param_p[i].mem.size;        /* GZ uses mem, not mem64, here */
param_p[i].mem.buffer = &(param->data[offset]);
param_p[i].mem.size   = size;
if (offset >= GZ_MSG_DATA_MAX_LEN) { KREE_ERR("CMTB: ERR: buffer overflow\n"); break; }
```

So **output memory travels inline inside the message envelope**, not by
address. The overflow guard is a `break`, i.e. remaining parameters are left
unrewritten and the call still proceeds — recorded as observed behaviour.

## 7. Transport body — `_GzServiceCall_body`

1932 bytes in stock, kCFI `0x3747dee1`. It performs the write/read round trip
over TIPC through `_gz_client_cmd` and `_gz_client_wait_ret`, and dispatches
inbound **REE service requests** from the secure world through
`_Gz_KreeServiceCall_body` (see §8). Full transport detail in
`kernel/phase4-gz-tz-system-transport.md`.

## 8. Reverse direction — `_Gz_KreeServiceCall_body`

The secure world can call *back* into Linux during a service call. Handled
commands (all from `REE_SERVICE_CMD_*`):

| command | Linux action |
|---|---|
| `REE_SERVICE_CMD_ADD` | `param[2].value.a = param[0].value.a + param[1].value.a` |
| `REE_SERVICE_CMD_MUL` | `param[2].value.a = param[0].value.a * param[1].value.a` |
| `REE_SERVICE_CMD_NEW_THREAD` | `ree_service_threads(1, …)` |
| `REE_SERVICE_CMD_NEW_THREAD_64` | `ree_service_threads(2, …)` |
| `REE_SERVICE_CMD_TEE_INIT_CTX` | `TEEC_InitializeContext(param[0].mem.buffer, param[1].mem.buffer)` |
| `REE_SERVICE_CMD_TEE_FINAL_CTX` | `TEEC_FinalizeContext(param[0].mem.buffer)` |
| `REE_SERVICE_CMD_TEE_OPEN_SE` | `TEEC_OpenSession(…)` |
| `REE_SERVICE_CMD_TEE_CLOSE_SE` | `TEEC_CloseSession(…)` |
| `REE_SERVICE_CMD_TEE_INVOK_CMD` | `TEEC_InvokeCommand(…)` |

The last five exist only under `CONFIG_TEE` and are exactly the call sites
that require the five WEAK `TEEC_*` stubs. Because `gz_tz_system` does **not**
link against `tkcore`, the weak definitions are the ones that bind at load
time: on this device those GenieZone→TEE bridge commands are **accepted and
silently no-op'd** (return `0` / `TEEC_SUCCESS`). That is the shipped
behaviour, and it is now reproduced byte-identically.

## 9. Return-value propagation

`_GzServiceCall_body`'s return is passed straight out of
`KREE_TeeServiceCallPlus` with no remapping. `TZ_RESULT` values are the
`TZ_RESULT_*` family from `tz_cross/trustzone.h`; `TZ_RESULT_SUCCESS == 0`.
Failures logged in this path:

* `"%s: get tipc dn channel failed"` → `TZ_RESULT_ERROR_BAD_PARAMETERS`
* `"%s: wait ret failed(%d)"` → from `_gz_client_wait_ret`
* `" invalid gp params"` / `" invalid input gp params in service call"`

## 10. What is deliberately NOT documented

The meaning of any `command` value handed to a TA, the layout of TA-specific
payloads, and anything executing in GenieZone/secure world. No evidence for
those exists in this module and none was invented.
