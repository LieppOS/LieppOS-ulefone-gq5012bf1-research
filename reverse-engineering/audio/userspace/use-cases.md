# Normal audio use cases

| use case | physical I/O | AFE / codec / amp | processing and format evidence |
|---|---|---|---|
| media on speaker | one loudspeaker | Playback_1/DL1 or Playback_3 deep -> I2S_OUT4 -> AW88394 | 44.1/48 kHz stereo transport; BesLoudness/SmartPA; mono physical channel |
| ringtone/alarm | one loudspeaker | same external-speaker route | HAL stream gain/profile differs; same amp |
| speakerphone downlink | one loudspeaker | MD1 voice DL -> speaker AFE route -> I2S_OUT4 -> AW88394 | hands-free DMNR option is input-side and off |
| earpiece call | receiver | MD1 PCM1 -> ADDA DL -> MT6369 RCV | AP speech interface fixed 48 kHz; modem processing proprietary |
| headset playback | HPL/HPR | DL1 -> ADDA DL -> MT6369 DAC L/R | 44.1/48 kHz normal policy |
| headset call uplink | headset mic | AIN1 -> PGA_L/ADC_L -> ADDA UL -> MD1 | ACCDET selects mic; MIC_BIAS_1 |
| handset call uplink | main+sub AMIC | AIN0/AIN2 -> ADDA UL -> MD1 | normal two-mic DMNR enabled |
| normal recording | main+sub AMIC | ADDA UL -> UL9/Capture_1 | PCM16, mono/stereo, 8–48 kHz |
| camcorder | back-first dual AMIC | `builtin_Mic_BackMic` lane swap -> Capture_1 | exact front/rear app selection is HAL-private |
| voice recognition | built-in AMIC | Capture_1 or VOW hotword path | record/ASR parameters; VOW is single main mic |
| VoIP earpiece/headset | selected output and built-in/headset mic | `voip_rx` + `voip_tx` | 16/48 kHz RX; AEC/NS/AGC; VoIP DMNR options off |
| speakerphone capture | built-in AMIC | ADDA UL -> Capture_1 / speech route | hands-free DMNR off; live weighting is HAL-private |
| compressed playback | selected output | offload policy -> ADSP/offload PCM -> normal sink | MP3/AAC direct/non-blocking/gapless |
| FM listening | headset antenna + selected sink | CONNSYS/FM AFE routes; output to HP or speaker | jack GPIO 195 connects antenna; FM core remains separate scope |

`PROVEN ACTIVE` here means the product has a selected physical path and stock
route. It does not assert that every app always chooses that route; AudioPolicy
and the proprietary HAL arbitrate live use.
