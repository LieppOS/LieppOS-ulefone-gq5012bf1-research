# `mtk_rpmsg_mbox.ko` — role and behaviour (exact source)

Source: `drivers/rpmsg/mtk_rpmsg_mbox.c`, blob `82ec9c50d3` (MTK ALPS mt6878 `5e415e059253`; same blob as NothingOSS `862ee58`, 2020-06-04). Header `include/linux/rpmsg/mtk_rpmsg.h` blob `2e21c19cb1` (**vendor** header; it shadows GKI's same-named header — see `../reconstruction/README.md`). The local `rpmsg_internal.h` comes from the GKI tree via `ccflags-y += -I$(srctree)/drivers/rpmsg`.

The stock binary is byte-identical to the rebuild except the build-id: 8/8 functions, all data, 14/14 imports, 3/3 exports. See `parity/mtk_rpmsg_mbox/`.

## Functions (stock `.text`, offset/size)

| fn | off | size | role |
|---|---|---|---|
| `mtk_mbox_send` (GPL export) | 0x004 | 0xe8 | TX primitive (below) |
| `mtk_rpmsg_create_channel` (GPL export) | 0x0f0 | 0x170 | `kzalloc(80)`, `info.src = chan_id`, `strlcpy(info.name, name, 32)`. Scans `pin_recv_table` then `pin_send_table` for `chan_id`, filling slot/size/pin index/array index and `mbox`. Never fails after allocation; a missing pin leaves zeros. |
| `mtk_rpmsg_create_device` (GPL export) | 0x264 | 0xa4 | `kzalloc(1016)`; sets `pdev`, `mbdev`, `ops = &mtk_rpmsg_ops`; `rpdev.ops = &mtk_rpmsg_device_ops`, `rpdev.src = ipc_chan_id` (the channel **count**), `dev.parent = &pdev->dev`, `dev.release = mtk_rpmsg_release_device`; then `rpmsg_register_device()`. On failure it calls `kfree` and returns NULL. |
| `mtk_rpmsg_release_device` | 0x30c | 0x1c | device release: `kfree(mdev)` |
| `mtk_rpmsg_create_ept` (+ inlined `__rpmsg_create_ept`) | 0x32c | 0x74 | `kzalloc(112)`; `mdev`, `mchan = priv`; `kref_init`; `ept.rpdev`, `ept.cb = cb` (TinySys passes NULL), `ept.ops = &mtk_rpmsg_endpoint_ops`, `ept.addr = chinfo.src` |
| `mtk_rpmsg_destroy_ept` (+ inlined `__ept_release`) | 0x3a4 | 0x78 | `kref_put` → `kfree(mept)` |
| `mtk_rpmsg_send` | 0x420 | 0x4c | `mdev->ops->mbox_send(mept, mchan, data, len, 1)` |
| `mtk_rpmsg_trysend` | 0x470 | 0x4c | same with `wait = 0`. `wait` is ignored by `mtk_mbox_send`, so the two are identical. |

Data: `mtk_rpmsg_ops` (`.data`, 8 B), `mtk_rpmsg_device_ops` (`.rodata`, 0x28: only `.create_ept`), `mtk_rpmsg_endpoint_ops` (`.rodata`, 0x48: `.destroy_ept/.send/.trysend`). There is no `module_init`/`module_exit`, no platform driver, no PM ops and no IRQ.

## TX path: `mtk_mbox_send(mept, mchan, buf, len, wait)`

1. `WARN_ON(len > mchan->send_slot_size) || WARN_ON(!buf)` → `-EINVAL`. These are the two `__bug_table` entries, at line 32 (which is what pins blob `82ec9c50d3` against `a8a808eb63`).
2. Under `mchan->channel_lock` (irqsave): `mtk_mbox_check_send_irq(mbdev, mchan->mbox, send_pin_index)`. If the bit is still set (the remote has not consumed the last message) → return `MBOX_PIN_BUSY` (1).
3. Lock dropped. `mtk_mbox_write(mbdev, mbox, send_slot, buf, len * 4)`, which copies into mailbox SRAM.
4. `mb()`.
5. `mtk_mbox_trigger_irq(mbdev, mbox, 1 << send_pin_index)` → `MBOX_DONE` (0).

The check→write→trigger sequence is not atomic within this module. Serialisation per pin is the caller's job: `mtk_tinysys_ipi` holds `pin->mutex_send` (WAIT) or `pin->pin_lock` (POLLING) across the whole send.

## RX path

None. Endpoints are created with `cb = NULL` and the module registers no IRQ. Inbound messages go `mtk-mbox` ISR → `mbdev->ipi_cb` (`ipi_isr_cb` in `mtk_tinysys_ipi`), bypassing rpmsg entirely.

## What it adds beyond MTK-MBOX

- A GKI `rpmsg_device` per TinySys processor, on the rpmsg bus. It is named `"<parent>..<count>.0"` (GKI `rpmsg_register_device_override`), and no driver matches it.
- One endpoint per IPI id, plus the id→(mailbox, slot, size, pin) resolution (`mtk_rpmsg_channel_info`).
- The non-blocking "busy-check / write / barrier / doorbell" TX primitive.

Shared memory, interrupts, suspend/resume and timeouts all live in `mtk-mbox` (slots/IRQ) and `mtk_tinysys_ipi` (timeouts), not here.

## Error behaviour

| condition | return |
|---|---|
| `len` > pin size, or `buf == NULL` | `-EINVAL` + WARN splat |
| pin busy | `MBOX_PIN_BUSY` (1) |
| `mtk_mbox_write` failure (bad mbox / slot > size / NULL dev) | `MBOX_PARA_ERR` (−4) / `MBOX_WRITE_SZ_ERR` (−5) / `MBOX_PLT_ERR` (−1) |
| `mtk_mbox_trigger_irq` failure | `MBOX_IRQ_ERR` (−2) / `MBOX_PLT_ERR` |
| `create_*` allocation or registration failure | NULL |
