# `mtk_tinysys_ipi.ko` — TinySys IPI framework (exact source)

Source: `drivers/soc/mediatek/mtk_tinysys_ipi.c` blob `1acca98c7c` (MTK ALPS mt6878 `5e415e059253`; identical blob at NothingOSS `a5b60cb`, 2023-05-31, "[ALPS07693493] scp: chre: Return fake signal"). Header `include/linux/soc/mediatek/mtk_tinysys_ipi.h` blob `2205ab98d8`.

The stock binary is byte-identical to the rebuild except the build-id: 12/12 functions, all data, 28/28 imports, 10/10 exports. See `parity/mtk_tinysys_ipi/`.

## Functions (stock `.text`)

| fn | off | size | export |
|---|---|---|---|
| `ipi_monitor_dump` | 0x004 | 0xf0 | yes |
| `mtk_ipi_device_register` | 0x0f8 | 0x3bc | yes |
| `ipi_isr_cb` | 0x4b8 | 0x104 | static (installed as `mbdev->ipi_cb`) |
| `mtk_ipi_device_reset` | 0x5c0 | 0xf0 | yes |
| `mtk_ipi_register` | 0x6b4 | 0xa8 | yes |
| `mtk_ipi_unregister` | 0x760 | 0xd4 | yes |
| `mtk_ipi_send` | 0x838 | 0x3bc | yes |
| `ipi_monitor` | 0xbf4 | 0x1ec | static |
| `mtk_ipi_recv` | 0xde4 | 0x148 | yes |
| `mtk_ipi_send_compl` | 0xf30 | 0x5bc | yes |
| `mtk_ipi_recv_reply` | 0x14f0 | 0x308 | yes |
| `mtk_ipi_tracking` | 0x17fc | 0x48 | yes |

The exports are plain `EXPORT_SYMBOL` (non-GPL). There is no `module_init`/`exit`, no device, no sysfs/proc/debugfs node and no PM callbacks.

## Registration — `mtk_ipi_device_register(ipidev, pdev, mbox, n)`

Called once per processor by its owner (scp/vcp/gpueb/mcupm). It:

1. returns `-EINVAL` if `!mbox || !n`, or `-ENXIO` if `!ipidev->name`;
2. `kcalloc(n, 96)` the channel table;
3. calls `mtk_rpmsg_create_device(pdev, mbox, n)` (NULL → `IPI_RPMSG_ERR`);
4. for each id `0..n-1`:
   - creates channel `"<name>_ipi#<id>"` and `rpmsg_create_ept(&rpdev, NULL, chan, chan->info)`;
   - marks the stage `UNUSED` and sets `holder = 0`;
5. inits `mutex_ipi_reg`, `lock_monitor`, `ipi_last_done = -1`;
6. for every send pin: inits `mutex_send`, `comp_ack`, `pin_lock`, and links `table[chan_id].pin_send`;
7. for every recv pin: inits `notify`, `pin_lock`, and links `table[chan_id].pin_recv`;
8. sets `mbox->ipi_cb = ipi_isr_cb`, `mbox->ipi_priv = ipidev`, then `ipi_inited = 1`;
9. logs `"%s (with %d IPI) has registered."`.

Source-visible error-path behaviour, not exercised here:

- A channel-create failure frees `mtk_rpdev` (already registered with the driver core) but not the table.
- An `ept == NULL` returns `-EINVAL` without cleanup.

`mtk_ipi_device_reset` clears the stage/seqno for all `rpdev.src` channels and sets `ipi_last_done = -1`. It then calls `mtk_mbox_reset_record()` and sets `ipi_inited = 1`. No shipped module calls it.

## Receive side

- **`mtk_ipi_register(dev, id, cb, prdata, msg)`:**
  - fails with `IPI_DEV_ILLEGAL` if the device is not inited, `IPI_NO_MSGBUF` if `msg` is NULL, `IPI_UNAVAILABLE` if the id has no recv pin, or `IPI_DUPLEX` if `pin_buf` is already set;
  - otherwise stores `cb`, `msg` (as `pin_buf`, the buffer the ISR copies into) and `prdata`, under `mutex_ipi_reg`.
  - `msg` must hold the pin's full `msg_size*4` bytes: the ISR copies the full pin size.
- **`mtk_ipi_unregister`:** `complete(&notify)` to release a waiter, resets stage/seqno, clears cb/buf/prdata.
- **`ipi_isr_cb(pin, priv)`** runs in the mtk-mbox ISR, after the payload has been copied to `pin_buf`:
  - `recv_opt == MESSAGE` → stage `ISR_RECV_MSGV`, `complete(&pin->notify)`;
  - `recv_opt == ACK` → completes only if `holder != 0` (stage `ISR_RECV_ACK`). It reads `holder` from a by-value copy of the `atomic_t`.
- **`mtk_ipi_recv(dev, id)`:** `wait_for_completion_interruptible(&notify)`.
  - An interrupt returns `IPI_FAKE_SIGNAL` (−10): the freezer fake signal during suspend.
  - Otherwise: stage `RECV_MSG`, `ipi_last_done = id`, and if `cb_ctx_opt == MBOX_CB_IN_PROCESS` it calls `cb(id, prdata, pin_buf, msg_size)`.
- **`mtk_ipi_recv_reply(dev, id, reply, len)`:** the same wait, then `pre_cb`, then `rpmsg_trysend` of the reply on the send pin of the same id under `pin_lock` (single attempt), then `post_cb`.

## Send side

Common prologue:

- `IPI_DEV_ILLEGAL` / `IPI_UNAVAILABLE` checks;
- `len > msg_size` → `IPI_NO_MEMORY`; `len == 0` → full pin size (**len is in 32-bit slots**);
- `pre_cb(prdata)`: non-zero → `IPI_PRE_CB_FAIL`.

**Locking and atomic-context rules:**

| `opt` | lock held across send (and the ACK wait for `send_compl`) | context rule |
|---|---|---|
| `IPI_SEND_WAIT` (0) | `pin_send->mutex_send` | `BUG_ON` with `"IPI Panic: … atomic=…"` if `preempt_count() \|\| in_interrupt() \|\| irqs_disabled()` |
| `IPI_SEND_POLLING` (1) | `pin_send->pin_lock` spinlock, **IRQs disabled for the entire send + ACK poll** | `BUG_ON` with `"IPI '%s' has been used in WAIT mode"` if the pin's `mutex_send` is currently held. A pin must not be used in both modes concurrently. |

**`mtk_ipi_send(dev, id, opt, data, len, timeout_ms)`:**

1. Sets `deadline = cpu_clock(0) + timeout_ms*1e6`.
2. Calls `rpmsg_trysend` until it returns 0 or the deadline passes, waiting `udelay(10)` between tries. `trysend_count` counts the attempts.
3. On success: stage `SEND_MSG`, `ipi_last_done = id`.
4. Unlocks, then runs `post_cb`.
5. A pin still busy at the deadline → `ipi_timeout_dump` + `IPI_PIN_BUSY` (−6). Any other error → `IPI_RPMSG_ERR` (−99).

There is no ACK.

**`mtk_ipi_send_compl(dev, id, opt, data, len, timeout_ms)`:**

1. Requires both pins. Increments `holder` and uses the same single deadline as `mtk_ipi_send` for the busy retries **and** the ACK.
2. Send failure → reset `holder`, `post_cb`, return `IPI_PIN_BUSY` or `IPI_RPMSG_ERR`.
3. On success, stage `SEND_MSG`, then wait for the ACK:
   - POLLING: loop `mtk_mbox_polling(mbdev, pin_r->mbox, pin_r->pin_buf, pin_r)` (`MBOX_DONE` means the reply was read directly) and `try_wait_for_completion(&notify)`, with `udelay(10)`, until the deadline;
   - WAIT: `wait_for_completion_timeout(&notify, remaining)`.
4. Resets `holder` to 0.
5. ACK → stage `RECV_ACK`, `ipi_last_done = id`, return 0. Timeout → `mtk_mbox_dump_recv_pin`, `ipi_timeout_dump`, `timeout_handler(id)` if set, return `IPI_COMPL_TIMEOUT` (−7).
6. Unlocks, then `post_cb` (failure overrides the result with `IPI_POST_CB_FAIL`).

On success the reply payload is in the `msg` buffer that was registered for that id.

Observed stock timeouts are in `../protocol/ipi-channel-map.tsv`. The POLLING users are `fhctl` (MCUPM/GPUEB: 10 ms and 3000 ms), `ged` (2000 ms) and `mtk_gpufreq_wrapper` (10000 ms). In those cases the CPU can spin with IRQs off up to that bound if the remote core does not answer.

## Diagnostics

- `ipi_monitor` records per channel `seqno` and three `(stage-index, cpu_clock)` pairs:
  - TX: t0 send, t4 ISR ACK, t5 ACK consumed;
  - RX: t1 ISR msg, t2 consumed, t3 reply sent.
- `ipi_monitor_dump(dev)` prints every non-`UNUSED` channel. Its only caller is `gpueb_plat_ipi_timeout_cb`.
- `mtk_ipi_tracking(dev, en)` toggles `mbdev->log_enable`, which enables per-message `pr_info` here and in mtk-mbox. No caller exists in the image.

## Suspend/resume

There are no PM hooks in this module. The only suspend interaction is `IPI_FAKE_SIGNAL` from interruptible waits being frozen. Processor PM (e.g. `scp_suspend_cb`/`scp_resume_cb` using `mtk_mbox_clr/get_index_record` and `IPI_OUT_SCP_PM_NOTIFY_0/1`) belongs to the owner modules.
