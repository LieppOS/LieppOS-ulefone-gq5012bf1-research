# Proposed PLATFORM-BATCH-03 —34 remaining identities

Recommendation only: revalidate current authoritative inventory and freeze before compiling.
Every identity below is currently uncertified; machine IDs/classes/owners/hashes/paths and
historical evidence are preserved in evidence/next-batch-identities.json. Do not transfer
canonical ownership. Keep four Batch01 CMDQ C members separate unless a new justified
recursive declaration operand appears. No widening the completed27 accounting.

Priority0: current canonical queue head sec-rng (normal-world secure RNG interface only).
Then consolidate watchdog/AEE providers, PMIF-linked MFD/ADC/clock infrastructure and
thermal/CPU/power policy. Use Batch02 source-derived witnesses instead of presumed whole
provider closure. Historical G MFD/ADC/clock/cooling work must be preserved and reproduced,
not rewritten. These host drivers do not authorize secure firmware reconstruction, PMIC
writes, radio/audio algorithms, TinySys commands or any phone interaction.

## Secure host / diagnostics / transport (7)
- `sec-rng.ko`
- `tinysys-scmi.ko`
- `aee_aed.ko`
- `aee_rs.ko`
- `aee_hangdet.ko`
- `mrdump.ko`
- `mtk_wdt.ko`

## Thermal / cooling (9)
- `thermal_interface.ko`
- `thermal_trace.ko`
- `board_temp.ko`
- `pmic_temp.ko`
- `soc_temp_lvts.ko`
- `vtskin_temp.ko`
- `thermal-generic-adc.ko`
- `charger_cooling.ko`
- `backlight_cooling.ko`

## CPU / bandwidth / power (13)
- `mediatek-cpufreq-hw.ko`
- `cpudvfs.ko`
- `cpufreq_sugov_ext.ko`
- `mtk_core_ctl.ko`
- `mtk_qos.ko`
- `mtk_pbm.ko`
- `mtk_peak_power_budget.ko`
- `mtk_cg_peak_power_throttling.ko`
- `mtk_cm_ipi.ko`
- `mtk_cm_mgr.ko`
- `mtk_cm_mgr_mt6878.ko`
- `mtk_dcm.ko`
- `mt6878_dcm.ko`

## PMIF children / common clock supply (5)
- `mtk-spmi-pmic.ko`
- `mtk-spmi-pmic-adc.ko`
- `mt6375.ko`
- `mt6685-core.ko`
- `clkbuf.ko`

Shared public pins/config/Clang/official GKI ABI remain candidates until full stock acceptance.
No compiled-provider byte or stock CRC transplantation. Fresh family clones/B1/B2 mandatory.
Approximately34 independent source-certified additions are possible, not guaranteed.
