# Current missing-coverage verdict

Snapshot: **2026-10-08**, source HEAD `c8de6a1`. Actual workspace directory status is authoritative; scope registration is not kernel reconstruction.

**0 unmapped normalized rows.** The prior Mali ownership hole is filled by the authorized MALI-GPU-KERNEL PARTIAL registration. Ownership is not source/parity closure.

## Historical canonical registration discrepancy

Mali is already workspace-DONE. Its older canonical PARTIAL registration below is retained
as pre-existing drift, not a current missing-kernel task; this camera closure does not
repair unrelated component records.

- **MALI-GPU-KERNEL (PARTIAL)**: ged.ko, mali_kbase_mt6878_r44.ko, mali_mgm_mt6878_r44.ko, mali_prot_alloc_mt6878_r44.ko, mtk_gpu_hal.ko, mtk_gpu_qos.ko, mtk_gpufreq_mt6878.ko, mtk_gpufreq_wrapper.ko. [Handoff](../accelerator-preparation/MALI-GPU-KERNEL/CLAUDE-HANDOFF.md).

All six registered accelerator kernel scopes are workspace-DONE. CAMERA-ISP-KERNEL now has complete public-source reconstruction and machine ledgers; its HAL/3A/firmware parent stays PARTIAL. Shared generic infrastructure and proprietary firmware remain explicit boundaries.

RT5133 still denotes an unbound reference client; its supported static DONE scope and rejected rename are unchanged. [Capture correction](notes/RT5133-CORRECTION.md). No new hardware binding/execution or parity is claimed.
