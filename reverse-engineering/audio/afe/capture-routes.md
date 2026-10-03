# MT6878 capture routes

## Primary built-in capture — proven active

```text
AIN0/main -> MT6369 PGA_L/ADC_L -> UL1_CH1/MISO0 --┐
AIN2/sub  -> MT6369 PGA_R/ADC_R -> UL1_CH2/MISO1 --┤
                                                    v
MT6878 ADDA UL -> UL9_CH1/2 / UL_CM1 interconnect -> Capture_1
 -> MediaTek primary HAL -> AudioFlinger/AudioRecord
```

The stock mixer path sets `UL_SRC_MUX=AMIC`. `builtin_Mic_BackMic` swaps the
MTKAIF lane order so the rear/sub microphone becomes first. Product options
select exactly two microphones and no AP/SCP DMIC.

## Wired-headset capture — proven active

```text
headset mic -> MIC_BIAS_1 -> AIN1 -> PGA_L/ADC_L -> ADDA_UL_CH1
 -> UL9 / Capture_1 -> HAL
```

ACCDET supplies jack/microphone state and button events.

## Cellular call uplink — proven configured

```text
built-in dual AMIC (or headset AMIC)
 -> ADDA_UL
 -> MT6878 PCM1 / MD1 speech path
 -> modem speech firmware
```

Normal handset dual-mic DMNR is enabled. Hands-free call DMNR is disabled.
Product option `MTK_PHONE_CALL_FIXED_48K_SAMPLERATE=yes` fixes the AP speech
interface at 48 kHz; modem voice bandwidth remains modem/codec dependent.

## Android input profiles

The primary policy exposes PCM16 mono/stereo at 8/16/32/44.1/48 kHz. It also
exposes fast input, MMAP input, `voip_tx`, hardware hotword and voice-TX ports.

| use case | selected physical input / processing conclusion |
|---|---|
| normal recorder | built-in AIN0/AIN2; HAL record profile |
| camcorder | built-in back-mic-first route; exact app/front-vs-rear switching is proprietary HAL policy |
| voice recognition | built-in AMIC route and ASR/record parameters; no third microphone |
| VoIP | built-in or headset mic according to Android device; AEC/NS/AGC are applied for `voice_communication`; VoIP DMNR options are off |
| speakerphone capture | built-in AMIC capture; hands-free DMNR off; exact live lane weighting remains runtime-only |
| handset call | AIN0/AIN2 -> MD1, normal two-mic DMNR on |
| headset call | AIN1 -> MD1 |
| VOW | single main AMIC; `Capture_9` is configured for barge-in/hotword |

## Dormant/platform routes

Generic `Mic3`, ThreeMic, AP DMIC, SCP DMIC and four-channel paths remain in
`audio_device.xml` and the AFE driver. They are not fitted selections for this
product. Their presence is not microphone-count evidence.
