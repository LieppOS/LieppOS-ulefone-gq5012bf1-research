# Android userspace contract — MTK-MDP-KERNEL

Everything below is read from the reconstructed source and the shipped ROM metadata. No
call was made on hardware, and nothing here claims that stock Android actually exercises a
path.

## 1. Two different submission models

### 1a. `mdp_drv_mt6878` — character device + ioctl

`mdp_driver.c` creates a class/cdev named **`mtk_mdp`** (`MDP_DRIVER_DEVICE_NAME`), binds
the platform driver to OF compatible **`mediatek,mdp`** (the `/mdp` DT node) and installs
`cmdq_ioctl` / `cmdq_ioctl_compat` on ioctl magic **`'x'`**.

The dispatcher accepts these (the compat table additionally forwards the legacy numbers):

| nr | name | direction |
|---:|---|---|
| 4 | `CMDQ_IOCTL_QUERY_USAGE` | W |
| 10 | `CMDQ_IOCTL_QUERY_CAP_BITS` | W (int) |
| 11 | `CMDQ_IOCTL_QUERY_DTS` | W |
| 12 | `CMDQ_IOCTL_NOTIFY_ENGINE` | W (u64) |
| 20 | `CMDQ_IOCTL_ASYNC_EXEC` | W — submit a recorded MDP job |
| 21 | `CMDQ_IOCTL_ASYNC_WAIT` | R — wait/complete |
| 22 | `CMDQ_IOCTL_ALLOC_READBACK_SLOTS` | W |
| 23 | `CMDQ_IOCTL_FREE_READBACK_SLOTS` | W |
| 24 | `CMDQ_IOCTL_READ_READBACK_SLOTS` | W |
| 25 | `CMDQ_IOCTL_SIMULATE` | R |

Legacy numbers 1–9 (`LOCK_MUTEX`, `UNLOCK_MUTEX`, `EXEC_COMMAND`, `ASYNC_JOB_EXEC`,
`ASYNC_JOB_WAIT_AND_CLOSE`, `ALLOC_WRITE_ADDRESS`, `FREE_WRITE_ADDRESS`,
`READ_ADDRESS_VALUE`) are declared in `mdp_driver.h` and routed by the compat handler.
Buffers are dma-buf (`import_ns=DMA_BUF`, `system_heap`); completion is an MDP fence
(`mdp_fence.o`). Submission always goes out as a CMDQ packet, never as direct MMIO.

The module exports exactly one symbol, `mdp_dpc_register` (GPL) — the hook `mtk_dpc.ko`
uses; `modules.dep` confirms `mtk_dpc.ko` depends on `mdp_drv_mt6878.ko`.

### 1b. `mtk-mml` — in-kernel API, no device node of its own

MML has **no** char device and **no** ioctl surface. Its 36 exports are the contract, and
its consumer is the display stack: `mediatek-drm` calls `mml_drm_get_context` /
`mml_drm_query_cap` / `mml_drm_try_frame` / `mml_drm_submit` (plus
`mml_drm_submit_timeout`, `mml_drm_stop`, `mml_drm_config_rdone`, `mml_drm_ctx_idle`,
`mml_drm_racing_config_sync`, `mml_drm_racing_stop_sync`, `mml_drm_split_info`,
`mml_drm_set_panel_pixel`, `mml_drm_dump`, `mml_drm_put_context`). A second
"direct-link / DLE" adaptor (`mtk-mml-dle-adaptor.o`) serves the display direct path.

Userspace therefore reaches MML **through the DRM/display path or the vendor PQ service**,
not through a dedicated node. Completion is a sync fence created on an `mtk_sync` timeline
named `mml_timeline` (`mtk_sync_timeline_create`/`mtk_sync_fence_create`), i.e. the
standard Android sync-file handle.

`mtk-mml-mt6878` registers the platform topology with `mml_topology_register_ip`; it has no
userspace interface at all, only the two module parameters `mml_force_rsz` and
`mml_path_mode`.

## 2. Static userspace consumer candidates

From the shipped ROM metadata (`userspace-consumers.tsv`), owned elsewhere:
`vendor.mediatek.hardware.mmlpq` (+ `vendor.mmlpq-default` init service),
`vendor.mediatek.hardware.pq` / `pq_aidl` (+ `pq_aidl-impl.so`, `vendor.mediatek.
hardware.pq_aidl-default`), `hwcomposer.mtk_common.so`, `libnativedisplay.so`,
`libaispq.so`, `android.frameworks.displayservice`. These are **declaration-level**
evidence only: no trace shows any of them opening `/dev/mtk_mdp` or driving an MML submit
on this device.

## 3. Module parameters as the live-tuning surface

`mtk-mml` exposes 31 writable parameters (`/sys/module/mtk_mml/parameters/`), including
`mtk_mml_msg`, `mml_trace`, `mml_qos`, `mml_qos_log`, `mml_dpc_log`, `mml_pq_disable`,
`mml_hrt_bound`, `mtk_mml_hrt_mode`, `mml_pkt_dump`, `mml_pkt_dump_p`, `mml_comp_dump`,
`mml_cmdq_err`, `mml_slt`, `monitor_interval` and the CRC-compare set
(`mml_pipe0_dest_crc`, `mml_pipe1_dest_crc`, `mml_crc_cmp*`, `mml_crc_err`,
`mml_crc_test`). `drv_debug` is documented in `.modinfo` as "mml driver debug case".
These are the safest observation points for any future authorized runtime test.

## 4. Runtime acceptance still required (none performed)

1. Does `mdp_drv_mt6878` bind to `/mdp` and create `/dev/mtk_mdp`? Does any stock process
   open it?
2. Do the 10 MML components probe and does `mtk-mml-mt6878` register the `mt6878`
   topology successfully?
3. A real submit: CMDQ packet built, GCE channel 16–19 (MML) / 20–21 (MDP) executed,
   WROT output produced, fence signalled.
4. IOMMU translation on ports 0x40/0x42/0x44 with a real dma-buf; no fault callback.
5. The single interrupt (SPI 868, AAL0) firing.
6. Timeout/abort/recovery: `mml_drm_submit_timeout`, CMDQ thread dump, AEE path.
7. Clock/power: all 12 MDPSYS gates, MDPSYS power domain 8, MMDVFS and SLBC transitions,
   DPC (`mml_dpc_*` / `mdp_dpc`) idle behaviour.
8. Whether the legacy MDP path blocks (rdma1/rsz1/wrot1/color0) are used at all.
9. Interaction with the display stack under racing / direct-link mode.

All require an authorized on-device test; this work is entirely offline.
