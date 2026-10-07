# TKCore normal-world interface (GQ5012BF1)

```
 userspace                       kernel (normal world)                              secure world
 ─────────                       ─────────────────────                              ────────────
 libteec / libTEECommon ─┐
  (keymint, gatekeeper,  │ open/ioctl  /dev/tkcore_client (0660 root:system)
   fp, face, DRM, ...)   ├──────────► tkcore.ko  (contexts, sessions, shm fds,       
 teed (supplicant) ──────┘ /dev/tkcore_admin (0600 system)  read/write mailbox,
                           /dev/tkcore_fp   (0660, no stock userspace opener)       
                                         │  struct tee_ops (tee_tz_fops, 11 slots)
                                         ▼
                           tkcore_drv.ko  ── this component (byte-exact rebuild) ──
                           tz_open/invoke/close/cancel → call_tee → run_tee_task
                           → per-CPU kthread or inline → do_smc (global g_lock)
                           → ptee->invoke_tee ──► invoke_tee_ffa ──► ffa_v10.ko ──FF-A direct req──► EL3 SPMC ─► TKCore OS SP 0x8001
                                                  invoke_tee_smc  (dormant: no DT node)                         (UUID 8bf0ccc3-…-479c)
                           ◄── RPC returns: pool alloc/free, wait queue, sleep, clkmgr,
                               RPMB/supplicant → tee_supp_cmd → teed via /dev/tkcore_admin
```

All `tkcore_drv` behaviour below is proven by the byte-identical rebuild (`parity/`); the
`tkcore.ko` side is cited from the existing TRUSTKERNEL-TEE research
(`kernel/phase4-tkcore-ioctl-uapi.md`, `…-fops-contract.md`, `…-session-contract.md`) and is
**not** reconstructed here.

## Lifecycle

| step | what happens | where |
|---|---|---|
| module init | `pr_info("TrustKernel TEE Driver initialization")`; `ffa_abi_rc = ffa_driver_register(&tkcore_ffa_driver)` (name "tkcore", UUID 8bf0ccc3-…); `smc_abi_rc = platform_driver_register(&tkcore_smc_driver)` ("tzdrv", `trustkernel,tzdrv`); returns `ffa_abi_rc && smc_abi_rc` (i.e. **1**, not an errno, only if both fail) | init_module |
| probe (FF-A on this board) | `tee_tz_new(&ffa_dev->dev, ffa_dev->id, invoke_tee_ffa, build_mem_share_handle_ffa, &tee)`; `ffa_dev_set_drvdata`; "ffa: initialized driver" | tkcore_ffa_probe |
| tee_tz_new | `tee_init_task()` (g_lock, waiters, completion, per-CPU kthreads, cpuhp) → `tee_core_alloc(dev, "tkcoredrv", id, &tee_tz_fops, 0xa0)` → private init → `tee_wait_queue_init` → OS revision (0xf2000001) → log ring (0xf2005705) → `tee_core_add` (tkcore creates the misc devices) → `__tee_get` (refcount 0→1 ⇒ `tz_start`) | tee_tz_new |
| tz_start | reserved window lookup / fallback, cacheable mapping, `tee_shm_pool_create`, `set_cached`, ADD_SHM 0xf2005704 | tz_start |
| remove | `tee_tz_free`: if CAPABLE `tee_wait_queue_exit`; `tee_core_del`; `tee_exit_task` (cpuhp remove, kthread_stop ×N, kfree) | tkcore_ffa_remove / tkcore_smc_remove |
| module exit | "TrustKernel TEE Driver Release"; unregisters **only the driver whose registration failed** (`if (ffa_abi_rc) ffa_unregister…`) — stock quirk, present in the public source too | cleanup_module |

## Operations (`tee_tz_fops`, `.rodata+0x70`, type `"tz"`, KCFI-proven prototypes)

| slot | function | behaviour | errors |
|---|---|---|---|
| start | tz_start | see above | -EINVAL (no tee/priv), -EBUSY (`conf & TEE_CONF_FW_NOT_CAPABLE`), -ENOMEM (no window / map failure), -EINVAL (pool/ADD_SHM failure) |
| stop | tz_stop | not capable → "tee: bad state", -EBUSY; else pool destroy, `iounmap(shm_vaddr)`, started=false | |
| open | tz_open | allocates `teesmc64_arg` (4+meta params) and `teesmc_meta_open_session` from the pool (4 KiB aligned), fills META memref, optional TA-image memref (`tee_shm_pool_v2p` of `cmd->ta`), copies UUID, `clnt_login`, `clnt_uuid`, `set_params`; std call; `get_params`; on non-COMMS result stores `sess->sessid`, `cmd->err/origin` | -1 (WARN, no ctx/tee/priv), -EBUSY (not capable / COMMS), -ENOMEM |
| invoke | tz_invoke | arg with 4 params, `session`, `ta_func`; std call; `get_params` | -1, -EBUSY, TEEC_ERROR_OUT_OF_MEMORY returned as int |
| cancel | tz_cancel | arg (0 params) CANCEL; **fast** call | -EBUSY on COMMS, OUT_OF_MEMORY |
| close | tz_close | CLOSE_SESSION std call | 0 (WARN on missing ctx), -EBUSY |
| alloc | tz_alloc | 0x68-byte `tee_shm`, page-rounded pool allocation, kaddr via p2v, `TEE_SHM_CACHED` flag | NULL (WARN/too big), ERR_PTR(-ENOMEM/-EFAULT) with "tz_alloc: …" logs |
| free | tz_free | pool free, `devm_kfree` when the chunk is gone | WARNs only |
| shm_inc_ref | tz_shm_inc_ref | `tee_shm_pool_incref` (bool → int) | WARNs only |

Parameter conversion (`set_params`/`get_params`): GP types → TEESMC attr (NONE 0, VALUE_IN 1,
VALUE_OUT 2, VALUE_INOUT 3, MEMREF_IN 5, MEMREF_OUT 6, MEMREF_INOUT 7; TEMP/PARTIAL/WHOLE fold
onto MEMREF); memrefs carry the shm **physical** address and `size_req`, plus cache attribute
`(DEFAULT=0xa or NONCACHE=0) << 4` from the pool; unknown type → WARN and attr 0.

## Secure-call engine

* `call_tee(ptee, aff, parg, arg, fid)`: `resp = {a0=fid, a1=parg}`; loop `run_tee_task`; while the
  return is an RPC (`(a0 & 0xffff0000) == 0xffff0000`) run `handle_rpc` and continue with
  return-from-RPC (`(fid & 0x80000000) | 0x72000003`). Final a0 ∉ {0, 0xffffffff} ⇒
  `arg->ret = TEEC_ERROR_COMMUNICATION`, `ret_origin = TEEC_ORIGIN_COMMS`.
* Affinity: `sess->ctx->config ? config->aff : NULL` (NULL → `default_affinity_operations`: never bind).
* `run_tee_task` / `submit_tee_task` / `post_tee_task` (all inlined): if binding is needed, queue a
  `struct tee_task {ptee, param, last_param, entry, done}` on `ctl->tasks`, preferring a CPU whose
  `tkcore_smc_task` is already busy (bit in `cpu_mask`), else the first online CPU accepted by
  `match_cpu` (mark busy, wake its `thread_wq`); if none for 2000 µs, `add_cpu(get_candidate_cpu())`
  and retry, then fall back to running inline. `ETHREAD_LIMIT` (1) parks on `smc_comp`;
  `EAFFINITY` (6) / RPC `BIND_CPU` (0xffff5702) switch to `tee_bind_cpu_request_operations` (mask in a1).
* `do_smc`: every secure entry holds the single global `g_lock`; saves a0/a1 into `last_call`,
  times the call, warns over 1 s (`WARNING SMC[0x%x] %sDURATION %lld us`, "IRQ " for func 4),
  tracks `max_smc_time`, and transparently resumes `RPC_IRQ` returns.
* CPU hotplug: `tee_cpu_prepare_down` refuses (-1) to offline a CPU whose thread is busy and
  re-binds the thread otherwise.

## Notifications / IRQ path

No interrupt handler in this module. Secure → normal notifications are RPC returns (wait-queue
wake, supplicant requests); foreign interrupts surface as `RPC_IRQ` and are resumed. The only
IRQ number it touches is the secure-log IRQ looked up for tkcore (absent in this DT).

## Error propagation

transport error (FF-A rc ≠ 0) → `do_smc` stores rc into a0 → not OK/UNKNOWN → `TEEC_ERROR_COMMUNICATION`
/ `TEEC_ORIGIN_COMMS` → `tz_*` returns -EBUSY → tkcore returns it from the ioctl, with
`err`/`origin` copied to `struct tee_cmd_io`. TA/OS errors travel as `arg->ret`/`ret_origin` →
`cmd->err`/`cmd->origin` with ioctl status 0.
