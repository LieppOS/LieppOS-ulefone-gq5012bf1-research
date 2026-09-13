# `tmem_ffa.ko` — object, ops-table and global-state contract

All 60 stock objects are reproduced by the source-built module (identical
names, sections, offsets, sizes and bindings; only `.modinfo` `vermagic`
differs in length). Highlights:

## 1. Driver / bus structures

| object | type | stock | rebuilt | parity |
|---|---|---|---|---|
| `tmem_ffa_driver` | `struct ffa_driver` | `.data` | same | EXACT |
| `tmem_ffa_device_id` | `struct ffa_device_id[3]` | `.rodata` | same | EXACT |
| trusted-memory `platform_driver` (probe `trusted_mem_init`) | `struct platform_driver` | `.data` | same | EXACT |
| `tee_smem_devs[]` | `struct tmem_device_description[]` | `.data` | same | EXACT |
| `mtee_mchunks[]` | `struct tmem_device_description[]` | `.data` | same | EXACT |
| `tee_smem_general_configs`, `mchunk_general_configs` | `struct trusted_mem_configs` | `.data` | same | EXACT |

## 2. Peer operation tables

`struct trusted_driver_operations` — 7 slots, both instances byte-identical to
stock:

| slot | TEEC peer (`tee_gp_peer_ops`) | KREE peer (`mtee_peer_ops`) | prototype |
|---:|---|---|---|
| 0 | `tee_session_open` | `mtee_session_open` | `int (*)(void **peer_data, void *dev_desc)` |
| 1 | `tee_session_close` | `mtee_session_close` | `int (*)(void *peer_data, void *dev_desc)` |
| 2 | `tee_alloc` | `mtee_alloc` | `int (*)(u32 align, u32 size, u32 *refcount, u32 *sec_handle, u8 *owner, u32 id, u32 clean, void *peer_data, void *dev_desc)` |
| 3 | `tee_free` | `mtee_free` | `int (*)(u32 sec_handle, u8 *owner, u32 id, void *peer_data, void *dev_desc)` |
| 4 | `tee_mem_reg_add` | `mtee_mem_reg_add` | `int (*)(u64 pa, u32 size, void *peer_data, void *dev_desc)` |
| 5 | `tee_mem_reg_remove` | `mtee_mem_reg_remove` | `int (*)(void *peer_data, void *dev_desc)` |
| 6 | `tee_invoke_command` | `mtee_invoke_command` | `int (*)(struct trusted_driver_cmd_params *, void *peer_data, void *dev_desc)` |

Accessors `get_tee_peer_ops()` / `get_mtee_peer_ops()` publish the tables
(`"TEE_OPS set"` / `"MTEE_OPS set"`). Every slot's KCFI type id is reproduced
exactly — the indirect-call contract is proven, not assumed.

## 3. Global state

| object | kind | notes |
|---|---|---|
| `g_sess_data` | `struct TEE_GP_SESSION_DATA *` (`.bss +0x430`) | single global TEEC session block (320 B) |
| `is_sess_ready` | `bool` (`.bss +0x42c`) | guards the TEEC session |
| `g_sess_lock` | `struct mutex` (`.data +0x1b90`) | serialises all TEEC traffic |
| `t_mgr_desc->lock` | `struct mutex` | device-manager list lock (lockdep name in `.rodata`) |
| `t_mgr_desc->peer_mgr_data.lock` | `struct mutex` | peer-manager lock |
| `mtee_lock` | `struct mutex` | `MTEE_CMD_LOCK()` for KREE command multiplexing |
| `tmem_ffa_dev`, `tmem_ffa_ops` | FF-A device + ops cache | set in probe |
| `tmem_carveout_heap[]` | `struct tmem_carveout_heap *[]` | per-`mchunk_id` `gen_pool` carve-outs |
| region/SSMR state | `struct SSMR_Feature[]` + delayed work | `[ON]`/`[OFF]`/`[ONING]`/`[OFFING]` state strings |

Kernel primitives used: `mutex`, `spinlock` (`_raw_spin_lock_irqsave`),
`list_head` (`__list_add_valid`/`__list_del_entry_valid`), `gen_pool`,
`sg_table`, `delayed_work` + `alloc_workqueue`, `timer` (`init_timer_key`),
`cma_alloc/cma_release`, `dma_alloc_attrs/dma_free_attrs`. No IDR/XArray is
used.

## 4. Tables of identifiers

| table | content | parity |
|---|---|---|
| FF-A id table | 2 partition UUIDs (see FF-A contract) | EXACT |
| TEE command table | per-device `tee_cmds[TEE_OP_MAX]` (alloc / alloc-zero / free / enable / disable) | EXACT |
| MTEE chunk-id table | `MTEE_MCHUNKS_{SVP,PROT,WFD,TUI,SAPU_*,AP_MD_SHM,AP_SCP_SHM}` | EXACT |
| SSMR feature table | `SecureVideoPath`, WFD, PROT, TUI, SAPU, AP-MD/AP-SCP SHM features | EXACT |
| TA UUID | `08030000-0000-0000-0000-000000000000` | EXACT |
| GZ service name | `com.mediatek.geniezone.srv.mem` | EXACT |

## 5. Device-tree dependencies

`get_reserved_memory()`, `set_svp_reserve_memory()`,
`of_reserved_mem_device_init_by_idx`, `of_reserved_mem_lookup`,
`of_find_compatible_node`, `of_find_node_by_name` — the SSMR region geometry is
read from DT at probe. No DT node was added, removed or edited by this task.
