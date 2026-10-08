# Runtime validation — status

**Nothing in this package was executed on hardware.**

| evidence | status |
|---|---|
| Stock load lists name all six in first stage (normal + recovery) | recorded |
| Historical capture (`module-classification.tsv`) reports all six loaded on stock | recorded (name-level) |
| Driver bindings in the saved stock bus snapshot | the snapshot covers I²C devices only; no clock-provider binding captured |
| Saved stock dmesg | ring buffer starts at ~180 s; no boot-time clock probe lines |
| Clock rates / enable state / parents at boot | **not captured** |
| Rebuilt modules loaded, probed or run | **no** |

## Still required (separately authorized Slot B only)

1. First-stage boot with the six rebuilt modules (procedure in `boot-dependencies.md`).
2. Compare `clk_summary` rates/enable/prepare counts and parents against stock.
3. Display-PWM backlight brightness control (exercises the restored DISP_PWM path).
4. UFS/MMC, I²C (13 controllers), SPI, UART, USB, audio AFE, camera sensor mclk probe.
5. GPU PLL force-off path (`mt6878_pll_force_off`) and HW-voter / IPI mux transitions
   (mminfra, disp0, venc; vdec/img/ipe/cam).
6. clkchk / pd-chk reports on suspend; suspend/resume cycles; fmeter measurements.
7. Error paths: clkchk AEE warnings must remain silent.
