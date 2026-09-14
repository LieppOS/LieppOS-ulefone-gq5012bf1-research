# GQ5012BF1 tkcore island — Phase 3 behavioral reconstruction work queue

Derived from the Phase-2 ELF comparison, not from estimation.

**5 stock functions remain unimplemented** (was 55 at Phase 2; Phase 3P closed
18, Phase 3A-R added 6, Phase 3B added 13, Phase 3C closed the ioctl/compat and
command-marshalling layer, Phase 3C-R closed the command-output residual, and
Phase 3D added the final 4). **117 of the 122 stock functions** are now present
in the rebuilt ELF, 47 of them byte-identical to stock, **all 25 exports are
present with naturally reproduced CRCs**, and the island still defines **no
function that is not a stock function**.

The only remaining work is Phase 3E: `big_core_affinity_get_candidate_cpu`,
`big_core_affinity_match_cpu`, `big_core_affinity_need_bind_cpu`,
`plat_cpu_is_big` and `plat_tee_init`.

Recommended order is bottom-up: leaf helpers and trace surfaces first, then the
subsystems that carry exported symbols, then the secure-world proxies last.

## Phase-3A gate result (2026-03-23)

Phase 3A attempted to close the exported core lifecycle before procfs/log and
SPI/clock-manager work. Stock disassembly proves that ordering is impossible
without placeholders: `tee_core_add` directly calls `tee_init_procfs` and
`tee_peridev_init`, while `tee_core_del` directly calls
`tee_peridev_exit`. The former reaches `plat_register_spi_clk` and
`tee_clkmgr_register`; the procfs pair creates/removes proc entries, IRQ state
and a kernel thread. Success-returning stand-ins are forbidden.

**No function was removed from this queue.** The safe next scheduling action is
to close the directly required Phase-3E/3F leaves first, or explicitly revise
the phase boundary. See `phase4-tkcore-island-phase3a-blocked.md`.

## Phase-3P prerequisite closure (resolves the Phase-3A blocker)

Phase 3P reconstructed exactly the blocking lifecycle leaves: the proc/log
surface (`tee_init_procfs`, `tee_exit_procfs` and every reachable callback) and
the peripheral/clock lifecycle (`tee_peridev_init`, `plat_register_spi_clk`,
`tee_clkmgr_register`, `tee_peridev_exit`). It also corrected
`tee_init_sysfs`/`tee_cleanup_sysfs` and audited `tee_supp_init`; those three are
now byte-identical to stock.

Result: **PHASE3A_CORE_DEPENDENCIES_READY** — see
`phase4-tkcore-island-phase3p-core-unblock.md`. `tee_clkmgr_handle` was
deliberately left for the dedicated clock-manager phase and is now **closed in
Phase 3D**; registration and
teardown do not depend on it.

## Phase 3A-R core + context/session closure

Phase 3A-R now closes all five core APIs, all three IDR handle helpers, and all
four TEEC context/session lifecycle APIs. It adds `__tee_get`,
`tee_core_alloc_uuid`, `tee_core_uuid2ptr`, `tee_core_free_uuid`,
`tee_supp_open`, and `tee_supp_release` to the rebuilt stock-function set. The
supplicant open/release pair was required only to install the stock core device
fops; general supplicant/RPC command handling was not entered.

Static lifecycle traces pass for frozen `tmem_ffa` and `tkcore_drv`. This is not
runtime acceptance. Overall tkcore remains **PARTIAL**, **NOT RUNTIME READY**,
and still depends on the **STOCK RUNTIME PROVIDER**. The next task is **Phase 3B
shared-memory reconstruction**.

## 1. core lifecycle — 1 function(s) remaining

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `tee_internal_ioctl` | MISSING | stock ELF only | tkcore_drv | MEDIUM - ioctl surface; not part of the closed core/context/session lifecycle |

## 2. context/session — 2 function(s)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `tee_session_compat_ioctl` | MISSING | stock ELF only | tkcore_drv | MEDIUM - session lifecycle |
| `tee_session_internal_ioctl` | MISSING | stock ELF only | tkcore_drv | MEDIUM - session lifecycle |

## 3. shared memory — 0 function(s) remaining (all 12 closed in Phase 3B)

| stock function | current state | class | consumer |
|---|---|---|---|
| `__tee_shm_attach_dma_buf` | **CLOSED (Phase 3B)** | EXACT_BYTE | dma_buf_ops |
| `__tee_shm_detach_dma_buf` | **CLOSED (Phase 3B)** | EXACT_BYTE | dma_buf_ops |
| `__tee_shm_dma_buf_map_dma_buf` | **CLOSED (Phase 3B)** | EXACT_BYTE | dma_buf_ops |
| `__tee_shm_dma_buf_mmap` | **CLOSED (Phase 3B)** | EXACT_BYTE | dma_buf_ops |
| `__tee_shm_dma_buf_release` | **CLOSED (Phase 3B)** | EXACT_BYTE | dma_buf_ops |
| `__tee_shm_dma_buf_unmap_dma_buf` | **CLOSED (Phase 3B)** | EXACT_BYTE | dma_buf_ops |
| `tee_map_cached_shm` **(EXPORTED)** | **CLOSED (Phase 3B)** | EXACT_BYTE | tkcore_drv `tz_start` |
| `tee_unmap_cached_shm` **(EXPORTED)** | **CLOSED (Phase 3B)** | EXACT_BYTE | exported; NOT_CALLED by frozen tkcore_drv |
| `tkcore_alloc_shm` | **CLOSED (Phase 3B)** | CFG_EQUIVALENT | tee_shm_alloc_io etc. |
| `tkcore_shm_free` | **CLOSED (Phase 3B)** | CFG_EQUIVALENT | tee_shm_free_io etc. |
| `tkcore_shm_get` | **CLOSED (Phase 3B)** | EXACT_BYTE | `_init_tee_cmd` |
| `tkcore_shm_put` | **CLOSED (Phase 3B)** | CFG_EQUIVALENT | `_release_tee_cmd` |

The three public TEEC shared-memory APIs were audited in the same phase:
`TEEC_RegisterSharedMemory` **EXACT_BYTE**, `TEEC_AllocateSharedMemory` and
`TEEC_ReleaseSharedMemory` **CFG_EQUIVALENT** — each had a real defect that is
now fixed (see `phase4-tkcore-island-phase3b-acceptance.md`).

## 5. supplicant/RPC — 0 function(s) remaining in the stock inventory

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `tee_supp_open` | **CLOSED (Phase 3A-R, core fops prerequisite only)** | stock ELF + donor | tkcore core fops | MEDIUM - command handling remains out of scope |
| `tee_supp_release` | **CLOSED (Phase 3A-R, core fops prerequisite only)** | stock ELF + donor | tkcore core fops | MEDIUM - command handling remains out of scope |

## 7. clock manager — 0 function(s) remaining (1 closed in Phase 3P, 1 in Phase 3D)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `tee_clkmgr_handle` **(EXPORTED)** | **CLOSED (Phase 3D)** SIZE_EXACT_SEMANTIC_EXACT | historical CRC already natural + consumer | tkcore_drv | HIGH - secure-world clock gating |
| `tee_clkmgr_register` **(EXPORTED)** | **CLOSED (Phase 3P)** | historical CRC already natural + consumer | tkcore_drv | HIGH - secure-world clock gating |

## 8. SPI proxy — 0 function(s) remaining (all 3 closed in Phase 3D)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `tee_spi_cfg_padsel` **(EXPORTED)** | **CLOSED (Phase 3D)** SIZE_EXACT_SEMANTIC_EXACT | historical CRC already natural + consumer | microarray_fp_tee | HIGH - secure SPI proxy touches fingerprint TA path |
| `tee_spi_transfer` **(EXPORTED)** | **CLOSED (Phase 3D)** SIZE_EXACT_SEMANTIC_EXACT | historical CRC already natural + consumer | microarray_fp_tee | HIGH - secure SPI proxy touches fingerprint TA path |
| `tee_spi_transfer_disable` **(EXPORTED)** | **CLOSED (Phase 3D)** SIZE_EXACT_SEMANTIC_EXACT | historical CRC already natural + consumer | microarray_fp_tee | HIGH - secure SPI proxy touches fingerprint TA path |

## 9. logging/proc/sysfs/misc glue — 0 function(s) remaining (all 11 closed in Phase 3P)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `drv_version_read` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `logd` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `tee_exit_procfs` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `tee_init_procfs` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `tee_log_open` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `tee_log_read` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `tee_log_release` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `tee_version_read` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `teed_version_read` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `teed_version_write` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |
| `tkcore_log_irq_handler` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - trace surface |

## 10. other TrustKernel-specific helpers — 12 function(s) remaining (6 closed in Phase 3P)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `big_core_affinity_get_candidate_cpu` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `big_core_affinity_match_cpu` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `big_core_affinity_need_bind_cpu` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `convert_compat_tee_cmd` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - 32-bit compat marshalling |
| `convert_compat_tee_shm_io` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - 32-bit compat marshalling |
| `convert_compat_tee_spta_inst` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - 32-bit compat marshalling |
| `copy_to_user_str` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | LOW - leaf helpers |
| `mtk_disable_clk` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `mtk_enable_clk` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `plat_cpu_is_big` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `plat_register_spi_clk` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `plat_tee_init` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `sg_nents` | **CLOSED (Phase 3B)** | stock ELF (WEAK local definition) | (internal) | LOW - leaf helpers; required by `tkcore_shm_get` |
| `tee_compat_ioctl` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - 32-bit compat marshalling |
| `tee_peridev_exit` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `tee_peridev_init` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `uaccess_ttbr0_disable` | MISSING | stock ELF strings/relocations | (internal) | LOW - leaf helpers |
| `uaccess_ttbr0_enable` | MISSING | stock ELF strings/relocations | (internal) | LOW - leaf helpers |

## Exported symbols still absent (4 of 25)

These are the only export-name gaps; every other stock export is already emitted.

* `tee_clkmgr_handle` — subsystem `clkmgr`
* `tee_spi_cfg_padsel` — subsystem `spi`
* `tee_spi_transfer` — subsystem `spi`
* `tee_spi_transfer_disable` — subsystem `spi`

Both shared-memory exports (`tee_map_cached_shm`, `tee_unmap_cached_shm`) were
closed naturally in Phase 3B — no CRC injection, no export-name fabrication.
Export count: 19/25 → **21/25**.

## Explicit non-goals for current reconstruction

* Do NOT reopen historical CRC brute forcing for blocked exports.
* Do NOT require final-natural tkcore_drv / tmem_ffa / microarray_fp_tee acceptance until the remaining subsystems and exports exist.
* Do NOT attempt runtime validation until a dedicated, separately authorised phase.
