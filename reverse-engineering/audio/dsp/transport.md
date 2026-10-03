# Audio DSP/SCP kernel transport: DONE

## Exact modules

| module | functions | data | role |
|---|---:|---:|---|
| `audio_ipi` | 119/119 | 32/32 | audio message queue, DMA/shared-memory and ADSP/SCP IPI abstraction |
| `adsp` | 166/166 | 68/68 | ADSP core, mailbox/IPI, reserved memory, clocks, exception/logging |
| `snd-soc-audiodsp-common` | 172/172 | 150/150 | DSP ALSA PCM and task management |
| `mtk-soc-offload-common` | 34/34 | 32/32 | compressed-offload PCM/transport |
| `mtk-scp-audiocommon` | 24/24 | 28/28 | SCP audio shared memory and message transport |
| `mtk-scp-vow` | 5/5 | 4/4 | VOW ASoC DAI bridge |
| `mtk-vow` | 71/71 | 48/48 | VOW userspace/control/IPI service |
| `snd-soc-mtk-scp-ultra` | 45/45 | 34/34 | ultrasound ASoC PCM |
| `mtk-scp-ultra` | 7/7 | 4/4 | ultrasound SCP common layer |

All ABI fields and section sizes match. Exact source and parity reports are in
this directory.

## Transport chain

```text
MediaTek primary HAL / Aurisys
 -> ALSA DSP/offload/VOW PCM or /dev audio control
 -> snd-soc-audiodsp-common / mtk-soc-offload-common / mtk-vow
 -> audio_ipi
 -> ADSP mailbox/IPI + reserved memory, or SCP tinysys IPI/shared memory
 -> proprietary firmware task
```

The ADSP core uses MediaTek IPI/mailbox/IPIC, not Linux rpmsg for its audio
messages. SCP audio uses the common tinysys IPI/mailbox infrastructure. DT
reserves `0x5c0000` for ADSP audio and configures two ADSP cores/devices.

## Board classification

- VOW is configured active (`MTK_VOW_SUPPORT=yes`), single main AMIC; Amazon,
  GVA and dual-mic VOW options are off.
- Compressed MP3/AAC offload is advertised by policy and the transport is
  present; exact runtime task selection is proprietary HAL behavior.
- SCP ultrasound and barge-in routes are configured; a live invocation was not
  proved offline.
- Generic AP/SCP DMIC, BLE, multichannel and dynamic DSP links are capabilities,
  not proof of fitted transducers.
