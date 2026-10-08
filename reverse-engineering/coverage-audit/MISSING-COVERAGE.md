# Current missing-coverage verdict

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

**0 unmapped normalized rows.** The prior Mali ownership hole is filled by the authorized MALI-GPU-KERNEL PARTIAL registration. Ownership is not source/parity closure.

## Six prepared normal-world kernel owners

- **MALI-GPU-KERNEL (PARTIAL)**: ged.ko, mali_kbase_mt6878_r44.ko, mali_mgm_mt6878_r44.ko, mali_prot_alloc_mt6878_r44.ko, mtk_gpu_hal.ko, mtk_gpu_qos.ko, mtk_gpufreq_mt6878.ko, mtk_gpufreq_wrapper.ko. [Handoff](../accelerator-preparation/MALI-GPU-KERNEL/CLAUDE-HANDOFF.md).
- **CAMERA-ISP-KERNEL (PARTIAL)**: c2ps_perf_ioctl.ko, camera_dpe_isp7sp.ko, ccd_rpmsg.ko, imgsensor-glue.ko, imgsensor.ko, mtk-cam-isp7sp.ko, mtk-ipesys-me.ko, mtk-vmm-isp71-regulator.ko, mtk-vmm-notifier.ko, mtk_aie.ko, mtk_aie_debug_7sp_2.ko, mtk_c2ps.ko, mtk_ccd_remoteproc.ko, mtk_ccuv.ko, mtk_hcp.ko, mtk_imgsys_cmdq.ko, mtk_imgsys_isp7sp.ko, mtk_imgsys_v4l2.ko, pda_drv_mt6878.ko. [Handoff](../accelerator-preparation/CAMERA-ISP-KERNEL/CLAUDE-HANDOFF.md).

APUSYS/MDLA/RPMsg is accelerator-kernel ownership, not camera-consumer ownership. Camera child preserves existing function/data proofs; HAL parent stays PARTIAL. MDP is not DRM DONE, and GPUEB/VCP clients are not TinySys IPI DONE. Shared generic infrastructure and proprietary firmware remain explicit boundaries.

RT5133 still denotes an unbound reference client; its supported static DONE scope and rejected rename are unchanged. [Capture correction](notes/RT5133-CORRECTION.md). No new hardware binding/execution or parity is claimed.
