# `yft_waite_for_finger_dts_paser` contract

The misspelling is stock public ABI and is preserved exactly.

```c
void yft_waite_for_finger_dts_paser(void);
/* CRC 0x4202702c, KCFI 0xa540670c */
```

## Primitive and condition

- primitive: statically initialized `wait_queue_head_t finger_init_waiter`
- condition: global platform-device pointer `yft_finger_plat != NULL`
- timeout: exactly 750 jiffies
- return: `void`; timeout and success are indistinguishable to the caller
- completion object, polling flag, and explicit mutex: none

The disassembly is the inlined `wait_event_timeout(finger_init_waiter,
yft_finger_plat, 750)` pattern using `init_wait_entry`,
`prepare_to_wait_event`, `schedule_timeout`, and `finish_wait`.

If the pointer is already non-NULL, the function returns immediately. Otherwise
each caller gets its own wait entry and sleeps interruptibly only as encoded by
stock `TASK_INTERRUPTIBLE` value 1; wake, condition, timeout, and signal paths
all converge on `finish_wait` and a void return. Repeated callers are allowed.

## Publication and wake point

`yft_finger_plat_probe` stores its `pdev` into `yft_finger_plat` before calling
`yft_finger_get_gpio_info`. That parser invokes:

```c
wake_up_interruptible(&finger_init_waiter);
```

before `devm_pinctrl_get` and before all state lookups. The condition therefore
means “platform probe pointer published”, not “DT/pinctrl parse succeeded.”
The parser can fail after the wake, and platform probe ignores its result.

`remove` clears `yft_finger_plat` but does not wake waiters. There is no ready
status or error status to report.

## Race and load-order behavior

Normal load order is `fingerprint.ko` index 181 followed by
`microarray_fp_tee.ko`. Platform-driver registration/probe is synchronous in
the ordinary boot path, so parsing normally finishes before the consumer loads.
The ABI nevertheless permits a concurrent waiter to wake before pinctrl lookup
completes; that is a stock quirk and is not silently repaired.

Stock `microarray_fp_tee:mas_probe` calls the wait export once at `.text+0x724`,
ignores any result by construction, and immediately begins its board/regulator
setup.
