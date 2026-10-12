# Baseline and selection

| Item | Detail |
|---|---|
| Baseline | canonical `63f12972` (BOOT-LOWPOWER-INTEGRATION-01 applied): A361 B1 C10 D32 E0 F0 G54 = 362/458, validator PASS, inventory 458/471 PASS |
| Branch | `claude/performance-powerhal-batch-01` |
| Worktree | `ulefone-gq5012bf1-research-claude-performance` |
| Concurrent work | Codex G-SOURCE-RECOVERY-BATCH-01 (Category G only; its assignment excludes these performance modules and canonical writes) |

## Frozen manifest: 14 identities

`BATCH-MANIFEST.tsv`, SHA256 `fa59a9044849c72d77c852132250ee250374105a9262991abd864a9b3dd37285`.

All 14 are canonical D, unowned (candidate source owner only), single vendor_dlkm occurrence, second-stage
`modules.load`, and recorded loaded. None has `.BTF`. Every source directory is present in pinned ALPS `5e415e05`
with no `_shipped` objects.

| Family | Modules | Stock `depends=` inside the batch |
|---|---|---|
| PERF-IOCTL | mtk_perf_ioctl, mtk_perf_ioctl_magt, mtk_ioctl_powerhal, mtk_ioctl_touch_boost | — (pure providers) |
| POWERHAL | powerhal_cpu_ctrl, touch_boost | powerhal_cpu_ctrl→mtk_ioctl_powerhal; touch_boost→scheduler, powerhal_cpu_ctrl, mtk_perf_ioctl, mtk_ioctl_touch_boost |
| FPSGO | mtk_fpsgo, frs | mtk_fpsgo→mtk_perf_ioctl, powerhal_cpu_ctrl, mtk_perf_ioctl_magt, scheduler; frs→mtk_fpsgo |
| SCHED-CPUQOS | scheduler, cpuqos_v3, task_turbo | scheduler→powerhal_cpu_ctrl, cpuqos_v3 |
| LOAD-TRACK | load_track, uload_ind | uload_ind→load_track |
| PERF-COMMON | mtk_perf_common | — |

### External providers

All 12 external providers are canonical A: mtk_slbc, cpufreq_sugov_ext, mediatek-drm, mtk_cm_mgr, mtk-dvfsrc,
ged, mtk-dvfsrc-helper, mtk_qos, thermal_interface, blocktag, mtk_gpu_hal, cpudvfs.

### Why these 14

- **Dependency closure:** `mtk_fpsgo` (the top consumer, also a provider to the now-certified `mtk_mbraink`) pulls
  in the PERF-IOCTL, POWERHAL and SCHED modules, and `scheduler` pulls in `cpuqos_v3`.
- **Same subsystem:** load_track/uload_ind, task_turbo and mtk_perf_common are members of the same ALPS
  `performance` / `perf_common` / `task_turbo` subsystem named in the LOW-POWER-BATCH-01 handoff. They are kept
  because they share subsystem, config (`CONFIG_MTK_PERFORMANCE_MODULE` / `MTK_LOAD_TRACKER` family) and
  load-order neighbourhood (340–431), not to reach a quota.

### Ownership check

- No maintained repository owns any of the 14. The five repository hits are `provider_dependencies` references to
  `scheduler.ko` from certified power-policy / mailbox / pmif / secure-diagnostics / thermal modules.
- No research package contains a reconstruction; mentions are audit baselines, candidate queues and witness
  boundaries.
- No kernel-work workspace builds them; only the earlier stock operand copies exist.

## Considered and excluded (remain canonical D)

| Module | Source | Reason |
|---|---|---|
| fpsgo.ko | Nothing `kernel_modules/fpsgo_cus` @ 5f75a3b | Kbuild links the MediaTek prebuilt objects `xgf_v3_ko_quark.o_shipped` / `_no_cfi.o_shipped`. The code inside them has no source, so building from them would substitute compiled code for source. Not Category-A-reconstructable; a separate shipped-object provenance decision is needed. |
| msync2_frd.ko | `kernel_modules/msync2_frd_cus` | Links prebuilt `mtk_disp_msync.o_shipped`; same reason (and display family). |
| scheduler_ext.ko | `kernel_modules/sched_cus` | Pure source (empty-init stub, MODULE_LICENSE "Proprietary"), but a different source tree and build root, no dependency link to this family, and no stock load-list entry (load order UNKNOWN). Proposed for a separate `kernel_modules _cus` batch. |
| hbt.ko | `kernel_modules/hbt_driver_cus` | Pure-source misc-device ioctl shim with no performance-family dependency; same separate-batch proposal. |
