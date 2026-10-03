# Audio policy / mixer contract

## Policy ports

Primary policy exposes:

- primary, deep-buffer and fast stereo PCM outputs (44.1/48 kHz, PCM16/32);
- MP3/AAC compressed offload;
- VoIP RX, MMAP/no-IRQ and incall-music output;
- primary, fast, MMAP, VoIP TX and hardware-hotword inputs;
- FM tuner input/output;
- HDMI and standard USB/Bluetooth included policy modules.

Declared physical devices include speaker, earpiece, wired headset/headphones,
built-in/back/wired-headset microphones, telephony RX/TX, USB, HDMI and FM.
Policy declaration means routable interface support; it does not prove a
physical accessory is connected.

## Mixer XML

`/vendor/etc/audio_device.xml` is consumed by the proprietary primary HAL. The
complete flattened path/control list is [`../afe/controls.tsv`](../afe/controls.tsv).
Key board routes:

| logical path | controls |
|---|---|
| external speaker | `Ext_Speaker_Amp Switch=1` |
| internal receiver | `RCV Mux=Voice Playback` |
| headphone | `HPL Mux=Audio Playback`, `HPR Mux=Audio Playback` |
| headset mic | `PGA_L Mux=AIN1`, `ADC_L Mux=Left Preamplifier` |
| main/sub built-ins | AIN0/PGA_L/ADC_L and AIN2/PGA_R/ADC_R |
| speaker PCM | `DL1_CH1/2 -> I2SOUT4_CH1/2` |
| normal codec playback | `DL1_CH1/2 -> ADDA_DL_CH1/2` |
| primary capture | ADDA_UL -> UL9/Capture_1 |

Generic unused routes are intentionally retained by MediaTek XML: Mic3,
ThreeMic, AP/SCP DMIC, multiple I2S/ETDM, dual speaker, RT/TFA and other
platform choices. Product options/DT determine what is actually selected.

## Android effects

Public `audio_effects.xml` registers standard bundle/reverb/visualizer/downmix,
loudness enhancer, dynamics processing, spatializer and MediaTek pre-processing.
`voice_communication` receives MediaTek AEC, NS and AGC. Awinic SKTune is a
private SmartPA integration, not a public effect entry.

## Properties

- AAudio MMAP policy and exclusive policy = 2.
- HiFi audio enabled.
- deep-buffer media enabled.
- audio offload for video enabled; minimum offload duration 30 seconds.
- A2DP offload and LE audio offload enabled.
- USB super-HiFi and USB offload enabled (digital USB audio).
