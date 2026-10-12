# Hardware contract and architecture (static, read-only)

Sources of evidence:
- **DT:** stock merged device tree `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`.
- **Source:** pinned ALPS 5e415e05, limited to the files that were actually compiled (`evidence/source-inputs/`).
- **Runtime:** only the saved capture, which records each module as *loaded*. Binding and probe results were
  not captured, so they are `UNKNOWN`.
- **Safety:** no device was accessed, and no power state, voltage or firmware was touched.

## Device-tree contract

| Module | Match | Stock DT node | Properties of note | Class |
|---|---|---|---|---|
| mtk-lpm | `mediatek,mtk-lpm` | `/mtk-lpm` | `suspend-method = "enable"`, `lpm-kernel-suspend = <0>`, `lpm-gov-enable = <1>`, `logger-enable-states = "mcusysoff_l","mcusysoff_b","system_vcore"`, 16 `irq-remain` entries, 8 `resource-ctrl`, 3 `constraints`, `spm-cond`, `hwreq = "hw_cg","peri_req"`, `mcusys-cnt-chk = <1>`; children `cpupm-sysram@11b000` (0x500), `mcusys-ctrl@c53a000`, `lpm-sysram@11b500` (0x300) | ENABLED_IN_STOCK_DT |
| mtk-lpm / plat-v1 / dbg | `mediatek,sleep` (of_find) | `/sleep@0` | SPM base 0x1c001000 (+0x1000), SPI 0x1f3 level-high | ENABLED_IN_STOCK_DT |
| lpm-gov-MHSP | `arm,idle-state` (of_find) | 8 cpu idle states under `idle-states` (`entry-method = "arm,psci"`). Example: `cpuoff-l` psci param 0x10000, entry 25 µs, exit 57 µs, residency 5700 µs. The deepest state has residency 0xffffffff | — | ENABLED_IN_STOCK_DT |
| mtk-lpm-dbg-* | `mediatek,mddriver` (of_find) | `mddriver` node (looked up by the LPM debug code; purpose not analysed further) | — | ENABLED_IN_STOCK_DT |
| mtk-swpm-* | `mediatek,mtk-swpm` (read by mtk-swpm-perf-arm-pmu, staged A) | `/swpm` | `pmu-boundary-num = <0>`, `pmu-dsu-support = <1>`, `pmu-dsu-type = <0xa>`, `pmu-ai-support = <0>` | ENABLED_IN_STOCK_DT |
| mtk-ssc / mtk-ssc-dbg-v2 | `mediatek,ssc` | **none** | — | STOCK_BINARY_IMPLEMENTATION; see finding below |
| mtk_mbraink | none (genetlink/char device) | — | — | STOCK_BINARY_IMPLEMENTATION |

### New GQ5012BF1 finding: SSC is configured off by the stock DT (static inference)

`ssc_init()` (`drivers/misc/mediatek/ssc/ssc_module.c`) behaves as follows:
1. It registers the platform driver.
2. It looks up `mediatek,ssc` and reads `ssc_enable` from that node, defaulting to 0.
3. When `ssc_enable == 0` it prints `[SSC] disabled` and returns, before any vcore/GPU vlogic-bound voting
   (`regulator_set_voltage(dvfsrc-vcore, 600000/575000 µV)`) or SCMI tinysys notifier registration.

The stock merged DT contains **no** `mediatek,ssc` node. By source and DT alone, the shipped module
therefore loads but stays disabled. This is labelled a static inference, not `PROVEN_RUNTIME`. In this
source family "SSC" refers to the safe-vlogic / vcore-bound coordination with SSPM via SCMI, not to a
generic expansion of the acronym.

## Architecture and firmware boundaries (Linux host side only)

- **LPM.** `mtk-lpm` is the platform driver and notifier/registry: it exports 48 symbols, with 20 imported by
  the dbg-common module and 2 by plat-v1. `mtk-lpm-plat-v1` implements suspend and resource control,
  `lpm-gov-MHSP` is the cpuidle governor, and `mtk-lpm-dbg-common-v2` provides sysfs/debug, with 50 exports
  used by the mt6878 logger, plat-v1 and mbraink.
  - All power-state transitions are requested from the secure monitor through
    `lpm_smc(MTK_SIP_MTK_LPM_CONTROL, …)` (`lpm_smc_cpu_pm`, `lpm_smc_cpu_pm_lp`, `lpm_smc_spm`,
    `lpm_smc_spm_dbg`). The SPM firmware and ATF implementation are **not** reconstructed and not claimed.
  - The `mtk-lpm-dbg-mt6878` logger imports `mtk-swpm`.
- **SWPM.** `mtk-swpm` maps the SSPM reserved-memory region (`sspm_reserve_mem_get_phys/virt/size`), reads
  shared buffers (`sspm_sbuf_get`) and sends `sspm_scmi_command`. The power tables and counters are
  produced by SSPM firmware and read from shared memory; the kernel modules contain no measured
  power or voltage constants. The debug modules consume the 10 `mtk-swpm-perf-arm-pmu` exports, plus GED,
  GPU HAL, QoS and thermal_interface. The DSU-PMU features are selected by the `/swpm` DT node.
- **SSC.** Uses SCMI tinysys status, report and notifier, and AEE. It is disabled by the DT as above.
- **mbraink.** Exposes a char-device ioctl interface (`mbraink_ioctl` / `compat_ioctl`) and a generic-netlink
  family (`MBRAINK_LINK`, multicast group `MBRAINK_MCGRP`). It hooks the `sched_process_fork` and
  `sched_process_exit` tracepoints and collects data from LPM dbg, SWPM, the SCP mbrain debug ops, CCCI shared
  memory, DVFSRC, FPSGO, GED and gpufreq. The matching userspace service is outside the kernel and is not
  claimed to be present or reconstructed.

## Load order (stock first/second-stage contract)

The stock order puts every provider before its consumers:
- sspm_v3 and mtk_qos load before mtk-swpm (370), followed by dbg-common-v1 (371), dbg-v6878 (372) and
  cpu-dbg-v6878 (373).
- mtk-lpm (382) loads before dbg-common-v2 (383), plat-v1 (384), dbg-mt6878 (385) and gov-MHSP (386).
- tinysys-scmi (first stage) loads before mtk-ssc (280) and ssc-dbg-v2 (281).
- mtk_mbraink is last (434), after all nine of its providers.
