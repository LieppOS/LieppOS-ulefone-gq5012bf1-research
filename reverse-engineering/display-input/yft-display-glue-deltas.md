# GQ5012BF1 (Ulefone/YFT) deltas in display glue, PWM, IR, haptics and flash modules

A = shipped stock module, B = rebuild from the stated source. Every "proven"
row means that B becomes byte-identical only with the delta and not without it.

| # | module | donor behaviour | GQ5012BF1 behaviour | evidence | reconstructed delta | confidence |
|---|---|---|---|---|---|---|
| 1 | pwm-mtk-disp | of_match lacks mt6878; probe has no start/end logs (MTK e46af0f) | adds `mediatek,mt6878-disp-pwm0` and `-pwm1` (`mt6799_pwm_data`) before mt6897; `pr_notice("%s start")` / `("%s end")` in probe | stock `.rodata` 2600 B vs 2200 B donor; 4 extra modalias strings; probe printk references | KDM 5326ad7 (3 hunks) | proven (10/10, 44/44) |
| 2 | leds-mtk | KDM baseline (957dac1) lacks battery-percent PT throttle | uses the newer MTK file at 164442952094 (`setPTBrightness`, `mt_leds_bat_low_cb`, `led_bat_per_pt`). Not a YFT change, a **newer MTK drop** than the Nothing baseline. Inactive on this board (`reg-bat-percent-pt` absent) | 25/25 only at 164442952094; later Nothing syncs give 21/25 | KDM 5326ad7 (file-for-file) | proven |
| 3 | mtk_irtx_pwm | no DMA mask handling | new DT property `dma-mask-bit` (live value 0x23 = 35) read at probe, default 32 with `dev_err("rc=%d,dma_mask_bit=%d")`; `dma_set_coherent_mask(DMA_BIT_MASK(dma_mask_bit))` before every TX `dma_alloc_coherent` | stock probe/tx disassembly; extra import `dma_set_coherent_mask` 0xceefb577; extra `.bss` object `dma_mask_bit` | KDM 3b99537 | proven (6/6, 16/16) |
| 4 | regulator-vibrator | code identical | 27 extra non-code lines: +9 before the first logging function, +9 between `vibr_enable`'s two `pr_notice` sites, +9 between `vibr_disable`'s; behaviour unchanged | all 23 `pr_fmt` `__LINE__` immediates match only with cumulative +9/+18/+27 (placement bounded by neighbouring `__LINE__` sites) | KDM ef13d89 (comment padding) | proven layout, text unrecoverable |
| 5 | aw36518 / aw36518_v2 | LieppOS Phase-4 recon | `aw36518_gpio_set` logs a constant `pin(0)`; FLAG1 bits 5 and 4 tested separately; `gpio_init` result checked `< 0`; `reg_show` declares `i` first; stock `__LINE__`s 932/986/991/993/1023/1033 (v2: 930/984/988/990/1020/1030) | per-function disassembly, 13 -> 22 of 23 byte-identical | `backlight-glue/source/aw36518*/phase4-recon-to-exact.diff` | proven |
| 6 | mtk-pwm, leds-mtk-disp, backlight_cooling, rt4831a_drv, mediatek-drm-gateic, mtk_disp_sec, met_backlight_api | — | **no code deltas**: the unmodified donor file is the shipped file | byte-identical rebuild | none | proven |

## Board-level (DT) deltas relevant to display glue

- `/mtk-leds/backlight`: led-mode 4 (CUST_LCM), 0x7FF range, no
  `reg-bat-percent-pt`.
- `/backlight-cooler`: present but not bound to any thermal zone.
- `lcd_ocp2131@3e` (`mediatek,i2c_lcd_bias`) on i2c@11e01000: LCD bias IC node
  kept from an LCD reference design. The AMOLED VTDR6115 path never writes it.
- `panel1@0 gate-ic = <0>`; panel2/panel3 (`jdi,nt36672e`, `truly,td4330`)
  stub nodes have no driver in the image.
- `tiny_lcd` has no `backlight_gpio` property (rear backlight GPIO absent).
- `irtx-pwm`: `pwm-ch = 0`, `pwm-data-invert = 0`, `dma-mask-bit = 35`,
  `pwm-supply = "mt6369_vio28"`.

## Build-environment facts (proven, apply to all KDM modules here)

- Stock `__FILE__` strings are `../kernel_device_modules-6.1/<path>`. Isolated
  `M=` rebuilds need `-fmacro-prefix-map=<M>/=../kernel_device_modules-6.1/<dir>/`
  (only modules that `WARN`/`BUG` embed `__FILE__`: backlight_cooling, leds-mtk).
- `.llvm_addrsig` is present in every stock module, so `KCFLAGS=-faddrsig` is
  needed (global, so `.mod.o` is covered).
- `CONFIG_LTO_NONE` (kout = lieppos/nfc/kout).
- Provider CRCs come from stock `__kcrctab` (`stock-all.symvers`, deduplicated
  against vmlinux `Module.symvers`).
