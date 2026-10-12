# Hardware, interface and runtime contract (static, read-only)

## Evidence sources

- **Device tree:** the stock merged DT, `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`.
- **Source:** pinned ALPS 5e415e05, limited to files actually compiled (`evidence/source-inputs/`).
- **Runtime:** the saved load capture records all 14 modules as loaded (`RECORDED_LOADED`). Nothing beyond
  loading was captured. Bindings, scheduler decisions, boost activity and userspace PowerHAL behaviour are
  therefore **UNKNOWN**.
- **Not done:** no phone access, scheduler experiment or boost-threshold change.

## Device-tree contract

| Module | Match | Stock DT | Properties | Label |
|---|---|---|---|---|
| mtk_fpsgo | `mediatek,fpsgo` (fbt_cpu_platform.c) | `/fpsgo` present | `interconnects = <0x16 1 0x16 0>` / `interconnect-names = "fpsgo-perf-bw"`, `required-opps = <0x17>`, `cpu-limit = <2>`, `gcc-enable = <1>`, `fbt-cpu-mask = <0xff 0xf0 0x0f 0x0f 0xf0 0xf0>`, `sbe-resceue-enable = <1>` (OEM spelling as shipped) | ENABLED_IN_STOCK_DT |
| (provider cpufreq_sugov_ext, not in batch) | `mediatek,mtk-lkg` (`sched/mtk_energy_model/v2/static_power.c`, linked into `cpufreq_sugov_ext-y`) | `lkg@114400` (reg 0x114400 +0xc00) present | leakage table for EAS static power | ENABLED_IN_STOCK_DT. It is consumed by the external provider, not by any of the 14 (static_power.c is not among scheduler.ko's 19 compiled files) |
| scheduler | `mediatek,flt` (eas/sched_main.c) | **absent** | — | PUBLIC_SOURCE_ONLY: the FLT DT path is not taken on GQ5012BF1 |
| cpuqos_v3 | `mediatek,cpuqos-v3` (cpuqos_v3_proto.c) | **absent** | — | STOCK_BINARY_IMPLEMENTATION; the platform-driver DT match has no stock node (behaviour without the node is not inferred further) |
| scheduler (fair.c) | `of_find_node_by_name(NULL, "eas-info")` | `eas-info` node (compatible `mediatek,eas-info`) present | — | ENABLED_IN_STOCK_DT |
| others | — | no DT binding | — | — |

## Userspace interfaces (exact ABI preserved by byte-identical objects)

All ioctl numbers and structure layouts come from the pinned headers and are byte-exact in the certified
objects. Nodes are procfs unless a misc device or kobject is noted (per-file `proc_create`/`proc_mkdir`/`misc_register`/
`kobject_create_and_add` census of the compiled sources).

| Module | Nodes | ioctls (`_IOW/_IOR`, type `'g'` unless noted) |
|---|---|---|
| mtk_perf_ioctl | `/proc/perfmgr/perf_ioctl`, `xgff_ioctl`, `xgff_boost_ioctl`, `fpsgo_lr_ioctl` | FPSGO_QUEUE 1, DEQUEUE 3, VSYNC 5, TOUCH 10, SWAP_BUFFER 14, QUEUE_CONNECT 15, BQID 16, GET_FPS 17, GET_CMD 18, GBE_GET_CMD 19, GET_FSTB_ACTIVE 20, WAIT_FSTB_ACTIVE 21, SBE_RESCUE 22, ACQUIRE 23, BUFFER_QUOTA 24, GET_CAM_APK_PID 25, GET_CAM_SERVER_PID 26, SBE_SET_POLICY 27, HINT_FRAME 28, VSYNC_PERIOD 29; XGFFRAME_START/END/MIN_CAP 1–3; XGFFRAME_BOOST_START/END 1–2; FPSGO_LR_PAIR 1, SF_TOUCH_ACTIVE 2 |
| mtk_perf_ioctl_magt | `/proc/perfmgr_magt/magt_ioctl` | MAGT_GET_CPU_LOADING `_IOR('r',0)`, MAGT_GET_PERF_INDEX `_IOR('r',1)`, MAGT_SET_TARGET_FPS 2, MAGT_SET_DEP_LIST 3 |
| mtk_ioctl_powerhal | `/proc/perfmgr_powerhal/ioctl_powerhal`, `ioctl_powerhal_adpf` | POWERHAL_SET_ADPF_DATA 1, GET_ADPF_DATA 2, DSU_CCI_SPORT_MODE 3 |
| mtk_ioctl_touch_boost | `/proc/perfmgr_touch_boost/ioctl_touch_boost` | TOUCH_BOOST_GET_CMD 1 |
| powerhal_cpu_ctrl | `/proc/powerhal_cpu_ctrl/*` | none. Applies per-policy `freq_qos` min/max requests and `cpufreq_set_cci_mode` (cpudvfs) |
| touch_boost | `/proc/touch_boost/*` | none. Registers an `input_handler` (touch events), `freq_qos` requests, hrtimer + kthread |
| cpuqos_v3 | `/proc/cpuqosmgr/cpuqos_ioctl`, kobject `cpuqos` | cgroup-attach vendor hook; cgroup/partition mapping (`cgroup_pd_map`) and `slbc_sram_read/write` calls into mtk_slbc |
| load_track | none | exports 2 symbols (CPU-loading tracking) consumed only by uload_ind |
| uload_ind | `/proc/cpu_loading/*` + 3 `misc_register` devices | sends `kobject_uevent(_env)` loading indications |
| mtk_fpsgo | sysfs (`fpsgo_sysfs.c`), GBE misc device (`gbe_common.c`) | FPSGO control enters through mtk_perf_ioctl's FPSGO_* ioctls: mtk_fpsgo imports 23 `*_fp` hook pointers exported by mtk_perf_ioctl and installs its handlers there |
| mtk_perf_common | kobject `perf` (`perf_tracker`) | `vh_scheduler_tick`; DRAM/DVFSRC OPP queries, blocktag, GPU HAL, QoS bandwidth tracking |
| frs | — | "Frame Rate Smoother": thermal-aware target-FPS adjustment through 5 FPSGO EARA exports (`eara2fstb_get_tfps`, `eara2fstb_tfps_mdiff`, `eara2fbt_set_2nd_t2wnt`, `eara_pre_change_fp`, `eara_pre_change_single_fp`) |

The kernel endpoints exist. Whether a userspace PowerHAL, FPSGO client or MAGT service uses them on GQ5012BF1
is **UNKNOWN**; it is not claimed and was not tested.

## Scheduler and vendor-hook boundaries

| Module | Vendor hooks registered (source) |
|---|---|
| scheduler | 43 `android_rvh/vh` hooks (enqueue/dequeue, can_migrate, check_preempt_wakeup, cgroup attach/online, overutilized, find_busiest_group, …) |
| task_turbo | 16 hooks (prio fork, rtmutex setprio, select_task_rq_fair, setscheduler, set_user_nice, futex/rwsem list add, binder priority, cgroup_set_task) |
| cpuqos_v3 | `vh_cgroup_attach`, `vh_is_fpsimd_save` |
| mtk_fpsgo | `rvh_cpufreq_transition` |
| mtk_perf_common | `vh_scheduler_tick` |

- **scheduler.ko:** built from 19 genuine source files (EAS, FLT, VIP, group-aware, rotate, core_pause,
  DSU power, ADPF). The config has `MTK_EAS=y` and the `MTK_SCHED_*` options `=y` (VIP_TASK, UPDOWN_MIGRATE,
  BIG_TASK_ROTATE, FAST_LOAD_TRACKING), with `GROUP_AWARE=m`.
- **External consumers:** 145 exports are consumed by mtk_fpsgo, touch_boost and certified external modules
  (mtk_core_ctl, mtk_c2ps, mtk-vcodec-common). Their CRCs are reproduced byte-exact.
- **cpufreq_sugov_ext:** provides 72 of the 98 external slots (canonical A, power_policy repo). It shares the
  ALPS `sched` directory, and is only witnessed here.
- **Policy values:** no thresholds, boost levels or policies were changed; the objects are byte-identical to
  stock.

## FPSGO and mbraink relationships

- **mtk_fpsgo:** 811 functions; FBT, FSTB, GBE, composer and XGF compiled from source. It exports 63 symbols.
- **Consumers of those exports:**
  - frs (5), certified here;
  - mtk_mbraink (4: `fpsgo_other2fstb_{register,unregister}_{info,perf}_callback`), certified in LOW-POWER-BATCH-01
    against an ABI witness of this source and now backed by mtk_fpsgo itself being Category A;
  - fpsgo.ko (36), which stays D because its Kbuild links MediaTek prebuilt `xgf_v3_ko_quark*.o_shipped`.
- **mtk_fpsgo's own imports:** mtk_perf_ioctl (23), scheduler (12), powerhal_cpu_ctrl (3), mtk_perf_ioctl_magt (2),
  cpufreq_sugov_ext, ged, mediatek-drm, mtk_cm_mgr and mtk-dvfsrc.

## Load order (stock, providers first everywhere)

- **First stage:** mtk-dvfsrc 44, mtk-dvfsrc-helper 53, mtk_slbc 76, mediatek-drm 89, blocktag 115.
- **Second stage (providers):** mtk_gpu_hal 282, mtk_qos 295, ged 297, thermal_interface 325, cpufreq_sugov_ext 337,
  cpudvfs 338.
- **Second stage (batch):** mtk_ioctl_powerhal 340, powerhal_cpu_ctrl 341, cpuqos_v3 342, scheduler 343,
  mtk_cm_mgr 356, mtk_perf_ioctl 358, mtk_perf_ioctl_magt 359, mtk_fpsgo 360, (fpsgo 361), frs 362,
  mtk_ioctl_touch_boost 389, touch_boost 390, task_turbo 426, mtk_perf_common 427, load_track 430, uload_ind 431.
- **Last:** mtk_mbraink 434.

## Firmware boundaries

None of the 14 talks to tinysys firmware directly. They use only kernel interfaces: cpufreq/freq_qos,
interconnect bandwidth (`fpsgo-perf-bw`), DVFSRC OPP query, SLBC SRAM through mtk_slbc, and GPU through GED/HAL.
Underlying firmware such as the CPU DVFS microcontroller or SSPM is not reconstructed or claimed.
