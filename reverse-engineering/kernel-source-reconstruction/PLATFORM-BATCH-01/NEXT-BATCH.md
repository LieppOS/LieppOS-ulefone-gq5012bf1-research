# Recommended next large batch —27 existing uncertified identities

Not a batch01 amendment or executed assignment. Revalidate/freeze before compiling.
Start with current canonical queue head mtk-icc-core and reuse this shared immutable
cache/config/provider engine. Cohesive families: EMI/DRAMC protection, PMIF/SPMI,
mailbox/TinySys normal-world transport, remaining clock/power-policy support. Preserve
existing G mailbox/IPI/power owners/recipes instead of rewriting them. No modem/audio
implementation or firmware algorithms included. Firmware commands remain forbidden.

- `mtk-icc-core.ko` — D; owner `COVERED-GENERIC`.
- `emi.ko` — D; owner `COVERED-GENERIC`.
- `emi-mpu.ko` — D; owner `COVERED-GENERIC`.
- `emi-fake-eng.ko` — D; owner `COVERED-GENERIC`.
- `smpu.ko` — D; owner `COVERED-GENERIC`.
- `smpu-hook-v1.ko` — D; owner `COVERED-GENERIC`.
- `mtk_dramc.ko` — D; owner `COVERED-GENERIC`.
- `fhctl.ko` — D; owner `COVERED-GENERIC`.
- `pd-chk-mt6878.ko` — D; owner `COVERED-GENERIC`.
- `spmi-mtk-mpu.ko` — D; owner `COVERED-GENERIC`.
- `spmi-mtk-pmif.ko` — D; owner `COVERED-GENERIC`.
- `mtk-mbox.ko` — G; owner `MTK-MBOX`.
- `mtk-mbox-mailbox.ko` — G; owner `MTK-MBOX`.
- `mtk_rpmsg_mbox.ko` — G; owner `MTK-RPMSG-MBOX`.
- `mtk_tinysys_ipi.ko` — G; owner `MTK-TINYSYS-IPI`.
- `mcupm.ko` — D; owner `MTK-TINYSYS-IPI`.
- `sspm_v3.ko` — D; owner `MTK-TINYSYS-IPI`.
- `mtk_battery_oc_throttling.ko` — D; owner `THERMAL-POWER-HAL`.
- `mtk_bp_thl.ko` — D; owner `THERMAL-POWER-HAL`.
- `mtk_cpu_power_throttling.ko` — D; owner `THERMAL-POWER-HAL`.
- `mtk_dynamic_loading_throttling.ko` — D; owner `THERMAL-POWER-HAL`.
- `mtk_gpu_power_throttling.ko` — D; owner `THERMAL-POWER-HAL`.
- `mtk_low_battery_throttling.ko` — G; owner `THERMAL-POWER-HAL`.
- `pmic_lbat_service.ko` — G; owner `THERMAL-POWER-HAL`.
- `pmic_lvsys_notify.ko` — D; owner `THERMAL-POWER-HAL`.
- `mtk-pmic-keys.ko` — D; owner `COVERED-GENERIC`.
- `mtk-pmic-oc-debug.ko` — D; owner `COVERED-GENERIC`.

Separately revisit the four C CMDQ ABI graphs when a justified declaration operand appears.
Their exact source/body progress is preserved; do not rebuild them blindly or force A/B.
