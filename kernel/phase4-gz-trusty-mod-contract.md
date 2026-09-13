# GQ5012BF1 `gz_trusty_mod` Linux contract

## Scope and proof

This closes the Linux provider ABI of all 14 exports. It does not interpret secure-world SMC numbers. The contract is `PROVEN_EXACT`: pinned source is unchanged and all 33 stock functions are byte/KCFI identical.

## Export ABI

| Export | Exact prototype | KCFI | Linux-visible behavior |
|---|---|---:|---|
| `get_smcnr_dev` | `uint32_t (enum smc_functions fid, struct device *dev)` | `0x8110f113` | obtains `trusty_state` from platform drvdata and maps `(fid, tee_id)` through the fixed SMC-number table |
| `trusty_fast_call32` | `s32 (struct device *, u32, u32, u32, u32)` | `0x97633315` | `-EINVAL` for null/error device; validates fast/32-bit shape with WARNs; invokes AArch64 `arm_smccc_smc`; no mutex and no sleeping |
| `trusty_std_call32` | `s32 (struct device *, u32, u32, u32, u32)` | `0x97633315` | serialized by `smc_lock` except NOP; notifier/IRQ bracket; retries busy/interrupted/CPU-idle returns; may sleep; returns secure-call result unchanged |
| `trusty_call_notifier_register` | `int (struct device *, struct notifier_block *)` | `0xada9d28e` | `-EINVAL` for invalid device; registers on atomic call notifier |
| `trusty_call_notifier_unregister` | same | `0xada9d28e` | unregisters from atomic call notifier |
| `trusty_callback_notifier_register` | `int (struct device *, struct notifier_block *)` | `0xada9d28e` | registers on blocking callback notifier |
| `trusty_callback_notifier_unregister` | same | `0xada9d28e` | unregisters from blocking callback notifier |
| `trusty_adjust_task_attr` | `int (struct device *, struct trusty_task_attr *)` | `0x2c37d833` | emits blocking callback `TRUSTY_CALLBACK_VIRTIO_WQ_ATTR`; returns 0 after valid device |
| `trusty_dump_systrace` | `int (struct device *, void *)` | `0xadc2f417` | compiled stock branch is an 8-byte no-op returning 0 because trace dump is hard-disabled |
| `trusty_version_str_get` | `const char * (struct device *)` | `0x4a1e8ad3` | invalid device gives `ERR_PTR(-EINVAL)`; otherwise returns device-managed version string, possibly NULL after probe retrieval failure |
| `trusty_get_api_version` | `u32 (struct device *)` | `0xaf9454d4` | invalid device returns the unsigned representation of `-EINVAL`; otherwise returns negotiated API version |
| `trusty_enqueue_nop` | `void (struct device *, struct trusty_nop *, int cpu)` | `0x2650b66a` | selects current/explicit possible CPU with preemption disabled; conditionally queues one NOP under `nop_lock`; completes that CPU thread's `run` completion |
| `trusty_dequeue_nop` | `void (struct device *, struct trusty_nop *)` | `0xc324ddc5` | validates pointers; removes queued node under irqsave `nop_lock`; no wait |
| `trusty_nop_set_switch_pri` | `int (uint32_t policy)` | `0xab53c5c9` | stock `DYNAMIC_SET_PRIORITY` branch is off; function returns 0 for every value; GPL-only export |

All export CRCs are in `phase4-gz-trusty-mod-exports.tsv`; all are reproduced naturally.

## Standard-call path

1. Reject null/error `dev` with `-EINVAL`; fetch `trusty_state` from platform drvdata.
2. WARN if the number is fast or 64-bit.
3. For non-NOP calls, lock `smc_lock` and reinitialize `cpu_idle_completion`. NOP calls deliberately avoid this mutex.
4. `trusty_std_call_helper` disables local IRQs, emits `TRUSTY_CALL_PREPARE`, calls the SMC loop, emits `TRUSTY_CALL_RETURNED`, then reenables IRQs.
5. `trusty_std_call_inner` restarts FIQ-interrupted calls and performs five immediate busy retries. The outer helper then retries busy results indefinitely with `msleep()` exponential backoff from 1 ms, capped by the `<1000` doubling condition.
6. Trusty and Nebula interrupted/CPU-idle values follow their source-selected restart paths. CPU-idle waits up to `HZ/5` on `cpu_idle_completion` before retrying.
7. A panic result triggers `WARN_ONCE` but is returned. NOP completion signals `cpu_idle_completion`; non-NOP unlocks `smc_lock`.

**Context rule:** `trusty_fast_call32` is atomic/non-sleeping; `trusty_std_call32` may sleep and must not be called from atomic context.

## NOP representation and lifecycle

`struct trusty_nop` is 32 bytes on the exact arm64 build: list node at 0, three `u32` arguments at 16. Each possible CPU receives a 104-byte `nop_task_info` with `run` and `rdy` completions and a private list; all lists share `trusty_state.nop_lock`.

Probe creates and binds `id<tee>_trusty_n/<cpu>` threads. API versions below SMP use the locked-NOP function; newer versions drain per-CPU lists. A worker calls `trusty_std_call32`, translates only source-named interrupted/done statuses, drains until neither queued work nor an interrupted result remains, then emits the callback notifier. Teardown marks each index `-1` and completes `run`; device-managed allocations own the records.

## Device lifecycle

Probe requires an OF node and `tee-id` 0 or 1, allocates/initializes `trusty_state`, installs platform drvdata, initializes SMC-number/API/version state, creates NOP threads and poll worker, populates child platform devices, and exposes `trusty_version` only if version retrieval succeeds. Remove unregisters children, frees poll/NOP execution, destroys the SMC mutex, and removes the attribute.

Drivers:

- `android,trusty-smc-v1` → `trusty`
- `android,nebula-smc-v1` → `nebula`

Module init registers Trusty then Nebula; exit unregisters Trusty then Nebula exactly as source.
