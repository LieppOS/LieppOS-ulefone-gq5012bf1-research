# GQ5012BF1 normal audio stack

Offline static-analysis result for Ulefone Armor 29 Pro Thermal / GQ5012BF1.
No device was accessed and no audio/calibration operation was run.

## Result

The board-specific kernel audio stack is source-closed. **22 directly relevant
modules rebuild with every function, data object and ABI check exact.** The
previously closed AW88394 module remains behaviour-exact (235/236 byte-exact;
236/236 semantically exact, full ABI).

The proprietary boundary is above that kernel layer: MediaTek's V3 primary HAL,
speech/Aurisys algorithms, ADSP/SCP firmware and product acoustic/speaker
tuning have binaries/configuration but not source.

```text
Android AudioTrack / AudioRecord / AudioManager
  -> audioserver: AudioPolicyService + AudioFlinger
  -> HIDL audio 7.1 service (effects 7.0)
  -> audio.primary.mediatek.so == audio.primary.mt6878.so
  -> tinyalsa + /vendor/etc/audio_device.xml mixer paths
  -> mt6878-mt6369 ASoC machine card
       -> MT6878 AFE (DL/UL memifs, interconnect, ADDA/I2S/PCM)
       -> MT6369 SPMI codec (headphone, receiver, microphones, ACCDET)
       -> I2S_OUT4/I2S_IN4 -> AW88394 mono smart amp -> one loudspeaker
       -> MD1 PCM -> modem speech firmware for cellular calls
       -> audio_ipi -> ADSP/SCP for configured offload/VOW/ultrasound tasks
```

## Fitted hardware

| block | fitted contract |
|---|---|
| AFE | MT6878 AFE at `0x11050000`, IRQ 392 |
| codec | MT6369 second PMIC, SPMI USID 5; codec child `mediatek,mt6369-sound` |
| smart amp | one AW88394 (PID `0x2049`), I2C-6 `0x34`, reset GPIO 193, IRQ GPIO 41, channel 0 |
| loudspeaker | one configured SmartPA/loudspeaker channel (`MTK_AUDIO_NUMBER_OF_SPEAKER=1`) |
| receiver | separate internal MT6369 `RCV` analog path (`RCV_PATH_INT=yes`); the earpiece does not use the SmartPA path in stock configuration |
| microphones | two built-in analog microphones: AIN0/main and AIN2/sub, plus the distinct wired-headset microphone on AIN1 |
| wired jack | MT6369 ACCDET, PMIC EINT0, AUXADC channel 9, 3-button headset, FM antenna switch GPIO 195 |

`AW88394` ACF contains both `Music` and `Receiver` profile names, but that is
capability/profile inventory, not proof that the receiver profile is selected.
The product options explicitly choose `RCV_PATH_INT=yes` and
`SPK_PATH_NO_ANA=yes`; therefore normal earpiece calls use MT6369 RCV while
speaker/media use AW88394. This corrects the older profile-name-only inference.

The firmware proves one external loudspeaker channel and one internal receiver
path. Mechanical placement of the loudspeaker grille still requires a teardown;
"bottom speaker" is not encoded in DT.

## Status by scope

| scope | result |
|---|---|
| MT6369 codec, ACCDET, PMIC support | **DONE** — complete source, 5 modules exact, functional register map and board routing |
| MT6878 AFE/machine/common | **DONE** — complete source, 7 modules exact, active routes separated from platform-only routes |
| audio DSP kernel transport | **DONE** — 9 transport/PCM/VOW/ultrasound modules exact |
| AW88394 kernel driver | **DONE** in `Reverse Engineer - DONE/AW883XX-SPEAKER-AMP` |
| Audio HAL / speech / effects | **PARTIAL / proprietary** — interfaces and dependencies mapped; source absent |
| ADSP/SCP algorithms and firmware | **PARTIAL / proprietary** — kernel transport exact; executable DSP payload source absent |
| AW88394 acoustic tuning/calibration | **PARTIAL data boundary** — stock ACF/parameter binaries preserved; acoustic/NVRAM data not reconstructable offline |
| physical microphone/grille placement | **PARTIAL physical boundary** |

See [`STATUS.md`](STATUS.md), [`kernel/module-inventory.tsv`](kernel/module-inventory.tsv),
[`afe/`](afe/), [`mt6369/`](mt6369/), [`dsp/`](dsp/), and
[`userspace/`](userspace/).
