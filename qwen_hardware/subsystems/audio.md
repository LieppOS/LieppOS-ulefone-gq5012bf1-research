> **Updated 2026-09-25.** This subsystem note incorporates the verification-pass
> microphone reconstruction. Where older first-pass reports disagree,
> `../verification/findings/microphone-audio-capture.md` and `../../docs/audio.md`
> win. The 2026-08-31 capture used a LieppOS GSI, so framework observations from
> it are not stock Ulefone behavior.

# Audio subsystem

## Hardware found

* Codec: **MT6369** under SPMI `second_pmic@5/mt6369codec`; this is distinct from
  Richtek RT5133 at I2C `5-0018`, which is a camera LDO.
* Built-in microphones: **two analog microphones**. Main role `bottom` routes
  AIN0 -> PGA_L -> ADC_L -> UL1_CH1; sub role `back` routes AIN2 -> PGA_R ->
  ADC_R -> UL1_CH2. Wired-headset mic is a separate accessory input.
* Headset: MT6369 accdet with 3/4-button remote support and FM antenna switching.
* Speaker smart PA: Awinic **AW88394**, I2C `6-0034`, chip ID `0x2049`, driven by
  `aw883xx_driver.ko` through `mtk-sp-spk-amp.ko`.

## Capture path

```text
bottom/back AMICs
 -> MT6369 internal MICBIAS, PGA and ADC
 -> MTKAIF/codec uplink
 -> MT6878 AFE ADDA/UL1
 -> optional AudioDSP/Aurisys processing
 -> MediaTek primary Audio HAL
 -> AudioFlinger / AudioPolicy built-in-mic input
```

Stock DT selects AMIC (`mic-type=<1 1 1>`, `dmic-mode=<0>`). AP DMIC, SCP DMIC,
`Mic3` and `ThreeMic` controls are reusable platform capability, not evidence of
fitted microphones. No enabled separate microphone IC or mic-enable GPIO was
found.

## Use cases and processing

* Default, VoIP, recognition, camcorder, MIC, fast, unprocessed and voice-
  performance profiles request two microphones; VoIP also requests echo ref.
* Dual-mic and normal-handset in-call AP-side DMNR are enabled. Hands-free and
  VoIP DMNR options are disabled. Android AEC/NS/AGC and MediaTek
  Record/Speech/VoIP DMNR/Aurisys calibration families ship.
* Voice wake-up selects one main built-in mic and disables reference, third and
  SCP-DMIC inputs.
* Telephony uses dedicated modem speech profiles (NB/WB/SWB, handset,
  hands-free, headset, HAC, TTY), while ordinary recording uses the record
  parameter families.

## Unused / hidden capability

1. AP/SCP digital-microphone pin groups and digital MicInfo project.
2. Third analog ADC (`AIN1`/`ADC_T`) and generic ThreeMic path.
3. AW88394 TDM/multi-channel and 96-kHz capability not proven in stock use.

## Remaining verification

Perform controlled bottom/back occlusion tests while tracing ALSA controls and
PCM activity. Confirm channel polarity, source-dependent route selection,
proprietary DMNR execution core, microphone part numbers and acoustic ports.

Sources: `../../docs/audio.md` and
`../verification/findings/microphone-audio-capture.md`.
