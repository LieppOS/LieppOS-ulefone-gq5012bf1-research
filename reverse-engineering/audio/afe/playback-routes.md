# MT6878 playback routes

## Proven active board routes

### Loudspeaker / ringtone / alarm / speakerphone downlink

```text
AudioFlinger primary/deep output
 -> MediaTek HAL PCM (normal primary is Playback_1 / DL1;
    product deep-buffer PCM is Playback_3)
 -> MT6878 DL memif
 -> AFE interconnect DL1_CH1/2 -> I2SOUT4
 -> `Ext_Speaker_Amp Switch`
 -> `Speaker Codec` BE (DT spk-i2s-out = 25 = MTK_SPK_I2S_OUT4)
 -> AW88394 digital input, channel 0
 -> one loudspeaker
```

Android policy advertises primary/deep/fast PCM at 44.1 or 48 kHz, stereo,
16- or 32-bit containers. The product forces 24-bit playback internally. A
stereo transport does not imply two loudspeakers; the SmartPA population is one
mono channel.

### Headphones

```text
Playback_1 / DL1
 -> DL1_CH1/2 -> ADDA_DL_CH1/2
 -> MT6369 MTKAIF RX -> DAC L/R
 -> HPL/HPR
```

### Earpiece / receiver call

```text
modem MD1 PCM1 downlink (voice path; fixed 48 kHz product option)
 -> MT6878 PCM/ADDA interconnect
 -> MT6369 DAC -> RCV Mux -> RCV output
 -> receiver transducer
```

`RCV_PATH_INT=yes`; the AW88394 receiver-labelled ACF profile is not evidence
that this stock route uses the smart amp.

### SmartPA feedback

`Speaker Codec Ref` maps DT value 24 to `MTK_SPK_I2S_IN4`. This returns the
AW88394 current/voltage feedback stream for protection/calibration. It is not a
second audible channel.

## Configured paths

| path | state |
|---|---|
| deep buffer | configured: `Playback_3`, 49,152-byte kernel buffer |
| compressed offload | policy advertises MP3/AAC direct non-blocking gapless; kernel offload/ADSP transport exact |
| VoIP RX | configured at 16/48 kHz through `voip_rx` |
| AAudio MMAP | configured at 48 kHz stereo |
| FM | policy and AFE CONNSYS/FM routes exist; FM receiver component remains its own PARTIAL scope |
| ultrasound | SCP ultrasound playback/capture modules and DT memifs configured; runtime use not proved |
| VOW barge-in echo | mixer templates configured, including DSP SmartPA reference; runtime selection not proved |

## Platform-only paths

The AFE source contains I2S0–9, ETDM, TDM, HDMI, hostless, SRC, HW-gain and
multi-channel routes. Do not equate source capability with board use. Product
DT only assigns speaker I2S_OUT4/I2S_IN4; no second SmartPA or ETDM speaker
array is fitted.

All 1,021 nested mixer/path operations from stock `audio_device.xml` are in
[`controls.tsv`](controls.tsv).
