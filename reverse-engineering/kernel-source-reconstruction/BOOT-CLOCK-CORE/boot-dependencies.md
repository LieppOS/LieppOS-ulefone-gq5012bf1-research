# First-stage boot dependencies

Operands: `vendor_boot` platform ramdisk `lib/modules/modules.load` (184 normal entries) and
`modules.load.recovery` (189), `modules.dep`, and shipped import/export graph
(`reverse-engineering/kernel-source-parity-audit/{LOAD-LIST-EVIDENCE,DEPENDENCY-EDGES}.tsv`).

## Load positions (normal / recovery)

| seq | module | note |
|---:|---|---|
| 3 / 3 | aee_aed | provider of 2 clk-common imports |
| 20–21 | pinctrl-mtk-v2, pinctrl-mt6878 | load **before** the clocks; no clock symbol dependency either way |
| **22** | **clk-common** | |
| **23** | **clk-mt6878** | topckgen/apmixed/VLP/GPU PLLs |
| 24–27 | clk-mt6878-adsp/-cam/-img/-mmsys | other owners |
| **28** | **clk-mt6878-peri** | |
| **29** | **clk-mt6878-bus** | |
| 30 | clk-mt6878-mdpsys | MTK-MDP-KERNEL (DONE) |
| **31** | **clk-mt6878-vlp** | |
| 32–33 | clk-mt6878-vcodec/-ccu | other owners |
| 34–38 | pmic-wrap, spmi-pmic, pmif, mt6315/mt6363/mt6369 regulators | after clocks |
| 40–43 | mtk-vmm-spm, mtk-scpsys(-mt6878, -bringup) | power domains reference topckgen muxes |
| 47–49 | clk-bringup, clk-chk-mt6878, pd-chk-mt6878 | other owners; recovery 46–48 |
| **50 / 49** | **clk-fmeter-mt6878** | |
| 107 / 109 / 112 | mtk-mmc, phy-mtk-ufs, ufs-mediatek-mod | storage consumers (recovery 105/107/110) |

## Symbol dependencies

`modules.dep`: `clk-common: aee_aed`; each of the other five: `clk-common aee_aed`.
Import graph: `clk-common` → 112 GKI + 2 AEE; the five consumers → GKI + `clk-common` only.
`clk-common` is imported by **25** shipped modules (clock domain modules, clk-chk/pd-chk/dbg,
fhctl, scp, vcp, adsp, mediatek-drm, mtk-cam-isp7sp, mmdvfs, mminfra-debug, usb_offload).
The other five export nothing that is imported (`mt6878_pll_force_off` has no shipped importer).

## Must they load before storage, pinctrl, regulators?

* **pinctrl**: no. Stock loads pinctrl first; neither depends on the other's symbols.
* **regulators / PMIC / SCPSYS**: stock loads clocks first; SCPSYS power-domain nodes reference
  topckgen clocks, so they would defer without clk-mt6878.
* **storage**: UFS (`ufshci`, `ufscfg_*`) and MMC reference topckgen/pericfg/ufscfg clocks.
  Without clk-mt6878 + clk-mt6878-peri, the storage controllers defer probe; first-stage init
  then cannot mount from UFS. So for *this* board the clock providers are a hard prerequisite
  for first-stage storage, by DT reference — not by module symbol dependency.
* Recovery uses the same relative order.

The load order was not changed.

## Conditions for a later controlled Slot B test (not performed)

1. Separately authorized procedure; Slot A untouched and known-good; rollback path rehearsed.
2. Replace only these six modules in the Slot B vendor_boot ramdisk with the B1 outputs;
   identical file names, same `modules.load` position; all other modules stock.
3. Same kernel (GKI 12901745) and vermagic; module signature enforcement state documented
   (stock copies are unsigned).
4. Capture serial/ramoops/pstore and `bootprof` before and after.
5. Pass criteria: boot to first-stage mount; `/sys/kernel/debug/clk/clk_summary` (or
   `/proc/clkchk` equivalent) rates/enable counts match a stock capture; no `clkchk` or AEE
   warnings; disp-pwm backlight, UFS, I²C, SPI, UART and USB probe; suspend/resume cycle.
6. Abort on any probe deferral loop, watchdog, or missing UFS.
