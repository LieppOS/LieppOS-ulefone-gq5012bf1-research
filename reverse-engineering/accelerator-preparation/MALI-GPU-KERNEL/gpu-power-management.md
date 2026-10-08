# GPU power / frequency management — MALI-GPU-KERNEL

All code paths below are in modules whose `.text`/data are byte-identical to stock. They
are therefore *the stock implementation*, read from the reconstructed source.

## Call chain

```
kbase pm backend (backend/gpu/mali_kbase_pm_*.c, CSF MCU/L2 state machines)
  └─ platform/mt6878/mali_kbase_config_mt6878.c  pm_callbacks
        power_on : gpufreq_power_ctrl_enable()? → gpufreq_power_control(GPU_PWR_ON)
                   → ged_dvfs_gpu_clock_switch_notify(GED_POWER_ON), mtk_notify_gpu_power_change(1)
                   (+ DSU/ACP request via SMC MTK_SIP_KERNEL_GPUEB_CONTROL only if
                    coherency_mode == ACE_LITE)
        power_off: ged notify OFF → gpufreq_power_control(GPU_PWR_OFF)
        runtime PM: kbase_device_runtime_init / gpu_active / gpu_idle
  └─ kbase devfreq (CONFIG_MALI_DEVFREQ, MTK governor mtk_platform_devfreq_governor.c,
     MTK devfreq thermal cooling) over the DT OPP table
ged.ko (DVFS policy, KPI, fast-DVFS on GPUEB: IPI "IPI_ID_FAST_DVFS", gpu_fdvfs sysram)
  └─ mtk_gpufreq_wrapper.ko (gpufreq_v2.c)
        gpueb-support = 1  → every query/commit is an IPI to GPUEB on "IPI_ID_GPUFREQ"
           (struct gpufreq_ipi_data; cmds 0..18: INIT_SHARED_MEM, GET_FREQ/POWER_BY_IDX,
            GET_OPPIDX_BY_FREQ, GET_LEAKAGE_POWER, SET_LIMIT, POWER_CONTROL,
            ACTIVE_SLEEP_CONTROL, COMMIT, DUAL_COMMIT, PDCA_CONFIG, ..., MSSV_COMMIT)
           via mtk_tinysys_ipi (mtk_ipi_register / mtk_ipi_send_compl) + gpueb exports
        else → platform fp registered by mtk_gpufreq_mt6878 (gpufreq_register_gpufreq_fp)
  └─ mtk_gpufreq_mt6878.ko: MFG register map (15 DT ranges), vgpu/vsram regulators,
        PLL/MTCMOS/buck control, AEE DVFS ram-console records (mrdump aee_rr_rec_gpu_dvfs_*)
mtk_gpu_qos.ko (gpu_bm): GPU bandwidth monitor, qos_ipi_to_sspm_scmi_command → SSPM
mtk_gpu_hal.ko: function-pointer hub (mtk_get_gpu_loading/freq/idle/pmu...) used by kbase,
        ged, gpufreq_wrapper and external perf/MET/thermal clients
```

**Suspend/resume:**
* `pm_callback_suspend` and `pm_callback_resume` drive the kbase PM backend, which issues
  `CMD_POWER_CONTROL`/`CMD_ACTIVE_SLEEP_CONTROL` through the wrapper.
* GPU reset is `kbase_pm_do_reset`, with the MTK `POWER_RESET`/`MFG2` backdoor paths
  compiled out for mt6878 (donor Makefile `mt6878` block) and identical to stock.

**Thermal and low-battery throttling:**
* `mtk_gpu_power_throttling` (owned by THERMAL-POWER-HAL) imports `gpufreq_set_limit`.
* `mtk_pbm` is the provider for `register_pbm_gpu_notify`.
* `thermal_interface` imports `gpufreq_get_freq_by_idx`.

All of these CRCs equal the reconstruction's.

**GPUEB boundary:**
* The OPP selection, voltage/frequency sequencing and fast-DVFS policy run in GPUEB
  firmware (`gpueb.ko` is owned by GPU-AI-AUX-KERNEL-INTERFACES; the firmware is in the
  `gpueb` partition).
* The kernel side inside this component is the IPI message format above, which is
  identical to stock; the firmware algorithm is outside it.
