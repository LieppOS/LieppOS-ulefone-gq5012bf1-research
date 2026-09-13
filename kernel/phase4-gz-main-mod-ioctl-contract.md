# gz_main_mod — complete ioctl contract

Two independent command spaces. Neither has a hole: every `case` in both
compiled switches is accounted for, and both `default` arms are documented.

---

# A. `/dev/gz_kree` — `gz_ioctl` / `gz_compat_ioctl` → `_gz_ioctl`

Magic `MTEE_IOC_MAGIC = 'T'` (0x54), defined in
`geniezone/public/kree/tz_mod.h`.

All nine encodings were computed from the header and then **confirmed against
the stock disassembly** of `_gz_ioctl` (`.text+0x974`, 2252 bytes), which
contains the comparands `0x5401 0x5402 0x5403 0x5404 0x5410 0x5411 0x5415
0x5416 0x5417` together with the direction/size halves `0xc010 0xc020 0xc008
0x4008 0x4004`.

| # | command | numeric | encoding | argument struct | size |
|---|---|---|---|---|---|
| 1 | `MTEE_CMD_OPEN_SESSION` | `0xC0105401` | `_IOWR('T',1,…)` | `struct kree_session_cmd_param` | 16 |
| 2 | `MTEE_CMD_CLOSE_SESSION` | `0xC0105402` | `_IOWR('T',2,…)` | `struct kree_session_cmd_param` | 16 |
| 3 | `MTEE_CMD_TEE_SERVICE` | `0xC0205403` | `_IOWR('T',3,…)` | `struct kree_tee_service_cmd_param` | 32 |
| 4 | `MTEE_CMD_SHM_REG` | `0xC0205404` | `_IOWR('T',4,…)` | `struct kree_tee_service_cmd_param` | 32 |
| 5 | `MTEE_CMD_FOD_TEE_SHM_ON` | `0x00005410` | `_IO('T',16)` | none | 0 |
| 6 | `MTEE_CMD_FOD_TEE_SHM_OFF` | `0x00005411` | `_IO('T',17)` | none | 0 |
| 7 | `MTEE_CMD_ADJUST_WQ_ATTR` | `0x40085415` | `_IOW('T',21,char *)` | pointer-sized user buffer | 8 |
| 8 | `MTEE_CMD_GET_CHM_HANDLE` | `0xC0085416` | `_IOWR('T',22,…)` | `struct user_chm_fd_to_hd_param` | 8 |
| 9 | `TRUSTY_NOP_SET_PRI` | `0x40045417` | `_IOW('T',23,…)` | `struct user_adjust_nop_pri` | 4 |

`DEV_IOC_MAXNR` is defined as 10 in the header but is **not enforced** by the
compiled code; command numbers 16-23 are dispatched regardless. Recorded
because it contradicts a naive reading of the header.

## Per-command behaviour

### 1. `MTEE_CMD_OPEN_SESSION` → `tz_client_open_session` (808 B)
* `copy_from_user` the 16-byte param; on failure return the raw `copy_*` residue.
* `strncpy_from_user` the TA name from `param.data` (bounded by
  `KREE_SESSION_HANDLE_MAX_SIZE` = 512).
* `KREE_CreateSession(name, &handle)`.
* On success `_register_session_info()` records the handle in the per-open table.
* `copy_to_user` the updated struct (`ret`, `handle`).
* Errors: `-EFAULT` on copy failure; TZ result codes propagate in `param.ret`.

### 2. `MTEE_CMD_CLOSE_SESSION` → `tz_client_close_session` (848 B)
* `copy_from_user`; `KREE_CloseSession(handle)`.
* Removes the handle from the per-open table (slot reset to `0xffffffff`).
* `copy_to_user` the result.

### 3. `MTEE_CMD_TEE_SERVICE` → `tz_client_tee_service` (2932 B)
The largest and most security-relevant path.
* `copy_from_user` the 32-byte param, then `copy_from_user` the GP parameter
  array addressed by `param.param`.
* Walks `paramTypes` one byte per slot (`tmpTypes & 0xff`, `tmpTypes >>= 8`).
* For `TZPT_MEM_INPUT/OUTPUT/INOUT`:
  * resolves the user buffer, honouring `compat_ptr()` when the compat entry
    was used (`mem32.buffer`/`mem32.size` vs `mem.buffer`/`mem.size`);
  * `access_ok()` is checked for read and/or write per direction;
  * enforces `ubuf_sz <= GP_MEM_MAX_LEN` (**1024**), else `-ENOMEM`;
  * bounce-buffers through `kmalloc`, `copy_from_user` for non-OUTPUT.
* For `TZPT_MEMREF_*` the slot is passed through unmodified (these carry an
  already-registered shared-memory handle, not a user pointer).
* Calls `KREE_TeeServiceCallPlus(handle, command, paramTypes, param, cpumask)`.
* On return, `TZPT_VALUE_OUTPUT/INOUT` are copied back into the local array and
  `TZPT_MEM_*` non-INPUT buffers are `copy_to_user`'d; every bounce buffer is
  `kfree`'d on both the success and the `error:` unwind path.
* Errors: `-EFAULT`, `-ENOMEM`, `TZ_RESULT_ERROR_BAD_FORMAT` for an
  unrecognised parameter type.

### 4. `MTEE_CMD_SHM_REG` → `_reg_shmem_from_userspace` (924 B)
Registers a user buffer as KREE shared memory. Full semantics in
`kernel/phase4-gz-main-mod-memory-contract.md`.
* Rejects `size <= 0` or NULL buffer with `TZ_RESULT_ERROR_BAD_PARAMETERS`.
* `kvmalloc`s a `struct MTIOMMU_PIN_RANGE_T`, then
  `_map_user_pages(pin, untagged_addr(buffer), size, 0)` — the gz_tz_system
  export that pins user pages on this caller's behalf.
* Builds the physical-address array and calls `KREE_RegisterSharedmem`.

### 5/6. `MTEE_CMD_FOD_TEE_SHM_ON` / `_OFF` → `mtee_sdsp_enable(1|0)` (116 B)
* Compiled in because `CONFIG_MTK_GZ_SUPPORT_SDSP` is **off** (see config
  contract). Both cases converge on a single `mtee_sdsp_enable` call site in
  the stock binary — the compiler merged the two tails, which is why exactly
  one `R_AARCH64_CALL26` relocation to that symbol exists.
* `mtee_sdsp_enable` issues a `trusty_fast_call32` SMC to toggle the SDSP
  fingerprint shared-memory window. Takes no user argument (`_IO`).

### 7. `MTEE_CMD_ADJUST_WQ_ATTR` → `gz_manual_adjust_trusty_wq_attr` (572 B)
* Reads a user string, parses it with `sscanf` into a task-attribute record.
* Applies it via `trusty_adjust_task_attr` and pushes the kick mask down with
  `tipc_set_default_cpumask(manual_task_attr.mask[TRUSTY_TASK_KICK_ID])` —
  this is the single `gz_ipc_mod` edge in the whole module.

### 8. `MTEE_CMD_GET_CHM_HANDLE` → `DMAFd2MemHandle` (140 B)
* `copy_from_user` `struct user_chm_fd_to_hd_param {u32 secm_handle; int buf_fd;}`.
* `dma_buf_get(buf_fd)` → `dmabuf_to_secure_handle()` (the sole `mtk_sec_heap`
  edge) → `dma_buf_put()`.
* Writes `secm_handle` back with `copy_to_user`.
* Errors: propagates `TZ_RESULT_*`; `-EFAULT` on copy failure.

### 9. `TRUSTY_NOP_SET_PRI` → `trusty_nop_set_switch_pri`
* `copy_from_user` a 4-byte `policy`, then calls the gz_trusty_mod export.
* Returns the raw error from the provider if non-zero.

### default
`KREE_ERR("[%s] undefined ioctl cmd 0x%x\n", …)` and `-EINVAL`.

## compat behaviour

`gz_compat_ioctl` (36 B) is a thin wrapper:

```c
void __user *user_req = (void __user *)compat_ptr(arg);
return _gz_ioctl(filep, cmd, user_req, /*compat=*/1);
```

`_gz_ioctl` carries the `compat` flag down into `tz_client_tee_service`, where
it selects the `mem32` view of each GP memory slot and applies `compat_ptr()`
to embedded user pointers. The command numbers themselves are identical in
both entry points — there is no separate compat command table. All nine
commands are therefore reachable from 32-bit userspace.

---

# B. `/dev/gz_ffa_dev` — `ff_a_gz_ioctl` (5068 B)

These are **plain integers**, not `_IOC`-encoded. The handler unconditionally
`copy_from_user`s a fixed `struct args { uint64_t arg[5]; }` (40 bytes) when
the argument pointer is non-NULL, and returns `-EFAULT` if that copy fails.

| # | command | numeric | handler | meaning |
|---|---|---|---|---|
| 1 | `GZ_FFA_IS_ENABLED` | 200 | inline | returns the `ffa_enabled` flag |
| 2 | `GZ_FF_A_MEMORY_SEND` | 250 | `gz_ffa_memory_share` | share/lend a memory region to a secure partition |
| 3 | `GZ_FF_A_MEM_RECLAIM` | 251 | `gz_ffa_memory_reclaim` | reclaim a previously shared handle |
| 4 | `GZ_FF_A_PARTITION_INFO_GET` | 252 | `gz_ffa_partition_info` | query partition id/count |
| 5 | `GZ_FF_A_MESSAGE_SEND` | 253 | `gz_ffa_message_send` | FF-A direct request to a partition |
| 6 | `GZ_FF_A_GET_CHM_HANDLE` | 254 | `gz_ffa_get_chm_handle` | dma-buf fd → secure chunk-memory handle |
| 7 | `FF_A_DRV_MEMORY_SEND` | 121 | `ffa_memory_send_write` | driver-level memory-send test path |
| 8 | `FF_A_DRV_READ_BACK` | 125 | `ffa_memory_share_read` | driver-level read-back test path |

`default:` returns `-EINVAL`, and the handler additionally logs
`"Invalid command for %s: %ld"` whenever the result is `-EINVAL`.

Enum gaps (`122`, `123`, `124`, and everything outside the listed values) are
**not** dispatched — they fall to `default` and return `-EINVAL`. There are no
`UNKNOWN` commands: every compiled `case` label is named above.

No semantics were invented from command names; each mapping is read from the
compiled switch and the corresponding source function.
