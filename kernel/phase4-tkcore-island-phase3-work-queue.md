# GQ5012BF1 tkcore island — Phase 3 behavioral reconstruction work queue

Derived from the Phase-2 ELF comparison, not from estimation.

**37 stock functions remain unimplemented** (was 55 at Phase 2; Phase 3P closed
18). 85 of the 122 stock functions are now present in the rebuilt ELF, 27 of
them byte-identical to stock.

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
`phase4-tkcore-island-phase3p-core-unblock.md`. Phase 3A can be rerun.
`tee_clkmgr_handle` was deliberately left for the dedicated clock-manager phase;
registration and teardown do not depend on it.

## 1. core lifecycle — 5 function(s)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `__tee_get` **(EXPORTED)** | MISSING | tkcore_drv call sites + donor | tkcore_drv | MEDIUM - lifecycle and ioctl surface |
| `tee_core_alloc_uuid` | MISSING | stock ELF only | tkcore_drv | MEDIUM - lifecycle and ioctl surface |
| `tee_core_free_uuid` | MISSING | stock ELF only | tkcore_drv | MEDIUM - lifecycle and ioctl surface |
| `tee_core_uuid2ptr` | MISSING | stock ELF only | tkcore_drv | MEDIUM - lifecycle and ioctl surface |
| `tee_internal_ioctl` | MISSING | stock ELF only | tkcore_drv | MEDIUM - lifecycle and ioctl surface |

## 2. context/session — 2 function(s)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `tee_session_compat_ioctl` | MISSING | stock ELF only | tkcore_drv | MEDIUM - session lifecycle |
| `tee_session_internal_ioctl` | MISSING | stock ELF only | tkcore_drv | MEDIUM - session lifecycle |

## 3. shared memory — 12 function(s)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `__tee_shm_attach_dma_buf` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `__tee_shm_detach_dma_buf` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `__tee_shm_dma_buf_map_dma_buf` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `__tee_shm_dma_buf_mmap` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `__tee_shm_dma_buf_release` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `__tee_shm_dma_buf_unmap_dma_buf` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `tee_map_cached_shm` **(EXPORTED)** | MISSING | historical CRC already natural + consumer | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `tee_unmap_cached_shm` **(EXPORTED)** | MISSING | historical CRC already natural + consumer | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `tkcore_alloc_shm` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `tkcore_shm_free` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `tkcore_shm_get` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |
| `tkcore_shm_put` | MISSING | stock ELF only | tkcore_drv, tmem_ffa | HIGH - dma-buf + secure memory lifetime |

## 5. supplicant/RPC — 2 function(s)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `tee_supp_open` | MISSING | OP-TEE donor analogue | tkcore_drv | MEDIUM - RPC handshake |
| `tee_supp_release` | MISSING | OP-TEE donor analogue | tkcore_drv | MEDIUM - RPC handshake |

## 7. clock manager — 1 function(s) remaining (1 closed in Phase 3P)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `tee_clkmgr_handle` **(EXPORTED)** | MISSING | historical CRC already natural + consumer | tkcore_drv | HIGH - secure-world clock gating |
| `tee_clkmgr_register` **(EXPORTED)** | **CLOSED (Phase 3P)** | historical CRC already natural + consumer | tkcore_drv | HIGH - secure-world clock gating |

## 8. SPI proxy — 3 function(s)

| stock function | current state | available oracle | consumer | risk |
|---|---|---|---|---|
| `tee_spi_cfg_padsel` **(EXPORTED)** | MISSING | historical CRC already natural + consumer | microarray_fp_tee | HIGH - secure SPI proxy touches fingerprint TA path |
| `tee_spi_transfer` **(EXPORTED)** | MISSING | historical CRC already natural + consumer | microarray_fp_tee | HIGH - secure SPI proxy touches fingerprint TA path |
| `tee_spi_transfer_disable` **(EXPORTED)** | MISSING | historical CRC already natural + consumer | microarray_fp_tee | HIGH - secure SPI proxy touches fingerprint TA path |

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
| `sg_nents` | MISSING | stock ELF strings/relocations | (internal) | LOW - leaf helpers |
| `tee_compat_ioctl` | MISSING | stock ELF strings/relocations | (internal) | MEDIUM - 32-bit compat marshalling |
| `tee_peridev_exit` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `tee_peridev_init` | **CLOSED (Phase 3P)** | stock ELF strings/relocations | (internal) | MEDIUM - MT6878 platform init / big-core affinity |
| `uaccess_ttbr0_disable` | MISSING | stock ELF strings/relocations | (internal) | LOW - leaf helpers |
| `uaccess_ttbr0_enable` | MISSING | stock ELF strings/relocations | (internal) | LOW - leaf helpers |

## Exported symbols still absent (7 of 25)

These are the only export-name gaps; every other stock export is already emitted.

* `__tee_get` — subsystem `core`
* `tee_clkmgr_handle` — subsystem `clkmgr`
* `tee_map_cached_shm` — subsystem `shared_memory`
* `tee_spi_cfg_padsel` — subsystem `spi`
* `tee_spi_transfer` — subsystem `spi`
* `tee_spi_transfer_disable` — subsystem `spi`
* `tee_unmap_cached_shm` — subsystem `shared_memory`

## Explicit non-goals for Phase 3

* Do NOT reopen historical CRC brute forcing for the 11 blocked exports.
* Do NOT rebuild tkcore_drv / tmem_ffa / microarray_fp_tee until the exports above exist.
* Do NOT attempt runtime validation until a dedicated, separately authorised phase.
