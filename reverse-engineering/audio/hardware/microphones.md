# Microphones (established result)

This pass confirms, and does not replace, the detailed `MICROPHONES` component.

| input | electrical route | normal lane |
|---|---|---|
| main/bottom built-in AMIC | MT6369 MIC_BIAS_0 1.9 V -> AIN0 -> PGA_L -> ADC_L | UL1_CH1 / MISO0 |
| sub/back built-in AMIC | MT6369 MIC_BIAS_0 1.9 V -> AIN2 -> PGA_R -> ADC_R | UL1_CH2 / MISO1 |
| wired-headset microphone | MT6369 MIC_BIAS_1 -> AIN1 -> PGA_L -> ADC_L | UL1_CH1 |

Product configuration says two built-in microphones and selects AMIC, not AP or
SCP DMIC. `builtin_Mic_BackMic` swaps MTKAIF ordering so AIN2 is first for the
back-mic use case. Generic Mic3, ThreeMic and DMIC routes are platform templates.

Normal handset-call two-mic DMNR is enabled. Hands-free and VoIP DMNR feature
options are disabled. VOW is single-main-AMIC. Physical package/port identity
and live per-application switching remain the separate microphone scope's
runtime/teardown boundary.
