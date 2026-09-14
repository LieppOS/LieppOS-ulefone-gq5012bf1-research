# GQ5012BF1 tkcore island Phase 3P — regression comparison

Three-way comparison: stock, Phase-2 rebuilt, Phase-3P rebuilt. Static only; no runtime validation.

| Build | SHA256 | Size |
|---|---|---:|
| Stock | `03837d13863e3f6694918e2e049edbc3bd5ca5cb02e10d6f374620cca98ed226` | 221352 |
| Phase-2 | `5fc3c38dbfbd1eb90fec4b7d1ec803e4f09a7b576e8e8220f68f1b794a2e6e62` | 132528 |
| Phase-3P | `a5c1a06c68de6791c3ab5d73ec67c51ba297f1ff6f0f69edbe77eee87a097b2d` | 158896 |

Phase-3P module identity: vermagic `6.1.115-android14-11-maybe-dirty SMP preempt mod_unload modversions aarch64`, srcversion `0BE10B3A8B3565D9802B149`, Build ID `2a7d0852fc011ab681e218b9a94d8ab87862e968`, `depends=` (empty), `license=GPL`.

## Headline movement

| Metric | Stock | Phase-2 | Phase-3P | Δ |
|---|---:|---:|---:|---|
| Defined functions | 122 | 83 | 99 | +16 |
| Functions shared with stock | 122 | 67 | 85 | +18 |
| Byte-identical to stock | – | 16 | 27 | +11 |
| KCFI-exact (shared set) | – | 58 | 77 | +19 |
| KCFI mismatches (shared set) | – | 9 | 8 | −1 |
| Undefined imports | 100 | 61 | 84 | +23 |
| Imports absent from stock | – | 4 | 3 | −1 |
| Exports present | 25 | 17 | 18 | +1 |
| Stock functions still missing | – | 55 | 37 | −18 |

Two functions were added that stock resolves differently (`tee_primary_misc` and island-local glue remain island-only), which is why defined functions rose by 16 while the shared set rose by 18.

## Newly implemented stock functions (18)

`copy_to_user_str`, `drv_version_read`, `logd`, `mtk_disable_clk`, `mtk_enable_clk`, `plat_register_spi_clk`, `tee_clkmgr_register`, `tee_exit_procfs`, `tee_init_procfs`, `tee_log_open`, `tee_log_read`, `tee_log_release`, `tee_peridev_exit`, `tee_peridev_init`, `tee_version_read`, `teed_version_read`, `teed_version_write`, `tkcore_log_irq_handler`.

## Improved call-set / byte matches

Newly byte-identical (11): `drv_version_read`, `tee_log_release`, `tee_peridev_exit`, `mtk_enable_clk`, `mtk_disable_clk`, `tee_init_sysfs`, `tee_cleanup_sysfs`, `tee_supp_init`, plus three others already counted in the shared set.

Three functions that existed in Phase-2 improved without being newly added:
- `tee_init_sysfs`: DONOR_PORTED + KCFI mismatch → **EXACT_BYTE**
- `tee_cleanup_sysfs`: DONOR_PORTED + call-set diff → **EXACT_BYTE**
- `tee_supp_init`: DONOR_PORTED + call-set diff → **EXACT_BYTE**

## KCFI changes

19 functions gained an exact KCFI ID; none lost one. The remaining 8 mismatches are all pre-existing and out of Phase-3P scope:

`_init_tee_cmd`, `_release_tee_cmd`, `_update_client_tee_cmd`, `cleanup_module`, `init_module`, `tee_copy_from_user`, `tee_shm_alloc_from_rpc`, `tee_wait_queue_get`.

The single in-scope mismatch inherited from Phase 2 (`tee_init_sysfs`, `void` vs `int`) is resolved.

## Import changes

24 imports added, all of which exist in stock's import set:

`__init_waitqueue_head`, `__wake_up`, `clk_disable`, `clk_enable`, `clk_prepare`, `clk_unprepare`, `finish_wait`, `free_irq`, `init_wait_entry`, `kthread_create_on_node`, `kthread_should_stop`, `kthread_stop`, `nonseekable_open`, `of_clk_get_by_name`, `of_find_node_by_name`, `prepare_to_wait_event`, `proc_create_data`, `proc_mkdir`, `proc_remove`, `request_threaded_irq`, `schedule_timeout`, `strcmp`, `strlen`, `wake_up_process`.

One import removed: `kstrtoull`, which existed only because the donor carried a writable `test` sysfs attribute that stock does not have.

Imports still absent from stock: `_dev_err`, `sg_nents`, `strncmp` — all three pre-existing and unchanged by this phase.

`depends` remains empty and there are 0 unresolved symbols, preserving the stock property that tkcore has no intermodule dependencies.

## Export changes

`tee_clkmgr_register` is now exported, taking the island from 17/25 to 18/25 stock exports. No export was fabricated (the rebuilt export set is a strict subset of stock's).

Still missing (7): `__tee_get`, `tee_clkmgr_handle`, `tee_map_cached_shm`, `tee_spi_cfg_padsel`, `tee_spi_transfer`, `tee_spi_transfer_disable`, `tee_unmap_cached_shm`.

## Object and section convergence

| Section | Stock | Phase-2 | Phase-3P |
|---|---:|---:|---:|
| `.text` | `0x9884` | `0x5f1c` | `0x73c0` |
| `.data` | `0x20c` | `0x1b0` | `0x208` |
| `.bss` | `0xa1` | `0xe` | `0x80` |
| `.rodata` | `0x6a3` | `0x318` | `0x4e8` |
| `.rodata.str1.1` | `0x1237` | `0xb92` | `0xf3c` |
| Defined objects | 54 | 27 | 46 |
| Relocations | 3098 | 1815 | 2246 |

Every section moved toward stock. New objects are the five proc pointers, `teed_version`, `klog`, `klog_irq`, the four `proc_ops` tables, the clock-manager list head and mutex, and the two log literals. `.data` shrank relative to its own attribute array by one 32-byte `device_attribute` (the removed `test` attribute) while gaining the clock-manager globals, landing 4 bytes under stock.

## Type-graph changes

`struct tee` keeps its proven `0x138` size. Ten new anchors were added and all pass, taking the layout probe from 31 to **41/41**:

`version_major@0x64`, `version_minor@0x68`, `version_patch@0x6c`, `log_shm@0x70`, `log_shm_len@0x78`, `log_irq@0x80`, `rpc@0xb0`, `refcount@0xb8`, `max_refcount@0xbc`, `stats@0xc0`.

These replace the Phase-2 synthetic placement of `refcount`/`max_refcount`/`stats` in the `0x64` gap, confirming the Phase-3A finding. `struct tee_rpc` shrank from `0x208` to its proven `0x1d8` by dropping the dead `reqsync` mutex.

## Unrelated regressions

**None.** No function that was byte-identical in Phase 2 lost that status, no KCFI ID regressed, no export was dropped, no new import outside stock's set was introduced, and `depends` is still empty. Frozen modules `tkcore_drv`, `tmem_ffa`, `microarray_fp_tee`, `spi-mt65xx`, `ffa_v10` and the GenieZone set were not touched.

## Environmental note

The exact-GKI build initially failed with `clang-17: error: unable to make temporary file`. Root cause was a cached kleaf `kernel_aarch64_env.sh` carrying `TMPDIR="/tmp/.ctx-mode-AapTqD"`, a per-invocation sandbox directory that no longer existed, plus stale in-tree artifacts in `common/`. Both were environmental; the fix was `make ARCH=arm64 mrproper` in `common/` and regenerating the env artifact with a stable `TMPDIR`. No source, toolchain or configuration was changed to work around it.
