# GQ5012BF1 audio hardware topology (kernel view)

Evidence classes: **PROVEN_RUNTIME** (saved live capture), **ENABLED_IN_STOCK_DT** (merged
vendor_boot FDT + dtbo, `workspace/phase4-connfem-hardware/offline-dt/gq5012bf1-merged.dts`),
**STOCK_BINARY_IMPLEMENTATION** (stock .ko, now source-identical), **PUBLIC_SOURCE_ONLY**, **UNKNOWN**.
Phandles are from the merged DTB. Existing route research is reused, not re-derived:
`reverse-engineering/audio/README.md` and `Reverse Engineer - DONE/MT6878-AFE/notes/*`.

## Chain

```text
source/sink -> codec/DAI -> AFE -> DMA/DSP -> kernel/firmware interface
loudspeaker  <- AW88394 (I2C-6 0x34) <- I2S_OUT4 (spk-i2s 0x19) <- DL memif/interconnect <- ALSA PCM (snd-soc-mt6878-afe) | DSP task via audio_ipi -> SCP RV55
SmartPA fb   -> AW88394 I/V -> I2S_IN4 (spk-i2s 0x18) -> UL memif -> capture/feedback
receiver     <- MT6369 RCV <- MTKAIF DL (ADDA) <- interconnect <- MD1 PCM (voice) / DL1
headphones   <- MT6369 HPL/HPR <- ADDA_DL_CH1/2 <- DL1
main mic     -> MT6369 AIN0 -> PGA_L/ADC_L -> MTKAIF MISO0 -> UL9/UL_CM1 -> Capture_1
sub mic      -> MT6369 AIN2 -> PGA_R/ADC_R -> MTKAIF MISO1 -> UL9/UL_CM1 -> Capture_1
headset mic  -> MIC_BIAS_1 -> AIN1 -> ADC_L -> ADDA_UL_CH1 -> Capture_1
jack detect  -> MT6369 ACCDET (PMIC EINT0, AUXADC ch 9) -> input/switch events; FM antenna switch GPIO 195
```

## Nodes and relationships

| Element | Exact stock relationship | Class | Kernel module |
|---|---|---|---|
| AFE | `mt6878-afe-pcm@11050000`, `compatible "mediatek,mt6878-sound"`, reg `0x11050000+0x9000`, GIC SPI 0x188 (IRQ 392), power-domain `<0x22 2>`, 24 pinctrl states (aud clk/dat MOSI/MISO), `etdm-in-sync = 1`, phandle `0x115` | ENABLED_IN_STOCK_DT + PROVEN_RUNTIME (bound) | snd-soc-mt6878-afe, snd-soc-mtk-common |
| Machine card | `sound { compatible "mediatek,mt6878-mt6369-sound"; mediatek,platform = <0x115>; mediatek,spk-i2s = <0x19 0x18>; mediatek,speaker-codec { sound-dai = <0x2ca> } }` | ENABLED_IN_STOCK_DT | mt6878-mt6369 |
| Smart amp | `/soc/i2c@11e01000/speaker_amp@34`, `compatible "mediatek,speaker_amp"`, reset-gpio pio 193, irq-gpio pio 41, re 1000–40000 mΩ, phandle `0x2ca`; Awinic PID 0x2049 (AW88394) | PROVEN_RUNTIME (`/sys/bus/i2c/devices/6-0034` bound to `speaker_amp`) | mtk-sp-spk-amp → aw883xx_driver (exported probe/remove) |
| Codec | `mt6369codec`, `"mediatek,mt6369-sound"`, `mic-type <1 1 1>`, `dmic-mode 0`, io-channel `<0xaf 0x0c>` (`pmic_hpofs_cal`), nvmem `<0xb0>`, `reg-vant18-supply <0xb1>`, `bypass-vant18` | ENABLED_IN_STOCK_DT | snd-soc-mt6369 |
| Jack | `accdet` under `second_pmic@5`, `"mediatek,mt6369-accdet"`, `gpio-accdet-fm-switch = <&pio 0xc3 0>`, `headset-eint-num 0`, 3-key thresholds `<0 0x50 0xdc 0x190>`, io-channel `<0xaf 9>`, status okay | ENABLED_IN_STOCK_DT; YFT FM-switch delta source-proven | mt6369-accdet |
| Codec supplies | MT6369 regulators (SPMI USID 5) | STOCK_BINARY_IMPLEMENTATION | mt6369-regulator |
| Audio clocks | MT6878 ADSP clock provider; MT6685 26 MHz DCXO audio clock (`mt6685_mfd`, exports `mt6685_set_dcxo[_mode]`) | STOCK_BINARY_IMPLEMENTATION | clk-mt6878-adsp, mt6685-audclk |
| DSP tasks | `snd-audio-dsp`, `mtk-dsp-type "RV55"`, 27 task descriptors (`mtk-dsp-primary/deep/offload/voip/call-final/…`), `swdsp-smartpa-process-enable 5`, `mtk-dsp-mem-afe <1 0x40000>`, SPI 0x1ec | ENABLED_IN_STOCK_DT | snd-soc-audiodsp-common, mtk-soc-offload-common |
| DSP transport | `scp-audio-mbox@1cbe0000`, two mailboxes (SPI 0x20a/0x217), reserved `adsp-rsv-audio 0x5c0000`, `ipidma 0x200000`, `logger 0x180000` | ENABLED_IN_STOCK_DT | mtk-scp-audiocommon, adsp, audio_ipi |
| Call enhancement | `speech-usip-mem`, `adsp-phone-call-enh-enable 5`, `adsp-ble-phone-call-enable 1` | ENABLED_IN_STOCK_DT | snd-soc-mtk-common (usip), audio_ipi |
| Ultrasound | `snd-scp-ultra`, DL memif 7, UL memif 0x14 | ENABLED_IN_STOCK_DT; runtime use UNKNOWN | snd-soc-mtk-scp-ultra, mtk-scp-ultra |
| Voice wakeup | VOW pinctrl states (`vow-dat/clk-miso`, `vow-scp-dmic-*`) | ENABLED_IN_STOCK_DT; configured, runtime UNKNOWN | mtk-vow, mtk-scp-vow |
| TFA98xx | driver loaded, no fitted TFA device | STOCK_BINARY_IMPLEMENTATION only (dormant) | snd-soc-tfa98xx |
| External AFE bridge | no board consumer node | STOCK_BINARY_IMPLEMENTATION | mtk-afe-external |

All 21 modules are `RECORDED_LOADED` in the saved stock module-load capture. Physical
speaker placement and grille position are **UNKNOWN** because the DT does not encode them.
Reference-board MT6878 routing was not assumed: every route above is backed by product options
(`RCV_PATH_INT=yes`, `SPK_PATH_NO_ANA=yes`, one speaker) or by the stock DT.
