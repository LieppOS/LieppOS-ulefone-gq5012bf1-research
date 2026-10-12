# tkcore_drv source lineage

**Classification: DONOR + PATCHES** — public TrustKernel source of the same driver (newer
release) + a reconstructed release delta that makes the rebuild binary-identical to stock.
Not DIRECT_SOURCE_MATCH: the stock `srcversion` (MD4 of the token stream of the armtz sources,
comments/whitespace ignored) is not reproduced, so the literal 6:1.1-era text differs somewhere
(dead code, macros, unused declarations). Supersedes the 2026-09 "NO_PUBLIC_SOURCE_FOUND /
SOURCE_RECONSTRUCTED" verdict (`kernel/phase4-tkcore-drv-reconstruction.md`).

## Donor (public, GPL-2.0)

| item | value |
|---|---|
| repository | `https://review.ozobot.com/plugins/gitiles/device/ozobot/anvil-kernel` (Gerrit/gitiles, MediaTek MT6789 kernel 5.10 for the Zinwa Q25) |
| import commit | `8e1a0f39478f` "tee: Import TrustKernel driver used by Zinwa Q25" (2026-01-29) |
| tree used | `6b94428fe0aae736e06693cda13bd284b88e93ed` ("treewide: Integrate tkcore across drivers, dts and configs"), path `drivers/tee/tkcore` |
| content pin | `source/donor-manifest.tsv` (44 files, per-file sha256; the gitiles tar wrapper is not byte-stable) |
| release | `TKCORE_NSDRV_VER "7:2.2"`, Copyright 2015-2018/2026 TrustKernel, `BUILD.bazel` for MediaTek `define_mgk_ddk_ko` (kernel_device_modules) |
| layout | `core/` → `tkcore.ko`, `armtz/{tee_tz_drv,tee_smc_xfer,tee_mem,handle}.c` → `tkcore_drv.ko` — identical file names and object order to the stock build paths (`../kernel_device_modules-6.1/drivers/tee/tkcore/armtz/tee_tz_drv.c`, `…/tee_mem.c` in stock strings) |
| ancestor | OP-TEE `optee_linuxdriver` @3a43adc (armtz/handle.c, tee_mem.c, tee_tz_drv.c) |

Found by a targeted search for the DT compatible `"trustkernel,tzdrv" tee_tz_drv.c` after the
local corpora (ALPS, NothingOSS mt6878, kernel_device_modules, optee donor) had been exhausted
(see `kernel/phase4-tkcore-source-candidates.md`).

## Stock generation

Stock `tkcore.ko` reports `version=6:1.1-k6.6`; `tkcore_drv.ko` `version=1.0`. The stock armtz
backend is the **older** generation (per-CPU kthread dispatcher). Donor as-is: 23/50 functions
byte-identical; with the delta below: **50/50**.

## Reconstructed delta (`patches/0001-…patch`, private tree commit ff135ee)

| # | public 7:2.2 | stock (GQ5012BF1) | proof |
|---|---|---|---|
| 1 | `tee_smc_xfer.c`: workqueue `tee_work` (`alloc_workqueue`, `queue_work_on`, `flush_work`), per-CPU int lock counts, 100 ms timeout, "submit tee task … timeout", `pr_fmt` | per-CPU kthreads `tkcore_smc_task.%u` (`struct tee_smc_thread {task, thread_wq}`), `u32 cpu_mask` busy bitmap, `tasks` list + `task_lock`, `struct tee_task {ptee,param,last_param,entry,done}` + completion, 2000 µs timeout then inline, `tee_cpu_online` + `tee_cpu_prepare_down` (rebinds), `kzalloc` thread array, no `pr_fmt` in this file | imports (`kthread_*`, `prepare_to_wait`, `__wake_up`, `schedule`), strings, 9/9 functions byte-identical |
| 2 | `invoke_tee_fn(ptee, fid, a0..a3, resp)`, `struct invoke_tee_response {a0..a4}` | three data args, four result words | KCFI `_ZTSFiP6tee_tzjmmmP19invoke_tee_responseE` = 0x2a6e6379 |
| 3 | `build_mem_share_handle_fn(ptee, unsigned long pa, …)` + `free_mem_share_handle_fn` | `(ptee, void *va, size_t, bool, unsigned long *, uint32_t *)`, `virt_to_phys` inside, no free hook | KCFI `_ZTSFiP6tee_tzPvmbPmPjE` = 0x3ce3af19 |
| 4 | ADD_SHM through `build_mem_share_handle` | direct PA to `invoke_tee` | tz_start bytes |
| 5 | `handle_rpc` global; `TEESMC_TKCORE_RPC_FLUSH_TEE_LOG` → `tkcore_notify_logger`; named-shm (`TEESMC_ATTR_ENABLE_NAMED_SHM`, `tee_rpc_alloc.named_shm`, `>= 1024` check); `tee_shm_pool_p2v_range` | static `handle_rpc` inlined into `call_tee`; none of these | call_tee bytes, no `tkcore_notify_logger` import |
| 6 | `tz_alloc` builds an `sg_table` (`alloc_sgt`), `tz_free` frees it; early-return WARNs | no sg_table; "tz_alloc: cannot alloc memory, size 0x%lx" / "tz_alloc: p2v(%p)=0"; WARN_ON without return in `tz_free`/`tz_shm_inc_ref` | strings, imports |
| 7 | `get_tee_ffa_dev()` EXPORT_SYMBOL + `tkcore_ffa_dev` | absent (0 exports) | export table |
| 8 | `core/tee_supp_com.h` `struct tee_rpc_alloc` has `named_shm` | `{u32 size; void *data; void *shm}` | call_tee stack layout |
| 9 | line layout | three blank-line adjustments so the 43 `__bug_table` `__LINE__` values match | `parity/bug-table-parity.tsv` |

Build configuration (`scripts/build_tkcore_drv.sh`): `CONFIG_TRUSTKERNEL_TEE_SUPPORT=m`,
`CONFIG_TRUSTKERNEL_TEE_RPMB_SUPPORT=y`, `-DCONFIG_TRUSTKERNEL_TEE_FP_SUPPORT=1`; exact GKI
12901745, clang r487747c, `module_scmversion=`, `-faddrsig`.

## Side findings for other components (recorded only)

* Built from the same donor, `core/` (7:2.2) exports reproduce the stock `tkcore.ko` CRCs for
  `tee_map_cached_shm`, `tee_unmap_cached_shm`, `tee_wait_queue_{init,exit,sleep,wakeup}`,
  `tee_clkmgr_handle`, `tee_spi_cfg_padsel`, `tee_spi_transfer`, `tee_spi_transfer_disable`
  (with FP support); `tee_core_{alloc,add,del,free}`, `__tee_get`, `tee_supp_cmd` differ
  (struct tee/tee_ops/tee_context changed between 6:1.1 and 7:2.2). Relevant to
  TRUSTKERNEL-TEE / TRUSTKERNEL-ABI-ISLAND / MICROARRAY-FP-TEE; not acted on here.
