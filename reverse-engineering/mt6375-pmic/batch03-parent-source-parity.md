# Batch03 PMIC parent/MFD source closure

The selected parent modules `mtk-spmi-pmic`, `mtk-spmi-pmic-adc`, `mt6375`,
`mt6685-core` and `clkbuf` now have independent whole-ELF stock acceptance
in PLATFORM-BATCH-03, PMIF-SPMI owner commit
`100c01a5b2625d3f18b609b11176376ec2f8fc83` in the maintained
android_kernel_modules_pmif_spmi_ulefone_gq5012bf1 repository.

A historical `mt6375.c` IRQ-acknowledgement delta was recovered and preserved as
complete source, then independently reapplied to immutable ALPS5e415e0. This
supersedes any missing-source claim for this selected parent only; it does not
certify MT6375 charger/battery/ADC/Type-C children or exercise an interrupt.

Saved MT6375 I2C address is 0x34 under i2c@11280000, interrupt pinctrl arguments
[15,8]. MT6685 MFD saved slave cells [9,0]. The node named mt6369-auxadc actually
advertises mediatek,mt6368-auxadc; do not rename the silicon lineage from node names.
SPMI PMIC@4/second_pmic@5/MT6319@6 retain slave addresses, not CPU register addresses.

Exact per-module source/function/data/ABI/relocation ledgers and all evidence-level
limits: ../kernel-source-reconstruction/PLATFORM-BATCH-03/PMIF-SPMI/ and
../kernel-source-reconstruction/PLATFORM-BATCH-03/HARDWARE-CONTRACT.md.
The proposed next charging/Type-C/USB batch can reuse these parent APIs; no firmware,
calibration, runtime binding, charging transaction or old component DONE status changed.
