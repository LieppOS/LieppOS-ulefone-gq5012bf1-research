# Audio

Last verified: 2026-09-25

## VERIFIED

### Hardware ownership

- The machine card is `mediatek,mt6878-mt6369-sound`; its platform is the
  MT6878 AFE at `soc/mt6878-afe-pcm@11050000`.
- The internal codec/headset block is **MT6369** under SPMI
  `second_pmic@5/mt6369codec`, with a separate MT6369 `accdet` path. I2C
  `5-0018` is not this codec: it is the separate Richtek RT5133 camera-LDO path (MT6878 base-DTB declaration only: the client is not bound and no chip answers on GQ5012BF1; camera LDO is WL2864C `11-0029` — see `reverse-engineering/power/rt5133/`).
- The loudspeaker amplifier is an **Awinic AW88394** at I2C `6-0034` (chip ID
  `0x2049`).

### Built-in microphone topology

- The fitted product configuration selects **exactly two built-in analog
  microphones (AMICs)**: main role `bottom`, sub role `back`.
- This is not inferred from generic mixer names. The stock MT6369 DT explicitly
  selects analog mode with `mediatek,mic-type = <1 1 1>` and
  `mediatek,dmic-mode = <0>`. The stock HAL's `MicInfo` parser branches on that
  DT mic type; value 1 selects project `SPH1642HT5H_REV_B`, whose two records
  are `MicType=AMIC`, `MicMain=bottom`, `MicSub=back`.
- The normal two-microphone capture path routes:

  ```text
  bottom/main -> MT6369 AIN0 -> PGA_L -> ADC_L -> UL1_CH1/MISO0_L
  back/sub    -> MT6369 AIN2 -> PGA_R -> ADC_R -> UL1_CH2/MISO0_R
  ```

  `builtin_Mic_BackMic` selects only the second lane (`AIN2` / `ADC_R` /
  `UL1_CH2`). `builtin_Mic_ThreeMic` adds AIN1/ADC_T, but is unused capability
  and does not prove a third fitted microphone.
- There is no built-in analog front microphone in the active calibration.
  `front` appears only in dormant alternative data. Front/rear video capture is
  not assigned a distinct physical mic in the static artifacts; camcorder
  requests two microphones and therefore uses the normal dual built-in input
  unless runtime routing overrides it.
- Wired-headset microphone capture is a separate accessory route
  (`AIN0`, `ACCDET_MIC_MODE_LOW_COST_WITHOUT_IN_BIAS`) and is not part of the
  two built-in-microphone count.

### Bias, regulator and pin control

- Active analog capture uses MT6369 codec-internal `MIC_BIAS_0` programmed to
  **1.9 V** for both built-ins. The normal dual route enables
  `Audio_MicSource1_Setting = ADC1`,
  `Audio_MicSource2_Setting = ADC3`, `PGA_L_Mux = AIN0`, and
  `PGA_R_Mux = AIN2`.
- The codec DT references `mt6369_vant18`, but sets
  `mediatek,bypass-vant18 = <1>`; VANT18 is not evidence for an external mic
  rail on the fitted path.
- AP DMIC and SCP voice-wakeup DMIC pinctrl groups exist as SoC capability, but
  the active project does not select them. Dormant mixer paths (`DMic`,
  `DMic3`, `DMIC1`, `SCP_DMIC`) and the digital `SPK0641HT4H_1_Rev_A` MicInfo
  project are alternatives, not populated-device evidence.
- No enabled external microphone codec/IC, microphone-specific I2C/SPI device,
  or microphone-enable GPIO was found. Passives and the exact microphone part
  numbers still require PCB inspection.

### Kernel, HAL and Android route

```text
physical AMICs
  -> MT6369 internal MICBIAS/PGA/ADC
  -> MT6369 codec uplink / MTKAIF TX
  -> MT6878 AFE (`ADDA_UL*`, `UL1`/`UL2` memif)
  -> optional DSP offload via `audio_ipi.ko` / AudioDSP common
  -> `/vendor/bin/hw/android.hardware.audio.service.mediatek`
     + `audio.primary.mediatek.so`
  -> HIDL Audio 7.1 / MediaTek `IMtkAudio/default`
  -> AudioFlinger / AudioPolicy
  -> Android built-in mic, back mic or wired-headset input
```

The machine, codec and AFE modules are `mt6878-mt6369.ko`,
`snd-soc-mt6369.ko`, and `snd-soc-mt6878-afe.ko`. Stock mixer XML supplies the
route controls; AudioPolicy exposes built-in mic and wired-headset inputs, but
not separate Android addresses for bottom and back.

### Use cases and processing

- `UplinkConfiguration_AudioParam.xml` requests two microphones for Default,
  VoIP, Recognition, Camcorder, MIC, Fast Record, Unprocessed and Voice
  Performance scenarios. `VoIP` additionally requests echo reference.
- Stock options enable dual-mic support and normal-handset in-call AP-side
  DMNR. Hands-free and VoIP DMNR options are disabled. `RecordDMNR`,
  `SpeechDMNR` and `VoIPDMNR` calibration families still ship; file presence
  alone does not prove profile activation.
- Android preprocessing exposes AEC, NS and AGC, but policy attaches AEC only
  to the `voice_communication` stream. MediaTek Aurisys/
  `mtk_speech_enh` supplies vendor record/VoIP gain and enhancement components.
- Telephony call capture is modem-oriented and has NB/WB/SWB handset,
  hands-free, headset, HAC and TTY speech profiles. Ordinary recording uses the
  record parameter families and the AFE/DSP path rather than the speech-modem
  calibration path.
- Voice wake-up selects one main built-in mic; reference, third-mic and SCP-DMIC
  inputs are disabled in `VoWMicSetting_AudioParam.xml`.

## IMPORTANT DISTINCTIONS

- Mixer names such as `Mic3`, `ThreeMic`, `DMic3` and `SCP_DMIC` describe reusable
  MediaTek capability, not fitted hardware.
- Analog and digital `MicInfo` projects are alternatives. DT value 1 and the HAL
  selection branch prove the analog project for this product.
- `emicen`/`emichn` DT names are EMI/memory-channel QoS nodes, not microphones.
- RT5133 and MT6369 are different devices: the former is an I2C camera LDO and
  the latter is the SPMI sub-PMIC/audio codec.
- Static configuration proves electrical and software route intent, not acoustic
  polarity, channel orientation or noise-reduction quality.

## STILL UNKNOWN / REQUIRES RUNTIME OR PHYSICAL VALIDATION

- Exact microphone manufacturer/model and PCB coordinates; whether the `back`
  acoustic port faces rearward or upward.
- Live ALSA control values and PCM activity for every requested Android source.
- Which processor executes every proprietary DMNR/Aurisys stage and the meaning
  of closed calibration coefficient arrays.
- Runtime channel polarity/order and acoustic performance for calls,
  speakerphone, camcorder, VoIP and voice recognition.
- Exact-GKI build and on-device validation under the target LieppOS ROM.

## PRIMARY EVIDENCE

- `workspace/gq5012bf1/stock/partitions/vendor/etc/mixer_paths.xml`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/audio_device.xml`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/audio_policy_configuration.xml`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/audio_effects.xml`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/audio_param/MicInfo_AudioParam.xml`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/audio_param/UplinkConfiguration_AudioParam.xml`
- `workspace/gq5012bf1/stock/partitions/vendor/etc/audio_param/AudioParamOptions_vext.xml`
- `workspace/gq5012bf1/snapshots/live-stock-adb-20260831-115649/devicetree.tar`
- `workspace/gq5012bf1/stock/partitions/vendor/lib64/hw/audio.primary.mediatek.so`
- `workspace/gq5012bf1/stock/partitions/vendor_dlkm/lib/modules/{mt6878-mt6369,snd-soc-mt6369,snd-soc-mt6878-afe}.ko`
- `../../Reverse Engineer - PARTIAL/MICROPHONES/` after workspace reclassification

The live snapshot used a LieppOS/GSI userspace. Kernel devicetree identity is
used as hardware evidence; framework behavior from that capture is not treated
as stock-framework behavior.
