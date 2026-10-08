# Userspace and in-kernel contract — GPU-AI-AUX-KERNEL-INTERFACES

Everything below is read from the reconstructed source and the shipped ROM metadata. No
call was made on hardware, and nothing claims that stock Android exercises a path.

## 1. These are in-kernel service modules, not application drivers

Neither `gpueb.ko` nor `vcp.ko` provides an ioctl interface. Their real contract is the
60 exported symbols other kernel modules link against (see
[abi-parity.md](abi-parity.md) §3 and §6). Userspace reaches them only indirectly — via
the GPU stack (`ged`, `mtk_gpufreq_wrapper`) or the video stack (`mtk-vcodec-*`,
`mtk-vcu`) — plus the small observation surface below.

## 2. Observable nodes

### `gpueb.ko`

* **Misc device** `/dev/gpueb` (`MISC_DYNAMIC_MINOR`) with `gpueb_log_file_ops`
  (read/poll/open over the GPUEB log buffer; the three `__kcfi_typeid_gpueb_log_if_*`
  entries are exactly these). The DT sets `gpueb-logger-support = 0` on this board, so the
  logger is not expected to produce data here.
* **Procfs** `/proc/gpueb/` with `gpueb_status`, `gpueb_dram_user_status`,
  `force_trigger_wdt` (mode 0660). `gpueb_ipi_test` is compiled out (`IPI_TEST`).
* **Procfs** `/proc/gpueb_hw_voter/hw_voter_dbg`.
* **Sysfs** `gpueb_mobile_log` (RW).
* Platform driver bound to OF `mediatek,gpueb`; module aliases
  `of:N*T*Cmediatek,gpueb` and `of:N*T*Cmediatek,gpuebC*`.

### `vcp.ko`

* **Misc device** `/dev/vcp` — registered, but with **no** `fops` in the shipped build
  (`CONFIG_MTK_TINYSYS_VCP_DEBUG_SUPPORT` unset), so it is a presence/attribute anchor,
  not a data channel.
* **Sysfs attributes** on that device: `vcp_register_on` (WO), `vcp_deregister_off` (WO),
  `vcp_A_status` (RO), `vcp_A_reg_status` (RO), `vcp_A_db_test` (WO), `vcp_ee_enable` (RW),
  `vcp_A_awake_lock` (RO), `vcp_A_awake_unlock` (RO), `vcp_ipi_test` (RW), `wdt_reset` (WO),
  `vcp_reset` (WO), `recovery_flag` (RW), `vcpctl`, plus the logger set
  (`vcp_mobile_log`, `log_filter`, `vcp_A_get_last_log`, `vcp_A_logger_wakeup_AP`,
  `vcp_A_mobile_log_UT`).
* Platform driver bound to OF `mediatek,vcp`, with secondary drivers for
  `mediatek,vcp-io-{vdec,venc,work,sec}` (and `ube-lat` / `ube-core`, which have no node
  here) that materialise the per-use DMA devices returned by `vcp_get_io_device()`.

### `vcp_status.ko`

No device node at all. It exists purely to publish an early, dependency-free symbol set
(`depends=` is empty) so that ramdisk-stage consumers can link before `vcp.ko` exists, and
to receive `vcp.ko`'s own function/ipidev/mminfra pointers at probe time via `vcp_set_fp`,
`vcp_set_ipidev`, `vcp_set_mminfra_cb`.

## 3. The actual application→kernel→firmware chains (as far as evidence permits)

* **Video:** app → `MediaCodec` → vendor Codec2 → `/dev/video*` + `/dev/vcu`
  (MTK-VCODEC-KERNEL, DONE) → `vcp_register_feature(VDEC/VENC_FEATURE_ID)`,
  `vcp_ipidev` IPI, `vcp_get_reserve_mem_*`, `vcp_get_io_device` (this component) →
  VCP firmware. The kernel half of this chain is now fully reconstructed on both sides;
  the firmware half is retained.
* **GPU DVFS:** `vendor.gpuserv` / `ged` / `mtk_gpufreq_wrapper` (MALI-GPU-KERNEL, DONE)
  → `get_gpueb_ipidev` + `gpueb_get_send_PIN_ID_by_name("IPI_ID_GPUFREQ"/"IPI_ID_FAST_DVFS")`
  + `gpueb_get_gpr_addr` (this component) → GPUEB firmware.
* **MM bandwidth / power:** `mmqos-common`, `mtk-mmdvfs-v3`, `mtk-cmdq-drv-ext`,
  `mtk-mminfra-debug`, `mediatek-drm`, `mtk_imgsys_cmdq` → `vcp_status` early API.

No userspace library in the shipped ROM was observed opening `/dev/vcp` or `/dev/gpueb`;
the vendor GPU libraries (`libgpud*.so`, `libmtkgpuserv.so`) are declaration-level
candidates only and are owned elsewhere.

## 4. Runtime acceptance still required (none performed)

1. Does `gpueb.ko` bind `/soc/gpueb@13c00000`, and does `vcp.ko` bind `/soc/vcp@1ea00000`
   and the four `vcp-io-*` nodes?
2. Does either firmware actually boot (GPUEB release, VCP core/hart start, readiness
   handshake, `is_vcp_ready` turning true)?
3. A real IPI round trip on at least one GPUEB channel and one VCP mailbox, with the
   declared slot geometry.
4. Mailbox interrupts: GPUEB SPI 273; VCP SPI 202–206; the VCP watchdog SPI 200.
5. Feature refcount behaviour under a real decode/encode (`vcp_register_feature(VDEC)` →
   frequency vote → release).
6. Reserved-memory and IOMMU mapping through `vcp_get_io_device` with a real dma-buf.
7. Suspend/resume (`is_vcp_suspending`, `vcp_awake_lock/unlock`, `pwclkcnt`).
8. Fault propagation: watchdog, exception dump, AEE record, `mrdump` extra file,
   `vcp_wdt_reset` and `wait_vcp_ready_to_reboot` recovery.
9. Whether the GPUEB logger (DT-disabled) and `/dev/vcp` (fops-less) are genuinely inert
   on this board.

All require an authorized on-device test; this work is entirely offline.
