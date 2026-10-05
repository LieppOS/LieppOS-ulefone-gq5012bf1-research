# TinySys IPC structures (AP side) — GQ5012BF1

## Evidence model

- The rebuilt `mtk_rpmsg_mbox.ko` and `mtk_tinysys_ipi.ko` are byte-identical to stock except the 20-byte build-id (see `../kernel/parity/`). The DWARF of the unstripped rebuild (`pahole`) therefore describes the stock layout exactly.
- Spot checks against **stock** instruction immediates:
  - `kmalloc_trace(.., 0x50)` in `mtk_rpmsg_create_channel` → `sizeof(mtk_rpmsg_channel_info)` = 80.
  - `ldr [x,#0x3f0]` → `mtk_rpmsg_device.mbdev` @1008.
  - `ldr [x,#0x3c0]` → `rpmsg_device.src` @960.
  - `mov #0x60` → `mtk_ipi_chan_table` stride 96.
  - `mov #0x68` → `mtk_mbox_pin_send` stride 104.
  - `add #0x78` → `mtk_ipi_device.lock_monitor` @120.
- Field meanings are only stated where the source code that reads or writes the field is exact (this module pair, or `mtk-mbox`/`scp`, which are closed). Anything else is marked.
- **Firmware-side structures** (inside SCP/VCP/GPUEB/MCUPM images) are not described here. The wire format is "N 32-bit slots at a fixed SRAM offset", and slot contents are defined per channel by each client driver, not by this transport.

## 1. On the wire: mailbox slots (direct mode)

| item | value | evidence |
|---|---|---|
| unit | 1 slot = 4 bytes (`MBOX_SLOT_SIZE`) | `mtk-mbox.h:18`; `mtk_mbox_send` writes `len * MBOX_SLOT_SIZE` bytes |
| **`len` in `mtk_ipi_send*`** | **number of 32-bit slots, not bytes**; `0` means the pin's full `msg_size` | `mtk_ipi_send`: `if (!len) len = pin->msg_size`; `mtk_mbox_send`: `WARN_ON(len > mchan->send_slot_size)` |
| AP→core message | `mtk_mbox_write(mbdev, mbox, send_slot, buf, len*4)` at SRAM `info_table[mbox].base + send_slot*4`, then `writel(1 << send_pin_index, set_irq_reg)` | `mtk_rpmsg_mbox.c` `mtk_mbox_send` |
| busy rule | Before writing, the pin's bit in `send_status_reg` (or `set_irq_reg`) must be 0, i.e. the remote has consumed the last message. Otherwise `MBOX_PIN_BUSY` (=1). | `mtk_mbox_check_send_irq` |
| ordering | `mb()` between the SRAM write and the IRQ trigger | `mtk_rpmsg_mbox.c` |
| core→AP message | The mtk-mbox ISR reads `recv_status`. For each recv pin whose bit is set, it copies `msg_size*4` bytes from `base + offset*4` into the registered `pin_buf`, optionally runs the ISR-context callback, then calls `mbdev->ipi_cb` (`ipi_isr_cb`). | `mtk-mbox.c` `mtk_mbox_isr` |
| header | **none** in direct/SMEM mode. `struct mtk_ipi_msg_hd` (queue mode) is unused by every TinySys-IPI processor on this board: SCP/VCP `opt` = 0 (`MBOX_OPT_DIRECT`), GPUEB `MBOX_OPT_SMEM`. MCUPM's table is static. | `scp_helper.c` / `vcp_helper.c` / `gpueb_ipi.c` table init |

Slot offsets per mailbox are computed by the owner driver:

- **SCP/VCP** (`is64d=1`): `mbox_setup_pin_table()`. Pins are packed in send-then-recv order. Each pin uses `ceil(size/2)` 64-bit pin-index units, and `offset = 2*pin_index`. The limit is 32 pin indices / 64 slots per mailbox.
- **GPUEB** (`is64d=0`): `pin_index = chan_id`, with offsets laid out sequentially.
- **MCUPM:** compile-time constants.

The resulting numbers for this board are in [`ipi-channel-map.tsv`](ipi-channel-map.tsv).

## 2. `struct mtk_rpmsg_channel_info` (80 B) — `mtk_rpmsg_mbox`, one per IPI id

| off | size | field | meaning | producer → consumer |
|---|---|---|---|---|
| 0 | 40 | `info` (`rpmsg_channel_info`: `name[32]`@0, `src`@32, `dst`@36) | `name` = `"<dev>_ipi#<id>"`, `src` = IPI id, `dst` = 0 | `mtk_rpmsg_create_channel` → `rpmsg_create_ept(chinfo)`; `name` is printed by `mtk_ipi_*` error paths |
| 40 | 4 | `send_slot` | SRAM slot offset of the send pin | create_channel (from `pin_send_table[i].offset`) → `mtk_mbox_send` |
| 44 | 4 | `recv_slot` | recv pin slot offset | create_channel → (unused by any shipped code) |
| 48 | 4 | `send_slot_size` | send pin size in slots | → `WARN_ON(len > …)` in `mtk_mbox_send` |
| 52 | 4 | `recv_slot_size` | recv pin size | unused at runtime |
| 56 | 4 | `send_pin_index` | IRQ bit of the send pin | → busy check, trigger |
| 60 | 4 | `recv_pin_index` | IRQ bit of recv pin | unused at runtime |
| 64 | 4 | `send_pin_offset` | index in `pin_send_table` | unused at runtime |
| 68 | 4 | `recv_pin_offset` | index in `pin_recv_table` | unused at runtime |
| 72 | 4 | `mbox` | mailbox number. If an id has both pins, the **send** pin's mailbox wins (second loop) | → all `mtk_mbox_*` calls |
| 76 | 4 | `channel_lock` | spinlock around the busy check only | `mtk_mbox_send` |

## 3. `struct mtk_rpmsg_endpoint` (112 B)

| off | size | field | meaning |
|---|---|---|---|
| 0 | 96 | `ept` (GKI `rpmsg_endpoint`: `rpdev`@0, `refcount`@8, `cb`@16 (**NULL**: TinySys passes no rx cb), `cb_lock`@24, `addr`@72 (= IPI id), `priv`@80 (not set), `ops`@88 (= `mtk_rpmsg_endpoint_ops`)) | handle stored in `mtk_ipi_chan_table.ept` |
| 96 | 8 | `mdev` | owning `mtk_rpmsg_device` |
| 104 | 8 | `mchan` | its `mtk_rpmsg_channel_info` (passed as `priv` to `create_ept`) |

`mtk_rpmsg_endpoint_ops` (`.rodata`, 0x48 B) has only `.destroy_ept`, `.send` and `.trysend`. Both send variants call `mdev->ops->mbox_send(mept, mchan, data, len, wait)` and `wait` is ignored.

## 4. `struct mtk_rpmsg_device` (1016 B), `struct mtk_rpmsg_operations` (8 B)

| off | size | field | meaning |
|---|---|---|---|
| 0 | 992 | `rpdev` (GKI `rpmsg_device`) | Registered on the rpmsg bus with `rpmsg_register_device()`. `src`@960 = **channel count** (read back by `ipi_monitor_dump`/`mtk_ipi_device_reset`). `dst` = 0, `id.name` empty, `ops`@984 = `mtk_rpmsg_device_ops` (`.create_ept` only). Device name per GKI `rpmsg_register_device_override`: `"<parent>..<count>.0"`. No rpmsg driver binds it. |
| 992 | 8 | `pdev` | owner platform device (scp/vcp/gpueb/mcupm) |
| 1000 | 8 | `ops` | → `mtk_rpmsg_ops` (`.data`, 8 B: `.mbox_send = mtk_mbox_send`) |
| 1008 | 8 | `mbdev` | the `mtk_mbox_device` |

## 5. `struct mtk_ipi_device` (136 B) — defined by each owner as a global (`scp_ipidev`, `sap_ipidev`, `vcp_ipidev`, `gpueb_ipidev`, `mcupm_ipidev`, all `.data/.bss` objects of size 0x88)

| off | size | field | set by | meaning |
|---|---|---|---|---|
| 0 | 8 | `name` | owner (static) | used in `"<name>_ipi#N"` and logs; `-ENXIO` if NULL |
| 8 | 4 | `id` | owner | `enum mtk_ipi_dev` value; not read by the framework |
| 16 | 8 | `mrpdev` | register | rpmsg device |
| 24 | 8 | `mbdev` | register | mailbox device; `mbdev->log_enable` toggled by `mtk_ipi_tracking` |
| 32 | 8 | `table` | register | `kcalloc(count, 96)` channel table |
| 40 | 48 | `mutex_ipi_reg` | register | serialises register/unregister |
| 88 | 8 | `pre_cb` | owner (optional) | called before every send; non-zero → `IPI_PRE_CB_FAIL` (−8). Typically wakes the core. |
| 96 | 8 | `post_cb` | owner (optional) | called after every send; non-zero → `IPI_POST_CB_FAIL` (−9) |
| 104 | 8 | `prdata` | owner | argument to `pre_cb`/`post_cb` |
| 112 | 8 | `timeout_handler` | owner (optional) | called with `ipi_id` on a `send_compl` ACK timeout |
| 120 | 4 | `lock_monitor` | register | spinlock for the stage/timestamp record |
| 124 | 4 | `ipi_last_done` | framework | last id that completed a send/recv/ack (−1 after register/reset) |
| 128 | 4 | `ipi_inited` | framework | 1 after register; every API returns `IPI_DEV_ILLEGAL` (−1) while it is 0 |

## 6. `struct mtk_ipi_chan_table` (96 B), `struct ipimon_s` (16 B)

| off | size | field | meaning |
|---|---|---|---|
| 0 | 8 | `ept` | rpmsg endpoint used for TX (`rpmsg_trysend`) |
| 8 | 8 | `rpchan` | channel info (its `info.name` is used in error logs) |
| 16 | 8 | `pin_send` | `&mbdev->pin_send_table[k]` whose `chan_id == id`, or NULL |
| 24 | 8 | `pin_recv` | `&mbdev->pin_recv_table[k]` whose `chan_id == id`, or NULL. NULL → `IPI_UNAVAILABLE` (−3). |
| 32 | 4 | `holder` | `atomic_t`, >0 while a `send_compl` waits for an ACK. `ipi_isr_cb` only completes ACK-type pins when it is non-zero. |
| 36 | 4 | `ipi_stage:4`, `ipi_seqno:28` | last stage (`enum ipi_stage`: 0 SEND_MSG, 1 ISR_RECV_MSGV, 2 RECV_MSG, 3 SEND_ACK, 4 ISR_RECV_ACK, 5 RECV_ACK, 0xF UNUSED) and sequence counter |
| 40 | 48 | `ipi_record[3]` | `{u16 idx @0; u64 ts @8}`: per-stage `cpu_clock(0)` timestamps (t0/t4/t5 for TX, t1/t2/t3 for RX) |
| 88 | 4 | `trysend_count` | `rpmsg_trysend` attempts of the last send |
| 92 | 4 | `polling_count` | `mtk_mbox_polling` loops of the last POLLING `send_compl` |

## 7. Mailbox pin/device structures (owned by `mtk-mbox`; listed for the boundary)

`struct mtk_mbox_pin_send` (104 B):

- `@0` bit-fields: `mbox:4`, `offset:20`, `send_opt:2`, `lock:2`
- `msg_size`@4, `pin_index`@8, `chan_id`@12
- `mutex_send`@16: WAIT-mode sender lock, initialised by `mtk_ipi_device_register`
- `comp_ack`@64: initialised, then unused
- `pin_lock`@96: POLLING-mode sender lock, held with IRQs off
- `send_record`@100: empty struct in this build

`struct mtk_mbox_pin_recv` (120 B):

- `@0` bit-fields: `mbox:4`, `offset:20`, `recv_opt:2` (0 MESSAGE / 1 ACK), `lock:2`, `buf_full_opt:2`, `cb_ctx_opt:2` (0 ISR / 1 PROCESS)
- `msg_size`@4, `pin_index`@8, `chan_id`@12
- `notify`@16: completion
- `mbox_pin_cb`@48, `pin_buf`@56, `prdata`@64: set by `mtk_ipi_register`
- `pin_lock`@72
- `recv_record`@80 (32 B)
- `polling_lock`@112

`struct mtk_mbox_device` (120 B):

- `name`@0, `id`@8
- `pin_recv_table`@16, `pin_send_table`@24, `info_table`@32
- `count`@40, `recv_count`@44, `send_count`@48
- `memcpy_to_tiny`@56, `memcpy_from_tiny`@64
- `ipi_cb`@72 (set to `ipi_isr_cb`), `ipi_priv`@80 (set to the `mtk_ipi_device`)
- `pre_cb`@88, `post_cb`@96, `prdata`@104, `log_enable`@112

`struct mtk_mbox_info` (104 B):

- `mbdev`@0, `irq_num`@8, `id`@12
- `slot`@16: capacity in slots
- `opt`@20, `enable`@24, `is64d`@25
- registers: `base`@32, `set_irq_reg`@40, `clr_irq_reg`@48, `init_base_reg`@56, `send_status_reg`@64, `recv_status_reg`@72
- `mbox_lock`@80, `record`@84

Stock confirmation: `mcupm_mbox_pin_send` is 0x680 B = 16 × 104, `mcupm_mbox_pin_recv` is 0x780 B = 16 × 120, `mcupm_mbox_table` is 0x680 B = 16 × 104, and every `*_ipidev` is 0x88 B. The MCUPM pin tables in [`ipi-channel-map.tsv`](ipi-channel-map.tsv) were decoded from the stock `.data` bytes with these layouts.

## 8. Return codes (`mtk_tinysys_ipi.h`)

| value | name | produced when |
|---|---|---|
| 0 | `IPI_ACTION_DONE` | success |
| −1 | `IPI_DEV_ILLEGAL` | `ipi_inited == 0` (device not registered, e.g. `sap_ipidev` on this board) |
| −2 | `IPI_DUPLEX` | `mtk_ipi_register` on a pin that already has a `pin_buf` |
| −3 | `IPI_UNAVAILABLE` | no send/recv pin for that id in the board table |
| −4 | `IPI_NO_MSGBUF` | `mtk_ipi_register` with `msg == NULL` |
| −5 | `IPI_NO_MEMORY` | `len > msg_size` |
| −6 | `IPI_PIN_BUSY` | pin still busy at the deadline (`mtk_ipi_send` dumps IPIMonitor) |
| −7 | `IPI_COMPL_TIMEOUT` | no ACK before the deadline (`send_compl`); dumps the recv pin and calls `timeout_handler` |
| −8 / −9 | `IPI_PRE_CB_FAIL` / `IPI_POST_CB_FAIL` | owner callbacks failed |
| −10 | `IPI_FAKE_SIGNAL` | `mtk_ipi_recv`/`recv_reply` interrupted (freezer fake signal during suspend) |
| −99 | `IPI_RPMSG_ERR` | any other negative/non-busy return from the mbox layer; also register-time rpmsg failures |
