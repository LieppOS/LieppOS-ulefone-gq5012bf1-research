# Recommended next coherent unowned batch

After this batch (projected A349/B1/C10/D44/G54) the largest coherent unowned **D** group is the
**MediaTek low-power / power-meter platform** (all KDM, ALPS 5e415e05, P3 loaded platform):

- **LPM:** `mtk-lpm`, `mtk-lpm-plat-v1`, `lpm-gov-MHSP`, `mtk-lpm-dbg-common-v2`, `mtk-lpm-dbg-mt6878`
- **SWPM:** `mtk-swpm`, `mtk-swpm-dbg-common-v1`, `mtk-swpm-dbg-v6878`, `mtk-swpm-cpu-dbg-v6878`
- **SSC:** `mtk-ssc`, `mtk-ssc-dbg-v2`
- **Consumers of the new swpm-perf provider:** `mtk_mbraink` (imports `mtk-swpm-perf-arm-pmu`, now certified here); `cpuqos_v3` (same subsystem neighbourhood)

Why this group:
- The swpm debug modules import the 10 exports of `mtk-swpm-perf-arm-pmu`, whose source and natural CRCs
  are now proven. The reusable engine (`android_kernel_modules_boot_dependencies`) already handles KDM
  targets, provider witnesses and duplicate-exporter derivation.

What must be checked first:
- Exact identities and current classes in the then-current canonical audit.
- Load phase: the targets are second-stage `insmod_sh:vendor` modules.
- The SSPM/MCUPM firmware boundary: Linux host modules only.

The second candidate is the **performance-HAL group** (14 D: `mtk_perf_ioctl*`, `mtk_ioctl_*`, `touch_boost`,
`powerhal_cpu_ctrl`, `uload_ind`, `load_track`, `frs`, `mtk_fpsgo`, `mtk_perf_common`). The remaining
P0_BOOT **G** rows (display glue, RT5133, charge pumps, fuel gauge, panels, TKCore) need independent recipe
closure of historical builds rather than public-source recovery, so they are better handled as a separate
G→A closure batch.
