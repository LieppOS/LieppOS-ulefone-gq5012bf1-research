# IR blaster kernel provider — closure

- **Chain:**
  `consumer_ir -> IConsumerIr AIDL example wrapper -> consumerir.common.so -> /dev/lirc0 -> rc-core -> mtk_irtx_pwm.ko -> mtk-pwm.ko PWM0 (memory/DMA mode) -> emitter on mt6369_vio28 (2.8 V)`.
- **DT `/irtx-pwm`:** `mediatek,irtx-pwm`, `pwm-ch 0`, `pwm-data-invert 0`,
  `dma-mask-bit 35`, `pwm-supply "mt6369_vio28"`.
- **DT `pwm@11008000`:** `mediatek,pwm`, pwm-version 3, irq 469, clocks
  PWM1..4/HCLK/main, `bclk-sw-ctrl` offsets.
- **mtk_irtx_pwm.ko** (`9eaf53b9…`): 6/6 functions, 16/16 data, 23/23
  imports, 6/6 modinfo; section-equal except build-id; B1==B2.
  - One GQ5012BF1 delta: the `dma-mask-bit` property plus
    `dma_set_coherent_mask` before each TX buffer allocation (KDM 3b99537).
- **mtk-pwm.ko** (`06c68f5d…`): 87/87 functions, 30/30 data, 27/27 imports,
  5/5 exports (`mt_pwm_clk_sel_hal`, `mt_pwm_disable`, `mt_pwm_dump_regs`,
  `pwm_set_easy_config`, `pwm_set_spec_config`); no source delta.
  - Consumers: `mtk_irtx_pwm` and `leds-ln2403`
    (`pwm_set_spec_config`, `mt_pwm_disable`).
- LIRC protocol and carrier table: unchanged from the existing IR-BLASTER
  analysis.
- Remaining: emitter part identification and authorized optical/waveform test
  (runtime/physical only).
