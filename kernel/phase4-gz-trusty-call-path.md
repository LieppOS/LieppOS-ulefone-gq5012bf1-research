# GQ5012BF1 Trusty call and NOP path

## Fast call

`trusty_fast_call32(dev, smcnr, a0, a1, a2)` validates the device and call shape, then directly executes `arm_smccc_smc`. It takes no module mutex, does not sleep, and returns register `a0` as signed 32-bit. The AArch64 SMCCC wrapper supplies the architectural call boundary; the source adds no separate explicit memory-barrier instruction.

## Standard call

```text
trusty_std_call32
  ├─ validate dev / fetch trusty_state
  ├─ non-NOP: mutex_lock(smc_lock), reinit cpu_idle_completion
  ├─ trusty_std_call_helper
  │    ├─ local_irq_disable
  │    ├─ atomic notifier TRUSTY_CALL_PREPARE
  │    ├─ arm_smccc_smc retry loop
  │    ├─ atomic notifier TRUSTY_CALL_RETURNED
  │    └─ local_irq_enable
  ├─ TEE-specific interrupted/CPU-idle restart loop
  ├─ panic WARN_ONCE
  └─ NOP: complete(cpu_idle_completion)
       non-NOP: mutex_unlock(smc_lock)
```

The inner loop handles FIQ interruption and five immediate busy retries. Persistent busy results return to the helper, which sleeps 1 ms and doubles the delay while below 1000 ms. Therefore standard calls may sleep. CPU-idle responses wait up to `HZ/5` for completion and then retry even after timeout.

The atomic notifier runs with local IRQs disabled; callbacks must obey atomic context. The blocking callback notifier is used separately for task-attribute and systrace events.

## NOP submission

`trusty_enqueue_nop(dev, nop, cpu)`:

1. ignores null/error devices;
2. disables preemption;
3. chooses current CPU for negative/impossible CPU, otherwise the requested possible CPU;
4. when a request object is supplied, requires SMP-NOP API by WARN, then under irqsave `nop_lock` queues it only if its list node is empty;
5. completes that CPU's `run` completion and reenables preemption.

A NULL request is valid: it wakes the target NOP thread without adding a list node.

`trusty_dequeue_nop` removes a caller-owned request if queued, under the same irqsave spinlock. It does not wait for execution.

## Per-CPU worker

Probe allocates one `nop_task_info` per possible CPU and creates a bound `id<tee>_trusty_n/<cpu>` kthread. Each thread completes `rdy`, waits interruptibly on `run`, executes either locked-NOP (old API) or list-draining NOP (SMP API), and self-migrates back if observed on the wrong online CPU.

The SMP worker dequeues three arguments, issues the source-selected NOP SMC, translates only the named interrupted/done return codes, and continues while another request exists or the result requires continuation. It then invokes `TRUSTY_CALLBACK_SYSTRACE` with NULL. Queue/list ordering is protected by `nop_lock`; completions provide wakeup ordering. No separate explicit barrier appears in this path.

## Poll worker

The source creates `trusty_poll_task` and a `trusty_poll_work` item that can request a CPU mask through a fast call and wake per-CPU NOP threads. However, the `trusty_call_notifier_register` block in `trusty_poll_create` is commented out in this exact revision. This fact is preserved exactly; no claim is made that the internal notifier automatically schedules this worker.

## Probe/remove lifecycle

Probe reads `tee-id`, installs state before initial SMC use, verifies the SMC-number-table API, retrieves version/API, creates NOP and poll threads, then populates DT children. Failures unwind children, version sysfs state, workers, and mutex in source order. Remove unregisters children, stops workers/threads, destroys the mutex, and removes `trusty_version` when created.

This is the complete Linux-side architecture. Secure-world dispatch and function-number semantics beyond source names remain out of scope.
