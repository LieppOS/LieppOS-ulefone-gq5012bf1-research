# Dependency-aware kernel source reconstruction queue

Frozen audit: 458 binary identities / 457 filenames. This queue does not alter existing components.

## Acceptance and order

1. Essential retained boot contract and storage; 2. radio/security interfaces; 3. active peripherals; 4. optional/diagnostic features.
Completed: BOOT-CLOCK-CORE (6 first-stage clock modules, D->A on 2026-10-09; reverse-engineering/kernel-source-reconstruction/BOOT-CLOCK-CORE). It no longer appears below.
The first project listed below is the current queue head.
`PRESERVE:*` projects must preserve/reproduce existing exact source work, not reverse-engineer it again. `G` is a finite evidence/input-closure question, not a missing-code claim.
All dependency entries below are stock symbol/CRC requirements. A provider gap is recorded separately from implementation effort; retained provider ABI records may support compilation but do not close that provider.
Firmware stays proprietary where documented. Runtime loading never proves successful hardware binding.

## Complete finite project list

### 1. PRESERVE:STORAGE — P0_BOOT
- Modules (10): `blocktag.ko`, `cqhci.ko`, `mtk-mmc-dbg.ko`, `mtk-mmc.ko`, `mtk-wp.ko`, `phy-mtk-ufs.ko`, `rpmb-mtk.ko`, `rpmb.ko`, `ufs-mediatek-dbg.ko`, `ufs-mediatek-mod.ko`.
- Source statuses: G:10.
- Source locations: `reverse-engineering/storage`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump;CANDIDATE:device_modules:drivers/misc/mediatek/sda;CANDIDATE:device_modules:drivers/pinctrl/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 2. CANDIDATE:device_modules:drivers/pinctrl/mediatek — P0_BOOT
- Modules (4): `pinctrl-mt6363.ko`, `pinctrl-mt6878.ko`, `pinctrl-mtk-common-v2_debug.ko`, `pinctrl-mtk-v2.ko`.
- Source statuses: D:4.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/pinctrl/mediatek`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 3. CANDIDATE:device_modules:drivers/regulator — P0_BOOT
- Modules (4): `mt6315-regulator.ko`, `mt6363-regulator.ko`, `mtk-dvfsrc-regulator.ko`, `rt6160-regulator.ko`.
- Source statuses: D:4.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/regulator`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/soc/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 4. CANDIDATE:device_modules:drivers/interconnect/mediatek — P0_BOOT
- Modules (3): `mmqos-common.ko`, `mmqos-mt6878.ko`, `mtk-emi.ko`.
- Source statuses: D:3.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/interconnect/mediatek`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/memory;CANDIDATE:device_modules:drivers/memory/mediatek;CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump;CANDIDATE:device_modules:drivers/misc/mediatek/mmdvfs;CANDIDATE:device_modules:drivers/misc/mediatek/mtk-interconnect;CANDIDATE:device_modules:drivers/misc/mediatek/smi;CANDIDATE:device_modules:drivers/soc/mediatek;PRESERVE:MTK-TINYSYS-IPI`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 5. CANDIDATE:device_modules:drivers/iommu — P0_BOOT
- Modules (1): `mtk_iommu.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/iommu`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/iommu;CANDIDATE:device_modules:drivers/misc/mediatek/smi`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 6. CANDIDATE:device_modules:drivers/misc/mediatek/cmdq/mailbox — P0_BOOT
- Modules (4): `cmdq-platform-mt6878.ko`, `cmdq-sec-drv.ko`, `cmdq-test.ko`, `mtk-cmdq-drv-ext.ko`.
- Source statuses: D:4.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/cmdq/mailbox`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/iommu;CANDIDATE:device_modules:drivers/misc/mediatek/mmp/dummy;CANDIDATE:device_modules:drivers/misc/mediatek/sda;CANDIDATE:device_modules:drivers/misc/mediatek/smi;CANDIDATE:device_modules:drivers/soc/mediatek/devapc;PRESERVE:GZ-TZ-SYSTEM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 7. CANDIDATE:device_modules:drivers/misc/mediatek/iommu — P0_BOOT
- Modules (3): `iommu_debug.ko`, `iommu_secure.ko`, `iommu_test.ko`.
- Source statuses: D:3.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/iommu`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 8. CANDIDATE:device_modules:drivers/misc/mediatek/mtk-interconnect — P0_BOOT
- Modules (1): `mtk-icc-core.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mtk-interconnect`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 9. CANDIDATE:device_modules:drivers/misc/mediatek/smi — P0_BOOT
- Modules (1): `mtk-smi-dbg.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/smi`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/memory;CANDIDATE:device_modules:drivers/memory/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 10. CANDIDATE:device_modules:drivers/char/hw_random — P0_BOOT
- Modules (1): `sec-rng.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/char/hw_random`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 11. CANDIDATE:device_modules:drivers/clk/mediatek — P0_BOOT
- Modules (10): `clk-bringup.ko`, `clk-chk-mt6878.ko`, `clk-dbg-mt6878.ko`, `clk-disable-unused.ko`, `clk-mt6878-cam.ko`, `clk-mt6878-ccu.ko`, `clk-mt6878-img.ko`, `clk-mt6878-mmsys.ko`, `fhctl.ko`, `pd-chk-mt6878.ko`.
- Source statuses: D:10.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/clk/mediatek`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/mcupm/v2;CANDIDATE:device_modules:drivers/soc/mediatek/devapc;PRESERVE:MTK-TINYSYS-IPI`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 12. CANDIDATE:device_modules:drivers/clocksource — P0_BOOT
- Modules (1): `timer-mediatek.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/clocksource`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 13. CANDIDATE:device_modules:drivers/cpufreq — P0_BOOT
- Modules (1): `mediatek-cpufreq-hw.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/cpufreq`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 14. CANDIDATE:device_modules:drivers/devfreq — P0_BOOT
- Modules (1): `mtk-dvfsrc-devfreq.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/devfreq`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/soc/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 15. CANDIDATE:device_modules:drivers/dma-buf/heaps — P0_BOOT
- Modules (3): `mtk_heap_debug.ko`, `mtk_sec_heap.ko`, `system_heap.ko`.
- Source statuses: D:3.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/dma-buf/heaps`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump;CANDIDATE:device_modules:drivers/misc/mediatek/monitor_hang;PRESERVE:TMEM-FFA`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 16. CANDIDATE:device_modules:drivers/dma/mediatek — P0_BOOT
- Modules (1): `mtk-uart-apdma.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/dma/mediatek`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 17. CANDIDATE:device_modules:drivers/gpu/drm — P0_BOOT
- Modules (1): `drm_dma_helper.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/gpu/drm`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 18. CANDIDATE:device_modules:drivers/gpu/drm/mediatek/dpc — P0_BOOT
- Modules (1): `mtk_dpc.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/gpu/drm/mediatek/dpc`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/cmdq/mailbox;CANDIDATE:device_modules:drivers/misc/mediatek/mmp/dummy;CANDIDATE:device_modules:drivers/soc/mediatek;PRESERVE:MEDIATEK-DRM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 19. CANDIDATE:device_modules:drivers/gpu/drm/mediatek/dummy_drm — P0_BOOT
- Modules (1): `mtk_sync.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/gpu/drm/mediatek/dummy_drm`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 20. CANDIDATE:device_modules:drivers/i2c/busses — P0_BOOT
- Modules (1): `i2c-mt65xx.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/i2c/busses`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/pinctrl/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 21. CANDIDATE:device_modules:drivers/input/keyboard — P0_BOOT
- Modules (1): `mtk-pmic-keys.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/input/keyboard`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 22. CANDIDATE:device_modules:drivers/leds — P0_BOOT
- Modules (1): `regulator-vibrator.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/leds`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 23. CANDIDATE:device_modules:drivers/memory — P0_BOOT
- Modules (1): `mtk-smi.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/memory`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 24. CANDIDATE:device_modules:drivers/memory/mediatek — P0_BOOT
- Modules (6): `emi-fake-eng.ko`, `emi-mpu.ko`, `emi.ko`, `mtk_dramc.ko`, `smpu-hook-v1.ko`, `smpu.ko`.
- Source statuses: D:6.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/memory/mediatek`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 25. CANDIDATE:device_modules:drivers/mfd — P0_BOOT
- Modules (1): `mt6338-core.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/mfd`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 26. CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed — P0_BOOT
- Modules (2): `aee_aed.ko`, `aee_rs.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/aee/aed`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `PRESERVE:MEDIATEK-DRM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 27. CANDIDATE:device_modules:drivers/misc/mediatek/aee/hangdet — P0_BOOT
- Modules (1): `aee_hangdet.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/aee/hangdet`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 28. CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump — P0_BOOT
- Modules (1): `mrdump.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/aee/mrdump`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 29. CANDIDATE:device_modules:drivers/misc/mediatek/dcm — P0_BOOT
- Modules (2): `mt6878_dcm.ko`, `mtk_dcm.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/dcm`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 30. CANDIDATE:device_modules:drivers/misc/mediatek/dvfsrc — P0_BOOT
- Modules (1): `mtk-dvfsrc-helper.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/dvfsrc`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/memory/mediatek;CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/soc/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 31. CANDIDATE:device_modules:drivers/misc/mediatek/log_store — P0_BOOT
- Modules (1): `log_store.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/log_store`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 32. CANDIDATE:device_modules:drivers/misc/mediatek/masp — P0_BOOT
- Modules (1): `sec.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/masp`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 33. CANDIDATE:device_modules:drivers/misc/mediatek/mdp — P0_BOOT
- Modules (1): `cmdq_helper_inf.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mdp`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/cmdq/mailbox`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 34. CANDIDATE:device_modules:drivers/misc/mediatek/mmdvfs — P0_BOOT
- Modules (3): `mtk-mmdvfs-debug.ko`, `mtk-mmdvfs-ftrace.ko`, `mtk-mmdvfs-v3-start.ko`.
- Source statuses: D:3.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mmdvfs`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump;CANDIDATE:device_modules:drivers/misc/mediatek/smi;CANDIDATE:device_modules:drivers/soc/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 35. CANDIDATE:device_modules:drivers/misc/mediatek/mminfra — P0_BOOT
- Modules (2): `mtk-mminfra-debug.ko`, `mtk-mminfra-imax.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mminfra`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/cmdq/mailbox;CANDIDATE:device_modules:drivers/misc/mediatek/slbc;CANDIDATE:device_modules:drivers/misc/mediatek/smi;CANDIDATE:device_modules:drivers/misc/mediatek/tinysys_scmi;CANDIDATE:device_modules:drivers/soc/mediatek/devapc`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 36. CANDIDATE:device_modules:drivers/misc/mediatek/mmp/dummy — P0_BOOT
- Modules (1): `mmprofile.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mmp/dummy`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 37. CANDIDATE:device_modules:drivers/misc/mediatek/monitor_hang — P0_BOOT
- Modules (1): `monitor_hang.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/monitor_hang`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 38. CANDIDATE:device_modules:drivers/misc/mediatek/mtprintk — P0_BOOT
- Modules (1): `mtk_printk_ctrl.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mtprintk`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 39. CANDIDATE:device_modules:drivers/misc/mediatek/mtprof — P0_BOOT
- Modules (1): `bootprof.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mtprof`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 40. CANDIDATE:device_modules:drivers/misc/mediatek/pidmap — P0_BOOT
- Modules (1): `pidmap.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/pidmap`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 41. CANDIDATE:device_modules:drivers/misc/mediatek/power_throttling — P0_BOOT
- Modules (6): `mtk_battery_oc_throttling.ko`, `mtk_bp_thl.ko`, `mtk_cpu_power_throttling.ko`, `mtk_dynamic_loading_throttling.ko`, `mtk_gpu_power_throttling.ko`, `pmic_lvsys_notify.ko`.
- Source statuses: D:6.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/power_throttling`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `PRESERVE:CONNECTIVITY`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 42. CANDIDATE:device_modules:drivers/misc/mediatek/sda — P0_BOOT
- Modules (6): `bus-parity.ko`, `cache-parity.ko`, `dbg_error_flag.ko`, `dbgtop-drm.ko`, `irq-dbg.ko`, `last_bus.ko`.
- Source statuses: D:6.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/sda`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 43. CANDIDATE:device_modules:drivers/misc/mediatek/slbc — P0_BOOT
- Modules (1): `mtk_slbc.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/slbc`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 44. CANDIDATE:device_modules:drivers/misc/mediatek/swpm — P0_BOOT
- Modules (2): `mtk-swpm-perf-arm-pmu.ko`, `mtk-swpm.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/swpm`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/qos;CANDIDATE:device_modules:drivers/misc/mediatek/sspm/v3`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 45. CANDIDATE:device_modules:drivers/misc/mediatek/tinysys_scmi — P0_BOOT
- Modules (1): `tinysys-scmi.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/tinysys_scmi`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 46. CANDIDATE:device_modules:drivers/misc/mediatek/vmm_spm — P0_BOOT
- Modules (1): `mtk-vmm-spm.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/vmm_spm`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 47. CANDIDATE:device_modules:drivers/nvmem — P0_BOOT
- Modules (2): `nvmem-mt635x-efuse.ko`, `nvmem_mtk-devinfo.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/nvmem`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 48. CANDIDATE:device_modules:drivers/power/supply — P0_BOOT
- Modules (7): `adapter_class.ko`, `mtk_charger_algorithm_class.ko`, `mtk_pd_adapter.ko`, `mtk_pd_charging.ko`, `mtk_pep.ko`, `mtk_pep40.ko`, `mtk_pep50.ko`.
- Source statuses: D:7.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/power/supply`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `PRESERVE:MTK-DISP-NOTIFY;PRESERVE:TCPC-CLASS;PRESERVE:USB-CHARGER-INTEGRATION`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 49. CANDIDATE:device_modules:drivers/reset — P0_BOOT
- Modules (1): `reset-ti-syscon.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/reset`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 50. CANDIDATE:device_modules:drivers/rtc — P0_BOOT
- Modules (1): `rtc-mt6685.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/rtc`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 51. CANDIDATE:device_modules:drivers/soc/mediatek — P0_BOOT
- Modules (10): `mtk-dvfsrc-start.ko`, `mtk-dvfsrc.ko`, `mtk-mmdvfs-v3.ko`, `mtk-mmdvfs.ko`, `mtk-pm-domain-disable-unused.ko`, `mtk-pmic-wrap.ko`, `mtk-scpsys-bringup.ko`, `mtk-scpsys-mt6878.ko`, `mtk-scpsys.ko`, `mtk-socinfo.ko`.
- Source statuses: D:10.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/soc/mediatek`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/mmp/dummy;CANDIDATE:device_modules:drivers/misc/mediatek/smi;PRESERVE:MTK-TINYSYS-IPI`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 52. CANDIDATE:device_modules:drivers/soc/mediatek/devapc — P0_BOOT
- Modules (2): `device-apc-common.ko`, `device-apc-mt6878.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/soc/mediatek/devapc`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 53. CANDIDATE:device_modules:drivers/spmi — P0_BOOT
- Modules (2): `spmi-mtk-mpu.ko`, `spmi-mtk-pmif.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/spmi`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 54. CANDIDATE:device_modules:drivers/tee/teeperf — P0_BOOT
- Modules (1): `teeperf.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/tee/teeperf`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 55. CANDIDATE:device_modules:drivers/tty/serial/8250 — P0_BOOT
- Modules (1): `8250_mtk.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/tty/serial/8250`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/dma/mediatek;PRESERVE:CONNECTIVITY`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 56. CANDIDATE:device_modules:drivers/watchdog — P0_BOOT
- Modules (1): `mtk_wdt.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/watchdog`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 57. CANDIDATE:kernel:drivers/gpu/drm/display — P0_BOOT
- Modules (1): `drm_display_helper.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/kernel/drivers/gpu/drm/display`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 58. CANDIDATE:kernel:drivers/iio/buffer — P0_BOOT
- Modules (2): `industrialio-triggered-buffer.ko`, `kfifo_buf.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/kernel/drivers/iio/buffer`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 59. CANDIDATE:kernel:drivers/perf — P0_BOOT
- Modules (1): `arm_dsu_pmu.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/kernel/drivers/perf`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 60. FINISH:ST21NFC — P0_BOOT
- Modules (1): `st21nfc.ko`.
- Source statuses: C:1.
- Source locations: `../Reverse Engineer - DONE/ST21NFC/source`.
- Effort: TARGETED_MISSING_CODE_ABI_OR_EQUIVALENCE_PROOF; exact blockers in SOURCE-GAPS.tsv.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 61. FINISH:TRUSTKERNEL-SOURCE-ABI — P0_BOOT
- Modules (1): `tkcore.ko`.
- Source statuses: C:1.
- Source locations: `../Reverse Engineer - BLOCKED/TRUSTKERNEL-ABI-ISLAND/source`.
- Effort: TARGETED_MISSING_CODE_ABI_OR_EQUIVALENCE_PROOF; exact blockers in SOURCE-GAPS.tsv.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 62. FINISH:YFT-DEVINFO — P0_BOOT
- Modules (1): `yft_devinfo.ko`.
- Source statuses: C:1.
- Source locations: `../Reverse Engineer - PARTIAL/YFT-DEVINFO/source`.
- Effort: TARGETED_MISSING_CODE_ABI_OR_EQUIVALENCE_PROOF; exact blockers in SOURCE-GAPS.tsv.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 63. PRESERVE:AUDIO — P0_BOOT
- Modules (22): `adsp.ko`, `audio_ipi.ko`, `clk-mt6878-adsp.ko`, `mt6369-accdet.ko`, `mt6369-regulator.ko`, `mt6685-audclk.ko`, `mt6878-mt6369.ko`, `mtk-afe-external.ko`, `mtk-scp-audiocommon.ko`, `mtk-scp-ultra.ko`, `mtk-scp-vow.ko`, `mtk-soc-offload-common.ko`, `mtk-sp-spk-amp.ko`, `mtk-spmi-pmic-adc.ko`, `mtk-spmi-pmic.ko`, `mtk-vow.ko`, `snd-soc-audiodsp-common.ko`, `snd-soc-mt6369.ko`, `snd-soc-mt6878-afe.ko`, `snd-soc-mtk-common.ko`, `snd-soc-mtk-scp-ultra.ko`, `snd-soc-tfa98xx.ko`.
- Source statuses: G:22.
- Source locations: `reverse-engineering/audio`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/memory/mediatek;CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump;CANDIDATE:device_modules:drivers/misc/mediatek/pbm;CANDIDATE:device_modules:drivers/misc/mediatek/power_throttling;CANDIDATE:device_modules:drivers/misc/mediatek/sda;CANDIDATE:device_modules:drivers/misc/mediatek/slbc;CANDIDATE:device_modules:drivers/soc/mediatek/devapc;PRESERVE:AW883XX-SPEAKER-AMP;PRESERVE:MODEM;PRESERVE:MTK-MBOX;PRESERVE:MTK-TINYSYS-IPI;PRESERVE:SENSOR-HUB`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 64. PRESERVE:AW2013-RGB-LED — P0_BOOT
- Modules (1): `leds-rgb-aw2013.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/AW2013-RGB-LED/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 65. PRESERVE:CONNECTIVITY — P0_BOOT
- Modules (21): `bluetooth.ko`, `bt_drv_6878.ko`, `cfg80211.ko`, `clkbuf.ko`, `connadp.ko`, `connfem.ko`, `conninfra.ko`, `connscp.ko`, `fmradio_drv_connac2x.ko`, `gps_drv_dl_v051.ko`, `gps_pwr.ko`, `gps_scp.ko`, `mac80211.ko`, `mt6685-core.ko`, `mtk-btcvsd.ko`, `mtk_low_battery_throttling.ko`, `pmic_lbat_service.ko`, `uarthub_drv.ko`, `wifi_cooling.ko`, `wlan_drv_gen4m_6878.ko`, `wmt_chrdev_wifi_connac2.ko`.
- Source statuses: G:21.
- Source locations: `reverse-engineering/connectivity`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/power_throttling;CANDIDATE:device_modules:drivers/soc/mediatek/devapc;CANDIDATE:device_modules:drivers/spmi;PRESERVE:MODEM;PRESERVE:MTK-DISP-NOTIFY;PRESERVE:MTK-TINYSYS-IPI;PRESERVE:SENSOR-HUB`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 66. PRESERVE:DISPLAY-GLUE — P0_BOOT
- Modules (9): `backlight_cooling.ko`, `leds-mtk-disp.ko`, `leds-mtk.ko`, `mediatek-drm-gateic.ko`, `met_backlight_api.ko`, `mtk-pwm.ko`, `mtk_disp_sec.ko`, `pwm-mtk-disp.ko`, `rt4831a_drv.ko`.
- Source statuses: G:9.
- Source locations: `reverse-engineering/display-input/backlight-glue/module-inventory.tsv`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/dma-buf/heaps;CANDIDATE:device_modules:drivers/misc/mediatek/cmdq/mailbox;CANDIDATE:device_modules:drivers/misc/mediatek/mtprintk;CANDIDATE:device_modules:drivers/misc/mediatek/power_throttling;CANDIDATE:kernel_modules:met_drv_v3;PRESERVE:MEDIATEK-DRM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 67. PRESERVE:FFA-V10 — P0_BOOT
- Modules (1): `ffa_v10.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/FFA-V10/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 68. PRESERVE:FINGERPRINT-PLATFORM-SHIM — P0_BOOT
- Modules (1): `fingerprint.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/FINGERPRINT-PLATFORM-SHIM/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 69. PRESERVE:MEDIATEK-DRM — P0_BOOT
- Modules (3): `mediatek-drm-panel-drv.ko`, `mediatek-drm.ko`, `mtk_panel_ext.ko`.
- Source statuses: G:3.
- Source locations: `../Reverse Engineer - DONE/MEDIATEK-DRM/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/dma-buf/heaps;CANDIDATE:device_modules:drivers/gpu/drm;CANDIDATE:device_modules:drivers/gpu/drm/mediatek/dummy_drm;CANDIDATE:device_modules:drivers/interconnect/mediatek;CANDIDATE:device_modules:drivers/memory;CANDIDATE:device_modules:drivers/memory/mediatek;CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump;CANDIDATE:device_modules:drivers/misc/mediatek/cmdq/mailbox;CANDIDATE:device_modules:drivers/misc/mediatek/iommu;CANDIDATE:device_modules:drivers/misc/mediatek/mminfra;CANDIDATE:device_modules:drivers/misc/mediatek/mmp/dummy;CANDIDATE:device_modules:drivers/misc/mediatek/mtk-interconnect;CANDIDATE:device_modules:drivers/misc/mediatek/slbc;CANDIDATE:device_modules:drivers/misc/mediatek/smi;CANDIDATE:device_modules:drivers/misc/mediatek/tinysys_scmi;CANDIDATE:device_modules:drivers/soc/mediatek;CANDIDATE:kernel:drivers/gpu/drm/display;PRESERVE:AUDIO;PRESERVE:DISPLAY-GLUE;PRESERVE:MTK-DISP-NOTIFY`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 70. PRESERVE:MICROARRAY-FP-TEE — P0_BOOT
- Modules (1): `microarray_fp_tee.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/MICROARRAY-FP-TEE/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `FINISH:TRUSTKERNEL-SOURCE-ABI;PRESERVE:FINGERPRINT-PLATFORM-SHIM;PRESERVE:SPI-MT65XX`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 71. PRESERVE:MT6375-CHARGER — P0_BOOT
- Modules (5): `mt6375-adc.ko`, `mt6375-auxadc.ko`, `mt6375-battery.ko`, `mt6375-charger.ko`, `mt6375.ko`.
- Source statuses: G:5.
- Source locations: `../Reverse Engineer - DONE/MT6375-CHARGER/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:kernel:drivers/iio/buffer;PRESERVE:CONNECTIVITY;PRESERVE:TCPC-CLASS;PRESERVE:USB-CHARGER-INTEGRATION`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 72. PRESERVE:MTK-DISP-NOTIFY — P0_BOOT
- Modules (1): `mtk_disp_notify.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/MTK-DISP-NOTIFY/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 73. PRESERVE:MTK-MBOX — P0_BOOT
- Modules (2): `mtk-mbox-mailbox.ko`, `mtk-mbox.ko`.
- Source statuses: G:2.
- Source locations: `../Reverse Engineer - DONE/MTK-MBOX/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 74. PRESERVE:MTK-RPMSG-MBOX — P0_BOOT
- Modules (1): `mtk_rpmsg_mbox.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/MTK-RPMSG-MBOX/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:MTK-MBOX`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 75. PRESERVE:MTK-TINYSYS-IPI — P0_BOOT
- Modules (1): `mtk_tinysys_ipi.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/MTK-TINYSYS-IPI/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:MTK-MBOX;PRESERVE:MTK-RPMSG-MBOX`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 76. PRESERVE:PD-DBG-INFO — P0_BOOT
- Modules (1): `pd_dbg_info.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/PD-DBG-INFO/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 77. PRESERVE:PROGRAMMABLE-KEYS — P0_BOOT
- Modules (1): `yft_gpio_keys.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/PROGRAMMABLE-KEYS/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 78. PRESERVE:RT5133-POWER-IC — P0_BOOT
- Modules (2): `extdev_io_class.ko`, `rt5133-regulator.ko`.
- Source statuses: G:2.
- Source locations: `../Reverse Engineer - DONE/RT5133-POWER-IC/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 79. PRESERVE:SC8510-BIDIRECTIONAL-CHARGE-PUMP — P0_BOOT
- Modules (1): `sc851x_charger.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/SC8510-BIDIRECTIONAL-CHARGE-PUMP/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 80. PRESERVE:SC8571-CHARGE-PUMP — P0_BOOT
- Modules (1): `sc8571_charger.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/SC8571-CHARGE-PUMP/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:USB-CHARGER-INTEGRATION`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 81. PRESERVE:SH366003-FUEL-GAUGE — P0_BOOT
- Modules (1): `sh366003_fg.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/SH366003-FUEL-GAUGE/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `FINISH:YFT-DEVINFO`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 82. PRESERVE:SPI-MT65XX — P0_BOOT
- Modules (1): `spi-mt65xx.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/SPI-MT65XX/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 83. PRESERVE:TCPC-CLASS — P0_BOOT
- Modules (1): `tcpc_class.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/TCPC-CLASS/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:PD-DBG-INFO`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 84. PRESERVE:TCPC-MT6375 — P0_BOOT
- Modules (1): `tcpc_mt6375.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/TCPC-MT6375/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:PD-DBG-INFO;PRESERVE:TCPC-CLASS`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 85. PRESERVE:TKCORE-DRV — P0_BOOT
- Modules (1): `tkcore_drv.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/TKCORE-DRV/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `FINISH:TRUSTKERNEL-SOURCE-ABI;PRESERVE:FFA-V10`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 86. PRESERVE:USB — P0_BOOT
- Modules (13): `extcon-mtk-usb.ko`, `mtk_u_ether.ko`, `mtk_usb_f_rndis.ko`, `mtu3.ko`, `mux_switch.ko`, `phy-mtk-xsphy.ko`, `rt_pd_manager.ko`, `tcpci_late_sync.ko`, `usb_boost.ko`, `usb_logger.ko`, `usb_meta.ko`, `usb_offload.ko`, `xhci-mtk-hcd-v2.ko`.
- Source statuses: G:13.
- Source locations: `reverse-engineering/usb`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/dvfsrc;CANDIDATE:device_modules:drivers/misc/mediatek/mtprof;CANDIDATE:device_modules:drivers/soc/mediatek;PRESERVE:AUDIO;PRESERVE:MODEM;PRESERVE:MT6375-CHARGER;PRESERVE:SENSOR-HUB;PRESERVE:TCPC-CLASS`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 87. PRESERVE:USB-CHARGER-INTEGRATION — P0_BOOT
- Modules (3): `charger_class.ko`, `mtk_charger_framework.ko`, `mtk_chg_type_det.ko`.
- Source statuses: G:3.
- Source locations: `../Reverse Engineer - DONE/USB-CHARGER-INTEGRATION/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/power/supply;PRESERVE:TCPC-CLASS`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 88. PRESERVE:VTDR6115-DISPLAY — P0_BOOT
- Modules (1): `panel-ky-vtdr6115-dphy-cmd.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/VTDR6115-DISPLAY/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:MEDIATEK-DRM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 89. PRESERVE:YFT-TPD-GESTURE — P0_BOOT
- Modules (1): `yft_tpd_gesture.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/YFT-TPD-GESTURE/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 90. PRESERVE:GZ-MAIN-MOD — P1_RADIO_OR_SECURITY
- Modules (1): `gz_main_mod.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/GZ-MAIN-MOD/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/dma-buf/heaps;PRESERVE:FFA-V10;PRESERVE:GZ-TRANSPORT;PRESERVE:GZ-TZ-SYSTEM;PRESERVE:TMEM-FFA`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 91. PRESERVE:GZ-TRANSPORT — P1_RADIO_OR_SECURITY
- Modules (5): `gz_ipc_mod.ko`, `gz_irq_mod.ko`, `gz_log_mod.ko`, `gz_trusty_mod.ko`, `gz_virtio_mod.ko`.
- Source statuses: G:5.
- Source locations: `../Reverse Engineer - DONE/GZ-TRANSPORT/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 92. PRESERVE:GZ-TZ-SYSTEM — P1_RADIO_OR_SECURITY
- Modules (1): `gz_tz_system.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/GZ-TZ-SYSTEM/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:GZ-TRANSPORT`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 93. PRESERVE:MODEM — P1_RADIO_OR_SECURITY
- Modules (16): `c2k_usb.ko`, `c2k_usb_f_via_atc.ko`, `c2k_usb_f_via_ets.ko`, `c2k_usb_f_via_modem.ko`, `ccci_auxadc.ko`, `ccci_ccif.ko`, `ccci_dpmaif.ko`, `ccci_fsm_scp.ko`, `ccci_md_all.ko`, `ccci_util_lib.ko`, `ccmni.ko`, `md_cooling_all.ko`, `mddp.ko`, `mtk_md_power_throttling.ko`, `mtk_mdpm.ko`, `rps_perf.ko`.
- Source statuses: G:16.
- Source locations: `reverse-engineering/modem`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/memory/mediatek;CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/aee/mrdump;CANDIDATE:device_modules:drivers/misc/mediatek/pbm;CANDIDATE:device_modules:drivers/misc/mediatek/power_throttling;CANDIDATE:device_modules:drivers/misc/mediatek/sda;CANDIDATE:device_modules:drivers/misc/mediatek/slbc;CANDIDATE:device_modules:drivers/soc/mediatek;CANDIDATE:device_modules:drivers/soc/mediatek/devapc;CANDIDATE:device_modules:drivers/spmi;CANDIDATE:device_modules:drivers/thermal/mediatek;PRESERVE:CONNECTIVITY;PRESERVE:MEDIATEK-DRM;PRESERVE:MTK-TINYSYS-IPI;PRESERVE:SENSOR-HUB`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 94. PRESERVE:TMEM-FFA — P1_RADIO_OR_SECURITY
- Modules (1): `tmem_ffa.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/TMEM-FFA/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `FINISH:TRUSTKERNEL-SOURCE-ABI;PRESERVE:FFA-V10;PRESERVE:GZ-TZ-SYSTEM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 95. FINISH:FT3680-TOUCH — P2_ACTIVE_FEATURE
- Modules (1): `focaltech_touch_spi_ft3680.ko`.
- Source statuses: C:1.
- Source locations: `../Reverse Engineer - PARTIAL/FT3680-TOUCH/source`.
- Effort: TARGETED_MISSING_CODE_ABI_OR_EQUIVALENCE_PROOF; exact blockers in SOURCE-GAPS.tsv.
- Separate provider blockers: `FINISH:YFT-DEVINFO;PRESERVE:MTK-DISP-NOTIFY;PRESERVE:YFT-TPD-GESTURE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 96. PRESERVE:CAMERA-EEPROMS — P2_ACTIVE_FEATURE
- Modules (1): `camera_eeprom_v4l2.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/CAMERA-EEPROMS/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 97. PRESERVE:CAMERA-VCMS — P2_ACTIVE_FEATURE
- Modules (6): `camera_af_media.ko`, `main2_vcm.ko`, `main3_vcm.ko`, `main4_vcm.ko`, `main_vcm.ko`, `sub_vcm.ko`.
- Source statuses: G:6.
- Source locations: `../Reverse Engineer - DONE/CAMERA-VCMS/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 98. PRESERVE:CO5300-REAR-DISPLAY — P2_ACTIVE_FEATURE
- Modules (1): `spi_tiny_co5300_lcd.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/CO5300-REAR-DISPLAY/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `FINISH:YFT-DEVINFO;PRESERVE:HYNITRON-REAR-TOUCH`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 99. PRESERVE:CUSTOM-LDO — P2_ACTIVE_FEATURE
- Modules (1): `custom-ldo.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/CUSTOM-LDO/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:WL2868-CAMERA-LDO`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 100. PRESERVE:FM78100-COMPANION — P2_ACTIVE_FEATURE
- Modules (1): `yft_tiny2c_usb.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/FM78100-COMPANION/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:MT6375-CHARGER`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 101. PRESERVE:HYNITRON-REAR-TOUCH — P2_ACTIVE_FEATURE
- Modules (1): `hynitron.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/HYNITRON-REAR-TOUCH/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `FINISH:YFT-DEVINFO`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 102. PRESERVE:SENSOR-HUB — P2_ACTIVE_FEATURE
- Modules (3): `hf_manager.ko`, `scp.ko`, `sensorhub.ko`.
- Source statuses: G:3.
- Source locations: `reverse-engineering/sensors`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;FINISH:YFT-DEVINFO;PRESERVE:AUDIO;PRESERVE:MTK-DISP-NOTIFY;PRESERVE:MTK-MBOX;PRESERVE:MTK-TINYSYS-IPI`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 103. PRESERVE:WL2868-CAMERA-LDO — P2_ACTIVE_FEATURE
- Modules (1): `custom-ldo-wl2868.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/WL2868-CAMERA-LDO/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 104. CANDIDATE:device_modules:drivers/input/touchscreen — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `tui-common.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/input/touchscreen`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 105. CANDIDATE:device_modules:drivers/media/platform/mtk-jpeg — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk_jpeg.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/media/platform/mtk-jpeg`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/mtk-interconnect;CANDIDATE:device_modules:drivers/soc/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 106. CANDIDATE:device_modules:drivers/misc/mediatek/apusys/sapu — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `sapu.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/apusys/sapu`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/dma-buf/heaps;PRESERVE:GZ-TRANSPORT;PRESERVE:GZ-TZ-SYSTEM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 107. CANDIDATE:device_modules:drivers/misc/mediatek/atf — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `atf_logger.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/atf`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 108. CANDIDATE:device_modules:drivers/misc/mediatek/cache-auditor/cpuqos_v3 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `cpuqos_v3.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/cache-auditor/cpuqos_v3`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/slbc`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 109. CANDIDATE:device_modules:drivers/misc/mediatek/cg_ppt — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk_cg_peak_power_throttling.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/cg_ppt`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 110. CANDIDATE:device_modules:drivers/misc/mediatek/cm_mgr — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (3): `mtk_cm_ipi.ko`, `mtk_cm_mgr.ko`, `mtk_cm_mgr_mt6878.ko`.
- Source statuses: D:3.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/cm_mgr`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/memory/mediatek;CANDIDATE:device_modules:drivers/misc/mediatek/tinysys_scmi;CANDIDATE:device_modules:drivers/soc/mediatek;PRESERVE:MTK-DISP-NOTIFY`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 111. CANDIDATE:device_modules:drivers/misc/mediatek/cpufreq_lite — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `cpudvfs.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/cpufreq_lite`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/sched`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 112. CANDIDATE:device_modules:drivers/misc/mediatek/flashlight — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (2): `flashlight.ko`, `mtk-composite.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/flashlight`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/pbm;CANDIDATE:device_modules:drivers/misc/mediatek/power_throttling;PRESERVE:CONNECTIVITY`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 113. CANDIDATE:device_modules:drivers/misc/mediatek/irtx — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk_irtx_pwm.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/irtx`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `PRESERVE:DISPLAY-GLUE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 114. CANDIDATE:device_modules:drivers/misc/mediatek/lpm — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk-lpm.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 115. CANDIDATE:device_modules:drivers/misc/mediatek/lpm/governors/MHSP — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `lpm-gov-MHSP.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm/governors/MHSP`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 116. CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/mt6878 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk-lpm-dbg-mt6878.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm/modules/debug/mt6878`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/v2;CANDIDATE:device_modules:drivers/misc/mediatek/swpm`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 117. CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/v2 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk-lpm-dbg-common-v2.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm/modules/debug/v2`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/lpm;CANDIDATE:device_modules:drivers/pinctrl/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 118. CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/platform/v1 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk-lpm-plat-v1.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/lpm/modules/platform/v1`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/lpm;CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/v2`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 119. CANDIDATE:device_modules:drivers/misc/mediatek/mbraink — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk_mbraink.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mbraink`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/dvfsrc;CANDIDATE:device_modules:drivers/misc/mediatek/lpm/modules/debug/v2;CANDIDATE:device_modules:drivers/misc/mediatek/performance/fpsgo_v3;CANDIDATE:device_modules:drivers/misc/mediatek/swpm;PRESERVE:MODEM;PRESERVE:SENSOR-HUB`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 120. CANDIDATE:device_modules:drivers/misc/mediatek/mcupm/v2 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mcupm.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mcupm/v2`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `PRESERVE:MTK-MBOX;PRESERVE:MTK-TINYSYS-IPI`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 121. CANDIDATE:device_modules:drivers/misc/mediatek/mmstat — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `trace_mmstat.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/mmstat`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 122. CANDIDATE:device_modules:drivers/misc/mediatek/pbm — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (2): `mtk_pbm.ko`, `mtk_peak_power_budget.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/pbm`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/power_throttling;PRESERVE:CONNECTIVITY;PRESERVE:MODEM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 123. CANDIDATE:device_modules:drivers/misc/mediatek/perf_common — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk_perf_common.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/perf_common`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/dvfsrc;CANDIDATE:device_modules:drivers/misc/mediatek/qos;CANDIDATE:device_modules:drivers/misc/mediatek/sched;CANDIDATE:device_modules:drivers/thermal/mediatek;PRESERVE:STORAGE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 124. CANDIDATE:device_modules:drivers/misc/mediatek/performance — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (4): `mtk_ioctl_powerhal.ko`, `mtk_ioctl_touch_boost.ko`, `mtk_perf_ioctl.ko`, `mtk_perf_ioctl_magt.ko`.
- Source statuses: D:4.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 125. CANDIDATE:device_modules:drivers/misc/mediatek/performance/fpsgo_v3 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk_fpsgo.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/fpsgo_v3`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/cm_mgr;CANDIDATE:device_modules:drivers/misc/mediatek/performance;CANDIDATE:device_modules:drivers/misc/mediatek/performance/powerhal_cpu_ctrl;CANDIDATE:device_modules:drivers/misc/mediatek/sched;CANDIDATE:device_modules:drivers/soc/mediatek;PRESERVE:MEDIATEK-DRM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 126. CANDIDATE:device_modules:drivers/misc/mediatek/performance/frs — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `frs.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/frs`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/performance/fpsgo_v3`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 127. CANDIDATE:device_modules:drivers/misc/mediatek/performance/load_track — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `load_track.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/load_track`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 128. CANDIDATE:device_modules:drivers/misc/mediatek/performance/powerhal_cpu_ctrl — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `powerhal_cpu_ctrl.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/powerhal_cpu_ctrl`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/cpufreq_lite;CANDIDATE:device_modules:drivers/misc/mediatek/performance`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 129. CANDIDATE:device_modules:drivers/misc/mediatek/performance/touch_boost — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `touch_boost.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/touch_boost`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/performance;CANDIDATE:device_modules:drivers/misc/mediatek/performance/powerhal_cpu_ctrl;CANDIDATE:device_modules:drivers/misc/mediatek/sched`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 130. CANDIDATE:device_modules:drivers/misc/mediatek/performance/uload_ind — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `uload_ind.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/performance/uload_ind`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/performance/load_track`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 131. CANDIDATE:device_modules:drivers/misc/mediatek/pmic_protect — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk-pmic-oc-debug.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/pmic_protect`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;PRESERVE:MODEM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 132. CANDIDATE:device_modules:drivers/misc/mediatek/qos — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk_qos.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/qos`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/memory/mediatek;CANDIDATE:device_modules:drivers/misc/mediatek/sspm/v3;CANDIDATE:device_modules:drivers/misc/mediatek/tinysys_scmi`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 133. CANDIDATE:device_modules:drivers/misc/mediatek/sched — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (3): `cpufreq_sugov_ext.ko`, `mtk_core_ctl.ko`, `scheduler.ko`.
- Source statuses: D:3.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/sched`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/cache-auditor/cpuqos_v3;CANDIDATE:device_modules:drivers/misc/mediatek/performance/powerhal_cpu_ctrl;CANDIDATE:device_modules:drivers/thermal/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 134. CANDIDATE:device_modules:drivers/misc/mediatek/ssc — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk-ssc.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/ssc`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/aee/aed;CANDIDATE:device_modules:drivers/misc/mediatek/tinysys_scmi`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 135. CANDIDATE:device_modules:drivers/misc/mediatek/ssc/debug/v2 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk-ssc-dbg-v2.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/ssc/debug/v2`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/ssc`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 136. CANDIDATE:device_modules:drivers/misc/mediatek/sspm/v3 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `sspm_v3.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/sspm/v3`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/tinysys_scmi`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 137. CANDIDATE:device_modules:drivers/misc/mediatek/swpm/modules/debug/v1 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `mtk-swpm-dbg-common-v1.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/swpm/modules/debug/v1`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/swpm`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 138. CANDIDATE:device_modules:drivers/misc/mediatek/swpm/modules/debug/v6878 — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (2): `mtk-swpm-cpu-dbg-v6878.ko`, `mtk-swpm-dbg-v6878.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/swpm/modules/debug/v6878`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/qos;CANDIDATE:device_modules:drivers/misc/mediatek/sspm/v3;CANDIDATE:device_modules:drivers/misc/mediatek/swpm;CANDIDATE:device_modules:drivers/misc/mediatek/swpm/modules/debug/v1;CANDIDATE:device_modules:drivers/thermal/mediatek`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 139. CANDIDATE:device_modules:drivers/misc/mediatek/task_turbo — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `task_turbo.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/task_turbo`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/sched`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 140. CANDIDATE:device_modules:drivers/misc/mediatek/widevine_drm — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `widevine_driver.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/misc/mediatek/widevine_drm`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/dma-buf/heaps`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 141. CANDIDATE:device_modules:drivers/thermal — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `thermal-generic-adc.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/thermal`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 142. CANDIDATE:device_modules:drivers/thermal/mediatek — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (7): `board_temp.ko`, `charger_cooling.ko`, `pmic_temp.ko`, `soc_temp_lvts.ko`, `thermal_interface.ko`, `thermal_trace.ko`, `vtskin_temp.ko`.
- Source statuses: D:7.
- Source locations: `../kernel-research/nothing-mt6878/device_modules/drivers/thermal/mediatek`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/memory/mediatek;PRESERVE:DISPLAY-GLUE;PRESERVE:MEDIATEK-DRM;PRESERVE:USB-CHARGER-INTEGRATION`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 143. CANDIDATE:kernel:drivers/power/reset — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (2): `reboot-mode.ko`, `syscon-reboot-mode.ko`.
- Source statuses: D:2.
- Source locations: `../kernel-research/nothing-mt6878/kernel/drivers/power/reset`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 144. CANDIDATE:kernel_modules:fpsgo_cus — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `fpsgo.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/kernel_modules/fpsgo_cus`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/performance/fpsgo_v3`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 145. CANDIDATE:kernel_modules:hbt_driver_cus — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `hbt.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/kernel_modules/hbt_driver_cus`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 146. CANDIDATE:kernel_modules:msync2_frd_cus — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `msync2_frd.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/kernel_modules/msync2_frd_cus`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `PRESERVE:MEDIATEK-DRM`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 147. PRESERVE:AW36515-FLASH — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `aw36515.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/AW36515-FLASH/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/flashlight`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 148. PRESERVE:AW36518-FLASH — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `aw36518.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/AW36518-FLASH/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/flashlight;FINISH:YFT-DEVINFO`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 149. PRESERVE:AW36518-V2-FLASH — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `aw36518_v2.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/AW36518-V2-FLASH/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/misc/mediatek/flashlight`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 150. PRESERVE:AW883XX-SPEAKER-AMP — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `aw883xx_driver.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/AW883XX-SPEAKER-AMP/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 151. PRESERVE:DW9781C-OIS — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `dw9781c.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/DW9781C-OIS/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:SENSOR-HUB`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 152. PRESERVE:LN2403-CAMPLIGHT — P3_LOADED_PLATFORM_OR_OPTIONAL
- Modules (1): `leds-ln2403.ko`.
- Source statuses: G:1.
- Source locations: `../Reverse Engineer - DONE/LN2403-CAMPLIGHT/source`.
- Effort: SOURCE_PRESERVATION_AND_REPRODUCTION_ONLY; do not redo established reconstruction.
- Separate provider blockers: `PRESERVE:DISPLAY-GLUE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 153. CANDIDATE:kernel_modules:met_drv_v3 — P4_DIAGNOSTIC_OR_REFERENCE
- Modules (10): `met.ko`, `met_emi_api.ko`, `met_gpu_adv_api.ko`, `met_gpu_api.ko`, `met_gpueb_api.ko`, `met_ipi_api.ko`, `met_mcupm_api.ko`, `met_scmi_api.ko`, `met_sspm_api.ko`, `met_vcore_api.ko`.
- Source statuses: D:10.
- Source locations: `../kernel-research/nothing-mt6878/kernel_modules/met_drv_v3`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `CANDIDATE:device_modules:drivers/memory/mediatek;CANDIDATE:device_modules:drivers/misc/mediatek/dvfsrc;CANDIDATE:device_modules:drivers/misc/mediatek/mcupm/v2;CANDIDATE:device_modules:drivers/misc/mediatek/sspm/v3;CANDIDATE:device_modules:drivers/misc/mediatek/tinysys_scmi;PRESERVE:MTK-TINYSYS-IPI`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 154. CANDIDATE:kernel_modules:sched_cus — P4_DIAGNOSTIC_OR_REFERENCE
- Modules (1): `scheduler_ext.ko`.
- Source statuses: D:1.
- Source locations: `../kernel-research/nothing-mt6878/kernel_modules/sched_cus`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

### 155. MALI-DMA-BUF-DIAGNOSTIC — P4_DIAGNOSTIC_OR_REFERENCE
- Modules (1): `mali_dmabuf_test_mt6878_r44.ko`.
- Source statuses: D:1.
- Source locations: `git-object:gpu/gpu_mali/mali_avalon/mali-r44p1/drivers/base/arm/dma_buf_test_exporter/dma-buf-test-exporter.c`.
- Effort: SOURCE_INTEGRATION_THEN_MEASURE_DELTAS; no substantial reverse engineering inferred.
- Separate provider blockers: `NONE`.
- Required proof: Independent pinned input closure + full stock code/data/CRC/KCFI/section/relocation acceptance; G means evidence/preservation unresolved, not code missing.

