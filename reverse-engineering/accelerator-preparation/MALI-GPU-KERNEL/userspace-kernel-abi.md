# Android userspace ↔ kernel ABI — MALI-GPU-KERNEL

## Device nodes

| node | provider | permissions / label (stock) | userspace consumers (static strings) |
|---|---|---|---|
| `/dev/mali0` (misc device `mali0` under `13000000.mali`) | kbase | ueventd `0666 system graphics`; `/dev/mali.*` → `gpu_device` | `libGLES_mali.so` (`/dev/mali`), and through it `vulkan.mali.so` and every GLES/Vulkan/OpenCL client; `arm.mali.platform-service.mediatek` (`arm.mali.platform` AIDL) |
| `/proc/ged` (`proc_ops`: open, release, poll, read, write, ioctl, compat_ioctl) | ged | — | `libged.so` ("ged_bridge"). By `DT_NEEDED`/string evidence, libged is used by `libGLES_mali.so`, `libgralloc_extra.so`, `libpowerhal.so`, `libgpudataproducer.so`, the codec2 MTK vdec/venc, `libneuron_adapter_mgvi.so` and the mediatek graphics allocator service. |
| `/d/ged/hal/*` (debugfs: `current_freqency`, `custom_upbound_gpu_freq`, `gpu_utilization`, `previous_freqency`, `vsync_offset_level`) | ged | debugfs | `libged.so` (best-effort, logs "not found") |
| `/proc/gpufreqv2/*` | mtk_gpufreq_wrapper | procfs | debugging and tuning |
| sysfs under `13000000.mali` | kbase | — | `core_mask csg_scheduling_period ctx_default_max_size diagnosis_dump_mask diagnosis_mode dvfs_period etm fw_timeout gpuinfo idle_hysteresis_time(_ns) lp_max_size lp_mem_pool_max_size lp_mem_pool_size max_size mcu_shader_pwroff_timeout(_ns) mem_pool_max_size mem_pool_size mtk_fwlog_enable_mask pm_poweroff power_policy progress_timeout reset_timeout` (the `dev_attr_*` set in stock = reconstruction) |
| `sys/class/devfreq/13000000.mali` | kbase devfreq | — | governor / perf HALs |

* The **uevents** are only the standard device-model `add`/`bind` events.
* None of the 8 modules calls `kobject_uevent*` directly (source scan).

## kbase ioctl ABI (`abi/kbase-ioctls.tsv`)

* `abi/kbase-ioctl-extract.c` compiles the reconstructed uapi headers for aarch64 with
  `MALI_USE_CSF=1 MALI_UNIT_TEST=1`, the defines kbase was built with, and records each
  command number, direction, nr and argument size.
* UK version 1.21; magic `0x80`.
* **54 commands are dispatched** in `kbase_ioctl()`:
  * `VERSION_CHECK(_RESERVED)`, `SET_FLAGS`, `KINSTR_PRFCNT_*`, `GET_GPUPROPS`;
  * `MEM_ALLOC(_EX)`/`QUERY`/`FREE`/`JIT_INIT`/`EXEC_INIT`/`SYNC`/`FIND_*`/`COMMIT`/
    `ALIAS`/`IMPORT`/`FLAGS_CHANGE`/`PROFILE_ADD`;
  * `STICKY_RESOURCE_*`, `DISJOINT_QUERY`, `GET_DDK_VERSION`, `GET_CONTEXT_ID`,
    `TLSTREAM_ACQUIRE/FLUSH/STATS`, `STREAM_CREATE`, `FENCE_VALIDATE`,
    `HWCNT_READER_SETUP`, `GET_CPU_GPU_TIMEINFO`;
  * all CSF queue, group, KCPU, tiler-heap and `GLB_IFACE` commands, `CS_CPU_QUEUE_DUMP`,
    `READ_USER_PAGE`;
  * `CONTEXT_PRIORITY_CHECK`, `SET_LIMITED_CORE_COUNT`;
  * MTK `INTERNAL_FENCE_WAIT` (nr 80, `CONFIG_MALI_MTK_FENCE_DEBUG`).
* **4 are not built:** `HWCNT_SET` (needs `CONFIG_MALI_NO_MALI`) and `CINSTR_GWT_*` (needs
  `CONFIG_MALI_CINSTR_GWT`).
* `kbase_ioctl`, the `KBASE_HANDLE_IOCTL*` handlers and `kbase_mmap` (the user-register,
  ring-buffer and tracking pages) are byte-identical to stock. So command numbers, argument
  sizes and copy directions are exactly the stock ABI.

## GED bridge ABI

* The command is `_IOWR('g', id, struct GED_BRIDGE_PACKAGE)`, and `GED_IOWR_32` for 32-bit
  compat.
* The package is `{u32 function_id; s32 size; void *in; s32 in_size; void *out; s32 out_size}`.
* The ids are 0–16 (log buffer, boost, 3D-fence monitor, query info, vsync notify,
  DVFS probe/return, event notify, HW-vsync wait, target FPS, GPU→CPU hint, force MDP,
  freq prediction, DVFS info), 100–107 (GE alloc/get/set, GPU timestamp, target FPS,
  GE info, tuner status, dma-buf set-name) and 200 (create timeline).
* Each command validates `sizeof(GED_BRIDGE_IN/OUT_*)` (`VALIDATE_ARG`).
* Dispatcher and handlers are byte-identical to stock.

## DMA-buf and shared memory

* kbase imports `DMA_BUF` namespace symbols (`import_ns=DMA_BUF`). User memory import uses
  dma-buf fds (`MEM_IMPORT`).
* Protected memory is reached through `mtk_sec_heap` (`dmabuf_to_secure_handle`,
  `is_support_secure_handle`) and `tmem_ffa` (`trusted_mem_ffa_query_pa`). Those modules
  are owned by TMEM-FFA (DONE), and their natural CRCs equal stock.
* ged names dma-bufs through `system_heap`'s `mtk_dma_buf_set_name`.

## Proprietary userspace (retained, not reconstructed)

The following stay stock binaries; they are not part of this kernel scope:
* `libGLES_mali.so`, `vulkan.mali.so`, `libged.so`, `libgpud*.so`, `libmtkgpuserv*.so`,
  `arm.mali.platform-service.mediatek*`, `vendor.mediatek.hardware.gpuserv-service`;
* the `arm.mali.platform` and `vendor.mediatek.hardware.gpu(serv)` HALs.

They depend only on the ABI above.
