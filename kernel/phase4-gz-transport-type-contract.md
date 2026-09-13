# GQ5012BF1 GenieZone transport type contract

## Proof method

The stock ELFs are stripped, so member names were not inferred from disassembly. Layouts below come from the exact pinned source/header set, whose generated functions are byte/KCFI identical, plus an analysis-only `sizeof`/`offsetof` probe compiled with the exact GKI/clang toolchain. Probe symbols encode size or offset and are not part of the final modules.

Classification:

- **PROVEN_EXACT** — complete public layout or exact source/compiler probe plus byte-identical use sites.
- **PROVEN_SEMANTICS_OFFSETS_ONLY** — private type, exact total size and listed offsets proven; omitted members intentionally not guessed.

All offsets are bytes for AArch64 GKI.

## Public/client-visible types

### `struct tipc_k_handle` — PROVEN_EXACT

Size 8, alignment 8.

| Offset | Width | Member | Ownership |
|---:|---:|---|---|
| 0 | 8 | `struct tipc_dn_chan *dn` | set by connect; downstream object released by channel release callback |

The caller owns the handle container; the module owns the pointed channel after successful connect.

### `struct tipc_msg_buf` — PROVEN_EXACT

Size 56, alignment 8.

| Offset | Width | Member | Meaning |
|---:|---:|---|---|
| 0 | 8 | `buf_va` | CPU virtual address |
| 8 | 8 | `buf_pa` | physical/shareable address |
| 16 | 8 | `buf_sz` | allocation size |
| 24 | 8 | `wpos` | write cursor |
| 32 | 8 | `rpos` | read cursor |
| 40 | 16 | `node` | free/RX queue list node |

Ownership moves between the virtio device free list, caller, virtqueue, and downstream RX queue. The containing list's lock is authoritative.

### `struct tipc_dn_chan` — PROVEN_EXACT

Size 200, alignment 8.

| Offset | Member |
|---:|---|
| 0 | `int state` |
| 4 | `int state_bak` |
| 8 | `struct mutex lock` |
| 56 | `struct tipc_chan *chan` |
| 64 | `wait_queue_head_t readq` |
| 88 | `struct completion reply_comp` |
| 120 | `struct list_head rx_msg_queue` |
| 136 | `u32 session` |
| 144 | `struct mutex sess_lock` |
| 192 | `enum tee_id_t tee_id` |
| 196 | `int32_t cpumask` |

`lock` protects state and RX queue. `reply_comp` completes connect/disconnect events; `readq` wakes data readers/state waiters. The channel release callback frees the object.

## Trusty types

### `enum tee_id_t` — PROVEN_EXACT

32-bit enum: `TEE_ID_TRUSTY=0`, `TEE_ID_NEBULA=1`, `TEE_ID_END=2`.

### `struct trusty_nop` — PROVEN_EXACT

Size 32: `list_head node` at 0 (16 bytes), `u32 args[3]` at 16 (12 bytes), 4 bytes trailing alignment. The caller owns storage; queue membership is protected by `trusty_state.nop_lock`.

### `struct nop_task_info` — PROVEN_EXACT

Size 104: `ts` 0, `idx` 8, `run` completion 16, `rdy` completion 48, `nop_func` 80, per-CPU `nop_queue` 88. Probe allocates one device-managed record per possible CPU; the bound NOP thread consumes it through teardown.

### `struct trusty_state` — PROVEN_SEMANTICS_OFFSETS_ONLY

Exact size 344. Proven anchor offsets: `smc_lock` 0, atomic call `notifier` 48, blocking `callback` 64, `api_version` 176, `dev` 184, `nop_tasks_info` 200, irqsave `nop_lock` 208, `tee_id` 212. Remaining source members include CPU-idle completion, version pointer, per-CPU task pointers, poll notifier/task/worker/work. It is device-managed, installed as platform drvdata at probe, and lives until remove.

## Private IPC types

### `enum tipc_chan_state` — PROVEN_EXACT

32-bit enum: `DISCONNECTED=0`, `CONNECTING=1`, `CONNECTED=2`, `STALE=3`.

### `enum tipc_device_state` — PROVEN_EXACT

32-bit enum: `VDS_OFFLINE=0`, `VDS_ONLINE=1`, `VDS_DEAD=2`.

### `enum tipc_chan_event` — PROVEN_EXACT

32-bit values: `CHANNEL_CONNECTED=1`, `CHANNEL_DISCONNECTED=2`, `CHANNEL_SHUTDOWN=3`.

### `struct tipc_chan` — PROVEN_EXACT

Size 360. Offsets: mutex 0, kref 48, state 52, device pointer 56, ops 64, callback argument 72, remote/local addresses 80/84, max message size/count 88/92, 256-byte service name 96, CPU affinity 352, selected CPU 356. The mutex protects state/address/service fields; kref and the device IDR govern lifetime.

### `struct tipc_virtio_dev` — PROVEN_SEMANTICS_OFFSETS_ONLY

Exact size 424. Proven anchors: state 208, cdev node 216, TEE ID 400, RX/TX queue counts 404/408, default CPU mask 416. Source-proven members also hold kref/mutex, virtio device, RX/TX queues and names, message limits, free-buffer list, send waitqueue, address IDR, cdev name, multi-queue flag, and atomic allowed-CPU mask. The device mutex/IDRs/list locks and kref partition ownership; remove marks it DEAD before final release.

## Unknowns

No private member spelling or padding outside the exact source/probe set is asserted. Secure-world representations behind physical buffers are out of scope.
