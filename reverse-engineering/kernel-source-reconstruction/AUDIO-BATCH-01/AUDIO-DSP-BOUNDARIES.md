# Audio DSP / co-processor boundaries

## What is now source-identical (kernel host side only)

| Layer | Module | Host-side protocol |
|---|---|---|
| Co-processor core host | `adsp` (166 fn) | ADSP/SCP core state, mailbox, IPI, semaphore, logger, time sync, reserved memory, exception/recovery dump, QoS, bus monitor; exports `set_adsp_state` and 53 others |
| Audio IPI transport | `audio_ipi` (119 fn) | task manager, messenger IPI, IPI queues, DMA ring buffers (`audio_ipi_dma`, `audio_ringbuf`), platform v4 |
| SCP audio mailbox | `mtk-scp-audiocommon` | `scp_audio_ipi`, `audio_mbox` on `scp-audio-mbox@1cbe0000`, SCP audio logger |
| DSP ALSA PCM | `snd-soc-audiodsp-common` | DSP DAIs/PCMs, shared-memory buffers (`audio_buf`, `mtk-dsp-mem-control`), task descriptors from `snd-audio-dsp` |
| Compressed offload | `mtk-soc-offload-common` | compress-offload transport into DSP task `offload` |
| Voice wakeup | `mtk-vow`, `mtk-scp-vow` | VOW control, model/bargein buffers, SCP IPI (`MTK_TINYSYS_SCP_DEBUG_SUPPORT` off in stock) |
| Ultrasound | `mtk-scp-ultra`, `snd-soc-mtk-scp-ultra` | SCP ultrasound PCM/memif, `ultra_ipi` |

Fault and recovery: the kernel side covers `adsp_excep`, the `scp_A_register_notify` callbacks
and `aee`/`mrdump` hooks. These go only as far as the provider boundary listed in `PROVIDER-BOUNDARIES.tsv`.

## Board fact

`snd-audio-dsp` declares `mtk-dsp-type = "RV55"`. The audio DSP tasks therefore run on the MT6878
RISC-V SCP and are reached via `scp-audio-mbox` and the `scp.ko` IPI table (`scp_ipidev`, reserved
memory exports). The `adsp` module is still loaded first-stage as the generic co-processor host
framework.

## Not open source (unchanged by this batch)

- SCP / audio DSP **firmware** (`scp.img` and its audio tasks), including task algorithms, the SmartPA
  software processing (`swdsp-smartpa-process-enable`), speech enhancement, VOW models and the
  ultrasound engine.
- The MediaTek V3 primary audio HAL, Aurisys/speech libraries, Awinic tuning (ACF) and calibration data.
- Modem speech firmware for the MD1 PCM voice path.

## Provider boundary (verified, not certified)

`scp` (13 symbols), `ccci_md_all` and `ccci_util_lib` (1 each) remain **G**, and `mtk_slbc` (4)
remains **D**. Their export CRC, licence, namespace and KCFI words are reproduced exactly by
compiled ALPS source, which is enough for the 21 audio modules to link against the stock
providers. The providers' own implementations are outside this batch and keep their
classifications.
