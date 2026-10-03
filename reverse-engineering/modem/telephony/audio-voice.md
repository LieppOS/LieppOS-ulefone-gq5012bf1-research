# Telephony ↔ audio dependency graph

This closes only the modem-facing edge. Audio kernel reconstruction remains in the existing
`reverse-engineering/audio/` and DONE audio components.

```
IRadioVoice / ImsService
  -> mtkfusionrild -> MIPC /dev/ttyCMIPC1 -> MD speech engine
                                           │
Audio HAL (audio.primary.mediatek.so)        │ control/state
  <-> /dev/ccci_aud (CCCI_AUDIO ch 6/7) <---┘
  <-> /dev/ccci_raw_audio (SMEM_USER_RAW_AUDIO, 52 KiB fallback size)
  <-> /dev/usip (SMEM_USER_RAW_USIP via snd-soc-mtk-common/mtk-usip)
  -> ALSA `PCM 1` / MT6878 AFE MD1 DAI <-> modem PCM samples
  -> speech enhancement / DMNR -> MT6369 codec -> receiver/headset
                             \-> I2S4 -> AW88394 mono loudspeaker
```

## Evidence

* `audio.primary.mediatek.so` has literal/open references to `/dev/ccci_aud` and
  `/dev/ccci_raw_audio`; SELinux grants both to `mtk_hal_audio` as `ccci_aud_device`.
* CCCI stock port table:
  * `ccci_aud`: CCCI_AUDIO_RX/TX (7/6), CCIF, char port.
  * `ccci_raw_audio`: shared-memory port for `SMEM_USER_RAW_AUDIO`.
* `snd-soc-mtk-common.ko` imports `get_smem_phy_start_addr` and
  `get_smem_start_addr` from ccci_util_lib. `mtk-usip.c` maps `SMEM_USER_RAW_USIP` and exposes
  `/dev/usip` for speech enhancement shared data.
* The previously closed MT6878 AFE scope identifies the active modem route as MD1/PCM1; voice
  samples do **not** traverse DPMAIF/CCMNI.
* `libMtkSpeechEnh.so` and `libspeech_enh_lib.so` are proprietary algorithms; static properties
  enable dual-mic support. DMNR coefficients/calibration are outside the CCCI kernel scope.

IMS voice uses the same speech/PCM hardware path after session control in the MD IMS stack.
