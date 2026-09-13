# `tmem_ffa.ko` — trusted-memory architecture (recovered from stock code)

All statements below are read off the stock ELF and its exactly-matching
source; nothing is inferred from the module name.

## 1. What it is

The MediaTek **Trusted Memory Subsystem** core, built in its FF-A flavour.
One module implements:

- a *device manager* (`dev_mgr.c`) that registers one trusted-memory device per
  configured region type;
- a *region manager* (`region_mgr.c`) that owns online/offline state of each
  SSMR region and an `ssmr_mgr` shim;
- a *peer manager* (`peer_mgr.c`) that owns the TEE-side session for a device;
- two *peer implementations* — GlobalPlatform TEEC (`tee_impl/`, provider
  `tkcore`) and GenieZone KREE (`mtee_impl/`, provider `gz_tz_system`);
- an *FF-A backend* (`mtee_impl/tmem_ffa.c`) that carves page pools and maps
  FF-A handles to physical addresses (provider `ffa_v10`);
- *SSMR* (`ssmr/memory_ssmr.c`) reserved-memory/CMA online/offline machinery;
- *SSHEAP* (`ssheap/ssheap_lib.c`) a scatter-gather secure-heap allocator;
- `proc.c` / `ssheap_proc.c` procfs surfaces and `tmemperf/` CPU-frequency
  boosting during allocation.

## 2. Memory classes managed

Device descriptors are built in `tee_devices.c` (TEEC peer) and
`mtee_devices.c` (KREE peer). On GQ5012BF1 the configured set is:

| device name | peer | class |
|---|---|---|
| `TEE_SVP` | TEEC (`tkcore`) | secure video path chunk memory |
| `TEE_WFD` | TEEC (`tkcore`) | WFD secure memory |
| `MTEE_SVP`, `MTEE_PROT`, `MTEE_WFD`, `MTEE_TUI` | KREE (`gz_tz_system`) | GenieZone multi-chunk regions |
| `MTEE_AP_MD_SHM`, `MTEE_AP_SCP_SHM` | KREE | AP↔modem / AP↔SCP shared memory |
| `MTEE_SAPU_DATA_SHM`, `MTEE_SAPU_ENGINE_SHM` | KREE | SAPU data/engine shared memory |

Page-based (`*_PAGE`) request types are served through the FF-A/ssheap path
(`trusted_mem_page_based_alloc/free`, `page-based-v2-enabled`).

## 3. Who calls it

Kernel consumers (proven by scanning all stock modules, §`consumer-abi`):
`mtk_sec_heap.ko` (11 symbols), `gz_main_mod.ko` (`ssmr_online/offline`),
`mali_kbase_mt6878_r44.ko` (`trusted_mem_ffa_query_pa`). `modules.dep` also
lists it as a dependency of `mtk-cam-isp7sp`, `sapu`, `mtk_heap_debug`,
`widevine_driver` and `mtk_disp_sec` through `mtk_sec_heap`.

## 4. Roles

- **FF-A role**: consumer of `ffa_v10`. It registers one `struct ffa_driver`
  (`.name = "tmem_ffa"`) with two device ids and keeps `ffa_dev->ops` for
  memory share/reclaim. See `phase4-tmem-ffa-ffa-contract.md`.
- **TrustKernel role**: GlobalPlatform client. One global context, one global
  session, one registered shared-memory block, all commands multiplexed over
  `TEEC_InvokeCommand`. See `phase4-tmem-ffa-teec-call-flow.md`.
- **GenieZone role**: KREE client. Per-device session handle, chunk-memory
  alloc/zalloc/unreference plus multi-chunk append/release. See
  `phase4-tmem-ffa-gz-contract.md`.

## 5. Allocation representation

- A chunk allocation is a `u64 sec_handle` plus `u32 refcount`, carried in
  `struct secmem_param` / `struct secmem_ta_msg_t` (TEEC) or `KREE_*` args.
- Page-based allocations are `struct ssheap_buf_info` objects: `sg_table *`,
  alignment, block list, requested/aligned/allocated size, element count,
  `pmm_msg_page`, `u8 mem_type`, `u64 ffa_handle` and (V2) a `pmm_msg_list` +
  `pmm_page`.
- FF-A handles are mapped back to physical addresses by
  `tmem_query_ffa_handle_to_pa()` / `trusted_mem_ffa_query_pa()`; the carve-out
  pools are `gen_pool` instances (`tmem_carveout_create/destroy`).

## 6. Registration / release

`tmem_ffa_region_alloc/free` and `tmem_ffa_page_alloc/free` allocate backing
memory (CMA/`gen_pool`/`dma_alloc_attrs`), then hand it to the secure world:
TEEC peers use `tee_mem_reg_add/remove`, KREE peers use
`KREE_AppendSecureMultichunkmem` / `KREE_ReleaseSecureMultichunkmem`, and the
FF-A path shares/reclaims through `ffa_dev->ops` ("page-based, failed to FF-A
send the memory" / "failed to FF-A reclaim" error strings).

## 7. Sessions

Sessions are **persistent per device**, not per operation:
`peer_mgr_session_open_locked()` opens once and keeps the session while the
region is online; `session_keep_alive_enable` in `struct trusted_mem_configs`
is `false` for both `tee_smem_general_configs` and `mchunk_general_configs`, so
the session is closed when the last user drops the region.

## 8. Locking, state, lifecycle

- `g_sess_lock` (`TEE_SESSION_LOCK`) serialises the single TEEC session and its
  shared-memory window; `MTEE_SESSION_LOCK` guards KREE session data.
- `t_mgr_desc->lock` and `t_mgr_desc->peer_mgr_data.lock` (both visible as
  stock `.data` mutex names) guard device/peer manager state.
- SSMR uses `down_write`/`up_write` and a delayed work item
  (`queue_delayed_work_on`, `cancel_delayed_work_sync`) for deferred region
  offline.
- Lifecycle: `platform_driver` probe (`trusted_mem_init`) → device creation
  (`create_trusted_mem_device`) → per-region `regmgr` online/offline → peer
  session open/close → chunk alloc/unref.
- Failure rollback is strict reverse ordering with labelled `goto` unwinds
  (see the TEEC flow document).

## 9. PM behaviour

No suspend/resume callbacks. The only PM-adjacent behaviour is the
`tmemperf` CPU-frequency boost (`cpufreq_cpu_get/put`,
`cpufreq_update_limits`) around large allocations, exposed as
`trusted_mem_enable_high_freq` / `trusted_mem_disable_high_freq`.

## 10. DT / config dependencies

`of_find_compatible_node`, `of_find_node_by_name`,
`of_reserved_mem_device_init_by_idx`, `of_reserved_mem_lookup`,
`of_property_read_u64`, `of_property_read_variable_u32_array` and
`__of_parse_phandle_with_args` are used to locate the SSMR/reserved-memory
nodes (`get_reserved_memory`, `set_svp_reserve_memory`,
`"ssmr: %s, failed to find the ssmr device tree"`). No DT was modified by this
task.
