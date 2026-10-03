# Loudspeaker and receiver

## Proven topology

- Product option: `MTK_AUDIO_NUMBER_OF_SPEAKER=1`.
- Speaker path: `MTK_AUDIO_SPEAKER_PATH=smartpa_awinic_aw883xx`.
- Speaker analog path: `SPK_PATH_NO_ANA=yes`; MT6369 lineout is not the stock
  loudspeaker drive.
- Receiver path: `RCV_PATH_INT=yes`; the normal earpiece path is MT6369 `RCV`.
- SmartPA type 5 = AW883XX; the selected fitted PID is AW88394.
- One amp, one ASoC instance, default channel 0. This is mono at the transducer
  even though Android and I2S streams normally carry stereo frames.
- AFE links are I2S_OUT4 (playback) and I2S_IN4 (current/voltage feedback).
- AW88394 parameters support 8–96 kHz and S16/S24/S32_LE. Android primary
  policy advertises stereo PCM at 44.1/48 kHz, 16/32-bit containers.

## Receiver correction

The Awinic ACF contains profile labels `Music` and `Receiver`. Those labels
alone do not prove the amp drives the earpiece. Product options give the stronger
routing decision: `RCV_PATH_INT=yes`. The MT6369 DAPM graph has an independent
`RCV Mux -> RCV` path, while `two_in_one_speaker_output` in `audio_device.xml`
is empty. Normal receiver calls therefore use MT6369, not AW88394.

## Physical boundary

Static firmware establishes one external loudspeaker channel plus an internal
receiver output. It does not encode the acoustic port or grille location. A
physical teardown is needed to call the loudspeaker "bottom" with hardware
proof.

## Protection and tuning

Kernel protections, monitor work, DSP profile loading, mute/power sequencing,
impedance calibration control and thermal monitoring are reconstructed in the
AW883XX DONE component. Proprietary/product data remain:

- `aw883xx_acf.bin` acoustic profiles;
- `awinic_params.bin` and `awinic_sinwave_params.bin` (13,640 bytes each);
- Awinic SKTune `awinic.audio.effect.so`;
- `/mnt/vendor/nvdata/APCFG/APRDCL/smartpa_calib` per-device calibration.

Do not synthesize or write calibration offline.
