# Hardware contract (static, read-only evidence)

Evidence classes: `PROVEN_RUNTIME`, `ENABLED_IN_STOCK_DT`, `STOCK_BINARY_IMPLEMENTATION`,
`PUBLIC_SOURCE_ONLY`, `UNKNOWN`.

- **DT source:** stock merged device tree `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`
  (vendor_boot base FDT `fdt-00-off-03b76040` plus dtbo entry 0).
- **Runtime:** the only runtime fact is the saved first-stage capture, which shows each module *loaded*
  (`loaded_in_capture=y`). Device binding/probe success was not captured, so it is recorded as `UNKNOWN`
  and never inferred.
- **Matching:** compatibles come from stock `modinfo` `of:` aliases. Where a module has no alias, they come
  from the pinned ALPS 5e415e05 driver match table.
- **Data protection:** no calibration, eFuse, NVRAM or secure data was read from a device, and none was
  generated.

| Module | Compatible / match | Stock DT node(s) | reg / IRQ / clocks / supplies | Class (binding) |
|---|---|---|---|---|
| timer-mediatek | `mediatek,mt6765-timer` (DT also lists `mediatek,mt6878-timer`) | `soc/systimer@1cc10000` | reg 0x1cc10000+0x1000; SPI 0xf9 level-high; clocks `<0xe0>` | ENABLED_IN_STOCK_DT (binding UNKNOWN) |
| 8250_mtk | `mediatek,mt6577-uart`, `mediatek,mt6985-uart` | `soc/serial@11001000`, `@11002000`, `@11003000` | SPI 0x18d/0x18e/0x18f | ENABLED_IN_STOCK_DT |
| i2c-mt65xx | 12 SoC compatibles; this board uses `mediatek,mt6989-i2c` | 15 controllers; `i2c@11280000` carries `mediatek-fifo-use-polling;` and hosts mt6375@34, rt5133@18, rt6160@75 | reg 0x11280000 + APDMA 0x11300580; SPI 0x195 | ENABLED_IN_STOCK_DT; **new GQ5012BF1 finding**: the polling-mode property uses the OEM hyphenated spelling, matching the stock driver string |
| reset-ti-syscon | `ti,syscon-reset` | `syscon@112b8000/reset-controller`, `syscon@112bb000/reset-controller` | one `resets = <0xb9 …>` consumer | ENABLED_IN_STOCK_DT |
| rtc-mt6685 | `mediatek,mt6685-rtc` | `soc/spmi@1cc04000/mt6685_mfd/mt6685_rtc` (status okay) | MFD IRQ `<0x09 0x00>` on SPMI PMIC MT6685 | ENABLED_IN_STOCK_DT |
| regulator-vibrator | `regulator-vibrator` | `/regulator-vibrator` label `vibrator` | min-volt 2 200 000 µV, max-volt 3 500 000 µV, vib-supply `<0x63>` | ENABLED_IN_STOCK_DT |
| nvmem_mtk-devinfo | `mediatek,devinfo` | `/efuse@11f10000` with 12 `segment@…` cells | 7 `nvmem-cells` consumer properties elsewhere in the DT | ENABLED_IN_STOCK_DT. Driver exposes eFuse/devinfo **read-only**; no cell contents examined. |
| mtk-vmm-spm | `mediatek,vmm_spm_mt6878` | `/vmmspm` | reg 0x1c001000 (SPM_BASE); `vmm-pmic-supply` `<0x4d>` | ENABLED_IN_STOCK_DT; SPM firmware boundary |
| mtk-mminfra-imax | `mediatek,mminfra-imax` | `mminfra-imax@1e80b000` | 6 regions (mminfra fake, dispsys, mdpsys, disp larb0/1, mdp larb0); fake ports 6/5/4 | ENABLED_IN_STOCK_DT |
| mtk_dpc | `mediatek,mt6878-disp-dpc` (and mt6989) | `soc/disp-dpc@14020000` | DPC/VLP/SPM/HW-vote/DVFSRC/mminfra-hangfree regions; SPI 0x157, 0x158 | ENABLED_IN_STOCK_DT; SPM/VLP hardware-vote boundary |
| sec | `mediatek,masp`, `mediatek,security_ao` | `masp@1040e000`, `security-ao@1040d000` | — | ENABLED_IN_STOCK_DT; secure-boot policy lives in preloader/TEE (not reconstructed) |
| teeperf | `mediatek,teeperf` | `/teeperf` (cpu-type 1, cpu-map 1) | — | ENABLED_IN_STOCK_DT; TEE-side implementation not reconstructed |
| arm_dsu_pmu | `arm,dsu-pmu` | `/dsu-pmu-0` | PPI 0x23 | ENABLED_IN_STOCK_DT |
| mtk-swpm-perf-arm-pmu | none (module_init, perf events) | — | provides 10 exports to vendor_dlkm swpm debug and mbraink | STOCK_BINARY_IMPLEMENTATION |
| kfifo_buf / industrialio-triggered-buffer | library modules | — | consumer mt6375-adc (MT6375 on `i2c@11280000`) | STOCK_BINARY_IMPLEMENTATION |

Firmware/secure-world boundaries (SSPM/SPM, TEE, MASP) are runtime interfaces. Matching the Linux
host modules to stock says nothing about reconstructing those firmware components.
