# Stale or corrected claims

| claim | correction |
|---|---|
| Audit: six modules are "D — public source candidate only" | All six now A (byte-exact except build ID). The pinned public candidate was *not* sufficient alone: two modules needed the GQ5012BF1 display-PWM clock delta. |
| Public alps5e41 MT6878 clock source equals the shipped tree | False for `clk-mt6878` and `clk-mt6878-peri`: stock retains `top_disp_pwm_sel` (ID 282) and `peraop_disp_pwm0/1` (IDs 31/32), removed upstream by ALPS `591991d44aad`. |
| "Remove no owner clock node" — the DISP_PWM mux has no owner | On GQ5012BF1 it is owned: `disp-pwm0/1` reference `<&topckgen 282>` and `<&pericfg_ao 31/32>`. |
| `NEXT-CLAUDE-TASK.md` lists clk-fmeter-mt6878 at loader sequence 51 | Normal list position is **50**, recovery **49** (counted from the actual list). |
| Old audit export count for clk-common: 64 | 64 exported **functions**; the module exports **87** symbols including 23 clock-ops data objects (counted from `__crc_*`). |
| `clk-mt6878-vlp` provides the VLP clock tree | It registers only the 4 SCP gates (`mediatek,mt6878-scp`); VLP muxes/factors are registered by `clk-mt6878` (`vlp_cksys`). |
| Clock modules must load after pinctrl because pinctrl precedes them | Stock order only; there is no symbol or DT dependency between them. |
| (this package) every one of the 67 DT consumers is `okay` | Static DT only; `mmc@11230000` is disabled in the live DT by the bootloader (found by PRESERVE:STORAGE). |
