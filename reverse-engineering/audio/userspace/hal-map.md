# Stock userspace audio stack

## Service/API boundary

```text
app AudioTrack / AudioRecord / AudioManager
 -> audioserver: AudioPolicyService + AudioFlinger
 -> /vendor/bin/hw/android.hardware.audio.service.mediatek
 -> HIDL android.hardware.audio@7.1::IDevicesFactory/default
 -> android.hardware.audio@7.1-impl-mediatek.so
 -> legacy primary module audio.primary.mt6878.so
    (byte-identical to audio.primary.mediatek.so)
 -> tinyalsa / tinycompress / ALSA controls
```

Effects are HIDL `android.hardware.audio.effect@7.0`. Bluetooth audio is AIDL
version 3 (`IBluetoothAudioProviderFactory/default`) while the MediaTek service
also links legacy MediaTek Bluetooth audio interfaces for compatibility.

The init service runs as `audioserver`, class `hal`; on restart it restarts
`audioserver`. It receives audio, camera, media, DRM, Bluetooth, network,
wakelock, context-hub and system groups and uses high-performance task profiles.

## Proprietary primary HAL

`audio.primary.mediatek.so` is 3,630,736 bytes and exactly equals
`audio.primary.mt6878.so` (SHA-256
`b5863802f617e5b14b0888d606c92def74c2591a500c450db722057328adbdb4`).
Strings/dynamic symbols identify MediaTek proprietary V3 classes for:

- normal/deep/fast/MMAP/offload/VoIP/FM/AAudio playback;
- normal/fast/MMAP/VoIP/VOW/modem/Bluetooth/USB capture;
- `AudioALSAHardwareResourceManager` route/power ownership;
- `AudioSmartPaController`;
- `AudioALSAPlaybackHandler*`, `AudioALSACaptureHandler*` and providers;
- phone-call controller/speech driver;
- Aurisys and record/VoIP processing.

No exact userspace source is in the release. This is the principal software
replacement boundary; the exported HIDL/legacy HAL and ALSA/mixer contracts are
mapped.

## Product choices

Important `AudioParamOptions_vext.xml` values:

- `MTK_AUDIO_SPEAKER_PATH=smartpa_awinic_aw883xx`;
- one speaker, two microphones;
- `RCV_PATH_INT=yes`, `SPK_PATH_NO_ANA=yes`;
- normal handset DMNR yes; hands-free and VoIP DMNR no;
- BesLoudness in HAL yes;
- VOW yes, single-mic, no GVA/Amazon/dual-mic;
- deep-buffer PCM `Playback_3`;
- VOW barge-in `Capture_9`;
- fixed 48 kHz phone-call AP interface;
- 24-bit-only playback internal path.

## SmartPA userspace

- `libaudiosmartpamtk.so`: MTK SmartPA manager, tinyalsa/NVRAM access.
- `libawinicsmartpaparse.so`: Awinic ACF/parameter parser.
- `awinic.audio.effect.so`: SKTune algorithm/calibration effect; loaded by the
  SmartPA/HAL path, not registered as a public Android effect in
  `audio_effects.xml`.
- `smartpa_nvtest`: calibration NVRAM helper.
- `awinic_params.bin` / `awinic_sinwave_params.bin`: 13,640-byte parameter bins.

Exact ELF dependencies and hashes are in [`library-dependencies.tsv`](library-dependencies.tsv).
