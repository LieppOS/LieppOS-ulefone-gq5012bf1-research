# Board-specific deltas — GQ5012BF1 / YFT (MALI-GPU-KERNEL)

**Result: the GPU kernel modules carry no GQ5012BF1, YFT or Ulefone code.**

* All 8 stock modules are byte-identical, build-id aside, to builds of public MediaTek
  MT6878 sources (NothingOSS / ALPS 5e41). That leaves no room for an OEM source delta in
  compiled code.
* A string scan of the 8 stock modules for `yft|ulefone|gq5012|armor|esun|sunyard` finds 0
  hits.

What *is* MediaTek-specific (relative to ARM's r44p1 DDK) is all present in the public
donors:
* the `platform/mt6878` and `mtk_platform_common` integration;
* the MTK `CONFIG_MALI_MTK_*` feature set selected by the donor `midgard/Makefile`
  `mt6878` block (35 features, from the kbase compile command: `CM7_TRACE`, `COMMON`, `CPUQ_DUMP_ENHANCEMENT`, `CREATE_KCPU_QUEUE_DEBUG`, `CROSS_QUEUE_SYNC_RECOVERY`, `CSG_ERROR_HANDLING`, `DEBUG`, `DEBUG_FS`, `DEVFREQ_GOVERNOR`, `DEVFREQ_THERMAL`, `DIAGNOSIS_MODE`, `DVFS_LOADING_MODE`, `DVFS_POLICY`, `FENCE_DEBUG`, `GPU_BM_CSF`, `IDLE_HYSTERESIS_TIME`, `JIT_RECLAIM_ANTITHRASHING`, `KE_DUMP_FWLOG`, `LOG_BUFFER`, `MEMORY_DEBUG`, `MEMORY_TP_DEBUG`, `MEMTRACK`, `MFGSYS_PM`, `MGMM`, `OOM_LOG_REDUCE`, `PAGE_TABLE_CLUSTERING`, `POWER_TRANSITION_TIMEOUT_DEBUG`, `PREVENT_PRINTK_TOO_MUCH`, `PROC_FS`, `PROTECTED_PATCH`, `SCHEDULER_KTHREAD_PATCH`, `SYSFS`, `TIMEOUT_RESET`, `TRIGGER_KE`, `UNHANDLED_PAGE_FAULT_DEBUG`);
* GED, gpufreq, GPU QoS and the GPU HAL.

The only build-level non-default is file-level revision mixing in kbase: the
page-migration fix from rc-V11.24 (`c3d070e`) on top of the V9.9-era `580d08e`. It is
MediaTek's, not the board's.

**Board data lives in the DT** (`dt-hardware-contract.md`):
* the 46-point OPP table (265–1300 MHz, 600–875 mV);
* the `vgpu` (mt6319 vbuck2) and `vsram` (vsram-cpum) supplies;
* `gpueb-support=1`, `dual-buck=0`;
* `gpu-frame-base-optimize=1`, `firmware-idle-hysteresis-time-ms=5`;
* the protected reserve (2 MiB) and GMPU table (4 MiB).

Whether these values are board or SoC defaults is a DT question. The kernel consumes them
unchanged.
